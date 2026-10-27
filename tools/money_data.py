#!/usr/bin/env python3
"""Single source of truth for the 9 core money hubs (+ homepage audio).

Used by:
  tools/money_keywords_apply.py   titles / descriptions / og+twitter / body block / aspx moneyMeta
  tools/generate_seo_audio.py     spoken audio summaries + AudioObject / Speakable schema
  tools/blog_money_links.py       contextual internal-link blocks on the blog
  tools/seo_integrity_check.py    read-only 24h enforcement against the LIVE site

Commercial refrigeration / AC only - never domestic. Official phone only.
Titles/H1s are NOT rewritten by nightly jobs: this data changes only by a deliberate commit.
"""
import re

SITE = "https://www.colddirect.co.uk"
PHONE_DISPLAY = "07983 759320"
PHONE_TEL = "tel:+447983759320"
OG_IMAGE = SITE + "/images/og-colddirect-london.jpg"

# slug -> data. Keys:
#  kw        primary keyword (display case)
#  title     <title> (<= 65 chars) - mirrored into auto-seo.aspx moneyMeta
#  desc      meta description (<= 160 chars, official mobile number)
#  offers    extra OfferCatalog variations (modifier-rich) appended to moneyMeta
#  audio     spoken summary script (plain text)
#  intro/cost/cover/faq1/faq2   body block copy
#  anchors   (variant A, variant B) natural anchor text for blog link blocks
MONEY = {
    "fridge-repair-london": {
        "kw": "Fridge repair London",
        "title": "Fridge Repair London | Same-Day 24/7 Emergency Engineers",
        "desc": "Fridge repair London for restaurants, pubs and shops: same-day 24/7 emergency repairs and service, fixed diagnostic call-out. Call 07983 759320.",
        "offers": ['Same day fridge repair London', '24 hour emergency fridge repair London', 'Affordable fridge repair London with fixed diagnostic call-out', 'Fridge repair London', 'Fridge repairs London', 'Fridge service London', 'Fridge services London', 'Emergency fridge repair London', 'Same day fridge repairs London', '24/7 fridge repair London', 'Cheap fridge repair London', 'Affordable fridge repair London', 'Fridge repair near me', 'Annual fridge maintenance and servicing London', 'Low-cost fridge diagnostics London'],
        "audio": "Cold Direct fridge repair London. If a commercial fridge in your restaurant, pub, cafe or shop stops cooling, our London engineers offer same day emergency repairs, twenty four hours a day, seven days a week. We charge a fixed diagnostic call-out, so the cost is clear and affordable before any repair work begins. We repair commercial refrigeration only. Call Cold Direct now on zero seven nine eight three, seven five nine, three two zero.",
        "intro": "When a commercial fridge fails, stock is at risk within hours. Our fridge repair London service sends F-Gas certified London engineers for same-day emergency repairs on kitchen fridges, under-counter units, display chillers and bar fridges, around the clock.",
        "cost": "Every fridge repair starts with a fixed diagnostic call-out, so you know the cost up front. Parts and labour are quoted transparently and only go ahead once you approve them.",
        "cover": "Our engineers cover London and the surrounding boroughs, 24 hours a day, 7 days a week, including nights, weekends and bank holidays, with vans stocked for the most common fridge repairs.",
        "faq1": "Yes. Book before midday and we aim for a same-day visit; true emergencies are dispatched immediately, 24/7.",
        "faq2": "You pay a fixed diagnostic call-out first. Any repair is then quoted transparently, so fridge repair stays affordable with no hidden extras.",
        "anchors": ["fridge repair London (same-day emergency)", "24/7 fridge repair London by commercial engineers"],
    },
    "freezer-repair-london": {
        "kw": "Freezer repair London",
        "title": "Freezer Repair London | Same-Day 24/7 Emergency Engineers",
        "desc": "Freezer repair London for kitchens, bars and shops: same-day 24/7 emergency repairs and service, fixed diagnostic call-out. Call 07983 759320.",
        "offers": ['Same day freezer repair London', '24 hour emergency freezer repair London', 'Affordable freezer repair London with fixed diagnostic call-out', 'Freezer repair London', 'Freezer repairs London', 'Freezer service London', 'Freezer services London', 'Emergency freezer repair London', 'Same day freezer repairs London', '24/7 freezer repair London', 'Cheap freezer repair London', 'Affordable freezer repair London', 'Freezer repair near me', 'Annual freezer maintenance and servicing London', 'Low-cost freezer diagnostics London'],
        "audio": "Cold Direct freezer repair London. A failed commercial freezer can ruin thousands of pounds of frozen stock overnight. Our London engineers provide same day emergency freezer repairs, twenty four hours a day, seven days a week, with a fixed diagnostic call-out and transparent, affordable pricing. Commercial freezers only. Call Cold Direct on zero seven nine eight three, seven five nine, three two zero.",
        "intro": "Frozen stock cannot wait. Our freezer repair London service dispatches F-Gas certified London engineers for same-day emergency repairs on kitchen freezers, display freezers and chest units, 24/7.",
        "cost": "We charge a fixed diagnostic call-out to find the fault, then quote the freezer repair clearly before starting. Affordable, transparent and approved by you first.",
        "cover": "Emergency freezer repairs are available across London every hour of every day, with engineers carrying common compressors, controllers and defrost parts.",
        "faq1": "Yes. We prioritise freezer failures for same-day attendance and dispatch genuine emergencies straight away, 24 hours a day.",
        "faq2": "The first cost is a fixed diagnostic call-out. The repair is then quoted transparently so you can approve it before work starts.",
        "anchors": ["freezer repair London (24/7 emergency)", "same day freezer repair London for kitchens and shops"],
    },
    "commercial-fridge-repair-london": {
        "kw": "Commercial fridge repair London",
        "title": "Commercial Fridge Repair London | 24/7 Same-Day Service",
        "desc": "Commercial fridge repair London: 24/7 emergency and same-day repairs, fixed diagnostic call-out, F-Gas certified London engineers. Call 07983 759320.",
        "offers": ['Same day commercial fridge repair London', '24 hour emergency commercial fridge repair London', 'Affordable commercial fridge repair London with fixed diagnostic call-out', 'Commercial fridge repair London', 'Commercial fridge repairs London', 'Commercial fridge service London', 'Commercial fridge services London', 'Emergency commercial fridge repair London', 'Same day commercial fridge repairs London', '24/7 commercial fridge repair London', 'Cheap commercial fridge repair London', 'Affordable commercial fridge repair London', 'Commercial fridge repair near me', 'Annual commercial fridge maintenance and servicing London', 'Low-cost commercial fridge diagnostics London'],
        "audio": "Cold Direct commercial fridge repair London. For restaurants, hotels, pubs, supermarkets and food producers, we offer twenty four seven emergency and same day commercial fridge repairs with F-Gas certified London engineers. A fixed diagnostic call-out keeps the cost transparent and affordable. Call Cold Direct on zero seven nine eight three, seven five nine, three two zero.",
        "intro": "Our commercial fridge repair London service covers prep fridges, upright and under-counter units, display chillers and walk-in chillers, with same-day emergency attendance by F-Gas certified London engineers.",
        "cost": "A fixed diagnostic call-out identifies the fault and the repair is quoted clearly afterwards, so commercial fridge repair stays affordable and transparent.",
        "cover": "Our London engineers are on call 24 hours a day, 7 days a week for emergency commercial fridge repairs, including overnight and bank holidays.",
        "faq1": "Yes. Urgent commercial fridge failures are dispatched immediately and standard faults are targeted for same-day repair.",
        "faq2": "You pay a fixed diagnostic call-out, then receive a transparent repair quote. Nothing proceeds without your approval.",
        "anchors": ["same day commercial fridge repair London", "24 hour emergency commercial fridge repair London"],
    },
    "commercial-freezer-repair-london": {
        "kw": "Commercial freezer repair London",
        "title": "Commercial Freezer Repair London | 24/7 Same-Day Service",
        "desc": "Commercial freezer repair London: 24/7 emergency and same-day repairs, fixed diagnostic call-out, walk-in and kitchen freezers. Call 07983 759320.",
        "offers": ['Same day commercial freezer repair London', '24 hour emergency commercial freezer repair London', 'Affordable commercial freezer repair London with fixed diagnostic call-out', 'Commercial freezer repair London', 'Commercial freezer repairs London', 'Commercial freezer service London', 'Commercial freezer services London', 'Emergency commercial freezer repair London', 'Same day commercial freezer repairs London', '24/7 commercial freezer repair London', 'Cheap commercial freezer repair London', 'Affordable commercial freezer repair London', 'Commercial freezer repair near me', 'Annual commercial freezer maintenance and servicing London', 'Low-cost commercial freezer diagnostics London'],
        "audio": "Cold Direct commercial freezer repair London. When a walk-in or kitchen freezer fails, every hour counts. Our London engineers provide twenty four hour emergency and same day commercial freezer repairs, with a fixed diagnostic call-out and transparent, affordable pricing. Call Cold Direct on zero seven nine eight three, seven five nine, three two zero.",
        "intro": "Our commercial freezer repair London service covers walk-in freezers, blast freezers, upright and chest freezers, with 24/7 emergency response and same-day repairs by London engineers.",
        "cost": "Diagnosis is a fixed diagnostic call-out; the commercial freezer repair is then quoted transparently, keeping cost affordable and predictable.",
        "cover": "Emergency commercial freezer repairs run 24/7 across London, with engineers dispatched day and night to protect your frozen stock.",
        "faq1": "Yes. Commercial freezer failures are treated as emergencies, dispatched immediately and repaired the same day wherever parts allow.",
        "faq2": "A fixed diagnostic call-out covers diagnosis, followed by a clear written quote for the repair, so there are no surprises.",
        "anchors": ["24 hour emergency commercial freezer repair London", "same day commercial freezer repair London"],
    },
    "catering-repair-london": {
        "kw": "Catering repair London",
        "title": "Catering Repair London | 24/7 Same-Day Service",
        "desc": "Catering repair London for restaurant and takeaway kitchens: same-day 24/7 emergency repairs and service, fixed diagnostic call-out. Call 07983 759320.",
        "offers": ['Same day catering repair London', '24 hour emergency catering repair London', 'Affordable catering repair London with fixed diagnostic call-out', 'Catering repair London', 'Catering repairs London', 'Catering service London', 'Catering services London', 'Emergency catering repair London', 'Same day catering repairs London', '24/7 catering repair London', 'Cheap catering repair London', 'Affordable catering repair London', 'Catering repair near me', 'Annual catering maintenance and servicing London', 'Low-cost catering diagnostics London'],
        "audio": "Cold Direct catering repair London. Restaurants, takeaways, cafes and catering kitchens rely on refrigeration that works. Our London engineers provide same day, twenty four seven emergency catering repair for kitchen fridges, freezers and chillers, with a fixed diagnostic call-out and affordable transparent pricing. Call Cold Direct on zero seven nine eight three, seven five nine, three two zero.",
        "intro": "Kitchens cannot trade without cold storage. Our catering repair London service sends London engineers for same-day emergency repairs on catering fridges, freezers, prep counters and chillers, 24/7.",
        "cost": "Catering repair starts with a fixed diagnostic call-out, followed by a transparent repair quote, so the cost for your kitchen is affordable and agreed in advance.",
        "cover": "We repair refrigeration for catering businesses across London at any hour, with out-of-hours attendance for late-night and early-morning kitchens.",
        "faq1": "Yes. Kitchen refrigeration failures are dispatched as emergencies, and we aim for same-day catering repair across London.",
        "faq2": "You pay a fixed diagnostic call-out and then approve a transparent quote. That keeps catering repair affordable with no hidden extras.",
        "anchors": ["affordable catering repair London", "same day catering repair London for restaurant kitchens"],
    },
    "commercial-appliances-repair-london": {
        "kw": "Commercial catering repair London",
        "title": "Commercial Catering Repair London | 24/7 Same-Day Engineers",
        "desc": "Commercial catering repair London: 24/7 same-day emergency repairs and service for kitchen refrigeration and ice machines. Fixed call-out. 07983 759320.",
        "offers": ['Same day commercial catering repair London', '24 hour emergency commercial catering repair London', 'Affordable commercial catering repair London with fixed diagnostic call-out', 'Commercial catering repair London', 'Commercial catering repairs London', 'Commercial catering service London', 'Commercial catering services London', 'Emergency commercial catering repair London', 'Same day commercial catering repairs London', '24/7 commercial catering repair London', 'Cheap commercial catering repair London', 'Affordable commercial catering repair London', 'Commercial catering repair near me', 'Annual commercial catering maintenance and servicing London', 'Low-cost commercial catering diagnostics London'],
        "audio": "Cold Direct commercial catering repair London. Our hub covers commercial kitchen refrigeration and catering appliances, including chillers, freezers and ice machines. London engineers offer same day, twenty four seven emergency repairs with a fixed diagnostic call-out and transparent pricing. Call Cold Direct on zero seven nine eight three, seven five nine, three two zero.",
        "intro": "This is our commercial catering repair London hub: emergency repairs and servicing for the refrigeration and ice-making equipment that keeps professional kitchens running.",
        "cost": "Commercial catering repair begins with a fixed diagnostic call-out, then a transparent quote, so costs stay affordable and clear.",
        "cover": "Our London engineers handle commercial catering repair 24 hours a day, 7 days a week, with same-day visits wherever possible.",
        "faq1": "Yes. We offer same-day emergency commercial catering repair across London, dispatching urgent failures immediately.",
        "faq2": "A fixed diagnostic call-out covers diagnosis; the repair is quoted transparently and only proceeds with your approval.",
        "anchors": ["commercial catering repair London (emergency kitchen refrigeration)", "24/7 commercial catering repair London"],
    },
    "cold-room-repair-london": {
        "kw": "Cold room repair London",
        "title": "Cold Room Repair London | 24/7 Same-Day Emergency Repairs",
        "desc": "Cold room repair London: 24/7 same-day emergency repairs and service by London engineers. Affordable, fixed diagnostic call-out. Call 07983 759320.",
        "offers": ['Same day cold room repair London', '24 hour emergency cold room repair London', 'Affordable cold room repair London with fixed diagnostic call-out', 'Cold room repair London', 'Cold room repairs London', 'Cold room service London', 'Cold room services London', 'Emergency cold room repair London', 'Same day cold room repairs London', '24/7 cold room repair London', 'Cheap cold room repair London', 'Affordable cold room repair London', 'Cold room repair near me', 'Annual cold room maintenance and servicing London', 'Low-cost cold room diagnostics London'],
        "audio": "Cold Direct cold room repair London. If your walk-in cold room or freezer room loses temperature, our London engineers provide same day emergency repair twenty four hours a day, seven days a week. A fixed diagnostic call-out keeps costs affordable and transparent. Call Cold Direct on zero seven nine eight three, seven five nine, three two zero.",
        "intro": "Walk-in cold rooms hold your most valuable stock. Our cold room repair London service delivers same-day emergency repairs and servicing for chiller rooms and freezer rooms, 24/7.",
        "cost": "A fixed diagnostic call-out pinpoints the cold room fault, then the repair is quoted transparently, keeping the cost affordable.",
        "cover": "London engineers attend cold room failures day and night, with experience across evaporators, condensing units, door seals and controllers.",
        "faq1": "Yes. A cold room losing temperature is an emergency; we dispatch immediately and aim to complete repairs the same day.",
        "faq2": "You pay a fixed diagnostic call-out and then receive a clear quote for the repair, with no hidden fees.",
        "anchors": ["same day cold room repair London", "24/7 cold room repair London for walk-in rooms"],
    },
    "air-conditioning-repair-london": {
        "kw": "Air conditioning repair London",
        "title": "Air Conditioning Repair London | 24/7 Same-Day Emergency AC",
        "desc": "Air conditioning repair London for offices, shops and server rooms: 24/7 same-day emergency repairs, fixed diagnostic call-out. Call 07983 759320.",
        "offers": ['Same day air conditioning repair London', '24 hour emergency air conditioning repair London', 'Affordable air conditioning repair London with fixed diagnostic call-out', 'Air conditioning repair London', 'Air conditioning repairs London', 'Air conditioning service London', 'Air conditioning services London', 'Emergency air conditioning repair London', 'Same day air conditioning repairs London', '24/7 air conditioning repair London', 'Cheap air conditioning repair London', 'Affordable air conditioning repair London', 'Air conditioning repair near me', 'Annual air conditioning maintenance and servicing London', 'Low-cost air conditioning diagnostics London'],
        "audio": "Cold Direct air conditioning repair London. When commercial air conditioning fails in an office, shop or server room, our London engineers provide same day emergency repairs, twenty four seven, with a fixed diagnostic call-out and affordable transparent pricing. Commercial systems only. Call Cold Direct on zero seven nine eight three, seven five nine, three two zero.",
        "intro": "Our air conditioning repair London service covers commercial split systems, cassette units and VRV/VRF systems, with same-day emergency repairs and servicing by F-Gas certified engineers.",
        "cost": "We charge a fixed diagnostic call-out to identify the fault, then give a transparent repair quote, so air conditioning repair is affordable and clear.",
        "cover": "Emergency commercial AC repairs are available 24/7 across London, including heatwave peaks when demand is highest.",
        "faq1": "Yes. We prioritise failed commercial air conditioning and aim for same-day repair; emergencies are dispatched around the clock.",
        "faq2": "A fixed diagnostic call-out comes first, then a transparent quote for the repair, so you approve costs before work begins.",
        "anchors": ["24/7 air conditioning repair London", "same day air conditioning repair London for businesses"],
    },
    "cellar-cooler-repair-london": {
        "kw": "Cellar repair London",
        "title": "Cellar Repair London | 24/7 Pub and Bar Engineers",
        "desc": "Cellar repair London for pubs and bars: same-day 24/7 emergency cellar cooler repairs and service, fixed diagnostic call-out. Call 07983 759320.",
        "offers": ['Same day cellar repair London', '24 hour emergency cellar cooler repair London', 'Affordable cellar repair London with fixed diagnostic call-out', 'Cellar cooler repair London', 'Cellar cooler repairs London', 'Cellar cooler service London', 'Cellar cooler services London', 'Emergency cellar cooler repair London', 'Same day cellar cooler repairs London', '24/7 cellar cooler repair London', 'Cheap cellar cooler repair London', 'Affordable cellar cooler repair London', 'Cellar cooler repair near me', 'Annual cellar cooler maintenance and servicing London', 'Low-cost cellar cooler diagnostics London'],
        "audio": "Cold Direct cellar repair London. Warm beer means lost sales. Our London engineers repair pub and bar cellar coolers with same day emergency visits, twenty four hours a day, seven days a week, for a fixed diagnostic call-out and affordable transparent pricing. Call Cold Direct on zero seven nine eight three, seven five nine, three two zero.",
        "intro": "A cellar that runs warm costs a pub or bar money every hour. Our cellar repair London service delivers same-day emergency repairs on cellar coolers and cooling systems, 24/7.",
        "cost": "A fixed diagnostic call-out finds the cellar cooling fault and the repair is quoted transparently, keeping cellar repair affordable.",
        "cover": "London engineers attend pubs, bars and restaurants at any hour, including weekends when cellars are under the most pressure.",
        "faq1": "Yes. A failed cellar cooler is dispatched as an emergency and we aim for same-day repair across London.",
        "faq2": "You pay a fixed diagnostic call-out, then approve a transparent repair quote before any work starts.",
        "anchors": ["cellar repair London for pubs and bars", "same day cellar cooler repair London"],
    },
}

