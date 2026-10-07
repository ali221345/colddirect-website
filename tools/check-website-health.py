"""Offline behavior fixtures for the read-only public health audit."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('health', Path(__file__).with_name('website-health.py'))
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)
SITE = health.SITE
HTML = '<title>Repair</title><h1>Repair</h1><link rel="canonical" href="https://www.colddirect.co.uk/">'

class AuditTests(unittest.TestCase):
    def test_redirect_loop_and_query(self):
        calls = []
        def getter(url):
            calls.append(url)
            return 301, {'Location': '/b?x=1' if '/a?' in url else '/a?x=1'}, ''
        result = health.follow(SITE + 'a?x=1', getter)
        self.assertEqual(result['error'], 'redirect_loop')
        self.assertEqual(calls, [SITE + 'a?x=1', SITE + 'b?x=1'])
        # Relative references keep the query when supplied, and RFC URL resolution
        # correctly removes it when the Location explicitly replaces the path.
        result = health.follow(SITE + 'a?x=1', lambda u: (301, {'Location': '?x=2'}, '') if u.endswith('x=1') else (200, {}, HTML))
        self.assertEqual(result['final_url'], SITE + 'a?x=2')

    def test_metadata_header_noindex_canonical(self):
        body = HTML.replace('href="https://www.colddirect.co.uk/"', 'href="/different/"')
        body += '<meta name="robots" content="noindex"><script type="application/ld+json">broken</script>'
        row, issues = health.inspect(SITE, True, lambda u: (200, {'X-Robots-Tag': 'Googlebot: noindex'}, body))
        self.assertEqual(row['title'], 'Repair')
        self.assertEqual({x['kind'] for x in issues}, {'noindex', 'canonical_mismatch', 'invalid_jsonld'})
        _, header_only = health.inspect(SITE, True, lambda u: (200, {'X-Robots-Tag': 'noindex'}, HTML))
        self.assertEqual([x['kind'] for x in header_only], ['noindex'])
        self.assertFalse(health.header_noindex('bingbot: noindex'))
        self.assertTrue(health.header_noindex('bingbot: noindex\nnoindex'))
        self.assertTrue(health.header_noindex('googlebot: noindex, nofollow'))

    def test_confirmed_http_errors_and_scope(self):
        row, issues = health.inspect(SITE, True, lambda u: (404, {}, 'Missing'))
        self.assertEqual(issues, [health.issue(SITE, 'http_status', '404')])
        self.assertNotIn('body', row)
        for url in [SITE + 'daily-job.php', SITE + 'cold-agent-v3.asp?a=create', SITE + '%64aily-job.php', SITE + 'safe/../%63old-agent-v3.asp', SITE + 'any.php', 'https://other.example/']:
            with self.assertRaises(health.AuditError):
                health.safe_url(url)

    def test_reviewed_file_alias_canonical(self):
        for alias, canonical in health.EXPECTED_CANONICALS.items():
            valid = HTML.replace(SITE, canonical)
            _, issues = health.inspect(alias, False, lambda u: (200, {}, valid))
            self.assertEqual(issues, [])
            invalid = HTML.replace(SITE, SITE + 'unexpected/')
            _, issues = health.inspect(alias, False, lambda u: (200, {}, invalid))
            self.assertEqual([x['kind'] for x in issues], ['canonical_mismatch'])

    def test_redirect_limit_and_operation_redirect(self):
        row = health.follow(SITE + '0', lambda u: (301, {'Location': '/' + str(int(u.rsplit('/', 1)[1]) + 1)}, ''))
        self.assertEqual(row['error'], 'redirect_limit')
        self.assertEqual(len(row['chain']), 9)
        row = health.follow(SITE, lambda u: (301, {'Location': '/%64aily-job.php'}, ''))
        self.assertEqual(row['error'], 'redirect_outside_public_scope')

    def test_successful_complete_snapshot_and_robots(self):
        workspace = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=workspace) as d:
            self.assertTrue(Path(d).resolve().is_relative_to(workspace))
            def getter(url):
                if url.endswith('sitemap.xml'):
                    return 200, {}, '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>' + SITE + '</loc></url></urlset>'
                if url.endswith('robots.txt'):
                    return 200, {}, 'User-agent: Googlebot\nDisallow: /\nUser-agent: *\nAllow: /'
                target = url.split('?')[0]
                html = HTML.replace(SITE, health.EXPECTED_CANONICALS.get(target, target))
                return 200, {}, html
            result = health.run(getter, Path(d))
            self.assertTrue(result['baseline_created'])
            self.assertEqual(result['changes'], {'new': [], 'resolved': []})
            self.assertEqual([x['kind'] for x in result['issues']], ['robots_blocked'])
            self.assertTrue((Path(d) / 'latest.json').exists())

    def test_transport_failure_preserves_latest(self):
        workspace = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=workspace) as d:
            self.assertTrue(Path(d).resolve().is_relative_to(workspace))
            output = Path(d)
            health.save({'issues': [], 'pages': []}, output)
            original = (output / 'latest.json').read_bytes()
            def getter(url):
                if url.endswith('sitemap.xml'):
                    return 200, {}, '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>' + SITE + '</loc></url></urlset>'
                if url.endswith('robots.txt'):
                    return 200, {}, 'User-agent: *\nAllow: /'
                raise health.AuditError('transport failed')
            with self.assertRaises(health.AuditError):
                health.run(getter, output)
            self.assertEqual((output / 'latest.json').read_bytes(), original)
            self.assertEqual(len(list(output.glob('*.json'))), 2)

    def test_issue_deltas_ignore_noise(self):
        defect = health.issue(SITE, 'noindex')
        baseline = {'issues': [defect], 'checked_at': 'old', 'pages': [{'title': 'old'}]}
        current = {'issues': [defect], 'checked_at': 'new', 'pages': [{'title': 'new'}]}
        self.assertEqual(health.compare(baseline, current), {'new': [], 'resolved': []})
        self.assertEqual(health.compare(baseline, {'issues': []})['resolved'], [defect])
        self.assertEqual(health.compare(None, current), {'new': [], 'resolved': []})

if __name__ == '__main__':
    unittest.main()

