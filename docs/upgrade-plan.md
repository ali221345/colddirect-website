# ColdDirect Upgrade Plan

**Date:** 2026-09-16  
**Branch:** `ai/cold-direct-growth-continue` (worktree; `ai/cold-direct-growth-upgrade` locked in another worktree)  
**Stack:** Static HTML + SSI (`header-nav.inc`, `footer-services.inc`) + PHP helpers; deploy Plesk `httpdocs` via FTP. Live ≈ IIS + `colddirect-public-html/`.

**Business constraint:** Repair service — do **not** build product catalogue / filters / Product Offer schema with invented prices.

---

## Audit snapshot (updated)

| Metric | Value |
|--------|------:|
| HTML files | ~116 (+ Liebherr) |
| Sitemap | Near-dup non-London URLs removed; Liebherr added |
| noindex money pages | Fixed earlier (AC + supermarket) |
| Thin hubs | Thickened (services/brands/coverage/faqs) |
| Liebherr nav | Fixed → dedicated page |
| Apache `.htaccess` | Contained dangerous brand 301s — **not active on IIS live**; corrected in repo |

---

## P0 — Critical

| ID | Task | Status |
|----|------|--------|
| P0-1 | Unblock AC + supermarket fridge noindex | **DONE** |
| P0-2 | Sitemap hygiene (utilities) | **DONE** |
| P0-3 | Robots disallow utilities | **DONE** |
| P0-4 | Booking endpoint | Verified OK (booking.asp) |
| P0-5 | Stop Apache `.htaccess` from 301ing Foster / commercial-fridge-london money pages | **DONE** (repo; live is IIS) |

---

## P1 — High impact

| ID | Task | Status |
|----|------|--------|
| P1-1 | Canonical policy sitewide | Partial — near-dups done; full site still mixed `.html` / bare |
| P1-2 | Thicken hubs | **DONE** this batch |
| P1-3 | Collapse near-dup slugs | **DONE** — IIS rewrite map + canonical/noindex + sitemap |
| P1-4 | Unique titles/metas (kill template) | **DONE** — 61 pages + 0 template leftovers |
| P1-5 | Schema on hubs + unify org type | **DONE** — ApplianceRepair sitewide (212); hubs already had Collection/FAQ |
| P1-6 | Liebherr nav + page | **DONE** |
| P1-7 | Homepage above-fold tel CTA | **DONE** |
| P1-8 | F-Gas/Refcom numbers | Blocked — needs human data |
| P1-9 | Repair guarantee policy | Blocked — needs policy |
| P1-10 | Brand pro-image WIP | Stashed on `cursor/ded04436` — do not clobber |

---

## P2 — Growth

| ID | Task | Status |
|----|------|--------|
| P2-1 | Business-type landing sections | Roadmap |
| P2-2 | PPM page if offered | Blocked |
| P2-3 | Content engine | See content-roadmap.md |
| P2-4 | Selective area pages | Careful — coverage page now honest |
| P2-5 | Lighthouse top 10 | **DONE** money URLs (home + commercial fridge + Foster/True/Liebherr) |
| P2-6 | Soften unverified “500+ businesses” badges sitewide | Planned (human confirm stats first) |

---

## Implementation order

1. Docs research depth  
2. P0 htaccess safety + P1 near-dups + Liebherr + hubs + homepage CTA  
3. Next: Lighthouse top money URLs; soften 500+ badge after human confirm; F-Gas/guarantee when data arrives  

**Do not push to `main` / Plesk until human approval.**
