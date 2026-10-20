#!/usr/bin/env python3
"""Cold Direct - 2026-10-21 de-cannibalisation + strike-distance body pass.

Idempotent: every edit checks whether its result is already present.
Edits ONLY page body / head social tags / local JSON-LD (data-cd-schema=local-service-faq).
Title + meta description + V4 schema/footer/bloghub stay owned by auto-seo.aspx
(its rules are updated separately in the same change).

Applies the edit to the root <slug>.html and then writes the identical result to
<slug>/index.html, colddirect-public-html/<slug>.html and colddirect-public-html/<slug>/index.html.

Usage: python tools/seo_decannibalise_pass.py [--check]
"""
import html as htmllib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK = "--check" in sys.argv
BASE = "https://www.colddirect.co.uk"
BIZ = {"@id": BASE + "/#business"}
BRAND_LINK_MARK = 'class="cd-brand-backlink"'
PHONE = "07983 759320"

changed_files = []


def read(p):
    with open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def sub1(text, old, new, label):
    """Replace exactly one occurrence; no-op when already applied."""
    if new in text and old not in text:
        return text
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"[{label}] expected exactly 1 match, found {n}: {old[:90]!r}")
    return text.replace(old, new, 1)


def clean(s):
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", htmllib.unescape(s)).strip()


def esc_faq_text(s):
    """Plain text -> HTML-safe visible text."""
    return htmllib.escape(s, quote=False)


# ---------------------------------------------------------------- shared helpers
def add_brand_backlink(text, slug):
    if BRAND_LINK_MARK in text:
        return text
    m = re.search(r'<p class="lead">.*?</p>', text, re.S)
    if not m:
        raise SystemExit(f"[{slug}] no hero lead paragraph for brand back-link")
    block = (
        '\n      <p class="cd-brand-backlink" style="margin:10px 0 16px;font-size:15px;">'
        'Part of <a href="/">ColdDirect London Refrigeration Engineers</a>: commercial refrigeration '
        'and air conditioning repair across London and North London.</p>'
    )
    return text[: m.end()] + block + text[m.end():]


def add_accordion_items(text, slug, items):
    """items: list of (question, answer_html). Appends numbered <details> to the FAQ accordion."""
    m = re.search(r'(<section class="cd-faq-accordion".*?)(</section>)', text, re.S)
    if not m:
        raise SystemExit(f"[{slug}] no FAQ accordion")
    body = m.group(1)
    existing = [clean(x) for x in re.findall(r"<summary>(.*?)</summary>", body, re.S)]
    n = len(existing)
    add = ""
    for q, a in items:
        if any(q in e for e in existing):
            continue
        n += 1
        add += f"    <details>\n      <summary>{n}. {esc_faq_text(q)}</summary>\n      <p>{a}</p>\n    </details>\n"
    # normalise indentation of items appended by an earlier run, then append the new ones
    section = re.sub(r"\n {6}<details>", "\n    <details>", text[m.start(1): m.end(2)])
    text = text[: m.start(1)] + section + text[m.end(2):]
    m = re.search(r'(<section class="cd-faq-accordion".*?)(</section>)', text, re.S)
    if not add:
        return text
    return text[: m.start(1)] + m.group(1).rstrip(" ") + add + "  " + text[m.start(2):]


def add_plain_faq_items(text, slug, items):
    """For pages with a <div class="faq"> h3/p list (ice cream)."""
    m = re.search(r'(<div class="faq">.*?)(</div>)', text, re.S)
    if not m:
        raise SystemExit(f"[{slug}] no .faq div")
    body = m.group(1)
    add = ""
    for q, a in items:
        if esc_faq_text(q) in body:
            continue
        add += f"        <h3>{esc_faq_text(q)}</h3>\n        <p>{a}</p>\n"
    section = re.sub(r"\n {14}<h3>", "\n        <h3>", text[m.start(1): m.end(2)])
    text = text[: m.start(1)] + section + text[m.end(2):]
    m = re.search(r'(<div class="faq">.*?)(</div>)', text, re.S)
    if not add:
        return text
    return text[: m.start(1)] + m.group(1).rstrip(" ") + add + "      " + text[m.start(2):]


