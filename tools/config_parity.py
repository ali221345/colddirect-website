#!/usr/bin/env python3
"""Offline .htaccess <-> web.config parity audit for Cold Direct (Microsoft-IIS/10.0 on Plesk).

  python tools/config_parity.py              offline audit: every .htaccess 301 / serve rule must be enforced by web.config ALONE
  python tools/config_parity.py --live       also probe https://www.colddirect.co.uk (no redirect following) + header checks
  python tools/config_parity.py --generate   rewrite the GENERATED rewrite-map block of web.config from .htaccess
  python tools/config_parity.py --selftest

Why: the live host (IIS) also runs an Apache-syntax .htaccess engine (Helicon-style, X-REWRITE-URL header). That layer
hid every gap in web.config. The contract is that web.config must give the SAME answers without it.

How it works (no network needed for the default audit)
  * .htaccess: every RewriteRule / RedirectMatch is parsed; each finite regex is ENUMERATED into the concrete URLs it
    matches (sre_parse; "^fridge-repairs-london(/|\\.html|\\.asp)?$" -> 4 URLs). Open-ended generic rules (.html -> /slug/)
    are exercised on the real file tree. The FIRST matching .htaccess rule decides the expectation (Apache order):
    301 -> target, "-" pass-through / internal rewrite -> served (200).
  * web.config: a small IIS URL Rewrite simulator (ordered rules, conditions incl. IsFile / IsDirectory / rewrite maps,
    {R:n} / {C:n}, Redirect / Rewrite / None, stopProcessing, default document, directory-slash redirect) runs on the repo
    tree as document root.
  * A URL is in parity when the simulator answers EXACTLY what .htaccess expects: ONE hop 301 to the final canonical
    https://www.colddirect.co.uk/... URL which itself answers 200 (an .htaccess target that redirects again is resolved to
    its end; 2 hops or a dead target are failures).
"""
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import re._parser as sre_parse  # Python >= 3.11
except ImportError:  # pragma: no cover
    import sre_parse  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://www.colddirect.co.uk"
GEN_BEGIN = "<!-- BEGIN GENERATED htaccess-parity (rebuild with: python tools/config_parity.py -g) -->"
GEN_END = "<!-- END GENERATED htaccess-parity -->"
MAP_NAME = "HtaccessParity"
MAX_VARIANTS = 64
SKIP_DIRS = {".git", ".github", ".vscode", ".cursor", "node_modules", "colddirect-public-html", "public", "docs", "logs", "tools", "agent",
             "scripts", "plesk-upload", "plesk-hero-upload", "_wa_src", "App_Data", "backups", "mnt", "includes", "templates", "reports",
             "seo-audit", "agent-status", "conf", "app", "__pycache__", "images", "css", "js", "assets", "audio"}

# --- header / cache / MIME contract (enforced natively by web.config) -------------------------------------------------
SECURITY_HEADERS = {
    "x-content-type-options": "nosniff",
    "x-frame-options": "SAMEORIGIN",
    "referrer-policy": "strict-origin-when-cross-origin",
}
CACHE_LOCATIONS = {  # folder -> max-age seconds (static asset folders only; HTML is never given a long max-age)
    "css": 86400, "js": 86400, "assets": 86400, "images": 604800, "audio": 604800,
}
MIME_TYPES = {".webp": "image/webp", ".mp3": "audio/mpeg", ".woff2": "font/woff2", ".woff": "font/woff", ".json": "application/json",
              ".webmanifest": "application/manifest+json", ".avif": "image/avif", ".svg": "image/svg+xml"}


# ------------------------------------------------------------------ regex enumeration (finite regexes only)
class NotFinite(Exception):
    pass


def _enum(parsed):
    out = [""]
    for op, av in parsed:
        name = str(op)
        if name == "LITERAL":
            opts = [chr(av)]
        elif name == "AT":
            continue
        elif name == "IN":
            chars = []
            for o, a in av:
                if str(o) == "LITERAL":
                    chars.append(chr(a))
                elif str(o) == "RANGE":
                    chars += [chr(c) for c in range(a[0], min(a[1], a[0] + 3) + 1)]
                else:
                    raise NotFinite(name)
            opts = chars[:6] or [""]
        elif name == "SUBPATTERN":
            opts = _enum(av[3])
        elif name == "BRANCH":
            opts = []
            for alt in av[1]:
                opts += _enum(alt)
        elif name in ("MAX_REPEAT", "MIN_REPEAT"):
            lo, hi, sub = av
            if hi > 1:
                raise NotFinite(name)
            opts = ([""] if lo == 0 else []) + _enum(sub)
        else:
            raise NotFinite(name)
        out = [a + b for a in out for b in opts]
        if len(out) > MAX_VARIANTS:
            raise NotFinite("too many variants")
    return out


