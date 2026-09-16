# ColdDirect Upgrade Plan

**Date:** 2026-09-16  
**Branch:** `ai/cold-direct-growth-upgrade`  
**Stack:** Static HTML + SSI (`header-nav.inc`, `footer-services.inc`) + PHP helpers; deploy Plesk `httpdocs` via FTP. Repo also mirrors files at root. Live site ≈ `colddirect-public-html/`.

**Business constraint:** Repair service — do **not** build product catalogue / filters / Product Offer schema with invented prices.

---

## Audit snapshot

| Metric | Value |
|--------|------:|
| HTML files | ~115 |
| Sitemap locs | 115 (includes utilities — bad) |
| noindex pages | 4 (2 utility + **2 promoted services**) |
| Missing schema | ~15 hubs/utility |
| Canonical `.html` / bare | ~19 / ~94 |
| Thin meta template | ~70 pages |

---

## P0 — Critical

### P0-1 Unblock or stop promoting AC + supermarket fridge
- **Problem:** `air-conditioning-repair-london.html` and `supermarket-fridge-repair-london.html` have `noindex,nofollow` but appear in nav + homepage.
- **Evidence:** Grep robots meta; `includes/header-nav.inc`; homepage cards.
- **Solution:** Remove noindex → `index,follow` (preferred if pages are quality). Keep in sitemap.
- **Impact:** High — restores indexability for money keywords.
- **Risk:** Low if content is commercial-only and unique.
- **Files:** those two HTML files.
- **Status:** **DONE** (this branch batch).
- **Verify:** Live meta robots; GSC URL inspection later.

### P0-2 Sitemap hygiene
- **Problem:** Sitemap lists `agent-status.html`, `image-preview.html`, `about.html`, `news.html`, `/index.html`.
- **Solution:** Remove utilities/stubs; keep `/` not `/index.html`.
- **Impact:** Cleaner crawl budget / fewer soft-404 signals.
- **Risk:** Low.
- **Files:** `colddirect-public-html/sitemap.xml` (+ root mirror if used).
- **Status:** **DONE** (this branch batch).
- **Verify:** sitemap parse; locs absent.

### P0-3 Robots disallow utilities
- **Problem:** Utility pages crawlable despite noindex.
- **Solution:** `Disallow: /agent-status.html` and `/image-preview.html`.
- **Impact:** Low–medium hygiene.
- **Risk:** Low.
- **Files:** `robots.txt`.
- **Status:** **DONE** (this branch batch).

### P0-4 Booking endpoint
- **Problem:** JS posts to `/booking.asp`; `/booking.php` 404 on live.
- **Evidence:** Live HEAD: booking.asp → 400 (endpoint present), booking.php → 404.
- **Solution:** Keep `.asp` unless migrating deliberately; document.
- **Status:** **Verified OK** — no code change this batch.
- **Verify:** Submit test form in staging when human available.

---

## P1 — High impact

| ID | Task | Status |
|----|------|--------|
| P1-1 | Canonical policy sitewide (prefer one format) | Planned |
| P1-2 | Thicken `services.html`, `brands.html`, `coverage.html`, `faqs.html` | Planned (brands WIP uncommitted — coordinate) |
| P1-3 | Collapse near-dup slugs (empire/bottle/display non-london) | Planned |
| P1-4 | Unique titles/metas — kill “{X} in London from Cold Direct…” template | Planned (scripted batch) |
| P1-5 | Schema on hubs; unify LocalBusiness vs HVACBusiness | Planned |
| P1-6 | Fix Liebherr nav (page or honest link) | Planned |
| P1-7 | Homepage above-fold primary tel CTA beside H1 | Planned |
| P1-8 | Publish F-Gas/Refcom **only with human numbers** | Blocked — needs data |
| P1-9 | Repair guarantee policy copy | Blocked — needs policy |
| P1-10 | Finish brand pro-image WIP (already in working tree) | In progress (human/agent WIP — do not clobber) |

---

## P2 — Growth

| ID | Task | Status |
|----|------|--------|
| P2-1 | Business-type landing sections (restaurant / pub / shop) | Roadmap |
| P2-2 | PPM / servicing page if offered | Blocked |
| P2-3 | Buying guides / troubleshooting content engine | See content-roadmap.md |
| P2-4 | Selective area pages only with unique proof | Careful |
| P2-5 | Lighthouse pass on top 10 URLs | Planned |

---

## Implementation order (this sprint)

1. Docs (research, keyword map, plan, roadmap, changelog)  
2. P0-1 noindex remove  
3. P0-2 + P0-3 sitemap + robots  
4. Stop — human review before main merge / Plesk deploy  

**Do not push this branch to `main` until human approval.**