def visible_faq(text, use_plain=False):
    out = []
    seen = set()
    sec = re.search(r'<section class="cd-faq-accordion".*?</section>', text, re.S)
    if sec:
        for q, a in re.findall(r"<details[^>]*>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>", sec.group(0), re.S):
            qq = re.sub(r"^\d+\.\s*", "", clean(q))
            if qq not in seen:
                seen.add(qq)
                out.append((qq, clean(a)))
    if use_plain:
        d = re.search(r'<div class="faq">(.*?)</div>', text, re.S)
        if d:
            for q, a in re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", d.group(1), re.S):
                qq = clean(q)
                if qq not in seen:
                    seen.add(qq)
                    out.append((qq, clean(a)))
    return out


LOCAL_RE = re.compile(
    r'(<script type="application/ld\+json" data-cd-schema="local-service-faq">)(.*?)(</script>)', re.S
)


def update_local_schema(text, slug, service_patch, use_plain=False, replace_service=False):
    m = LOCAL_RE.search(text)
    if not m:
        raise SystemExit(f"[{slug}] no local-service-faq schema block")
    data = json.loads(m.group(2))
    graph = data["@graph"]
    svc = next((n for n in graph if n.get("@type") == "Service"), None)
    if svc is None or replace_service:
        new = dict(service_patch)
        if svc is None:
            graph.append(new)
        else:
            graph[graph.index(svc)] = new
    else:
        svc.update(service_patch)
    faq = next((n for n in graph if n.get("@type") == "FAQPage"), None)
    entities = [
        {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        }
        for q, a in visible_faq(text, use_plain)
    ]
    if faq is None:
        graph.append({"@type": "FAQPage", "mainEntity": entities})
    else:
        faq["mainEntity"] = entities
    body = json.dumps(data, indent=2, ensure_ascii=False)
    # keep the original line ending convention of the block
    eol = "\r\n" if "\r\n" in m.group(2) else "\n"
    body = body.replace("\n", eol)
    return text[: m.start(2)] + eol + body + eol + text[m.end(2):]


def svc_node(slug, name, service_type, description, offers):
    url = f"{BASE}/{slug}/"
    return {
        "@type": "Service",
        "@id": url + "#service",
        "name": name,
        "serviceType": service_type,
        "description": description,
        "url": url,
        "provider": BIZ,
        "areaServed": ["London", "Greater London"],
        "hoursAvailable": "Mo-Su 00:00-23:59",
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": f"{name} - keyword variations",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": o}} for o in offers
            ],
        },
    }


def insert_before_ctaband(text, marker, block):
    if marker in text:
        return text
    i = text.find('<section class="cta-band">')
    if i < 0:
        raise SystemExit(f"[{marker}] no cta-band to anchor on")
    return text[:i] + block + "\n  " + text[i:]


def variants(slug):
    out = [ROOT / f"{slug}.html"]
    for p in (
        ROOT / slug / "index.html",
        ROOT / "colddirect-public-html" / f"{slug}.html",
        ROOT / "colddirect-public-html" / slug / "index.html",
    ):
        out.append(p)
    return out


def commit(slug, new_text, create_missing=False, require_identical=True):
    root_file = ROOT / f"{slug}.html"
    old_text = read(root_file)
    if require_identical:
        for p in variants(slug)[1:]:
            if p.exists() and read(p) != old_text:
                raise SystemExit(f"[{slug}] copy differs from root before edit: {p}")
    if new_text == old_text and all(
        (not p.exists() and not create_missing) or (p.exists() and read(p) == new_text)
        for p in variants(slug)[1:]
    ):
        print(f"  = {slug}: already up to date")
        return
    if CHECK:
        print(f"  ! {slug}: would change")
        changed_files.append(slug)
        return
    for p in variants(slug):
        if p.exists() or create_missing or p == root_file:
            write(p, new_text)
    print(f"  + {slug}: updated")
    changed_files.append(slug)


