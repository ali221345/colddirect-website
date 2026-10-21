#!/usr/bin/env python3
"""Live smoke test for https://www.colddirect.co.uk - run in GitHub Actions after every deploy.

Checks (all against the LIVE site, no redirects followed for the 200 checks):
  * HTTP 200 on the homepage, the 9 core money pages, /commercial-fridge-repair-enfield/ and /blog/
  * live HTML content integrity of the homepage, the 9 core money pages and /commercial-fridge-repair-enfield/:
    no noindex (X-Robots-Tag header or robots/googlebot meta), exactly one self-referencing canonical
    (https://www.colddirect.co.uk/<slug>/), non-empty <title> and <h1>, >=1 JSON-LD block and every block parses
    with json.loads, official phone 07983 759320 present and no dummy 123 4567 / 1234567. A passing row reads
    "HTTP 200 + Schema + Canonical + Phone OK"; a failing row names the exact failing check(s).
  * response time (time.monotonic, ms) of the homepage, 9 core pages, Enfield page, /blog/, sitemap.xml and robots.txt:
    < 1500 ms healthy; 1500-3000 ms passes with a "⚠️ SLOW" note; > 3000 ms is retried once and FAILS only if the
    retry is also > 3000 ms. Every row shows "(N ms)"; the Step Summary header shows average and max.
  * critical static assets referenced by the live homepage HTML (same-origin only, max 14, de-duplicated):
    stylesheets, <script src>, favicon / apple-touch-icon / og:image and the first 3 <img> tags. Each must be
    HTTP 200, non-empty and not an HTML (soft-404) page. Table row "🎨 Static Assets (Homepage)"; a failure lists the URL.
  * sitemap.xml is HTTP 200, contains /blog/ and /commercial-fridge-repair-enfield/, and does NOT contain
    /about/, /news/, /preview-colddirect-homepage/, /refrigeration-brands-repairs-london/
  * the 301s from web.config: /about/ -> /about-us/ and /refrigeration-brands-repairs-london/ -> /refrigeration-brands-repair-london/
  * robots.txt: HTTP 200 text body (not an HTML error page); neither "User-agent: *" nor Googlebot may be blocked
    ("Disallow: /"), none of /blog/ and the money-page prefixes may be disallowed, and the exact line
    "Sitemap: https://www.colddirect.co.uk/sitemap.xml" must be present (table row "🤖 robots.txt")
  * canonical host / protocol: http://colddirect.co.uk/, http://www.colddirect.co.uk/ and https://colddirect.co.uk/
    must each reach https://www.colddirect.co.uk/ (HTTP 200) via permanent 301/308 redirects only, at most 2 hops,
    no loop; a direct 200 (duplicate host) or a temporary 302/307 FAILS. Exact hop chain is printed / summarised.
  * TLS certificate of www.colddirect.co.uk and colddirect.co.uk (port 443, 10 s timeout, full verification):
    FAILS if the certificate is invalid, expired or has fewer than 14 days left (days_remaining < 14)
Writes a Markdown summary (including the live sitemap URL count and SSL status / expiry / days remaining)
to $GITHUB_STEP_SUMMARY.
Offline unit tests of the SSL threshold logic: python tools/live_smoke_test.py --selftest
Exit code 0 = all good, 1 = at least one check failed.

Env: AUTO_SEO_RESPONSE (optional) - the text returned by auto-seo.aspx, shown in the summary.
Args: --attempt N --max-attempts M  (summary is written on success or on the last attempt only)
Nothing secret is ever printed (the auto-seo key is not passed to this script).
"""
import math
import os
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE = "https://www.colddirect.co.uk"

# TLS certificate health: both host names must present a valid certificate with >= SSL_MIN_DAYS left.
SSL_HOSTS = ["www.colddirect.co.uk", "colddirect.co.uk"]
SSL_MIN_DAYS = 14      # fewer days remaining (or expired / invalid) = smoke test FAILS
SSL_WARN_DAYS = 30     # still passes, but flagged "renew soon" in the output
SSL_TIMEOUT = 10       # seconds for connect + handshake
UA = "Mozilla/5.0 (compatible; ColdDirect-CI-SmokeTest/1.0)"

CORE = [
    "commercial-fridge-repair-london", "commercial-freezer-repair-london", "cold-room-repair-london",
    "fridge-repair-london", "freezer-repair-london", "catering-repair-london",
    "commercial-appliances-repair-london", "air-conditioning-repair-london", "cellar-cooler-repair-london",
]
PAGES = ["/"] + ["/%s/" % s for s in CORE] + ["/commercial-fridge-repair-enfield/", "/blog/"]
MUST_BE_IN_SITEMAP = [BASE + "/blog/", BASE + "/commercial-fridge-repair-enfield/"]
MUST_NOT_BE_IN_SITEMAP = [BASE + "/about/", BASE + "/news/", BASE + "/preview-colddirect-homepage/",
                          BASE + "/refrigeration-brands-repairs-london/"]
REDIRECTS = [
    ("/about/", "/about-us/"),
    ("/refrigeration-brands-repairs-london/", "/refrigeration-brands-repair-london/"),
]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def fetch(path, body=False, tries=3):
    last = None
    for _ in range(tries):
        req = urllib.request.Request(BASE + path, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
        try:
            r = OPENER.open(req, timeout=40)
            return r.status, dict(r.headers), (r.read().decode("utf-8", "replace") if body else "")
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), ""
        except Exception as e:  # network blip - retry
            last = e
    return 0, {}, "ERR %s" % type(last).__name__


# ------------------------------------------------------------------ response-time (latency) enforcement
LAT_SLOW_MS = 1500     # >= this: "SLOW" warning, still PASS
LAT_FAIL_MS = 3000     # >  this: retry once; if the retry is ALSO > this the smoke test FAILS


def timed_fetch(fn, clock=time.monotonic):
    """Run fn() -> (status, headers, body) and measure it in whole milliseconds with a monotonic clock.

    A response slower than LAT_FAIL_MS is retried exactly once (GitHub runner network jitter); the retry's
    time is the one that counts. level: ok (<1500) / slow (1500..3000, warning only) / fail (>3000 twice).
    """
    def once():
        t0 = clock()
        res = fn()
        return res, int(round((clock() - t0) * 1000))

    res, ms = once()
    first = None
    if ms > LAT_FAIL_MS:
        first = ms
        res, ms = once()
    level = "fail" if ms > LAT_FAIL_MS else ("slow" if ms >= LAT_SLOW_MS else "ok")
    return {"result": res, "ms": ms, "first_ms": first, "level": level}


def latency_note(t):
    """Text appended to a row: ' (245 ms)', ' (1800 ms ⚠️ SLOW)', spike / persistent-slow variants."""
    ms, first, level = t["ms"], t["first_ms"], t["level"]
    if level == "fail":
        return " (%d ms, retry of %d ms also > %d ms ❌ TOO SLOW)" % (ms, first, LAT_FAIL_MS)
    if first is not None:
        return " (%d ms%s after a transient %d ms spike, retried)" % (ms, " ⚠️ SLOW" if level == "slow" else "", first)
    return " (%d ms%s)" % (ms, " ⚠️ SLOW" if level == "slow" else "")


def with_latency(row, t, failures, label):
    """Append the timing to a (name, value, ok) row; a persistent >3000 ms response fails the row and the run."""
    name, val, ok = row
    if t["level"] == "fail":
        failures.append("%s response time %d ms (retry of %d ms also) exceeds %d ms" % (label, t["ms"], t["first_ms"], LAT_FAIL_MS))
    return (name, val + latency_note(t), ok and t["level"] != "fail")


def latency_summary(samples):
    """One-line Average / Max over the measured pages (ms)."""
    if not samples:
        return "n/a"
    return "average %d ms, max %d ms (%d requests)" % (round(sum(samples) / len(samples)), max(samples), len(samples))


# ------------------------------------------------------------------ live HTML content integrity
# Pages that get the full integrity check: homepage, the 9 core money pages and the Enfield page (not /blog/).
INTEGRITY_PAGES = [p for p in PAGES if p != "/blog/"]
INTEGRITY_OK = "HTTP 200 + Schema + Canonical + Phone OK"
OFFICIAL_PHONE_RE = re.compile(r"(?<!\d)(?:\+44\s?|0)7983\s?759\s?320(?!\d)")   # 07983 759320 / 07983759320 / +447983759320
DUMMY_PHONE_RE = re.compile(r"123[\s.\-]?4567")                                  # 123 4567 / 1234567 placeholders
_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
_ATTR_RE = re.compile(r"""([^\s=/>"']+)\s*=\s*("[^"]*"|'[^']*'|[^\s"'>]+)""")
_ROBOTS_NAMES = ("robots", "googlebot", "googlebot-news", "bingbot")


def _attrs(tag):
    out = {}
    for k, v in _ATTR_RE.findall(tag):
        out[k.lower()] = v.strip("\"'")
    return out


def _text(fragment):
    import html as _html
    return " ".join(_html.unescape(re.sub(r"<[^>]*>", " ", fragment)).split())


def _has_noindex(value):
    return any(tok.strip().lower() in ("noindex", "none") for tok in re.split(r"[,\s]+", value or "") if tok)


