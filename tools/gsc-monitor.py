"""Daily read-only Search Console snapshots. Never submits Indexing API notifications."""
import json
import os
import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import httplib2
import google_auth_httplib2

SITE = 'https://www.colddirect.co.uk/'
ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'reports/gsc-monitor'
FIELDS = ('verdict', 'coverageState', 'lastCrawlTime', 'googleCanonical', 'userCanonical', 'indexingState', 'pageFetchState')

def changes(previous, current):
    if not previous:
        return []
    old = {row['url']: row for row in previous['inspection']}
    updates = []
    for row in current['inspection']:
        prior = old.get(row['url'])
        if prior and any(prior.get(key) != row.get(key) for key in ('verdict', 'coverageState', 'googleCanonical', 'indexingState')):
            updates.append({'url': row['url'], 'before': {key: prior.get(key) for key in ('verdict', 'coverageState', 'googleCanonical', 'indexingState')}, 'after': {key: row.get(key) for key in ('verdict', 'coverageState', 'googleCanonical', 'indexingState')}})
    before = previous.get('sitemaps', [])
    after = current.get('sitemaps', [])
    if before != after:
        updates.append({'sitemap_status_changed': True, 'before': before, 'after': after})
    return updates

def save_snapshot(report):
    # Called only after every API request succeeds; partial runs preserve the last baseline.
    OUTPUT.mkdir(parents=True, exist_ok=True)
    latest = OUTPUT / 'latest.json'
    previous = json.loads(latest.read_text(encoding='utf-8')) if latest.exists() else None
    report['changes'] = changes(previous, report)
    report['baseline_created'] = previous is None
    encoded = json.dumps(report, indent=2) + '\n'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    (OUTPUT / f'{stamp}.json').write_text(encoded, encoding='utf-8')
    temporary = OUTPUT / 'latest.tmp'
    temporary.write_text(encoded, encoding='utf-8')
    temporary.replace(latest)
    return report

def main():
    socket.setdefaulttimeout(30)
    key = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', r'C:\Users\khora\gsc-oauth.json')
    credential_info = json.loads(Path(key).read_text(encoding='utf-8'))
    def make_client():
        credentials = service_account.Credentials.from_service_account_info(credential_info, scopes=['https://www.googleapis.com/auth/webmasters.readonly'])
        http = google_auth_httplib2.AuthorizedHttp(credentials, http=httplib2.Http(timeout=30))
        return build('searchconsole', 'v1', http=http, cache_discovery=False)
    client = make_client()
    sites = client.sites().list().execute(num_retries=2).get('siteEntry', [])
    selected = next((entry for entry in sites if entry['siteUrl'] == SITE), None)
    if not selected:
        raise RuntimeError('Search Console property access unavailable')
    with urlopen(SITE + 'sitemap.xml', timeout=30) as response:
        document = ET.fromstring(response.read())
    urls = sorted({item.text for item in document.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')})
    if not urls or len(urls) > 200:
        raise RuntimeError('Unexpected sitemap size; review before inspecting URLs')
    if any(not url.startswith(SITE) or urlsplit(url).netloc != 'www.colddirect.co.uk' for url in urls):
        raise RuntimeError('Sitemap includes an unexpected website')
    sitemap_response = client.sitemaps().list(siteUrl=SITE).execute(num_retries=2).get('sitemap', [])
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'site': SITE, 'sitemap_urls': len(urls), 'permission': selected.get('permissionLevel'), 'inspection': [], 'sitemaps': [{key: item.get(key) for key in ('path', 'isPending', 'errors', 'warnings')} for item in sitemap_response]}
    local = threading.local()
    def inspect(url):
        if not hasattr(local, 'client'):
            local.client = make_client()
        result = local.client.urlInspection().index().inspect(body={'siteUrl': SITE, 'inspectionUrl': url}).execute(num_retries=1)
        status = result.get('inspectionResult', {}).get('indexStatusResult', {})
        if not status:
            raise RuntimeError('Google returned no inspection status; baseline preserved')
        return {'url': url, **{key: status.get(key) for key in FIELDS}}
    print(f'Inspecting {len(urls)} sitemap URLs', flush=True)
    # Each worker owns its HTTP client; googleapiclient transports are not thread-safe.
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i, row in enumerate(pool.map(inspect, urls), 1):
            report['inspection'].append(row)
            if i % 25 == 0:
                print(f'Inspected {i}/{len(urls)} URLs', flush=True)
    report['verdict_counts'] = dict(Counter(row.get('verdict', 'UNKNOWN') for row in report['inspection']))
    saved = save_snapshot(report)
    print(json.dumps({key: saved[key] for key in ('checked_at', 'sitemap_urls', 'verdict_counts', 'baseline_created', 'changes')}, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except HttpError as error:
        print(f'Search Console monitor failed: HTTP {error.resp.status}; last baseline preserved')
        raise SystemExit(1)
    except Exception as error:
        print(f'Search Console monitor failed: {type(error).__name__}; last baseline preserved')
        raise SystemExit(1)