# ---------------------------------------------------------------- the four cannibalised pages
MONEY = {
    "commercial-fridge-repair-london": {
        "h1": ("<h1>Emergency Commercial Fridge Repair London</h1>",
               "<h1>Commercial Fridge Repair London – Same-Day Walk-In &amp; Display Chiller Engineers</h1>"),
        "lead": ('<p class="lead">Commercial fridge repair in London for restaurants,',
                 '<p class="lead"><strong>Commercial fridge repair London</strong> for restaurants,'),
        "svc": ("Commercial fridge repair London", "Commercial fridge repair",
                "24/7 same-day commercial fridge repair in London for restaurants, pubs, hotels, shops and catering kitchens: "
                "upright and prep-counter fridges, walk-in chillers and glass-door display chillers. F-Gas certified engineers, fixed price quoted on site. Commercial only.",
                ["Commercial fridge repair London", "Commercial fridge repairs", "Commercial fridge service",
                 "Walk-in chiller repair London", "Display chiller repair London", "Emergency fridge repair"]),
        "faq": [
            ("Do you offer same-day commercial fridge repair in London for walk-in and display chillers?",
             "Yes. Commercial fridge repair London is a 24/7 same-day service for upright and prep-counter fridges, glass-door display chillers and multidecks. "
             "Walk-in rooms are handled by our cold room repair engineers. Call 07983 759320 with your postcode, make and fault."),
            ("How much does commercial fridge repair cost in London?",
             'We quote a fixed price on site before any long repair starts, so you know the cost before work begins. The price depends on the fault, the parts and the make of the cabinet. '
             'Our <a href="/blog/commercial-fridge-repair-cost-london/">commercial fridge repair cost guide</a> explains what a London quote should include.'),
        ],
    },
    "fridge-repair-london": {
        "h1": None,
        "lead": ('<p class="lead">Fridge repair in London for commercial kitchens,',
                 '<p class="lead"><strong>Fridge repair London</strong> for commercial kitchens,'),
        "svc": ("Fridge repair London", "Commercial fridge repair",
                "Same-day fridge repair and fridge service in London for commercial kitchens, shops, bars and hospitality businesses. "
                "24/7 emergency callout, F-Gas certified engineers, fixed price quoted on site. Commercial equipment only.",
                ["Fridge repair London", "Fridge repairs London", "Fridge service London",
                 "Emergency fridge repair London", "Commercial fridge repair"]),
        "faq": [
            ("Who offers fridge repair London for restaurants, shops and bars?",
             "Cold Direct offers same-day fridge repair London for commercial kitchens, restaurants, shops, bars and hotels. We attend 24/7, repair trade equipment only "
             "and quote a fixed price on site. Call 07983 759320 with your postcode, fridge make and fault."),
            ("Do you do fridge service London as well as emergency fridge repair?",
             "Yes. Planned fridge service visits cover condensers, door seals and temperature probes to reduce the risk of breakdowns, and we repair failed fridges around the clock. "
             "Call 07983 759320 to book either."),
        ],
    },
    "freezer-repair-london": {
        "h1": None,
        "lead": ('<p class="lead">Freezer repair in London for restaurants,',
                 '<p class="lead"><strong>Freezer repair London</strong> for restaurants,'),
        "svc": ("Freezer repair London", "Commercial freezer repair",
                "Same-day freezer repair and freezer service in London for restaurants, pubs, shops and catering kitchens: "
                "upright, chest, undercounter and walk-in freezers. 24/7 emergency callout, F-Gas certified engineers, fixed price quoted on site. Commercial only.",
                ["Freezer repair London", "Freezer repairs London", "Freezer service London",
                 "Emergency freezer repair London", "Commercial freezer repair"]),
        "faq": [
            ("Do you repair freezers that are icing up or running above -18°C in London?",
             "Yes. Freezer repair London covers iced evaporators, failed defrost heaters, worn door seals, controller faults and compressor trips on commercial upright, chest, undercounter and walk-in freezers. "
             "Probe the product, keep the door shut and call 07983 759320."),
            ("Is freezer repair London available at night and at weekends?",
             "Yes. We cover emergencies 24/7, with a 60–90 minute target across North and Central London and 2–4 hours across Greater London within the M25, subject to postcode and engineer availability."),
        ],
    },
    "commercial-freezer-repair-london": {
        "h1": ("<h1>Commercial Freezer Repair London &mdash; 24/7 Same-Day Emergency Engineers</h1>",
               "<h1>Commercial Freezer Repair London – Same-Day Walk-In &amp; Kitchen Freezer Engineers</h1>"),
        "lead": ('<p class="lead">Same-day emergency freezer repair for restaurants,',
                 '<p class="lead"><strong>Commercial freezer repair London</strong>: same-day emergency repair for restaurants,'),
        "svc": ("Commercial freezer repair London", "Commercial freezer repair",
                "24/7 same-day commercial freezer repair in London for restaurants, hotels, shops and catering kitchens: "
                "walk-in freezer rooms, upright, chest and blast freezers. F-Gas certified engineers, fixed price quoted on site. Commercial only.",
                ["Commercial freezer repair London", "Commercial freezer repairs", "Commercial freezer service",
                 "Walk-in freezer repair London", "Emergency commercial freezer repair"]),
        "faq": [
            ("Do you repair walk-in and kitchen freezers across London?",
             "Yes. Commercial freezer repair London covers walk-in freezer rooms, upright and chest freezers, undercounter units and blast freezers for restaurants, hotels, shops and catering sites. "
             "Call 07983 759320 with your postcode, make and fault."),
            ("What counts as a commercial freezer emergency?",
             "Product warming above -18°C, a high-temperature alarm, an iced evaporator or a compressor that keeps tripping. Keep the door shut, move high-risk stock if you can and call 07983 759320 for 24/7 emergency dispatch."),
        ],
    },
}