def check_page_integrity(path, status, headers, body):
    """Validate one live page. Returns {"ok", "summary", "problems"}.

    Checks: HTTP 200; no noindex (X-Robots-Tag header, robots/googlebot/bingbot meta); exactly the expected
    self-referencing canonical; non-empty <title> and <h1>; >=1 JSON-LD block and every block parses with json.loads;
    official mobile 07983 759320 present and no dummy 123 4567 / 1234567 placeholder anywhere in the HTML.
    """
    import json
    problems = []
    if status != 200:
        return {"ok": False, "summary": "HTTP %s" % status, "problems": ["HTTP %s instead of 200" % status]}
    h = {k.lower(): v for k, v in (headers or {}).items()}
    src = _COMMENT_RE.sub("", body or "")            # ignore commented-out markup

    # 1. noindex (response header + meta tags)
    if _has_noindex(h.get("x-robots-tag", "")):
        problems.append("noindex in X-Robots-Tag header (%s)" % h.get("x-robots-tag"))
    for tag in re.findall(r"<meta\b[^>]*>", src, re.I):
        a = _attrs(tag)
        if a.get("name", "").lower() in _ROBOTS_NAMES and _has_noindex(a.get("content", "")):
            problems.append("noindex in <meta name=%s content=%s>" % (a["name"], a.get("content")))

    # 2. canonical must be present, single and exactly self-referencing
    expected = BASE + path
    canon = []
    for tag in re.findall(r"<link\b[^>]*>", src, re.I):
        a = _attrs(tag)
        if "canonical" in a.get("rel", "").lower().split():
            canon.append(a.get("href", ""))
    if not canon:
        problems.append("canonical missing")
    elif len(set(canon)) > 1:
        problems.append("multiple conflicting canonicals (%s)" % ", ".join(sorted(set(canon))))
    elif canon[0] != expected:
        problems.append("canonical mismatch (got %s, expected %s)" % (canon[0] or "<empty>", expected))

    # 3. title and h1
    m = re.search(r"<title\b[^>]*>(.*?)</title>", src, re.I | re.S)
    if not m:
        problems.append("<title> missing")
    elif not _text(m.group(1)):
        problems.append("<title> empty")
    h1s = re.findall(r"<h1\b[^>]*>(.*?)</h1>", src, re.I | re.S)
    if not h1s:
        problems.append("<h1> missing")
    elif not any(_text(x) for x in h1s):
        problems.append("<h1> empty")

    # 4. JSON-LD: at least one block, every block must parse
    blocks = [m2.group(2) for m2 in re.finditer(
        r"<script\b([^>]*)>(.*?)</script>", src, re.I | re.S) if "application/ld+json" in m2.group(1).lower()]
    if not blocks:
        problems.append("JSON-LD schema missing")
    for i, blk in enumerate(blocks, 1):
        try:
            json.loads(blk)
        except ValueError as e:
            problems.append("JSON-LD block %d invalid (%s)" % (i, str(e)[:60]))

    # 5. phone numbers (raw HTML, so tel: links and JSON-LD count too)
    if not OFFICIAL_PHONE_RE.search(body or ""):
        problems.append("official phone 07983 759320 missing")
    if DUMMY_PHONE_RE.search(body or ""):
        problems.append("dummy phone pattern (123 4567 / 1234567) present")

    if problems:
        return {"ok": False, "summary": "HTTP 200 but " + "; ".join(problems), "problems": problems}
    return {"ok": True, "summary": INTEGRITY_OK, "problems": []}


def integrity_checks(paths=None, fetcher=None, latencies=None, clock=time.monotonic, bodies=None):
    """Fetch every core page (with body, timed) and validate it. Returns (rows, failures).
    latencies: optional list that receives the response time (ms) of every page.
    bodies: optional dict that receives {path: html} so other checks reuse the fetched HTML."""
    fetcher = fetcher or (lambda p: fetch(p, body=True))
    rows, failures = [], []
    for path in (INTEGRITY_PAGES if paths is None else paths):
        t = timed_fetch(lambda: fetcher(path), clock)
        status, headers, body = t["result"]
        if bodies is not None:
            bodies[path] = body
        r = check_page_integrity(path, status, headers, body)
        if latencies is not None:
            latencies.append(t["ms"])
        rows.append(with_latency(("HTTP 200 " + path, r["summary"], r["ok"]), t, failures, path))
        if not r["ok"]:
            failures.append("%s content integrity: %s" % (path, "; ".join(r["problems"])))
    return rows, failures


# ------------------------------------------------------------------ critical static assets of the homepage
ASSET_ROW = "🎨 Static Assets (Homepage)"
ASSET_MAX = 14             # cap so the smoke test stays fast (4 CSS + 4 JS + icons/og:image + 3 images fit)
ASSET_IMG_COUNT = 3        # first N <img> tags of the page = logo / hero (above the fold)
ASSET_MAX_BYTES = 8 * 1024 * 1024
_HOST = urllib.parse.urlsplit(BASE).netloc.lower()


def fetch_asset(url, tries=2):
    """GET one absolute same-origin URL (no redirects followed). Returns (status, headers, raw bytes)."""
    for _ in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
        try:
            r = OPENER.open(req, timeout=40)
            return r.status, dict(r.headers), r.read(ASSET_MAX_BYTES)
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), b""
        except Exception:  # noqa: BLE001 - network blip, retry once
            pass
    return 0, {}, b""


def _same_origin(ref, page_url):
    """Absolute https URL on www.colddirect.co.uk (fragment removed) or None for external / non-http refs."""
    ref = (ref or "").strip()
    if not ref or ref.lower().startswith(("data:", "javascript:", "mailto:", "tel:", "about:", "#")):
        return None
    full = urllib.parse.urljoin(page_url, ref)
    parts = urllib.parse.urlsplit(full)
    if parts.scheme not in ("http", "https") or parts.netloc.lower() != _HOST:
        return None
    return urllib.parse.urlunsplit(("https", parts.netloc, parts.path or "/", parts.query, ""))


def extract_assets(html, page_url=BASE + "/", limit=ASSET_MAX):
    """Critical same-origin assets of a page as an ordered, de-duplicated [(kind, url)] list.

    kinds: css (rel=stylesheet), js (<script src>), icon (favicon / apple-touch-icon / og:image),
    img (the first 3 <img> tags). External hosts (analytics, CDNs, fonts) are ignored.
    """
    src = _COMMENT_RE.sub("", html or "")
    found = {"css": [], "js": [], "icon": [], "img": []}
    for tag in re.findall(r"<link\b[^>]*>", src, re.I):
        a = _attrs(tag)
        rel = a.get("rel", "").lower().split()
        if "stylesheet" in rel:
            found["css"].append(a.get("href"))
        elif any(r in ("icon", "apple-touch-icon", "apple-touch-icon-precomposed") for r in rel):
            found["icon"].append(a.get("href"))
    for tag in re.findall(r"<script\b[^>]*>", src, re.I):
        found["js"].append(_attrs(tag).get("src"))
    for tag in re.findall(r"<meta\b[^>]*>", src, re.I):
        a = _attrs(tag)
        if (a.get("property") or a.get("name") or "").lower() == "og:image":
            found["icon"].append(a.get("content"))
    for tag in re.findall(r"<img\b[^>]*>", src, re.I)[:ASSET_IMG_COUNT]:
        found["img"].append(_attrs(tag).get("src"))
    out, seen = [], set()
    for kind in ("css", "js", "icon", "img"):
        for ref in found[kind]:
            url = _same_origin(ref, page_url)
            if url and url not in seen:
                seen.add(url)
                out.append((kind, url))
    return out[:limit]


# ------------------------------------------------------------------ spoken SEO audio summaries (homepage + 9 money hubs)
AUDIO_ROW = "🔊 SEO Audio Assets"    # same string as seo_integrity_check.AUDIO_ROW (asserted in selftest)


def audio_checks(bodies, fetcher=fetch_asset):
    """Verify the <audio> embeds, AudioObject/SpeakableSpecification JSON-LD and the live MP3 files of the homepage
    and the 9 money pages, reusing the already-fetched HTML in `bodies` {path: html}. The logic lives in
    seo_integrity_check.py (single source of truth, also run by the 24 h integrity job). Returns (row, failures)."""
    import seo_integrity_check as sic
    ok, text, problems = sic.audio_check(lambda p: (200, bodies[p]) if bodies.get(p) else (0, ""), fetcher,
                                         base=BASE)
    return (AUDIO_ROW, text, ok), ["SEO audio: " + p for p in problems]


def looks_like_html(headers, data):
    """True for an HTML document (soft-404 / error page) served where CSS, JS or an image is expected."""
    ct = {k.lower(): v for k, v in (headers or {}).items()}.get("content-type", "").lower()
    if "text/html" in ct or "application/xhtml" in ct:
        return True
    head = (data or b"")[:1024].lstrip(b"\xef\xbb\xbf \t\r\n").lower()
    return head.startswith((b"<!doctype html", b"<!doctype", b"<html", b"<head", b"<body", b"<title"))