def enumerate_regex(pattern):
    """All strings an anchored finite regex matches, or None when it is open-ended (.*, .+ ...)."""
    try:
        return sorted(set(_enum(sre_parse.parse(pattern))))
    except (NotFinite, re.error, TypeError, ValueError, IndexError):
        return None


# ------------------------------------------------------------------ .htaccess
def parse_htaccess(text):
    """-> list of rule dicts: line, kind (redirect|pass|rewrite|skip), pattern, target, status, conds, src, text."""
    rules, conds = [], []
    for no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"RewriteCond\s+(\S+)\s+(\S+)", line)
        if m:
            conds.append((m.group(1), m.group(2)))
            continue
        m = re.match(r"RewriteRule\s+(\S+)\s+(\S+)(?:\s+\[([^\]]*)\])?", line)
        if m:
            pat, target, flags = m.group(1), m.group(2), (m.group(3) or "")
            fl = [f.strip().upper() for f in flags.split(",") if f.strip()]
            status = 0
            for f in fl:
                if f.startswith("R"):
                    v = f.split("=")[1] if "=" in f else "302"
                    status = int(v) if v.isdigit() else 302
            if status and not 300 <= status < 400:
                kind = "status"                  # R=404 etc.: answers with that status
            elif status:
                kind = "redirect"
            else:
                kind = "pass" if target == "-" else "rewrite"
            if conds:
                kind = "skip"                    # RewriteCond-guarded (HTTPS force, pretty-URL / WordPress fallbacks): conditional, not a contract
            rules.append({"line": no, "kind": kind, "pattern": pat, "target": target, "status": status, "conds": list(conds),
                          "src": "RewriteRule", "text": line, "nocase": "NC" in fl})
            conds = []
            continue
        m = re.match(r"RedirectMatch\s+(\d+)\s+(\S+)\s+(\S+)", line)
        if m:
            rules.append({"line": no, "kind": "redirect", "pattern": "^" + m.group(2).lstrip("^").lstrip("/"), "target": m.group(3),
                          "status": int(m.group(1)), "conds": [], "src": "RedirectMatch", "text": line, "nocase": False})
    return rules


def _abs(target):
    return target if target.startswith("http") else BASE + (target if target.startswith("/") else "/" + target)


def _compiled(rules):
    out = []
    for r in rules:
        if r["kind"] == "skip":
            continue
        try:
            out.append((re.compile(r["pattern"], re.I if r["nocase"] or r["src"] == "RedirectMatch" else 0), r))
        except re.error:
            pass
    return out


def expect(compiled, path):
    """First matching .htaccess rule decides -> ('redirect', abs target, rule) | ('serve', None, rule) | ('status', code, rule) | None."""
    for rx, rr in compiled:
        m = rx.search(path)
        if not m:
            continue
        if rr["kind"] == "redirect":
            tgt = re.sub(r"\$(\d)", lambda mm: m.group(int(mm.group(1))) or "", rr["target"])
            return ("redirect", _abs(tgt), rr)
        if rr["kind"] == "status":
            return ("status", rr["status"], rr)
        return ("serve", None, rr)
    return None


def fs_html_paths(root=ROOT):
    """Existing .html files visitors can request: root *.html, <dir>/index.html, blog/*.html, blog/<post>/index.html."""
    root = Path(root)
    found = [f.name for f in sorted(root.glob("*.html")) if not f.name.startswith("_")]
    for d in sorted(x for x in root.iterdir() if x.is_dir() and x.name not in SKIP_DIRS and not x.name.startswith((".", "_"))):
        if (d / "index.html").is_file():
            found.append(d.name + "/index.html")
    blog = root / "blog"
    if blog.is_dir():
        found += ["blog/" + f.name for f in sorted(blog.glob("*.html"))]
        for d in sorted(x for x in blog.iterdir() if x.is_dir()):
            if (d / "index.html").is_file():
                found.append("blog/" + d.name + "/index.html")
    return found


def htaccess_probes(rules, root=None):
    """-> [(probe path without leading slash, (kind, target), rule)]. root=None: finite-regex probes only."""
    compiled = _compiled(rules)
    probes, seen = [], set()

    def add(v):
        key = v.lower()
        if not v or key in seen:
            return
        seen.add(key)
        e = expect(compiled, v)
        if e:
            probes.append((v, (e[0], e[1]), e[2]))

    for r in rules:
        if r["kind"] in ("redirect", "rewrite", "pass"):
            for v in enumerate_regex(r["pattern"]) or []:
                add(v)
    if root is not None:
        for v in fs_html_paths(root):
            add(v)
    return probes


