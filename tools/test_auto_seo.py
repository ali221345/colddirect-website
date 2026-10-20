#!/usr/bin/env python3
"""Behavioural tests for auto-seo.aspx (V4.9) - compiles the REAL script body with csc and runs it.

How: the <script runat="server"> body is pasted into a plain C# class that supplies fake Request/Response/Server,
compiled with the .NET Framework 4 csc.exe (Windows) and executed against temp copies of HTML trees.

Checks
  1. synthetic tree: sitemap includes /blog/, blog articles, Enfield; excludes about, news, brands-plural,
     canonical-elsewhere, noindex, logs/; blog pages keep their layout (only an EMPTY description is filled).
  2. real tree: every page of this repo is copied to a temp dir and the agent is run 3 times;
     run 2 and run 3 must report "HTML Updated: 0" (100% idempotent, no blank-line growth) and be byte-identical.
Usage:  python tools/test_auto_seo.py
"""
import glob
import hashlib
import os
import re
import secrets
import shutil
import string
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASPX = os.path.join(ROOT, "auto-seo.aspx")
CSC_CANDIDATES = [
    r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe",
    r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe",
]

HARNESS = r"""
using System; using System.IO; using System.Text; using System.Text.RegularExpressions;
using System.Collections.Generic; using System.Collections.Specialized;
class FakeRequest { public NameValueCollection QueryString = new NameValueCollection(); }
class FakeResponse { public int StatusCode = 200; public string ContentType = ""; public StringBuilder Out = new StringBuilder(); public void Write(string s) { Out.Append(s); } }
class FakeServer { public string Root = ""; public string MapPath(string p) { if (p != null && p.StartsWith("~/") && p.Length > 2) return Path.Combine(Root, p.Substring(2).Replace('/', '\\')); return Root; } }
class P {
  public FakeRequest Request = new FakeRequest(); public FakeResponse Response = new FakeResponse(); public FakeServer Server = new FakeServer();
//BODY//
  public string Run(string root, string key) {
    if (!root.EndsWith("\\")) root += "\\";
    Server.Root = root; if (key != null) Request.QueryString["key"] = key;
    Page_Load(null, null);
    return Response.StatusCode + " " + Response.Out.ToString();
  }
}
class T { static int Main(string[] a) { P p = new P(); Console.Write(p.Run(a[0], a.Length > 1 && a[1] != "<none>" ? a[1] : null)); return 0; } }
"""


def find_csc():
    for c in CSC_CANDIDATES:
        if os.path.exists(c):
            return c
    return None


def build(tmp):
    src = open(ASPX, encoding="utf-8").read()
    start = src.index('<script runat="server">') + len('<script runat="server">')
    body = src[start:src.rindex("</script>")]
    cs = os.path.join(tmp, "harness.cs")
    exe = os.path.join(tmp, "harness.exe")
    open(cs, "w", encoding="utf-8").write(HARNESS.replace("//BODY//", body))
    r = subprocess.run([find_csc(), "/nologo", "/out:" + exe, cs], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout + r.stderr)
        raise SystemExit("COMPILE FAILED")
    return exe


# per-run random key: the real key never appears in the repo, and "cd2026" must be rejected
TEST_KEY = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))


def write_key(root, content=TEST_KEY):
    d = os.path.join(root, "App_Data")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "auto-seo.key"), "w", encoding="ascii", newline="") as f:
        f.write(content)


def call(exe, root, key):
    return subprocess.run([exe, root, key if key is not None else "<none>"], capture_output=True, text=True, timeout=300).stdout


def run(exe, root):
    if not os.path.exists(os.path.join(root, "App_Data", "auto-seo.key")):
        write_key(root)
    out = call(exe, root, TEST_KEY)
    m = re.search(r"HTML Updated: (\d+) \| Sitemap URLs: (\d+)", out)
    assert m and "AUTO-SEO V4.9" in out and out.startswith("200"), out
    return int(m.group(1)), int(m.group(2))


def snapshot(root):
    snap = {}
    for dp, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(dp, f)
            snap[os.path.relpath(p, root)] = hashlib.sha1(open(p, "rb").read()).hexdigest()
    return snap


def sitemap(root):
    return set(re.findall(r"<loc>(.*?)</loc>", open(os.path.join(root, "sitemap.xml"), encoding="utf-8").read()))


