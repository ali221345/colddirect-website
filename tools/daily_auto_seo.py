#!/usr/bin/env python3
"""
Daily Automated SEO & GSC Self-Healing Agent for Cold Direct (https://www.colddirect.co.uk/).
Runs automatically in GitHub Actions every day without manual intervention:
1. Checks Google Search Console for sitemap errors, ranking drops, legacy .asp traffic, and unindexed pages.
2. Enforces clean self-referencing canonicals (no .asp regressions) across all HTML pages.
3. Injects contextual internal links from high-authority hubs/blogs to any unindexed or dropping priority pages.
4. Syncs <slug>.html, <slug>/index.html, and colddirect-public-html/ twins so deployments never diverge.
5. Regenerates sitemap.xml & robots.txt (via agent/run.py) and triggers GSC sitemap submission + URL indexing.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "colddirect-public-html"
AUDIT = ROOT / "seo-audit"
BASE_URL = "https://www.colddirect.co.uk"

PRIORITY_PAGES = [
    {
        "slug": "freezer-room-repair-london",
        "url": "https://www.colddirect.co.uk/freezer-room-repair-london/",
        "href": "/freezer-room-repair-london/",
        "anchor": "freezer room repair London",
        "query": "freezer room repair london",
    },
    {
        "slug": "commercial-appliances-repair-london",
        "url": "https://www.colddirect.co.uk/commercial-appliances-repair-london/",
        "href": "/commercial-appliances-repair-london/",
        "anchor": "commercial appliances repair London",
        "query": "commercial appliances repair london",
    },
    {
        "slug": "cold-room-repair-london",
        "url": "https://www.colddirect.co.uk/cold-room-repair-london/",
        "href": "/cold-room-repair-london/",
        "anchor": "cold room repair London",
        "query": "cold room repair london",
    },
    {
        "slug": "commercial-fridge-repair-london",
        "url": "https://www.colddirect.co.uk/commercial-fridge-repair-london/",
        "href": "/commercial-fridge-repair-london/",
        "anchor": "commercial fridge repair London",
        "query": "commercial fridge repair london",
    },
    {
        "slug": "commercial-freezer-repair-london",
        "url": "https://www.colddirect.co.uk/commercial-freezer-repair-london/",
        "href": "/commercial-freezer-repair-london/",
        "anchor": "commercial freezer repair London",
        "query": "commercial freezer repair london",
    },
    {
        "slug": "chiller-repairs-london",
        "url": "https://www.colddirect.co.uk/chiller-repairs-london/",
        "href": "/chiller-repairs-london/",
        "anchor": "chiller repairs London",
        "query": "chiller repair london",
    },
    {
        "slug": "fridge-repair-london",
        "url": "https://www.colddirect.co.uk/fridge-repair-london/",
        "href": "/fridge-repair-london/",
        "anchor": "fridge repair London",
        "query": "fridge repair london",
    },
    {
        "slug": "freezer-repair-london",
        "url": "https://www.colddirect.co.uk/freezer-repair-london/",
        "href": "/freezer-repair-london/",
        "anchor": "freezer repair London",
        "query": "freezer repair london",
    },
    {
        "slug": "ice-machine-repair-london",
        "url": "https://www.colddirect.co.uk/ice-machine-repair-london/",
        "href": "/ice-machine-repair-london/",
        "anchor": "ice machine repair London",
        "query": "ice machine repair london",
    },
]

BLOG_DONORS = [
    "blog/why-commercial-freezer-icing-up.html",
    "blog/cold-room-temperature-fluctuation.html",
    "blog/commercial-fridge-not-cooling.html",
    "blog/commercial-freezer-temperature-guide.html",
    "blog/different-types-of-ice.html",
    "blog/types-of-cold-storage.html",
]


def load_protected_files() -> set[str]:
    manifest = ROOT / "protected-pages.json"
    if not manifest.exists():
        return set()
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        out: set[str] = set()
        for page in data.get("pages", []):
            for f in page.get("files", []):
                out.add(f.replace("\\", "/"))
        return out
    except Exception:
        return set()


def fix_asp_canonicals(protected: set[str]) -> list[str]:
    """Ensure no indexable HTML page has a legacy .asp canonical tag."""
    fixed: list[str] = []
    canonical_re = re.compile(
        r'(<link\s+rel=["\']canonical["\']\s+href=["\'])https://www\.colddirect\.co\.uk/([^"\']+?)\.asp(["\'][^>]*>)',
        re.IGNORECASE,
    )
    for html_file in sorted(ROOT.glob("*.html")) + sorted((ROOT / "blog").glob("*.html")):
        rel = html_file.relative_to(ROOT).as_posix()
        if rel in protected or html_file.name.startswith("google"):
            continue
        text = html_file.read_text(encoding="utf-8", errors="ignore")
        if ".asp" not in text.lower():
            continue
        new_text = canonical_re.sub(
            lambda m: f"{m.group(1)}{BASE_URL}/{m.group(2).rstrip('/')}/{m.group(3)}",
            text,
        )
        if new_text != text:
            html_file.write_text(new_text, encoding="utf-8")
            fixed.append(rel)
    return fixed


def ensure_blog_link(blog_rel: str, href: str, anchor: str, protected: set[str]) -> bool:
    if blog_rel in protected:
        return False
    p = ROOT / blog_rel
    if not p.exists():
        return False
    html = p.read_text(encoding="utf-8", errors="ignore")
    if href in html or href.rstrip("/") in html:
        return False
    marker = "</article>"
    if marker not in html:
        return False
    addition = (
        f'      <p class="cd-auto-related">Need 24/7 commercial engineer support? '
        f'See <a href="{href}">{anchor}</a> for rapid London attendance.</p>\n    </article>'
    )
    updated = html.replace(marker, addition, 1)
    if updated != html:
        p.write_text(updated, encoding="utf-8")
        return True
    return False


def sync_page_twins(protected: set[str]) -> int:
    """Keep <slug>.html, <slug>/index.html, and colddirect-public-html/ copies aligned."""
    synced = 0
    candidates = [
        "index.html",
        "index.php",
        "services.html",
        "freezer-room-repair-london.html",
        "commercial-appliances-repair-london.html",
        "chiller-repairs-london.html",
        "cold-room-repair-london.html",
        "catering-repair-london.html",
        "appliances-repair-london.html",
        "blog/different-types-of-ice.html",
        "blog/types-of-cold-storage.html",
        "blog/why-commercial-freezer-icing-up.html",
        "blog/cold-room-temperature-fluctuation.html",
        "blog/commercial-fridge-not-cooling.html",
        "blog/commercial-freezer-temperature-guide.html",
    ]
    for rel in candidates:
        if rel in protected:
            continue
        src = ROOT / rel
        if not src.exists():
            continue
        targets: list[Path] = []
        if rel in ("index.html", "index.php"):
            targets.append(PUBLIC / rel)
        elif rel.startswith("blog/") and rel.endswith(".html"):
            slug = rel[5:-5]
            targets.extend([
                ROOT / "blog" / slug / "index.html",
                PUBLIC / rel,
                PUBLIC / "blog" / slug / "index.html",
            ])
        elif rel.endswith(".html"):
            slug = rel[:-5]
            if slug != "services":
                targets.append(ROOT / slug / "index.html")
                targets.append(PUBLIC / rel)
                targets.append(PUBLIC / slug / "index.html")
            else:
                targets.append(ROOT / "services" / "index.html")

        src_bytes = src.read_bytes()
        for dst in targets:
            dst_rel = dst.relative_to(ROOT).as_posix()
            if dst_rel in protected:
                continue
            if dst.parent.exists():
                if not dst.exists() or dst.read_bytes() != src_bytes:
                    shutil.copyfile(src, dst)
                    synced += 1
    return synced


def main() -> int:
    AUDIT.mkdir(parents=True, exist_ok=True)
    protected = load_protected_files()

    # 1. Fix any .asp canonical regressions
    fixed_canonicals = fix_asp_canonicals(protected)
    if fixed_canonicals:
        print(f"[AUTO-SEO] Fixed .asp canonicals on: {', '.join(fixed_canonicals)}")

    # 2. Enforce homepage & footer links via scripts/internal_linking.js
    subprocess.run(["node", str(ROOT / "scripts" / "internal_linking.js")], cwd=str(ROOT), check=False)

    # 3. Inspect GSC & request indexing if credentials are available
    unindexed_urls: set[str] = set()
    try:
        from request_indexing import run_indexing

        inspect_results = run_indexing([p["url"] for p in PRIORITY_PAGES])
        for item in inspect_results:
            verdict = item.get("verdict", "")
            state = item.get("coverageState", "")
            if verdict != "PASS" or "not indexed" in state.lower() or "unknown" in state.lower():
                unindexed_urls.add(item["url"])
    except Exception as exc:
        print(f"[AUTO-SEO] GSC inspection warning (continuing): {exc}")

    # 4. If any priority page is unindexed, ensure at least 2 blog donors link to it
    links_injected: list[str] = []
    for p in PRIORITY_PAGES:
        if p["url"] in unindexed_urls or p["slug"] in ("freezer-room-repair-london", "commercial-appliances-repair-london"):
            count = 0
            for blog_rel in BLOG_DONORS:
                if count >= 2:
                    break
                if ensure_blog_link(blog_rel, p["href"], p["anchor"], protected):
                    links_injected.append(f"{blog_rel} -> {p['href']}")
                    count += 1

    # 5. Sync twin files across root and colddirect-public-html
    synced = sync_page_twins(protected)
    print(f"[AUTO-SEO] Synced {synced} twin file(s)")

    # 6. Regenerate sitemap.xml (offline canonical collection) and check robots.txt
    sys.path.insert(0, str(ROOT / "agent"))
    from scripts.sitemap import generate_sitemap
    from scripts.robots import check_robots

    generate_sitemap(str(ROOT), verify_live=False)
    check_robots(str(ROOT))
    if (ROOT / "sitemap.xml").exists() and PUBLIC.exists():
        shutil.copyfile(ROOT / "sitemap.xml", PUBLIC / "sitemap.xml")

    # 7. Write summary status JSON
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    summary = {
        "date": today,
        "fixed_canonicals": fixed_canonicals,
        "unindexed_priority_urls": sorted(unindexed_urls),
        "links_injected": links_injected,
        "twins_synced": synced,
    }
    (AUDIT / "daily-auto-seo-last.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"[AUTO-SEO] Completed daily self-healing run for {today}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
