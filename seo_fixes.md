# SEO fixes — high-click GSC queries

Period: 2026-08-23 to 2026-09-19. Property: `https://www.colddirect.co.uk/`. Source: live GSC (`gsc_report.csv`).

Goal: rank higher for queries people already click. Do not send fridge or freezer anchors to the cold-room URL.

## GSC snapshot (query totals)

| Query | Clicks | CTR | Position | Current ranking URL (most clicks) |
|---|---:|---:|---:|---|
| cold room repair london | 112 | 65% | 4.4 | `/cold-room-repairs-london` — 93 clicks, **pos 2.9**, 57% CTR |
| commercial fridge repair london | 28 | 21% | 12.5 | Homepage `/` — 25 clicks, pos 8.5 |
| fridge repair london | 24 | 12% | 20.6 | Homepage `/` — 22 clicks, pos 14.6 |
| freezer repair london | 13 | 13% | 28.1 | `/fridge-freezer-repairs-london` — 11 clicks, pos 49 |
| commercial freezer repair london | 10 | 77% | 4.8 | `/commercial-freezer-repair-north-london` — 7 clicks, pos 2.0 |

`/cold-room-repairs-london` page average (all queries) is position 36.3. That is mix noise. For the money query it is already position 2.9.

## Title tags (before → after, all under 60 characters)

| Page | Before | After | Chars |
|---|---|---|---:|
| `/cold-room-repairs-london` | Cold Room Repair London - Same Day 24/7 Emergency \| ColdDirect London | Cold Room Repair London \| Same Day 24/7 | 40 |
| `/commercial-fridge-repair-london` | Commercial Fridge Repair London \| 24/7 Emergency \| Cold Direct - Not Domestic | Commercial Fridge Repair London \| 24/7 | 38 |
| `/fridge-repair-london` | Fridge Repair London \| Same-Day Commercial, 2–4 Hour Callout | Fridge Repair London \| Same-Day 24/7 | 36 |
| `/freezer-repair-london` | Freezer Repair London \| Same-Day Commercial, 2–4 Hour Callout | Freezer Repair London \| Same-Day 24/7 | 37 |
| `/commercial-freezer-repair-london` | Commercial Freezer Repair London \| Emergency 24/7 \| Cold Direct | Commercial Freezer Repair London \| 24/7 | 40 |

Public-html copies of the commercial fridge/freezer pages had longer “Emergency Same Day …” titles. Those now match the same after titles.

## Meta descriptions (CTR)

| Query | Old CTR | New meta intent |
|---|---:|---|
| cold room repair london | 57–65% already strong | Keep same-day + 2–4 hour + phone. Do not clickbait. |
| commercial fridge repair london | 21% at pos 12 | “today / same-day 24/7 / quote first / 07983 759320” |
| fridge repair london | 12% at pos 21 | “trade kitchens / 2–4 hour / not domestic / phone” |
| freezer repair london | 13% at pos 28 | “before stock thaws / same-day 24/7 / phone” |
| commercial freezer repair london | 77% already strong | Keep short emergency + trade + phone. |

## Page audit — `/cold-room-repairs-london` (priority #1)

- H1 already exact: `Cold Room Repair London`. Left unchanged.
- Title shortened so the full query shows in SERP (old title truncated after “Emergency”).
- Added intent H2s: what it covers, same-day, who needs it, FAQs.
- Added visible FAQ plus `FAQPage` JSON-LD (5 questions). Schema IDs now use this URL, not the old `.asp` IDs.
- Internal links out to the four cabinet/freezer URLs so fridge/freezer queries stop leaking here (GSC: 0 clicks, pos 95 for commercial fridge on this URL).
- Service-tag `.asp` links replaced with live pretty URLs. Design (black hero, tag bar, CTA) unchanged.

## Homepage internal links

Three exact-match links from `/` to `/cold-room-repairs-london` with anchor `cold room repair london`:

1. Commercial services card
2. FAQ “Who does cold room repair in London?” (root homepage)
3. SEO services list (`seo-home-links`)

Public-html homepage has no FAQ block, so the third link is the footer Services line.

Fridge and freezer query anchors stay on their dedicated pages. Pointing those anchors at the cold-room URL would worsen cannibalisation.

Apply or re-check with:

```bash
node scripts/internal_linking.js
```

## Files touched

- `cold-room-repairs-london/index.html` and `colddirect-public-html/cold-room-repairs-london/index.html`
- `commercial-fridge-repair-london/index.html` + public-html `.html`
- `fridge-repair-london/index.html` + public-html `.html`
- `freezer-repair-london/index.html` + public-html `.html`
- `commercial-freezer-repair-london/index.html` + public-html `.html`
- `index.html` and `colddirect-public-html/index.html`
- `gsc_report.csv`, `seo_fixes.md`, `scripts/internal_linking.js`

