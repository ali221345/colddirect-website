"""Bounded, read-only one-level public page link audit; no website changes."""
import importlib.util
import json
import socket
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('health', ROOT / 'website-health.py')
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)

class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href')
            if href:
                self.hrefs.append(href)

def public_page(url):
    p = urlsplit(health.safe_url(url))
    # Query links can operate an endpoint or explode the URL inventory.
    if p.query or p.path.lower() in health.UTILITIES:
        raise health.AuditError('Excluded utility or query URL')
    suffix = Path(p.path.rstrip('/')).suffix.lower()
    if suffix not in ('', '.html', '.htm', '.asp'):
        raise health.AuditError('Excluded asset or endpoint')
    if any(segment.lower() in ('admin', 'login', 'logout', 'tools', 'scripts', '.git')
           for segment in p.path.split('/')):
        raise health.AuditError('Excluded operational path')
    return urlunsplit((p.scheme, p.netloc, p.path or '/', '', ''))

def checked(url):
    try:
        row = health.follow(url)
        body = row.pop('body', '')
        headers = row.pop('headers', {})
        links = []
        if row.get('status') == 200 and 'text/html' in headers.get('content-type', '').lower():
            parser = Links()
            parser.feed(body)
            for href in parser.hrefs:
                try:
                    links.append(public_page(urljoin(row['final_url'], href)))
                except (health.AuditError, ValueError):
                    pass
        return row, sorted(set(links))
    except (health.AuditError, ValueError, OSError) as exc:
        return {'url': url, 'error': 'transport_or_scope', 'detail': str(exc)}, []

def run():
    latest = json.loads((ROOT / 'reports/website-health/latest.json').read_text(encoding='utf-8'))
    seeds = []
    for row in latest['pages']:
        try:
            seeds.append(public_page(row['url']))
        except (health.AuditError, ValueError):
            pass
    seeds = sorted(set(seeds))[:120]
    referrals, cached = defaultdict(set), {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for row, links in pool.map(checked, seeds):
            cached[row['url']] = row
            for link in links:
                referrals[link].add(row.get('final_url', row['url']))
    discovered = sorted(referrals, key=lambda u: (-len(referrals[u]), u))
    selected = discovered[:350]
    missing = [u for u in selected if u not in cached]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for row, _ in pool.map(checked, missing):
            cached[row['url']] = row
    rows = []
    for url in sorted(set(seeds) | set(selected)):
        row = cached[url]
        row['referring_pages'] = sorted(referrals.get(url, set()))
        row['seed'] = url in seeds
        rows.append(row)
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'scope': 'one-level public page links; read-only',
              'seed_count': len(seeds), 'discovered_unique_links': len(discovered),
              'discovered_checked': len(selected), 'truncated': len(discovered) > 350,
              'checked_total': len(rows), 'status_counts': dict(Counter(str(r.get('status', r.get('error'))) for r in rows)),
              'proven_404': [r for r in rows if r.get('status') == 404],
              'other_http_errors': [r for r in rows if r.get('status', 0) >= 400 and r.get('status') != 404],
              'redirect_or_transport_errors': [r for r in rows if r.get('error')], 'pages': rows}
    target = ROOT / 'reports/internal-links-404.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('seed_count', 'discovered_unique_links', 'discovered_checked', 'truncated', 'checked_total', 'status_counts')}))
    print(json.dumps(report['proven_404'], ensure_ascii=False))

if __name__ == '__main__':
    socket.setdefaulttimeout(30)
    run()