def check_asset(kind, url, fetcher=fetch_asset):
    """Returns None when healthy, otherwise a short reason."""
    status, headers, data = fetcher(url)
    if status != 200:
        return "HTTP %s" % status
    if not data:
        return "empty (0 bytes)"
    if looks_like_html(headers, data):
        return "HTML page served instead of %s (soft-404)" % {"css": "CSS", "js": "JavaScript"}.get(kind, "an image")
    return None


def asset_checks(html, fetcher=fetch_asset, page_url=BASE + "/"):
    """Fetch and validate the homepage's critical assets. Returns (row, failures)."""
    assets = extract_assets(html, page_url)
    if not assets:
        msg = "no same-origin CSS/JS/image assets found in the homepage HTML"
        return (ASSET_ROW, msg, False), ["Static assets: " + msg]
    bad = []
    for kind, url in assets:
        why = check_asset(kind, url, fetcher)
        if why:
            bad.append((url, why))
    n, kinds = len(assets), {}
    for kind, _ in assets:
        kinds[kind] = kinds.get(kind, 0) + 1
    mix = ", ".join("%d %s" % (kinds[k], lbl) for k, lbl in (("css", "CSS"), ("js", "JS"), ("icon", "icon"), ("img", "image")) if k in kinds)
    if not bad:
        return (ASSET_ROW, "%d/%d core CSS/JS/Image assets HTTP 200 & non-empty (%s)" % (n, n, mix), True), []
    detail = "; ".join("%s -> %s" % (u.replace(BASE, ""), w) for u, w in bad)
    row = (ASSET_ROW, "%d/%d healthy, FAILING: %s" % (n - len(bad), n, detail), False)
    return row, ["Static asset %s: %s" % (u, w) for u, w in bad]


# ------------------------------------------------------------------ robots.txt health
ROBOTS_SITEMAP = "https://www.colddirect.co.uk/sitemap.xml"
# path prefixes that must stay crawlable; every one is tested literally AND as a real page ("<prefix>london/")
ROBOTS_CRITICAL = ["/blog/", "/commercial-fridge-repair-", "/cold-room-repair-", "/fridge-repair-", "/freezer-repair-",
                   "/catering-repair-", "/air-conditioning-repair-", "/cellar-cooler-repair-"]


def parse_robots(text):
    """-> (groups, sitemaps). groups = list of (set(lower-case agents), [(directive, value), ...]) where directive is
    'allow' or 'disallow'. Consecutive User-agent lines share one group (as Google does)."""
    groups, sitemaps = [], []
    agents, rules, in_rules = [], [], False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip().lower(), val.strip()
        if key == "user-agent":
            if in_rules:
                groups.append((set(agents), rules))
                agents, rules, in_rules = [], [], False
            agents.append(val.lower())
        elif key in ("allow", "disallow"):
            in_rules = True
            rules.append((key, val))
        elif key == "sitemap":
            sitemaps.append(val)
    if agents:
        groups.append((set(agents), rules))
    return groups, sitemaps


def _rule_regex(pattern):
    return re.compile("^" + re.escape(pattern).replace(r"\*", ".*").replace(r"\$", "$"))


def robots_allows(groups, agent, path):
    """Google semantics: the most specific user-agent group wins (named group beats '*'); the longest matching
    Allow/Disallow wins, Allow wins a tie; an empty Disallow allows everything."""
    agent = agent.lower()
    chosen = [g for g in groups if agent in g[0]] or [g for g in groups if "*" in g[0]]
    best_len, allowed = -1, True
    for _, rules in chosen:
        for kind, val in rules:
            if val == "":
                continue
            if _rule_regex(val).match(path):
                n = len(val)
                if n > best_len or (n == best_len and kind == "allow"):
                    best_len, allowed = n, (kind == "allow")
    return allowed


def check_robots(status, headers, body):
    """Returns dict(ok, problems[list], summary). Healthy = HTTP 200 text body, '*' and Googlebot may crawl '/' and
    every critical path, and the exact 'Sitemap: https://www.colddirect.co.uk/sitemap.xml' line is declared."""
    problems = []
    ctype = {k.lower(): v for k, v in (headers or {}).items()}.get("content-type", "").lower()
    text = (body or "").lstrip("\ufeff")
    if status != 200:
        problems.append("robots.txt returned HTTP %s" % status)
    elif not text.strip():
        problems.append("robots.txt body is empty")
    elif "html" in ctype or re.search(r"<\s*(html|body|head|!doctype)", text[:1000], re.I):
        problems.append("robots.txt looks like an HTML page, not a text file")
    elif not re.search(r"^\s*user-agent\s*:", text, re.I | re.M):
        problems.append("robots.txt has no User-agent directive")
    if problems:
        return {"ok": False, "problems": problems, "summary": "; ".join(problems)}
    groups, sitemaps = parse_robots(text)
    for agent, label in (("*", "User-agent: *"), ("googlebot", "Googlebot")):
        if not robots_allows(groups, agent, "/"):
            problems.append("blanket 'Disallow: /' blocks %s" % label)
            continue
        for prefix in ROBOTS_CRITICAL:
            for sample in sorted({prefix, prefix if prefix.endswith("/") else prefix + "london/"}):
                if not robots_allows(groups, agent, sample):
                    problems.append("%s blocked for %s" % (sample, label))
    if ROBOTS_SITEMAP not in sitemaps:
        problems.append("missing 'Sitemap: %s'" % ROBOTS_SITEMAP)
    if problems:
        return {"ok": False, "problems": problems, "summary": "; ".join(problems)}
    return {"ok": True, "problems": [], "summary": "HTTP 200, Googlebot allowed, Sitemap declared"}


def robots_check(fetcher=None):
    code, headers, body = (fetcher or (lambda: fetch("/robots.txt", body=True)))()
    r = check_robots(code, headers, body)
    row = ("🤖 robots.txt", r["summary"], r["ok"])
    return row, ([] if r["ok"] else ["robots.txt: " + r["summary"]])


# ------------------------------------------------------------------ canonical host / protocol redirects
CANONICAL = "https://www.colddirect.co.uk/"
CANONICAL_VARIANTS = ["http://colddirect.co.uk/", "http://www.colddirect.co.uk/", "https://colddirect.co.uk/"]
MAX_REDIRECT_HOPS = 2


def fetch_first_hop(url, tries=3):
    """One request, redirects NOT followed. Returns (status, Location header or '')."""
    last = None
    for _ in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
        try:
            r = OPENER.open(req, timeout=40)
            return r.status, ""
        except urllib.error.HTTPError as e:
            return e.code, {k.lower(): v for k, v in dict(e.headers).items()}.get("location", "")
        except Exception as e:  # noqa: BLE001 - network blip, retry
            last = e
    return 0, "ERR %s" % type(last).__name__


def check_canonical_redirect(start, first_hop=fetch_first_hop, canonical=CANONICAL, max_hops=MAX_REDIRECT_HOPS):
    """Follow `start` hop by hop and require: only permanent (301/308) redirects, at most `max_hops` of them,
    no loop, and a final HTTP 200 on the canonical URL. A direct 200 on a non-canonical variant is a failure
    (duplicate host). Returns dict(start, ok, chain, error); chain looks like
    'http://colddirect.co.uk/ -> 301 -> https://www.colddirect.co.uk/ (200)'."""
    chain = [start]
    parts = [start]
    cur = start
    hops = 0
    error = ""
    while True:
        status, loc = first_hop(cur)
        if status in (301, 308):
            nxt = urllib.parse.urljoin(cur, loc) if loc else ""
            parts += ["%d" % status, nxt or "(no Location)"]
            if not nxt:
                error = "%d redirect without a Location header" % status
                break
            if nxt in chain:
                error = "redirect loop (%s seen twice)" % nxt
                break
            hops += 1
            if hops > max_hops:
                error = "more than %d redirect hops" % max_hops
                break
            chain.append(nxt)
            cur = nxt
            continue
        if status in (302, 303, 307):
            parts += ["%d" % status, urllib.parse.urljoin(cur, loc) if loc else "(no Location)"]
            error = "temporary %d redirect instead of a permanent 301" % status
            break
        if status == 200:
            parts[-1] += " (200)"
            if hops == 0:
                error = "returns 200 without redirecting (duplicate host/protocol variant)"
            elif cur != canonical:
                error = "lands on %s instead of %s" % (cur, canonical)
            break
        parts += ["%s" % (status or loc or "no response")]
        error = "unexpected status %s" % (status or loc or "no response")
        break
    return {"start": start, "ok": not error, "chain": " -> ".join(parts), "error": error}


def canonical_checks(variants=None, first_hop=fetch_first_hop):
    rows, failures = [], []
    for v in variants or CANONICAL_VARIANTS:
        r = check_canonical_redirect(v, first_hop=first_hop)
        rows.append(("Canonical redirect " + v, r["chain"], r["ok"]))
        if not r["ok"]:
            failures.append("canonical redirect %s: %s [%s]" % (v, r["error"], r["chain"]))
    return rows, failures


# ------------------------------------------------------------------ SSL / TLS certificate check
def fetch_peer_cert(host, port=443, timeout=SSL_TIMEOUT):
    """Connect with full verification (chain + host name + validity period) and return getpeercert()."""
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as tls:
            return tls.getpeercert()


def _rdn(rdns, key):
    for rdn in rdns or ():
        for k, v in rdn:
            if k == key:
                return v
    return ""