def do_money_pages():
    for slug, cfg in MONEY.items():
        text = read(ROOT / f"{slug}.html")
        if cfg["h1"]:
            text = sub1(text, cfg["h1"][0], cfg["h1"][1], f"{slug} h1")
        text = sub1(text, cfg["lead"][0], cfg["lead"][1], f"{slug} lead")
        text = add_brand_backlink(text, slug)
        text = add_accordion_items(text, slug, cfg["faq"])
        name, stype, desc, offers = cfg["svc"]
        text = update_local_schema(text, slug, svc_node(slug, name, stype, desc, offers))
        commit(slug, text)


# ---------------------------------------------------------------- cold room
COLD_ROOM_BLOCK = """<!-- CD-COLD-ROOM-COVERAGE -->
  <section class="section"><div class="wrap">
    <h2>Cold room repair London &amp; North London: 24/7 rapid response, no hidden call-out fees</h2>
    <p>Cold room repairs across London and North London are booked 24/7. Whether you search for <strong>cold room repair London</strong>, <strong>cold room repairs</strong> or cold room repair near me, you reach the same F-Gas certified engineers: walk-in chillers and freezer rooms in Enfield, Barnet, Finchley, Camden, Islington, Hackney, Haringey, Westminster and the City, plus the Hertfordshire and Essex towns inside our 25 mile radius. We quote a fixed price on site before any long repair starts, so there are no hidden call-out fees. Call <a href="tel:+447983759320">07983 759320</a> now.</p>
  </div></section>"""


def do_cold_room():
    slug = "cold-room-repair-london"
    text = read(ROOT / f"{slug}.html")
    text = sub1(
        text,
        '<p class="lead">Emergency <strong>cold room repair London</strong> for walk-in chillers in restaurants, butchers, hotels, supermarkets and production kitchens. F-Gas certified engineers on site in 2–4 hours when your room temperature is climbing.</p>',
        '<p class="lead">Emergency <strong>cold room repair London</strong> and <strong>cold room repairs</strong> across London and North London for walk-in chillers and freezer rooms in restaurants, butchers, hotels, supermarkets and production kitchens. F-Gas certified engineers, 24/7 rapid response (2–4 hours, with a 60–90 minute target across North &amp; Central London) and no hidden call-out fees.</p>',
        f"{slug} lead",
    )
    text = sub1(text, "<h2>Walk-in cold rooms are the backbone of a trade kitchen</h2>",
                "<h2>Cold room repairs London: walk-in cold rooms are the backbone of a trade kitchen</h2>", f"{slug} h2a")
    text = sub1(text, "<h2>Areas covered</h2>",
                "<h2>Cold room repair near me: areas covered across London &amp; North London</h2>", f"{slug} h2b")
    text = sub1(text, "<h2>Frequently Asked Questions — Walk-In Cold Room Repair London</h2>",
                "<h2>Frequently Asked Questions — Cold Room Repair London &amp; Cold Room Repairs</h2>", f"{slug} h2c")
    text = add_brand_backlink(text, slug)
    text = insert_before_ctaband(text, "<!-- CD-COLD-ROOM-COVERAGE -->", "  " + COLD_ROOM_BLOCK)
    text = add_accordion_items(text, slug, [
        ("Do you offer cold room repairs across London and North London?",
         "Yes. Our cold room repairs cover London and North London, including Enfield, Barnet, Finchley, Camden, Islington, Hackney, Haringey, Westminster and the City, plus the Hertfordshire and Essex towns inside our 25 mile radius. "
         "Searching for cold room repair near me? Call 07983 759320 with your postcode."),
        ("Are there hidden call-out fees for cold room repair London?",
         "No. We quote a fixed price on site before any long repair starts, so there are no hidden call-out fees. Call 07983 759320, 0800 112 3427 or 0203 952 4822 to book 24/7 rapid response."),
    ])
    text = update_local_schema(text, slug, svc_node(
        slug, "Cold room repair London", "Walk-in cold room repair",
        "24/7 cold room repair London and North London: rapid-response walk-in chiller and freezer room repairs by F-Gas certified engineers, "
        "fixed price quoted on site with no hidden call-out fees.",
        ["Cold room repair London", "Cold room repairs London", "Cold room repair near me",
         "Cold room service London", "Emergency cold room repair", "Walk-in chiller repair London"]))
    commit(slug, text)


