#!/usr/bin/env python3
"""Targeted Search Console ping: re-submit the sitemap, URL-Inspect and (best effort) Indexing-API notify
a short list of URLs. Prints sanitised results only (no credentials, no account ids).

Usage: python tools/gsc_targeted_ping.py [url ...]      (defaults to the 2026-10-21 de-cannibalisation set)
"""
import re
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from google.auth.transport.requests import AuthorizedSession  # noqa: E402
from request_indexing import get_credentials  # noqa: E402

SITE = "https://www.colddirect.co.uk/"
SITEMAP = SITE + "sitemap.xml"
DEFAULT = [
    "",  # homepage
    "commercial-fridge-repair-london/",
    "fridge-repair-london/",
    "freezer-repair-london/",
    "commercial-freezer-repair-london/",
    "cold-room-repair-london/",
    "ice-machine-repair-london/",
    "ice-cream-machine-repair-london/",
    "catering-repair-london/",
    "commercial-appliances-repair-london/",
]


def scrub(s: str) -> str:
    return re.sub(r"\d{6,}", "<id>", s or "")[:200]


def main() -> int:
    urls = [u if u.startswith("http") else SITE + u for u in (sys.argv[1:] or DEFAULT)]
    s = AuthorizedSession(get_credentials())
    feed = urllib.parse.quote(SITEMAP, safe="")
    site = urllib.parse.quote(SITE, safe="")
    api = f"https://www.googleapis.com/webmasters/v3/sites/{site}/sitemaps/{feed}"
    r = s.put(api, timeout=30)
    print(f"sitemap submit: HTTP {r.status_code}")
    g = s.get(api, timeout=30)
    if g.status_code == 200:
        d = g.json()
        print(f"  lastSubmitted={d.get('lastSubmitted')} lastDownloaded={d.get('lastDownloaded')} pending={d.get('isPending')} errors={d.get('errors', 0)} warnings={d.get('warnings', 0)}")
    index_api_ok = True
    for u in urls:
        verdict, state, crawl = "?", "?", "?"
        try:
            ir = s.post("https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",
                        json={"inspectionUrl": u, "siteUrl": SITE}, timeout=60)
            if ir.status_code == 200:
                x = ir.json().get("inspectionResult", {}).get("indexStatusResult", {})
                verdict, state, crawl = x.get("verdict", "?"), x.get("coverageState", "?"), x.get("lastCrawlTime", "?")
            else:
                verdict = f"HTTP {ir.status_code}"
        except Exception as e:  # noqa: BLE001
            verdict = f"error {type(e).__name__}"
        note = ""
        if index_api_ok:
            pr = s.post("https://indexing.googleapis.com/v3/urlNotifications:publish",
                        json={"url": u, "type": "URL_UPDATED"}, timeout=30)
            if pr.status_code == 200:
                note = "indexing API: notified"
            else:
                index_api_ok = False
                note = f"indexing API: HTTP {pr.status_code} ({scrub(pr.text)[:90]}) - skipping the rest"
        print(f"{u.replace(SITE, '/')} | {verdict} | {state} | lastCrawl={crawl} | {note}")
        time.sleep(1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