def check_ssl(host, now=None, getcert=fetch_peer_cert, tries=2):
    """Inspect the TLS certificate of `host`:443.

    Returns a dict: host, ok, days_remaining (int, negative = expired, None if unknown), expires ('YYYY-MM-DD' UTC),
    issuer, error, line (one-line human summary). ok is False when the certificate is invalid, expired, unreachable
    or has fewer than SSL_MIN_DAYS days left. `now` (epoch seconds) and `getcert` exist so the logic is unit-testable.
    """
    now = time.time() if now is None else now
    res = {"host": host, "ok": False, "days_remaining": None, "expires": "", "issuer": "", "error": ""}
    cert, last = None, None
    for _ in range(tries):
        try:
            cert = getcert(host)
            break
        except ssl.SSLCertVerificationError as e:  # invalid / expired / wrong host / untrusted: no point retrying
            res["error"] = "certificate verification failed: %s" % (getattr(e, "verify_message", "") or "invalid certificate")
            break
        except ssl.SSLError as e:
            res["error"] = "TLS handshake failed: %s" % (getattr(e, "reason", "") or type(e).__name__)
            break
        except (OSError, socket.timeout) as e:  # network blip / timeout - retry
            last = e
    if cert is None and not res["error"]:
        res["error"] = "could not connect to %s:443 within %ds (%s)" % (host, SSL_TIMEOUT, type(last).__name__ if last else "no response")
    if cert is not None:
        try:
            exp = ssl.cert_time_to_seconds(cert["notAfter"])
            res["days_remaining"] = int(math.floor((exp - now) / 86400.0))
            res["expires"] = datetime.fromtimestamp(exp, timezone.utc).strftime("%Y-%m-%d")
            org, cn = _rdn(cert.get("issuer"), "organizationName"), _rdn(cert.get("issuer"), "commonName")
            res["issuer"] = ("%s (%s)" % (org, cn) if org and cn else org or cn or "unknown").replace("|", "/")
        except (KeyError, ValueError, TypeError):
            res["error"] = "certificate has no readable notAfter date"
    d = res["days_remaining"]
    if res["error"]:
        res["line"] = "🔒 SSL Certificate: INVALID for %s - %s" % (host, res["error"])
    elif d < 0:
        res["line"] = "🔒 SSL Certificate: EXPIRED for %s (expired %s, %d days ago)" % (host, res["expires"], -d)
    elif d < SSL_MIN_DAYS:
        res["line"] = "🔒 SSL Certificate: EXPIRING SOON for %s (expires %s, only %d days remaining, minimum %d)" % (
            host, res["expires"], d, SSL_MIN_DAYS)
    else:
        res["ok"] = True
        res["line"] = "🔒 SSL Certificate: Valid for %s (expires %s, %d days remaining)%s" % (
            host, res["expires"], d, " - renew soon" if d < SSL_WARN_DAYS else "")
    return res


def ssl_checks(hosts=None, now=None, getcert=fetch_peer_cert):
    """Run check_ssl for every host. Returns (rows, failures, results) in the same shape main() uses."""
    rows, failures, results = [], [], []
    for host in hosts or SSL_HOSTS:
        r = check_ssl(host, now=now, getcert=getcert)
        results.append(r)
        if r["days_remaining"] is not None and not r["error"]:
            val = "expires %s, %d days left, issuer %s" % (r["expires"], r["days_remaining"], r["issuer"])
        else:
            val = r["error"] or "unknown"
        rows.append(("SSL certificate " + host, val, r["ok"]))
        if not r["ok"]:
            failures.append(r["line"].replace("🔒 SSL Certificate: ", "SSL certificate: "))
    return rows, failures, results