# ---------------------------------------------------------------- ice machine + ice cream
ICE_RELATED = """<!-- CD-ICE-MACHINE-RELATED -->
  <section class="section"><div class="wrap">
    <p>Catering and hospitality sites usually need more than ice. See <a href="/catering-repair-london/">catering repair London</a> and <a href="/commercial-appliances-repair-london/">commercial catering repair London</a> for kitchen refrigeration, <a href="/cold-room-repair-london/">cold room repair London</a> for walk-in rooms, <a href="/cellar-cooler-repair-london/">cellar cooler repair London</a> for pubs and bars, and <a href="/ice-cream-machine-repair-london/">commercial ice cream &amp; soft serve machine repair London</a>.</p>
  </div></section>"""


def do_ice_machine():
    slug = "ice-machine-repair-london"
    text = read(ROOT / f"{slug}.html")
    text = sub1(text, "<h1>Ice Machine Same-Day Repair London</h1>",
                "<h1>Ice Machine Repairs &amp; Service London – 24/7 Commercial Engineers</h1>", f"{slug} h1")
    text = sub1(
        text,
        '<p class="lead">Commercial ice machine repair for pubs, restaurants, hotels and bars across North London and London. 24/7 emergency. 25 mile radius.</p>',
        '<p class="lead"><strong>Ice machine repairs &amp; service London</strong> for pubs, restaurants, hotels and bars across North London and London. 24/7 emergency repair, planned PPM service and fixed-price quotes. 25 mile radius.</p>',
        f"{slug} lead",
    )
    text = sub1(text, "<h2>Commercial ice machine engineers in North London</h2>",
                "<h2>Ice machine repairs &amp; service London: commercial engineers in North London</h2>", f"{slug} h2a")
    text = sub1(text, "<h2>Ice machine service London</h2>",
                "<h2>Ice machine service London: descale, filter, drain &amp; harvest test</h2>", f"{slug} h2b")
    text = sub1(text, "<h2>FAQ</h2>", "<h2>Ice machine repairs &amp; service FAQ</h2>", f"{slug} h2c")
    text = sub1(text, "<h2>Frequently Asked Questions — Ice Machine Repair London</h2>",
                "<h2>Frequently Asked Questions — Ice Machine Repairs &amp; Service London</h2>", f"{slug} h2d")
    text = add_brand_backlink(text, slug)
    text = insert_before_ctaband(text, "<!-- CD-ICE-MACHINE-RELATED -->", "  " + ICE_RELATED)
    text = add_accordion_items(text, slug, [
        ("What does an ice machine service in London include?",
         "A planned ice machine service London visit covers descaling, water filter change, drain clearance, condenser clean and a harvest test, so cubes stay food-safe and the bin passes an EHO check. We still repair failed ice makers 24/7."),
        ("How quickly can you attend an ice machine repair in London?",
         "We target 60–90 minutes across North &amp; Central London and 2–4 hours across Greater London within the M25, 24/7, subject to postcode and engineer availability. Call 07983 759320."),
    ])
    text = update_local_schema(text, slug, svc_node(
        slug, "Ice Machine Repairs & Service London", "Commercial ice machine repair and service",
        "24/7 ice machine repairs and planned ice machine service in London for pubs, restaurants, hotels and bars: "
        "cube, flake and nugget machines from Hoshizaki, Scotsman, Ice-O-Matic and Polar. F-Gas certified engineers, fixed price quoted on site. Commercial only.",
        ["Ice machine repairs London", "Ice machine service London", "Ice machine repair London",
         "Emergency ice machine repair London", "Commercial ice machine repair", "Hoshizaki ice machine repair London"]),
        use_plain=True, replace_service=True)
    commit(slug, text)


