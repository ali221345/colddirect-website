#!/usr/bin/env python3
"""Startup guard for Cold Direct. Read-only. Run this before any SEO or redirect edit.

Prints the locked milestones and exits 0 when they are still intact, so a new
session skips work that is already live. Exits 1 when a locked artifact is
missing: that is a regression to repair, not a reason to rebuild the milestone.

    python tools/check_locked_state.py
    python tools/check_locked_state.py --selftest
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COOLDOWN_UNTIL = "2026-10-31"

# Live-audited sitemap size on https://www.colddirect.co.uk (all <loc> URLs
# verified 200 OK, self-canonical, zero redirect hops on 2026-10-31).
SITEMAP_URL_COUNT = 131

# (url path, repo file, markers that must still be in that file)
PAGES = [
    ("/", "index.html", ("CD-HERO-KEYWORD-MATRIX", "CD-9-MONEY-KEYWORD-SILO-V47", "CD-HOMEPAGE-6-BLOG-HUB", "#business")),
    ("/fridge-repair-london/", "fridge-repair-london/index.html", ("CD-HERO-KEYWORD-MATRIX", "CD-9-MONEY-TECH-MATRIX-V47", "CD-9-MONEY-KEYWORD-SILO-V47", "#business")),
    ("/freezer-repair-london/", "freezer-repair-london/index.html", ("CD-HERO-KEYWORD-MATRIX", "CD-9-MONEY-TECH-MATRIX-V47", "CD-9-MONEY-KEYWORD-SILO-V47", "#business")),
    ("/commercial-fridge-repair-london/", "commercial-fridge-repair-london/index.html", ("CD-HERO-KEYWORD-MATRIX", "CD-9-MONEY-TECH-MATRIX-V47", "CD-9-MONEY-KEYWORD-SILO-V47", "#business")),
    ("/commercial-freezer-repair-london/", "commercial-freezer-repair-london/index.html", ("CD-HERO-KEYWORD-MATRIX", "CD-9-MONEY-TECH-MATRIX-V47", "CD-9-MONEY-KEYWORD-SILO-V47", "#business")),
    ("/cold-room-repair-london/", "cold-room-repair-london/index.html", ("CD-HERO-KEYWORD-MATRIX", "CD-9-MONEY-TECH-MATRIX-V47", "CD-9-MONEY-KEYWORD-SILO-V47", "#business")),
    ("/catering-repair-london/", "catering-repair-london/index.html", ("CD-HERO-KEYWORD-MATRIX", "CD-9-MONEY-TECH-MATRIX-V47", "CD-9-MONEY-KEYWORD-SILO-V47", "#business")),
    ("/commercial-appliances-repair-london/", "commercial-appliances-repair-london/index.html", ("CD-HERO-KEYWORD-MATRIX", "CD-9-MONEY-TECH-MATRIX-V47", "CD-9-MONEY-KEYWORD-SILO-V47", "#business")),
    ("/air-conditioning-repair-london/", "air-conditioning-repair-london/index.html", ("CD-HERO-KEYWORD-MATRIX", "CD-9-MONEY-TECH-MATRIX-V47", "CD-9-MONEY-KEYWORD-SILO-V47", "#business")),
    ("/cellar-cooler-repair-london/", "cellar-cooler-repair-london/index.html", ("CD-HERO-KEYWORD-MATRIX", "CD-9-MONEY-TECH-MATRIX-V47", "CD-9-MONEY-KEYWORD-SILO-V47", "#business")),
]

# Bare slug -> somewhere else, on purpose. A self-slash rule here would be a second hop.
LEGACY_ELSEWHERE = (
    ("walk-in-cold-room-repair-london", "/cold-room-repair-london/"),
    ("cold-room-repairs-london", "/cold-room-repair-london/"),
    ("commercial-dishwasher-repair-london", "/commercial-catering-repair-london/"),
    ("about", "/about-us/"),
    ("news", "/blog/"),
)

PIPELINES = (
    "auto-seo.aspx",
    ".github/workflows/auto-seo-nightly.yml",
    ".github/workflows/site-backup-48h.yml",
    "tools/backup_site.py",
    "tools/live_production_audit.py",
    "tools/seo_integrity_check.py",
)


def page_gaps(text: str, markers: tuple[str, ...]) -> list[str]:
    return [m for m in markers if m not in text]


def sitemap_gaps(text: str) -> list[str]:
    locs = len(re.findall(r"<loc>", text))
    if locs != SITEMAP_URL_COUNT:
        return ["sitemap.xml has %d <loc> URLs, want %d" % (locs, SITEMAP_URL_COUNT)]
    return []


def bare_slugs(web_config: str) -> list[str]:
    return re.findall(r'<rule name="Bare slug to slash: ([a-z0-9-]+)"', web_config)


def redirect_gaps(htaccess: str, web_config: str) -> list[str]:
    gaps = []
    slugs = bare_slugs(web_config)
    if len(slugs) != 102 or len(set(slugs)) != 102:
        gaps.append("web.config has %d bare-slug rules, want 102 unique" % len(slugs))
    for slug in slugs:
        rule = "RewriteRule ^%s$ /%s/ [R=301,L]" % (slug, slug)
        if rule not in htaccess:
            gaps.append(".htaccess missing " + rule)
        if ('<match url="^%s$" ignoreCase="true" />' % slug) not in web_config:
            gaps.append("web.config missing match for " + slug)
    for slug, target in LEGACY_ELSEWHERE:
        if target not in htaccess or target not in web_config:
            gaps.append("legacy target %s missing for %s" % (target, slug))
        self_rule = "RewriteRule ^%s$ /%s/ [R=301,L]" % (slug, slug)
        if self_rule in htaccess:
            gaps.append("self-slash rule would chain " + slug)
    return gaps


def pipeline_gaps(root: Path) -> list[str]:
    gaps = []
    for rel in PIPELINES:
        if not (root / rel).is_file():
            gaps.append("missing " + rel)
    aspx = root / "auto-seo.aspx"
    if aspx.is_file():
        text = aspx.read_text(encoding="utf-8", errors="replace")
        if "V4.9" not in text:
            gaps.append("auto-seo.aspx is not V4.9")
        if "ContentDiffers" not in text:
            gaps.append("auto-seo.aspx missing ContentDiffers")
    return gaps


def check(root: Path = ROOT) -> list[str]:
    problems = []
    for url, rel, markers in PAGES:
        path = root / rel
        if not path.is_file():
            problems.append("missing %s (%s)" % (rel, url))
            continue
        gaps = page_gaps(path.read_text(encoding="utf-8", errors="replace"), markers)
        if gaps:
            problems.append("%s missing %s" % (url, ", ".join(gaps)))
    ht = root / ".htaccess"
    wc = root / "web.config"
    sm = root / "sitemap.xml"
    if not sm.is_file():
        problems.append("missing sitemap.xml")
    else:
        problems.extend(sitemap_gaps(sm.read_text(encoding="utf-8", errors="replace")))
    if not ht.is_file() or not wc.is_file():
        problems.append("missing .htaccess or web.config")
    else:
        problems.extend(redirect_gaps(ht.read_text(encoding="utf-8"), wc.read_text(encoding="utf-8")))
        mirror_wc = root / "colddirect-public-html" / "web.config"
        if mirror_wc.is_file() and bare_slugs(mirror_wc.read_text(encoding="utf-8")) != bare_slugs(wc.read_text(encoding="utf-8")):
            problems.append("web.config mirror does not match root")
    problems.extend(pipeline_gaps(root))
    return problems


def report(problems: list[str]) -> str:
    lines = [
        "LOCKED #1 money pages + homepage: markers present. SKIP title, H1 and meta description edits until %s." % COOLDOWN_UNTIL,
        "LOCKED #2 trailing-slash 301s (87e96a0, 5aad3d0): 102 bare-slug rules plus the legacy single-hop aliases. SKIP .htaccess and web.config redirect edits.",
        "LOCKED #3 pipelines: auto-seo.aspx V4.9, 24h nightly, 48h backup, live_production_audit.py. SKIP rebuilding them.",
        "LOCKED #4 sitemap.xml: exactly %d <loc> URLs (live-audited 2026-10-31, all 200 OK + self-canonical + zero redirects). SKIP sitemap edits until %s." % (SITEMAP_URL_COUNT, COOLDOWN_UNTIL),
    ]
    if problems:
        lines.append("REGRESSION: %d locked artifact(s) missing. Repair these; do not rebuild the milestone from scratch." % len(problems))
        lines.extend("  - " + p for p in problems)
    else:
        lines.append("check_locked_state: ALL LOCKS INTACT")
    return "\n".join(lines)


def selftest() -> None:
    assert page_gaps("CD-HERO-KEYWORD-MATRIX #business", ("CD-HERO-KEYWORD-MATRIX", "#business")) == []
    assert page_gaps("x", ("CD-HERO-KEYWORD-MATRIX",)) == ["CD-HERO-KEYWORD-MATRIX"]
    assert sitemap_gaps("<loc>a</loc>" * SITEMAP_URL_COUNT) == []
    assert any("want %d" % SITEMAP_URL_COUNT in g for g in sitemap_gaps("<loc>a</loc>" * (SITEMAP_URL_COUNT - 1)))
    good_wc = "\n".join(
        '<rule name="Bare slug to slash: slug-%02d" stopProcessing="true">\n<match url="^slug-%02d$" ignoreCase="true" />' % (i, i)
        for i in range(102)
    )
    good_ht = "\n".join("RewriteRule ^slug-%02d$ /slug-%02d/ [R=301,L]" % (i, i) for i in range(102))
    for slug, target in LEGACY_ELSEWHERE:
        good_ht += "\n# %s -> %s" % (slug, target)
        good_wc += "\n<!-- %s %s -->" % (slug, target)
    assert redirect_gaps(good_ht, good_wc) == []
    chained = good_ht + "\nRewriteRule ^about$ /about/ [R=301,L]"
    assert any("chain about" in g for g in redirect_gaps(chained, good_wc))
    short = good_wc.replace('slug-00', "slug-xx", 1)
    assert any("102 unique" in g or "missing" in g for g in redirect_gaps(good_ht, short))
    print("check_locked_state selftest OK (7 checks)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        selftest()
        return 0
    problems = check()
    print(report(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
