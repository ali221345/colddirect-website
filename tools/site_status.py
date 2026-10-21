#!/usr/bin/env python3
"""Read-only CLI health & SEO dashboard for https://www.colddirect.co.uk - the whole live state in one terminal view.

    python tools/site_status.py              # everything
    python tools/site_status.py --skip-gsc   # no Search Console section (also automatic without local credentials)
    python tools/site_status.py --skip-gh    # no GitHub section
    python tools/site_status.py --selftest   # offline unit tests (no network, no gh, no GSC)

Sections
  1. Live smoke & speed   - the checks of tools/live_smoke_test.py (11 core pages HTTP 200 + schema/canonical/phone,
                            latency average/max, homepage static assets, sitemap, robots.txt, 301 / canonical redirects)
  2. SSL certificates     - exact expiry date, issuer and days_remaining for www.colddirect.co.uk and colddirect.co.uk
  3. GitHub Actions       - latest Deploy / Nightly auto-seo / GSC Weekly Sync runs (gh CLI) and open [LIVE SITE ALERT] issues
  4. GSC indexing watchlist - the WATCHLIST of tools/gsc_weekly_report.py via the URL Inspection API ONLY

STRICTLY READ-ONLY: only HTTP GETs against the public site, `gh run list` / `gh issue list`, and the URL Inspection
endpoint (read-only OAuth scope webmasters.readonly). The Indexing API (urlNotifications:publish), sitemap pings and every
other Google endpoint are structurally blocked by a guard around the HTTP session, so no write quota is ever consumed.
No credential or secret is ever printed.

Exit code: 0 = everything healthy, 1 = a live check failed or a [LIVE SITE ALERT] issue is open (GSC never affects it).
"""
import importlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SITE_URL = "https://www.colddirect.co.uk/"
INSPECT_URL = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
READONLY_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
WORKFLOWS = [("Deploy", "deploy.yml"), ("Nightly auto-seo", "auto-seo-nightly.yml"), ("GSC Weekly Sync", "gsc-weekly-sync.yml")]
ALERT_TAG = "[LIVE SITE ALERT]"
ALERT_LABEL = "live-site-alert"
OK, BAD, WARN = "✅", "❌", "⚠️"


def now_utc():
    return datetime.now(timezone.utc)


def head(title):
    return ["", "━" * 78, " " + title, "━" * 78]


def table(headers, rows, indent="  "):
    """Plain aligned text table."""
    widths = [max(len(str(x)) for x in col) for col in zip(headers, *rows)] if rows else [len(h) for h in headers]
    fmt = indent + "  ".join("{:<%d}" % w for w in widths)
    out = [fmt.format(*headers), indent + "  ".join("-" * w for w in widths)]
    out += [fmt.format(*[str(c) for c in r]) for r in rows]
    return out


