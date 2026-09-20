#!/usr/bin/env python3
"""GSC ranking check for Cold Direct SEO fixes.

Usage:
  python gsc_report.py
  python gsc_report.py --start 2026-08-23 --end 2026-09-19

Auth: GOOGLE_APPLICATION_CREDENTIALS or C:\\Users\\khora\\gsc-oauth.json
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date, timedelta
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build

SITE = "https://www.colddirect.co.uk/"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
KEY_CANDIDATES = [
    Path(r"C:\Users\khora\gsc-oauth.json"),
    Path(__file__).resolve().parent / "gsc-key.json",
]
OUT_CSV = Path(__file__).resolve().parent / "gsc_report.csv"
OUT_MD = Path(__file__).resolve().parent / "gsc_followup.md"

QUERIES = [
    "cold room repair london",
    "commercial fridge repair london",
    "fridge repair london",
    "freezer repair london",
    "commercial freezer repair london",
]
WATCH_PAGES = [
    "https://www.colddirect.co.uk/",
    "https://www.colddirect.co.uk/cold-room-repairs-london",
    "https://www.colddirect.co.uk/fridge-freezer-repairs-london",
    "https://www.colddirect.co.uk/walk-in-fridge-repairs-london",
    "https://www.colddirect.co.uk/fridge-repair-london",
    "https://www.colddirect.co.uk/freezer-repair-london",
    "https://www.colddirect.co.uk/commercial-fridge-repair-london",
    "https://www.colddirect.co.uk/commercial-freezer-repair-london",
]

# Baseline from 2026-08-23 .. 2026-09-19
BASELINE = {
    "cold_room_page_pos": 2.89,
    "commercial_fridge_ctr": 0.2137,
    "commercial_fridge_pos": 12.53,
    "fridge_impr_home": 163,
    "freezer_impr_home": 60,
}


def credentials():
    import os

    env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    paths = [Path(env)] if env else []
    paths.extend(KEY_CANDIDATES)
    for p in paths:
        if p and p.is_file():
            return service_account.Credentials.from_service_account_file(str(p), scopes=SCOPES)
    raise SystemExit("No GSC key. Set GOOGLE_APPLICATION_CREDENTIALS or place gsc-oauth.json")


def query_rows(svc, start: str, end: str, dimensions: list[str], expression: str | None = None):
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": dimensions,
        "rowLimit": 250,
        "type": "web",
        "dataState": "all",
    }
    if expression:
        body["dimensionFilterGroups"] = [
            {
                "groupType": "and",
                "filters": [{"dimension": "query", "operator": "equals", "expression": expression}],
            }
        ]
    res = svc.searchanalytics().query(siteUrl=SITE, body=body).execute()
    return res.get("rows", [])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start")
    parser.add_argument("--end")
    args = parser.parse_args()
    end = args.end or (date.today() - timedelta(days=1)).isoformat()
    start = args.start or (date.fromisoformat(end) - timedelta(days=27)).isoformat()

    svc = build("searchconsole", "v1", credentials=credentials(), cache_discovery=False)
    lines = [["section", "query_or_page", "clicks", "impressions", "ctr", "position"]]
    notes = [f"# GSC follow-up {start} to {end}", ""]

    qrows = query_rows(svc, start, end, ["query"])
    top = sorted(qrows, key=lambda r: r.get("clicks", 0), reverse=True)[:10]
    for r in top:
        lines.append(["top_queries", r["keys"][0], r.get("clicks", 0), r.get("impressions", 0), r.get("ctr", 0), r.get("position", 0)])

    prows = query_rows(svc, start, end, ["page"])
    top_p = sorted(prows, key=lambda r: r.get("clicks", 0), reverse=True)[:10]
    for r in top_p:
        lines.append(["top_pages", r["keys"][0], r.get("clicks", 0), r.get("impressions", 0), r.get("ctr", 0), r.get("position", 0)])

    # 1) cold room page position
    cr = query_rows(svc, start, end, ["query", "page"], "cold room repair london")
    cr_page = next((r for r in cr if "/cold-room-repairs-london" in r["keys"][1]), None)
    if cr_page:
        pos = cr_page.get("position", 0)
        ok = 2.0 <= pos <= 3.5
        notes.append("## 1. cold room repair london on /cold-room-repairs-london")
        notes.append(f"- position {pos:.2f} (baseline {BASELINE['cold_room_page_pos']:.2f})")
        notes.append(f"- clicks {cr_page.get('clicks')} / impressions {cr_page.get('impressions')} / CTR {cr_page.get('ctr', 0):.1%}")
        notes.append(f"- stay pos 2-3: **{'YES' if ok else 'NO'}**")
        notes.append("")
        lines.append(["check1", "cold room repair london | /cold-room-repairs-london", cr_page.get("clicks", 0), cr_page.get("impressions", 0), cr_page.get("ctr", 0), pos])
    else:
        notes.append("## 1. cold room repair london — no rows for /cold-room-repairs-london")
        notes.append("")

    # 2) fridge/freezer impressions home vs target pages
    notes.append("## 2. Fridge/freezer impressions: homepage vs target pages")
    for q in ("fridge repair london", "freezer repair london"):
        rows = query_rows(svc, start, end, ["query", "page"], q)
        notes.append(f"### {q}")
        for r in sorted(rows, key=lambda x: x.get("impressions", 0), reverse=True):
            page = r["keys"][1]
            if any(w.rstrip("/") in page.rstrip("/") for w in WATCH_PAGES) or "fridge" in page or "freezer" in page:
                notes.append(f"- {page}: impr {r.get('impressions')} clicks {r.get('clicks')} pos {r.get('position', 0):.1f}")
                lines.append(["check2", f"{q} | {page}", r.get("clicks", 0), r.get("impressions", 0), r.get("ctr", 0), r.get("position", 0)])
        notes.append("")

    # 3) commercial fridge CTR
    cfr = query_rows(svc, start, end, ["query"], "commercial fridge repair london")
    notes.append("## 3. commercial fridge repair london CTR")
    if cfr:
        r = cfr[0]
        ctr = r.get("ctr", 0)
        pos = r.get("position", 0)
        notes.append(f"- CTR {ctr:.1%} at pos {pos:.1f} (baseline {BASELINE['commercial_fridge_ctr']:.1%} at pos {BASELINE['commercial_fridge_pos']:.1f})")
        notes.append(f"- delta CTR {(ctr - BASELINE['commercial_fridge_ctr']) * 100:+.1f} pp")
        notes.append("")
        lines.append(["check3", "commercial fridge repair london", r.get("clicks", 0), r.get("impressions", 0), ctr, pos])
    else:
        notes.append("- no query rows")
        notes.append("")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(lines)
    OUT_MD.write_text("\n".join(notes) + "\n", encoding="utf-8")
    print("\n".join(notes))
    print(f"wrote {OUT_CSV} and {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
