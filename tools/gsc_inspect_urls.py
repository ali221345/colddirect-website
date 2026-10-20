#!/usr/bin/env python3
"""Read-only URL Inspection for a few URLs. Prints sanitised index status only.

Usage: python tools/gsc_inspect_urls.py <url> [<url> ...]
Auth: GSC_CREDENTIALS_JSON env var or local key file (see tools/request_indexing.get_credentials).
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from google.auth.transport.requests import AuthorizedSession  # noqa: E402
from request_indexing import get_credentials  # noqa: E402

SITE = "https://www.colddirect.co.uk/"
FIELDS = ["verdict", "coverageState", "lastCrawlTime", "indexingState", "robotsTxtState", "pageFetchState",
          "googleCanonical", "userCanonical", "crawledAs", "referringUrls", "sitemap"]


def main() -> int:
    s = AuthorizedSession(get_credentials())
    for u in sys.argv[1:]:
        r = s.post("https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",
                   json={"inspectionUrl": u, "siteUrl": SITE}, timeout=90)
        print(f"== {u}  (HTTP {r.status_code})")
        if r.status_code != 200:
            print("   ", re.sub(r"\d{6,}", "<id>", r.text)[:200])
            continue
        x = r.json().get("inspectionResult", {}).get("indexStatusResult", {})
        for f in FIELDS:
            print(f"   {f}: {x.get(f, '-')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
