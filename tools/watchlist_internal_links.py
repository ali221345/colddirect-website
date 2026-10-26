#!/usr/bin/env python3
"""Keep the six indexing-watchlist pages linked from the homepage and their footers.

The same marked blocks are written to every deployable root/public HTML copy.
Use --check in CI or before deployment; it exits 1 without writing when drift exists.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
CHECK = "--check" in sys.argv
HOME_MARKER = "<!-- CD-WATCHLIST-HOME-LINKS-V1 -->"
FOOTER_MARKER = "<!-- CD-WATCHLIST-FOOTER-LINKS-V1 -->"
TARGETS = [
    ("/cold-room-repair-harrow/", "Cold room repair Harrow"),
    ("/cold-room-repair-palmers-green/", "Cold room repair Palmers Green"),
    ("/cold-room-repair-southgate/", "Cold room repair Southgate"),
    ("/cold-room-repair-wood-green/", "Cold room repair Wood Green"),
    ("/commercial-fridge-repair-enfield/", "Commercial fridge repair Enfield"),
    ("/commercial-fridge-repair-central-london/", "Commercial fridge repair Central London"),
]
HOME_SLUGS = {href.strip("/") for href, _ in TARGETS} - {"commercial-fridge-repair-enfield"}

HOME_BLOCK = HOME_MARKER + """
<section class="section" aria-label="Local commercial refrigeration repair">
  <div class="wrap">
    <h2>Local commercial refrigeration repair across London</h2>
    <p>Book a local commercial engineer for <a href="/cold-room-repair-harrow/">cold room repair in Harrow</a>, <a href="/cold-room-repair-palmers-green/">cold room repair in Palmers Green</a>, <a href="/cold-room-repair-southgate/">cold room repair in Southgate</a>, <a href="/cold-room-repair-wood-green/">cold room repair in Wood Green</a>, or <a href="/commercial-fridge-repair-central-london/">commercial fridge repair in Central London</a>.</p>
  </div>
</section>
<!-- /CD-WATCHLIST-HOME-LINKS-V1 -->
"""
FOOTER_BLOCK = FOOTER_MARKER + """
<nav class="cd-watchlist-footer-links" aria-label="Local commercial refrigeration repair">
  <h2>Local repair services</h2>
  <ul>
""" + "".join(f'    <li><a href="{href}">{anchor}</a></li>\n' for href, anchor in TARGETS) + """  </ul>
</nav>
<!-- /CD-WATCHLIST-FOOTER-LINKS-V1 -->
"""


def read(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def write(path, text):
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def variants(slug):
    relative = ["index.html"] if slug == "index" else [f"{slug}.html", f"{slug}/index.html"]
    paths = []
    for rel in relative:
        paths.extend((ROOT / rel, ROOT / "colddirect-public-html" / rel))
    return [path for path in paths if path.exists()]


def add_home_links(text):
    if HOME_MARKER in text:
        return text
    insertion = text.find('<section class="cta-band">')
    if insertion < 0:
        raise RuntimeError("Homepage CTA insertion point not found")
    return text[:insertion] + HOME_BLOCK + text[insertion:]


def add_footer_links(text):
    if FOOTER_MARKER in text:
        return text
    closing = text.lower().find("</footer>")
    if closing >= 0:
        return text[:closing] + FOOTER_BLOCK + text[closing:]
    insertion = text.find("<!-- CD-VOICE-BAR-V1 -->")
    if insertion < 0:
        insertion = text.lower().find("</body>")
    if insertion < 0:
        raise RuntimeError("Footer/body insertion point not found")
    footer = '<footer class="site-footer"><div class="wrap">' + FOOTER_BLOCK + "</div></footer>\n"
    return text[:insertion] + footer + text[insertion:]


def process(slug):
    paths = variants(slug)
    if not paths:
        raise RuntimeError(f"No deployable copies found for {slug}")
    baseline = read(paths[0])
    for path in paths[1:]:
        if read(path) != baseline:
            raise RuntimeError(f"Copies differ before edit: {path.relative_to(ROOT)}")
    updated = add_footer_links(add_home_links(baseline) if slug == "index" else baseline)
    changed = updated != baseline
    if changed and not CHECK:
        for path in paths:
            write(path, updated)
    print(f"{'WOULD CHANGE' if CHECK and changed else 'UPDATED' if changed else 'OK'} {slug}: {len(paths)} copies")
    return changed


def main():
    changed = [slug for slug in ["index"] + sorted(HOME_SLUGS | {"commercial-fridge-repair-enfield"}) if process(slug)]
    print(f"{len(changed)} page(s) {'need updates' if CHECK else 'updated'}")
    return 1 if CHECK and changed else 0


if __name__ == "__main__":
    sys.exit(main())
