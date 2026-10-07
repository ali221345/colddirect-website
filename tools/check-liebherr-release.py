"""Bounded read-only live checks of the approved PR20 restoration."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
import importlib.util
spec = importlib.util.spec_from_file_location('health', Path(__file__).with_name('website-health.py'))
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args): return None
def fetch(url, method='GET'):
    if url != 'http://www.colddirect.co.uk/liebherr-fridge-repair-london/':
        h.safe_url(url)
    try:
        response = build_opener(NoRedirect).open(Request(url, method=method), timeout=30)
    except HTTPError as exc:
        response = exc
    with response:
        return response.code, response.headers.get('Location'), response.read(2000000)
route = h.SITE + 'liebherr-fridge-repair-london'
rows = []
for suffix in ['/', '/index.html', '.html', '']:
    for query in ['', '?releasecheck=51eb8251&x=1']:
        for method in ['GET', 'HEAD']:
            url = route + suffix + query
            status, location, body = fetch(url, method)
            assert status == (200 if suffix in ('/', '/index.html') else 301), (url, method, status, location)
            final = h.follow(url)
            assert final.get('status') == 200, final
            assert final['final_url'] == route + (suffix if suffix == '/index.html' else '/') + query, final
            if status == 200 and method == 'GET':
                meta = h.Metadata(); meta.feed(body.decode('utf-8'))
                assert meta.h1 == ['Liebherr Fridge Repair in London'], meta.h1
                assert meta.canonicals == [route + '/'], meta.canonicals
                assert meta.structured and all(meta.structured), meta.structured
                assert b'href="/css/styles.css?v=navwrap3"' in body
                assert b'src="/js/main.js"' in body
            rows.append({'url': url, 'method': method, 'status': status, 'final': final['final_url']})
http = 'http://www.colddirect.co.uk/liebherr-fridge-repair-london/'
status, location, _ = fetch(http, 'HEAD')
assert status in (301, 308) and location == route + '/', (status, location)
rows.append({'url':http,'status':status,'location':location})
for path in ['images/liebherr-fridge-repair-london.webp', 'css/styles.css?v=navwrap3', 'js/main.js']:
    status, location, data = fetch(h.SITE + path)
    assert status == 200 and not location and data, (path, status, location)
    if path.endswith('.webp'):
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert blob == '5fa6655a8eac924e025a54dba7dd8e81122b9fc4', blob
    rows.append({'asset':path,'status':status})
report = {'checked_at':datetime.now(timezone.utc).isoformat(), 'commit':'51eb8251e3a2c1dd60bbc3707f9bee806507e914', 'passed':len(rows), 'rows':rows}
Path('reports/liebherr-release.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print('PASS:',len(rows),'live Liebherr route/identity/asset checks')