def page(title, desc, canon, body="<p>x</p>", extra=""):
    d = '<meta name="description" content="%s">' % desc if desc is not None else ""
    c = '<link rel="canonical" href="%s">' % canon if canon else ""
    return "<!DOCTYPE html>\n<html lang=\"en-GB\">\n<head>\n<title>%s</title>\n%s\n%s\n%s\n</head>\n<body>\n%s\n</body>\n</html>\n" % (title, d, c, extra, body)


BASE = "https://www.colddirect.co.uk/"


def synthetic(exe, tmp):
    root = os.path.join(tmp, "syn")
    files = {
        "index.html": page("Home", "home", BASE),
        "fridge-repair-london.html": page("Fridge", "d", BASE + "fridge-repair-london/"),
        "commercial-fridge-repair-enfield.html": page("Enfield", "d", BASE + "commercial-fridge-repair-enfield/"),
        "commercial-fridge-repair-enfield/index.html": page("Enfield", "d", BASE + "commercial-fridge-repair-enfield/"),
        "about.html": page("About", "", BASE + "about-us/", extra='<meta http-equiv="refresh" content="0;url=/about-us.html"><meta name="robots" content="noindex, follow">'),
        "news.html": page("News", "", BASE + "blog/", extra='<meta http-equiv="refresh" content="0;url=/blog/">'),
        "refrigeration-brands-repairs-london.html": page("Brands", "d", BASE + "refrigeration-brands-repairs-london"),
        "elsewhere.html": page("E", "d", BASE + "something-else/"),
        "hidden.html": page("H", "d", BASE + "hidden/", extra='<meta name="robots" content="noindex, nofollow">'),
        "logs/old.html": page("Log", "d", BASE + "logs/old/"),
        "blog/index.html": page("Blog | Cold Direct", "hub", BASE + "blog/"),
        "blog/a/index.html": page("Article A", "has description", BASE + "blog/a/", body="<p>A</p>\n\n\n<!-- AUTO-SEO-V4-2026 -->\n<div class=\"seo-service-tags\">keep</div>\n"),
        "blog/b/index.html": page("Why Freezers Ice Up | Cold Direct", "", BASE + "blog/b/"),
        "blog/c/index.html": page("Dup of A", "dup", BASE + "blog/a/"),
        "blog/a.html": page("Article A", "has description", BASE + "blog/a/"),
    }
    for rel, content in files.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8", newline="").write(content)
    blog_a_before = open(os.path.join(root, "blog", "a", "index.html"), "rb").read()
    u1, n1 = run(exe, root)
    sm = sitemap(root)
    must = [BASE, BASE + "fridge-repair-london/", BASE + "commercial-fridge-repair-enfield/", BASE + "blog/", BASE + "blog/a/", BASE + "blog/b/"]
    mustnot = [BASE + "about/", BASE + "news/", BASE + "refrigeration-brands-repairs-london/", BASE + "elsewhere/", BASE + "hidden/",
               BASE + "blog/c/", BASE + "logs/old/", BASE + "logs/"]
    for u in must:
        assert u in sm, "missing from sitemap: " + u
    for u in mustnot:
        assert u not in sm, "must NOT be in sitemap: " + u
    assert open(os.path.join(root, "blog", "a", "index.html"), "rb").read() == blog_a_before, "blog article layout was altered"
    b = open(os.path.join(root, "blog", "b", "index.html"), encoding="utf-8").read()
    assert re.search(r'<meta name="description" content="[^"]{20,}', b), "empty blog description not filled"
    assert "AUTO-SEO-V4-2026" not in b and "AUTO-SEO-V4-SCHEMA" not in b, "V4 blocks injected into blog"
    assert "AUTO-SEO-V4-2026" in open(os.path.join(root, "blog", "a", "index.html"), encoding="utf-8").read(), "V4 footer removed from blog"
    s1 = snapshot(root)
    u2, _ = run(exe, root)
    s2 = snapshot(root)
    assert u2 == 0 and s1 == s2, "synthetic tree not idempotent (updated=%d)" % u2
    print("synthetic OK: sitemap=%d urls, run1 updated=%d, run2 updated=0" % (n1, u1))