# ------------------------------------------------------------------ section 1: live smoke & speed
def smoke_section(res, lt):
    """res = live_smoke_test.run_all_checks() result; lt = the live_smoke_test module. Returns (lines, n_problems)."""
    rows = res["rows"]
    core = [r for r in rows if r[0][9:] in lt.INTEGRITY_PAGES and r[0].startswith("HTTP 200 ")]
    core_ok = sum(1 for r in core if r[2])
    blog = [r for r in rows if r[0] == "HTTP 200 /blog/"]
    assets = [r for r in rows if r[0] == lt.ASSET_ROW]
    robots = [r for r in rows if "robots.txt" in r[0] and not r[0].startswith("HTTP 200")]
    sm = [r for r in rows if r[0].startswith("HTTP 200 /sitemap.xml")]
    sm_rules = [r for r in rows if r[0].startswith(("sitemap contains", "sitemap excludes"))]
    redirects301 = [r for r in rows if r[0].startswith("301 ")]
    canon = [r for r in rows if r[0].startswith("Canonical redirect")]
    problems = len(res["failures"])
    lat = lt.latency_summary(res["latencies"])

    def mark(ok):
        return OK if ok else BAD

    L = head("1. LIVE SMOKE & SPEED  (tools/live_smoke_test.py checks)")
    L.append("  %s Core pages  HTTP 200 + Schema + Canonical + Phone : %d/%d OK" % (mark(core_ok == len(lt.INTEGRITY_PAGES)), core_ok, len(lt.INTEGRITY_PAGES)))
    L.append("  %s Response time                                     : %s" % (mark(not any(r[1].find("TOO SLOW") >= 0 for r in rows)), lat))
    slow = [r[0][9:] for r in rows if "⚠️ SLOW" in r[1]]
    if slow:
        L.append("  %s Slow pages (1.5-3 s)                              : %s" % (WARN, ", ".join(slow)))
    for r in assets:
        L.append("  %s Static assets (homepage)                          : %s" % (mark(r[2]), r[1]))
    for r in [r for r in rows if r[0] == getattr(lt, "AUDIO_ROW", None)]:
        L.append("  %s SEO audio assets (home + 9 money pages)          : %s" % (mark(r[2]), r[1]))
    for r in sm:
        L.append("  %s sitemap.xml                                       : %d URLs (HTTP %s)" % (mark(r[2]), len(res["urls"]), r[1].split(" ")[0]))
    if sm_rules:
        L.append("  %s sitemap must-have / must-not-have rules           : %d/%d OK" % (mark(all(r[2] for r in sm_rules)), sum(1 for r in sm_rules if r[2]), len(sm_rules)))
    for r in robots:
        L.append("  %s robots.txt                                        : %s" % (mark(r[2]), r[1]))
    if canon:
        L.append("  %s Canonical host redirects (-> 301 -> https://www.)  : %d/%d OK" % (mark(all(r[2] for r in canon)), sum(1 for r in canon if r[2]), len(canon)))
    if redirects301:
        L.append("  %s 301 redirects (web.config)                        : %d/%d OK" % (mark(all(r[2] for r in redirects301)), sum(1 for r in redirects301 if r[2]), len(redirects301)))
    L.append("")
    L += table(["Page", "Result"], [(r[0][9:], r[1] if r[2] else "FAIL: " + r[1]) for r in core + blog])
    if res["failures"]:
        L.append("")
        L.append("  FAILURES:")
        L += ["   - " + f for f in res["failures"]]
    return L, problems


# ------------------------------------------------------------------ section 2: SSL
def ssl_section(ssl_results):
    L = head("2. SSL CERTIFICATE HEALTH")
    rows, problems = [], 0
    for r in ssl_results:
        if r["error"] or r["days_remaining"] is None:
            rows.append((r["host"], "-", r["issuer"] or "-", "-", "FAIL: " + (r["error"] or "unknown")))
            problems += 1
            continue
        state = "OK" if r["ok"] else "FAIL (below %d days)" % 14
        warn = " (renew soon)" if r["ok"] and r["days_remaining"] < 30 else ""
        problems += 0 if r["ok"] else 1
        rows.append((r["host"], r["expires"], r["issuer"], str(r["days_remaining"]), state + warn))
    L += table(["Host", "Expires", "Issuer", "days_remaining", "Status"], rows)
    return L, problems


# ------------------------------------------------------------------ section 3: GitHub Actions & alerts
def run_gh(args, timeout=40):
    """Read-only gh call (list arguments, no shell). Returns parsed JSON; raises RuntimeError with a short reason."""
    try:
        p = subprocess.run(["gh"] + args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(type(e).__name__)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or "gh failed").strip().splitlines()[0][:120] if (p.stderr or "").strip() else "gh failed")
    return json.loads(p.stdout or "null")


def ago(iso, now):
    try:
        t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except Exception:  # noqa: BLE001
        return "?"
    s = int((now - t).total_seconds())
    if s < 90:
        return "just now"
    if s < 5400:
        return "%d min ago" % round(s / 60)
    if s < 172800:
        return "%d h ago" % round(s / 3600)
    return "%d days ago" % round(s / 86400)