# ------------------------------------------------------------------ web.config + IIS simulator
def _conv(p):
    return p


def parse_webconfig(text):
    root = ET.fromstring(text.encode("utf-8"))
    maps = {}
    for mp in root.iter("rewriteMap"):
        maps[mp.get("name")] = {a.get("key").lower(): a.get("value") for a in mp.findall("add")}
    rules = []
    for rule in root.iter("rule"):
        m = rule.find("match")
        a = rule.find("action")
        if m is None or a is None:
            continue
        rules.append({"name": rule.get("name"), "pattern": m.get("url"), "nocase": m.get("ignoreCase", "true").lower() != "false",
                      "negate": m.get("negate", "false").lower() == "true", "conds": [dict(c.attrib) for c in rule.findall("./conditions/add")],
                      "grouping": (rule.find("conditions").get("logicalGrouping", "MatchAll") if rule.find("conditions") is not None else "MatchAll"),
                      "type": a.get("type"), "url": a.get("url"), "redirectType": a.get("redirectType", "Permanent"),
                      "stop": rule.get("stopProcessing", "false").lower() == "true", "enabled": rule.get("enabled", "true").lower() != "false"})
    return rules, maps


class IIS:
    def __init__(self, rules, maps, docroot=ROOT, default_docs=("index.html", "index.asp", "index.php")):
        self.rules, self.maps, self.root, self.docs = rules, maps, Path(docroot), default_docs

    def _phys(self, p):
        return self.root / p.replace("/", os.sep).rstrip(os.sep)

    def _expand(self, s, R, C, p, host="www.colddirect.co.uk", https="on"):
        def rep(m):
            grp = R if m.group(1) == "R" else C
            try:
                return grp.group(int(m.group(2))) or ""
            except (IndexError, AttributeError):
                return ""
        s = re.sub(r"\{(R|C):(\d+)\}", rep, s)
        s = s.replace("{REQUEST_FILENAME}", str(self._phys(p))).replace("{APPL_PHYSICAL_PATH}", str(self.root) + os.sep)
        return s.replace("{HTTPS}", https).replace("{HTTP_HOST}", host)

    def _conds_ok(self, rule, R, p, host, https):
        C = None
        results = []
        for c in rule["conds"]:
            inp = c.get("input", "")
            mt = c.get("matchType", "Pattern")
            mm = re.fullmatch(r"\{(\w+):(\{.*\})\}", inp)
            if mm:                                                  # rewrite map lookup {Map:{R:1}} (unknown map = empty)
                key = self._expand(mm.group(2), R, C, p, host, https).lower()
                m = re.search(c.get("pattern", "(.+)"), self.maps.get(mm.group(1), {}).get(key, ""))
                ok = bool(m)
            elif mt in ("IsFile", "IsDirectory"):
                path = Path(self._expand(inp, R, C, p, host, https))
                ok, m = (path.is_file() if mt == "IsFile" else path.is_dir()), None
            else:
                val = self._expand(inp, R, C, p, host, https)
                m = re.search(c.get("pattern", ".*"), val, re.I if c.get("ignoreCase", "true").lower() != "false" else 0)
                ok = bool(m)
            if c.get("negate", "false").lower() == "true":
                ok = not ok
            if ok and m is not None:
                C = m
            results.append(ok)
            if rule["grouping"] == "MatchAll" and not ok:
                return False, C
        if rule["grouping"] == "MatchAny":
            return (any(results) if results else True), C
        return True, C

    def run(self, path, host="www.colddirect.co.uk", https="on"):
        """path like 'fridge-repair-london/' (no leading slash). -> ('redirect', status, abs url) | ('serve', status, final path)."""
        p = path
        for _ in range(12):
            for rule in self.rules:
                if not rule["enabled"]:
                    continue
                m = re.search(rule["pattern"], p, re.I if rule["nocase"] else 0)
                if bool(m) == rule["negate"]:
                    continue
                ok, C = self._conds_ok(rule, m, p, host, https)
                if not ok:
                    continue
                t = rule["type"]
                if t == "Redirect":
                    url = self._expand(rule["url"], m, C, p, host, https)
                    if not url.startswith("http"):
                        url = BASE + (url if url.startswith("/") else "/" + url)
                    return ("redirect", 301 if rule["redirectType"] in ("Permanent", "301") else 302, url)
                if t == "Rewrite":
                    p = self._expand(rule["url"], m, C, p, host, https).lstrip("/")
                    if rule["stop"]:
                        return self._serve(p)
                    continue
                if t == "None" and rule["stop"]:
                    return self._serve(p)
            break
        return self._serve(p)

    def _serve(self, p):
        phys = self._phys(p)
        if p and phys.is_file():
            return ("serve", 200, p)
        if p == "" or phys.is_dir():
            if p and not p.endswith("/"):
                return ("redirect", 301, BASE + "/" + p + "/")
            if any((phys / d).is_file() for d in self.docs):
                return ("serve", 200, p)
        return ("serve", 404, p)


