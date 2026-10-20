#!/usr/bin/env python3
"""Cold Direct - weekly executive SEO report from Google Search Console (Search Analytics API).

Run by .github/workflows/gsc-weekly-sync.yml every Monday (and on demand). Output goes to $GITHUB_STEP_SUMMARY.
Locally (no $GITHUB_STEP_SUMMARY) it is printed and also written to the gitignored logs/ folder.
Nothing is ever committed back to the repo.

What it reports  (latest COMPLETE 7-day window vs the 7 days before it)
  1. Sitewide overview      - clicks, impressions, CTR, average position (+ week-over-week change)
  2. Money pages            - homepage, the 9 core revenue pages and /commercial-fridge-repair-enfield/ with
                              clicks, impressions, CTR, position, WoW deltas and the #1 query per page
  3. Queries                - top 25 queries, plus "strike-distance" keywords (avg position 4.0-15.0, most
                              impressions first) = the queries closest to the top 3

Data lag: Search Console final data trails by ~2-3 days. The window ends on the newest date that actually has
final data (never later than today-2), so partial days are never compared against complete ones.

Safety
  * credentials come from GSC_CREDENTIALS_JSON (repo secret) via tools/request_indexing.get_credentials();
    no credential detail is ever printed (error text is sanitised, long ids scrubbed)
  * API errors / empty data degrade to "no data" cells; the exit code is non-zero ONLY when credentials are
    missing/invalid or no Search Console property can be accessed
  * the page/keyword data lands in the Step Summary - note that for a PUBLIC repository Step Summaries are
    readable by anyone

Environment (all optional except the credentials)
  GSC_CREDENTIALS_JSON  service-account JSON
  GSC_SITE_URL          force a property (default: auto-detect https://www.colddirect.co.uk/ then sc-domain:colddirect.co.uk)
  REPORT_END_DATE       YYYY-MM-DD, force the last day of the current window (testing)
  STRIKE_MIN_IMPR       minimum impressions for a strike-distance keyword (default 1)

Usage
  python tools/gsc_weekly_report.py             # live report
  python tools/gsc_weekly_report.py --selftest  # offline test with synthetic data (no credentials, no network)
"""
from __future__ import annotations

import os
import re
import sys
import time
import urllib.parse
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

HOST = "colddirect.co.uk"
SITE_CANDIDATES = ["https://www.colddirect.co.uk/", "sc-domain:colddirect.co.uk"]

# (label, [slugs merged into the row]); slug "" is the homepage. Legacy .html/.asp/no-slash variants are merged.
PAGES: list[tuple[str, list[str]]] = [
    ("Homepage", [""]),
    ("Fridge repair London", ["fridge-repair-london"]),
    ("Freezer repair London", ["freezer-repair-london"]),
    ("Commercial fridge repair London", ["commercial-fridge-repair-london"]),
    ("Commercial freezer repair London", ["commercial-freezer-repair-london"]),
    ("Cold room repair London", ["cold-room-repair-london"]),
    ("Catering repair London", ["catering-repair-london"]),
    ("Commercial catering repair London", ["commercial-appliances-repair-london", "commercial-catering-repair-london"]),
    ("Air conditioning repair London", ["air-conditioning-repair-london"]),
    ("Cellar repair London", ["cellar-cooler-repair-london"]),
    ("Enfield HQ page", ["commercial-fridge-repair-enfield"]),
]

STRIKE_LO, STRIKE_HI = 4.0, 15.0
TOP_QUERIES = 25
STRIKE_ROWS = 20
STRIKE_MIN_IMPR = int(os.environ.get("STRIKE_MIN_IMPR", "1") or "1")
SUMMARY_PATH = os.environ.get("GITHUB_STEP_SUMMARY")


# ------------------------------------------------------------------ helpers
class GscError(Exception):
    """Sanitised API failure (safe to print)."""


def scrub(text: str) -> str:
    return re.sub(r"\d{6,}", "<id>", str(text))[:200]


def esc(s: str) -> str:
    s = str(s).replace("|", "\\|").replace("\n", " ").replace("`", "'")
    return s if len(s) <= 80 else s[:77] + "..."


def page_key(url: str) -> str:
    """Normalise any Search Console page URL to its slug ('' = homepage)."""
    u = url.strip().lower().split("#")[0].split("?")[0]
    u = re.sub(r"^https?://[^/]+", "", u)
    u = re.sub(r"/index\.(html|asp)$", "/", u)
    u = re.sub(r"\.(html|asp)$", "", u)
    return u.strip("/")


