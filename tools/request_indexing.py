#!/usr/bin/env python3
"""Request Google URL update notifications after a content pass.

Uses Indexing API (urlNotifications:publish) plus Search Console URL Inspection.
Auth: GOOGLE_APPLICATION_CREDENTIALS or C:\\Users\\khora\\gsc-oauth.json
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SITE = "https://www.colddirect.co.uk/"
URLS = [
    "https://www.colddirect.co.uk/fridge-repair-london/",
    "https://www.colddirect.co.uk/freezer-repair-london/",
    "https://www.colddirect.co.uk/ice-cream-machine-repair-london/",
    "https://www.colddirect.co.uk/blog/different-types-of-ice",
    "https://www.colddirect.co.uk/blog/prevent-commercial-fridge-breakdown/",
    "https://www.colddirect.co.uk/blog/commercial-freezer-temperature-guide/",
]
KEY_CANDIDATES = [
    Path(r"C:\Users\khora\gsc-oauth.json"),
    Path(__file__).resolve().parents[1] / "gsc-key.json",
]
SCOPES = [
    "https://www.googleapis.com/auth/webmasters",
    "https://www.googleapis.com/auth/indexing",
]


def credentials():
    env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    paths = [Path(env)] if env else []
    paths.extend(KEY_CANDIDATES)
    for p in paths:
        if p and p.is_file():
            return service_account.Credentials.from_service_account_file(str(p), scopes=SCOPES)
    raise SystemExit("No GSC key. Set GOOGLE_APPLICATION_CREDENTIALS or place gsc-oauth.json")


def main() -> int:
    creds = credentials()
    indexing = build("indexing", "v3", credentials=creds, cache_discovery=False)
    gsc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
    try:
        gsc.sitemaps().submit(siteUrl=SITE, feedpath=SITE + "sitemap.xml").execute()
        print("sitemap_submit_ok")
    except HttpError as e:
        print("sitemap_submit_error", e.resp.status, e.content.decode("utf-8", "replace")[:400])
    ok = True
    for url in URLS:
        print("URL", url)
        try:
            notify = indexing.urlNotifications().publish(
                body={"url": url, "type": "URL_UPDATED"}
            ).execute()
            print("indexing_notify", json.dumps(notify, indent=2))
        except HttpError as e:
            ok = False
            print("indexing_notify_error", e.resp.status, e.content.decode("utf-8", "replace")[:800])
        try:
            inspect = gsc.urlInspection().index().inspect(
                body={"inspectionUrl": url, "siteUrl": SITE}
            ).execute()
            status = inspect.get("inspectionResult", {}).get("indexStatusResult", {})
            print(
                "inspect",
                status.get("coverageState"),
                status.get("lastCrawlTime"),
                status.get("googleCanonical"),
                status.get("userCanonical"),
            )
        except HttpError as e:
            ok = False
            print("inspect_error", e.resp.status, e.content.decode("utf-8", "replace")[:800])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
