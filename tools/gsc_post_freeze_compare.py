#!/usr/bin/env python3
"""Phase 1 (read-only): GSC pre/post ranking comparison around commit c762ad2e.

Pre-Recovery Baseline : 2026-11-08 .. 2026-11-12
Post-Recovery Window  : 2026-11-15 .. latest FINALIZED date available

Reports MOBILE and ALL-device clicks/impressions/CTR/position + primary URL
for the hero money keywords. Writes JSON to logs/ for the report step.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build

SITE = "https://www.colddirect.co.uk/"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
KEY = Path(r"C:\Users\khora\gsc-oauth.json")

PRE = ("2026-11-08", "2026-11-12")
POST_START = "2026-11-15"

KEYWORDS = [
    "cold room repair london",
    "commercial fridge repair london",
    "commercial freezer repair london",
    "fridge repair london",
    "freezer repair london",
    "cellar repair london",
    "cellar cooler repair london",
    "air conditioning repair london",
    "catering repair london",
    "commercial appliances repair london",
    "commercial catering repair london",
]

OUT = Path(__file__).resolve().parents[1] / "logs" / "gsc_post_freeze_compare.json"


def creds():
    return service_account.Credentials.from_service_account_file(str(KEY), scopes=SCOPES)


def q(svc, start, end, dimensions, device=None, data_state="final"):
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": dimensions,
        "rowLimit": 25000,
        "type": "web",
        "dataState": data_state,
    }
    if device:
        body["dimensionFilterGroups"] = [
            {
                "groupType": "and",
                "filters": [
                    {"dimension": "device", "operator": "equals", "expression": device}
                ],
            }
        ]
    res = svc.searchanalytics().query(siteUrl=SITE, body=body).execute()
    return res.get("rows", [])


def latest_final_date(svc):
    rows = q(svc, POST_START, "2026-11-19", ["date"], data_state="final")
    if not rows:
        return None
    return max(r["keys"][0] for r in rows)


def window_stats(svc, start, end, device=None):
    """Return {query: {clicks, impressions, ctr, position, pages: [(page, clicks, impr)]}}"""
    agg = {}
    for r in q(svc, start, end, ["query"], device=device):
        query = r["keys"][0].lower()
        if query in KEYWORDS:
            agg[query] = {
                "clicks": r["clicks"],
                "impressions": r["impressions"],
                "ctr": r["ctr"],
                "position": r["position"],
                "pages": [],
            }
    page_rows = q(svc, start, end, ["query", "page"], device=device)
    for r in page_rows:
        query = r["keys"][0].lower()
        if query in KEYWORDS:
            agg.setdefault(
                query,
                {"clicks": 0, "impressions": 0, "ctr": 0, "position": None, "pages": []},
            )["pages"].append((r["keys"][1], r["clicks"], r["impressions"]))
    for v in agg.values():
        v["pages"].sort(key=lambda p: -p[2])
    return agg


def main():
    svc = build("searchconsole", "v1", credentials=creds(), cache_discovery=False)
    end = latest_final_date(svc)
    print(f"Latest FINALIZED GSC date in post window: {end}")
    post = (POST_START, end or "2026-11-18")

    result = {"pre": PRE, "post": post, "devices": {}}
    for device, label in [("MOBILE", "MOBILE"), (None, "ALL")]:
        pre_s = window_stats(svc, PRE[0], PRE[1], device=device)
        post_s = window_stats(svc, post[0], post[1], device=device)
        result["devices"][label] = {"pre": pre_s, "post": post_s}
        print(f"\n##### device={label} | pre={PRE} | post={post} #####")
        hdr = f"{'keyword':38} | {'pre pos':>7} {'post pos':>8} {'delta':>6} | {'pre cl/impr':>12} {'post cl/impr':>13} | primary URL (post)"
        print(hdr)
        print("-" * len(hdr))
        for kw in KEYWORDS:
            a = pre_s.get(kw, {})
            b = post_s.get(kw, {})
            pa, pb = a.get("position"), b.get("position")
            delta = (pb - pa) if (pa is not None and pb is not None) else None
            url = b["pages"][0][0].replace(SITE, "/") if b.get("pages") else "-"
            pre_url = a["pages"][0][0].replace(SITE, "/") if a.get("pages") else "-"
            print(
                f"{kw:38} | {pa if pa is not None else '-':>7} "
                f"{pb if pb is not None else '-':>8} "
                f"{('%+.2f' % delta) if delta is not None else '-':>6} | "
                f"{str(a.get('clicks','-'))+'/'+str(a.get('impressions','-')):>12} "
                f"{str(b.get('clicks','-'))+'/'+str(b.get('impressions','-')):>13} | "
                f"{url}  (pre: {pre_url})"
            )
            # per-page breakdown for cannibalisation checks
            for page, cl, im in b.get("pages", [])[:3]:
                print(f"{'':38} | {'':>7} {'':>8} {'':>6} | {'':>12} {'cl '+str(cl)+' / im '+str(im):>13} |   -> {page.replace(SITE,'/')}")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2))
    print(f"\nSaved: {OUT}")


if __name__ == "__main__":
    sys.exit(main())
