#!/usr/bin/env python3
"""
Phase 3 SEO Optimizer:
1. Upgrades all 20 London Borough pages (commercial-refrigeration-repair-<borough>)
   - Replaces 'Cold Chain' titles with high-CTR 'Commercial Refrigeration Repair <Borough> | Same-Day 24/7 | Cold Direct'
   - Connects all internal links directly to canonical London hubs (/cold-room-repair-london/, /commercial-fridge-repair-london/, /commercial-freezer-repair-london/, /freezer-room-repair-london/, /fridge-repair-london/, /freezer-repair-london/, /commercial-appliances-repair-london/)
   - Fixes mojibake 'Â©' -> '&copy;'
2. Upgrades all 10 North London Cold Room town pages (cold-room-repair-<town>)
   - Replaces legacy phone 020 8050 2374 with 0203 952 4822 (tel:+442039524822)
   - Adds contextual internal links to /cold-room-repair-london/, /freezer-room-repair-london/, /commercial-fridge-repair-london/
   - Normalizes all area links to trailing-slash canonicals
3. Syncs all changes across root <slug>.html, <slug>/index.html, and colddirect-public-html/
"""
import glob
import os
import re
import shutil

BOROUGH_NAMES = {
    "westminster": "Westminster",
    "camden": "Camden",
    "islington": "Islington",
    "city-of-london": "City of London",
    "hackney": "Hackney",
    "haringey": "Haringey",
    "kensington": "Kensington",
    "chelsea": "Chelsea",
    "hammersmith": "Hammersmith",
    "southwark": "Southwark",
    "lambeth": "Lambeth",
    "wandsworth": "Wandsworth",
    "tower-hamlets": "Tower Hamlets",
    "greenwich": "Greenwich",
    "brent": "Brent",
    "ealing": "Ealing",
    "richmond": "Richmond",
    "croydon": "Croydon",
    "newham": "Newham",
    "hounslow": "Hounslow",
}

COLD_ROOM_TOWNS = [
    "enfield",
    "barnet",
    "edgware",
    "finchley",
    "harrow",
    "palmers-green",
    "southgate",
    "tottenham",
    "wembley",
    "wood-green",
]


def sync_variants(root_html_path: str) -> int:
    slug = root_html_path[:-5]
    targets = [
        f"{slug}/index.html",
        f"colddirect-public-html/{root_html_path}",
        f"colddirect-public-html/{slug}/index.html",
    ]
    synced = 0
    for t in targets:
        parent = os.path.dirname(t)
        if os.path.exists(t) or (parent and os.path.isdir(parent)):
            shutil.copyfile(root_html_path, t)
            synced += 1
    return synced