def real_tree(exe, tmp):
    root = os.path.join(tmp, "real")
    skip = {"node_modules", ".git", "colddirect-public-html", "logs", "backups", "docs", "tools", "agent", "reports", "seo-audit",
            "scripts", "templates", "images", "css", "js", "public", "app", "mnt", ".github", ".cursor", ".vscode", "_wa_src"}
    n = 0
    for dp, dns, fs in os.walk(ROOT):
        rel = os.path.relpath(dp, ROOT)
        if rel == ".":
            dns[:] = [d for d in dns if d not in skip]
        for f in fs:
            if f.endswith(".html"):
                dst = os.path.join(root, rel, f) if rel != "." else os.path.join(root, f)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(os.path.join(dp, f), dst)
                n += 1
    u1, n1 = run(exe, root)
    s1 = snapshot(root)
    u2, n2 = run(exe, root)
    s2 = snapshot(root)
    u3, n3 = run(exe, root)
    s3 = snapshot(root)
    print("real tree: %d html files | run1 updated=%d | run2 updated=%d | run3 updated=%d | sitemap=%d urls" % (n, u1, u2, u3, n3))
    changed = [k for k in s1 if s1[k] != s2.get(k)]
    assert u2 == 0 and u3 == 0 and s2 == s3, "NOT IDEMPOTENT: run2 changed %d files, e.g. %s" % (len(changed), changed[:5])
    sm = sitemap(root)
    for u in (BASE + "blog/", BASE + "commercial-fridge-repair-enfield/"):
        assert u in sm, "real tree: missing from sitemap: " + u
    for u in (BASE + "about/", BASE + "news/", BASE + "preview-colddirect-homepage/", BASE + "refrigeration-brands-repairs-london/"):
        assert u not in sm, "real tree: must NOT be in sitemap: " + u
    blog_urls = [u for u in sm if "/blog/" in u]
    assert len(blog_urls) >= 10, "expected the blog hub + articles in the sitemap, got %d" % len(blog_urls)
    # blog pages must not get V4 injections beyond what they already had
    for p in glob.glob(os.path.join(root, "blog", "*", "index.html")):
        orig = open(os.path.join(ROOT, os.path.relpath(p, root)), "rb").read()
        assert open(p, "rb").read() == orig, "blog page altered by auto-seo: " + os.path.relpath(p, root)
    print("real tree OK: blog urls in sitemap=%d, enfield present, stubs/preview/brands-plural absent, blog pages untouched" % len(blog_urls))


def auth_tests(exe, tmp):
    root = os.path.join(tmp, "auth")
    os.makedirs(root)
    open(os.path.join(root, "index.html"), "w", encoding="utf-8").write(page("Home", "home", BASE))
    # no key file at all -> fail closed, even with the right-looking key
    for k in (TEST_KEY, "cd2026", None, ""):
        out = call(exe, root, k)
        assert out.startswith("403") and "AUTO-SEO" not in out, "missing key file must reject everything: %r" % out[:40]
    assert not os.path.exists(os.path.join(root, "sitemap.xml")), "agent ran without a key file"
    # short key file -> fail closed
    write_key(root, "cd2026")
    assert call(exe, root, "cd2026").startswith("403"), "short key file must not authenticate"
    # proper key file
    write_key(root)
    for bad in ("cd2026", "", None, TEST_KEY[:-1], TEST_KEY + "x", TEST_KEY.swapcase() if TEST_KEY.swapcase() != TEST_KEY else TEST_KEY[::-1] + "0"):
        out = call(exe, root, bad)
        assert out.startswith("403") and "AUTO-SEO" not in out, "wrong key accepted: %r" % bad
    assert not os.path.exists(os.path.join(root, "sitemap.xml")), "agent ran with a wrong key"
    out = call(exe, root, TEST_KEY)
    assert out.startswith("200") and "AUTO-SEO V4.9" in out and "OK" in out, out[:80]
    # trailing newline in the key file is tolerated
    write_key(root, TEST_KEY + "\r\n")
    assert call(exe, root, TEST_KEY).startswith("200")
    print("auth OK: no key file / short file / wrong, old (cd2026), empty, truncated, extended keys all rejected; right key accepted")


def main():
    if not find_csc():
        print("csc.exe (.NET Framework 4) not found - cannot run behavioural tests on this machine")
        return 2
    tmp = tempfile.mkdtemp(prefix="autoseo-test-")
    try:
        exe = build(tmp)
        print("compiled OK")
        auth_tests(exe, tmp)
        synthetic(exe, tmp)
        real_tree(exe, tmp)
        print("ALL AUTO-SEO TESTS PASSED")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