ICE_CREAM_CTA = """<!-- CD-ICE-CREAM-CTA -->
  <section class="section"><div class="wrap">
    <h2>Soft serve or ice cream machine down? Book a commercial engineer now</h2>
    <p>We repair <strong>commercial ice cream &amp; soft serve machines in London</strong> for shops, restaurants, hotels and parlours: <a class="btn" href="tel:+447983759320">Call 07983 759320</a> <a class="btn" href="tel:+442039524822">0203 952 4822</a>. We repair commercial machines only, so if you are looking for a home ice cream maker, contact the manufacturer.</p>
    <p>Trade sites also rely on <a href="/commercial-freezer-repair-london/">commercial freezer repair London</a> for scoop-ready storage, <a href="/commercial-fridge-repair-london/">commercial fridge repair London</a> for dairy and mix, <a href="/cold-room-repair-london/">cold room repair London</a> for walk-in stock and <a href="/ice-machine-repair-london/">ice machine repairs &amp; service London</a> for cube ice.</p>
  </div></section>"""


def do_ice_cream():
    slug = "ice-cream-machine-repair-london"
    text = read(ROOT / f"{slug}.html")
    text = sub1(text, "<h1>Ice Cream Machine Same-Day Repair London</h1>",
                "<h1>Commercial Ice Cream &amp; Soft Serve Machine Repair London</h1>", f"{slug} h1")
    text = sub1(
        text,
        '<p class="lead">Commercial ice cream and gelato machine repair for shops,',
        '<p class="lead"><strong>Commercial ice cream &amp; soft serve machine repair London</strong> for shops,',
        f"{slug} lead",
    )
    text = sub1(text, "<h2>Commercial ice cream machine repair in North London</h2>",
                "<h2>Commercial ice cream &amp; soft serve machine repair in North London</h2>", f"{slug} h2a")
    junk = re.search(r"\n    <p>The cream and pink theme on this page is for branding only\..*?</p>", text, re.S)
    if junk:
        text = text[: junk.start()] + text[junk.end():]
    text = sub1(text, "<h2>FAQ</h2>", "<h2>Commercial ice cream &amp; soft serve machine repair FAQ</h2>", f"{slug} h2b")
    text = sub1(text, '<a href="/ice-machine-repair-london">ice machine repair london</a>',
                '<a href="/ice-machine-repair-london/">ice machine repairs &amp; service London</a>', f"{slug} link1")
    text = sub1(text, '<a href="/freezer-repair-london">freezer repair London</a>',
                '<a href="/freezer-repair-london/">freezer repair London</a>', f"{slug} link2")
    text = add_brand_backlink(text, slug)
    text = insert_before_ctaband(text, "<!-- CD-ICE-CREAM-CTA -->", "  " + ICE_CREAM_CTA)
    text = add_plain_faq_items(text, slug, [
        ("Do you repair soft serve machines in London?",
         "Yes. We repair commercial soft serve and batch freezers (Carpigiani, Taylor, Bravo) in shops, restaurants, hotels and parlours. 24/7 emergency, commercial sites only. We do not repair or advise on domestic ice cream makers."),
        ("How quickly can you attend a commercial ice cream machine repair?",
         "We target 60–90 minutes across North &amp; Central London and 2–4 hours across Greater London within the M25, 24/7, subject to postcode and engineer availability. Call 07983 759320."),
    ])
    text = update_local_schema(text, slug, svc_node(
        slug, "Commercial Ice Cream & Soft Serve Machine Repair London", "Commercial ice cream machine repair",
        "24/7 commercial ice cream and soft serve machine repair and service in London for shops, restaurants, hotels and parlours: "
        "Carpigiani, Taylor and Bravo. F-Gas certified engineers, fixed price quoted on site. Commercial machines only.",
        ["Commercial ice cream machine repair London", "Soft serve machine repair London",
         "Ice cream machine service London", "Carpigiani repair London", "Taylor ice cream machine repair London"]),
        use_plain=True, replace_service=True)
    commit(slug, text, create_missing=True, require_identical=False)


# ---------------------------------------------------------------- catering pages: strong internal links to ice machine page
CATERING_ICE = """<!-- CD-ICE-MACHINE-LINK -->
  <section class="section"><div class="wrap">
    <p>Kitchens, bars and hotels depend on ice as much as on cold storage. Our engineers also handle <a href="/ice-machine-repair-london/">ice machine repairs &amp; service London</a> for cube, flake and nugget machines (including <a href="/hoshizaki-ice-machine-repair-london/">Hoshizaki ice machine repair London</a>) and <a href="/ice-cream-machine-repair-london/">commercial ice cream &amp; soft serve machine repair London</a>, often on the same visit as your fridge, freezer or <a href="/cold-room-repair-london/">cold room repair London</a>.</p>
  </div></section>"""


