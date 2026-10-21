#!/usr/bin/env python3
"""Contextual internal-link block from every blog page to all 9 money hubs (idempotent).

  python tools/blog_money_links.py --apply | --check | --selftest

Marker `<!-- CD-BLOG-MONEY-LINKS-V1 -->`. Anchors come from tools/money_data.py (exact + natural, with
the same-day / 24/7 / affordable modifiers); two anchor variants alternate per page so the blog does not
repeat one identical anchor everywhere. `commercial catering repair London` points at the
commercial-appliances hub (the canonical owner of that keyword) - never at the canonicalised duplicate.
Targets: blog/index.html + blog/<post>.html + blog/<post>/index.html in root and colddirect-public-html/.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import money_data as md  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MIRROR = ROOT / "colddirect-public-html"
START, END = "<!-- CD-BLOG-MONEY-LINKS-V1 -->", "<!-- /CD-BLOG-MONEY-LINKS-V1 -->"
BLOCK_RX = re.compile(re.escape(START) + r"[\s\S]*?" + re.escape(END) + r"(?:\r?\n)?")
INSERT_BEFORE = [r"<!-- CD-9-MONEY-KEYWORD-SILO-V47 -->", r"<footer\b", r"</body>"]

BLURB = {
    "commercial-freezer-repair-london": "walk-in and kitchen freezers",
    "commercial-fridge-repair-london": "prep, display and walk-in chillers",
    "cold-room-repair-london": "walk-in chiller and freezer rooms",
    "catering-repair-london": "restaurant and takeaway kitchens",
    "commercial-appliances-repair-london": "kitchen refrigeration and ice machines",
    "air-conditioning-repair-london": "offices, shops and server rooms",
    "cellar-cooler-repair-london": "pub and bar cellar cooling",
    "fridge-repair-london": "commercial fridges for shops and cafes",
    "freezer-repair-london": "commercial freezers for kitchens and shops",
}
TOPIC_FIRST = [("freezer", ["commercial-freezer-repair-london", "freezer-repair-london"]),
               ("fridge", ["commercial-fridge-repair-london", "fridge-repair-london"]),
               ("cold", ["cold-room-repair-london"]), ("storage", ["cold-room-repair-london"]),
               ("ice", ["commercial-appliances-repair-london"]), ("f-gas", ["air-conditioning-repair-london"])]


def targets():
    out = {}
    blog = ROOT / "blog"
    for p in sorted(blog.glob("*.html")):
        out["" if p.stem == "index" else p.stem] = None
    for base in (ROOT, MIRROR):
        b = base / "blog"
        if (b / "index.html").exists():
            out.setdefault("", None)
    pages = []
    for post in sorted(out):
        for base in (ROOT, MIRROR):
            b = base / "blog"
            if post == "":
                pages.append(("", b / "index.html"))
            else:
                pages += [(post, b / f"{post}.html"), (post, b / post / "index.html")]
    return [(post, p) for post, p in pages if p.exists()]


def order_for(post):
    first = []
    for key, hubs in TOPIC_FIRST:
        if key in post:
            first += [h for h in hubs if h not in first]
    return first + [h for h in md.HUB_ORDER if h not in first]


def variant_for(post):
    return sum(map(ord, post)) % 2


def block(post):
    v = variant_for(post)
    items = []
    for slug in order_for(post):
        d = md.MONEY[slug]
        items.append(f'<li><a href="/{slug}/">{md.esc(d["anchors"][v])}</a> &ndash; {md.esc(BLURB[slug])}</li>')
    return "\n".join([
        START,
        '<aside class="cd-blog-money-links" aria-label="Commercial refrigeration repair services in London" '
        'style="max-width:1140px;margin:32px auto;padding:20px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px">',
        '<h2 style="margin:0 0 10px;font-size:22px;color:#0a2540">Need help now? Same-day &amp; 24/7 emergency repair in London</h2>',
        '<p style="margin:0 0 10px;line-height:1.6;color:#334155">Cold Direct repairs commercial refrigeration and air conditioning only. '
        "Our London engineers offer a fixed diagnostic call-out and affordable, transparent quotes:</p>",
        '<ul style="margin:0 0 10px;padding-left:20px;line-height:1.8">',
        *items,
        "</ul>",
        f'<p style="margin:0;font-weight:700">Emergency line: <a href="{md.PHONE_TEL}">{md.PHONE_DISPLAY}</a></p>',
        "</aside>",
        END,
    ]) + "\n"


def apply_text(html, post):
    html = BLOCK_RX.sub("", html)
    for pat in INSERT_BEFORE:
        m = re.search(pat, html, re.I)
        if m:
            nl = "\r\n" if html.count("\r\n") * 2 > html.count("\n") else "\n"  # keep the file's own line-ending style
            return html[:m.start()] + block(post).replace("\n", nl) + html[m.start():]
    raise ValueError("no insertion point")


def run(write):
    pend = 0
    for post, p in targets():
        old = p.read_bytes().decode("utf-8")
        new = apply_text(old, post)
        if new != old:
            pend += 1
            print(("updated " if write else "pending ") + str(p.relative_to(ROOT)))
            if write:
                p.write_bytes(new.encode("utf-8"))
    print(("applied" if write else "pending") + f": {pend}")
    return pend


def selftest():
    page = "<html><body><h1>x</h1>\n<footer>f</footer></body></html>"
    a = apply_text(page, "commercial-freezer-ice-buildup-causes")
    assert apply_text(a, "commercial-freezer-ice-buildup-causes") == a and a.count(START) == 1
    for slug in md.HUB_ORDER:
        assert f'href="/{slug}/"' in a, slug
    assert 'href="/commercial-catering-repair-london/"' not in a
    assert a.index('href="/commercial-freezer-repair-london/"') < a.index('href="/cold-room-repair-london/"')
    assert md.PHONE_TEL in a and "domestic" not in a.lower()
    assert variant_for("a") in (0, 1)
    print("blog_money_links selftest OK;", len(targets()), "target files")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--selftest" in a:
        selftest()
    elif "--apply" in a:
        run(True)
    else:
        sys.exit(1 if run(False) else 0)