def selftest():
    """Offline unit tests for the SSL threshold logic (no network)."""
    def ts(epoch):  # epoch -> OpenSSL notAfter text
        t = time.gmtime(epoch)
        mon = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][t.tm_mon - 1]
        return "%s %2d %02d:%02d:%02d %d GMT" % (mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec, t.tm_year)

    NOW = ssl.cert_time_to_seconds("Oct 21 01:00:00 2026 GMT")
    DAY = 86400
    issuer = ((("countryName", "US"),), (("organizationName", "Let's Encrypt"),), (("commonName", "R11"),))

    def cert_in(seconds):
        return lambda host: {"notAfter": ts(NOW + seconds), "issuer": issuer}

    def raising(exc):
        def f(host):
            raise exc
        return f

    # healthy certificate (45 days) -> ok, exact day count, issuer and date parsed
    r = check_ssl("www.colddirect.co.uk", now=NOW, getcert=cert_in(45 * DAY))
    assert r["ok"] and r["days_remaining"] == 45 and r["expires"] == "2026-12-05", r
    assert r["issuer"] == "Let's Encrypt (R11)", r["issuer"]
    assert r["line"] == "🔒 SSL Certificate: Valid for www.colddirect.co.uk (expires 2026-12-05, 45 days remaining)", r["line"]
    # 20 days: passes but flagged
    r = check_ssl("x", now=NOW, getcert=cert_in(20 * DAY))
    assert r["ok"] and r["days_remaining"] == 20 and "renew soon" in r["line"], r
    # threshold: exactly 14 days passes, 14 days minus one second fails (13 whole days)
    assert check_ssl("x", now=NOW, getcert=cert_in(14 * DAY))["ok"]
    r = check_ssl("x", now=NOW, getcert=cert_in(14 * DAY - 1))
    assert not r["ok"] and r["days_remaining"] == 13 and "EXPIRING SOON" in r["line"], r
    # expiring in 5 days -> fail
    r = check_ssl("x", now=NOW, getcert=cert_in(5 * DAY))
    assert not r["ok"] and r["days_remaining"] == 5, r
    # expired 2 days ago (cert still readable) -> fail, negative days
    r = check_ssl("x", now=NOW, getcert=cert_in(-2 * DAY))
    assert not r["ok"] and r["days_remaining"] == -2 and "EXPIRED" in r["line"] and "2 days ago" in r["line"], r
    # handshake rejected as expired / wrong host -> fail with the reason, no retry
    calls = []

    def verify_fail(host):
        calls.append(host)
        e = ssl.SSLCertVerificationError(1, "certificate verify failed")
        e.verify_message = "certificate has expired"
        raise e

    r = check_ssl("x", now=NOW, getcert=verify_fail)
    assert not r["ok"] and "certificate has expired" in r["error"] and "INVALID" in r["line"] and len(calls) == 1, r
    # unreachable host / timeout -> fail after one retry
    n = []

    def timeout(host):
        n.append(1)
        raise socket.timeout("timed out")

    r = check_ssl("x", now=NOW, getcert=timeout)
    assert not r["ok"] and "could not connect" in r["error"] and len(n) == 2, (r, n)
    # a blip on the first try is retried and succeeds
    state = {"n": 0}

    def flaky(host):
        state["n"] += 1
        if state["n"] == 1:
            raise OSError("reset")
        return {"notAfter": ts(NOW + 60 * DAY), "issuer": issuer}

    assert check_ssl("x", now=NOW, getcert=flaky)["ok"]
    # garbage / missing notAfter -> fail
    assert not check_ssl("x", now=NOW, getcert=lambda h: {})["ok"]
    assert not check_ssl("x", now=NOW, getcert=lambda h: {"notAfter": "garbage"})["ok"]
    # aggregate: both hosts healthy -> rows ok, no failures; one expiring -> exactly one failure naming the host
    rows, failures, results = ssl_checks(["a.example", "b.example"], now=NOW, getcert=cert_in(40 * DAY))
    assert len(rows) == 2 and all(ok for _, _, ok in rows) and not failures
    def mixed(host):
        return {"notAfter": ts(NOW + (3 if host == "b.example" else 90) * DAY), "issuer": issuer}
    rows, failures, results = ssl_checks(["a.example", "b.example"], now=NOW, getcert=mixed)
    assert [ok for _, _, ok in rows] == [True, False] and len(failures) == 1 and "b.example" in failures[0], failures
    # nothing secret-looking ever ends up in the text
    assert "BEGIN" not in str(results) and "private" not in str(results).lower()

    # ---------------- canonical host / protocol redirect logic (no network)
    def site(table):
        """fake first-hop fetcher: url -> (status, location)"""
        def f(url):
            return table[url]
        return f

    H, HW, SW, S = "http://colddirect.co.uk/", "http://www.colddirect.co.uk/", "https://colddirect.co.uk/", CANONICAL
    # direct 301 to canonical
    r = check_canonical_redirect(H, first_hop=site({H: (301, S), S: (200, "")}))
    assert r["ok"] and r["chain"] == "http://colddirect.co.uk/ -> 301 -> https://www.colddirect.co.uk/ (200)", r
    # 2-hop 301 chain (http apex -> https apex -> https www) and a 308 are fine
    r = check_canonical_redirect(H, first_hop=site({H: (301, SW), SW: (301, S), S: (200, "")}))
    assert r["ok"] and r["chain"] == ("http://colddirect.co.uk/ -> 301 -> https://colddirect.co.uk/ -> 301 -> "
                                      "https://www.colddirect.co.uk/ (200)"), r
    assert check_canonical_redirect(SW, first_hop=site({SW: (308, S), S: (200, "")}))["ok"]
    # relative Location header is resolved
    assert check_canonical_redirect(HW, first_hop=site({HW: (301, "https://www.colddirect.co.uk/"), S: (200, "")}))["ok"]
    # accidental 200 without redirect (duplicate host) -> FAIL
    r = check_canonical_redirect(SW, first_hop=site({SW: (200, "")}))
    assert not r["ok"] and "without redirecting" in r["error"], r
    # temporary 302 / 307 instead of 301 -> FAIL (also when it is the 2nd hop)
    r = check_canonical_redirect(H, first_hop=site({H: (302, S)}))
    assert not r["ok"] and "temporary 302" in r["error"], r
    r = check_canonical_redirect(H, first_hop=site({H: (301, SW), SW: (307, S)}))
    assert not r["ok"] and "temporary 307" in r["error"], r
    # redirect loop -> FAIL
    r = check_canonical_redirect(H, first_hop=site({H: (301, SW), SW: (301, H)}))
    assert not r["ok"] and "loop" in r["error"], r
    r = check_canonical_redirect(S, first_hop=site({S: (301, S)}))
    assert not r["ok"] and "loop" in r["error"], r
    # three hops -> FAIL (max 2)
    X = "https://colddirect.co.uk/x"
    r = check_canonical_redirect(H, first_hop=site({H: (301, SW), SW: (301, X), X: (301, S), S: (200, "")}))
    assert not r["ok"] and "more than 2" in r["error"], r
    # wrong landing page -> FAIL; error status / no response / missing Location -> FAIL
    r = check_canonical_redirect(H, first_hop=site({H: (301, "https://www.colddirect.co.uk/about-us/"),
                                                    "https://www.colddirect.co.uk/about-us/": (200, "")}))
    assert not r["ok"] and "lands on" in r["error"], r
    assert not check_canonical_redirect(H, first_hop=site({H: (301, S), S: (500, "")}))["ok"]
    assert not check_canonical_redirect(H, first_hop=site({H: (0, "ERR URLError")}))["ok"]
    assert not check_canonical_redirect(H, first_hop=site({H: (301, "")}))["ok"]
    # aggregate: all 3 healthy -> 3 ok rows; one bad variant -> exactly one failure naming it
    good = {H: (301, S), HW: (301, S), SW: (301, S), S: (200, "")}
    rows, failures = canonical_checks(first_hop=site(good))
    assert len(rows) == 3 and all(ok for _, _, ok in rows) and not failures, (rows, failures)
    bad = dict(good)
    bad[SW] = (200, "")
    rows, failures = canonical_checks(first_hop=site(bad))
    assert [ok for _, _, ok in rows] == [True, True, False] and len(failures) == 1 and SW in failures[0], failures

    # ---------------- robots.txt health (no network)
    LIVE = ("# One shared group: named crawlers must inherit the utility exclusions too.\n"
            "User-agent: *\nUser-agent: Googlebot\nUser-agent: Bingbot\nUser-agent: GPTBot\n"
            "Disallow: /agent-status.html\nDisallow: /agent-status/\nDisallow: /image-preview.html\n"
            "Disallow: /agent-status-full-report.txt\n\nSitemap: https://www.colddirect.co.uk/sitemap.xml\n")
    TXT = {"Content-Type": "text/plain"}
    SM = "\nSitemap: https://www.colddirect.co.uk/sitemap.xml\n"

    def rb(body, status=200, headers=TXT):
        return check_robots(status, headers, body)

    # healthy: the real live file (grouped User-agent lines), case-insensitive directive names, BOM, Allow override
    r = rb(LIVE)
    assert r["ok"] and r["summary"] == "HTTP 200, Googlebot allowed, Sitemap declared", r
    assert rb("USER-AGENT: *\nDISALLOW: /private/\nSITEMAP: https://www.colddirect.co.uk/sitemap.xml\n")["ok"]
    assert rb("\ufeffUser-agent: *\nDisallow:\n" + SM)["ok"]                      # empty Disallow = allow all
    assert rb("User-agent: *\nDisallow: /blog/\nAllow: /blog/\n" + SM)["ok"]    # Allow ties/wins
    # blanket Disallow: / for '*' -> fail
    r = rb("User-agent: *\nDisallow: /\n" + SM)
    assert not r["ok"] and "blanket" in r["summary"], r
    # Googlebot-specific blanket block (while '*' is open) -> fail
    r = rb("User-agent: *\nDisallow: /agent-status/\n\nUser-agent: Googlebot\nDisallow: /\n" + SM)
    assert not r["ok"] and "Googlebot" in r["summary"] and "blanket" in r["summary"], r
    # a Googlebot group REPLACES '*' for Googlebot: '*' blocks /blog/ but Googlebot's own group allows it -> '*' still fails
    r = rb("User-agent: *\nDisallow: /blog/\n\nUser-agent: Googlebot\nDisallow: /agent-status/\n" + SM)
    assert not r["ok"] and "/blog/ blocked for User-agent: *" in r["summary"] and "Googlebot" not in r["summary"], r
    # blocked /blog/ or any money page prefix (also via wildcard / partial prefix) -> fail
    for bad in ("Disallow: /blog/", "Disallow: /blog", "Disallow: /cold-room-repair-", "Disallow: /commercial-fridge-repair-",
                "Disallow: /fridge-repair-london/", "Disallow: /*repair-london", "Disallow: /freezer-repair-",
                "Disallow: /catering-repair-", "Disallow: /air-conditioning-repair-", "Disallow: /cellar-cooler-repair-"):
        r = rb("User-agent: *\n" + bad + "\n" + SM)
        assert not r["ok"] and "blocked" in r["summary"], (bad, r)
    # Sitemap missing / wrong URL / wrong host / http / trailing junk -> fail
    for sm in ("", "\nSitemap: https://www.colddirect.co.uk/sitemap-old.xml\n", "\nSitemap: http://www.colddirect.co.uk/sitemap.xml\n",
               "\nSitemap: https://colddirect.co.uk/sitemap.xml\n", "\nSitemap: https://www.colddirect.co.uk/sitemap.xml.gz\n"):
        r = rb("User-agent: *\nDisallow: /agent-status/\n" + sm)
        assert not r["ok"] and "missing 'Sitemap" in r["summary"], (sm, r)
    # HTML error pages / wrong status / empty / not robots -> fail
    html = "<!DOCTYPE html><html><head><title>404 - File or directory not found.</title></head><body>Not found</body></html>"
    assert not rb(html, 404, {"Content-Type": "text/html"})["ok"]
    assert not rb(html, 500, {"Content-Type": "text/html"})["ok"]
    r = rb(html, 200, {"Content-Type": "text/html"})                              # soft-404: 200 + HTML body
    assert not r["ok"] and "HTML" in r["summary"], r
    assert not rb(html, 200, TXT)["ok"]                                           # HTML body even with a text content-type
    assert not rb("", 200)["ok"] and not rb("   \n", 200)["ok"]
    assert not rb("hello world", 200)["ok"]
    assert not check_robots(0, {}, "ERR URLError")["ok"]
    # glue: row + failure message shape
    row, fails = robots_check(lambda: (200, TXT, LIVE))
    assert row == ("🤖 robots.txt", "HTTP 200, Googlebot allowed, Sitemap declared", True) and not fails
    row, fails = robots_check(lambda: (200, TXT, "User-agent: *\nDisallow: /\n" + SM))
    assert row[2] is False and fails and fails[0].startswith("robots.txt: "), (row, fails)

    # ---------------- live HTML content integrity (no network)
    P = "/cold-room-repair-london/"
    GOOD = ('<!DOCTYPE html><html><head><title>Cold Room Repair London | Cold Direct</title>'
            '<meta name="robots" content="index, follow, max-image-preview:large">'
            '<link rel="canonical" href="https://www.colddirect.co.uk/cold-room-repair-london/">'
            '<script type="application/ld+json">{"@context":"https://schema.org","@type":"HVACBusiness",'
            '"telephone":"+447983759320"}</script></head><body><h1>Cold Room Repair London</h1>'
            '<a href="tel:+447983759320">07983 759320</a></body></html>')
    HDR = {"Content-Type": "text/html"}

    def pg(body=GOOD, path=P, status=200, headers=HDR):
        return check_page_integrity(path, status, headers, body)

    r = pg()
    assert r["ok"] and r["summary"] == "HTTP 200 + Schema + Canonical + Phone OK" and not r["problems"], r
    # homepage canonical is the bare host with a slash; phone in every accepted spelling
    home = GOOD.replace("cold-room-repair-london/\">", "\">", 1)
    assert pg(home, path="/")["ok"]
    for ph in ("07983 759320", "07983759320", "+447983759320", "+44 7983 759320", "07983 759 320"):
        assert pg(GOOD.replace("tel:+447983759320", "tel:x").replace("07983 759320", ph).replace(
            '"+447983759320"', '"x"'))["ok"], ph
    # commented-out noindex / bad markup is ignored
    assert pg(GOOD.replace("<body>", '<body><!-- <meta name="robots" content="noindex"> -->'))["ok"]
    # noindex: meta robots / googlebot (any attribute order, case), 'none', header
    for meta in ('<meta name="robots" content="noindex, follow">', '<meta content="NOINDEX" name="robots">',
                 "<meta name='googlebot' content='index,noindex'>", '<meta name="robots" content="none">'):
        r = pg(GOOD.replace("<link ", meta + "<link ", 1))
        assert not r["ok"] and "noindex" in r["summary"], (meta, r)
    r = pg(headers={"X-Robots-Tag": "noindex, nofollow"})
    assert not r["ok"] and "X-Robots-Tag" in r["summary"], r
    assert pg(headers={"x-robots-tag": "all"})["ok"]
    # canonical: missing / wrong page / non-www / http / no trailing slash / empty / conflicting
    r = pg(GOOD.replace('<link rel="canonical" href="https://www.colddirect.co.uk/cold-room-repair-london/">', ""))
    assert not r["ok"] and "canonical missing" in r["summary"], r
    for wrong in ("https://www.colddirect.co.uk/fridge-repair-london/", "https://colddirect.co.uk/cold-room-repair-london/",
                  "http://www.colddirect.co.uk/cold-room-repair-london/", "https://www.colddirect.co.uk/cold-room-repair-london",
                  "https://www.colddirect.co.uk/cold-room-repair-london.html", ""):
        r = pg(GOOD.replace("https://www.colddirect.co.uk/cold-room-repair-london/\"><script", wrong + "\"><script"))
        assert not r["ok"] and "canonical mismatch" in r["summary"], (wrong, r)
    r = pg(GOOD.replace("<script", '<link rel="canonical" href="https://www.colddirect.co.uk/">\n<script', 1))
    assert not r["ok"] and "conflicting" in r["summary"], r
    assert not pg(GOOD, path="/")["ok"]                                       # page canonical on the wrong URL
    # title / h1 missing or empty
    assert "<title> missing" in pg(re.sub(r"<title>.*?</title>", "", GOOD))["summary"]
    assert "<title> empty" in pg(GOOD.replace("Cold Room Repair London | Cold Direct", " "))["summary"]
    assert "<h1> missing" in pg(re.sub(r"<h1>.*?</h1>", "", GOOD))["summary"]
    assert "<h1> empty" in pg(GOOD.replace("<h1>Cold Room Repair London</h1>", "<h1> <span></span> </h1>"))["summary"]
    # JSON-LD: missing, trailing comma, unquoted key, truncated, one good + one bad block
    r = pg(re.sub(r"<script.*?</script>", "", GOOD))
    assert not r["ok"] and "JSON-LD schema missing" in r["summary"], r
    for broken in ('{"@type":"HVACBusiness",}', '{@type: "HVACBusiness"}', '{"@type":"HVACBusiness"', ""):
        r = pg(GOOD.replace('{"@context":"https://schema.org","@type":"HVACBusiness",'
                            '"telephone":"+447983759320"}', broken))
        assert not r["ok"] and "JSON-LD block 1 invalid" in r["summary"], (broken, r)
    r = pg(GOOD.replace("</head>", '<script type="application/ld+json">{"a":}</script></head>'))
    assert not r["ok"] and "JSON-LD block 2 invalid" in r["summary"], r
    assert pg(GOOD.replace("</head>", '<script>var x = 1;</script></head>'))["ok"]   # non-LD scripts ignored
    # phone: missing entirely, another number, dummy 123 4567 / 1234567 (also next to the real one)
    nophone = GOOD.replace("tel:+447983759320", "tel:x").replace("07983 759320", "call us").replace(
        '"+447983759320"', '"x"')
    r = pg(nophone)
    assert not r["ok"] and "phone 07983 759320 missing" in r["summary"], r
    assert not pg(nophone.replace("call us", "07123 456789"))["ok"]
    for dummy in ("020 123 4567", "0201234567", "123-4567", "tel:+441234567"):
        r = pg(GOOD.replace("</body>", dummy + "</body>"))
        assert not r["ok"] and "dummy phone" in r["summary"], (dummy, r)
        r = pg(nophone.replace("call us", dummy))
        assert not r["ok"] and "missing" in r["summary"] and "dummy" in r["summary"], r
    # non-200 -> fail with the status; network error -> fail
    assert pg(status=404)["summary"] == "HTTP 404" and not pg(status=500)["ok"] and not pg("", status=0)["ok"]
    # several problems are all reported
    r = pg(nophone.replace('<meta name="robots"', '<meta name="robots" content="noindex"><meta name="x"'))
    assert len(r["problems"]) >= 2, r
    # aggregate: all good -> rows named "HTTP 200 <path>"; one bad page -> exactly one failure naming it
    def fake(bad=None):
        def f(path):
            body = GOOD.replace("cold-room-repair-london/", path.strip("/") + "/") if path != "/" else home
            if path == bad:
                body = body.replace('content="index, follow, max-image-preview:large"', 'content="noindex"')
            return 200, HDR, body
        return f
    lat = []
    rows, failures = integrity_checks(fetcher=fake(), latencies=lat)
    assert len(rows) == len(INTEGRITY_PAGES) == 11 and all(ok for _, _, ok in rows) and not failures, (rows, failures)
    assert rows[0][0] == "HTTP 200 /" and all(v.startswith(INTEGRITY_OK + " (") and v.endswith(" ms)") for _, v, _ in rows), rows
    assert len(lat) == 11
    rows, failures = integrity_checks(fetcher=fake("/fridge-repair-london/"))
    assert sum(1 for *_, ok in rows if not ok) == 1 and len(failures) == 1, failures
    assert failures[0].startswith("/fridge-repair-london/ content integrity: noindex"), failures

    # ---------------- response-time thresholds (fake monotonic clock, no network)
    def fake_clock(durations_ms):
        """clock() pairs: every timed call reads the clock twice; the Nth call 'takes' durations_ms[N]."""
        ticks = []
        now = 1000.0
        for d in durations_ms:
            ticks += [now, now + d / 1000.0]
            now += 100.0
        it = iter(ticks)
        return lambda: next(it)

    calls = []

    def probe(fn=lambda: (200, {}, "x")):
        def f():
            calls.append(1)
            return fn()
        return f

    # fast (<1.5 s): PASS, single request, plain "(245 ms)" note
    calls.clear()
    t = timed_fetch(probe(), fake_clock([245]))
    assert t["ms"] == 245 and t["level"] == "ok" and t["first_ms"] is None and len(calls) == 1, t
    assert latency_note(t) == " (245 ms)", latency_note(t)
    fl = []
    row = with_latency(("HTTP 200 /", INTEGRITY_OK, True), t, fl, "/")
    assert row == ("HTTP 200 /", "HTTP 200 + Schema + Canonical + Phone OK (245 ms)", True) and not fl, (row, fl)
    # boundaries: 1499 ms ok, 1500 ms slow, 3000 ms slow (not a failure), 3001 ms -> retry
    assert timed_fetch(probe(), fake_clock([1499]))["level"] == "ok"
    assert timed_fetch(probe(), fake_clock([1500]))["level"] == "slow"
    calls.clear()
    t = timed_fetch(probe(), fake_clock([3000]))
    assert t["level"] == "slow" and len(calls) == 1, t                       # exactly 3.0 s is still only a warning
    # slow warning (1.5-3 s): PASS (row ok, no failure) with the SLOW marker, no retry
    calls.clear()
    t = timed_fetch(probe(), fake_clock([1800]))
    assert t["ms"] == 1800 and t["level"] == "slow" and len(calls) == 1, t
    assert latency_note(t) == " (1800 ms ⚠️ SLOW)", latency_note(t)
    fl = []
    row = with_latency(("HTTP 200 /x/", "200", True), t, fl, "/x/")
    assert row[2] is True and "⚠️ SLOW" in row[1] and not fl, (row, fl)
    # transient spike (>3 s then <1.5 s): retried once, PASS, spike noted
    calls.clear()
    t = timed_fetch(probe(), fake_clock([3400, 480]))
    assert t["ms"] == 480 and t["first_ms"] == 3400 and t["level"] == "ok" and len(calls) == 2, t
    assert latency_note(t) == " (480 ms after a transient 3400 ms spike, retried)", latency_note(t)
    fl = []
    row = with_latency(("HTTP 200 /x/", "200", True), t, fl, "/x/")
    assert row[2] is True and not fl, (row, fl)
    # spike then a slow-warning retry: still PASS
    t = timed_fetch(probe(), fake_clock([5000, 2000]))
    assert t["level"] == "slow" and "⚠️ SLOW" in latency_note(t) and t["first_ms"] == 5000, t
    # persistent slow (>3 s on both attempts): retried exactly once, FAIL with failure message
    calls.clear()
    t = timed_fetch(probe(), fake_clock([3500, 3300]))
    assert t["ms"] == 3300 and t["first_ms"] == 3500 and t["level"] == "fail" and len(calls) == 2, t
    assert "TOO SLOW" in latency_note(t) and "3500" in latency_note(t), latency_note(t)
    fl = []
    row = with_latency(("HTTP 200 /x/", "200", True), t, fl, "/x/")
    assert row[2] is False and len(fl) == 1 and fl[0].startswith("/x/ response time 3300 ms"), (row, fl)
    # a slow page with a healthy-looking body is not retried more than once (3 calls would be a bug)
    calls.clear()
    timed_fetch(probe(), fake_clock([9000, 9000]))
    assert len(calls) == 2
    # integration: one persistently slow core page fails the aggregate (and only that page); a spike on another passes
    seq = {"/": [200], "/cold-room-repair-london/": [3600, 3200], "/fridge-repair-london/": [4000, 400]}
    clock_durations = []
    for p in INTEGRITY_PAGES:
        clock_durations += seq.get(p, [150])
    lat = []
    rows, failures = integrity_checks(fetcher=fake(), latencies=lat, clock=fake_clock(clock_durations))
    bad = [n for n, _, ok in rows if not ok]
    assert bad == ["HTTP 200 /cold-room-repair-london/"], bad
    assert len(failures) == 1 and failures[0].startswith("/cold-room-repair-london/ response time 3200 ms"), failures
    assert len(lat) == 11 and 3200 in lat and 400 in lat and 4000 not in lat, lat
    # the integrity failure and the latency failure are both reported when a slow page is also broken
    rows, failures = integrity_checks(fetcher=fake("/"), latencies=[], clock=fake_clock([3500, 3500] + [100] * 10))
    assert len(failures) == 2 and "response time" in failures[0] and "content integrity" in failures[1], failures
    # summary metric
    assert latency_summary([200, 400, 3000]) == "average 1200 ms, max 3000 ms (3 requests)", latency_summary([200, 400, 3000])
    assert latency_summary([]) == "n/a"

    # ---------------- critical static assets of the homepage (no network)
    HOME_HTML = (
        '<html><head><link rel="icon" href="/favicon.ico">'
        '<link rel="apple-touch-icon" href="/images/logo/favicon-512.png">'
        '<link rel="canonical" href="https://www.colddirect.co.uk/">'
        '<meta property="og:image" content="https://www.colddirect.co.uk/images/og.jpg">'
        '<link rel="stylesheet" href="/css/styles.css?v=1"><link rel="stylesheet" href="/css/styles.css?v=1">'
        '<link rel="stylesheet" href="https://www.colddirect.co.uk/css/pro.css">'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter">'
        '<link rel="stylesheet" href="//cdn.example.net/x.css">'
        '<script async src="https://analytics.ahrefs.com/analytics.js" data-key="k"></script>'
        '<script src="https://www.googletagmanager.com/gtag/js?id=G-1"></script>'
        '<script src="https://cdn.jsdelivr.net/npm/x.js"></script><script>var inline=1;</script>'
        '<script src="/js/main.js"></script><script defer src="/assets/slider.js?v=2"></script>'
        '<script src="data:text/javascript,1"></script></head><body>'
        '<!-- <link rel="stylesheet" href="/css/commented-out.css"> -->'
        '<img src="/images/logo.jpg" alt="logo"><img src="/images/hero.webp" alt="hero">'
        '<img src="https://www.colddirect.co.uk/images/third.webp"><img src="/images/fourth-ignored.webp">'
        '<img src="https://img.thirdparty.com/pixel.png"></body></html>')
    EXPECT = [("css", "https://www.colddirect.co.uk/css/styles.css?v=1"), ("css", "https://www.colddirect.co.uk/css/pro.css"),
              ("js", "https://www.colddirect.co.uk/js/main.js"), ("js", "https://www.colddirect.co.uk/assets/slider.js?v=2"),
              ("icon", "https://www.colddirect.co.uk/favicon.ico"),
              ("icon", "https://www.colddirect.co.uk/images/logo/favicon-512.png"),
              ("icon", "https://www.colddirect.co.uk/images/og.jpg"),
              ("img", "https://www.colddirect.co.uk/images/logo.jpg"), ("img", "https://www.colddirect.co.uk/images/hero.webp"),
              ("img", "https://www.colddirect.co.uk/images/third.webp")]
    got = extract_assets(HOME_HTML)
    assert got == EXPECT, got                      # order, dedupe (styles.css once), external/data/commented/4th img ignored
    assert not any("google" in u or "ahrefs" in u or "jsdelivr" in u or "cdn.example" in u or "thirdparty" in u
                   or "commented-out" in u or "fourth" in u for _, u in got)
    # cap: 30 distinct stylesheets -> at most ASSET_MAX assets
    many = "".join('<link rel="stylesheet" href="/c%d.css">' % i for i in range(30))
    assert len(extract_assets(many)) == ASSET_MAX == 14
    # root-relative, absolute and protocol-relative same-origin forms all resolve; apex host / http host are external here
    fm = extract_assets('<script src="//www.colddirect.co.uk/a.js"></script><script src="http://www.colddirect.co.uk/b.js"></script>'
                        '<script src="https://colddirect.co.uk/c.js"></script><script src="rel/d.js"></script>')
    assert [u for _, u in fm] == ["https://www.colddirect.co.uk/a.js", "https://www.colddirect.co.uk/b.js",
                                  "https://www.colddirect.co.uk/rel/d.js"], fm
    assert extract_assets("") == [] and extract_assets("<html></html>") == []

    CSS, JS, PNG = b"body{margin:0}", b"console.log(1);", b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
    SOFT404 = b"<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0//EN\"><html><head><title>404 - File or directory not found.</title>"

    def good_fetcher(overrides=None):
        ov = overrides or {}

        def f(url):
            if url in ov:
                return ov[url]
            if url.split("?")[0].endswith(".css"):
                return 200, {"Content-Type": "text/css"}, CSS
            if url.split("?")[0].endswith(".js"):
                return 200, {"Content-Type": "application/javascript"}, JS
            return 200, {"Content-Type": "image/png"}, PNG
        return f

    # healthy: 10/10 with the exact summary wording and no failures
    row, fails = asset_checks(HOME_HTML, good_fetcher())
    assert row == (ASSET_ROW, "10/10 core CSS/JS/Image assets HTTP 200 & non-empty (2 CSS, 2 JS, 3 icon, 3 image)", True), row
    assert fails == []
    # 404 broken stylesheet -> fail naming the URL
    U = "https://www.colddirect.co.uk/css/pro.css"
    row, fails = asset_checks(HOME_HTML, good_fetcher({U: (404, {}, b"")}))
    assert row[2] is False and "9/10 healthy" in row[1] and "/css/pro.css -> HTTP 404" in row[1], row
    assert fails == ["Static asset %s: HTTP 404" % U], fails
    # 0-byte JavaScript -> fail; 500 on an image -> fail; network error (0) -> fail
    U = "https://www.colddirect.co.uk/js/main.js"
    row, fails = asset_checks(HOME_HTML, good_fetcher({U: (200, {"Content-Type": "application/javascript"}, b"")}))
    assert not row[2] and fails == ["Static asset %s: empty (0 bytes)" % U], (row, fails)
    U = "https://www.colddirect.co.uk/images/hero.webp"
    assert not asset_checks(HOME_HTML, good_fetcher({U: (500, {}, b"")}))[0][2]
    assert not asset_checks(HOME_HTML, good_fetcher({U: (0, {}, b"")}))[0][2]
    # soft-404: HTML served with 200 for a .css, .js and an image (by body sniff AND by Content-Type)
    for u in ("https://www.colddirect.co.uk/css/styles.css?v=1", "https://www.colddirect.co.uk/assets/slider.js?v=2",
              "https://www.colddirect.co.uk/images/logo.jpg", "https://www.colddirect.co.uk/favicon.ico"):
        row, fails = asset_checks(HOME_HTML, good_fetcher({u: (200, {"Content-Type": "text/plain"}, SOFT404)}))
        assert not row[2] and len(fails) == 1 and "soft-404" in fails[0] and u in fails[0], (u, row, fails)
        row, fails = asset_checks(HOME_HTML, good_fetcher({u: (200, {"Content-Type": "text/html; charset=utf-8"}, CSS)}))
        assert not row[2] and "soft-404" in fails[0], (u, fails)
    assert looks_like_html({}, b"\xef\xbb\xbf  \n<!DOCTYPE html><html>") and looks_like_html({}, b"<HTML><body>")
    assert not looks_like_html({"Content-Type": "text/css"}, b"/* <html> in a comment */ a{}")
    assert not looks_like_html({"Content-Type": "application/javascript"}, b"var t='<html>';")
    # several broken assets are all listed; external third-party assets are never fetched
    fetched = []

    def spy(url):
        fetched.append(url)
        return good_fetcher({"https://www.colddirect.co.uk/css/pro.css": (404, {}, b""),
                             "https://www.colddirect.co.uk/images/og.jpg": (200, {"Content-Type": "image/jpeg"}, b"")})(url)

    row, fails = asset_checks(HOME_HTML, spy)
    assert len(fails) == 2 and "8/10 healthy" in row[1] and "og.jpg -> empty" in row[1], (row, fails)
    assert len(fetched) == 10 and all(u.startswith("https://www.colddirect.co.uk/") for u in fetched), fetched
    # no extractable assets (e.g. homepage fetch failed) -> fail instead of a vacuous pass
    row, fails = asset_checks("")
    assert not row[2] and "no same-origin" in row[1] and fails, (row, fails)
    # kind-specific wording
    assert "JavaScript" in check_asset("js", "u", lambda u: (200, {}, SOFT404))
    assert "CSS" in check_asset("css", "u", lambda u: (200, {}, SOFT404))
    assert "an image" in check_asset("img", "u", lambda u: (200, {}, SOFT404))
    assert check_asset("css", "u", lambda u: (200, {"Content-Type": "text/css"}, CSS)) is None
    # integrity_checks hands the homepage HTML to the asset check
    bd = {}
    integrity_checks(paths=["/"], fetcher=lambda p: (200, HDR, home), bodies=bd)
    assert bd == {"/": home}

    # spoken SEO audio: shared scenarios (10/10 ID3 valid, missing <audio>, mismatched contentUrl, 404, truncated,
    # HTML soft-404, ...) + the live_smoke_test wrapper / row shape
    import seo_integrity_check as sic
    import generate_seo_audio as ga
    assert AUDIO_ROW == sic.AUDIO_ROW
    n_audio = sic.audio_selftest()
    a_bodies = {}
    for a_path, a_stem in sic.audio_targets():
        a_slug = a_path.strip("/")
        a_name, a_script = {s: (n, sc) for s, _, n, sc in ga.md.audio_pages()}[a_slug]
        a_bodies[a_path] = ga.inject("<html><body><h1>H</h1><footer></footer></body></html>",
                                     ga.audio_block(a_slug, a_stem, a_name, a_script, 27.0))
    mp3_ok = (200, {"Content-Type": "audio/mpeg", "Content-Length": "20000"}, sic._fake_mp3())
    row, fails = audio_checks(a_bodies, lambda u: mp3_ok)
    assert row == (AUDIO_ROW, "10/10 MP3 audio summaries HTTP 200, audio/mpeg & AudioObject schema intact", True) and fails == [], row
    soft = (200, {"Content-Type": "text/html"}, b"<!DOCTYPE html><html><body>" + b"x" * 20000 + b"</body></html>")
    row, fails = audio_checks(a_bodies, lambda u: soft if u.endswith("/cold-room-repair-london.mp3") else mp3_ok)
    assert not row[2] and row[1].startswith("9/10 healthy, FAILING: /cold-room-repair-london/") and len(fails) == 1 and fails[0].startswith("SEO audio:"), row
    row, fails = audio_checks({}, lambda u: mp3_ok)       # no page HTML fetched -> fail, never a vacuous pass
    assert not row[2] and len(fails) == 10, (row, fails)
    miss = dict(a_bodies)
    miss["/"] = ""
    row, fails = audio_checks(miss, lambda u: mp3_ok)
    assert not row[2] and "page not fetched" in row[1], row

    print("selftest OK (SEO audio assets: %d scenarios incl. 10/10 ID3 valid, missing <audio>, mismatched AudioObject contentUrl, "
          "HTTP 404, truncated <10 KB, HTML soft-404; static assets: css/js/img extraction + 200 ok; 404 / 0-byte / soft-404 HTML / external ignored; "
          "page integrity: valid page ok; noindex / canonical / title / h1 / JSON-LD / phone / dummy-phone fail; "
          "latency: <1.5 s ok, 1.5-3 s slow warning, >3 s retried once, spike passes, persistent fails; "
          "SSL threshold: fail below %d days, expired/invalid certificates; "
          "canonical redirects: 301 / 2-hop ok, 200 / 302 / 307 / loop / 3 hops / wrong target fail; "
          "robots.txt: healthy ok, blanket / Googlebot / money-path blocks, bad Sitemap, HTML 404/500 fail)" % (n_audio, SSL_MIN_DAYS))
    return 0


