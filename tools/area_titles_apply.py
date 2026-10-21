#!/usr/bin/env python3
"""Apply the areaMeta title/description rules of auto-seo.aspx (area pages + de-duplicated service pages)
to every HTML copy of each page. Titles must be 50-65 chars, descriptions <= 160.

auto-seo.aspx is the single source of truth (areaMeta["slug"] = { title, description }).
Writes root <slug>.html, root <slug>/index.html, mirror <slug>.html and mirror <slug>/index.html.
Idempotent. --check exits 1 if anything would change.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import area_pages_audit as ap  # noqa: E402

ROOT = ap.ROOT
ASPX = ROOT / "auto-seo.aspx"
RX = re.compile(r'areaMeta\["([^"]+)"\]\s*=\s*new string\[\]\s*\{\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*\}\s*;')


def unescape(s):
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s).replace('\\"', '"')


def load():
    t = ASPX.read_text(encoding="utf-8")
    return {m.group(1): (unescape(m.group(2)), unescape(m.group(3))) for m in RX.finditer(t)}


def apply(text, title, desc):
    new = re.sub(r"<title>[\s\S]*?</title>", lambda m: f"<title>{title}</title>", text, count=1, flags=re.I)
    meta = f'<meta name="description" content="{desc}">'
    rxd = re.compile(r'<meta\s+name=["\']description["\'][^>]*>', re.I)
    if rxd.search(new):
        new = rxd.sub(lambda m: meta, new, count=1)
    else:
        new = re.sub(r"</title>", lambda m: "</title>\n  " + meta, new, count=1, flags=re.I)
    return new


def main():
    check = "--check" in sys.argv
    meta = load()
    print(f"areaMeta rules: {len(meta)}")
    pending = 0
    warned = 0
    for slug, (title, desc) in sorted(meta.items()):
        if len(desc) > 160:
            print(f"WARN description {len(desc)} chars (>160): {slug}")
        if not 50 <= len(title) <= 65:
            print(f"WARN title {len(title)} chars (target 50-65): {slug}")
            warned += 1
        for name, p in ap.copies(slug).items():
            if not p.exists():
                continue
            raw = p.read_bytes().decode("utf-8")
            new = apply(raw, title, desc)
            if new != raw:
                pending += 1
                if not check:
                    p.write_bytes(new.encode("utf-8"))
    print(f"files {'to change' if check else 'changed'}: {pending}")
    return 1 if (check and (pending or warned)) else 0


if __name__ == "__main__":
    sys.exit(main())
