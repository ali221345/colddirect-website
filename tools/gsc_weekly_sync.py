#!/usr/bin/env python3
"""Cold Direct - weekly Google Search Console sync (run by .github/workflows/gsc-weekly-sync.yml).

What it does
  1. Submits https://www.colddirect.co.uk/sitemap.xml to Search Console and reports its status.
  2. Builds a priority queue: homepage -> 9 core revenue pages -> /commercial-fridge-repair-enfield/
     -> service pages modified in the last N days (git log) -> modified /blog/ pages.
  3. Filters every candidate through tools/deploy_guard.py + tools/html_preflight.py logic
     (blocked paths, noindex, meta-refresh redirect stubs, canonical elsewhere, preflight issues)
     and a live HTTP check (must be 200 with no redirect), so broken/non-indexable URLs are never sent.
  4. Inspects + pings the queue within hard per-run caps that stay far below the daily quotas
     (Indexing API publish: 200/day default; URL Inspection: 2000/day, 600/min per property).
     HTTP 429 / quota errors stop that API cleanly - rate limits never fail the run.
  5. Writes the run summary to $GITHUB_STEP_SUMMARY (nothing is committed back to the repo).

Environment
  GSC_CREDENTIALS_JSON  service-account JSON (repo secret). Required unless DRY_RUN=true.
  DRY_RUN               "true" = build/filter the queue and live-check it, no Google API calls.
  LOOKBACK_DAYS         git look-back window (default 7).
  INDEXING_MAX          max Indexing API calls per run (default 80).
  INSPECT_MAX           max URL Inspection calls per run (default 150).

Exit code is non-zero ONLY for auth failure or a failed sitemap submission.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from deploy_guard import should_skip_upload  # noqa: E402
from html_preflight import is_noindex, is_redirect_stub, validate_html_file  # noqa: E402

SITE = "https://www.colddirect.co.uk/"
SITEMAP = SITE + "sitemap.xml"

# (slug, label) - slug "" is the homepage
PRIORITY = [
    ("", "Homepage"),
    ("commercial-fridge-repair-london", "Core: commercial fridge repair"),
    ("commercial-freezer-repair-london", "Core: commercial freezer repair"),
    ("cold-room-repair-london", "Core: cold room repair"),
    ("fridge-repair-london", "Core: fridge repair"),
    ("freezer-repair-london", "Core: freezer repair"),
    ("catering-repair-london", "Core: catering repair"),
    ("commercial-appliances-repair-london", "Core: commercial appliances / catering"),
    ("air-conditioning-repair-london", "Core: air conditioning repair"),
    ("cellar-cooler-repair-london", "Core: cellar repair"),
    ("commercial-fridge-repair-enfield", "Priority: Enfield"),
]

# top-level folders whose HTML is never a public page
SKIP_DIRS = {
    ".git", ".github", ".cursor", ".vscode", "node_modules", "colddirect-public-html", "docs", "agent",
    "tools", "scripts", "logs", "plesk-hero-upload", "plesk-upload", "_wa_src", "images", "css", "js",
    "includes", "seo-audit", "images-source",
}

CANON_RE = re.compile(r'<link\s+[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', re.I)

LOOKBACK_DAYS = int(os.environ.get("LOOKBACK_DAYS", "7") or "7")
INDEXING_MAX = int(os.environ.get("INDEXING_MAX", "80") or "80")
INSPECT_MAX = int(os.environ.get("INSPECT_MAX", "150") or "150")
DRY_RUN = os.environ.get("DRY_RUN", "false").strip().lower() in ("1", "true", "yes")
TABLE_ROWS = 200

SUMMARY: list[str] = []


def out(line: str = "") -> None:
    SUMMARY.append(line)
    print(line, flush=True)


def esc(s: str) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def norm(u: str) -> str:
    u = u.strip().lower().split("#")[0].split("?")[0].rstrip("/")
    return u[:-5] if u.endswith(".html") else u


def write_step_summary() -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\n".join(SUMMARY) + "\n")


# ------------------------------------------------------------------ queue building
def file_to_url(rel: str) -> str | None:
    if rel == "index.html":
        return SITE
    if rel.endswith("/index.html"):
        return SITE + rel[: -len("index.html")]
    if rel.endswith(".html"):
        return SITE + rel[: -len(".html")] + "/"
    return None


def candidate_files(url: str) -> list[Path]:
    path = url[len(SITE):].strip("/")
    if not path:
        cands = [ROOT / "index.html"]
    else:
        cands = [ROOT / f"{path}.html", ROOT / path / "index.html"]
    return [p for p in cands if p.is_file()]


def git_changed_files(days: int) -> tuple[list[str], bool]:
    shallow = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=ROOT, capture_output=True, text=True).stdout.strip() == "true"
    cmd = ["git", "-c", "core.quotepath=off", "log", f"--since={days} days ago", "--name-only", "--diff-filter=AMR", "--pretty=format:"]
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    seen: dict[str, None] = {}
    for line in res.stdout.splitlines():
        line = line.strip()
        if line and line not in seen:
            seen[line] = None
    return list(seen), shallow


def build_queue() -> tuple[list[dict], dict]:
    queue: list[dict] = []
    seen: set[str] = set()
    for slug, label in PRIORITY:
        url = SITE + (slug + "/" if slug else "")
        queue.append({"url": url, "group": 0, "label": label})
        seen.add(url)
    changed, shallow = git_changed_files(LOOKBACK_DAYS)
    stats = {"changed_files": len(changed), "shallow": shallow, "ignored_paths": 0}
    service, blog = [], []
    for rel in changed:
        if not rel.endswith(".html") or not (ROOT / rel).is_file():
            continue
        top = rel.split("/")[0]
        name = rel.rsplit("/", 1)[-1].lower()
        if top in SKIP_DIRS or re.match(r"google[0-9a-f]+\.html$", name) or "404" in name or name.startswith("error"):
            stats["ignored_paths"] += 1
            continue
        url = file_to_url(rel)
        if not url or url in seen:
            continue
        seen.add(url)
        (blog if rel.startswith("blog/") else service).append({"url": url, "group": 2 if rel.startswith("blog/") else 1,
                                                                "label": "Modified blog page" if rel.startswith("blog/") else "Modified service page"})
    return queue + service + blog, stats


# ------------------------------------------------------------------ filters
def evaluate_local(url: str) -> str:
    """Return '' if the page may be submitted, else the reason it is skipped."""
    files = candidate_files(url)
    if not files:
        return "no local source file"
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        if should_skip_upload(rel):
            return f"blocked path ({rel})"
        text = p.read_text(encoding="utf-8-sig", errors="replace")
        if is_redirect_stub(text):
            return f"redirect stub / meta refresh ({rel})"
        if is_noindex(text):
            return f"noindex ({rel})"
        m = CANON_RE.search(text)
        if m and norm(m.group(1)) != norm(url):
            return f"canonical points elsewhere: {m.group(1)}"
        issues = validate_html_file(str(p))
        if issues:
            return "preflight: " + issues[0].rsplit(": ", 1)[-1] + f" ({rel})"
    return ""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):  # noqa: D401
        return None


_opener = urllib.request.build_opener(_NoRedirect)


def live_check(url: str) -> str:
    """Return '' if the live URL answers 200 directly, else the reason."""
    try:
        r = _opener.open(urllib.request.Request(url, headers={"User-Agent": "ColdDirect-GSC-Sync/1.0"}), timeout=30)
        return "" if r.status == 200 else f"live returns HTTP {r.status}"
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location")
        return f"live returns HTTP {e.code}" + (f" -> {loc}" if loc else "")
    except Exception as e:  # noqa: BLE001
        return f"live check failed: {e}"


# ------------------------------------------------------------------ Google APIs
class Quota:
    def __init__(self, name: str, cap: int):
        self.name, self.cap, self.used, self.stopped = name, cap, 0, ""

    def can(self) -> bool:
        return not self.stopped and self.used < self.cap

    def left(self) -> int:
        return 0 if self.stopped else max(self.cap - self.used, 0)


def call(session, method: str, url: str, quota: Quota, **kw):
    """One API call with a single retry on 5xx. Quota/permission errors stop that API, never raise."""
    for attempt in (1, 2):
        r = session.request(method, url, timeout=30, **kw)
        quota.used += 1
        low = r.text.lower() if r.text else ""
        if r.status_code == 429 or (r.status_code == 403 and any(k in low for k in ("quota", "ratelimit", "resource_exhausted"))):
            quota.stopped = f"quota/rate limit reached (HTTP {r.status_code})"
        elif r.status_code in (401, 403):
            quota.stopped = f"permission denied (HTTP {r.status_code})"
        elif r.status_code >= 500 and attempt == 1:
            time.sleep(3)
            continue
        return r
    return r


def sitemap_section(session) -> bool:
    out("## Sitemap submission")
    feed = urllib.parse.quote(SITEMAP, safe="")
    site = urllib.parse.quote(SITE, safe="")
    url = f"https://www.googleapis.com/webmasters/v3/sites/{site}/sitemaps/{feed}"
    q = Quota("sitemap", 10)
    ok = True
    if DRY_RUN:
        out("- DRY RUN: sitemap not submitted")
    else:
        r = session.put(url, timeout=30)
        if r.status_code in (200, 204):
            out(f"- Submitted `{SITEMAP}` - HTTP {r.status_code} OK")
        else:
            ok = False
            hint = ""
            if r.status_code in (401, 403):
                hint = " - the service account needs **Owner / Full** access to the `https://www.colddirect.co.uk/` property in Search Console"
            out(f"- **FAILED** to submit sitemap: HTTP {r.status_code} {esc(r.text[:200])}{hint}")
    if not DRY_RUN:
        g = call(session, "GET", url, q)
        if g.status_code == 200:
            d = g.json()
            out(f"- Last submitted: `{d.get('lastSubmitted', '?')}` | last downloaded: `{d.get('lastDownloaded', '?')}` | pending: `{d.get('isPending')}`")
            out(f"- Errors: **{d.get('errors', 0)}** | warnings: **{d.get('warnings', 0)}**")
            for c in d.get("contents", []):
                out(f"- Type `{c.get('type')}`: submitted {c.get('submitted')} / indexed {c.get('indexed', 'n/a')}")
    # sanity-check the live sitemap itself
    try:
        xml = urllib.request.urlopen(urllib.request.Request(SITEMAP, headers={"User-Agent": "ColdDirect-GSC-Sync/1.0"}), timeout=30).read().decode("utf-8", "replace")
        locs = re.findall(r"<loc>(.*?)</loc>", xml)
        miss = [SITE + s + "/" for s, _ in PRIORITY[1:10] if SITE + s + "/" not in locs]
        out(f"- Live sitemap: {len(locs)} URLs, duplicates: {len(locs) - len(set(locs))}, core pages missing: {miss or 'none'}")
        bad = [u for u in locs if u.rstrip("/").endswith(("/about", "/news"))]
        if bad:
            out(f"- **WARNING** redirect stubs present in sitemap: {bad}")
    except Exception as e:  # noqa: BLE001
        out(f"- Could not read live sitemap: {e}")
    out()
    return ok


def inspect(session, url: str, quota: Quota) -> tuple[str, str]:
    r = call(session, "POST", "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect", quota,
             json={"inspectionUrl": url, "siteUrl": SITE})
    if r.status_code == 200:
        idx = r.json().get("inspectionResult", {}).get("indexStatusResult", {})
        return idx.get("verdict", "UNKNOWN"), idx.get("coverageState", "UNKNOWN")
    return f"HTTP {r.status_code}", ""


def publish(session, url: str, quota: Quota) -> str:
    r = call(session, "POST", "https://indexing.googleapis.com/v3/urlNotifications:publish", quota,
             json={"url": url, "type": "URL_UPDATED"})
    return "OK" if r.status_code == 200 else f"HTTP {r.status_code}"


# ------------------------------------------------------------------ main
def main() -> int:
    started = datetime.now(timezone.utc)
    out("# GSC weekly sync")
    out(f"- Run: `{started:%Y-%m-%d %H:%M} UTC` | look-back: **{LOOKBACK_DAYS} days** | mode: **{'DRY RUN' if DRY_RUN else 'LIVE'}**")
    out(f"- Caps this run: Indexing API **{INDEXING_MAX}** (daily quota 200) | URL Inspection **{INSPECT_MAX}** (daily quota 2000)")
    out()

    session = None
    failed = False
    if not DRY_RUN:
        raw = os.environ.get("GSC_CREDENTIALS_JSON", "").strip()
        if not raw:
            out("## ERROR\n- Repo secret **`GSC_CREDENTIALS_JSON`** is missing/empty. Add it under Settings > Secrets and variables > Actions.")
            write_step_summary()
            return 1
        try:
            from google.auth.transport.requests import AuthorizedSession  # noqa: WPS433
            from request_indexing import get_credentials  # noqa: WPS433
            session = AuthorizedSession(get_credentials())
        except Exception as e:  # noqa: BLE001
            out(f"## ERROR\n- Could not load Google credentials from `GSC_CREDENTIALS_JSON`: `{esc(type(e).__name__)}: {esc(str(e)[:200])}`")
            write_step_summary()
            return 1
        try:
            if not sitemap_section(session):
                failed = True
        except Exception as e:  # noqa: BLE001
            out(f"- **FAILED** sitemap step: `{esc(type(e).__name__)}: {esc(str(e)[:300])}`")
            out()
            failed = True
    else:
        sitemap_section(None)

    # ---- queue
    queue, stats = build_queue()
    out("## Delta detection")
    out(f"- `git log --since=\"{LOOKBACK_DAYS} days ago\"` found **{stats['changed_files']}** added/modified/renamed paths "
        f"({stats['ignored_paths']} ignored: non-page folders, verification/404 files)")
    if stats["shallow"]:
        out("- **WARNING**: shallow clone - the look-back window is truncated. Use `fetch-depth: 0`.")
    out(f"- Candidate queue: **{len(queue)}** URLs ({sum(1 for q in queue if q['group'] == 0)} priority, "
        f"{sum(1 for q in queue if q['group'] == 1)} service, {sum(1 for q in queue if q['group'] == 2)} blog)")
    out()

    skipped: list[tuple[str, str]] = []
    valid: list[dict] = []
    for item in queue:
        reason = evaluate_local(item["url"])
        if reason:
            skipped.append((item["url"], reason))
        else:
            valid.append(item)

    accepted: list[dict] = []
    deferred: list[dict] = []
    for item in valid:
        if len(accepted) >= INDEXING_MAX:
            deferred.append(item)
            continue
        reason = live_check(item["url"])
        if reason:
            skipped.append((item["url"], reason))
        else:
            accepted.append(item)

    # ---- Google calls
    results: list[dict] = []
    insp_q, idx_q = Quota("inspect", INSPECT_MAX), Quota("indexing", INDEXING_MAX)
    for item in accepted:
        row = dict(item, verdict="-", coverage="-", indexing="-")
        if session is not None:
            if insp_q.can():
                row["verdict"], row["coverage"] = inspect(session, item["url"], insp_q)
                time.sleep(0.3)
            else:
                row["verdict"] = "not inspected (" + (insp_q.stopped or "cap reached") + ")"
            if idx_q.can():
                row["indexing"] = publish(session, item["url"], idx_q)
                time.sleep(0.5)
            else:
                row["indexing"] = "not sent (" + (idx_q.stopped or "cap reached") + ")"
        else:
            row["verdict"] = row["indexing"] = "dry run"
        results.append(row)

    out("## Submitted / checked URLs")
    out(f"- Indexing API calls: **{idx_q.used}/{INDEXING_MAX}**{' - STOPPED: ' + idx_q.stopped if idx_q.stopped else ''}")
    out(f"- URL Inspection calls: **{insp_q.used}/{INSPECT_MAX}**{' - STOPPED: ' + insp_q.stopped if insp_q.stopped else ''}")
    out()
    out("| # | URL | Group | Index status (GSC) | Indexing API |")
    out("|---|-----|-------|--------------------|--------------|")
    for i, r in enumerate(results[:TABLE_ROWS], 1):
        status = f"{r['verdict']} / {r['coverage']}" if r["coverage"] not in ("", "-") else r["verdict"]
        out(f"| {i} | {r['url']} | {esc(r['label'])} | {esc(status)} | {esc(r['indexing'])} |")
    if len(results) > TABLE_ROWS:
        out(f"| ... | {len(results) - TABLE_ROWS} more rows omitted | | | |")
    out()

    out(f"## Skipped ({len(skipped)})")
    if skipped:
        out("| URL | Reason |")
        out("|-----|--------|")
        for u, why in skipped[:TABLE_ROWS]:
            out(f"| {u} | {esc(why)} |")
        if len(skipped) > TABLE_ROWS:
            out(f"| ... | {len(skipped) - TABLE_ROWS} more omitted |")
    else:
        out("- none")
    out()
    out(f"## Deferred by the per-run cap ({len(deferred)})")
    out("- These valid URLs were not sent this week to stay inside the daily quota; they are picked up again only if modified again, "
        "and Google still discovers them through the submitted sitemap." if deferred else "- none")
    out()
    out("> Note: Google officially supports the Indexing API only for job-posting and livestream pages. For regular pages "
        "the sitemap submission and URL Inspection results above are the reliable signals; Indexing API pings are best-effort.")
    if any("noindex" in r or "stub" in r for _, r in skipped):
        out("> Redirect stubs and noindex pages were filtered out as designed.")
    out()
    out(f"_Finished in {(datetime.now(timezone.utc) - started).seconds}s - failed={failed}_")
    write_step_summary()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
