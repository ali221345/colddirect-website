"""Read-only Search Console performance research; no website or indexing writes."""
import json, os, socket
from pathlib import Path
from datetime import date, datetime, timedelta, timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import httplib2, google_auth_httplib2

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'reports/gsc-keywords'
SITE = 'https://www.colddirect.co.uk/'

def main():
    socket.setdefaulttimeout(30)
    credentials = service_account.Credentials.from_service_account_file(
        os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', r'C:\Users\khora\gsc-oauth.json'),
        scopes=['https://www.googleapis.com/auth/webmasters.readonly'])
    client = build('searchconsole', 'v1', http=google_auth_httplib2.AuthorizedHttp(credentials, http=httplib2.Http(timeout=30)), cache_discovery=False)
    def query(start, end, dimensions, uk=False):
        rows = []
        for offset in range(0, 10000, 2500):
            body = dict(startDate=str(start), endDate=str(end), dimensions=dimensions, type='web', dataState='final', rowLimit=2500, startRow=offset)
            if uk:
                body['dimensionFilterGroups'] = [{'filters': [{'dimension': 'country', 'operator': 'equals', 'expression': 'gbr'}]}]
            batch = client.searchanalytics().query(siteUrl=SITE, body=body).execute(num_retries=1).get('rows', [])
            rows.extend(batch)
            if len(batch) < 2500:
                return {'rows': rows, 'bounded_truncated': False}
        return {'rows': rows, 'bounded_truncated': True}
    probe = query(date.today()-timedelta(days=12), date.today()-timedelta(days=1), ['date'])
    if not probe['rows']:
        raise RuntimeError('No final daily performance data available')
    end = date.fromisoformat(max(r['keys'][0] for r in probe['rows']))
    report = {'collected_at': datetime.now(timezone.utc).isoformat(), 'site': SITE, 'type': 'web', 'data_state': 'final', 'source': 'Google Search Console API', 'date_timezone': 'Pacific Time as supplied by Search Console', 'limitations': ['Query rows omit anonymized queries and may not sum to totals.', 'Impressions are observed visibility for this property, not keyword market search volume.', 'Average position is an aggregate, not a fixed ranking.', 'This records a baseline; no ranking or conversion uplift is attributed.'], 'windows': {}}
    for label, last in [('current', end), ('previous', end-timedelta(days=28))]:
        start = last-timedelta(days=27)
        item = {'start': str(start), 'end': str(last), 'days': 28}
        for name, dims, uk in [('totals', [], False), ('queries', ['query'], False), ('pages', ['page'], False), ('query_pages', ['query','page'], False), ('uk_query_pages', ['query','page'], True), ('devices', ['device'], False)]:
            item[name] = query(start, last, dims, uk)
            print(f'{label} {name}: {len(item[name]["rows"])} rows', flush=True)
        report['windows'][label] = item
    OUT.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(report, indent=2, ensure_ascii=False)
    (OUT / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json')).write_text(encoded, encoding='utf-8')
    temporary = OUT/'latest.tmp'
    temporary.write_text(encoded, encoding='utf-8'); temporary.replace(OUT/'latest.json')
    print(json.dumps({'completed': True, 'periods': {k: {'start':v['start'],'end':v['end'],'totals':v['totals']['rows']} for k,v in report['windows'].items()}}, ensure_ascii=False))

if __name__ == '__main__':
    try:
        main()
    except HttpError as error:
        print(f'Research incomplete: API HTTP {error.resp.status}; previous complete report preserved')
        raise SystemExit(1)
    except Exception as error:
        print(f'Research incomplete: {type(error).__name__}; previous complete report preserved')
        raise SystemExit(1)

