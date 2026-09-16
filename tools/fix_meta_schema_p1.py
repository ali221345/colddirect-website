#!/usr/bin/env python3
"""P1: repair-intent meta templates + unified ApplianceRepair schema."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path("colddirect-public-html")
TEMPLATE_RE = re.compile(r"in London from Cold Direct", re.I)
SKIP_META = {"agent-status.html", "image-preview.html"}

BRANDS = [
    "foster", "williams", "true", "gram", "polar", "adexa", "empire",
    "liebherr", "hoshizaki", "subzero",
]

TYPE_KEYS = [
    ("walk-in-freezer-room", "Walk-in Freezer Room"),
    ("walk-in-cold-room", "Walk-in Cold Room"),
    ("walk-in-freezer", "Walk-in Freezer"),
    ("walk-in-fridge", "Walk-in Fridge"),
    ("walk-in-chiller", "Walk-in Chiller"),
    ("commercial-blast-chiller", "Blast Chiller"),
    ("commercial-blast-freezer", "Blast Freezer"),
    ("commercial-chest-freezer", "Chest Freezer"),
    ("commercial-display-cabinet", "Display Cabinet"),
    ("commercial-ice-machine", "Ice Machine"),
    ("commercial-dishwasher", "Commercial Dishwasher"),
    ("commercial-appliances", "Commercial Appliances"),
    ("commercial-bottle-cooler", "Bottle Cooler"),
    ("commercial-freezer", "Commercial Freezer"),
    ("commercial-fridge", "Commercial Fridge"),
    ("supermarket-freezer", "Supermarket Freezer"),
    ("supermarket-fridge", "Supermarket Fridge"),
    ("air-conditioning", "Air Conditioning"),
    ("ice-cream-machine", "Ice Cream Machine"),
    ("undercounter-fridge", "Undercounter Fridge"),
    ("cabinet-fridge", "Cabinet Fridge"),
    ("multideck-fridge", "Multideck Fridge"),
    ("open-front-display", "Open Front Display"),
    ("display-cabinet", "Display Cabinet"),
    ("display-fridge", "Display Fridge"),
    ("display-cooler", "Display Cooler"),
    ("dairy-cabinet", "Dairy Cabinet"),
    ("bottle-cooler", "Bottle Cooler"),
    ("bottle-fridge", "Bottle Cooler"),
    ("cellar-cooler", "Cellar Cooler"),
    ("wine-cooler", "Wine Cooler"),
    ("prep-fridge", "Prep Fridge"),
    ("drinks-fridge", "Drinks Fridge"),
    ("blast-chiller", "Blast Chiller"),
    ("blast-freezer", "Blast Freezer"),
    ("freezer-room", "Freezer Room"),
    ("cold-room", "Cold Room"),
    ("fridge-room", "Fridge Room"),
    ("ice-machine", "Ice Machine"),
    ("multideck", "Multideck"),
    ("chiller", "Chiller"),
    ("freezer", "Freezer"),
    ("fridge", "Fridge"),
    ("catering", "Catering Equipment"),
    ("appliances", "Commercial Appliances"),
]

RICH_BUSINESS = (
    '{"@type":"ApplianceRepair","@id":"https://www.colddirect.co.uk/#business",'
    '"name":"Cold Direct","url":"https://www.colddirect.co.uk/",'
    '"telephone":["+447983759320","+448001123427","+442039524822"],'
    '"priceRange":"££",'
    '"address":{"@type":"PostalAddress","streetAddress":"27 Felixstowe Road",'
    '"addressLocality":"Enfield","addressRegion":"Greater London",'
    '"postalCode":"N9 0DX","addressCountry":"GB"},'
    '"areaServed":['
    '{"@type":"AdministrativeArea","name":"North London"},'
    '{"@type":"GeoCircle","geoMidpoint":{"@type":"GeoCoordinates",'
    '"latitude":"51.6478","longitude":"-0.0701"},"geoRadius":"40233"},'
    '{"@type":"City","name":"London"}],'
    '"openingHoursSpecification":{"@type":"OpeningHoursSpecification",'
    '"dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],'
    '"opens":"00:00","closes":"23:59"},'
    '"description":"Trade-only commercial refrigeration repair across North London and a 25 mile radius."}'
)

PROVIDER_STUB = (
    '{"@type":"ApplianceRepair","@id":"https://www.colddirect.co.uk/#business","name":"Cold Direct"}'
)

HOMEPAGE_SCHEMA = """{
  "@context": "https://schema.org",
  "@type": "ApplianceRepair",
  "@id": "https://www.colddirect.co.uk/#business",
  "name": "Cold Direct - Commercial Refrigeration Repair",
  "url": "https://www.colddirect.co.uk/",
  "image": "https://www.colddirect.co.uk/images/logo/colddirect-main.webp",
  "telephone": ["+442039524822", "+448001123427", "+447983759320"],
  "priceRange": "££",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "27 Felixstowe Road",
    "addressLocality": "Enfield",
    "addressRegion": "Greater London",
    "postalCode": "N9 0DX",
    "addressCountry": "GB"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "51.6478",
    "longitude": "-0.0701"
  },
  "areaServed": [
    {"@type": "AdministrativeArea", "name": "North London"},
    {"@type": "GeoCircle", "geoMidpoint": {"@type": "GeoCoordinates", "latitude": "51.6478", "longitude": "-0.0701"}, "geoRadius": "40233"},
    {"@type": "City", "name": "London"},
    {"@type": "City", "name": "Enfield"},
    {"@type": "City", "name": "Barnet"},
    {"@type": "City", "name": "Haringey"},
    {"@type": "City", "name": "Islington"},
    {"@type": "City", "name": "Camden"}
  ],
  "openingHoursSpecification": {
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    "opens": "00:00",
    "closes": "23:59"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.9",
    "reviewCount": "38"
  },
  "description": "24/7 emergency commercial refrigeration repair for trade kitchens across North London and a 25 mile radius."
}"""


def brand_label(slug: str) -> str:
    if slug == "subzero":
        return "Sub-Zero"
    return slug.replace("-", " ").title()


def parse_stem(stem: str) -> tuple[str | None, str, str]:
    """Return brand, equipment label, location label."""
    area = "London"
    s = stem
    if s.endswith("-north-london"):
        area = "North London"
        s = s[: -len("-north-london")]
    elif s.endswith("-london"):
        area = "London"
        s = s[: -len("-london")]

    m = re.match(r"^commercial-refrigeration-repair-(.+)$", s)
    if m:
        place = m.group(1).replace("-", " ").title()
        return None, "Commercial Refrigeration", place

    m = re.match(r"^cold-room-repair-(.+)$", s)
    if m and m.group(1) not in ("",):
        place = m.group(1).replace("-", " ").title()
        if place.lower() != "london":
            return None, "Cold Room", place

    brand = None
    rest = s
    for b in sorted(BRANDS, key=len, reverse=True):
        if s == b or s.startswith(b + "-"):
            brand = brand_label(b)
            rest = s[len(b) :].lstrip("-") if s != b else ""
            break

    equip = None
    search = rest or s
    for key, label in TYPE_KEYS:
        if search == key or search.startswith(key) or search.endswith(key) or key in search:
            equip = label
            break
    if equip is None:
        words = [w for w in search.split("-") if w and w not in ("repair", "repairs")]
        equip = " ".join(w.title() for w in words) or "Commercial Refrigeration"

    # Avoid "Foster Fridge" when brand=Foster and equip=Fridge → keep as Fridge under brand
    if brand and equip.lower().startswith(brand.lower()):
        equip = equip[len(brand) :].strip() or equip

    return brand, equip, area


def build_meta(stem: str, filename: str) -> tuple[str, str]:
    special = {
        "about-us": (
            "About Cold Direct | Commercial Refrigeration Engineers London",
            "Cold Direct commercial refrigeration engineers serving North London and a 25 mile radius. Trade kitchens only. Call 07983 759320.",
        ),
        "about": (
            "About Cold Direct | Commercial Refrigeration Engineers London",
            "Cold Direct commercial refrigeration engineers serving North London and a 25 mile radius. Trade kitchens only. Call 07983 759320.",
        ),
        "contact": (
            "Contact Cold Direct | Commercial Refrigeration Repair London",
            "Book commercial refrigeration repair in London. Call 07983 759320, freephone 0800 112 3427 or 0203 952 4822. Trade only. Enfield N9 0DX.",
        ),
        "write-a-review": (
            "Write a Review | Cold Direct Commercial Refrigeration London",
            "Leave a review for Cold Direct commercial refrigeration repair in North London. Trade callouts across a 25 mile radius.",
        ),
        "fridge-repair": (
            "Commercial Fridge Repair London | Same-Day Callout - Cold Direct",
            "Commercial fridge repair in London for restaurants, pubs and shops. Same-day callout. Trade only. Cold Direct. Call 07983 759320.",
        ),
        "freezer-repair": (
            "Commercial Freezer Repair London | Same-Day Callout - Cold Direct",
            "Commercial freezer repair in London for trade kitchens. Same-day callout. Cold Direct. Call 07983 759320.",
        ),
        "multideck-repair": (
            "Multideck Fridge Repair London | Same-Day Callout - Cold Direct",
            "Multideck fridge repair in London for shops and convenience stores. Trade only. Cold Direct. Call 07983 759320.",
        ),
        "drinks-fridge-repair": (
            "Drinks Fridge Repair London | Same-Day Callout - Cold Direct",
            "Commercial drinks fridge repair in London. Trade only. Same-day callout. Cold Direct. Call 07983 759320.",
        ),
        "fridge-room-repair": (
            "Fridge Room Repair London | Same-Day Callout - Cold Direct",
            "Fridge room and walk-in chiller repair in London. Trade only. Cold Direct. Call 07983 759320.",
        ),
        "walk-in-chiller-repair": (
            "Walk-in Chiller Repair London | Same-Day Callout - Cold Direct",
            "Walk-in chiller repair in London for restaurants and catering. Trade only. Cold Direct. Call 07983 759320.",
        ),
    }
    if stem in special:
        return special[stem]

    # Strip -london already handled in parse; use full stem
    brand, equip, area = parse_stem(stem)

    if brand:
        title = f"{brand} Commercial {equip} Repair {area} | Same-Day Callout - Cold Direct"
        title = title.replace("Commercial Commercial ", "Commercial ")
        desc = (
            f"{brand} commercial {equip.lower()} repair in {area}. Same-day emergency callout for trade kitchens. "
            f"North London & 25 miles. Cold Direct. Call 07983 759320."
        )
    else:
        title = f"{equip} Repair {area} | Same-Day Callout - Cold Direct"
        desc = (
            f"{equip} repair in {area} for restaurants, pubs, hotels and shops. "
            f"Trade only. Same-day callout. Cold Direct. Call 07983 759320."
        )

    title = re.sub(r"\s+", " ", title).strip()
    desc = re.sub(r"\s+", " ", desc).strip()
    if len(title) > 70:
        title = title.replace(" | Same-Day Callout - Cold Direct", " | Cold Direct")
    if len(title) > 70:
        title = title[:67].rstrip(" |-") + "..."
    if len(desc) > 158:
        desc = desc[:155].rstrip() + "..."
    return title, desc


def replace_meta(html: str, title: str, desc: str) -> str:
    title_esc = title.replace("&", "&amp;").replace('"', "&quot;")
    desc_esc = desc.replace("&", "&amp;").replace('"', "&quot;")
    html = re.sub(r"<title>.*?</title>", f"<title>{title_esc}</title>", html, count=1, flags=re.I | re.S)
    html, n = re.subn(
        r'(<meta\s+name=["\']description["\']\s+content=["\'])(.*?)(["\'])',
        rf"\1{desc_esc}\3",
        html,
        count=1,
        flags=re.I | re.S,
    )
    if n == 0:
        html, n = re.subn(
            r'(<meta\s+content=["\'])(.*?)(["\']\s+name=["\']description["\'])',
            rf"\1{desc_esc}\3",
            html,
            count=1,
            flags=re.I | re.S,
        )
    return html


THIN_LB = re.compile(
    r'\{\s*"@type"\s*:\s*"LocalBusiness"\s*,\s*"name"\s*:\s*"Cold Direct"\s*,\s*"url"\s*:\s*"https://www\.colddirect\.co\.uk/"\s*,\s*"telephone"\s*:\s*"\+447983759320"\s*,\s*"areaServed"\s*:\s*\[\s*"London"\s*,\s*"Greater London"\s*\]\s*\}',
    re.S,
)

# Also spaced variants with newlines
THIN_LB_FLEX = re.compile(
    r'\{\s*"@type"\s*:\s*"LocalBusiness"\s*,\s*"name"\s*:\s*"Cold Direct"[^{}]*?"areaServed"\s*:\s*\[[^\]]*\]\s*\}',
    re.S,
)

PROVIDER_LB = re.compile(
    r'\{\s*"@type"\s*:\s*"LocalBusiness"\s*,\s*"name"\s*:\s*"Cold Direct"\s*\}',
    re.S,
)


def unify_schema(html: str, filename: str) -> tuple[str, list[str]]:
    notes: list[str] = []

    if filename == "index.html" and re.search(r'"@type"\s*:\s*"HVACBusiness"', html):
        html2, n = re.subn(
            r'<script type="application/ld\+json">\s*\{.*?"@type"\s*:\s*"HVACBusiness".*?\}\s*</script>',
            f'<script type="application/ld+json">\n{HOMEPAGE_SCHEMA}\n  </script>',
            html,
            count=1,
            flags=re.S,
        )
        if n:
            html = html2
            notes.append("homepage HVACBusiness→rich ApplianceRepair")
        else:
            html = html.replace('"@type": "HVACBusiness"', '"@type": "ApplianceRepair"')
            html = html.replace('"@type":"HVACBusiness"', '"@type":"ApplianceRepair"')
            notes.append("homepage HVACBusiness renamed")

    # Other HVACBusiness
    if re.search(r'"@type"\s*:\s*"HVACBusiness"', html):
        html = html.replace('"@type": "HVACBusiness"', '"@type": "ApplianceRepair"')
        html = html.replace('"@type":"HVACBusiness"', '"@type":"ApplianceRepair"')
        notes.append("HVACBusiness→ApplianceRepair")

    # Provider stubs first (smaller)
    html2, n = PROVIDER_LB.subn(PROVIDER_STUB, html)
    if n:
        html = html2
        notes.append(f"provider stubs enriched x{n}")

    # Thin top-level LocalBusiness with areaServed list
    html2, n = THIN_LB_FLEX.subn(RICH_BUSINESS, html)
    if n:
        html = html2
        notes.append(f"thin LocalBusiness→rich ApplianceRepair x{n}")

    # Any remaining LocalBusiness → ApplianceRepair (including richer blocks)
    before = len(re.findall(r'"@type"\s*:\s*"LocalBusiness"', html))
    if before:
        html = re.sub(r'("@type"\s*:\s*)"LocalBusiness"', r'\1"ApplianceRepair"', html)
        notes.append(f"LocalBusiness→ApplianceRepair remaining x{before}")

    # Store type if any
    if re.search(r'"@type"\s*:\s*"Store"', html):
        html = re.sub(r'("@type"\s*:\s*)"Store"', r'\1"ApplianceRepair"', html)
        notes.append("Store→ApplianceRepair")

    # Ensure priceRange + openingHours on rich ApplianceRepair blocks that have address but lack priceRange
    # (best-effort for commercial-fridge style blocks already renamed)
    def enrich_named_block(m: re.Match) -> str:
        block = m.group(0)
        changed = False
        if '"priceRange"' not in block:
            block = block.replace('"name": "Cold Direct"', '"name": "Cold Direct", "priceRange": "££"', 1)
            block = block.replace('"name":"Cold Direct"', '"name":"Cold Direct","priceRange":"££"', 1)
            changed = True
        if '"areaServed"' in block and "North London" not in block and "GeoCircle" not in block:
            block = re.sub(
                r'"areaServed"\s*:\s*\[[^\]]*\]',
                '"areaServed":[{"@type":"AdministrativeArea","name":"North London"},'
                '{"@type":"GeoCircle","geoMidpoint":{"@type":"GeoCoordinates","latitude":"51.6478","longitude":"-0.0701"},'
                '"geoRadius":"40233"},{"@type":"City","name":"London"}]',
                block,
                count=1,
            )
            changed = True
        if changed:
            notes.append("enriched ApplianceRepair fields")
        return block

    html = re.sub(
        r'\{\s*"@type"\s*:\s*"ApplianceRepair"[^{}]*?(?:\{[^{}]*\}[^{}]*?)*?\}',
        enrich_named_block,
        html,
        count=3,
        flags=re.S,
    )

    return html, notes


def main():
    changed_meta = []
    changed_schema = []
    for p in sorted(ROOT.glob("*.html")):
        original = p.read_text(encoding="utf-8", errors="replace")
        html = original
        stem = p.stem

        if p.name not in SKIP_META and TEMPLATE_RE.search(html):
            title, desc = build_meta(stem, p.name)
            html = replace_meta(html, title, desc)
            if TEMPLATE_RE.search(html):
                # leftover in non-title fields
                html = TEMPLATE_RE.sub("for trade kitchens from Cold Direct", html)
            changed_meta.append({"file": p.name, "title": title, "description": desc})

        html, notes = unify_schema(html, p.name)
        if notes:
            changed_schema.append({"file": p.name, "notes": notes})

        if html != original:
            p.write_text(html, encoding="utf-8", newline="\n")

    # Post audit
    left_meta = []
    type_counts: dict[str, int] = {}
    for p in sorted(ROOT.glob("*.html")):
        t = p.read_text(encoding="utf-8", errors="replace")
        if TEMPLATE_RE.search(t) and p.name not in SKIP_META:
            left_meta.append(p.name)
        for m in re.finditer(r'"@type"\s*:\s*"([^"]+)"', t):
            typ = m.group(1)
            if typ in (
                "LocalBusiness",
                "ApplianceRepair",
                "HVACBusiness",
                "Store",
                "HomeAndConstructionBusiness",
            ):
                type_counts[typ] = type_counts.get(typ, 0) + 1

    report = {
        "changed_meta_count": len(changed_meta),
        "changed_schema_count": len(changed_schema),
        "remaining_template_non_utility": left_meta,
        "schema_type_counts": type_counts,
        "changed_meta": changed_meta,
        "changed_schema": changed_schema,
    }
    Path("docs/_meta-schema-batch.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k not in ("changed_meta", "changed_schema")}, indent=2))
    print("META sample:")
    for row in changed_meta[:8]:
        print(" ", row["file"], "=>", row["title"])


if __name__ == "__main__":
    main()
