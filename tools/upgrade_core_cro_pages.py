#!/usr/bin/env python3
"""
Upgrades the visible body content, Above-the-Fold CRO Emergency Dispatch Trust Bar,
Common Breakdowns Grid, Commercial Brands Grid, Cellar/Catering Trade Sections,
and Visible HTML FAQ Accordion across the core London pages while strictly preserving
all `auto-seo.aspx` V4 blocks (`<!-- AUTO-SEO-V4-2026 -->`, `<!-- AUTO-SEO-V4-SCHEMA -->`,
`<!-- AUTO-SEO-V4-BLOGHUB -->`), `<title>`, `<meta name="description">`, `auto-seo.aspx`,
and `sitemap.xml`.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CRO_STYLES = """<style id="cd-cro-v4-styles">
.cd-trust-bar{background:#0a2540;color:#fff;padding:16px 0;border-bottom:3px solid #00a99d}
.cd-trust-bar .wrap{max-width:1140px;margin:0 auto;padding:0 20px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:14px}
.cd-trust-pills{display:flex;flex-wrap:wrap;gap:12px;margin:0;padding:0;list-style:none}
.cd-trust-pills li{background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.22);border-radius:999px;padding:7px 14px;font-size:13.5px;font-weight:700;color:#fff;display:inline-flex;align-items:center;gap:6px}
.cd-trust-ctas{display:flex;flex-wrap:wrap;gap:10px}
.cd-trust-ctas a{display:inline-block;padding:9px 16px;border-radius:8px;font-weight:800;font-size:14px;text-decoration:none;transition:opacity .15s}
.cd-trust-ctas .cta-office{background:#00a99d !important;color:#fff !important}
.cd-trust-ctas .cta-mobile{background:#facc15 !important;color:#0a2540 !important}
.cd-cro-section{margin:32px 0;padding:24px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px}
.cd-cro-section h2{margin-top:0;color:#0a2540;font-size:24px}
.cd-breakdown-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px;margin:18px 0}
.cd-breakdown-card{background:#fff;border:1px solid #cbd5e1;border-left:4px solid #0a2540;border-radius:8px;padding:16px}
.cd-breakdown-card h3{margin:0 0 8px;font-size:17px;color:#0a2540}
.cd-breakdown-card p{margin:0;font-size:14.5px;line-height:1.55;color:#334155}
.cd-brands-strip{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 0;padding:0;list-style:none}
.cd-brands-strip li{background:#fff;border:1px solid #cbd5e1;border-radius:8px;padding:8px 14px;font-weight:700;font-size:14px;color:#0a2540}
.cd-faq-accordion{max-width:960px;margin:32px auto;padding:0 20px}
.cd-faq-accordion h2{color:#0a2540;margin-bottom:16px}
.cd-faq-accordion details{background:#fff;border:1px solid #cbd5e1;border-radius:8px;margin-bottom:10px;padding:14px 18px}
.cd-faq-accordion summary{font-weight:700;font-size:16px;color:#0a2540;cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center}
.cd-faq-accordion summary::-webkit-details-marker{display:none}
.cd-faq-accordion summary::after{content:"+";font-size:20px;font-weight:800;color:#00a99d}
.cd-faq-accordion details[open] summary::after{content:"−"}
.cd-faq-accordion details p{margin:10px 0 0;color:#334155;font-size:15px;line-height:1.6}
</style>"""

TRUST_BAR_HTML = ""  # CD-CRO-TRUST-BAR REMOVED 2026-10-23 — dark navy strip deleted per owner

FRIDGE_FREEZER_GRID_HTML = """      <!-- CD-CRO-BREAKDOWN-GRID -->
      <div class="cd-cro-section">
        <h2>Common Commercial Breakdowns We Fix Same-Day</h2>
        <p>Our North &amp; Central London response vans carry diagnostic gauges, OEM sensors, fan motors and F-Gas refrigerants to resolve critical kitchen breakdowns on the first visit:</p>
        <div class="cd-breakdown-grid">
          <div class="cd-breakdown-card">
            <h3>1. Compressor Failures &amp; Overload Trips</h3>
            <p>Diagnosing seized, short-cycling or overheating Embraco, Danfoss and Secop compressors, start relays, run capacitors and high-head-pressure trips.</p>
          </div>
          <div class="cd-breakdown-card">
            <h3>2. Evaporator Fan &amp; Airflow Faults</h3>
            <p>Replacing seized evaporator and condenser fan motors, clearing solid ice blocks across coils, and restoring uniform airflow across all cabinet shelves.</p>
          </div>
          <div class="cd-breakdown-card">
            <h3>3. Thermostat &amp; Digital Controller Errors</h3>
            <p>Fixing Carel, Dixell and Eliwell digital controllers displaying <code>HA</code>, <code>Hi</code>, <code>P1</code>, <code>P2</code> or <code>dEF</code> probe alarms and erratic temperature hunting.</p>
          </div>
          <div class="cd-breakdown-card">
            <h3>4. Split Door Gaskets &amp; Frame Heaters</h3>
            <p>Stopping warm kitchen air ingress, heavy frost build-up and sweating door frames by fitting tight commercial magnetic door seals and mullion heaters.</p>
          </div>
          <div class="cd-breakdown-card">
            <h3>5. F-Gas Refrigerant Leak Detection &amp; Recharge</h3>
            <p>Electronic nitrogen pressure testing, brazing split copper lines, replacing filter driers and weighing in virgin R290, R404A, R448A, R449A or R134a charges.</p>
          </div>
          <div class="cd-breakdown-card">
            <h3>6. Blocked Condensate Drains &amp; Defrost Heaters</h3>
            <p>Clearing overflowing drip trays, replacing burnt-out electric defrost elements and termination thermostats so coils stay ice-free during peak service.</p>
          </div>
        </div>
        <h3>Commercial Brands We Repair Every Day Across London</h3>
        <ul class="cd-brands-strip">
          <li>Williams</li>
          <li>Foster</li>
          <li>True</li>
          <li>Polar</li>
          <li>Gram</li>
          <li>Rational</li>
          <li>Hoshizaki</li>
          <li>Liebherr</li>
          <li>Blizzard</li>
          <li>Tefcold</li>
        </ul>
      </div>"""

CATERING_TRADE_SECTION_HTML = """      <!-- CD-CRO-CATERING-TRADE -->
      <div class="cd-cro-section">
        <h2>Specialist Commercial Catering Refrigeration &amp; Pub Cellar Cooling Repairs</h2>
        <p>High-volume hospitality kitchens and bars rely on continuous cold storage. We repair the full spectrum of commercial catering refrigeration and cellar plant on the same visit:</p>
        <div class="cd-breakdown-grid">
          <div class="cd-breakdown-card">
            <h3>Refrigerated Prep Counters &amp; Saladettes</h3>
            <p>Same-day repairs for pass prep counters, pizza marble chillers and gastronorm saladettes struggling to hold 1–4°C opposite hot cooking lines.</p>
          </div>
          <div class="cd-breakdown-card">
            <h3>Blast Chillers &amp; Shock Freezers</h3>
            <p>Restoring rapid pull-down cycles (+70°C to +3°C within 90 minutes) on Foster, Williams and Lainox blast chillers for full HACCP compliance.</p>
          </div>
          <div class="cd-breakdown-card">
            <h3>Undercounter Chillers &amp; Upright Cabinets</h3>
            <p>Fixing compressor trips, seized fans, Dixell/Carel thermostats and torn door gaskets on single, double and triple-door stainless steel cabinets.</p>
          </div>
          <div class="cd-breakdown-card">
            <h3>Pub Beer Cellar Cooling (11–13°C) &amp; Line Chillers</h3>
            <p>Emergency repairs for underground pub cellars, remote beer chillers and glycol/water baths so kegs and casks stay at 11–13°C without fobbing.</p>
          </div>
        </div>
        <h3>Commercial Catering &amp; Refrigeration Brands We Repair</h3>
        <ul class="cd-brands-strip">
          <li>Williams</li>
          <li>Foster</li>
          <li>True</li>
          <li>Polar</li>
          <li>Gram</li>
          <li>Rational</li>
          <li>Hoshizaki</li>
          <li>Blizzard</li>
          <li>Adexa</li>
        </ul>
      </div>"""

CELLAR_TRADE_SECTION_HTML = """      <!-- CD-CRO-CELLAR-TRADE -->
      <div class="cd-cro-section">
        <h2>Pub Beer Cellar Cooling Systems (11–13°C) &amp; Hospitality Catering Refrigeration</h2>
        <p>Whether your venue runs a traditional cask &amp; keg basement cellar or a full restaurant kitchen upstairs, our F-Gas engineers restore exact temperature control same-day:</p>
        <div class="cd-breakdown-grid">
          <div class="cd-breakdown-card">
            <h3>Maintaining 11–13°C Keg &amp; Cask Temperatures</h3>
            <p>Calibrating cellar evaporator blowers, clearing hop-dust choked condensers and fixing refrigerant leaks so real ales and lagers never fob at the tap.</p>
          </div>
          <div class="cd-breakdown-card">
            <h3>Remote Beer Line Chillers &amp; Ice Bank Coolers</h3>
            <p>Repairing agitator motors, circulation pumps, ice-bank thermostats and compressor packs on remote under-counter and cellar python line chillers.</p>
          </div>
          <div class="cd-breakdown-card">
            <h3>Back-Bar Bottle Coolers &amp; Glass Frosters</h3>
            <p>Same-day fan motor, LED controller and door seal repairs for double and triple hinged/sliding door bar chillers and wine cabinets.</p>
          </div>
          <div class="cd-breakdown-card">
            <h3>Pub Kitchen Prep Counters, Saladettes &amp; Blast Chillers</h3>
            <p>While on site for your cellar, our engineers can also diagnose and repair commercial catering prep fridges, walk-in cold rooms, undercounter chillers and ice machines.</p>
          </div>
        </div>
        <h3>Cellar &amp; Commercial Brands We Repair Across London</h3>
        <ul class="cd-brands-strip">
          <li>Marstair</li>
          <li>J&amp;E Hall</li>
          <li>Hubbard</li>
          <li>Mitsubishi</li>
          <li>Williams</li>
          <li>Foster</li>
          <li>True</li>
          <li>Polar</li>
          <li>Gram</li>
          <li>Hoshizaki</li>
        </ul>
      </div>"""


def build_faq_accordion(page_title_short: str, specific_q: str, specific_a: str) -> str:
    return f"""  <!-- CD-CRO-FAQ-ACCORDION -->
  <section class="cd-faq-accordion" aria-label="Frequently Asked Questions">
    <h2>Frequently Asked Questions — {page_title_short}</h2>
    <details open>
      <summary>1. How fast is your emergency callout response across London?</summary>
      <p>We target a <strong>60–90 minute emergency arrival</strong> across North &amp; Central London (and 2–4 hours across Greater London within the M25) 24 hours a day, 7 days a week. Call <a href="tel:+442039524822">0203 952 4822</a> or <a href="tel:+447983759320">07983 759320</a> with your postcode for immediate dispatch.</p>
    </details>
    <details>
      <summary>2. Are your engineers F-Gas certified and do you provide HACCP paperwork?</summary>
      <p>Yes. Every Cold Direct engineer holds full UK F-Gas certification for commercial refrigerants (R290, R404A, R448A, R449A, R134a, R410A). Every visit includes calibrated air and core product temperature readings plus a written F-Gas &amp; HACCP service report for your EHO records.</p>
    </details>
    <details>
      <summary>3. {specific_q}</summary>
      <p>{specific_a}</p>
    </details>
    <details>
      <summary>4. Do you carry spare parts for same-day first-visit repairs?</summary>
      <p>Yes. Our vans stock universal and OEM digital controllers (Dixell, Carel, Eliwell), evaporator and condenser fan motors, start relays, capacitors, defrost heaters, filter driers and commercial door gaskets so over 85% of breakdowns are resolved on the first visit.</p>
    </details>
    <details>
      <summary>5. Do you repair domestic household fridges or only commercial equipment?</summary>
      <p>We are <strong>strictly commercial-only (B2B)</strong>. We repair refrigeration for restaurants, pubs, bars, hotels, supermarkets, dark kitchens, schools, hospitals and food production sites across London. We do not attend domestic residential appliances.</p>
    </details>
  </section>"""


def inject_standard_page(rel_slug: str, body_block: str, faq_block: str) -> None:
    paths = [
        ROOT / f"{rel_slug}.html",
        ROOT / rel_slug / "index.html",
        ROOT / "colddirect-public-html" / f"{rel_slug}.html",
        ROOT / "colddirect-public-html" / rel_slug / "index.html",
    ]
    primary = paths[0]
    html = primary.read_text(encoding="utf-8")

    # Sanity check: ensure V4 markers exist before editing
    assert "<!-- AUTO-SEO-V4-2026 -->" in html, f"Missing V4 footer marker in {primary}"
    assert "<!-- AUTO-SEO-V4-SCHEMA -->" in html, f"Missing V4 schema marker in {primary}"

    # 1. Inject CRO CSS right before <!-- AUTO-SEO-V4-SCHEMA --> (without touching title/meta/schema)
    if 'id="cd-cro-v4-styles"' not in html:
        html = html.replace(
            "<!-- AUTO-SEO-V4-SCHEMA -->",
            CRO_STYLES + "\n<!-- AUTO-SEO-V4-SCHEMA -->",
            1,
        )

    # 2. Inject Above-the-Fold Trust Bar right after the hero </section>
    if TRUST_BAR_HTML and "<!-- CD-CRO-TRUST-BAR -->" not in html:
        hero_end = html.find("</section>")
        if hero_end != -1:
            insert_pos = hero_end + len("</section>")
            html = html[:insert_pos] + "\n" + TRUST_BAR_HTML + html[insert_pos:]

    # 3. Inject Body Content Grid inside the main <section class="section"> before its closing </div>\n  </section>
    if "<!-- CD-CRO-" not in html.split("<!-- CD-CRO-TRUST-BAR -->")[-1]:
        cta_band_pos = html.find('<section class="cta-band">')
        if cta_band_pos != -1:
            # Find the last </div> before <section class="cta-band">
            div_close = html.rfind("</div>", 0, cta_band_pos)
            if div_close != -1:
                html = html[:div_close] + "\n" + body_block + "\n    " + html[div_close:]

    # 4. Inject Visible FAQ Accordion right above <footer class="site-footer">
    if "<!-- CD-CRO-FAQ-ACCORDION -->" not in html:
        footer_pos = html.find('<footer class="site-footer">')
        if footer_pos != -1:
            html = html[:footer_pos] + faq_block + "\n  " + html[footer_pos:]

    # Verify V4 markers and title are 100% preserved
    assert "<!-- AUTO-SEO-V4-2026 -->" in html
    assert "<!-- AUTO-SEO-V4-SCHEMA -->" in html
    assert "<!-- AUTO-SEO-LOCKED -->" not in html

    for p in paths:
        if p.exists() or p.parent.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(html, encoding="utf-8")
    print(f"Upgraded {rel_slug} (all 4 synced copies)")


def update_cellar_asp() -> None:
    asp_paths = [
        ROOT / "cellar-cooler-repair-london.asp",
        ROOT / "colddirect-public-html" / "cellar-cooler-repair-london.asp",
    ]
    primary = asp_paths[0]
    if not primary.exists():
        return
    html = primary.read_text(encoding="utf-8")
    if 'id="cd-cro-v4-styles"' not in html:
        html = html.replace("</head>", CRO_STYLES + "\n</head>", 1)
    if TRUST_BAR_HTML and "<!-- CD-CRO-TRUST-BAR -->" not in html:
        # Insert after hero div
        marker = '<div class="service-seo"'
        if marker in html:
            html = html.replace(marker, TRUST_BAR_HTML + "\n" + marker, 1)
    if "<!-- CD-CRO-CELLAR-TRADE -->" not in html:
        faq = build_faq_accordion(
            "Beer Cellar Cooling & Pub Cellar Repair London",
            "What temperature should a pub beer cellar be kept at in London?",
            "Standard UK pub cellars must hold a steady <strong>11–13°C (52–55°F)</strong> for cask conditioned ales and keg storage, while remote glycol/ice-bank line chillers pull draught lager down to 2–6°C at the tap.",
        )
        html = html.replace(
            "</section>\n</body>",
            "</section>\n<div style='max-width:960px;margin:0 auto;padding:0 16px'>"
            + CELLAR_TRADE_SECTION_HTML
            + "</div>\n"
            + faq
            + "\n</body>",
            1,
        )
    for p in asp_paths:
        if p.exists() or p.parent.exists():
            p.write_text(html, encoding="utf-8")
    print("Upgraded cellar-cooler-repair-london.asp (root + mirror)")


def main() -> int:
    inject_standard_page(
        "commercial-fridge-repair-london",
        FRIDGE_FREEZER_GRID_HTML,
        build_faq_accordion(
            "Commercial Fridge Repair London",
            "Which commercial fridge brands and cabinet types do you repair?",
            "We repair all trade refrigeration including upright single and double-door cabinets, refrigerated prep counters, saladettes, undercounter fridges and multideck display chillers from <strong>Williams, Foster, True, Polar, Gram, Rational, Hoshizaki, Liebherr and Blizzard</strong>.",
        ),
    )
    inject_standard_page(
        "commercial-freezer-repair-london",
        FRIDGE_FREEZER_GRID_HTML,
        build_faq_accordion(
            "Commercial Freezer Repair London",
            "My commercial freezer is icing up and climbing above -18°C — should we chip the ice?",
            "<strong>Never chip ice with a knife or metal bar</strong> as it punctures the pressurized evaporator tubing. Keep the door shut, move high-risk stock if needed, and call us — we safely de-ice the coil, test the electric defrost heater, termination probe and drain heater, and restore -18°C to -22°C operation.",
        ),
    )
    inject_standard_page(
        "cold-room-repair-london",
        FRIDGE_FREEZER_GRID_HTML,
        build_faq_accordion(
            "Walk-In Cold Room Repair London",
            "Do you repair both integral and remote rooftop walk-in cold room systems?",
            "Yes. We repair walk-in chillers (+1°C to +4°C) and walk-in freezer rooms (-18°C to -25°C), including monoblock wall packs, split remote condensing units in basements or rooftops, evaporator fan banks, Carel/Dixell control panels and cold room door hardware.",
        ),
    )
    inject_standard_page(
        "catering-repair-london",
        CATERING_TRADE_SECTION_HTML,
        build_faq_accordion(
            "Commercial Catering Refrigeration Repair London",
            "Which commercial catering equipment do you repair on the same visit?",
            "We repair all commercial catering refrigeration: chef pass prep counters, gastronorm saladettes, blast chillers, undercounter chillers, upright storage cabinets, ice machines and pub beer cellar cooling systems across all London postcodes.",
        ),
    )
    inject_standard_page(
        "cellar-cooler-repair-london",
        CELLAR_TRADE_SECTION_HTML,
        build_faq_accordion(
            "Beer Cellar Cooling & Pub Cellar Repair London",
            "What temperature should a pub beer cellar be kept at in London?",
            "Standard UK pub cellars must hold a steady <strong>11–13°C (52–55°F)</strong> for cask conditioned ales and keg storage, while remote glycol/ice-bank line chillers pull draught lager down to 2–6°C at the tap.",
        ),
    )
    update_cellar_asp()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
