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
import shutil
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
class FakeServer { public string Root = ""; public string MapPath(string p) { return Root; } }
class P {
  public FakeRequest Request = new FakeRequest(); public FakeResponse Response = new FakeResponse(); public FakeServer Server = new FakeServer();
//BODY//
  public string Run(string root) {
    if (!root.EndsWith("\\")) root += "\\";
    Server.Root = root; Request.QueryString["key"] = "cd2026";
    Page_Load(null, null);
    return Response.StatusCode + " " + Response.Out.ToString();
  }
}
class T { static int Main(string[] a) { P p = new P(); Console.Write(p.Run(a[0])); return 0; } }
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


def run(exe, root):
    out = subprocess.run([exe, root], capture_output=True, text=True, timeout=300).stdout
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


def main():
    if not find_csc():
        print("csc.exe (.NET Framework 4) not found - cannot run behavioural tests on this machine")
        return 2
    tmp = tempfile.mkdtemp(prefix="autoseo-test-")
    try:
        exe = build(tmp)
        print("compiled OK")
        synthetic(exe, tmp)
        real_tree(exe, tmp)
        print("ALL AUTO-SEO TESTS PASSED")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
