#!/usr/bin/env python3
"""Inject CD-TOP3-RANK-BOOSTER-V5 body + expand moneyMeta OfferCatalog (idempotent).

Does NOT rewrite <title>, <h1>, or <meta name="description">.

  python tools/top3_rank_booster_v5.py --apply | --check | --selftest
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import money_data as md  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MIRROR = ROOT / "colddirect-public-html"
ASPX = ROOT / "auto-seo.aspx"

START, END = "<!-- CD-TOP3-RANK-BOOSTER-V5 -->", "<!-- /CD-TOP3-RANK-BOOSTER-V5 -->"
SCHEMA_S, SCHEMA_E = "<!-- CD-TOP3-SCHEMA-V5 -->", "<!-- /CD-TOP3-SCHEMA-V5 -->"
BLOCK_RX = re.compile(re.escape(START) + r"[\s\S]*?" + re.escape(END) + r"(?:\r?\n)?")
SCHEMA_RX = re.compile(re.escape(SCHEMA_S) + r"[\s\S]*?" + re.escape(SCHEMA_E) + r"(?:\r?\n)?")
LIT = r'"(?:[^"\\]|\\.)*"'

# Equipment label used in H2/H3 and OfferCatalog strings (never rewrite locked titles).
EQUIP = {
    "fridge-repair-london": "Fridge",
    "freezer-repair-london": "Freezer",
    "commercial-fridge-repair-london": "Commercial fridge",
    "commercial-freezer-repair-london": "Commercial freezer",
    "cold-room-repair-london": "Cold room",
    "catering-repair-london": "Catering",
    "commercial-appliances-repair-london": "Commercial catering",
    "air-conditioning-repair-london": "Air conditioning",
    "cellar-cooler-repair-london": "Cellar cooler",
}

HOME_EQUIP = "Commercial refrigeration"


def offer_names(equip: str) -> list[str]:
    e = equip
    el = e[0].lower() + e[1:] if e else e
    return [
        f"{e} repair London",
        f"{e} repairs London",
        f"{e} service London",
        f"{e} services London",
        f"Emergency {el} repair London",
        f"Same day {el} repairs London",
        f"24/7 {el} repair London",
        f"Cheap {el} repair London",
        f"Affordable {el} repair London",
        f"{e} repair near me",
        f"Annual {el} maintenance and servicing London",
        f"Low-cost {el} diagnostics London",
    ]


def expand_money_offers() -> None:
    """Append Top-3 offer strings into money_data.MONEY[*]['offers'] (in-memory + aspx)."""
    for slug, equip in EQUIP.items():
        d = md.MONEY[slug]
        have = {o.lower() for o in d["offers"]}
        for o in offer_names(equip):
            if o.lower() not in have:
                d["offers"].append(o)
                have.add(o.lower())


CSS = (
    "<style>.cd-top3-v5{max-width:1140px;margin:28px auto;padding:22px 18px;background:linear-gradient(180deg,#f8fafc 0%,#fff 100%);"
    "border:1px solid #e2e8f0;border-radius:12px}.cd-top3-v5 h2{margin:0 0 10px;color:#0a2540;font-size:22px}"
    ".cd-top3-v5 h3{margin:16px 0 6px;color:#0a2540;font-size:17px}.cd-top3-v5 p,.cd-top3-v5 li{color:#334155;line-height:1.55}"
    ".cd-top3-v5 ul{margin:6px 0 10px 18px}.cd-top3-v5 table{width:100%;border-collapse:collapse;margin:10px 0;font-size:14px}"
    ".cd-top3-v5 th,.cd-top3-v5 td{border:1px solid #cbd5e1;padding:8px 10px;text-align:left}.cd-top3-v5 th{background:#0a2540;color:#fff}"
    ".cd-top3-v5 .cd-top3-cta{font-weight:800;margin-top:12px}</style>"
)


def body_block(equip: str, slug: str | None) -> str:
    e = equip
    el = e[0].lower() + e[1:]
    href = f"/{slug}/" if slug else "/"
    phone = f'<a href="{md.PHONE_TEL}">{md.PHONE_DISPLAY}</a>'
    rows = [
        ("Repair / Repairs", f"{e} repair London &amp; {el} repairs London for trade sites"),
        ("Service / Services", f"{e} service London, {el} services &amp; annual maintenance"),
        ("Emergency / Same day", f"Emergency {el} repair &amp; same day {el} repairs London"),
        ("24/7 / Near me", f"24/7 rapid response and {el} repair near me across London"),
        ("Cheap / Affordable", f"Cheap {el} repair London with fixed diagnostic call-out"),
    ]
    tr = "".join(f"<tr><th>{a}</th><td>{b}</td></tr>" for a, b in rows)
    return "\n".join(
        [
            START,
            f'<section class="cd-top3-v5" aria-label="{md.esc(e)} repair, service and emergency keyword coverage">',
            CSS,
            f"<h2>{md.esc(e)} Repair, Repairs, Service &amp; Emergency Call-Out in London</h2>",
            (
                f"<p>Cold Direct covers commercial <strong>{md.esc(el)} repair London</strong> and "
                f"<strong>{md.esc(el)} repairs London</strong>, plus ongoing "
                f"<strong>{md.esc(el)} service</strong> and <strong>{md.esc(el)} services</strong> for restaurants, "
                "pubs, shops, hotels and catering kitchens. Trade equipment only — never domestic appliances.</p>"
            ),
            f"<h3>Emergency, same day &amp; 24/7 {md.esc(el)} response</h3>",
            "<ul>",
            f"<li><strong>Emergency {md.esc(el)} repair London</strong> — night and weekend dispatch</li>",
            f"<li><strong>Same day {md.esc(el)} repairs London</strong> when booked before midday where parts allow</li>",
            f"<li><strong>24/7 rapid response call-out</strong> across Greater London</li>",
            f"<li><strong>{md.esc(e)} repair near me</strong> from our Enfield N9 0DX base</li>",
            "</ul>",
            f"<h3>Cheap &amp; affordable {md.esc(el)} repair with transparent cost</h3>",
            (
                f"<p>Looking for <strong>cheap {md.esc(el)} repair London</strong> without surprise bills? "
                "We use a fixed diagnostic call-out, then quote parts and labour before work starts — "
                f"affordable, competitive fixed-rate repairs with a full guarantee. Call {phone}.</p>"
            ),
            f"<h3>{md.esc(e)} service matrix (how London buyers search)</h3>",
            f"<table><thead><tr><th>Intent</th><th>What we deliver</th></tr></thead><tbody>{tr}</tbody></table>",
            (
                f'<p class="cd-top3-cta">Book {md.esc(el)} repair or service in London — '
                f'<a href="{href}">open this hub</a> or call {phone} now.</p>'
            ),
            "</section>",
            END,
        ]
    ) + "\n"


def schema_block(equip: str, slug: str | None) -> str:
    """Extra Service JSON-LD (does not redefine #business). Survives nightly V4 schema rewrite."""
    url = md.SITE + (f"/{slug}/" if slug else "/")
    names = offer_names(equip)
    offers = [
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n}} for n in names
    ]
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Service",
                "@id": url + "#top3-service",
                "name": f"{equip} repair London",
                "alternateName": names,
                "serviceType": [
                    f"{equip} repair",
                    f"{equip} repairs",
                    f"{equip} service",
                    f"{equip} services",
                    f"Emergency {equip.lower()} repair",
                    f"Same day {equip.lower()} service",
                    f"Cheap affordable commercial {equip.lower()} repair in London",
                ],
                "url": url,
                "provider": {"@id": md.SITE + "/#business"},
                "areaServed": ["London", "Greater London"],
                "hoursAvailable": "Mo-Su 00:00-23:59",
                "hasOfferCatalog": {
                    "@type": "OfferCatalog",
                    "name": f"{equip} repair London - Top-3 keyword variations",
                    "itemListElement": offers,
                },
            },
            {
                "@type": "FAQPage",
                "@id": url + "#top3-faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f"Do you offer same day {equip.lower()} repairs London?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": (
                                f"Yes. Cold Direct provides same day {equip.lower()} repairs London and "
                                f"24/7 emergency {equip.lower()} repair for commercial sites, with a fixed diagnostic call-out."
                            ),
                        },
                    },
                    {
                        "@type": "Question",
                        "name": f"Is cheap {equip.lower()} repair London available with a guarantee?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": (
                                f"We keep {equip.lower()} repair affordable with a fixed diagnostic call-out, "
                                "transparent quotes and a full guarantee on repair work. Commercial equipment only."
                            ),
                        },
                    },
                    {
                        "@type": "Question",
                        "name": f"Do you provide {equip.lower()} service and annual servicing in London?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": (
                                f"Yes. Alongside emergency repair we offer {equip.lower()} service, services and "
                                "annual maintenance & servicing for trade refrigeration and AC across London."
                            ),
                        },
                    },
                ],
            },
        ],
    }
    ld = json.dumps(graph, ensure_ascii=False, indent=2).replace("</", "<\\/")
    return f"{SCHEMA_S}\n<script type=\"application/ld+json\" data-cd-schema=\"top3-v5\">\n{ld}\n</script>\n{SCHEMA_E}\n"