# Natural word-order and high-intent coverage. One concise visible paragraph per hub;
# deliberately not a list of every mechanical permutation (which would read as keyword stuffing).
SEMANTIC = {
    "fridge-repair-london": "For customers searching London fridge repair or London fridge service, our commercial technicians provide local diagnostics, breakdown repairs and planned maintenance, with urgent same-day call-outs across London.",
    "freezer-repair-london": "When you need emergency freezer repair London or a local freezer service, our commercial engineers diagnose and fix temperature failures quickly, with same-day call-outs and planned maintenance available across London.",
    "commercial-fridge-repair-london": "Our London commercial fridge repair and service team handles urgent breakdown diagnostics for professional kitchens, with local technicians, same-day call-outs and planned maintenance for commercial sites across London.",
    "commercial-freezer-repair-london": "For London commercial freezer repair, servicing or urgent breakdown diagnostics, our local technicians provide same-day emergency call-outs and planned maintenance for professional kitchens and food businesses.",
    "catering-repair-london": "Our London catering repair and service engineers cover urgent refrigeration breakdowns, diagnostics and planned maintenance for professional caterers, with same-day emergency call-outs across London.",
    "commercial-appliances-repair-london": "For commercial catering equipment repair London or commercial appliance engineers London, our technicians diagnose refrigeration and ice-machine faults, with emergency repairs, servicing and maintenance for professional kitchens.",
    "cold-room-repair-london": "For same day cold room repairs London or a planned cold room service, our local engineers provide emergency breakdown diagnostics, repairs and maintenance for walk-in chillers and freezer rooms.",
    "air-conditioning-repair-london": "Our London air conditioning repair and service engineers cover commercial breakdown diagnostics, urgent fixes and planned maintenance, with same-day emergency call-outs for offices, shops and server rooms.",
    "cellar-cooler-repair-london": "For beer cellar cooler service London or urgent cellar repairs, our local engineers diagnose cooling faults and provide same-day emergency call-outs, repairs and planned maintenance for pubs, bars and restaurants.",
}
for _slug, _semantic in SEMANTIC.items():
    MONEY[_slug]["semantic"] = _semantic