## 7-day GSC follow-up (due 2026-09-26)

```bash
python gsc_report.py
```

Checks written to `gsc_followup.md` and `gsc_report.csv`:
1. `/cold-room-repairs-london` still pos 2–3 for `cold room repair london`
2. Fridge/freezer impressions moving off `/` toward `/fridge-freezer-repairs-london` and `/walk-in-fridge-repairs-london`
3. CTR change for `commercial fridge repair london` vs 21.4% at pos 12.5

## What not to do next

- Do not 301 `/cold-room-repairs-london` away. It is the winning URL for 93 of 112 cold-room clicks.
- Do not retarget that URL at fridge or freezer queries.
- Fridge/freezer H1s stay locked until 2026-09-28 (`scripts/daily-seo-update.js`).

## Low CTR / high impression pages (2026-09-19)

Filter: >3000 impressions, <1% CTR, and ~<10 clicks. `logs/gsc_report_*.csv` was not in the repo; used `gsc-analysis-2026-09-19.html` (28-day), live GSC Search Analytics (90-day from 2026-06-22), URL Inspection, and wrote `logs/gsc_report_low_ctr_2026-09-19.csv`.

| Page | 28-day impr / clicks / CTR | 90-day impr / clicks / CTR | Last crawl (inspect) | Action |
|---|---|---|---|---|
| `/blog/different-types-of-ice` | 6,472 / 10 / 0.15% | 21,468 / 33 / 0.15% | 31 Aug 2026 | **noindex, follow**. Rewrote to commercial ice-machine types. Kept live. Not in sitemap. |
| `/air-conditioning-repairs-london` | 4,469 / 1 / 0.02% | 28,583 / 3 / 0.01% | 29 Aug 2026 | **canonical** → `/air-conditioning-repair-london/`. Commercial AC intent. Stopped 301 to homepage. |
| `/chiller-repairs-london` | 3,844 / 6 / 0.16% | 11,693 / 10 / 0.09% | **5 Aug 2026** | **canonical** → `/chiller-repair-london/`. Commercial chiller intent. Stopped 301 to fridge North London. |

Also matching the 28-day filter (not in the named set): `/refrigeration-brands-repairs-london` already 301s to the singular brands page; `/blog/types-of-cold-storage` left for a later pass.

Nothing deleted. Live IIS was 404ing `/blog/different-types-of-ice` and `/air-conditioning-repairs-london` (rewrite fell through to missing `.asp`). `/chiller-repairs-london` was still the old ASP page. Retry 2026-09-19 19:24: IIS rewrite rules in `web.config`, FTP upload, plural URL removed from sitemap.

Request indexing on `/chiller-repair-london/` after Google recrawls the 5 Aug snapshot.

Files: `blog/different-types-of-ice.html`, `air-conditioning-repairs-london.html`, `chiller-repairs-london.html` (+ public-html copies), `.htaccess` / `colddirect-public-html/.htaccess`, `seo_fixes.md`, `logs/gsc_report_low_ctr_2026-09-19.csv`.

## 2026-09-19 - Removed accidental noindex from singular service pages per GSC Live Test

GSC reason: noindex-trap

GSC Live Test 19 Sep 21:43 showed `/air-conditioning-repair-london/` blocked by noindex. Live IIS files (not repo copies) had `<meta name="robots" content="noindex, nofollow">` on both `air-conditioning-repair-london.html` and `air-conditioning-repair-london/index.html`. `web.config` had no `X-Robots-Tag`. Set those to `index, follow`. Confirmed `/chiller-repair-london/` already `index, follow`. Added explicit `index, follow` on `/ice-machine-repair-london/` HTML. Left `noindex, follow` only on `/blog/different-types-of-ice` and plural canonicals (`air-conditioning-repairs-london`, `chiller-repairs-london`). IIS only. Did not touch Vercel.

Guards re-run 19 Sep 22:06 (IIS, not Vercel): live `curl -I` on the three singular money URLs is `200` Microsoft-IIS/10.0 with **no** `X-Robots-Tag` / header `noindex`. HTML is `index, follow`. Ice blog and both plural canonicals stay `noindex, follow`. GSC inspect: AC `/` is **Submitted and indexed** / `INDEXING_ALLOWED` (last crawl 19 Sep 20:57 UTC). Ice `/` is `INDEXING_ALLOWED` (canonical without slash).
