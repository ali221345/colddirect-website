#!/usr/bin/env python3
"""Read-only HTTPS audit of the homepage and the 9 money hubs.

Fetches each live URL over HTTPS and reports, per page: HTTP status, <title>,
<meta name="description"> (plus whether it carries a CTR hook), the presence of
the CD marker blocks, descriptive image alt coverage and the #business JSON-LD
node. Nothing is written to the live site.

    python tools/live_production_audit.py            # table
    python tools/live_production_audit.py --json     # machine readable
    python tools/live_production_audit.py --selftest  # offline
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request

BASE = "https://www.colddirect.co.uk"

PAGES = [
    "/",
    "/commercial-fridge-repair-london/",
    "/fridge-repair-london/",
    "/commercial-freezer-repair-london/",
    "/cold-room-repair-london/",
    "/freezer-repair-london/",
    "/catering-repair-london/",
    "/commercial-appliances-repair-london/",
    "/air-conditioning-repair-london/",
    "/cellar-cooler-repair-london/",
]

# Markers every money hub must carry; the blog hub is homepage-only.
MONEY_MARKERS = (
    "CD-HERO-KEYWORD-MATRIX",
    "CD-9-MONEY-TECH-MATRIX-V47",
    "CD-9-MONEY-KEYWORD-SILO-V47",
)
HOME_MARKERS = ("CD-HERO-KEYWORD-MATRIX", "CD-9-MONEY-KEYWORD-SILO-V47", "CD-HOMEPAGE-6-BLOG-HUB")

# A description only earns the "CTR hook" flag when it promises something
# measurable: response speed, availability, price transparency or a phone number.
CTR_HOOKS = (
    r"same[- ]day",
    r"24/7",
    r"\b\d{2,3}\s*[-–]\s*\d{2,3}\s*min",
    r"no hidden fees",
    r"fixed .{0,20}call[- ]out",
    r"affordable",
    r"free quote",
    r"07983\s*759320",
    r"0800\s*112\s*3427",
    r"0203\s*952\s*4822",
)

UA = {"User-Agent": "ColdDirect-live-audit/1.0 (read-only SEO audit)"}
# Alt text shorter than this is decorative filler rather than a description.
MIN_ALT_WORDS = 3


def fetch(url: str, timeout: int = 30) -> tuple[int, str]:
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return resp.getcode(), raw.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def first_group(pattern: str, html: str) -> str:
    m = re.search(pattern, html, re.I | re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def title_of(html: str) -> str:
    return first_group(r"<title[^>]*>(.*?)</title>", html)


def description_of(html: str) -> str:
    for pattern in (
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
        r'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']',
    ):
        value = first_group(pattern, html)
        if value:
            return value
    return ""


def ctr_hooks(description: str) -> list[str]:
    return [h for h in CTR_HOOKS if re.search(h, description, re.I)]


def alt_coverage(html: str) -> tuple[int, int, int]:
    """Return (img count, imgs with alt, imgs with a descriptive alt)."""
    imgs = re.findall(r"<img\b[^>]*>", html, re.I)
    with_alt = 0
    descriptive = 0
    for tag in imgs:
        alt = re.search(r'\balt\s*=\s*["\'](.*?)["\']', tag, re.I | re.S)
        if not alt:
            continue
        with_alt += 1
        if len(alt.group(1).split()) >= MIN_ALT_WORDS:
            descriptive += 1
    return len(imgs), with_alt, descriptive


def business_schema(html: str) -> dict:
    """Locate the JSON-LD node whose @id ends in #business."""
    for block in re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.I | re.S
    ):
        try:
            data = json.loads(block.strip())
        except json.JSONDecodeError:
            continue
        nodes = data.get("@graph", data) if isinstance(data, dict) else data
        if isinstance(nodes, dict):
            nodes = [nodes]
        if not isinstance(nodes, list):
            continue
        for node in nodes:
            if isinstance(node, dict) and str(node.get("@id", "")).endswith("#business"):
                return node
    return {}


def audit_html(path: str, status: int, html: str) -> dict:
    markers = HOME_MARKERS if path == "/" else MONEY_MARKERS
    business = business_schema(html)
    total, with_alt, descriptive = alt_coverage(html)
    description = description_of(html)
    row = {
        "path": path,
        "status": status,
        "title": title_of(html),
        "description": description,
        "ctr_hooks": ctr_hooks(description),
        "markers": {m: (m in html) for m in markers},
        "images": {"total": total, "with_alt": with_alt, "descriptive_alt": descriptive},
        "business_schema": {
            "present": bool(business),
            "types": business.get("@type", ""),
            "telephone": business.get("telephone", ""),
        },
    }
    problems = []
    if status != 200:
        problems.append(f"HTTP {status}")
    if not row["title"]:
        problems.append("no <title>")
    if not description:
        problems.append("no meta description")
    elif not row["ctr_hooks"]:
        problems.append("description has no CTR hook")
    for marker, present in row["markers"].items():
        if not present:
            problems.append(f"missing {marker}")
    if total and with_alt < total:
        problems.append(f"{total - with_alt} <img> without alt")
    if with_alt and descriptive < with_alt:
        problems.append(f"{with_alt - descriptive} alt text(s) not descriptive")
    if not business:
        problems.append("no #business JSON-LD")
    row["problems"] = problems
    return row