def load(root=ROOT):
    ht = parse_htaccess((Path(root) / ".htaccess").read_text(encoding="utf-8"))
    wc, maps = parse_webconfig((Path(root) / "web.config").read_text(encoding="utf-8"))
    return ht, IIS(wc, maps, root)


def resolve_final(iis, abs_url, hops=8):
    """Follow the simulator from an absolute URL to its end -> (final abs url, hops, status)."""
    cur, n = abs_url, 0
    for _ in range(hops):
        r = iis.run(urllib.parse.urlsplit(cur).path.lstrip("/"))
        if r[0] == "redirect":
            cur, n = r[2], n + 1
            continue
        return cur, n, r[1]
    return cur, n, 0


def audit(ht=None, iis=None, root=ROOT):
    """-> (rows, problems). Each row: probe, kind, expected, chain, dest_status, got, ok, line, why."""
    if ht is None:
        ht, iis = load(root)
    rows = []
    for probe, (kind, tgt), rule in htaccess_probes(ht, root):
        got = iis.run(probe)
        why, row = "", {"probe": "/" + probe, "line": rule["line"], "got": got}
        if kind == "redirect":
            final, n, st = resolve_final(iis, tgt)
            ok = got[0] == "redirect" and got[1] == 301 and got[2] == final and st == 200
            if not ok:
                if st != 200:
                    why = "dead-target (.htaccess target %s answers %s on IIS)" % (final, st)
                elif got[0] != "redirect":
                    why = "missing-in-web.config (IIS answers %s)" % got[1]
                else:
                    why = "chain/wrong-target (IIS -> %s, canonical end %s)" % (got[2], final)
            row.update(kind="301", expected=final, chain=n, dest_status=st)
        elif kind == "status":
            ok = got[0] == "serve" and got[1] == tgt
            if not ok:
                why = "expected HTTP %s (IIS answers %s)" % (tgt, got[1])
            row.update(kind="status", expected="HTTP %s" % tgt, chain=0, dest_status=tgt)
        elif rule["kind"] == "pass" and (probe.endswith(".php") or not (Path(root) / probe.rstrip("/")).exists()):
            continue                                  # WordPress boilerplate: IIS has no PHP handler / nothing to serve
        else:
            ok = got[0] == "serve" and got[1] == 200
            if not ok and got[0] == "redirect" and got[1] == 301:   # IIS canonicalises to the slash form: fine if it ends in 200
                final, n, st = resolve_final(iis, got[2])
                ok = st == 200 and n == 0
            if not ok:
                why = "serve-expected (IIS answers %s)" % got[1]
            row.update(kind="serve", expected="HTTP 200", chain=0, dest_status=200)
        row.update(ok=ok, why=why)
        rows.append(row)
    return rows, [r for r in rows if not r["ok"]]


def webconfig_probes(iis):
    """URL paths (no leading slash) that exercise every redirect web.config itself can emit: enumerated Redirect-rule patterns
    + every rewrite-map key."""
    probes = set()
    for rule in iis.rules:
        if rule["type"] == "Redirect" and rule["enabled"] and not rule["negate"]:
            for v in enumerate_regex(rule["pattern"]) or []:
                if v:
                    probes.add(v)
    for name, mp in iis.maps.items():
        probes.update(mp)
    return sorted(probes)


def legacy_rows(root=ROOT):
    """Rows for the live legacy-301 probe: every .htaccess-derived URL plus every redirect only web.config defines.
    Each row is {probe, kind '301'|'serve', expected}. Rows that are not in parity offline are left to the offline check."""
    ht, iis = load(root)
    rows, _ = audit(ht, iis, root)
    out = [r for r in rows if r["ok"] and r["kind"] in ("301", "serve")]
    seen = {r["probe"].lower() for r in out}
    for probe in webconfig_probes(iis):
        got = iis.run(probe)
        if got[0] == "redirect" and ("/" + probe).lower() not in seen:
            seen.add(("/" + probe).lower())
            out.append({"probe": "/" + probe, "kind": "301", "expected": got[2]})
    return out


