"""Regression checks for canonical selection, deployed copies and failure preservation."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sitemap_generator', ROOT / 'agent/scripts/sitemap.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
BASE = module.BASE

def html(path, robots=''):
    return f'<html><head><link href="{BASE}{path}" rel="canonical"><meta content="{robots}" name="robots"></head></html>'

class Checks(unittest.TestCase):
    def test_local_inventory_and_mirrors(self):
        with TemporaryDirectory(dir=ROOT, prefix='.sitemap-test-') as folder:
            root = Path(folder)
            fixtures = {'index.html': html('/'), 'service.html': html('/service/'),
                        'service/index.html': html('/service/'),
                        'alias.html': html('/service/'), 'hidden.html': html('/hidden/', 'noindex'),
                        'blocked.html': html('/blocked/'), 'colddirect-public-html/copy.html': html('/copy/'),
                        'docs/report.html': html('/report/'), '.backup/old.html': html('/old/'),
                        'preview-colddirect-homepage/index.html': html('/preview-colddirect-homepage/'),
                        'conflict.html': html('/conflict/'), 'conflict/index.html': html('/conflict/', 'noindex'),
                        'foreign.html': '<link rel="canonical" href="https://other.example/foreign/">'}
            for path, body in fixtures.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(body)
            (root / 'robots.txt').write_text('User-agent: *\nDisallow: /blocked/\n')
            self.assertEqual(module.collect_urls(root), [BASE + '/', BASE + '/service/'])
            module.generate_sitemap(root, verify_live=False)
            original = (root / 'sitemap.xml').read_bytes()
            self.assertEqual(original, (root / 'colddirect-public-html/sitemap.xml').read_bytes())
            self.assertNotIn(b'lastmod', original)
            self.assertEqual(len(ET.fromstring(original)), 2)
            module.generate_sitemap(root, verify_live=False)
            self.assertEqual(original, (root / 'sitemap.xml').read_bytes())

    def test_live_redirects_canonicals_and_loops(self):
        pages = {'/old/': (301, {'Location': '/new/'}, ''),
                 '/new/': (200, {}, html('/new/')),
                 '/bare': (301, {'Location': '/bare/'}, ''),
                 '/bare/': (200, {}, html('/bare')),
                 '/alias/': (200, {}, html('/new/')),
                 '/loop/': (301, {'Location': '/loop.html'}, ''),
                 '/loop.html': (301, {'Location': '/loop/'}, ''),
                 '/gone/': (404, {}, ''), '/hidden/': (200, {}, html('/hidden/', 'noindex')),
                 '/header/': (200, {'X-Robots-Tag': 'noindex'}, html('/header/'))}
        urls = [BASE + path for path in pages]
        self.assertEqual(module.verify_urls(urls, lambda url: pages[url.removeprefix(BASE)]), [BASE + '/bare/', BASE + '/new/'])

    def test_temporary_failures_abort(self):
        for status in (429, 500, 503):
            with self.assertRaises(RuntimeError):
                module.verify_urls([BASE + '/'], lambda url: (status, {}, ''))
        def timeout(url):
            raise TimeoutError('temporary outage')
        with self.assertRaises(TimeoutError):
            module.verify_urls([BASE + '/'], timeout)

    def test_missing_home_preserves_existing_map(self):
        with TemporaryDirectory(dir=ROOT, prefix='.sitemap-test-') as folder:
            root = Path(folder)
            (root / 'robots.txt').write_text('User-agent: *\nAllow: /\n')
            (root / 'sitemap.xml').write_text('keep existing')
            with self.assertRaises(ValueError):
                module.generate_sitemap(root, verify_live=False)
            self.assertEqual((root / 'sitemap.xml').read_text(), 'keep existing')

if __name__ == '__main__':
    unittest.main()
