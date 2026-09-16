# ColdDirect Change Log

Branch: `ai/cold-direct-growth-continue` (continues work from `ai/cold-direct-growth-upgrade`)  
Started: 2026-09-16

---

## 2026-09-16 — Research & audit docs

- **Change:** Added competitive research, keyword map, upgrade plan, content roadmap.
- **Why:** Human asked for research-first growth programme with reversible Git work on a dedicated branch.
- **Evidence:** Live competitor SERPs (Kept Cold, Be Cool, Xpress, Bear, CKKE, Fridge UK) + local repo audit (noindex money pages, sitemap utilities).
- **Files:** `docs/competitive-research.md`, `docs/seo-keyword-map.md`, `docs/upgrade-plan.md`, `docs/content-roadmap.md`, `docs/change-log.md`
- **Testing:** File presence; stack confirmed static HTML + SSI.
- **Git:** commit `docs: add competitive research, SEO map and upgrade plan`

---

## 2026-09-16 — P0 indexability

- **Change:** Removed `noindex` from `air-conditioning-repair-london.html` and `supermarket-fridge-repair-london.html`.
- **Why:** Pages linked from nav/homepage but blocked from Google.
- **Evidence:** Audit grep; upgrade-plan P0-1.
- **Files:** those two HTML files under `colddirect-public-html/`.
- **Testing:** Confirm meta robots = `index, follow`.
- **Git:** commit `seo: unblock AC and supermarket fridge pages from noindex`

---

## 2026-09-16 — P0 sitemap + robots hygiene

- **Change:** Removed utility/stub URLs from sitemap; disallow agent-status and image-preview in robots.txt.
- **Why:** Crawl hygiene; stubs and internal tools should not be discovery targets.
- **Files:** `colddirect-public-html/sitemap.xml`, `colddirect-public-html/robots.txt` (+ root mirrors if committed).
- **Testing:** Grep sitemap for removed locs; robots Disallow lines present.
- **Git:** commit `seo: clean sitemap utilities and disallow internal tools`

---

## 2026-09-16 — Research deepen + P1 growth batch

- **Change:** Expanded competitor set (15+ repair/supply sites); thickened hubs; Liebherr page; near-dup 301s; homepage CTA; fixed dangerous Apache brand redirects in repo `.htaccess`.
- **Why:** Competitors win on trust clarity + hub depth + brand IA; ColdDirect had thin hubs and a Liebherr nav dead-end.
- **Evidence:** Kept Cold / Be Cool / Xpress / Bear / CRL / Fast Fix / Thermachill / FixMyFridge / London Refrigeration / A&E CoolTech + supplier IA patterns; live HEAD shows IIS (Apache htaccess inactive).
- **Files:** docs/*; hubs; `liebherr-fridge-repair-london.html`; `web.config` rewrite map; sitemap; header-nav; index; near-dup HTML canonicals; `.htaccess`.
- **Testing:** Word counts hubs ≥239; sitemap lacks near-dups; nav links Liebherr page; homepage CTA present; root `web.config` restored after accidental overwrite (not committed).
- **Git:** `426b4c5` docs · `17082b2` near-dups · `1888994` Liebherr · `85ee957` hubs/homepage CTA

---

## 2026-09-16 — P1 meta templates + ApplianceRepair schema

- **Change:** Rewrote 61 `"in London from Cold Direct"` title/description templates to repair-intent metas; unified org schema to `ApplianceRepair` (212 nodes); enriched thin stubs with NAP, priceRange, North London + 25 mile `GeoCircle`, 24/7 openingHours; cleared template phrase on utility pages.
- **Why:** Template metas dilute SERP CTR; mixed LocalBusiness/HVACBusiness confuses entity signals vs repair competitors.
- **Evidence:** Pre-batch audit found 63 template hits and LocalBusiness 210 + HVACBusiness 2; post-batch 0 templates and ApplianceRepair-only org types. JSON-LD parse check: 0 invalid scripts.
- **Files:** `colddirect-public-html/*.html` (61+ meta, ~101 schema touches); `tools/fix_meta_schema_p1.py`; `docs/_meta-schema-batch.json`; `docs/seo-keyword-map.md`; `docs/upgrade-plan.md`; `docs/change-log.md`
- **Testing:** Python audit/verify — 0 leftover template; 0 LocalBusiness/HVACBusiness/Store; all LD+JSON parse; spot-checked Foster/Gram/Williams/Hoshizaki/index/commercial-fridge.
- **Git:** `P1: repair-intent meta templates + unified LocalBusiness schema`

---

## 2026-09-16 — Verification: zero templates + LD+JSON build

- **Change:** Cleared 7 remaining `"in London from Cold Direct"` hits (3 blog metas + 4 root body mirrors); fixed scaffold `templates/page-template.asp` JSON; added `npm run build` → `tools/validate-ldjson.js`.
- **Why:** Verification grep was not yet 0; package.json had no build for LD+JSON checks.
- **Testing:** `rg` file count = 0; `npm run build` → VALIDATION OK (0 parse errors, 0 duplicate org definitions per page).
- **Git:** follow-up commit on `ai/cold-direct-growth-continue`

---

## Notes for human review

- **Not pushed to `main`.** Approve before merge/deploy to Plesk.
- Brand-image WIP stashed as `stash@{0}` on prior branch — restore when ready (`git stash pop` carefully).
- F-Gas registration / repair guarantee / “500+ businesses” claims **not** invented — awaiting your facts.
- Deploy `colddirect-public-html/web.config` carefully — rewrite map now 301s near-dup non-London URLs.