INSERT_BEFORE = [
    r"<!-- CD-MONEY-V1 -->",
    r"<!-- CD-CRO-FAQ-ACCORDION -->",
    r"<!-- CD-9-MONEY-KEYWORD-SILO-V47 -->",
    r"<!-- CD-HOMEPAGE-6-BLOG-HUB -->",
    r"<footer\b",
    r"</body>",
]


def copies(slug: str) -> list[Path]:
    return [
        ROOT / f"{slug}.html",
        ROOT / slug / "index.html",
        MIRROR / f"{slug}.html",
        MIRROR / slug / "index.html",
    ]


def home_copies() -> list[Path]:
    return [ROOT / "index.html", MIRROR / "index.html"]


def inject_body(html: str, block: str) -> str:
    html = BLOCK_RX.sub("", html)
    for pat in INSERT_BEFORE:
        m = re.search(pat, html, re.I)
        if m:
            nl = "\r\n" if html.count("\r\n") * 2 > html.count("\n") else "\n"
            return html[: m.start()] + block.replace("\n", nl) + html[m.start() :]
    raise ValueError("no insertion point for TOP3 body")


def inject_schema(html: str, block: str) -> str:
    html = SCHEMA_RX.sub("", html)
    m = re.search(r"</head>", html, re.I)
    if not m:
        raise ValueError("no </head>")
    nl = "\r\n" if html.count("\r\n") * 2 > html.count("\n") else "\n"
    return html[: m.start()] + block.replace("\n", nl) + html[m.start() :]