def gh_section(gh=run_gh, now=None, which=shutil.which):
    """Returns (lines, problems). problems counts open alert issues only (a failed past run is shown, not counted)."""
    now = now or now_utc()
    L = head("3. GITHUB ACTIONS & ALERT STATUS")
    if not which("gh"):
        return L + ["  gh CLI not installed - section skipped."], 0
    rows, problems = [], 0
    for label, wf in WORKFLOWS:
        try:
            runs = gh(["run", "list", "--workflow", wf, "--limit", "1", "--json", "status,conclusion,createdAt,updatedAt,headSha,event"])
        except RuntimeError as e:
            rows.append((label, "n/a", "gh error: %s" % e, "-", "-"))
            continue
        if not runs:
            rows.append((label, "-", "no runs yet", "-", "-"))
            continue
        r = runs[0]
        state = r.get("conclusion") or r.get("status") or "?"
        stamp = (r.get("updatedAt") or r.get("createdAt") or "")
        rows.append((label, state, stamp.replace("T", " ").replace("Z", " UTC"), ago(stamp, now),
                     (r.get("headSha") or "")[:7] or "-"))
    L += table(["Workflow", "Latest run", "Timestamp", "Age", "Commit"], rows)
    L.append("")
    try:
        issues = gh(["issue", "list", "--state", "open", "--limit", "100", "--json", "number,title,labels,url"])
        alerts = [i for i in issues if ALERT_TAG in i.get("title", "") or any(lb.get("name") == ALERT_LABEL for lb in i.get("labels", []))]
        if alerts:
            problems += len(alerts)
            L.append("  %s Open %s issues: %d" % (BAD, ALERT_TAG, len(alerts)))
            L += ["     #%s %s  %s" % (i.get("number"), i.get("title"), i.get("url", "")) for i in alerts]
        else:
            L.append("  %s Open %s issues: 0" % (OK, ALERT_TAG))
    except RuntimeError as e:
        L.append("  %s could not read issues (%s)" % (WARN, e))
    return L, problems


# ------------------------------------------------------------------ section 4: GSC watchlist (URL Inspection ONLY)
class ReadOnlySession:
    """Wraps an authorised requests session so ONLY the URL Inspection endpoint can ever be called.
    Indexing API publishes, sitemap submissions, any other POST/PUT/DELETE and GETs raise PermissionError."""

    def __init__(self, session):
        self._s = session

    def post(self, url, **kw):
        if url != INSPECT_URL:
            raise PermissionError("site_status is read-only: blocked POST to %s" % url.split("?")[0])
        return self._s.post(url, **kw)

    def get(self, url, **kw):
        raise PermissionError("site_status is read-only: blocked GET to %s" % url.split("?")[0])

    put = delete = patch = get


def readonly_session():
    """Authorised read-only session or (None, reason). Never prints credentials."""
    try:
        ri = importlib.import_module("request_indexing")
        from google.auth.transport.requests import AuthorizedSession
    except Exception as e:  # noqa: BLE001
        return None, "Google client libraries unavailable (%s)" % type(e).__name__
    try:
        creds = ri.get_credentials()
    except FileNotFoundError:
        return None, "no local GSC credentials (GSC_CREDENTIALS_JSON not set, no key file)"
    except Exception as e:  # noqa: BLE001
        return None, "GSC credentials unreadable (%s)" % type(e).__name__
    try:
        creds = creds.with_scopes([READONLY_SCOPE])           # drop the indexing/write scope entirely
    except Exception:  # noqa: BLE001
        pass
    return ReadOnlySession(AuthorizedSession(creds)), ""


def fmt_crawl(s):
    s = (s or "").strip()
    if not s:
        return "never"
    return s.replace("T", " ").replace("Z", " UTC")[:16] + (" UTC" if s.endswith("Z") else "")