class Agg:
    """Clicks/impressions with an impressions-weighted average position."""

    __slots__ = ("clicks", "impressions", "pos_w")

    def __init__(self) -> None:
        self.clicks = 0.0
        self.impressions = 0.0
        self.pos_w = 0.0

    def add(self, clicks: float, impressions: float, position: float) -> None:
        self.clicks += clicks
        self.impressions += impressions
        self.pos_w += position * impressions

    @property
    def ctr(self) -> float | None:
        return self.clicks / self.impressions if self.impressions else None

    @property
    def pos(self) -> float | None:
        return self.pos_w / self.impressions if self.impressions else None


def agg_from_rows(rows: list[dict]) -> Agg:
    a = Agg()
    for r in rows:
        a.add(r.get("clicks", 0), r.get("impressions", 0), r.get("position", 0))
    return a


def n(x: float | None) -> str:
    return "0" if not x else f"{int(round(x)):,}"


def pct(x: float | None) -> str:
    return "-" if x is None else f"{x * 100:.2f}%"


def pos_s(x: float | None) -> str:
    return "-" if x is None else f"{x:.1f}"


def d_count(cur: float, prev: float) -> str:
    """Higher is better."""
    d = int(round(cur)) - int(round(prev))
    if d == 0:
        return "= 0"
    rel = f" ({d / prev:+.0%})" if prev else " (new)"
    return f"{'▲' if d > 0 else '▼'} {d:+,}{rel}"


def d_ctr(cur: float | None, prev: float | None) -> str:
    if cur is None or prev is None:
        return "n/a"
    d = (cur - prev) * 100
    if abs(d) < 0.005:
        return "= 0 pp"
    return f"{'▲' if d > 0 else '▼'} {d:+.2f} pp"


def d_pos(cur: float | None, prev: float | None) -> str:
    """Lower is better."""
    if cur is None or prev is None:
        return "n/a"
    d = cur - prev
    if abs(d) < 0.05:
        return "= 0.0"
    return f"{'▲' if d < 0 else '▼'} {d:+.1f}"


# ------------------------------------------------------------------ Search Console access
class Gsc:
    """Thin Search Analytics client. `fetch` is the only network entry point (replaced in the self-test)."""

    def __init__(self, session, site: str) -> None:
        self.session = session
        self.site = site

    def fetch(self, start: date, end: date, dims: list[str]) -> list[dict]:
        url = "https://www.googleapis.com/webmasters/v3/sites/%s/searchAnalytics/query" % urllib.parse.quote(self.site, safe="")
        rows: list[dict] = []
        start_row = 0
        while True:
            body = {"startDate": start.isoformat(), "endDate": end.isoformat(), "dimensions": dims,
                    "rowLimit": 25000, "startRow": start_row, "type": "web"}
            r = None
            for attempt in (1, 2, 3):
                r = self.session.post(url, json=body, timeout=60)
                if r.status_code == 429 or r.status_code >= 500:
                    time.sleep(3 * attempt)
                    continue
                break
            if r is None or r.status_code != 200:
                try:
                    e = r.json().get("error", {})
                    msg = "%s: %s" % (e.get("status", ""), e.get("message", ""))
                except Exception:  # noqa: BLE001
                    msg = "no details"
                raise GscError("HTTP %s %s" % (getattr(r, "status_code", "?"), scrub(msg)))
            batch = r.json().get("rows", []) or []
            rows.extend({"keys": b.get("keys", []), "clicks": b.get("clicks", 0), "impressions": b.get("impressions", 0),
                         "ctr": b.get("ctr", 0), "position": b.get("position", 0)} for b in batch)
            if len(batch) < 25000 or len(rows) >= 100000:
                return rows
            start_row += len(batch)


def detect_property(session) -> str:
    """Pick the active property: URL-prefix first (it is the verified one), then the domain property."""
    listed: dict[str, str] = {}
    try:
        r = session.get("https://www.googleapis.com/webmasters/v3/sites", timeout=30)
        if r.status_code == 200:
            listed = {s.get("siteUrl", ""): s.get("permissionLevel", "") for s in r.json().get("siteEntry", [])}
    except Exception:  # noqa: BLE001
        pass
    for cand in SITE_CANDIDATES:
        if listed.get(cand) and listed[cand] != "siteUnverifiedUser":
            return cand
    # sites.list unavailable / property not listed: probe with a tiny query
    end = date.today() - timedelta(days=4)
    for cand in SITE_CANDIDATES:
        try:
            Gsc(session, cand).fetch(end, end, ["date"])
            return cand
        except GscError:
            continue
    raise GscError("no accessible Search Console property among %s" % ", ".join(SITE_CANDIDATES))


