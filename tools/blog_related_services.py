#!/usr/bin/env python3
"""Blog -> money-page internal linking guard (idempotent).

Every blog ARTICLE (blog/<slug>.html and blog/<slug>/index.html, root + colddirect-public-html mirror)
must link contextually to at least MIN_LINKS of the 9 core revenue landing pages.

"Contextual" = links in the page content, i.e. NOT counting the nav include, hero, the
AUTO-SEO-V4-2026 footer strip, the CD-9-MONEY silo block, <footer>, or our own injected block.

If a post has fewer than MIN_LINKS, a small "Related London Services" block is injected right before
</article> (fallbacks: before the money silo, <footer>, </body>). The block is wrapped in
<!-- CD-BLOG-RELATED-SERVICES --> ... <!-- /CD-BLOG-RELATED-SERVICES --> so re-runs never duplicate it.

The blog hub (blog/index.html) is a listing page, not an article, and is never touched.
Pages are never touched when they already satisfy the rule, so a clean tree = zero diff.

Usage:
  python tools/blog_related_services.py            # apply
  python tools/blog_related_services.py --check    # report only, exit 1 if any article lacks links
  python tools/blog_related_services.py --selftest # synthetic injection + idempotency test
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = "colddirect-public-html"
MIN_LINKS = 2
START, END = "<!-- CD-BLOG-RELATED-SERVICES -->", "<!-- /CD-BLOG-RELATED-SERVICES -->"

# slug -> (anchor text, one-line description)
CORE = {
    "fridge-repair-london": ("Fridge Repair London", "same-day commercial fridge repair and service"),
    "freezer-repair-london": ("Freezer Repair London", "emergency commercial freezer repair"),
    "commercial-fridge-repair-london": ("Commercial Fridge Repair London", "24/7 engineers for kitchens, shops and bars"),
    "commercial-freezer-repair-london": ("Commercial Freezer Repair London", "upright, chest and walk-in freezer faults"),
    "cold-room-repair-london": ("Cold Room Repair London", "walk-in chiller and freezer room repair"),
    "catering-repair-london": ("Catering Repair London", "kitchen refrigeration and catering equipment"),
    "commercial-catering-repair-london": ("Commercial Catering Repair London", "restaurants, hotels and takeaways"),
    "air-conditioning-repair-london": ("Air Conditioning Repair London", "commercial AC, split and VRV/VRF systems"),
    "cellar-cooler-repair-london": ("Cellar Repair London", "pub and bar beer cellar cooling"),
}

# topic keywords (matched against slug + title + h1) -> preferred core slugs, most relevant first
TOPICS = [
    (("air-con", "air con", "hvac", " ac ", "vrv", "vrf"),
     ["air-conditioning-repair-london", "commercial-fridge-repair-london", "cold-room-repair-london"]),
    (("cellar", "beer", "pub", "keg"),
     ["cellar-cooler-repair-london", "air-conditioning-repair-london", "commercial-fridge-repair-london"]),
    (("catering", "kitchen", "restaurant", "takeaway"),
     ["catering-repair-london", "commercial-catering-repair-london", "commercial-fridge-repair-london"]),
    (("cold room", "cold-room", "walk-in", "storage"),
     ["cold-room-repair-london", "commercial-freezer-repair-london", "commercial-fridge-repair-london"]),
    (("freezer", "freezing", "ice", "icing", "frost", "defrost"),
     ["commercial-freezer-repair-london", "freezer-repair-london", "cold-room-repair-london"]),
    (("fridge", "cooling", "chiller", "temperature", "f-gas", "fgas", "cost", "breakdown"),
     ["commercial-fridge-repair-london", "fridge-repair-london", "commercial-freezer-repair-london"]),
]
DEFAULT = ["commercial-fridge-repair-london", "commercial-freezer-repair-london", "cold-room-repair-london"]

STRIP_PATTERNS = [
    r"<!-- AUTO-SEO-V4-2026 -->[\s\S]*?</div>",
    r"<!-- CD-9-MONEY-KEYWORD-SILO-V47 -->[\s\S]*?<!-- /CD-9-MONEY-KEYWORD-SILO-V47 -->",
    r"<footer\b[\s\S]*?</footer>",
    r"<header\b[\s\S]*?</header>",
    r"<nav\b[\s\S]*?</nav>",
    r"<section[^>]*class=[\"'][^\"']*\bhero\b[^\"']*[\"'][\s\S]*?</section>",
    r"<!--#include[\s\S]*?-->",
]
HREF_RE = re.compile(r"""href=["'](?:https?://(?:www\.)?colddirect\.co\.uk)?/([a-z0-9-]+)(?:/|\.html|\.asp)?(?:[?#][^"']*)?["']""", re.I)


def contextual_core_links(html):
    body = html
    for pat in STRIP_PATTERNS:
        body = re.sub(pat, "", body, flags=re.I)
    return sorted({m.group(1).lower() for m in HREF_RE.finditer(body)} & set(CORE))


def pick_links(html, path):
    title = re.search(r"<title>([\s\S]*?)</title>", html, re.I)
    h1 = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", html, re.I)
    hay = " ".join([os.path.basename(path), title.group(1) if title else "", h1.group(1) if h1 else ""]).lower()
    chosen = []
    for words, slugs in TOPICS:
        if any(w in hay for w in words):
            for s in slugs:
                if s not in chosen:
                    chosen.append(s)
    for s in DEFAULT:
        if s not in chosen:
            chosen.append(s)
    return chosen[:3]


def build_block(slugs, nl):
    lines = [
        START,
        '<aside class="cd-related-services" style="margin:28px 0 0;padding:16px 18px;border:1px solid #e2e8f0;border-radius:10px;background:#f8fafc;">',
        '  <h2 style="font-size:18px;margin:0 0 8px;">Related London Services</h2>',
        '  <ul style="margin:0;padding-left:18px;">',
    ]
    for s in slugs:
        text, desc = CORE[s]
        lines.append('    <li><a href="/%s/">%s</a> - %s</li>' % (s, text, desc))
    lines += ["  </ul>", "</aside>", END]
    return nl.join(lines) + nl


def inject(html, block, nl):
    m = list(re.finditer(r"</article>", html, re.I))
    if m:
        i = m[-1].start()
        return html[:i] + block + html[i:]
    for marker in (r"<!-- CD-9-MONEY-KEYWORD-SILO-V47 -->", r"<footer\b", r"</body>"):
        mm = re.search(marker, html, re.I)
        if mm:
            return html[:mm.start()] + block + html[mm.start():]
    return html + nl + block


def process(html, path):
    """Return (new_html, links_before). new_html == html when nothing to do."""
    links = contextual_core_links(html)
    if len(links) >= MIN_LINKS or START in html:
        return html, links
    nl = "\r\n" if "\r\n" in html else "\n"
    return inject(html, build_block(pick_links(html, path), nl), nl), links


def article_files():
    out = []
    for base in ("", MIRROR + "/"):
        pats = [os.path.join(ROOT, base, "blog", "*.html"), os.path.join(ROOT, base, "blog", "*", "index.html")]
        for pat in pats:
            for p in glob.glob(pat):
                p = os.path.normpath(p)
                if os.path.normpath(os.path.join(ROOT, base, "blog", "index.html")) == p:
                    continue  # blog hub is a listing page, not an article
                out.append(p)
    return sorted(out)


def read(p):
    with open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def selftest():
    bare = ("<!DOCTYPE html><html><head><title>Why Your Freezer Is Icing Up</title></head><body>\n"
            "<!--#include virtual=\"/includes/header-nav.inc\" -->\n<section class=\"hero\"><h1>Freezer icing</h1>"
            "<a href=\"/fridge-repair-london/\">nav-ish</a></section>\n<article>\n<p>No service links here.</p>\n</article>\n"
            "<!-- AUTO-SEO-V4-2026 -->\n<div><a href=\"/cold-room-repair-london/\">f</a><a href=\"/freezer-repair-london/\">g</a></div>\n</body></html>\n")
    assert len(contextual_core_links(bare)) == 0, contextual_core_links(bare)
    once, _ = process(bare, "blog/why-freezer-icing.html")
    assert once != bare and once.count(START) == 1 and "</article>" in once
    assert once.index(START) < once.index("</article>")
    assert len(contextual_core_links(once)) >= 2
    twice, _ = process(once, "blog/why-freezer-icing.html")
    assert twice == once, "not idempotent"
    ok = bare.replace("<p>No service links here.</p>", '<p><a href="/commercial-fridge-repair-london/">a</a> <a href="/cold-room-repair-london/">b</a></p>')
    same, _ = process(ok, "blog/x.html")
    assert same == ok, "touched a page that already has links"
    crlf = bare.replace("\n", "\r\n")
    c1, _ = process(crlf, "blog/x.html")
    assert "\r\n" in c1 and "\n" not in c1.replace("\r\n", ""), "mixed newlines"
    print("selftest OK")


def main():
    if "--selftest" in sys.argv:
        return selftest()
    check = "--check" in sys.argv
    lacking, changed = 0, 0
    for p in article_files():
        html = read(p)
        new, links = process(html, p)
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        if new != html:
            lacking += 1
            if not check:
                write(p, new)
                changed += 1
            print(("LACKS %d link(s): " % len(links) if check else "INJECTED (had %d): " % len(links)) + rel)
    total = len(article_files())
    print("blog articles scanned: %d | lacking links: %d | files changed: %d" % (total, lacking, changed))
    return 1 if (check and lacking) else 0


if __name__ == "__main__":
    sys.exit(main())
