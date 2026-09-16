# ColdDirect Change Log

Branch: `ai/cold-direct-growth-upgrade`  
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

## Notes for human review

- **Not pushed to `main`.** Approve before merge/deploy to Plesk.
- Uncommitted brand-image WIP on this branch was **left untouched** to avoid clobbering in-progress work.
- F-Gas registration / repair guarantee copy **not** invented — awaiting your facts.