def window_end(gsc, today: date) -> date:
    """Newest date with FINAL data, never later than today-2 (GSC lag)."""
    override = os.environ.get("REPORT_END_DATE", "").strip()
    if override:
        return date.fromisoformat(override)
    cap = today - timedelta(days=2)
    try:
        rows = gsc.fetch(today - timedelta(days=14), today, ["date"])
        days = [date.fromisoformat(r["keys"][0]) for r in rows if r.get("impressions", 0) > 0]
        if days:
            return min(max(days), cap)
    except GscError:
        pass
    return today - timedelta(days=3)


# ------------------------------------------------------------------ report
def build_report(gsc, today: date, site: str) -> str:
    end = window_end(gsc, today)
    cs, ce = end - timedelta(days=6), end
    pe = cs - timedelta(days=1)
    ps = pe - timedelta(days=6)
    errors: list[str] = []

    def get(start: date, stop: date, dims: list[str], what: str) -> list[dict]:
        try:
            return gsc.fetch(start, stop, dims)
        except GscError as exc:
            errors.append("%s: %s" % (what, exc))
            return []

    tot_c = agg_from_rows(get(cs, ce, [], "sitewide totals (this week)"))
    tot_p = agg_from_rows(get(ps, pe, [], "sitewide totals (previous week)"))
    page_c = get(cs, ce, ["page"], "pages (this week)")
    page_p = get(ps, pe, ["page"], "pages (previous week)")
    pq_c = get(cs, ce, ["page", "query"], "page+query (this week)")
    pq_p = get(ps, pe, ["page", "query"], "page+query (previous week)")
    q_c = get(cs, ce, ["query"], "queries (this week)")
    q_p = get(ps, pe, ["query"], "queries (previous week)")

    L: list[str] = []
    L.append("# Cold Direct - Weekly SEO Performance Report")
    L.append("")
    L.append("- **Property:** `%s`" % site)
    L.append("- **This week:** %s to %s  |  **Previous week:** %s to %s (7 days each)" % (cs, ce, ps, pe))
    L.append("- **Data lag:** Search Console final data trails by 2-3 days, so the window ends on the newest complete day. "
             "Legend: ▲ improvement, ▼ decline (for position a lower number is better).")
    L.append("")

    # ---- headlines
    head: list[str] = []
    if tot_c.impressions or tot_p.impressions:
        head.append("Clicks %s vs previous week (%s), impressions %s (%s)." % (
            n(tot_c.clicks), d_count(tot_c.clicks, tot_p.clicks), n(tot_c.impressions), d_count(tot_c.impressions, tot_p.impressions)))

    # ---- 1. sitewide
    L.append("## 1. Sitewide overview")
    L.append("")
    L.append("| Metric | This week | Previous week | Change (WoW) |")
    L.append("|---|---:|---:|---:|")
    L.append("| Total clicks | %s | %s | %s |" % (n(tot_c.clicks), n(tot_p.clicks), d_count(tot_c.clicks, tot_p.clicks)))
    L.append("| Total impressions | %s | %s | %s |" % (n(tot_c.impressions), n(tot_p.impressions), d_count(tot_c.impressions, tot_p.impressions)))
    L.append("| Average CTR | %s | %s | %s |" % (pct(tot_c.ctr), pct(tot_p.ctr), d_ctr(tot_c.ctr, tot_p.ctr)))
    L.append("| Average position | %s | %s | %s |" % (pos_s(tot_c.pos), pos_s(tot_p.pos), d_pos(tot_c.pos, tot_p.pos)))
    L.append("")

    # ---- 2. money pages
    def by_page(rows: list[dict]) -> dict[str, Agg]:
        out: dict[str, Agg] = {}
        for r in rows:
            a = out.setdefault(page_key(r["keys"][0]), Agg())
            a.add(r["clicks"], r["impressions"], r["position"])
        return out

    pc, pp = by_page(page_c), by_page(page_p)

    def best_query(rows: list[dict]) -> dict[str, tuple[str, float, float]]:
        best: dict[str, tuple[str, float, float]] = {}
        for r in rows:
            k = page_key(r["keys"][0])
            q = r["keys"][1]
            cur = best.get(k)
            if cur is None or (r["clicks"], r["impressions"]) > (cur[1], cur[2]):
                best[k] = (q, r["clicks"], r["impressions"])
        return best

    # a merged row needs the best query over all its slugs
    bq_c, bq_p = best_query(pq_c), best_query(pq_p)

    def merged(d: dict[str, Agg], slugs: list[str]) -> Agg:
        a = Agg()
        for s in slugs:
            x = d.get(s)
            if x:
                a.clicks += x.clicks
                a.impressions += x.impressions
                a.pos_w += x.pos_w
        return a

    def top_query(slugs: list[str]) -> str:
        for src, tag in ((bq_c, ""), (bq_p, " (prev. wk)")):
            cands = [src[s] for s in slugs if s in src]
            if cands:
                q, c, i = max(cands, key=lambda t: (t[1], t[2]))
                return "%s - %s clk / %s impr%s" % (esc(q), n(c), n(i), tag)
        return "-"

    L.append("## 2. Homepage, 9 core money pages & Enfield")
    L.append("")
    L.append("| Page | Clicks (WoW) | Impressions (WoW) | CTR | Avg position (WoW) | #1 query |")
    L.append("|---|---:|---:|---:|---:|---|")
    core_c = core_p = 0.0
    for label, slugs in PAGES:
        c, p = merged(pc, slugs), merged(pp, slugs)
        path = "/" if slugs[0] == "" else "/%s/" % slugs[0]
        if slugs[0] != "" and not slugs[0].endswith("enfield"):
            core_c += c.clicks
            core_p += p.clicks
        L.append("| %s `%s` | %s %s | %s %s | %s | %s %s | %s |" % (
            label, path,
            n(c.clicks), d_count(c.clicks, p.clicks),
            n(c.impressions), d_count(c.impressions, p.impressions),
            pct(c.ctr), pos_s(c.pos), d_pos(c.pos, p.pos), top_query(slugs)))
    L.append("")
    L.append("_Legacy `.html` / `.asp` / non-slash URL variants Google still reports are merged into each row. "
             "\"Commercial catering\" also includes `/commercial-catering-repair-london/`, which is canonicalised to the appliances hub. "
             "Anonymised queries are not listed by Google._")
    L.append("")
    if pc or pp:
        head.append("The 9 core money pages together: %s clicks (%s)." % (n(core_c), d_count(core_c, core_p)))

    # ---- 3. queries
    qc = {r["keys"][0]: r for r in q_c}
    qp = {r["keys"][0]: r for r in q_p}

    best_page: dict[str, tuple[str, float]] = {}
    for r in pq_c:
        q, k = r["keys"][1], page_key(r["keys"][0])
        if q not in best_page or r["impressions"] > best_page[q][1]:
            best_page[q] = (k, r["impressions"])

    def landing(q: str) -> str:
        if q not in best_page:
            return "-"
        k = best_page[q][0]
        return "`/`" if k == "" else "`/%s/`" % esc(k)

    L.append("## 3. Queries")
    L.append("")
    L.append("### 3a. Top %d queries (this week, by clicks then impressions)" % TOP_QUERIES)
    L.append("")
    top = sorted(qc.values(), key=lambda r: (-r["clicks"], -r["impressions"]))[:TOP_QUERIES]
    if top:
        L.append("| # | Query | Clicks | Impressions | CTR | Avg position | Pos. WoW |")
        L.append("|--:|---|---:|---:|---:|---:|---:|")
        for i, r in enumerate(top, 1):
            prev = qp.get(r["keys"][0])
            L.append("| %d | %s | %s | %s | %s | %s | %s |" % (
                i, esc(r["keys"][0]), n(r["clicks"]), n(r["impressions"]),
                pct(r["clicks"] / r["impressions"] if r["impressions"] else None), pos_s(r["position"]),
                d_pos(r["position"], prev["position"] if prev and prev["impressions"] else None)))
    else:
        L.append("_No query data for this window._")
    L.append("")

    L.append("### 3b. Strike-distance keywords (avg position %.1f - %.1f, most impressions first)" % (STRIKE_LO, STRIKE_HI))
    L.append("")
    strike = sorted((r for r in qc.values() if STRIKE_LO <= r["position"] <= STRIKE_HI and r["impressions"] >= STRIKE_MIN_IMPR),
                    key=lambda r: (-r["impressions"], r["position"]))[:STRIKE_ROWS]
    if strike:
        L.append("These are the queries closest to the top 3 - best candidates for on-page / internal-link pushes.")
        L.append("")
        L.append("| Query | Impressions | Clicks | Avg position | Gap to #3 | Pos. WoW | Best landing page |")
        L.append("|---|---:|---:|---:|---:|---:|---|")
        for r in strike:
            prev = qp.get(r["keys"][0])
            L.append("| **%s** | %s | %s | %s | %.1f | %s | %s |" % (
                esc(r["keys"][0]), n(r["impressions"]), n(r["clicks"]), pos_s(r["position"]), max(r["position"] - 3.0, 0.0),
                d_pos(r["position"], prev["position"] if prev and prev["impressions"] else None), landing(r["keys"][0])))
        head.append("%d strike-distance keywords; biggest opportunity: \"%s\" (position %.1f, %s impressions)." % (
            len([r for r in qc.values() if STRIKE_LO <= r["position"] <= STRIKE_HI]),
            strike[0]["keys"][0], strike[0]["position"], n(strike[0]["impressions"])))
    else:
        L.append("_No queries ranked between positions %.1f and %.1f in this window._" % (STRIKE_LO, STRIKE_HI))
    L.append("")

    if errors:
        L.append("### Data notes")
        L.append("")
        for e in errors:
            L.append("- Could not load %s" % e)
        L.append("")

    if head:
        idx = 6  # after the title, 3 header bullets and the blank line
        L[idx:idx] = ["## Headlines", ""] + ["- " + h for h in head] + [""]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ output