def gsc_section(inspector, watchlist, base="https://www.colddirect.co.uk"):
    """inspector.inspect(url) -> {verdict, coverageState, lastCrawlTime} | {error}. Returns (lines, summary)."""
    L = head("4. GSC INDEXING WATCHLIST  (URL Inspection API - read only)")
    rows = []
    indexed = waiting = errors = 0
    for slug in watchlist:
        res = inspector.inspect("%s/%s/" % (base, slug))
        if "error" in res:
            errors += 1
            rows.append(("/%s/" % slug, "n/a", "inspection failed (%s)" % res["error"], "-"))
            continue
        verdict = res.get("verdict", "?")
        if verdict == "PASS":
            indexed += 1
        else:
            waiting += 1
        rows.append(("/%s/" % slug, verdict, res.get("coverageState", "?"),
                     fmt_crawl(res.get("lastCrawlTime"))))
    L += table(["URL", "Verdict", "Coverage State", "Last Crawl"], rows)
    total = len(watchlist)
    score = "Indexed %d/%d (PASS)  |  Waiting %d  |  Not inspectable %d  |  Indexing API notifications sent: 0 (read-only)" % (
        indexed, total, waiting, errors)
    L += ["", "  " + score]
    return L, score


class GoogleInspector:
    """Thin adapter over tools/gsc_weekly_report.Indexer.inspect (the notify() half is never reachable: the session guard
    blocks every endpoint except URL Inspection and publish_ok is forced False)."""

    def __init__(self, session, site=SITE_URL):
        gw = importlib.import_module("gsc_weekly_report")
        self._ix = gw.Indexer(session, site)
        self._ix.publish_ok = False

    def inspect(self, url):
        return self._ix.inspect(url)


# ------------------------------------------------------------------ main
def build_dashboard(skip_gsc=False, skip_gh=False, smoke=None, gh=run_gh, gsc=None, now=None, which=shutil.which):
    """Assemble all sections. Everything external is injectable for the self-test. Returns (lines, exit_code)."""
    lt = importlib.import_module("live_smoke_test")
    now = now or now_utc()
    res = smoke() if smoke else lt.run_all_checks()
    out = ["", "COLD DIRECT  -  colddirect.co.uk  -  live site status      %s UTC   (read-only)" % now.strftime("%Y-%m-%d %H:%M")]
    problems = 0
    lines, p = smoke_section(res, lt)
    out += lines
    problems += p
    lines, p = ssl_section(res["ssl_results"])
    out += lines
    problems += p
    if skip_gh:
        out += head("3. GITHUB ACTIONS & ALERT STATUS") + ["  skipped (--skip-gh)"]
    else:
        lines, p = gh_section(gh, now, which)
        out += lines
        problems += p
    if skip_gsc:
        out += head("4. GSC INDEXING WATCHLIST") + ["  skipped (--skip-gsc)"]
    else:
        inspector, why = gsc() if gsc else _default_gsc()
        if inspector is None:
            out += head("4. GSC INDEXING WATCHLIST") + ["  skipped: %s" % why, "  (run with GSC_CREDENTIALS_JSON set to see live Google indexing status; --skip-gsc silences this)"]
        else:
            wl = importlib.import_module("gsc_weekly_report").WATCHLIST
            lines, _ = gsc_section(inspector, wl)
            out += lines
    out += ["", "━" * 78,
            " OVERALL: %s" % ("%s ALL GREEN" % OK if not problems else "%s %d item(s) need attention (see above)" % (BAD, problems)),
            "━" * 78]
    return out, (1 if problems else 0)


def _default_gsc():
    sess, why = readonly_session()
    if sess is None:
        return None, why
    return GoogleInspector(sess), ""


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return selftest()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    lines, code = build_dashboard(skip_gsc="--skip-gsc" in argv, skip_gh="--skip-gh" in argv)
    print("\n".join(lines))
    return code


