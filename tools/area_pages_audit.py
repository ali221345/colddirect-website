#!/usr/bin/env python3
"""Audit London area / suburb landing pages listed in sitemap.xml.

Checks (read-only unless --fix):
  a) root <slug>.html, root <slug>/index.html, mirror <slug>.html and mirror <slug>/index.html
     exist and are byte-identical (the root <slug>.html is the source of truth)
  b) every area page is linked from /coverage/ AND from its parent hub page

--fix  : sync the copies and add missing links (idempotent, marker CD-AREA-LINKS-V1)
--check: exit 1 if anything would change / any problem remains
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIRROR = ROOT / "colddirect-public-html"
SITE = "https://www.colddirect.co.uk"
MARK = "<!-- CD-AREA-LINKS-V1 -->"
END_MARK = "<!-- /CD-AREA-LINKS-V1 -->"

SERVICES = (("commercial-refrigeration-repair-", "commercial refrigeration repair"),
            ("cold-room-repair-", "cold room repair"),
            ("commercial-freezer-repair-", "commercial freezer repair"),
            ("commercial-fridge-repair-", "commercial fridge repair"),
            ("freezer-room-repair-", "freezer room repair"),
            ("chiller-repair-", "chiller repair"),
            ("blast-chiller-repair-", "blast chiller repair"),
            ("display-cabinet-repair-", "display cabinet repair"),
            ("ice-machine-repair-", "ice machine repair"))
NORTH_HUB = {
    "cold-room-repair-": "cold-room-repair-north-london",
    "commercial-freezer-repair-": "commercial-freezer-repair-north-london",
    "commercial-fridge-repair-": "commercial-fridge-repair-north-london",
}
BOROUGH_HUB = "commercial-fridge-repair-london"
AREA_SUFFIX_OK = re.compile(r"-(north|central|east|south|west)-london$")


def sitemap_slugs():
    t = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    return [s.strip("/") for s in re.findall(r"<loc>https://www\.colddirect\.co\.uk(/[^<]*)</loc>", t)]


def split_slug(slug):
    for p, n in SERVICES:
        if slug.startswith(p):
            return n, slug[len(p):]
    return None, None


def area_slugs():
    out = []
    for s in sitemap_slugs():
        if not s or "/" in s:
            continue
        n, rest = split_slug(s)
        if n is None or rest in ("london", "servicing-london"):
            continue
        out.append(s)
    return out


def label(slug):
    _, rest = split_slug(slug)
    return " ".join(w.capitalize() for w in rest.split("-")).replace(" Of ", " of ")


def copies(slug):
    return {"root .html": ROOT / f"{slug}.html",
            "root /index.html": ROOT / slug / "index.html",
            "mirror .html": MIRROR / f"{slug}.html",
            "mirror /index.html": MIRROR / slug / "index.html"}


def source_pages():
    pages = {}
    for p in ROOT.glob("*.html"):
        pages["" if p.name == "index.html" else p.stem] = p
    for p in (ROOT / "blog").glob("*.html"):
        if p.name != "index.html":
            pages["blog/" + p.stem] = p
    for d in ROOT.iterdir():  # folder-only pages (no <slug>.html)
        f = d / "index.html"
        if d.is_dir() and f.exists() and d.name not in pages and d.name not in ("blog", "colddirect-public-html") \
                and not d.name.startswith((".", "node_modules")):
            pages[d.name] = f
    return pages


def link_re(slug):
    return re.compile(r'href="(?:' + re.escape(SITE) + r')?/' + re.escape(slug) + r'(?:/|\.html)?(?:[#?][^"]*)?"', re.I)


def inbound(slug, texts):
    rx = link_re(slug)
    return sorted(k for k, t in texts.items() if k != slug and rx.search(t))


def parent_hub(slug, pages):
    if AREA_SUFFIX_OK.search(slug):
        base = re.sub(r"-(north|central|east|south|west)-london$", "-london", slug)
        if base in pages and base != slug:
            return base
    for p, h in NORTH_HUB.items():
        if slug.startswith(p) and h in pages and h != slug:
            return h
    return BOROUGH_HUB


def add_links(text, target, slugs):
    items = {}
    for s in slugs:
        n, _ = split_slug(s)
        a = f"{n} {label(s)}"
        items[s] = f'<li><a href="/{s}/">{a[0].upper() + a[1:]}</a></li>'
    if MARK in text:
        m = re.search(re.escape(MARK) + r"(.*?)" + re.escape(END_MARK), text, re.S)
        body = m.group(1)
        new = [it for s, it in items.items() if f'href="/{s}/"' not in body]
        if not new:
            return text
        body2 = body.replace("</ul>", "\n".join(new) + "\n</ul>", 1)
        return text[: m.start(1)] + body2 + text[m.end(1):]
    block = (f'{MARK}<section class="section"><div class="wrap"><h2>More London Areas We Cover</h2>'
             f'<ul class="cd-area-links">\n' + "\n".join(items.values()) +
             f'\n</ul></div></section>{END_MARK}\n')
    for pat in (r'<section class="cta-band"', r"<!-- CD-9-MONEY-KEYWORD-SILO-V47 -->", r"<footer\b"):
        m = re.search(pat, text, re.I)
        if m:
            return text[: m.start()] + block + text[m.start():]
    raise SystemExit(f"no insertion point on {target}")


def main():
    fix = "--fix" in sys.argv
    check = "--check" in sys.argv
    pages = source_pages()
    texts = {k: v.read_text(encoding="utf-8", errors="replace") for k, v in pages.items()}
    areas = area_slugs()
    problems = 0
    changed = set()
    print(f"area pages in sitemap: {len(areas)}")

    for slug in areas:
        c = copies(slug)
        src = c["root .html"]
        if not src.exists():
            src = c["root /index.html"]  # folder-only legacy page: the folder index is the source of truth
        if not src.exists():
            print(f"MISSING root page: {slug}")
            problems += 1
            continue
        data = src.read_bytes()
        for name, p in c.items():
            if p == src:
                continue
            if not p.exists() or p.read_bytes() != data:
                state = "missing" if not p.exists() else "differs"
                print(f"COPY {state:8} {name}: {slug}")
                if fix:
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes(data)
                    changed.add(str(p.relative_to(ROOT)))
                else:
                    problems += 1

    rows = [(s, inbound(s, texts), parent_hub(s, pages)) for s in areas]
    print("\nslug | inbound sources | from coverage | from parent hub")
    for slug, ins, hub in rows:
        cov = "coverage" in ins
        hubl = hub in ins
        flag = "" if (cov and hubl and len(ins) >= 2) else "   <-- NEEDS LINKS"
        print(f"{slug} | {len(ins)} | {'Y' if cov else 'n'} | {hub}:{'Y' if hubl else 'n'}{flag}")

    need = {}
    for slug, ins, hub in rows:
        if "coverage" not in ins:
            need.setdefault("coverage", []).append(slug)
        if hub not in ins and hub != slug:
            need.setdefault(hub, []).append(slug)
    if not need:
        print("\nno missing coverage/hub links")
    for target, slugs in need.items():
        print(f"\nlinks to add on {target}: {', '.join(slugs)}")
        if not fix:
            problems += len(slugs)
            continue
        tp = pages[target]
        text = tp.read_bytes().decode("utf-8")
        crlf = "\r\n" in text
        new_text = add_links(text.replace("\r\n", "\n"), target, slugs)
        if crlf:
            new_text = new_text.replace("\n", "\r\n")
        tp.write_bytes(new_text.encode("utf-8"))
        changed.add(str(tp.relative_to(ROOT)))
        data = tp.read_bytes()
        for name, p in copies(target).items():
            if name != "root .html" and p.exists():
                p.write_bytes(data)
                changed.add(str(p.relative_to(ROOT)))
    if fix:
        print(f"\nfiles written: {len(changed)}")
    return 1 if (check and problems) else 0


if __name__ == "__main__":
    sys.exit(main())
