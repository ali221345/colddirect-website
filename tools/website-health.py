"""Bounded read-only public website audit. No credentials or publishing operations."""
import json
import posixpath
import re
import socket
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.robotparser import RobotFileParser

SITE = 'https://www.colddirect.co.uk/'
OUTPUT = Path(__file__).resolve().parent / 'reports/website-health'
LIMIT = 2 * 1024 * 1024
SENTINELS = ['/', '/services/', '/services', '/services.html', '/services/index.html',
             '/services/?healthcheck=1', '/fridge-repair-london/', '/freezer-repair-london/',
             '/commercial-fridge-repair-london/', '/cold-room-repair-london/',
             '/blog/commercial-fridge-repair-cost-london/',
             '/blog/commercial-fridge-repair-cost-london.html',
             '/blog/commercial-fridge-repair-cost-london', '/refrigeration-brands-repair-london/']
UTILITIES = ['/agent-status.html', '/agent-status/', '/image-preview.html', '/agent-status-full-report.txt']
PUBLIC_ASP = {'/chiller-repair-london.asp', '/ice-machine-repair-london.asp'}
EXPECTED_CANONICALS = {
    SITE + 'services/index.html': SITE + 'services/',
    SITE + 'blog/commercial-fridge-repair-cost-london.html': SITE + 'blog/commercial-fridge-repair-cost-london/',
}

class AuditError(RuntimeError):
    pass

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def safe_url(url):
    p = urlsplit(url)
    if p.scheme != 'https' or p.netloc != 'www.colddirect.co.uk' or p.username or p.password:
        raise AuditError('Unexpected public URL host or scheme')
    decoded = p.path
    for _ in range(4):
        decoded = unquote(decoded)
    if '\\' in decoded or '..' in decoded.split('/') or re.search(r'%[0-9a-f]{2}', decoded, re.I):
        raise AuditError('Encoded traversal or ambiguous public path excluded')
    normalized = posixpath.normpath(decoded.replace('\\', '/'))
    if re.search(r'(^|/)(?:cold-agent[^/]*|daily-job\.php|keepalive\.php|book\.php|booking[^/]*|agent(?:/|$)|api(?:/|$))', normalized, re.I) or re.search(r'\.php(?:/|$)', normalized, re.I):
        raise AuditError('Operational endpoint excluded')
    if re.search(r'\.asp(?:/|$)', normalized, re.I) and normalized.lower() not in PUBLIC_ASP:
        raise AuditError('Unreviewed ASP endpoint excluded')
    return urlunsplit((p.scheme, p.netloc, p.path or '/', p.query, ''))

def fetch(url):
    # A fresh opener per request avoids shared mutable HTTP state across workers.
    request = Request(safe_url(url), headers={'User-Agent': 'ColdDirectHealthAudit/1.0', 'Accept': '*/*'})
    try:
        try:
            response = build_opener(NoRedirect).open(request, timeout=30)
        except HTTPError as exc:
            response = exc
        with response:
            body = response.read(LIMIT + 1)
            if len(body) > LIMIT:
                raise AuditError('Public response exceeds 2MB limit')
            charset = response.headers.get_content_charset() or 'utf-8'
            headers = dict(response.headers.items())
            robot_headers = response.headers.get_all('X-Robots-Tag')
            if robot_headers:
                headers = {k: v for k, v in headers.items() if k.lower() != 'x-robots-tag'}
                headers['X-Robots-Tag'] = '\n'.join(robot_headers)
            return response.code, headers, body.decode(charset, errors='replace')
    except (URLError, TimeoutError, OSError, LookupError) as exc:
        raise AuditError('Public HTTP transport failed: ' + type(exc).__name__) from None

def follow(url, getter=fetch):
    current = safe_url(url)
    seen, chain = set(), []
    for hop in range(9):
        if current in seen:
            return {'url': url, 'final_url': current, 'chain': chain, 'error': 'redirect_loop'}
        seen.add(current)
        status, headers, body = getter(current)
        headers = {k.lower(): v for k, v in headers.items()}
        chain.append({'url': current, 'status': status})
        if status in (301, 302, 303, 307, 308):
            location = headers.get('location')
            if not location:
                return {'url': url, 'final_url': current, 'chain': chain, 'error': 'redirect_missing_location'}
            target = urljoin(current, location)
            try:
                target = safe_url(target)
            except AuditError:
                return {'url': url, 'final_url': current, 'chain': chain, 'error': 'redirect_outside_public_scope'}
            if hop == 8:
                return {'url': url, 'final_url': current, 'chain': chain, 'error': 'redirect_limit'}
            current = target
        else:
            return {'url': url, 'final_url': current, 'chain': chain, 'status': status, 'headers': headers, 'body': body}