def do_catering_pages():
    for slug in ("catering-repair-london", "commercial-appliances-repair-london", "commercial-catering-repair-london"):
        if not (ROOT / f"{slug}.html").exists():
            continue
        text = read(ROOT / f"{slug}.html")
        text = insert_before_ctaband(text, "<!-- CD-ICE-MACHINE-LINK -->", "  " + CATERING_ICE)
        commit(slug, text)


# ---------------------------------------------------------------- homepage
HOME_MATRIX = (
    '<!-- CD-HERO-KEYWORD-MATRIX -->\n'
    '<div class="cd-kw-matrix" style="background:#f1f7fb;border-left:4px solid #00a99d;border-radius:8px;padding:16px 18px;margin:18px 0;">'
    '<p style="margin:0 0 10px;font-size:16px;line-height:1.65;color:#0a2540;">'
    'ColdDirect are <strong>commercial refrigeration &amp; air conditioning engineers in London</strong>: 24/7 emergency <strong>repair</strong> and planned <strong>service</strong> '
    'for restaurants, pubs, hotels, shops and supermarkets, with affordable fixed-rate quotes and repair at board and component level instead of main-dealer markups. '
    'Every service has its own dedicated page, so you reach the right engineers first time: '
    '<a href="/commercial-fridge-repair-london/">commercial fridge repair London</a>, '
    '<a href="/fridge-repair-london/">fridge repair London</a>, '
    '<a href="/freezer-repair-london/">freezer repair London</a>, '
    '<a href="/commercial-freezer-repair-london/">commercial freezer repair London</a>, '
    '<a href="/cold-room-repair-london/">cold room repair London</a>, '
    '<a href="/cellar-cooler-repair-london/">cellar cooler repair London</a>, '
    '<a href="/catering-repair-london/">catering repair London</a>, '
    '<a href="/commercial-appliances-repair-london/">commercial catering repair London</a>, '
    '<a href="/air-conditioning-repair-london/">air conditioning repair London</a> and '
    '<a href="/ice-machine-repair-london/">ice machine repairs &amp; service London</a>.</p>'
    '<ul style="display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0;list-style:none;">'
    + "".join(
        '<li style="display:inline-block;background:#fff;border:1px solid #bcd3e4;border-radius:999px;padding:5px 12px;font-size:13.5px;font-weight:700;color:#0a2540;">%s</li>' % t
        for t in [
            "Refrigeration engineers London",
            "Commercial refrigeration repair",
            "Air conditioning engineers London",
            "24/7 emergency callout",
            "Planned maintenance &amp; service",
            "F-Gas certified engineers",
            "Fixed-rate quotes",
        ]
    )
    + '</ul></div>\n<!-- /CD-HERO-KEYWORD-MATRIX -->'
)