def apply_aspx_offers(text: str) -> str:
    """Append new OfferCatalog literals into moneyMeta without changing [0]/[1] title/desc."""
    for slug in md.HUB_ORDER:
        rx = re.compile(r'(moneyMeta\["' + re.escape(slug) + r'"\] = new string\[\] \{ )(.*?)( \};)')
        m = rx.search(text)
        if not m:
            raise SystemExit(f"moneyMeta[{slug}] missing")
        lits = re.findall(LIT, m.group(2))
        if len(lits) < 4:
            raise SystemExit(f"moneyMeta[{slug}] too short")
        # keep [0] title and [1] desc exactly
        have = {x.lower() for x in lits}
        for off in md.MONEY[slug]["offers"]:
            lit = '"' + md.aspx_js_escape(off) + '"'
            if lit.lower() not in have:
                lits.append(lit)
                have.add(lit.lower())
        for off in offer_names(EQUIP[slug]):
            lit = '"' + md.aspx_js_escape(off) + '"'
            if lit.lower() not in have:
                lits.append(lit)
                have.add(lit.lower())
        text = text[: m.start()] + m.group(1) + ", ".join(lits) + m.group(3) + text[m.end() :]
    return text


def patch_build_money_schema(text: str) -> str:
    """Add alternateName into BuildMoneySchema Service node if missing."""
    needle = '"name": "' + '" + J(m[2]) + "' + '",\\r\\n      "serviceType":'
    # actual source uses string concat differently - patch C# source:
    old = (
        '\"name\": \\\"\" + J(m[2]) + \"\\\",\\r\\n'
        '      \"serviceType\": \\\"\" + J(m[3]) + \"\\\",\\r\\n'
    )
    # Read actual file snippet style from aspx BuildMoneySchema
    marker = '"name": "\" + J(m[2]) + "\",\r\n      "serviceType":'
    if "alternateName" in text.split("BuildMoneySchema")[1][:800]:
        return text
    old2 = (
        '\"name\": \\\"\" + J(m[2]) + \"\\\",\\r\\n      \"serviceType\": \\\"\" + J(m[3]) + \"\\\","'
    )
    # Simpler: in BuildMoneySchema function string
    target = (
        '"name": "\" + J(m[2]) + "\",\r\n'
        '      "serviceType": "\" + J(m[3]) + "\",\r\n'
        '      "url": "'
    )
    repl = (
        '"name": "\" + J(m[2]) + "\",\r\n'
        '      "alternateName": [\" + string.Join(\",\", Array.ConvertAll(m.Skip(4).Take(8).ToArray(), '
        'x => \"\\\"\" + J(x) + \"\\\"\")) + \"],\r\n'
        '      "serviceType": "\" + J(m[3]) + "\",\r\n'
        '      "url": "'
    )
    # Skip C# LINQ dependency - keep schema enrichment in CD-TOP3-SCHEMA-V5 only.
    return text


