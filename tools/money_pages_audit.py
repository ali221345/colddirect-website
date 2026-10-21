#!/usr/bin/env python3
"""Read-only audit of the homepage + 9 core money pages (root copy): title / description / H1 / headings / FAQ / schema /
og + twitter image / audio / modifiers. Usage: python tools/money_pages_audit.py [--json]"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = [
    ("index.html", "commercial refrigeration repair london"),
    ("fridge-repair-london.html", "fridge repair london"),
    ("freezer-repair-london.html", "freezer repair london"),
    ("commercial-fridge-repair-london.html", "commercial fridge repair london"),
    ("commercial-freezer-repair-london.html", "commercial freezer repair london"),
    ("catering-repair-london.html", "catering repair london"),
    ("commercial-appliances-repair-london.html", "commercial catering repair london"),
    ("cold-room-repair-london.html", "cold room repair london"),
    ("air-conditioning-repair-london.html", "air conditioning repair london"),
    ("cellar-cooler-repair-london.html", "cellar repair london"),
]
MODS = ["repairs", "service", "services", "emergency", "same day", "24 hour", "24/7", "affordable", "fixed", "diagnostic", "call-out", "07983 759320"]


def txt(s):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", s)).split())


def audit(path):
    t = open(os.path.join(ROOT, path), encoding="utf-8", errors="replace").read()
    g = lambda p, f=re.I | re.S: re.search(p, t, f)
    title = txt(g(r"<title[^>]*>(.*?)</title>").group(1)) if g(r"<title[^>]*>(.*?)</title>") else ""
    desc = (g(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']') or [None, ""])[1] if g(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']') else ""
    h1 = [txt(x) for x in re.findall(r"<h1\b[^>]*>(.*?)</h1>", t, re.I | re.S)]
    types = set()
    for blk in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', t, re.I | re.S):
        try:
            d = json.loads(blk)
        except ValueError:
            types.add("INVALID")
            continue
        stack = [d]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                ty = x.get("@type")
                for tt in (ty if isinstance(ty, list) else [ty]):
                    if tt:
                        types.add(tt)
                stack += list(x.values())
            elif isinstance(x, list):
                stack += x
    low = html.unescape(re.sub(r"<[^>]+>", " ", t)).lower()
    return {
        "page": path, "title": title, "title_len": len(title), "desc_len": len(html.unescape(desc)), "h1": h1,
        "h2": len(re.findall(r"<h2\b", t, re.I)), "h3": len(re.findall(r"<h3\b", t, re.I)),
        "faq": bool(re.search(r"FAQPage", t)), "types": sorted(types),
        "og_image": bool(re.search(r'property=["\']og:image["\']', t)), "tw_image": bool(re.search(r'name=["\']twitter:image["\']', t)),
        "audio": "<audio" in t, "speakable": "SpeakableSpecification" in t,
        "mods": [m for m in MODS if m in low or m in title.lower() or m in html.unescape(desc).lower()],
    }


def main():
    rows = [audit(p) | {"kw": kw} for p, kw in PAGES]
    if "--json" in sys.argv:
        print(json.dumps(rows, indent=1))
        return 0
    for r in rows:
        kw_t = r["kw"] in r["title"].lower()
        print("%-42s title(%d)%s | desc %d | h1 %d | h2 %d h3 %d | faq %s | og %s tw %s | audio %s speak %s" % (
            r["page"], r["title_len"], "*" if kw_t else "!", r["desc_len"], len(r["h1"]), r["h2"], r["h3"],
            "Y" if r["faq"] else "-", "Y" if r["og_image"] else "-", "Y" if r["tw_image"] else "-",
            "Y" if r["audio"] else "-", "Y" if r["speakable"] else "-"))
        print("    T: %s" % r["title"])
        print("    H1: %s" % " / ".join(r["h1"]))
        print("    types: %s | mods: %s" % (",".join(r["types"]), ",".join(r["mods"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