class Metadata(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.canonicals, self.robots, self.h1, self.structured = [], [], [], []
        self.title = ''
        self.capture, self.buffer = None, []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'link' and 'canonical' in a.get('rel', '').lower().split():
            self.canonicals.append(a.get('href', ''))
        if tag == 'meta' and a.get('name', '').lower() in ('robots', 'googlebot'):
            self.robots.append(a.get('content', '').lower())
        if tag in ('title', 'h1') or (tag == 'script' and a.get('type', '').lower() == 'application/ld+json'):
            self.capture, self.buffer = tag, []
    def handle_data(self, data):
        if self.capture:
            self.buffer.append(data)
    def handle_endtag(self, tag):
        if tag != self.capture:
            return
        value = ''.join(self.buffer).strip()
        if tag == 'title':
            self.title = value
        elif tag == 'h1':
            self.h1.append(value)
        else:
            try:
                json.loads(value)
                self.structured.append(True)
            except (ValueError, TypeError):
                self.structured.append(False)
        self.capture, self.buffer = None, []

def issue(url, kind, detail=''):
    return {'url': url, 'kind': kind, 'detail': detail}

def header_noindex(value):
    # Agent-targeted directives apply only to their named crawler. Reset targeting
    # for each separate HTTP header, retained as separate lines by fetch().
    for line in value.lower().splitlines():
        agent = None
        for segment in line.split(','):
            directive = segment.strip()
            if ':' in directive:
                agent, directive = (part.strip() for part in directive.split(':', 1))
            if agent in (None, '*', 'googlebot') and re.search(r'\b(noindex|none)\b', directive):
                return True
    return False

def inspect(url, listed, getter=fetch):
    row = follow(url, getter)
    problems = []
    if row.get('error'):
        return row, [issue(url, row['error'])]
    status = row['status']
    if status != 200:
        problems.append(issue(url, 'http_status', str(status)))
    if listed and len(row['chain']) > 1:
        problems.append(issue(url, 'sitemap_redirect', row['final_url']))
    headers, body = row.pop('headers'), row.pop('body')
    if status == 200:
        parsed = Metadata()
        parsed.feed(body)
        row.update(title=parsed.title, h1=parsed.h1, canonicals=parsed.canonicals,
                   robots=parsed.robots, x_robots_tag=headers.get('x-robots-tag', ''),
                   jsonld_blocks=len(parsed.structured), jsonld_valid=all(parsed.structured))
        directives = ' '.join(parsed.robots)
        if re.search(r'\b(noindex|none)\b', directives) or header_noindex(headers.get('x-robots-tag', '')):
            problems.append(issue(url, 'noindex'))
        if not parsed.title:
            problems.append(issue(url, 'missing_title'))
        if len(parsed.h1) != 1:
            problems.append(issue(url, 'h1_count', str(len(parsed.h1))))
        if len(parsed.canonicals) != 1:
            problems.append(issue(url, 'canonical_count', str(len(parsed.canonicals))))
        elif urljoin(row['final_url'], parsed.canonicals[0]).split('#')[0].split('?')[0] != EXPECTED_CANONICALS.get(row['final_url'].split('?')[0], row['final_url'].split('?')[0]):
            problems.append(issue(url, 'canonical_mismatch', urljoin(row['final_url'], parsed.canonicals[0])))
        if not all(parsed.structured):
            problems.append(issue(url, 'invalid_jsonld'))
    return row, problems

def compare(previous, report):
    if previous is None:
        return {'new': [], 'resolved': []}
    def keyed(rows):
        return {(x['url'], x['kind'], x['detail']): x for x in rows}
    old, new = keyed(previous['issues']), keyed(report['issues'])
    return {'new': [new[k] for k in sorted(new.keys() - old.keys())],
            'resolved': [old[k] for k in sorted(old.keys() - new.keys())]}

def save(report, output=OUTPUT):
    output.mkdir(parents=True, exist_ok=True)
    latest = output / 'latest.json'
    previous = json.loads(latest.read_text(encoding='utf-8')) if latest.exists() else None
    report['baseline_created'] = previous is None
    report['changes'] = compare(previous, report)
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    archive = output / (stamp + '.json')
    temporary = output / 'latest.tmp'
    temporary.write_text(encoded, encoding='utf-8')
    archive.write_text(encoded, encoding='utf-8')
    temporary.replace(latest)
    return report

def run(getter=fetch, output=OUTPUT):
    sm = follow(SITE + 'sitemap.xml', getter)
    if sm.get('error') or sm.get('status') != 200:
        raise AuditError('Sitemap unavailable (' + str(sm.get('error') or sm.get('status')) + '); baseline preserved')
    try:
        doc = ET.fromstring(sm['body'])
        urls = sorted({safe_url(item.text or '') for item in doc.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')})
    except (ET.ParseError, ValueError) as exc:
        raise AuditError('Sitemap invalid; baseline preserved') from None
    if not urls or len(urls) > 200:
        raise AuditError('Sitemap size outside 1..200; baseline preserved')
    rb = follow(SITE + 'robots.txt', getter)
    if rb.get('error') or rb.get('status') != 200:
        raise AuditError('Robots unavailable (' + str(rb.get('error') or rb.get('status')) + '); baseline preserved')
    robots = RobotFileParser()
    robots.parse(rb['body'].splitlines())
    requested = sorted(set(urls) | {urljoin(SITE, x) for x in SENTINELS})
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'site': SITE,
              'sitemap_urls': len(urls), 'checked_urls': len(requested), 'pages': [], 'issues': []}
    with ThreadPoolExecutor(max_workers=4) as pool:
        # Any transport failure propagates before save: incomplete audits never replace latest.
        for row, problems in pool.map(lambda u: inspect(u, u in urls, getter), requested):
            report['pages'].append(row)
            report['issues'].extend(problems)
    for url in urls:
        if not robots.can_fetch('Googlebot', url):
            report['issues'].append(issue(url, 'robots_blocked'))
    for path in UTILITIES:
        if robots.can_fetch('Googlebot', urljoin(SITE, path)):
            report['issues'].append(issue(urljoin(SITE, path), 'utility_crawl_allowed'))
    report['issues'].sort(key=lambda x: (x['url'], x['kind'], x['detail']))
    return save(report, output)

if __name__ == '__main__':
    socket.setdefaulttimeout(30)
    try:
        result = run()
        print(json.dumps({k: result[k] for k in ('checked_at', 'sitemap_urls', 'checked_urls', 'baseline_created', 'changes')}, ensure_ascii=False))
        print('Issue count:', len(result['issues']))
    except (AuditError, OSError, ValueError) as exc:
        print('Audit incomplete; previous baseline preserved. ' + str(exc), file=sys.stderr)
        sys.exit(1)