HOME_AUDIO = {
    "slug": "",
    "file": "colddirect-home",
    "name": "Cold Direct - Commercial Refrigeration Repair London (audio summary)",
    "script": "Welcome to Cold Direct, London's commercial refrigeration and air conditioning repair specialists. We provide twenty four seven emergency and same day repairs for commercial fridges, freezers, cold rooms, catering equipment, cellar coolers and air conditioning, with a fixed diagnostic call-out and transparent affordable pricing. Call Cold Direct on zero seven nine eight three, seven five nine, three two zero.",
}

# Blog posts and the index: all 9 hubs in a stable order, so every post links to every hub.
HUB_ORDER = [
    "commercial-freezer-repair-london", "commercial-fridge-repair-london", "cold-room-repair-london",
    "catering-repair-london", "commercial-appliances-repair-london", "air-conditioning-repair-london",
    "cellar-cooler-repair-london", "fridge-repair-london", "freezer-repair-london",
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def aspx_js_escape(s):
    """Same escaping style the aspx already uses (en-dash etc. as \\u escapes; none needed here)."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def audio_pages():
    """(slug, file_stem, display_name, script) for the 9 hubs + homepage."""
    out = []
    for slug in HUB_ORDER:
        d = MONEY[slug]
        out.append((slug, slug, d["kw"] + " - 24/7 same-day emergency service (audio summary)", d["audio"]))
    out.append((HOME_AUDIO["slug"], HOME_AUDIO["file"], HOME_AUDIO["name"], HOME_AUDIO["script"]))
    return out


def selftest():
    seen_t, seen_d = set(), set()
    for slug, d in MONEY.items():
        assert len(d["title"]) <= 70, (slug, len(d["title"]))
        assert 100 <= len(d["desc"]) <= 160, (slug, len(d["desc"]))
        assert PHONE_DISPLAY in d["desc"], slug
        # auto-seo.aspx writes title/description raw into the HTML: an '&' (or other escapable char) would make the
        # repo copy (escaped) and the aspx output (raw) flip-flop every run
        assert not re.search(r"[&<>\"]", d["title"] + d["desc"]), slug
        assert d["title"] not in seen_t and d["desc"] not in seen_d, slug
        seen_t.add(d["title"]); seen_d.add(d["desc"])
        assert len(d["offers"]) >= 3 and len(d["anchors"]) == 2
        for k in ("intro", "cost", "cover", "faq1", "faq2", "audio"):
            assert d[k].strip(), (slug, k)
        assert "semantic" in d and d["semantic"].strip(), (slug, "missing semantic word-order copy")
        assert not re.search(r"domestic|household|home appliance", " ".join(str(v) for v in d.values()), re.I), slug
    assert "London fridge repair" in MONEY["fridge-repair-london"]["semantic"]
    assert "London fridge service" in MONEY["fridge-repair-london"]["semantic"]
    assert "emergency freezer repair London" in MONEY["freezer-repair-london"]["semantic"]
    assert "same day cold room repairs London" in MONEY["cold-room-repair-london"]["semantic"]
    assert "beer cellar cooler service London" in MONEY["cellar-cooler-repair-london"]["semantic"]
    assert "commercial catering equipment repair London" in MONEY["commercial-appliances-repair-london"]["semantic"]
    assert "commercial appliance engineers London" in MONEY["commercial-appliances-repair-london"]["semantic"]
    assert sorted(HUB_ORDER) == sorted(MONEY)
    print("money_data selftest OK:", len(MONEY), "hubs; longest title", max(len(d["title"]) for d in MONEY.values()))


if __name__ == "__main__":
    selftest()