def webconfig_self_audit(iis):
    """Every redirect web.config itself can emit must be ONE hop to a 200: no 2-hop chains, no dead targets.
    Probes = enumerated Redirect-rule patterns + every rewrite-map key. -> [problem]"""
    problems = []
    for probe in webconfig_probes(iis):
        got = iis.run(probe)
        if got[0] != "redirect":
            continue
        final, n, st = resolve_final(iis, got[2])
        if n > 0:
            problems.append("2-hop chain: /%s -> %s -> %s" % (probe, got[2].replace(BASE, ""), final.replace(BASE, "")))
        elif st != 200:
            problems.append("dead redirect target: /%s -> %s answers %s" % (probe, got[2].replace(BASE, ""), st))
    return problems


def strip_generated(text):
    return re.sub(r"[ \t]*" + re.escape(GEN_BEGIN) + r"[\s\S]*?" + re.escape(GEN_END) + r"\r?\n?", "", text)


def generated_entries(ht=None, root=ROOT):
    """{probe path: final canonical path} for every finite .htaccess 301 whose final destination answers 200 on IIS.
    Computed with the GENERATED block stripped (idempotent). Dead targets are skipped here and reported by audit()."""
    root = Path(root)
    if ht is None:
        ht = parse_htaccess((root / ".htaccess").read_text(encoding="utf-8"))
    wc, maps = parse_webconfig(strip_generated((root / "web.config").read_text(encoding="utf-8")))
    bare = IIS(wc, dict(maps, **{MAP_NAME: {}}), root)               # hand-written rules only: decides what is a gap
    probes = [p for p in htaccess_probes(ht, root) if p[1][0] == "redirect"]
    entries = {}
    for _ in range(5):                                                # fixpoint: finals are resolved WITH the map built so far
        full = IIS(wc, dict(maps, **{MAP_NAME: {k.lower(): v for k, v in entries.items()}}), root)
        new = {}
        for probe, (kind, tgt), rule in probes:
            final, n, st = resolve_final(full, tgt)
            if st != 200:
                continue
            if bare.run(probe) == ("redirect", 301, final):
                continue                                          # already answered correctly by a hand-written rule
            new[probe] = final.replace(BASE, "") or "/"
        if new == entries:
            break
        entries = new
    return entries


def render_map(entries):
    lines = ["        " + GEN_BEGIN, '        <rewriteMap name="%s">' % MAP_NAME]
    for k in sorted(entries):
        lines.append('          <add key="%s" value="%s" />' % (k, entries[k]))
    lines += ["        </rewriteMap>", "        " + GEN_END]
    return "\r\n".join(lines) + "\r\n"


def generate(root=ROOT, write=True):
    root = Path(root)
    path = root / "web.config"
    text = path.read_bytes().decode("utf-8")
    base = strip_generated(text)
    entries = generated_entries(None, root)
    m = re.search(r"[ \t]*</rewriteMaps>", base)
    if not m:
        raise SystemExit("web.config has no </rewriteMaps> to extend")
    new = base[:m.start()] + render_map(entries) + base[m.start():]
    changed = new != text
    if write and changed:
        path.write_bytes(new.encode("utf-8"))
    return entries, changed


# ------------------------------------------------------------------ static header / cache / MIME / host checks (offline)
def static_config_checks(text):
    """Offline contract on web.config: security headers, MIME maps, asset caching, canonical host/HTTPS rule. -> [problem]"""
    problems = []
    try:
        root = ET.fromstring(text.encode("utf-8"))
    except ET.ParseError as e:
        return ["web.config is not well-formed XML: %s" % e]
    headers = {a.get("name", "").lower(): a.get("value") for a in root.iterfind("./system.webServer/httpProtocol/customHeaders/add")}
    for name, val in SECURITY_HEADERS.items():
        if headers.get(name) != val:
            problems.append("web.config customHeaders lacks %s: %s" % (name, val))
    removed = {a.get("name", "").lower() for a in root.iterfind("./system.webServer/httpProtocol/customHeaders/remove")}
    if "x-powered-by" not in removed:
        problems.append("web.config does not remove the X-Powered-By header")
    mimes = {a.get("fileExtension"): a.get("mimeType") for a in root.iterfind("./system.webServer/staticContent/mimeMap")}
    for ext, mt in MIME_TYPES.items():
        if mimes.get(ext) != mt:
            problems.append("web.config staticContent lacks mimeMap %s -> %s" % (ext, mt))
    for loc in root.iterfind("./location"):
        pass
    caches = {}
    for loc in root.iterfind("./location"):
        cc = loc.find("./system.webServer/staticContent/clientCache")
        if cc is not None:
            ma = cc.get("cacheControlMaxAge", "")
            m = re.fullmatch(r"(?:(\d+)\.)?(\d+):(\d+):(\d+)", ma)
            if m:
                caches[loc.get("path")] = int(m.group(1) or 0) * 86400 + int(m.group(2)) * 3600 + int(m.group(3)) * 60 + int(m.group(4))
    for folder, secs in CACHE_LOCATIONS.items():
        if caches.get(folder) != secs:
            problems.append("web.config has no <location path=\"%s\"> clientCache max-age=%d" % (folder, secs))
    rules, _ = parse_webconfig(text)
    canon = [r for r in rules if r["type"] == "Redirect" and (r["url"] or "").startswith(BASE + "/{R:1}")]
    host_ok = any(any("HTTPS" in c.get("input", "") for c in r["conds"]) for r in canon) and \
        any(any("HTTP_HOST" in c.get("input", "") for c in r["conds"]) for r in canon)
    if not host_ok:
        problems.append("web.config has no single-hop http->https / non-www->www canonical redirect rule")
    return problems