def apply_page(path: Path, equip: str, slug: str | None) -> bool:
    old = path.read_bytes().decode("utf-8")
    new = inject_schema(inject_body(old, body_block(equip, slug)), schema_block(equip, slug))
    if new == old:
        return False
    path.write_bytes(new.encode("utf-8"))
    return True


def run(apply: bool) -> int:
    expand_money_offers()
    pending = 0
    aspx = ASPX.read_bytes().decode("utf-8")
    new_aspx = apply_aspx_offers(aspx)
    if new_aspx != aspx:
        pending += 1
        print("auto-seo.aspx moneyMeta offers: pending")
        if apply:
            ASPX.write_bytes(new_aspx.encode("utf-8"))
            (MIRROR / "auto-seo.aspx").write_bytes(new_aspx.encode("utf-8"))
    else:
        print("auto-seo.aspx moneyMeta offers: up to date")

    for slug, equip in EQUIP.items():
        for p in copies(slug):
            if not p.exists():
                print("MISSING", p)
                pending += 1
                continue
            old = p.read_bytes().decode("utf-8")
            new = inject_schema(inject_body(old, body_block(equip, slug)), schema_block(equip, slug))
            if new != old:
                pending += 1
                print("pending", p.relative_to(ROOT).as_posix())
                if apply:
                    p.write_bytes(new.encode("utf-8"))
    for p in home_copies():
        if not p.exists():
            continue
        old = p.read_bytes().decode("utf-8")
        new = inject_schema(inject_body(old, body_block(HOME_EQUIP, None)), schema_block(HOME_EQUIP, None))
        if new != old:
            pending += 1
            print("pending", p.relative_to(ROOT).as_posix())
            if apply:
                p.write_bytes(new.encode("utf-8"))
    print(f"top3 pending={pending} apply={apply}")
    return pending


def selftest() -> None:
    expand_money_offers()
    b = body_block("Fridge", "fridge-repair-london")
    assert START in b and "Cheap fridge repair London" in b
    s = schema_block("Fridge", "fridge-repair-london")
    data = json.loads(s.split("<script", 1)[1].split(">", 1)[1].split("</script>")[0])
    assert data["@graph"][0]["@type"] == "Service"
    assert "#business" in data["@graph"][0]["provider"]["@id"]
    assert data["@graph"][1]["@type"] == "FAQPage"
    print("top3_rank_booster_v5 selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif "--check" in sys.argv:
        sys.exit(1 if run(False) else 0)
    elif "--apply" in sys.argv:
        run(True)
        selftest()
    else:
        print("Usage: --apply | --check | --selftest")
        sys.exit(2)