def run(pages: list[str] | None = None) -> list[dict]:
    rows = []
    for path in pages or PAGES:
        status, html = fetch(BASE + path)
        rows.append(audit_html(path, status, html))
    return rows


def print_table(rows: list[dict]) -> None:
    for row in rows:
        flag = "PASS" if not row["problems"] else "FAIL"
        print(f"\n{flag} {row['status']} {row['path']}")
        print(f"  title       : {row['title']}")
        print(f"  description : {row['description']}")
        print(f"  ctr hooks   : {len(row['ctr_hooks'])}")
        print(
            "  markers     : "
            + ", ".join(f"{m}={'yes' if v else 'NO'}" for m, v in row["markers"].items())
        )
        img = row["images"]
        print(
            f"  images      : {img['total']} img, {img['with_alt']} with alt, "
            f"{img['descriptive_alt']} descriptive"
        )
        biz = row["business_schema"]
        print(
            f"  #business   : {'yes' if biz['present'] else 'NO'} "
            f"{biz['types']} tel={biz['telephone']}"
        )
        if row["problems"]:
            print("  problems    : " + "; ".join(row["problems"]))
    failed = [r for r in rows if r["problems"]]
    print(f"\n{len(rows) - len(failed)}/{len(rows)} pages clean")


GOOD_PAGE = """<html><head><title>Fridge Repair London</title>
<meta name="description" content="Same-day fridge repair, call 07983 759320">
<script type="application/ld+json">{"@graph":[{"@id":"https://x/#business",
"@type":["HVACBusiness"],"telephone":"+447983759320"}]}</script></head>
<body><!-- CD-HERO-KEYWORD-MATRIX --><!-- CD-9-MONEY-TECH-MATRIX-V47 -->
<!-- CD-9-MONEY-KEYWORD-SILO-V47 -->
<img src="a.jpg" alt="Engineer repairing a commercial fridge in London"></body></html>"""


def selftest() -> None:
    row = audit_html("/fridge-repair-london/", 200, GOOD_PAGE)
    assert row["problems"] == [], row["problems"]
    assert row["title"] == "Fridge Repair London"
    assert row["business_schema"]["telephone"] == "+447983759320"
    assert row["images"] == {"total": 1, "with_alt": 1, "descriptive_alt": 1}

    # a money-page marker set is not applied to the homepage and vice versa
    assert set(audit_html("/", 200, GOOD_PAGE)["markers"]) == set(HOME_MARKERS)
    assert "missing CD-HOMEPAGE-6-BLOG-HUB" in audit_html("/", 200, GOOD_PAGE)["problems"]

    assert "HTTP 404" in audit_html("/x/", 404, GOOD_PAGE)["problems"]
    assert "missing CD-9-MONEY-TECH-MATRIX-V47" in audit_html(
        "/x/", 200, GOOD_PAGE.replace("CD-9-MONEY-TECH-MATRIX-V47", "")
    )["problems"]
    assert "no meta description" in audit_html(
        "/x/", 200, re.sub(r'<meta name="description"[^>]*>', "", GOOD_PAGE)
    )["problems"]
    assert "description has no CTR hook" in audit_html(
        "/x/", 200, GOOD_PAGE.replace("Same-day fridge repair, call 07983 759320", "We fix fridges")
    )["problems"]
    assert "no #business JSON-LD" in audit_html(
        "/x/", 200, GOOD_PAGE.replace("#business", "#other")
    )["problems"]
    assert "1 <img> without alt" in audit_html(
        "/x/", 200, GOOD_PAGE.replace(' alt="Engineer repairing a commercial fridge in London"', "")
    )["problems"]
    assert "1 alt text(s) not descriptive" in audit_html(
        "/x/", 200, GOOD_PAGE.replace("Engineer repairing a commercial fridge in London", "fridge")
    )["problems"]
    # broken JSON-LD must not crash the parser
    assert audit_html("/x/", 200, GOOD_PAGE.replace('{"@graph"', '{"@graph"{'))[
        "business_schema"
    ]["present"] is False
    print("live_production_audit selftest OK (11 checks)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    parser.add_argument("--selftest", action="store_true", help="run offline checks and exit")
    args = parser.parse_args()

    if args.selftest:
        selftest()
        return 0

    rows = run()
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    else:
        print_table(rows)
    return 1 if any(r["problems"] for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