def run_all_checks():
    """Run every live (read-only, GET-only) check once. Returns a dict:
    rows [(name, value, ok)], failures [str], latencies [ms], urls [sitemap <loc>], ssl_results [dict],
    bodies {path: html}. Used by main() and by the read-only dashboard tools/site_status.py."""
    rows, failures = [], []
    latencies = []                          # response time (ms) of every timed core request

    for path in PAGES:
        if path in INTEGRITY_PAGES:
            continue                        # validated below with the full content integrity checks
        t = timed_fetch(lambda: fetch(path))
        code = t["result"][0]
        latencies.append(t["ms"])
        ok = code == 200
        rows.append(with_latency(("HTTP 200 " + path, "200" if ok else str(code), ok), t, failures, path))
        if not ok:
            failures.append("%s returned %s" % (path, code))

    bodies = {}
    page_rows, page_failures = integrity_checks(latencies=latencies, bodies=bodies)
    rows += page_rows
    failures += page_failures

    asset_row, asset_failures = asset_checks(bodies.get("/", ""))     # reuses the already-fetched homepage HTML
    rows.append(asset_row)
    failures += asset_failures

    audio_row, audio_failures = audio_checks(bodies)                  # homepage + 9 money pages: <audio>, schema, MP3 files
    rows.append(audio_row)
    failures += audio_failures

    t = timed_fetch(lambda: fetch("/sitemap.xml", body=True))
    code, _, sm = t["result"]
    latencies.append(t["ms"])
    urls = re.findall(r"<loc>\s*(.*?)\s*</loc>", sm) if code == 200 else []
    ok = code == 200 and len(urls) > 0
    rows.append(with_latency(("HTTP 200 /sitemap.xml (%d URLs)" % len(urls), str(code), ok), t, failures, "/sitemap.xml"))
    if not ok:
        failures.append("sitemap.xml returned %s with %d urls" % (code, len(urls)))
    for u in MUST_BE_IN_SITEMAP:
        ok = u in urls
        rows.append(("sitemap contains " + u.replace(BASE, ""), "yes" if ok else "MISSING", ok))
        if not ok:
            failures.append("sitemap is missing " + u)
    for u in MUST_NOT_BE_IN_SITEMAP:
        ok = u not in urls
        rows.append(("sitemap excludes " + u.replace(BASE, ""), "absent" if ok else "PRESENT", ok))
        if not ok:
            failures.append("sitemap wrongly contains " + u)

    for src, dst in REDIRECTS:
        code, headers, _ = fetch(src)
        loc = {k.lower(): v for k, v in headers.items()}.get("location", "")
        ok = code == 301 and loc.rstrip("/").endswith(dst.rstrip("/"))
        rows.append(("301 %s -> %s" % (src, dst), "%s %s" % (code, loc.replace(BASE, "") or "-"), ok))
        if not ok:
            failures.append("%s expected 301 to %s, got %s %s" % (src, dst, code, loc))

    t = timed_fetch(lambda: fetch("/robots.txt", body=True))
    latencies.append(t["ms"])
    robots_row, robots_failures = robots_check(lambda: t["result"])
    rows.append(with_latency(robots_row, t, failures, "/robots.txt"))
    failures += robots_failures

    host_rows, host_failures = canonical_checks()
    rows += host_rows
    failures += host_failures

    ssl_rows, ssl_failures, ssl_results = ssl_checks()
    rows += ssl_rows
    failures += ssl_failures
    return {"rows": rows, "failures": failures, "latencies": latencies, "urls": urls,
            "ssl_results": ssl_results, "bodies": bodies}