# ------------------------------------------------------------------ self-test (offline)
def selftest():
    lt = importlib.import_module("live_smoke_test")
    gw = importlib.import_module("gsc_weekly_report")
    now = datetime(2026, 10, 21, 1, 30, tzinfo=timezone.utc)

    # ---- fake smoke result in the exact shape of run_all_checks()
    ok_val = lt.INTEGRITY_OK + " (120 ms)"
    rows = [("HTTP 200 /blog/", "200 (80 ms)", True)]
    rows += [("HTTP 200 " + p, ok_val, True) for p in lt.INTEGRITY_PAGES]
    rows += [(lt.ASSET_ROW, "13/13 core CSS/JS/Image assets HTTP 200 & non-empty (4 CSS, 4 JS, 2 icon, 3 image)", True),
             (lt.AUDIO_ROW, "10/10 MP3 audio summaries HTTP 200, audio/mpeg & AudioObject schema intact", True),
             ("HTTP 200 /sitemap.xml (123 URLs)", "200 (90 ms)", True),
             ("sitemap contains /blog/", "yes", True), ("sitemap excludes /about/", "absent", True),
             ("301 /about/ -> /about-us/", "301 /about-us/", True),
             ("🤖 robots.txt", "HTTP 200, Googlebot allowed, Sitemap declared (70 ms)", True),
             ("Canonical redirect http://colddirect.co.uk/", "x", True), ("Canonical redirect https://colddirect.co.uk/", "x", True),
             ("SSL certificate www.colddirect.co.uk", "x", True)]
    ssl_ok = [{"host": "www.colddirect.co.uk", "ok": True, "days_remaining": 183, "expires": "2027-04-22", "issuer": "GlobalSign nv-sa (AlphaSSL CA 2025)", "error": ""},
              {"host": "colddirect.co.uk", "ok": True, "days_remaining": 183, "expires": "2027-04-22", "issuer": "GlobalSign nv-sa (AlphaSSL CA 2025)", "error": ""}]
    res = {"rows": rows, "failures": [], "latencies": [100, 200, 300], "urls": ["u"] * 123, "ssl_results": ssl_ok, "bodies": {}}
    text, p = smoke_section(res, lt)
    t = "\n".join(text)
    assert p == 0 and "11/11 OK" in t and "average 200 ms, max 300 ms (3 requests)" in t and "13/13 core CSS/JS/Image" in t, t
    assert "123 URLs (HTTP 200)" in t and "robots.txt" in t and "Canonical host redirects" in t and "2/2 OK" in t, t
    assert "/blog/" in t and "/commercial-fridge-repair-enfield/" in t
    assert "SEO audio assets" in t and "10/10 MP3 audio summaries HTTP 200, audio/mpeg & AudioObject schema intact" in t, t
    # a failing page and a SLOW page are surfaced; FAILURES listed
    bad = dict(res, rows=[("HTTP 200 /cold-room-repair-london/", "HTTP 200 but canonical missing (90 ms)", False) if r[0] == "HTTP 200 /cold-room-repair-london/"
                          else ("HTTP 200 /", ok_val.replace("120 ms", "1800 ms ⚠️ SLOW"), True) if r[0] == "HTTP 200 /" else r for r in rows],
               failures=["/cold-room-repair-london/ content integrity: canonical missing"])
    text, p = smoke_section(bad, lt)
    t = "\n".join(text)
    assert p == 1 and "10/11 OK" in t and "FAIL: HTTP 200 but canonical missing" in t and "Slow pages" in t and "FAILURES:" in t, t

    # ---- SSL section
    text, p = ssl_section(ssl_ok)
    t = "\n".join(text)
    assert p == 0 and "2027-04-22" in t and "183" in t and "GlobalSign" in t and "www.colddirect.co.uk" in t and "\n" in t
    expiring = [dict(ssl_ok[0], ok=False, days_remaining=5), dict(ssl_ok[1], ok=False, days_remaining=None, error="could not connect", issuer="", expires="")]
    text, p = ssl_section(expiring)
    assert p == 2 and "FAIL" in "\n".join(text) and "could not connect" in "\n".join(text)

    # ---- GitHub section (fake gh)
    def fake_gh(alerts):
        def gh(args):
            if args[0] == "run":
                wf = args[args.index("--workflow") + 1]
                return {"deploy.yml": [{"status": "completed", "conclusion": "success", "updatedAt": "2026-10-21T01:24:30Z", "createdAt": "2026-10-21T01:22:00Z", "headSha": "f19249c9", "event": "push"}],
                        "auto-seo-nightly.yml": [{"status": "completed", "conclusion": "failure", "updatedAt": "2026-10-20T20:23:00Z", "createdAt": "2026-10-20T20:21:00Z", "headSha": "abcdef1", "event": "schedule"}],
                        "gsc-weekly-sync.yml": []}[wf]
            return alerts
        return gh
    text, p = gh_section(fake_gh([{"number": 9, "title": "unrelated bug", "labels": [], "url": "u"}]), now, which=lambda x: "/usr/bin/gh")
    t = "\n".join(text)
    assert p == 0 and "Deploy" in t and " success " in t and "f19249c" in t and " failure " in t and "no runs yet" in t, t
    assert "2026-10-21 01:24:30 UTC" in t and "6 min ago" in t and "Open [LIVE SITE ALERT] issues: 0" in t, t
    text, p = gh_section(fake_gh([{"number": 12, "title": "🚨 [LIVE SITE ALERT] ColdDirect Smoke Test / Auto-SEO Failure", "labels": [], "url": "http://x/12"},
                                  {"number": 13, "title": "other", "labels": [{"name": "live-site-alert"}], "url": "http://x/13"}]), now, which=lambda x: "gh")
    assert p == 2 and "#12" in "\n".join(text) and "#13" in "\n".join(text), text
    text, p = gh_section(lambda a: (_ for _ in ()).throw(RuntimeError("HTTP 401")), now, which=lambda x: "gh")
    assert p == 0 and "gh error: HTTP 401" in "\n".join(text) and "could not read issues" in "\n".join(text)
    text, p = gh_section(None, now, which=lambda x: None)
    assert p == 0 and "not installed" in "\n".join(text)
    assert ago("2026-10-20T01:30:00Z", now) == "24 h ago" and ago("2026-10-10T01:30:00Z", now) == "11 days ago" and ago("garbage", now) == "?"

    # ---- GSC section: fake inspector, read-only guard
    calls = []

    class FakeInspector:
        def inspect(self, url):
            calls.append(url)
            i = len(calls)
            if i == 1:
                return {"verdict": "PASS", "coverageState": "Submitted and indexed", "lastCrawlTime": "2026-10-19T08:15:00Z"}
            if i == 2:
                return {"error": "HTTP 429"}
            return {"verdict": "NEUTRAL", "coverageState": "Discovered - currently not indexed", "lastCrawlTime": ""}
    wl = gw.WATCHLIST
    assert len(wl) == 14
    text, score = gsc_section(FakeInspector(), wl)
    t = "\n".join(text)
    assert len(calls) == 14 and all(c.startswith("https://www.colddirect.co.uk/") and c.endswith("/") for c in calls)
    assert score.startswith("Indexed 1/14 (PASS)  |  Waiting 12  |  Not inspectable 1") and "notifications sent: 0" in score, score
    assert "Submitted and indexed" in t and "2026-10-19 08:15 UTC" in t and "never" in t and "inspection failed (HTTP 429)" in t
    # table columns align: header and every data row share the same column offsets
    data = [l for l in text if l.startswith("  /")]
    assert len(data) == 14 and ("/%s/" % wl[0]) in t
    hdr = next(l for l in text if l.lstrip().startswith("URL"))
    c = hdr.index("Verdict")
    assert all(l[c - 2:c] == "  " and l[c] != " " for l in data), data
    c2 = hdr.index("Coverage State")
    assert all(l[c2 - 2:c2] == "  " and l[c2] != " " for l in data), data
    assert fmt_crawl("") == "never" and fmt_crawl("2026-10-19T08:15:00Z") == "2026-10-19 08:15 UTC"

    # the guard: only URL Inspection may be POSTed; everything else (Indexing API, sitemaps, GETs, PUT) is blocked
    sent = []

    class Raw:
        def post(self, url, **kw):
            sent.append(url)

            class R:
                status_code = 200
                def json(self):
                    return {"inspectionResult": {"indexStatusResult": {"verdict": "PASS", "coverageState": "x", "lastCrawlTime": ""}}}
            return R()
    g = ReadOnlySession(Raw())
    ix = gw.Indexer(g, SITE_URL)
    ix.publish_ok = False
    assert ix.inspect("https://www.colddirect.co.uk/")["verdict"] == "PASS" and sent == [INSPECT_URL]
    assert ix.notify("https://www.colddirect.co.uk/") .startswith("skipped") and sent == [INSPECT_URL]        # notify can never fire
    for fn, url in ((g.post, "https://indexing.googleapis.com/v3/urlNotifications:publish"),
                    (g.post, "https://www.googleapis.com/webmasters/v3/sites/x/sitemaps/y"),
                    (g.put, "https://www.googleapis.com/webmasters/v3/sites/x/sitemaps/y"),
                    (g.get, "https://www.googleapis.com/webmasters/v3/sites")):
        try:
            fn(url, json={})
            raise AssertionError("guard let through " + url)
        except PermissionError as e:
            assert "read-only" in str(e)
    assert sent == [INSPECT_URL]
    assert INSPECT_URL.endswith("index:inspect") and READONLY_SCOPE.endswith("webmasters.readonly")

    # ---- whole dashboard: skip flags, missing credentials fallback, exit codes, no secrets
    fake_smoke = lambda: res
    out, code = build_dashboard(skip_gsc=True, skip_gh=True, smoke=fake_smoke, now=now)
    t = "\n".join(out)
    assert code == 0 and "ALL GREEN" in t and "skipped (--skip-gsc)" in t and "skipped (--skip-gh)" in t, t
    for sec in ("1. LIVE SMOKE", "2. SSL CERTIFICATE", "3. GITHUB", "4. GSC"):
        assert sec in t, sec
    out, code = build_dashboard(skip_gh=True, smoke=fake_smoke, gsc=lambda: (None, "no local GSC credentials (GSC_CREDENTIALS_JSON not set, no key file)"), now=now)
    t = "\n".join(out)
    assert code == 0 and "skipped: no local GSC credentials" in t and "--skip-gsc" in t, t
    out, code = build_dashboard(skip_gh=True, smoke=fake_smoke, gsc=lambda: (FakeInspector(), ""), now=now)
    assert code == 0 and "Indexed" in "\n".join(out) and "Waiting" in "\n".join(out)             # GSC never changes the exit code
    out, code = build_dashboard(skip_gsc=True, skip_gh=True, smoke=lambda: bad, now=now)
    assert code == 1 and "need attention" in "\n".join(out)
    out, code = build_dashboard(skip_gsc=True, gh=fake_gh([{"number": 5, "title": "[LIVE SITE ALERT] x", "labels": [], "url": "u"}]),
                                smoke=fake_smoke, now=now, which=lambda x: "gh")
    assert code == 1 and "Open [LIVE SITE ALERT] issues: 1" in "\n".join(out)
    out, code = build_dashboard(skip_gsc=True, gh=fake_gh([]), smoke=fake_smoke, now=now, which=lambda x: "gh")
    assert code == 0 and "Open [LIVE SITE ALERT] issues: 0" in "\n".join(out)
    assert "BEGIN" not in "\n".join(out) and "private_key" not in "\n".join(out)
    print("selftest OK (site_status: sections 1-4 render; failing page / slow page / expiring SSL / open alert / gh error / no gh; "
          "GSC table + scoreboard; read-only guard blocks Indexing API, sitemaps, PUT and GET; --skip-gsc and missing-credentials fallback)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
