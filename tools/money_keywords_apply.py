#!/usr/bin/env python3
"""Apply the 9 money-hub keyword upgrade (idempotent).

  python tools/money_keywords_apply.py --check      read-only report (exit 1 if anything is pending)
  python tools/money_keywords_apply.py --apply      write auto-seo.aspx moneyMeta + all 4 HTML copies per hub
  python tools/money_keywords_apply.py --selftest   offline tests

What it touches (per slug, 4 copies: root .html, root /index.html, mirror .html, mirror /index.html):
  <title>, <meta name="description">, og:title, og:description, twitter:title, twitter:description
  + one `<!-- CD-MONEY-V1 -->` body block (H2/H3 + visible FAQ) placed before the FAQ/silo/footer.
and in auto-seo.aspx: moneyMeta[slug][0..1] (title/description) + extra OfferCatalog variations.
auto-seo.aspx stays the owner of title/description at runtime, so both sides always agree.
Never removes V4 blocks, never adds AUTO-SEO-LOCKED.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import money_data as md  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MIRROR = ROOT / "colddirect-public-html"
ASPX = ROOT / "auto-seo.aspx"

START, END = "<!-- CD-MONEY-V1 -->", "<!-- /CD-MONEY-V1 -->"
BLOCK_RX = re.compile(re.escape(START) + r"[\s\S]*?" + re.escape(END) + r"(?:\r?\n)?")
LIT = r'"(?:[^"\\]|\\.)*"'


def copies(slug):
    return [ROOT / f"{slug}.html", ROOT / slug / "index.html",
            MIRROR / f"{slug}.html", MIRROR / slug / "index.html"]


def read(p):
    return p.read_bytes().decode("utf-8")


def write(p, s):
    p.write_bytes(s.encode("utf-8"))


# ---------- auto-seo.aspx ----------
def aspx_line_rx(slug):
    return re.compile(r'(moneyMeta\["' + re.escape(slug) + r'"\] = new string\[\] \{ )(.*?)( \};)')


def aspx_new_literals(slug, old_literals):
    d = md.MONEY[slug]
    lits = list(old_literals)
    lits[0] = '"' + md.aspx_js_escape(d["title"]) + '"'
    lits[1] = '"' + md.aspx_js_escape(d["desc"]) + '"'
    have = {l.lower() for l in lits[4:]}
    for off in d["offers"]:
        lit = '"' + md.aspx_js_escape(off) + '"'
        if lit.lower() not in have:
            lits.append(lit)
    return lits


def apply_aspx(text, slug):
    rx = aspx_line_rx(slug)
    m = rx.search(text)
    if not m:
        raise SystemExit(f"moneyMeta[{slug}] not found in auto-seo.aspx")
    old = re.findall(LIT, m.group(2))
    new = aspx_new_literals(slug, old)
    return text[:m.start()] + m.group(1) + ", ".join(new) + m.group(3) + text[m.end():]


# ---------- HTML ----------
def meta_rx(attr, name):
    return re.compile(r'<meta\s+' + attr + r'="' + re.escape(name) + r'"\s+content="[^"]*"\s*/?>', re.I)


def set_meta(html, attr, name, value):
    tag = f'<meta {attr}="{name}" content="{md.esc(value)}">'
    rx = meta_rx(attr, name)
    if rx.search(html):
        return rx.sub(lambda m: tag, html, count=1)
    return None  # caller inserts


def apply_head(html, slug):
    d = md.MONEY[slug]
    html = re.sub(r"<title>[\s\S]*?</title>", lambda m: "<title>" + md.esc(d["title"]) + "</title>", html, count=1, flags=re.I)
    html = set_meta(html, "name", "description", d["desc"]) or html
    missing = []
    for attr, name, val in (("property", "og:title", d["title"]), ("property", "og:description", d["desc"]),
                            ("name", "twitter:title", d["title"]), ("name", "twitter:description", d["desc"])):
        out = set_meta(html, attr, name, val)
        if out is None:
            missing.append(f'<meta {attr}="{name}" content="{md.esc(val)}">')
        else:
            html = out
    if missing:
        anchor = meta_rx("name", "description").search(html)
        if anchor:
            html = html[:anchor.end()] + "\n" + "\n".join(missing) + html[anchor.end():]
    return html


CSS = ("<style>.cd-money-boost{max-width:1140px;margin:32px auto;padding:24px 20px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px}"
       ".cd-money-boost h2{margin:0 0 12px;color:#0a2540;font-size:24px}.cd-money-boost h3{margin:18px 0 6px;color:#0a2540;font-size:18px}"
       ".cd-money-boost p{margin:0 0 10px;line-height:1.6;color:#334155}.cd-money-boost details{margin:8px 0;background:#fff;border:1px solid #cbd5e1;border-radius:8px;padding:10px 14px}"
       ".cd-money-boost summary{font-weight:700;color:#0a2540;cursor:pointer}.cd-money-cta{font-weight:800}</style>")


def money_block(slug):
    d = md.MONEY[slug]
    kw = d["kw"]
    low = kw[0].lower() + kw[1:] if not kw.startswith(("London",)) else kw
    parts = [
        START,
        f'<section class="cd-money-boost" aria-label="{md.esc(kw)} - same day 24/7 emergency service">',
        CSS,
        f"<h2>{md.esc(kw)}: Same-Day, 24/7 Emergency Repairs &amp; Service</h2>",
        f"<p>{md.esc(d['intro'])}</p>",
        f"<p>{md.esc(d['semantic'])}</p>",
        f"<h3>Affordable {md.esc(low)} with a fixed diagnostic call-out</h3>",
        f"<p>{md.esc(d['cost'])}</p>",
        "<h3>London engineers, 24 hours a day, 7 days a week</h3>",
        f"<p>{md.esc(d['cover'])}</p>",
        f"<h3>{md.esc(kw)}: quick answers</h3>",
        f"<details><summary>Do you offer same-day {md.esc(low)}?</summary><p>{md.esc(d['faq1'])}</p></details>",
        f"<details><summary>How much does {md.esc(low)} cost?</summary><p>{md.esc(d['faq2'])}</p></details>",
        f'<p class="cd-money-cta">Emergency {md.esc(low)} service &ndash; call <a href="{md.PHONE_TEL}">{md.PHONE_DISPLAY}</a> now.</p>',
        "</section>",
        END,
    ]
    return "\n".join(parts) + "\n"


INSERT_BEFORE = [r"<!-- CD-CRO-FAQ-ACCORDION -->", r'<section[^>]*class="[^"]*cd-faq-accordion', r"<!-- CD-9-MONEY-KEYWORD-SILO-V47 -->",
                 r'<section[^>]*class="[^"]*cd-money-silo', r"<footer\b", r"</body>"]


def apply_block(html, slug):
    html = BLOCK_RX.sub("", html)
    for pat in INSERT_BEFORE:
        m = re.search(pat, html, re.I)
        if m:
            nl = "\r\n" if html.count("\r\n") * 2 > html.count("\n") else "\n"  # keep the file's own line-ending style (idempotent on CRLF checkouts)
            return html[:m.start()] + money_block(slug).replace("\n", nl) + html[m.start():]
    raise ValueError("no insertion point")


def apply_html(html, slug):
    return apply_block(apply_head(html, slug), slug)


# ---------- check ----------
def pending_html(html, slug):
    return [] if apply_html(html, slug) == html else ["differs"]


def run(apply_changes):
    pend = 0
    aspx = ASPX.read_bytes().decode("utf-8")
    new_aspx = aspx
    for slug in md.HUB_ORDER:
        new_aspx = apply_aspx(new_aspx, slug)
    if new_aspx != aspx:
        pend += 1
        print("auto-seo.aspx moneyMeta: pending")
        if apply_changes:
            ASPX.write_bytes(new_aspx.encode("utf-8"))
    else:
        print("auto-seo.aspx moneyMeta: up to date")
    for slug in md.HUB_ORDER:
        for p in copies(slug):
            if not p.exists():
                print("MISSING", p)
                pend += 1
                continue
            old = read(p)
            new = apply_html(old, slug)
            if new != old:
                pend += 1
                print(("updated " if apply_changes else "pending ") + str(p.relative_to(ROOT)))
                if apply_changes:
                    write(p, new)
    print(f"{'applied' if apply_changes else 'pending'}: {pend}")
    return pend


def selftest():
    slug = "cold-room-repair-london"
    page = ('<html><head><title>Old</title>\n<meta name="description" content="old">\n'
            '<meta property="og:title" content="old og">\n</head><body><h1>x</h1>\n'
            '<section class="cd-faq-accordion"><h2>FAQ</h2></section>\n<footer>f</footer></body></html>')
    once = apply_html(page, slug)
    twice = apply_html(once, slug)
    assert once == twice, "not idempotent"
    assert once.count(START) == 1 and once.count("<title>") == 1
    assert md.MONEY[slug]["title"] in once and 'og:description' in once and 'twitter:title' in once
    assert once.index(START) < once.index('class="cd-faq-accordion"')
    assert md.MONEY[slug]["semantic"] in once, "semantic word-order copy missing from visible body"
    assert once.count(md.MONEY[slug]["semantic"]) == 1, "semantic copy must not be duplicated"
    assert md.PHONE_TEL in once and "domestic" not in once.lower()
    line = 'x\r\n    moneyMeta["%s"] = new string[] { "T \\u2013 old", "D", "Name", "Type", "Cold room repair London" };\r\n' % slug
    a1 = apply_aspx(line, slug)
    assert apply_aspx(a1, slug) == a1 and "\\u2013" not in a1.split("{")[1].split(",")[0]
    assert a1.endswith("\r\n") and md.MONEY[slug]["offers"][0] in a1
    print("money_keywords_apply selftest OK")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--selftest" in a:
        selftest()
    elif "--apply" in a:
        run(True)
    else:
        sys.exit(1 if run(False) else 0)
