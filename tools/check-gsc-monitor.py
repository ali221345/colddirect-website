"""Check alerts distinguish index changes from routine crawl timestamps."""
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('gsc_monitor', Path(__file__).with_name('gsc-monitor.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
old = {'inspection': [{'url': module.SITE + 'services/', 'verdict': 'NEUTRAL', 'coverageState': 'URL is unknown to Google', 'lastCrawlTime': None}], 'sitemaps': []}
same = {'inspection': [dict(old['inspection'][0], lastCrawlTime='2026-10-08T09:00:00Z')], 'sitemaps': []}
assert module.changes(old, same) == [], 'Routine crawl timestamp should not alert'
new = {'inspection': [dict(old['inspection'][0], verdict='PASS', coverageState='Submitted and indexed')], 'sitemaps': []}
assert len(module.changes(old, new)) == 1, 'Newly indexed Services should alert'
assert module.changes(None, new) == [], 'First baseline is not measured growth'
assert len(module.changes(new, old)) == 1, 'Loss of indexed status should alert'
print('PASS: unchanged, new indexing, loss of indexing and initial baseline alert checks')