def canonical_host_sim(iis):
    """Simulator check: http / non-www URLs must be ONE 301 straight to https://www ... (-> [problem])."""
    out = []
    for host, https, path in (("www.colddirect.co.uk", "off", "about-us/"), ("colddirect.co.uk", "on", "about-us/"), ("colddirect.co.uk", "off", "about-us/")):
        r = iis.run(path, host=host, https=https)
        if r != ("redirect", 301, BASE + "/about-us/"):
            out.append("host=%s https=%s /about-us/ -> %s (want 301 %s/about-us/)" % (host, https, r, BASE))
    ok = iis.run("about-us/")
    if ok[0] != "serve" or ok[1] != 200:
        out.append("canonical https://www host must not redirect again: %s" % (ok,))
    return out


# ------------------------------------------------------------------ live probing (no redirect following)
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def live_get(url, method="GET", timeout=25):
    """-> (status, {lowercase header: value}); never follows redirects."""
    import time
    req = urllib.request.Request(url, method=method, headers={"User-Agent": "cd-config-parity/1.0", "Accept": "*/*"})
    res = (0, {"error": "no attempt"})
    for attempt in range(3):                       # transient network errors are retried; HTTP statuses never are
        try:
            r = _OPENER.open(req, timeout=timeout)
            return r.status, {k.lower(): v for k, v in r.headers.items()}
        except urllib.error.HTTPError as e:
            return e.code, {k.lower(): v for k, v in e.headers.items()}
        except Exception as e:  # network error
            res = (0, {"error": str(e)[:80]})
            time.sleep(1 + attempt)
    return res


def live_audit(rows, base=BASE, workers=8, fetch=live_get):
    """Probe every audit row live. -> (problems [str], n_checked). A 301 row passes with status 301 + exact Location (single hop)."""
    from concurrent.futures import ThreadPoolExecutor
    wanted = [r for r in rows if r["kind"] in ("301", "serve")]

    def one(r):
        st, hd = fetch(base + r["probe"])
        if r["kind"] == "301":
            loc = hd.get("location", "")
            if st == 301 and loc == r["expected"]:
                return None
            return "%s -> %s %s (want 301 %s)" % (r["probe"], st, loc or "", r["expected"])
        if st == 200:
            return None
        if st == 301 and hd.get("location", "").startswith(base) and hd.get("location", "").rstrip("/") == (base + r["probe"]).rstrip("/"):
            return None                                   # slash canonicalisation of a served page
        return "%s -> %s (want 200)" % (r["probe"], st)

    with ThreadPoolExecutor(workers) as ex:
        res = list(ex.map(one, wanted))
    problems = [x for x in res if x]
    finals = sorted({r["expected"] for r in wanted if r["kind"] == "301" and r["expected"].startswith(base)})   # 301 -> 200
    with ThreadPoolExecutor(workers) as ex:
        fres = list(ex.map(lambda u: (u, fetch(u)[0]), finals))
    problems += ["301 destination %s -> HTTP %s (want 200)" % (u.replace(base, ""), st) for u, st in fres if st != 200]
    return problems, len(wanted) + len(finals)


