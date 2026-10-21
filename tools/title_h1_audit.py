#!/usr/bin/env python3
"""List <title>/<h1> of every sitemap page and report duplicates (titles/h1s shared by >1 page).

Usage: python tools/title_h1_audit.py [--area] [--check]
  --area  only report duplicates that involve an area page (see area_pages_audit.area_slugs)
  --check exit 1 if such duplicates exist
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import area_pages_audit as ap  # noqa: E402

ROOT = ap.ROOT


def page_file(slug):
    for f in (ROOT / f"{slug}.html", ROOT / slug / "index.html"):
        if f.exists():
            return f
    return None


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip().lower()


def info(f):
    t = f.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"<title>(.*?)</title>", t, re.S | re.I)
    h = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S | re.I)
    return (norm(m.group(1)) if m else ""), (norm(h.group(1)) if h else "")


def main():
    area_only = "--area" in sys.argv
    areas = set(ap.area_slugs())
    titles, h1s = defaultdict(list), defaultdict(list)
    for s in ap.sitemap_slugs():
        if not s or s.startswith("blog"):
            continue
        f = page_file(s)
        if not f:
            continue
        t, h = info(f)
        titles[t].append(s)
        h1s[h].append(s)
    bad = 0
    for kind, d in (("title", titles), ("h1", h1s)):
        for k, v in d.items():
            if len(v) > 1 and (not area_only or any(x in areas for x in v)):
                bad += 1
                print(f"DUPLICATE {kind}: {k!r}\n    {', '.join(v)}")
    print(f"area pages: {len(areas)} | duplicate groups involving area pages: {bad}")
    return 1 if ("--check" in sys.argv and bad) else 0


if __name__ == "__main__":
    sys.exit(main())