def process_borough_pages() -> int:
    updated = 0
    for slug_suffix, name in BOROUGH_NAMES.items():
        fname = f"commercial-refrigeration-repair-{slug_suffix}.html"
        if not os.path.exists(fname):
            continue
        with open(fname, "r", encoding="utf-8") as f:
            html = f.read()

        orig = html
        # 1. Upgrade <title> from "<Borough> Cold Chain Same-Day Repair | ColdDirect"
        new_title = f"<title>Commercial Refrigeration Repair {name} | Same-Day 24/7 | Cold Direct</title>"
        html = re.sub(r"<title>[^<]+</title>", new_title, html, count=1)

        # 2. Replace "cold chain" in meta description and JSON-LD description
        html = html.replace("cold chain same-day repair", "commercial refrigeration, fridge, freezer &amp; cold room repair")
        html = html.replace("cold chain repair", "commercial refrigeration, fridge, freezer & cold room repair")
        html = html.replace(f"ColdDirect Cold Chain Repair {name}", f"Cold Direct Commercial Refrigeration Repair {name}")

        # 3. Fix JSON-LD url to have trailing slash
        html = html.replace(
            f'"url": "https://www.colddirect.co.uk/commercial-refrigeration-repair-{slug_suffix}"',
            f'"url": "https://www.colddirect.co.uk/commercial-refrigeration-repair-{slug_suffix}/"',
        )

        # 4. Upgrade internal links to London canonical hubs
        html = html.replace(
            'walk-in <a href="/cold-room-repair-north-london">cold rooms</a>, freezer rooms,',
            'walk-in <a href="/cold-room-repair-london/">cold rooms</a>, <a href="/freezer-room-repair-london/">freezer rooms</a>,',
        )
        html = html.replace(
            '<a href="/cellar-cooler-repair-london">cellar coolers</a>',
            '<a href="/cellar-cooler-repair-london/">cellar coolers</a>',
        )
        html = html.replace(
            'Internal links stay on this domain: <a href="/">homepage</a>, <a href="https://www.colddirect.co.uk/contact">contact</a>, <a href="/commercial-fridge-repair-north-london">commercial fridge repair</a>, <a href="/commercial-freezer-repair-north-london">commercial freezer repair</a>, and the cold room and cellar pages.',
            'Internal links stay on this domain: <a href="/">homepage</a>, <a href="/contact/">contact</a>, <a href="/commercial-fridge-repair-london/">commercial fridge repair London</a>, <a href="/fridge-repair-london/">fridge repair London</a>, <a href="/commercial-freezer-repair-london/">commercial freezer repair London</a>, <a href="/freezer-repair-london/">freezer repair London</a>, <a href="/cold-room-repair-london/">cold room repair London</a>, <a href="/freezer-room-repair-london/">freezer room repair London</a>, and <a href="/commercial-appliances-repair-london/">commercial appliances repair London</a>.',
        )

        # 5. Normalize borough cross-links to trailing slashes
        for b_slug in BOROUGH_NAMES:
            html = html.replace(
                f'href="/commercial-refrigeration-repair-{b_slug}"',
                f'href="/commercial-refrigeration-repair-{b_slug}/"',
            )
        html = html.replace('href="https://www.colddirect.co.uk/contact"', 'href="https://www.colddirect.co.uk/contact/"')
        html = html.replace("Â© ColdDirect", "&copy; Cold Direct")

        if html != orig:
            with open(fname, "w", encoding="utf-8") as f:
                f.write(html)
            sync_variants(fname)
            updated += 1
    return updated


def process_cold_room_towns() -> int:
    updated = 0
    for town_slug in COLD_ROOM_TOWNS:
        fname = f"cold-room-repair-{town_slug}.html"
        if not os.path.exists(fname):
            continue
        with open(fname, "r", encoding="utf-8") as f:
            html = f.read()

        orig = html
        # 1. Replace legacy phone number 020 8050 2374 with 0203 952 4822
        html = html.replace("tel:+442080502374", "tel:+442039524822")
        html = html.replace("020 8050 2374", "0203 952 4822")

        # 2. Fix JSON-LD link to trailing slash
        html = html.replace(
            "https://www.colddirect.co.uk/commercial-freezer-repair-london\"",
            "https://www.colddirect.co.uk/commercial-freezer-repair-london/\"",
        )

        # 3. Upgrade Services list in town pages to link to main London hubs
        old_services = """      <ul>
        <li>Walk-in Cold Room</li>
        <li>Freezer Room</li>
        <li>Chiller Room</li>
        <li>Cellar Cooler</li>
      </ul>"""
        new_services = """      <ul>
        <li><a href="/cold-room-repair-london/">Walk-in Cold Room Repair London</a></li>
        <li><a href="/freezer-room-repair-london/">Walk-in Freezer Room Repair London</a></li>
        <li><a href="/chiller-repair-london/">Commercial Chiller Repair London</a></li>
        <li><a href="/commercial-fridge-repair-london/">Commercial Fridge Repair London</a> &amp; <a href="/commercial-freezer-repair-london/">Commercial Freezer Repair London</a></li>
        <li><a href="/cellar-cooler-repair-london/">Pub &amp; Bar Cellar Cooler Repair</a></li>
      </ul>"""
        html = html.replace(old_services, new_services)

        # 4. Normalize town cross-links to trailing slashes
        for t_slug in COLD_ROOM_TOWNS:
            html = html.replace(
                f'href="/cold-room-repair-{t_slug}"',
                f'href="/cold-room-repair-{t_slug}/"',
            )
        html = html.replace("Â© ColdDirect", "&copy; Cold Direct")

        if html != orig:
            with open(fname, "w", encoding="utf-8") as f:
                f.write(html)
            sync_variants(fname)
            updated += 1
    return updated


if __name__ == "__main__":
    b_count = process_borough_pages()
    t_count = process_cold_room_towns()
    print(f"Phase 3 complete: updated {b_count} borough pages and {t_count} cold-room town pages (plus all folder/mirror copies).")
