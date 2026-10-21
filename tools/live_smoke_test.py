#!/usr/bin/env python3
"""Live smoke test for https://www.colddirect.co.uk - run in GitHub Actions after every deploy.

Checks (all against the LIVE site, no redirects followed for the 200 checks):
  * HTTP 200 on the homepage, the 9 core money pages, /commercial-fridge-repair-enfield/ and /blog/
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

    print("selftest OK (SSL threshold: fail below %d days, expired/invalid certificates; "
          "canonical redirects: 301 / 2-hop ok, 200 / 302 / 307 / loop / 3 hops / wrong target fail; "
          "robots.txt: healthy ok, blanket / Googlebot / money-path blocks, bad Sitemap, HTML 404/500 fail)" % SSL_MIN_DAYS)
    return 0


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

    rows, failures = [], []

    for path in PAGES:
        code, _, _ = fetch(path)
        ok = code == 200
        rows.append(("HTTP 200 " + path, "200" if ok else str(code), ok))
        if not ok:
            failures.append("%s returned %s" % (path, code))

    code, _, sm = fetch("/sitemap.xml", body=True)
    urls = re.findall(r"<loc>\s*(.*?)\s*</loc>", sm) if code == 200 else []
    ok = code == 200 and len(urls) > 0
    rows.append(("HTTP 200 /sitemap.xml (%d URLs)" % len(urls), str(code), ok))
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

    robots_row, robots_failures = robots_check()
    rows.append(robots_row)
    failures += robots_failures

    host_rows, host_failures = canonical_checks()
    rows += host_rows
    failures += host_failures

    ssl_rows, ssl_failures, ssl_results = ssl_checks()
    rows += ssl_rows
    failures += ssl_failures

    passed = not failures
    for name, val, ok in rows:
        print(("PASS " if ok else "FAIL ") + name + "  [" + val + "]")
    for r in ssl_results:
        print(r["line"])
    print("live sitemap URL count: %d | attempt %d/%d | %s" % (len(urls), attempt, max_attempts, "ALL PASSED" if passed else "FAILURES: " + "; ".join(failures)))

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary and (passed or attempt >= max_attempts):
        resp = (os.environ.get("AUTO_SEO_RESPONSE") or "").strip()[:200]
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## Post-deploy live check %s\n\n" % ("PASSED" if passed else "FAILED"))
            f.write("- **Live sitemap URLs:** %d\n- **Attempt:** %d of %d\n" % (len(urls), attempt, max_attempts))
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
