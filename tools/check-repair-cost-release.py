"""Live approved PR18 release verification; no forms or write endpoints."""
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
from urllib.parse import urlsplit

SITE = 'https://www.colddirect.co.uk'
SLUG = '/blog/commercial-fridge-repair-cost-london'
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None

def request(url, method='GET'):
    try:
        r = build_opener(NoRedirect).open(Request(url, method=method, headers={'Accept': '*/*'}), timeout=30)
    except HTTPError as e:
        r = e
    with r:
        return r.code, r.headers.get('Location'), r.read(2000000).decode('utf-8', errors='replace')

rows = []
limitations = []
for alias in ['/', '.html', '']:
    for query in ['', '?releasecheck=6d0a4570&x=a%2Fb']:
        for method in ['GET', 'HEAD']:
            url = SITE + SLUG + alias + query
            status, location, body = request(url, method)
            assert status == (301 if alias == '' else 200), (url, method, status)
            if alias == '':
                expected = SITE + SLUG + '/' + query
                if '%2F' in query and location == expected.replace('%2F', '%252F'):
                    limitations.append({'url': url, 'method': method, 'kind': 'encoded_query_double_escape', 'location': location})
                else:
                    assert location == expected, (url, location)
            else:
                assert location is None, (url, location)
            if method == 'GET' and status == 200:
                assert '<h1>Commercial Fridge Repair Cost in London</h1>' in body
                assert 'href="' + SITE + SLUG + '/"' in body
                assert not re.search(r'<meta[^>]+(?:robots|googlebot)[^>]+noindex', body, re.I)
                ld = re.findall(r'<script[^>]+type=[\"\']application/ld\+json[\"\'][^>]*>(.*?)</script>', body, re.S | re.I)
                assert ld, 'Missing structured data'
                for block in ld:
                    json.loads(block)
            rows.append({'url': url, 'method': method, 'status': status, 'location': location})
for alias in ['/', '.html', '']:
    for method in ['GET', 'HEAD']:
        url = 'http://www.colddirect.co.uk' + SLUG + alias + '?releasecheck=6d0a4570'
        status, location, _ = request(url, method)
        assert status in (301, 308) and location and urlsplit(location).scheme == 'https', (url, method, status, location)
        rows.append({'url': url, 'method': method, 'status': status, 'location': location})
for path in ['/', '/services/', '/fridge-repair-london/', '/freezer-repair-london/', '/commercial-fridge-repair-london/', '/cold-room-repair-london/', '/blog/', '/blog/commercial-fridge-not-cooling/']:
    status, location, _ = request(SITE + path + '?releasecheck=6d0a4570')
    assert status == 200 and not location, (path, status, location)
    rows.append({'url': SITE + path, 'method': 'GET', 'status': status})
# Observe legacy directory blogs separately; their pre-existing defects are not repaired here.
observed = []
for path in ['/blog/commercial-freezer-ice-buildup-causes/', '/blog/cold-room-temperature-fluctuation/']:
    status, location, _ = request(SITE + path + '?releasecheck=6d0a4570')
    observed.append({'url': SITE + path, 'status': status, 'location': location})
report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'commit': '6d0a4570e7f8c86876e0bade9fe2522c37efd777', 'passed_checks': len(rows) - len(limitations), 'rows': rows, 'limitations': limitations, 'legacy_observations': observed}
Path('reports/repair-cost-release.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'passed_checks': len(rows) - len(limitations), 'limitations': limitations, 'legacy_observations': observed}))