def main():
    if "--selftest" in sys.argv:
        return selftest()
    try:  # console may be cp1252 on Windows; the summary lines contain an emoji
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    attempt, max_attempts = 1, 1
    if "--attempt" in sys.argv:
        attempt = int(sys.argv[sys.argv.index("--attempt") + 1])
    if "--max-attempts" in sys.argv:
        max_attempts = int(sys.argv[sys.argv.index("--max-attempts") + 1])

    res = run_all_checks()
    rows, failures, latencies = res["rows"], res["failures"], res["latencies"]
    urls, ssl_results = res["urls"], res["ssl_results"]

    passed = not failures
    for name, val, ok in rows:
        print(("PASS " if ok else "FAIL ") + name + "  [" + val + "]")
    for r in ssl_results:
        print(r["line"])
    print("response times: " + latency_summary(latencies))
    print("live sitemap URL count: %d | attempt %d/%d | %s" % (len(urls), attempt, max_attempts, "ALL PASSED" if passed else "FAILURES: " + "; ".join(failures)))

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary and (passed or attempt >= max_attempts):
        resp = (os.environ.get("AUTO_SEO_RESPONSE") or "").strip()[:200]
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## Post-deploy live check %s\n\n" % ("PASSED" if passed else "FAILED"))
            f.write("- **Live sitemap URLs:** %d\n- **Attempt:** %d of %d\n" % (len(urls), attempt, max_attempts))
            f.write("- **⏱️ Response time:** %s (healthy < %d ms, slow warning %d-%d ms, fail > %d ms after one retry)\n"
                    % (latency_summary(latencies), LAT_SLOW_MS, LAT_SLOW_MS, LAT_FAIL_MS, LAT_FAIL_MS))
            if resp:
                f.write("- **auto-seo.aspx:** `%s`\n" % resp.replace("`", "'"))
            for r in ssl_results:
                f.write("- %s" % r["line"] + (" (issuer: %s)" % r["issuer"] if r["issuer"] else "") + "\n")
            f.write("\n| Check | Result | Status |\n|---|---|---|\n")
            for name, val, ok in rows:
                f.write("| %s | %s | %s |\n" % (name.replace("|", "/"), val.replace("|", "/"), "PASS" if ok else "**FAIL**"))
            if failures:
                f.write("\n**Failures:**\n" + "".join("- %s\n" % x for x in failures))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