def live_header_checks(base=BASE, fetch=live_get):
    """Security + caching headers on live pages / assets and MIME types of the static types. -> (problems, n_checked)"""
    problems, n = [], 0
    for path in ("/", "/fridge-repair-london/", "/blog/", "/css/styles.css"):
        st, hd = fetch(base + path)
        n += 1
        if st != 200:
            problems.append("%s -> HTTP %s (headers not checkable)" % (path, st))
            continue
        for name, val in SECURITY_HEADERS.items():
            if hd.get(name) != val:
                problems.append("%s: header %s = %r (want %r)" % (path, name, hd.get(name), val))
        if "x-powered-by" in hd:
            problems.append("%s: X-Powered-By still sent (%s)" % (path, hd["x-powered-by"]))
    assets = {"/css/styles.css": ("text/css", 86400), "/js/main.js": ("javascript", 86400),
              "/images/slider-colour-ac.webp": ("image/webp", 604800), "/audio/colddirect-home.mp3": (("audio/mpeg", "audio/mp3"), 604800)}
    for path, (mt, secs) in assets.items():
        st, hd = fetch(base + path)
        n += 1
        if st != 200:
            problems.append("%s -> HTTP %s" % (path, st))
            continue
        ctype = hd.get("content-type", "").lower()
        mts = mt if isinstance(mt, tuple) else (mt,)
        if not any(m in ctype for m in mts):
            problems.append("%s: Content-Type %r (want %s)" % (path, ctype, "/".join(mts)))
        cc = hd.get("cache-control", "")
        m = re.search(r"max-age=(\d+)", cc)
        if not m or int(m.group(1)) != secs:
            problems.append("%s: Cache-Control %r (want max-age=%d)" % (path, cc, secs))
        if hd.get("x-content-type-options") != "nosniff":
            problems.append("%s: missing X-Content-Type-Options: nosniff" % path)
    return problems, n


def offline_problems(root=ROOT):
    """Everything the permanent offline guard enforces -> (problems [str], stats dict)."""
    root = Path(root)
    ht = parse_htaccess((root / ".htaccess").read_text(encoding="utf-8"))
    text = (root / "web.config").read_text(encoding="utf-8")
    wc, maps = parse_webconfig(text)
    iis = IIS(wc, maps, root)
    rows, bad = audit(ht, iis, root)
    probs = ["line %d %s: %s" % (r["line"], r["probe"], r["why"]) for r in bad]
    probs += webconfig_self_audit(iis)
    probs += static_config_checks(text)
    probs += canonical_host_sim(iis)
    entries = generated_entries(ht, root)
    cur = {k: v for k, v in maps.get(MAP_NAME, {}).items()}
    stale = [k for k in entries if cur.get(k.lower()) != entries[k]]
    if stale:
        probs.append("web.config %s map is out of date (%d entries): run python tools/config_parity.py --generate" % (MAP_NAME, len(stale)))
    return probs, {"rules": len(ht), "probes": len(rows), "redirect_probes": sum(1 for r in rows if r["kind"] == "301"), "map_entries": len(cur)}


