#!/usr/bin/env python3
"""Live smoke test for https://www.colddirect.co.uk - run in GitHub Actions after every deploy.

Checks (all against the LIVE site, no redirects followed for the 200 checks):
  * HTTP 200 on the homepage, the 9 core money pages, /commercial-fridge-repair-enfield/ and /blog/
  * sitemap.xml is HTTP 200, contains /blog/ and /commercial-fridge-repair-enfield/, and does NOT contain
    /about/, /news/, /preview-colddirect-homepage/, /refrigeration-brands-repairs-london/
  * the 301s from web.config: /about/ -> /about-us/ and /refrigeration-brands-repairs-london/ -> /refrigeration-brands-repair-london/
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
    print("selftest OK (SSL threshold: fail below %d days, expired and invalid certificates)" % SSL_MIN_DAYS)
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
