#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

from ping_indexnow import build_payload, parse_sitemap, submit_indexnow


class PingIndexNowTests(unittest.TestCase):
    def test_parse_sitemap_reads_namespaced_locations(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sitemap.xml"
            path.write_text(
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                '<url><loc>https://www.colddirect.co.uk/</loc></url>'
                '<url><loc>https://www.colddirect.co.uk/soho/</loc></url>'
                '</urlset>',
                encoding="utf-8",
            )
            self.assertEqual(
                parse_sitemap(path),
                ["https://www.colddirect.co.uk/", "https://www.colddirect.co.uk/soho/"],
            )

    def test_build_payload_deduplicates_urls_and_sets_key_location(self):
        key = "09f0efc65468d3e8598408ac29953023"
        payload = build_payload(key, [
            "https://www.colddirect.co.uk/one/",
            "https://www.colddirect.co.uk/two/",
            "https://www.colddirect.co.uk/one/",
        ])
        self.assertEqual(payload["host"], "www.colddirect.co.uk")
        self.assertEqual(payload["key"], key)
        self.assertEqual(payload["keyLocation"], f"https://www.colddirect.co.uk/{key}.txt")
        self.assertEqual(payload["urlList"], [
            "https://www.colddirect.co.uk/one/",
            "https://www.colddirect.co.uk/two/",
        ])

    def test_submit_indexnow_accepts_http_202(self):
        seen = {}

        class Response:
            status = 202
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False

        def fake_urlopen(request, timeout):
            seen["url"] = request.full_url
            seen["payload"] = json.loads(request.data.decode("utf-8"))
            seen["timeout"] = timeout
            return Response()

        payload = build_payload("09f0efc65468d3e8598408ac29953023", ["https://www.colddirect.co.uk/"])
        status = submit_indexnow(payload, urlopen=fake_urlopen)
        self.assertEqual(status, 202)
        self.assertEqual(seen["url"], "https://api.indexnow.org/indexnow")
        self.assertEqual(seen["payload"], payload)
        self.assertEqual(seen["timeout"], 30)


if __name__ == "__main__":
    unittest.main()