# ------------------------------------------------------------------ selftest
def selftest():
    import tempfile
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    check("enum alternation", enumerate_regex(r"^fridge-repairs-london(/|\.html|\.asp)?$") == sorted(["fridge-repairs-london", "fridge-repairs-london/", "fridge-repairs-london.html", "fridge-repairs-london.asp"]))
    check("enum class", enumerate_regex(r"^[Ee]mergency$") == ["Emergency", "emergency"])
    check("enum optional char", enumerate_regex(r"^ab?c$") == ["abc", "ac"])
    check("open-ended not enumerated", enumerate_regex(r"^(.*)\.html$") is None)
    ht = parse_htaccess("RewriteEngine On\nRewriteRule ^old\\.asp$ /new/ [R=301,L]\nRedirectMatch 301 ^/x\\.html$ /y/\nRewriteRule ^p/?$ /p.html [L]\n"
                        "RewriteRule ^gone/(.+)$ - [R=404,L]\nRewriteCond %{HTTPS} off\nRewriteRule ^(.*)$ https://a/$1 [R=301,L]\n")
    check("parse kinds", [r["kind"] for r in ht] == ["redirect", "redirect", "rewrite", "status", "skip"])
    check("first match wins", expect(_compiled(ht), "old.asp")[:2] == ("redirect", BASE + "/new/"))
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "new").mkdir()
        (root / "new" / "index.html").write_text("x")
        (root / "p.html").write_text("x")
        (root / ".htaccess").write_text("RewriteRule ^old\\.asp$ /new/ [R=301,L]\nRewriteRule ^p\\.html$ /p/ [R=301,L]\n", encoding="utf-8")
        wc = '<configuration><system.webServer><rewrite><rewriteMaps><rewriteMap name="M"><add key="old.asp" value="/new/" /></rewriteMap></rewriteMaps><rules>%s</rules></rewrite></system.webServer></configuration>'
        rule_ok = ('<rule name="a" stopProcessing="true"><match url="^(.+)$" /><conditions><add input="{M:{R:1}}" pattern="(.+)" /></conditions>'
                   '<action type="Redirect" url="https://www.colddirect.co.uk{C:1}" redirectType="Permanent" /></rule>')
        (root / "web.config").write_text(wc % rule_ok, encoding="utf-8")
        rows, bad = audit(root=root)
        check("old.asp ok, p.html not enforced -> 1 problem", len(bad) == 1 and bad[0]["probe"] == "/p.html")
        rule_p = ('<rule name="b" stopProcessing="true"><match url="^p\\.html$" /><action type="Redirect" url="https://www.colddirect.co.uk/p/" redirectType="Permanent" /></rule>')
        (root / "web.config").write_text(wc % (rule_ok + rule_p), encoding="utf-8")
        rows, bad = audit(root=root)
        check("p/ has no page -> dead target", len(bad) == 1 and "dead-target" in bad[0]["why"])
        (root / "p").mkdir()
        (root / "p" / "index.html").write_text("x")
        rows, bad = audit(root=root)
        check("all in parity", not bad and len(rows) >= 2)
        rule_chain = ('<rule name="c" stopProcessing="true"><match url="^old\\.asp$" /><action type="Redirect" url="https://www.colddirect.co.uk/old2/" redirectType="Permanent" /></rule>')
        (root / "web.config").write_text(wc % (rule_chain + rule_p), encoding="utf-8")
        rows, bad = audit(root=root)
        check("wrong target detected", any("old.asp" in r["probe"] for r in bad))
        (root / "web.config").write_text(wc % rule_p, encoding="utf-8")       # nothing answers old.asp yet -> it is a gap
        e, changed = generate(root)
        check("generate adds only the gap entries", changed and "old.asp" in e and "p.html" not in e
              and "<rewriteMap name=\"HtaccessParity\">" in (root / "web.config").read_text())
        e2, changed2 = generate(root)
        check("generate idempotent", not changed2)
    check("static checks flag empty config", len(static_config_checks("<configuration><system.webServer/></configuration>")) >= 5)
    row = [{"probe": "/a", "kind": "301", "expected": BASE + "/b/"}]

    def site(a_resp, b_status=200):
        return lambda u: a_resp if u.endswith("/a") else (b_status, {})
    check("live 301 single hop to 200 passes", live_audit(row, fetch=site((301, {"location": BASE + "/b/"})))[0] == [])
    check("live 200 instead of 301 fails", len(live_audit(row, fetch=site((200, {})))[0]) == 1)
    check("live 302 fails", len(live_audit(row, fetch=site((302, {"location": BASE + "/b/"})))[0]) == 1)
    check("live wrong Location fails", len(live_audit(row, fetch=site((301, {"location": BASE + "/c/"})))[0]) == 1)
    check("live dead destination fails", any("destination" in x for x in live_audit(row, fetch=site((301, {"location": BASE + "/b/"}), 404))[0]))
    good = {"content-type": "text/css", "cache-control": "max-age=86400", **SECURITY_HEADERS}
    p, n = live_header_checks(fetch=lambda u: (200, dict(good)))
    check("live header checks detect wrong asset types", len(p) >= 3 and n == 8)
    p, n = live_header_checks(fetch=lambda u: (200, {k: v for k, v in good.items() if k != "x-frame-options"}))
    check("live header checks detect missing X-Frame-Options", any("x-frame-options" in x for x in p))
    if fails:
        print("config_parity selftest FAILED: " + ", ".join(fails))
        return 1
    print("config_parity selftest OK (%d checks)" % 20)
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--generate" in argv or "-g" in argv:
        entries, changed = generate()
        print("web.config %s map: %d entries (%s)" % (MAP_NAME, len(entries), "updated" if changed else "unchanged"))
        return 0
    probs, stats = offline_problems()
    print("config parity (offline): %(rules)d .htaccess rules, %(probes)d probes (%(redirect_probes)d 301s), %(map_entries)d generated map entries" % stats)
    for p in probs:
        print("  ✗ " + p)
    rc = 1 if probs else 0
    if "--live" in argv:
        lp, n = live_audit(legacy_rows())
        hp, hn = live_header_checks()
        print("config parity (live): %d URL probes, %d header/asset probes" % (n, hn))
        for p in lp + hp:
            print("  ✗ " + p)
        rc = rc or (1 if lp or hp else 0)
    print("RESULT: " + ("PARITY BROKEN" if rc else "PARITY OK"))
    return rc


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main(sys.argv[1:]))
