#!/usr/bin/env python3
"""Request Google indexing for all pages touched by the same-day tag pass.

Uses the Indexing API (urlNotifications:publish) now that the service
account has Owner-level Search Console access, plus a sitemap resubmit.
Reads the page list from agent/sameday-tag-report.json.

Auth: GOOGLE_APPLICATION_CREDENTIALS or C:\\Users\\khora\\gsc-oauth.json
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SITE = "https://www.colddirect.co.uk/"
ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "agent" / "sameday-tag-report.json"
LOG = ROOT / "agent" / "indexing-request-log.json"
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
    raise SystemExit("No GSC key found.")


def urls_from_report():
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    urls = []
    for entry in data:
        slug = entry["file"][:-5]  # strip .html
        if slug == "index":
            urls.append(SITE)
        else:
            urls.append(f"{SITE}{slug}/")
    return urls


def main():
    creds = credentials()
    indexing = build("indexing", "v3", credentials=creds, cache_discovery=False)
    gsc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    try:
        gsc.sitemaps().submit(siteUrl=SITE, feedpath=SITE + "sitemap.xml").execute()
        print("sitemap_submit_ok")
    except HttpError as e:
        print("sitemap_submit_error", e.resp.status, e.content.decode("utf-8", "replace")[:300])

    urls = urls_from_report()
    print(f"Requesting indexing for {len(urls)} URLs")

    results = []
    for i, url in enumerate(urls, 1):
        entry = {"url": url}
        try:
            notify = indexing.urlNotifications().publish(
                body={"url": url, "type": "URL_UPDATED"}
            ).execute()
            entry["status"] = "ok"
            entry["response"] = notify
            print(f"[{i}/{len(urls)}] OK   {url}")
        except HttpError as e:
            entry["status"] = "error"
            entry["error"] = f"{e.resp.status} {e.content.decode('utf-8', 'replace')[:300]}"
            print(f"[{i}/{len(urls)}] FAIL {url} -> {entry['error'][:120]}")
        results.append(entry)
        time.sleep(1)  # gentle pacing, avoid burst-rate issues

    LOG.write_text(json.dumps(results, indent=2), encoding="utf-8")
    ok_count = sum(1 for r in results if r["status"] == "ok")
    print(f"\nDone: {ok_count}/{len(urls)} succeeded. Log written to {LOG}")


if __name__ == "__main__":
    main()