def do_home():
    p = ROOT / "index.html"
    mirror = ROOT / "colddirect-public-html" / "index.html"
    text = read(p)
    if read(mirror) != text:
        raise SystemExit("[index] mirror differs from root before edit")
    text = sub1(
        text,
        "<h1>Emergency Commercial Refrigeration Repair London - Same Day Service</h1>",
        "<h1>Commercial Refrigeration &amp; Air Conditioning Engineers London – 24/7 Repair &amp; Service</h1>",
        "index h1",
    )
    m = re.search(r"<!-- CD-HERO-KEYWORD-MATRIX -->.*?<!-- /CD-HERO-KEYWORD-MATRIX -->", text, re.S)
    if not m:
        raise SystemExit("[index] hero matrix not found")
    if m.group(0) != HOME_MATRIX:
        text = text[: m.start()] + HOME_MATRIX + text[m.end():]
    text = sub1(text, '<a class="more" href="/cold-room-repair-london/">cold room repair london</a>',
                '<a class="more" href="/cold-room-repair-london/">cold room repair London</a>', "index card cold room")
    text = sub1(text, '<a class="more" href="/ice-machine-repair-london/">Ice machine repair London →</a>',
                '<a class="more" href="/ice-machine-repair-london/">ice machine repairs &amp; service London →</a>', "index card ice")
    text = sub1(text, '<a class="more" href="/cellar-cooler-repair-london">Cellar cooler repair →</a>',
                '<a class="more" href="/cellar-cooler-repair-london/">cellar cooler repair London →</a>', "index card cellar")
    text = sub1(
        text,
        '<meta property="og:title" content="Commercial Fridge &amp; Freezer Same-Day Repair London | 24/7 Emergency | ColdDirect">',
        '<meta property="og:title" content="Commercial Refrigeration &amp; Air Conditioning Engineers London | ColdDirect">',
        "index og:title",
    )
    text = sub1(
        text,
        '<meta property="og:description" content="Emergency same-day commercial fridge and freezer repair London. Trade kitchens only. 2-4 hour response. Foster, Williams, True. Call 07983 759320.">',
        '<meta property="og:description" content="Commercial refrigeration &amp; air conditioning engineers in London. 24/7 emergency repair and planned service for restaurants, pubs, hotels and shops. Call 07983 759320.">',
        "index og:desc",
    )
    # <title> + meta description: mirror the rules auto-seo.aspx applies nightly so the two never fight
    text = sub1(
        text,
        "<title>Commercial Fridge, Freezer & Cold Room Repair London | 24/7 Emergency | ColdDirect</title>",
        "<title>Commercial Refrigeration & Air Conditioning Engineers London | ColdDirect</title>",
        "index title",
    )
    text = sub1(
        text,
        '<meta name="description" content="24/7 emergency commercial fridge, freezer & cold room repair in London. 60–90 Min Response, Fixed-Rate Quotes, F-Gas Certified engineers. Call 0203 952 4822.">',
        '<meta name="description" content="Commercial refrigeration & air conditioning engineers in London. 24/7 emergency repair & service, fixed-rate quotes, F-Gas certified. Call 0203 952 4822.">',
        "index description",
    )
    if text == read(p) and read(mirror) == text:
        print("  = index: already up to date")
        return
    if CHECK:
        print("  ! index: would change")
        changed_files.append("index")
        return
    write(p, text)
    write(mirror, text)
    print("  + index: updated")
    changed_files.append("index")


# ---------------------------------------------------------------- head tags (mirror of the auto-seo.aspx rules)
HEADS = {
    "cold-room-repair-london": (
        "Cold Room Repair London | 24/7 Cold Room Repairs, No Hidden Fees",
        "24/7 cold room repair London & North London. Rapid-response cold room repairs by F-Gas engineers, no hidden call-out fees. Call 07983 759320.",
    ),
    "ice-machine-repair-london": (
        "Ice Machine Repairs & Service London | 24/7 Commercial Engineers",
        "24/7 ice machine repairs & service in London. Same-day engineers for Hoshizaki, Scotsman & Ice-O-Matic cube, flake & nugget ice makers. Call 0203 952 4822.",
    ),
    "ice-cream-machine-repair-london": (
        "Commercial Ice Cream & Soft Serve Machine Repair London | 24/7",
        "24/7 commercial ice cream & soft serve machine repair in London. Same-day engineers for Carpigiani, Taylor & Bravo. Trade sites only. Call 0203 952 4822.",
    ),
}


def set_meta(text, attr, key, value):
    pat = re.compile(r'(<meta\s+%s="%s"\s+content=")[^"]*(")' % (attr, re.escape(key)))
    if not pat.search(text):
        return text
    return pat.sub(lambda m: m.group(1) + value + m.group(2), text, count=1)


def do_heads():
    for slug, (title, desc) in HEADS.items():
        text = read(ROOT / f"{slug}.html")
        text = re.sub(r"<title>.*?</title>", lambda m: f"<title>{title}</title>", text, count=1, flags=re.S)
        text = re.sub(r'<meta name="description" content="[^"]*">',
                      lambda m: f'<meta name="description" content="{desc}">', text, count=1)
        og_t = title.replace("&", "&amp;")
        og_d = desc.replace("&", "&amp;")
        for attr, key, val in (("property", "og:title", og_t), ("property", "og:description", og_d),
                               ("name", "twitter:title", og_t), ("name", "twitter:description", og_d)):
            text = set_meta(text, attr, key, val)
        commit(slug, text, create_missing=(slug == "ice-cream-machine-repair-london"),
               require_identical=(slug != "ice-cream-machine-repair-london"))


def main():
    print("Cold Direct de-cannibalisation pass" + (" (check only)" if CHECK else ""))
    do_home()
    do_money_pages()
    do_cold_room()
    do_ice_machine()
    do_ice_cream()
    do_catering_pages()
    do_heads()
    print(f"done: {len(changed_files)} page(s) {'would change' if CHECK else 'changed'}")
    if CHECK and changed_files:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
