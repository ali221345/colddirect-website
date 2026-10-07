"""Generate canonical public URLs from the deployment root, not repository mirrors."""
import os
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.error import HTTPError
import xml.etree.ElementTree as ET

BASE = 'https://www.colddirect.co.uk'
NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
EXCLUDED = {'colddirect-public-html', 'node_modules', 'agent', 'docs', 'tools',
            'scripts', 'templates', 'includes', 'assets', 'images', 'css', 'js',
            'logs', 'reports', 'seo-audit', 'conf', 'mnt', 'public', 'app',
            'plesk-upload', 'plesk-hero-upload', 'preview-colddirect-homepage',
            'agent-status', '_wa_src'}

class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals = []
        self.noindex = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link' and 'canonical' in attrs.get('rel', '').lower().split():
            self.canonicals.append(attrs.get('href', ''))
        if tag == 'meta' and attrs.get('name', '').lower() in ('robots', 'googlebot'):
            self.noindex |= 'noindex' in attrs.get('content', '').lower()

def collect_urls(site_folder):
    root = Path(site_folder)
    robots = RobotFileParser()
    robots_file = root / 'robots.txt'
    robots.parse(robots_file.read_text(encoding='utf-8-sig').splitlines() if robots_file.exists() else [])
    candidates = {}
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not d.startswith(('.', '_')))
        for name in sorted(files):
            if not name.endswith('.html') or name.startswith('google'):
                continue
            file = Path(folder) / name
            rel = file.relative_to(root).as_posix()
            metadata = Metadata()
            metadata.feed(file.read_text(encoding='utf-8-sig', errors='replace'))
            if len(metadata.canonicals) != 1 or not metadata.canonicals[0]:
                continue
            canonical = urljoin(BASE + '/', metadata.canonicals[0])
            parsed = urlsplit(canonical)
            if parsed.scheme != 'https' or parsed.netloc != 'www.colddirect.co.uk' or parsed.query or parsed.fragment:
                continue
            stem = '/' + rel[:-5]
            if name == 'index.html':
                stem = '/' + rel[:-10]
                aliases = {stem, stem.rstrip('/'), '/' + rel}
            else:
                aliases = {stem, stem + '/', '/' + rel}
            # Pages canonicalised to another page are aliases, not new discovery URLs.
            if parsed.path not in aliases:
                continue
            candidates.setdefault(canonical, []).append((name == 'index.html', metadata.noindex))
    urls = []
    for canonical, variants in candidates.items():
        # Directory documents are actually served ahead of duplicate root HTML files.
        directory = [v for v in variants if v[0]]
        selected = directory or variants
        if any(noindex for _, noindex in selected):
            continue
        if not robots.can_fetch('Googlebot', canonical) or not robots.can_fetch('*', canonical):
            continue
        urls.append(canonical)
    return sorted(urls)

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def fetch_page(url):
    try:
        response = build_opener(NoRedirect).open(Request(url, headers={'User-Agent': 'ColdDirect-Sitemap/1.0'}), timeout=20)
    except HTTPError as exc:
        response = exc
    with response:
        return response.code, dict(response.headers.items()), response.read(2000000).decode('utf-8', errors='replace')

def verify_urls(urls, fetch=fetch_page):
    cache = {}
    def resolve(url):
        seen = set()
        for _ in range(8):
            parsed = urlsplit(url)
            if parsed.scheme != 'https' or parsed.netloc != 'www.colddirect.co.uk' or url in seen:
                return None
            seen.add(url)
            if url not in cache:
                cache[url] = fetch(url)
            status, headers, body = cache[url]
            headers = {k.lower(): v for k, v in headers.items()}
            if status == 429 or status >= 500:
                raise RuntimeError(f'Temporary HTTP {status}: {url}; existing sitemap preserved')
            if status in (301, 302, 307, 308) and headers.get('location'):
                url = urljoin(url, headers['location'])
                continue
            if status != 200:
                return None
            metadata = Metadata()
            metadata.feed(body)
            if metadata.noindex or 'noindex' in headers.get('x-robots-tag', '').lower():
                return None
            if len(metadata.canonicals) != 1:
                return None
            return url, urljoin(url, metadata.canonicals[0])
        return None
    verified = set()
    for url in urls:
        page = resolve(url)
        if page:
            preferred = resolve(page[1])
            if preferred:
                # A canonical pointing to a redirect is normalized to the served URL.
                confirmation = resolve(preferred[1])
                if confirmation and confirmation[0] == preferred[0]:
                    verified.add(preferred[0])
        else:
            print(f'Sitemap excludes unavailable/noindex/loop URL: {url}')
    return sorted(verified)

def generate_sitemap(site_folder, verify_live=True):
    root = Path(site_folder)
    urls = collect_urls(root)
    if verify_live:
        urls = verify_urls(urls)
    robots = RobotFileParser()
    robots.parse((root / 'robots.txt').read_text(encoding='utf-8-sig').splitlines())
    urls = [url for url in urls if robots.can_fetch('Googlebot', url) and robots.can_fetch('*', url)]
    if not urls or BASE + '/' not in urls:
        raise ValueError('Refusing to write a sitemap without public URLs and homepage')
    ET.register_namespace('', NS)
    document = ET.Element(f'{{{NS}}}urlset')
    for url in urls:
        entry = ET.SubElement(document, f'{{{NS}}}url')
        ET.SubElement(entry, f'{{{NS}}}loc').text = url
    # A checkout/run timestamp is not a page modification date. Omit unverified lastmod.
    ET.indent(document, space='  ')
    output = ET.tostring(document, encoding='utf-8', xml_declaration=True) + b'\n'
    (root / 'sitemap.xml').write_bytes(output)
    mirror = root / 'colddirect-public-html'
    if mirror.is_dir():
        (mirror / 'sitemap.xml').write_bytes(output)
    print(f'Sitemap: {len(urls)} unique public canonical URLs')
