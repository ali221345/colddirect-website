#!/usr/bin/env python3
"""Idempotent contextual internal-link boost for pages Google has not indexed yet.

Targets
  appliances : /commercial-appliances-repair-london/   anchor "commercial appliances repair London"
  enfield    : /commercial-fridge-repair-enfield/      anchor "commercial fridge repair Enfield"

For every source page the link block is added ONLY when
  * its marker comment (<!-- CD-LINK-BOOST-<KEY> -->) is not already present, AND
  * the page has no link to the target URL whose visible text already equals the anchor.
The result is written to the root <slug>.html, <slug>/index.html and the colddirect-public-html mirror
(whichever copies exist). Running it twice changes nothing.

Usage: python tools/internal_link_boost.py [--check]
Exit code with --check: 1 when something would change.
"""
import html as htmllib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK = "--check" in sys.argv

TARGETS = {
    "appliances": {
        "href": "/commercial-appliances-repair-london/",
        "anchor": "commercial appliances repair London",
        "page": ('Running a busy kitchen? Our <a href="{href}">{anchor}</a> team looks after fridges, freezers, '
                 'cold rooms, blast chillers and ice machines in one 24/7 call-out.'),
        "blog": ('If a breakdown affects more than one machine in your kitchen, our <a href="{href}">{anchor}</a> '
                 'service covers fridges, freezers, cold rooms, blast chillers and ice machines on a single visit.'),
    },
    "enfield": {
        "href": "/commercial-fridge-repair-enfield/",
        "anchor": "commercial fridge repair Enfield",
        "page": ('Based in North London? Cold Direct is headquartered at 27 Felixstowe Road, Enfield N9 0DX, so our '
                 '<a href="{href}">{anchor}</a> service starts close to home for Enfield restaurants, pubs and shops.'),
        "blog": ('Based in Enfield or elsewhere in North London? See our <a href="{href}">{anchor}</a> page for '
                 'how we cover local restaurants, pubs and shops from our Enfield head office.'),
    },
}

# (kind, slug-or-blog-slug, [target keys])
PAGES = [
    ("page", "index", ["appliances", "enfield"]),
    ("page", "catering-repair-london", ["appliances"]),
    ("page", "commercial-catering-repair-london", ["appliances"]),
    ("page", "commercial-fridge-repair-london", ["appliances", "enfield"]),
    ("page", "fridge-repair-london", ["enfield"]),
    ("page", "cold-room-repair-london", ["enfield"]),
    # North London / area coverage sections
    ("page", "coverage", ["enfield"]),
    ("page", "commercial-fridge-repair-north-london", ["enfield"]),
    ("page", "cold-room-repair-north-london", ["enfield"]),
    ("page", "freezer-room-repair-north-london", ["enfield"]),
    # top commercial catering blog posts
    ("blog", "prevent-commercial-fridge-breakdown", ["appliances"]),
    ("blog", "commercial-freezer-temperature-guide", ["appliances"]),
    ("blog", "commercial-fridge-repair-cost-london", ["appliances"]),
]

IN_BODY_REQUIRED = {("index", "appliances")}

changed = []
report = []


def read(p):
    with open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def write(p, t):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(t)


def marker(key):
    return f"<!-- CD-LINK-BOOST-{key.upper()} -->"


def has_exact_anchor(text, key):
    t = TARGETS[key]
    want = t["anchor"].lower()
    pat = re.compile(r'<a\b[^>]*href="(?:https://www\.colddirect\.co\.uk)?%s/?"[^>]*>(.*?)</a>' % re.escape(t["href"].rstrip("/")), re.I | re.S)
    for m in pat.finditer(text):
        vis = re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", "", m.group(1)))).strip().lower()
        if vis == want:
            return True
    return False


def variants(kind, slug):
    if kind == "blog":
        rel = [f"blog/{slug}.html", f"blog/{slug}/index.html"]
    elif slug == "index":
        rel = ["index.html"]
    else:
        rel = [f"{slug}.html", f"{slug}/index.html"]
    out = []
    for r in rel:
        out.append(ROOT / r)
        out.append(ROOT / "colddirect-public-html" / r)
    return [p for p in out if p.exists()]


def insert_page_block(text, key, sentence):
    block = (f"{marker(key)}\n  <section class=\"section\"><div class=\"wrap\"><p class=\"cd-link-boost\">"
             f"{sentence}</p></div></section>\n  ")
    for pat in (r'<section class="cta-band">', r"<!-- CD-9-MONEY-KEYWORD-SILO-V47 -->", r"<footer\b"):
        m = re.search(pat, text)
        if m:
            return text[: m.start()] + block + text[m.start():]
    raise SystemExit("no insertion point found")


def insert_blog_block(text, key, sentence):
    ms = list(re.finditer(r"</article>", text, re.I))
    if ms:
        i = ms[-1].start()
        block = f"      {marker(key)}\n      <p class=\"cd-link-boost\">{sentence}</p>\n    "
        return text[:i] + block + text[i:]
    for pat in (r"<!-- CD-9-MONEY-KEYWORD-SILO-V47 -->", r"<footer\b", r"</body>"):
        m = re.search(pat, text, re.I)
        if m:
            block = (f"{marker(key)}\n<section class=\"section\"><div class=\"wrap\"><p class=\"cd-link-boost\">"
                     f"{sentence}</p></div></section>\n")
            return text[: m.start()] + block + text[m.start():]
    raise SystemExit("blog: no insertion point")


def process(kind, slug, keys):
    files = variants(kind, slug)
    if not files:
        report.append(f"MISSING  {kind}:{slug}")
        return
    base = read(files[0])
    for p in files[1:]:
        if read(p) != base:
            raise SystemExit(f"copies differ before edit: {slug} ({p.relative_to(ROOT)})")
    text = base
    added = []
    for key in keys:
        if marker(key) in text:
            continue
        # the homepage already links the hub with this anchor, but only from footer/link lists: it still gets one in-body link
        if has_exact_anchor(text, key) and (slug, key) not in IN_BODY_REQUIRED:
            continue
        t = TARGETS[key]
        sentence = t["blog" if kind == "blog" else "page"].format(href=t["href"], anchor=t["anchor"])
        text = insert_blog_block(text, key, sentence) if kind == "blog" else insert_page_block(text, key, sentence)
        added.append(key)
    state = ", ".join(f"{k}: " + ("added" if k in added else "already linked") for k in keys)
    report.append(f"{'CHANGE' if added else 'ok    '}  {kind}:{slug} ({len(files)} copies) {state}")
    if added:
        changed.append(slug)
        if not CHECK:
            for p in files:
                write(p, text)


def main():
    for kind, slug, keys in PAGES:
        process(kind, slug, keys)
    print("\n".join(report))
    print(f"{'would change' if CHECK else 'changed'}: {len(changed)} page(s)")
    return 1 if (CHECK and changed) else 0


if __name__ == "__main__":
    sys.exit(main())
