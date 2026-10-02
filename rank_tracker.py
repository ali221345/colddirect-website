#!/usr/bin/env python3
"""
Cold Direct keyword rank tracker — persists a daily position snapshot for every target
keyword and reports progress toward page 1 (Google positions 1-10).

Reuses the GSC credentials/API pattern from gsc_report.py but writes its own durable
history file (rank_history.jsonl, append-only, one line per day) so progress toward
the "first page for all target keywords" goal is visible over time, not just today's
snapshot.

Usage:
  python rank_tracker.py                 # append today's snapshot, print progress report
  python rank_tracker.py --report-only   # print the trend report without fetching new data
"""
from __future__ import annotations

import argparse
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
HISTORY_FILE = Path(__file__).resolve().parent / "rank_history.jsonl"

# Target keywords for the "first page for all target keywords" goal. Keep in sync with
# gsc_report.py's QUERIES list — these are the keywords that matter for this goal.
TARGET_KEYWORDS = [
    "cold room repair london",
    "commercial fridge repair london",
    "fridge repair london",
    "freezer repair london",
    "commercial freezer repair london",
]
PAGE_1_THRESHOLD = 10.0  # Google position <= 10 is page 1


def credentials():
    import os

    env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    paths = [Path(env)] if env else []
    paths.extend(KEY_CANDIDATES)
    for p in paths:
        if p and p.is_file():
            return service_account.Credentials.from_service_account_file(str(p), scopes=SCOPES)
    raise SystemExit("No GSC key. Set GOOGLE_APPLICATION_CREDENTIALS or place gsc-oauth.json")


def fetch_snapshot(svc, start: str, end: str, min_impressions: int = 10) -> dict:
    """One row per target keyword: best (lowest) position among rows with a statistically
    meaningful sample (>= min_impressions), not just whichever row happens to have the
    single best position — a page with 1 impression can show position 3 by pure chance
    while the page genuinely driving traffic sits at position 7 across 150+ impressions.
    Falls back to the highest-impression row if nothing clears the threshold."""
    snapshot = {}
    for kw in TARGET_KEYWORDS:
        body = {
            "startDate": start,
            "endDate": end,
            "dimensions": ["page"],
            "dimensionFilterGroups": [
                {"groupType": "and", "filters": [{"dimension": "query", "operator": "equals", "expression": kw}]}
            ],
            "rowLimit": 50,
            "type": "web",
            "dataState": "all",
        }
        res = svc.searchanalytics().query(siteUrl=SITE, body=body).execute()
        rows = res.get("rows", [])
        if not rows:
            snapshot[kw] = {"position": None, "url": None, "clicks": 0, "impressions": 0}
            continue
        reliable = [r for r in rows if r.get("impressions", 0) >= min_impressions]
        pool = reliable if reliable else rows
        best = min(pool, key=lambda r: r.get("position", 999)) if reliable else max(pool, key=lambda r: r.get("impressions", 0))
        snapshot[kw] = {
            "position": round(best.get("position", 0), 2),
            "url": best["keys"][0],
            "clicks": best.get("clicks", 0),
            "impressions": best.get("impressions", 0),
            "low_confidence": not reliable,
        }
    return snapshot


def append_history(day: str, snapshot: dict) -> None:
    entry = {"date": day, "keywords": snapshot}
    with HISTORY_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    entries = []
    with HISTORY_FILE.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def print_report(history: list[dict]) -> None:
    if not history:
        print("No rank history yet.")
        return

    latest = history[-1]
    first = history[0]
    print(f"# Cold Direct Rank Tracker — {latest['date']} (tracking since {first['date']}, {len(history)} snapshots)")
    print()
    print(f"Goal: all {len(TARGET_KEYWORDS)} target keywords on page 1 (position <= {PAGE_1_THRESHOLD:.0f})")
    print()

    on_page_1 = 0
    print(f"{'Keyword':<38} {'Position':>9} {'Page 1?':>8} {'Trend (vs first)':>18} {'Best URL'}")
    print("-" * 110)
    for kw in TARGET_KEYWORDS:
        latest_kw = latest["keywords"].get(kw, {})
        first_kw = first["keywords"].get(kw, {})
        pos = latest_kw.get("position")
        first_pos = first_kw.get("position")
        url = (latest_kw.get("url") or "—").replace(SITE.rstrip("/"), "")

        if pos is None:
            pos_str, page1_str, trend_str = "no data", "—", "—"
        else:
            page1 = pos <= PAGE_1_THRESHOLD
            if page1:
                on_page_1 += 1
            conf_flag = " (low-conf)" if latest_kw.get("low_confidence") else ""
            pos_str = f"{pos:.2f}{conf_flag}"
            page1_str = "✅ YES" if page1 else "no"
            if first_pos is not None and pos is not None:
                delta = first_pos - pos  # positive = improved (moved up, lower number)
                arrow = "↑" if delta > 0.1 else ("↓" if delta < -0.1 else "→")
                trend_str = f"{arrow} {delta:+.1f}"
            else:
                trend_str = "—"

        print(f"{kw:<38} {pos_str:>9} {page1_str:>8} {trend_str:>18} {url}")

    print()
    print(f"**{on_page_1}/{len(TARGET_KEYWORDS)} target keywords on page 1.**")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report-only", action="store_true", help="Print trend report without fetching new data")
    args = parser.parse_args()

    if not args.report_only:
        end = (date.today() - timedelta(days=1)).isoformat()
        start = (date.fromisoformat(end) - timedelta(days=27)).isoformat()
        svc = build("searchconsole", "v1", credentials=credentials(), cache_discovery=False)
        snapshot = fetch_snapshot(svc, start, end)
        today = date.today().isoformat()

        existing = load_history()
        if existing and existing[-1]["date"] == today:
            print(f"Already have a snapshot for {today}, skipping fetch (use --report-only to just view).")
        else:
            append_history(today, snapshot)
            print(f"Appended snapshot for {today} to {HISTORY_FILE}")

    history = load_history()
    print()
    print_report(history)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