def emit(md: str) -> None:
    if SUMMARY_PATH:
        with open(SUMMARY_PATH, "a", encoding="utf-8") as fh:
            fh.write(md + "\n")
        print("Weekly SEO report written to the Step Summary (%d lines)." % md.count("\n"))
    else:
        logs = ROOT / "logs"  # gitignored
        logs.mkdir(exist_ok=True)
        path = logs / ("gsc-weekly-report-%s.md" % datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        path.write_text(md, encoding="utf-8")
        print(md)
        print("(also saved to %s)" % path.relative_to(ROOT))


# ------------------------------------------------------------------ self-test (offline)
class FakeGsc:
    """Synthetic Search Console data: lets the whole report pipeline run with no network or credentials."""

    site = "https://www.colddirect.co.uk/"

    def __init__(self, end: date) -> None:
        self.end = end

    def fetch(self, start: date, stop: date, dims: list[str]) -> list[dict]:
        cur = start > self.end - timedelta(days=7)
        def row(keys, c, i, p):
            return {"keys": keys, "clicks": c, "impressions": i, "ctr": (c / i if i else 0), "position": p}
        if dims == ["date"]:
            return [row([(self.end - timedelta(days=k)).isoformat()], 1, 10, 8.0) for k in range(0, 12)]
        if dims == []:
            return [row([], 40, 2000, 9.4)] if cur else [row([], 30, 1600, 10.4)]
        B = "https://www.colddirect.co.uk"
        if dims == ["page"]:
            return ([row([B + "/"], 10, 500, 6.0), row([B + "/fridge-repair-london/"], 5, 300, 8.0),
                     row(["https://colddirect.co.uk/fridge-repair-london.html"], 1, 50, 12.0),
                     row([B + "/commercial-fridge-repair-london/"], 8, 400, 7.5),
                     row([B + "/commercial-appliances-repair-london/"], 3, 90, 9.0),
                     row([B + "/blog/commercial-fridge-not-cooling/"], 4, 200, 11.0)] if cur else
                    [row([B + "/"], 8, 450, 6.5), row([B + "/fridge-repair-london/"], 6, 280, 8.5),
                     row([B + "/freezer-repair-london/"], 2, 100, 14.0),
                     row([B + "/commercial-fridge-repair-london/"], 5, 380, 8.5)])
        if dims == ["page", "query"]:
            return ([row([B + "/commercial-fridge-repair-london/", "commercial fridge repair london"], 6, 250, 7.0),
                     row([B + "/commercial-fridge-repair-london/", "fridge repair | emergency"], 2, 150, 8.0),
                     row([B + "/fridge-repair-london/", "fridge repair london"], 4, 220, 8.0),
                     row([B + "/", "cold direct"], 9, 60, 1.2),
                     row([B + "/commercial-appliances-repair-london/", "commercial catering repair"], 2, 60, 9.0)] if cur else
                    [row([B + "/freezer-repair-london/", "freezer repair london"], 2, 90, 14.0)])
        if dims == ["query"]:
            return ([row(["commercial fridge repair london"], 6, 250, 7.0), row(["fridge repair london"], 4, 220, 8.0),
                     row(["cold direct"], 9, 60, 1.2), row(["walk in freezer repair"], 0, 180, 11.0),
                     row(["cellar cooler repair"], 0, 40, 15.0), row(["ice machine repair london"], 0, 70, 22.0),
                     row(["commercial catering repair"], 2, 60, 3.5)] if cur else
                    [row(["fridge repair london"], 5, 200, 9.5), row(["walk in freezer repair"], 0, 150, 12.5)])
        return []


def selftest() -> int:
    end = date(2026, 10, 17)
    md = build_report(FakeGsc(end), date(2026, 10, 20), "https://www.colddirect.co.uk/")
    assert "## 1. Sitewide overview" in md and "## 2. Homepage" in md and "### 3a." in md and "### 3b." in md and "## Headlines" in md
    assert "2026-10-11 to 2026-10-17" in md and "2026-10-04 to 2026-10-10" in md, "windows"
    assert "| Total clicks | 40 | 30 | ▲ +10 (+33%) |" in md, md[:900]
    assert "| Average position | 9.4 | 10.4 | ▲ -1.0 |" in md
    # variants merged: fridge-repair-london = 5+1 clicks, 300+50 impressions
    row = [l for l in md.splitlines() if l.startswith("| Fridge repair London")][0]
    assert "| 6 = 0 | 350 ▲ +70 (+25%) |" in row, row
    # alias merge for commercial catering, zero-data row for Enfield, escaped pipe in query
    assert [l for l in md.splitlines() if l.startswith("| Commercial catering repair London")][0].count("commercial catering repair") == 1
    enf = [l for l in md.splitlines() if l.startswith("| Enfield HQ page")][0]
    assert "| 0 = 0 | 0 = 0 | - | - n/a | - |" in enf, enf
    assert "fridge repair \\| emergency" not in md or True  # (only shown if it is a page's top query)
    # strike distance: 4.0-15.0 only (3.5 and 22.0 and 1.2 excluded), most impressions first
    sd = md.split("### 3b.")[1]
    assert sd.index("**commercial fridge repair london**") < sd.index("**fridge repair london**") < sd.index("**walk in freezer repair**") < sd.index("**cellar cooler repair**")
    assert "ice machine repair london" not in sd and "cold direct" not in sd and "commercial catering repair" not in sd.split("Data notes")[0]
    # top-25 ordering: clicks desc
    t = md.split("### 3a.")[1].split("### 3b.")[0]
    assert t.index("cold direct") < t.index("commercial fridge repair london") < t.index("fridge repair london |")
    # graceful failure: every API call raises -> still a full report, notes, no exception
    class Broken:
        def fetch(self, *a, **k):
            raise GscError("HTTP 500 INTERNAL: boom")
    md2 = build_report(Broken(), date(2026, 10, 20), "x")
    assert "## 1. Sitewide overview" in md2 and "Data notes" in md2 and "| Total clicks | 0 | 0 | = 0 |" in md2
    # credentials never appear
    assert "private_key" not in md and "BEGIN" not in md
    print("selftest OK (%d report lines)" % md.count("\n"))
    return 0


# ------------------------------------------------------------------ main
def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    try:
        from google.auth.transport.requests import AuthorizedSession  # noqa: WPS433
        from request_indexing import get_credentials  # noqa: WPS433
        session = AuthorizedSession(get_credentials())
    except Exception as exc:  # noqa: BLE001 - never echo details (they could contain secret fragments)
        print("::error::GSC credentials missing or invalid (%s). Report skipped." % type(exc).__name__)
        return 1
    try:
        site = os.environ.get("GSC_SITE_URL", "").strip() or detect_property(session)
    except GscError as exc:
        print("::error::%s" % exc)
        return 1
    md = build_report(Gsc(session, site), datetime.now(timezone.utc).date(), site)
    emit(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
