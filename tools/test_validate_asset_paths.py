"""Focused regression cases for the PR62 source-path guard."""
import unittest
from validate_asset_paths import in_scope, inspect


class AssetPathTests(unittest.TestCase):
    def test_historical_bug_with_variants(self):
        for prefix in ('', './', '../', '../../'):
            for asset in ('main', 'booking'):
                with self.subTest(prefix=prefix, asset=asset):
                    self.assertEqual(inspect(f"<script defer src='{prefix}js/{asset}.js?v=2#x'></script>"),
                                     [(1, f'js/{asset}.js')])
        self.assertEqual(inspect('\n<link href="css/styles.css?v=logo11" rel="stylesheet">'),
                         [(2, 'css/styles.css')])

    def test_correct_paths(self):
        for prefix in ('/', 'https://www.colddirect.co.uk/', '//cdn.example.com/'):
            self.assertEqual(inspect(f'<script src="{prefix}js/main.js"></script>'
                                     f'<script src="{prefix}js/booking.js"></script>'
                                     f'<link rel="stylesheet" href="{prefix}css/styles.css?v=x">'), [])

    def test_not_source_attributes(self):
        self.assertEqual(inspect('<!-- <script src="js/main.js"></script> -->'
                                 '<script>const x = \'<script src="js/main.js">\';</script>'
                                 '<a href="js/main.js">x</a>'
                                 '<link rel="canonical" href="css/styles.css">'
                                 '<script src="js/other.js"></script>'), [])

    def test_scope(self):
        for name in ('index.html', 'index.php', 'fridge-room-repair.html',
                     'fridge-room-repair/index.html'):
            self.assertTrue(in_scope(name), name)
        for name in ('tools/index.html', 'tools/tests/before.html', '_backup_index_old.html',
                     'colddirect-public-html/index.html', 'plesk-upload/index.html',
                     'a/b/index.html', 'contact.php', 'index.asp', 'images/photo.webp'):
            self.assertFalse(in_scope(name), name)


if __name__ == '__main__':
    unittest.main()
