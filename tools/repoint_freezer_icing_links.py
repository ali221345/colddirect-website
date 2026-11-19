#!/usr/bin/env python3
"""Repoint every internal link from /blog/why-commercial-freezer-icing-up/
to /blog/commercial-freezer-ice-buildup-causes/.

Rules:
- blog/index.html (root + mirror): delete the whole retire card <article>.
- A mesh <li> that links the retire URL is DELETED when the same file already
  links to the survivor (avoids duplicate list entries), otherwise REPOINTED.
- Any remaining href to the retire URL is repointed.
- The retire post's own 4 files are skipped (they are deleted separately).
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
RETIRE = "/blog/why-commercial-freezer-icing-up/"
SURVIVOR = "/blog/commercial-freezer-ice-buildup-causes/"
SKIP_DIRS = {"node_modules", ".git", "logs", "backups", "seo-audit", "__pycache__", "_wa_src", "mnt"}
RETIRE_FILES = {
    "blog/why-commercial-freezer-icing-up.html",
    "blog/why-commercial-freezer-icing-up/index.html",
    "colddirect-public-html/blog/why-commercial-freezer-icing-up.html",
    "colddirect-public-html/blog/why-commercial-freezer-icing-up/index.html",
}

LI_RE = re.compile(
    r'\s*<li><a href="/blog/why-commercial-freezer-icing-up/">[^<]*</a></li>', re.I
)
CARD_RE = re.compile(
    r'\s*<article class="card">(?:(?!</article>).)*?/blog/why-commercial-freezer-icing-up/(?:(?!</article>).)*?</article>',
    re.S,
)
HREF_RE = re.compile(r'href="/blog/why-commercial-freezer-icing-up/"')

changed = []
for path in sorted(ROOT.rglob("*.html")):
    rel = path.relative_to(ROOT).as_posix()
    if rel in RETIRE_FILES:
        continue
    if any(part in SKIP_DIRS for part in path.parts):
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    if "why-commercial-freezer-icing-up" not in text:
        continue
    orig = text
    notes = []

    # 1) blog/index.html retire card
    new_text, n = CARD_RE.subn("", text)
    if n:
        notes.append(f"card removed x{n}")
        text = new_text

    # 2) mesh <li>: delete if survivor already linked, else repoint
    def li_sub(m):
        return "" if SURVIVOR in text else m.group(0).replace(RETIRE, SURVIVOR)
    new_text, n = LI_RE.subn(li_sub, text)
    if n:
        notes.append(f"mesh li {'removed' if SURVIVOR in text else 'repointed'} x{n}")
        text = new_text

    # 3) any remaining hrefs
    new_text, n = HREF_RE.subn(f'href="{SURVIVOR}"', text)
    if n:
        notes.append(f"href repointed x{n}")
        text = new_text

    if "why-commercial-freezer-icing-up" in text:
        leftover = [l.strip()[:100] for l in text.splitlines() if "why-commercial-freezer-icing-up" in l]
        print(f"LEFTOVER {rel}: {leftover[:3]}")
        sys.exit(1)

    if text != orig:
        path.write_text(text, encoding="utf-8")
        changed.append((rel, "; ".join(notes)))

for rel, note in changed:
    print(f"{rel}: {note}")
print(f"\n{len(changed)} files updated.")
