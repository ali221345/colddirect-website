#!/usr/bin/env python3
"""
Inspect & Request Google Search Console Indexing + Sitemap Submission for Cold Direct.
Supports both GitHub Actions (GSC_CREDENTIALS_JSON env var) and local service account key files.
"""
import json
import os
from pathlib import Path
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

ROOT = Path(__file__).resolve().parents[1]

SCOPES = [
    "https://www.googleapis.com/auth/webmasters",
    "https://www.googleapis.com/auth/indexing",
]

SITE_URL = "https://www.colddirect.co.uk/"

DEFAULT_URLS = [
    "https://www.colddirect.co.uk/",
    "https://www.colddirect.co.uk/services/",
    "https://www.colddirect.co.uk/freezer-room-repair-london/",
    "https://www.colddirect.co.uk/commercial-appliances-repair-london/",
    "https://www.colddirect.co.uk/chiller-repairs-london/",
    "https://www.colddirect.co.uk/chiller-repair-london/",
    "https://www.colddirect.co.uk/cold-room-repair-london/",
    "https://www.colddirect.co.uk/commercial-fridge-repair-london/",
    "https://www.colddirect.co.uk/commercial-freezer-repair-london/",
    "https://www.colddirect.co.uk/catering-repair-london/",
    "https://www.colddirect.co.uk/appliances-repair-london/",
    "https://www.colddirect.co.uk/blog/different-types-of-ice/",
    "https://www.colddirect.co.uk/blog/types-of-cold-storage/",
    "https://www.colddirect.co.uk/blog/why-commercial-freezer-icing-up/",
    "https://www.colddirect.co.uk/blog/cold-room-temperature-fluctuation/",
    "https://www.colddirect.co.uk/blog/commercial-fridge-not-cooling/",
]


def get_credentials():
    raw_json = os.environ.get("GSC_CREDENTIALS_JSON", "").strip()
    if raw_json:
        info = json.loads(raw_json)
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)

    key_candidates = [
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
        r"C:\Users\khora\gsc-oauth.json",
        str(ROOT / "gsc-key.json"),
        str(ROOT / "credentials.json"),
        str(ROOT / "seo-audit" / "gsc-key.json"),
    ]
    for candidate in key_candidates:
        if candidate and os.path.exists(candidate):
            return service_account.Credentials.from_service_account_file(candidate, scopes=SCOPES)

    raise FileNotFoundError(
        "No GSC credentials found in GSC_CREDENTIALS_JSON env var or local key files."
    )


def run_indexing(extra_urls=None):
    creds = get_credentials()
    session = AuthorizedSession(creds)

    # 1. Submit sitemap.xml in GSC
    sitemap_endpoint = (
        "https://www.googleapis.com/webmasters/v3/sites/"
        "https%3A%2F%2Fwww.colddirect.co.uk%2F/sitemaps/"
        "https%3A%2F%2Fwww.colddirect.co.uk%2Fsitemap.xml"
    )
    sm_res = session.put(sitemap_endpoint)
    print(f"[SITEMAP SUBMIT] status={sm_res.status_code}")

    urls = list(dict.fromkeys(DEFAULT_URLS + (extra_urls or [])))
    results = []

    # 2. Inspect URLs via Search Console URL Inspection API + Indexing API
    inspect_endpoint = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
    indexing_endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"

    for u in urls:
        verdict = "UNKNOWN"
        coverage = "UNKNOWN"
        try:
            r = session.post(
                inspect_endpoint,
                json={"inspectionUrl": u, "siteUrl": SITE_URL},
                timeout=30,
            )
            if r.status_code == 200:
                idx = r.json().get("inspectionResult", {}).get("indexStatusResult", {})
                verdict = idx.get("verdict", "UNKNOWN")
                coverage = idx.get("coverageState", "UNKNOWN")
                print(f"[INSPECT 200] {u} -> verdict={verdict} | state={coverage}")
            else:
                print(f"[INSPECT {r.status_code}] {u}")
        except Exception as exc:
            print(f"[INSPECT ERR] {u} -> {exc}")

        try:
            r2 = session.post(
                indexing_endpoint,
                json={"url": u, "type": "URL_UPDATED"},
                timeout=20,
            )
            print(f"[INDEXING API {r2.status_code}] {u}")
        except Exception as exc:
            print(f"[INDEXING ERR] {u} -> {exc}")

        results.append({"url": u, "verdict": verdict, "coverageState": coverage})

    return results


def main():
    run_indexing()


if __name__ == "__main__":
    main()
