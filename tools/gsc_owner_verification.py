#!/usr/bin/env python3
"""Targeted GSC Owner verification: one API permission test, sitemap, and 13 inspections.

Never prints credentials, credential-derived identities, project IDs, or raw Google errors.
The single Indexing API call is a permission diagnostic, not recurring submission support
for ordinary commercial pages.
"""
import json
import os
import sys
import urllib.parse
SITE = "https://www.colddirect.co.uk/"
SITEMAP = SITE + "sitemap.xml"
PATHS = [
    "/commercial-fridge-repair-enfield/",
    "/commercial-fridge-repair-central-london/",
    "/blast-chiller-repair-north-london/",
    "/chiller-repair-north-london/",
    "/cold-room-repair-barnet/",
    "/cold-room-repair-edgware/",
    "/cold-room-repair-finchley/",
    "/cold-room-repair-tottenham/",
    "/cold-room-repair-wembley/",
    "/cold-room-repair-harrow/",
    "/cold-room-repair-palmers-green/",
    "/cold-room-repair-southgate/",
    "/cold-room-repair-wood-green/",
]
SITEMAP_ENDPOINT = (
    "https://www.googleapis.com/webmasters/v3/sites/"
    + urllib.parse.quote(SITE, safe="")
    + "/sitemaps/"
    + urllib.parse.quote(SITEMAP, safe="")
)
INSPECT_ENDPOINT = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
INDEXING_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"


def selftest():
    assert len(PATHS) == 13 and len(set(PATHS)) == 13
    assert all(path.startswith("/") and path.endswith("/") for path in PATHS)
    assert "https%3A%2F%2Fwww.colddirect.co.uk%2F" in SITEMAP_ENDPOINT
    assert SITEMAP_ENDPOINT.endswith("sitemap.xml")
    print("gsc_owner_verification selftest OK: 13 unique watchlist URLs")


def main():
    from google.auth.transport.requests import AuthorizedSession
    from request_indexing import get_credentials

    session = AuthorizedSession(get_credentials())
    result = {"indexingPermissionTest": {}, "sitemap": {}, "inspections": []}

    # Exactly one diagnostic call; do not hammer the API or submit the other pages.
    test_url = SITE.rstrip("/") + PATHS[0]
    response = session.post(
        INDEXING_ENDPOINT,
        json={"url": test_url, "type": "URL_UPDATED"},
        timeout=30,
    )
    result["indexingPermissionTest"] = {"path": PATHS[0], "httpStatus": response.status_code}

    response = session.put(SITEMAP_ENDPOINT, timeout=30)
    result["sitemap"]["submitHttpStatus"] = response.status_code
    response = session.get(SITEMAP_ENDPOINT, timeout=30)
    result["sitemap"]["statusHttpStatus"] = response.status_code
    if response.status_code == 200:
        data = response.json()
        result["sitemap"].update({
            "lastSubmitted": data.get("lastSubmitted", ""),
            "lastDownloaded": data.get("lastDownloaded", ""),
            "isPending": data.get("isPending"),
            "warnings": data.get("warnings"),
            "errors": data.get("errors"),
        })

    for path in PATHS:
        url = SITE.rstrip("/") + path
        response = session.post(
            INSPECT_ENDPOINT,
            json={"inspectionUrl": url, "siteUrl": SITE},
            timeout=60,
        )
        item = {"path": path, "httpStatus": response.status_code}
        if response.status_code == 200:
            status = response.json().get("inspectionResult", {}).get("indexStatusResult", {}) or {}
            item.update({
                "verdict": status.get("verdict", ""),
                "coverageState": status.get("coverageState", ""),
                "lastCrawlTime": status.get("lastCrawlTime", ""),
            })
        result["inspections"].append(item)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        lines = [
            "## GSC Owner verification",
            "",
            f"- Indexing API diagnostic: HTTP {result['indexingPermissionTest']['httpStatus']}",
            f"- Sitemap submit: HTTP {result['sitemap']['submitHttpStatus']}",
            f"- Sitemap status: HTTP {result['sitemap']['statusHttpStatus']}",
            "",
            "| URL | HTTP | Verdict | Coverage | Last crawl |",
            "|---|---:|---|---|---|",
        ]
        for item in result["inspections"]:
            lines.append(
                f"| `{item['path']}` | {item['httpStatus']} | {item.get('verdict', '-')} | "
                f"{item.get('coverageState', '-')} | {item.get('lastCrawlTime') or 'never'} |"
            )
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")

    success = (
        result["indexingPermissionTest"]["httpStatus"] == 200
        and result["sitemap"]["submitHttpStatus"] in (200, 204)
        and result["sitemap"]["statusHttpStatus"] == 200
        and all(item["httpStatus"] == 200 for item in result["inspections"])
    )
    return 0 if success else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        raise SystemExit(main())
