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

## Archived PUBLISHED entries (full detail in seo_fixes_archive.md)

- PUBLISHED — walk-in-freezer-room-repair-london — 2026-09-23 22:41 — query=freezer room repair london clicks=5 impressions=25 pos=31.6 CTR=20% date=2026-09-23
- PUBLISHED — freezer-room-repair-london — 2026-09-25 22:15 — query=freezer room repair london clicks=5 impressions=25 pos=31.6 CTR=20% date=2026-09-23 (top_queri
- PUBLISHED — freezer-repair-london — 2026-09-26 21:52 — query=freezer repair london clicks=20 impressions=99 pos=23.15 CTR=20.2% date=2026-09-26 (top_querie
- PUBLISHED — commercial-fridge-repair-london — 2026-09-27 22:05 — query=commercial fridge repair london clicks=43 impressions=175 pos=11.8 CTR=24.6% date=2026-09-27 (

## PUBLISHED — fridge-repair-london — 2026-09-28 22:05
Keyword Tags: fridge repair london, commercial fridge repair london, fridge service london, Foster freezer repair, Williams freezer repair, commercial refrigeration repair London
SEO Focus: local intent, commercial, emergency, brand-specific
Target Borough: Greater London (North London base)
GSC Source: query=fridge repair london clicks=33 impressions=202 pos=17.09 CTR=16.34% date=2026-09-28 (top_queries row, gsc_report.csv), winner=https://www.colddirect.co.uk/ (per check2 breakdown: homepage takes 31/33 clicks at pos 11.78 for this query; the dedicated /fridge-repair-london/ page itself gets 0 attributed clicks — a leak/cannibalisation opportunity flagged as a candidate in the 2026-09-26 log entry, picked up tonight)
Files touched:
- fridge-repair-london.html (root)
- fridge-repair-london/index.html (folder, live IIS URL)
- colddirect-public-html/fridge-repair-london.html
- colddirect-public-html/fridge-repair-london/index.html
Before/after title: "Fridge Repair London | Same-Day Commercial, 2–4 Hour Callout" (all 4 copies, identical) -> "Emergency Same Day Fridge Repair London | ColdDirect 24/7" (57 chars) — brings the page onto the Emergency Same Day convention already used on sibling pages (commercial-fridge-repair-london, freezer-repair-london, freezer-room-repair-london); added the required `<!-- SEO: Title updated Emergency Same Day for Google SERP -->` comment directly after `<title>`.
Before/after H1: "Fridge Same-Day Repair London" -> "Fridge Repair London - Same-Day Emergency Callout" (exact-match primary keyword leads the H1, all 4 files).
Before/after meta description: "Fridge repair London for restaurants, pubs and shops. Same-day commercial engineers, 2–4 hour 24/7 emergency. Quote before we start. Call 07983 759320." (152 chars) -> "Emergency Same Day 24/7 callout. Fridge repair London across London. Trade kitchens only. Call 07983 759320." (108 chars, matches the required site pattern). Page CTR is 16.34%, below the 60% "keep untouched" exemption threshold, so rewrite applied. og:title/og:description/twitter:title/twitter:description updated to match.
Meta robots: page had no explicit `<meta name="robots">` tag on any of the 4 copies (defaulted indexable) -> added explicit `<meta name="robots" content="index, follow">` since this is a singular money-query page, not a plural/blog page.
Change summary: page was already substantial (~1290 words, LocalBusiness+Service+FAQPage JSON-LD with 3 FAQs, tel CTAs) but (1) the `Service` schema `name`/`serviceType` had been copy-pasted from `commercial-fridge-repair-london` and incorrectly read "Commercial Fridge Repair London | 24/7 Emergency | Cold Direct" instead of describing this page's own service — fixed to "Fridge Repair London | 24/7 Emergency | Cold Direct"; (2) added explicit `<meta name="robots" content="index, follow">`; (3) added a 3-item benefits bullet list under the hero lead ("2-4 hour emergency response 24/7", "F-Gas certified engineers...", "Fixed price quoted on site..."); (4) rewrote H1/title/meta description onto the site's Emergency Same Day / emergency-CTA convention; (5) added 3 more FAQ entries (schema + visible, now 6 total) — "How fast can you attend a fridge breakdown in London?", "Do you repair domestic fridges?", "What does a call-out cost?"; (6) appended the required GSC keyword HTML comment at end of file. No content deleted — only added/rewritten in place. Hero image (commercial-fridge-kitchen-london.webp) and its alt text left untouched — already leads with a relevant description and is not a DO-NOT-TOUCH image, but was already correct so no change was needed.
Internal links: page already links out to /commercial-fridge-repair-london, /commercial-fridge-repair-north-london, /polar-fridge-repair-london, /adexa-fridge-repair-london, /empire-fridge-repair-london, /subzero-fridge-repair-london, /freezer-repair-london. Homepage (index.html) and colddirect-public-html/index.html already have exact-match anchor "fridge repair london" -> `/fridge-repair-london/` in the body content section, the commercial-fridge blurb, and the services list footer (3 existing exact-match links found, confirmed present, not modified). `scripts/internal_linking.js` already has a LINKS entry for `/fridge-repair-london` (anchor "fridge repair london", count 1) — confirmed present, not modified (publish job owns this file per skill rules; no change needed since it already exists).
Reason category: leak (real GSC query getting meaningful clicks, but 31/33 of them land on the homepage instead of the dedicated page per the check2 breakdown — the dedicated page needed its on-page SEO strengthened, schema bug fixed, and Emergency Same Day convention applied so it can compete with the homepage for this query rather than keep losing clicks to it).

### Skipped / not touched tonight (1-page-per-run limit)
- `commercial-fridge-repair-north-london.html`, `commercial-freezer-repair-tottenham.html`, the `cold-room-repair-{borough}.html` batch: same as prior runs — no individual GSC query/page row in tonight's `gsc_report.csv` grounding a keyword choice for any of these specific URLs. Still candidates for a future run once/if GSC surfaces page-level data for them.
- `check2` GSC cannibalisation for "freezer repair london" (still landing across `/`, `/fridge-freezer-repairs-london` per prior notes — those file paths still do not exist on disk): unchanged from the 2026-09-26 note, needs its own investigation pass before any web.config redirect work, not attempted tonight.
- A second real opportunity exists in tonight's data — `commercial freezer repair london` (10 clicks, pos 4.77, CTR 77% — already a winner per the CTR>40%+pos<5 rule, so this would be a "leave title alone, verify robots/schema only" pass on `commercial-freezer-repair-north-london.html`, not a full rewrite) — flagged as tomorrow's candidate rather than attempting a second page tonight per the 1-page-per-run limit.

### Publish verification — 2026-09-28 22:05
Committed bbf007c, pushed to main. GitHub Actions "Deploy to WHUK Plesk" run 36482395950 completed success (26s). Live https://www.colddirect.co.uk/fridge-repair-london/ checked post-deploy: title, meta description, robots meta, canonical, and Service schema serviceType all match the committed source. GSC URL Inspection API (service account) verdict for the page: PASS, coverageState "Submitted and indexed", robotsTxtState ALLOWED, indexingState INDEXING_ALLOWED, googleCanonical/userCanonical both `https://www.colddirect.co.uk/fridge-repair-london/`, richResultsResult PASS (Review snippets detected). No DO-NOT-TOUCH files were touched; internal link check on the page found no broken (4xx/5xx) links.

## PUBLISHED — commercial-freezer-repair-north-london — 2026-10-05 21:15
Keyword Tags: commercial freezer repair london, commercial freezer repair north london, Foster freezer repair, Williams freezer repair, commercial refrigeration repair London
SEO Focus: local intent, commercial, emergency, brand-specific
Target Borough: North London (Enfield base)
GSC Source: query=commercial freezer repair london clicks=10 impressions=11 pos=3.36 CTR=90.9% date=2026-10-05 (top_queries row, gsc_report.csv) — WINNER per the CTR>40%+pos<5 rule (position 3.36, CTR 90.9%), so per the skill's own checklist this page gets a "verify robots/schema only" pass, NOT a title/content rewrite.
Files touched:
- commercial-freezer-repair-north-london.html (root)
- commercial-freezer-repair-north-london/index.html (folder, live IIS URL)
- colddirect-public-html/commercial-freezer-repair-north-london.html
Before/after title: unchanged on all 3 copies — this is a winner page (pos 3.36 < 5, CTR 90.9% > 40%), so per the checklist's WINNER exemption the title is left as-is, not rewritten onto the Emergency Same Day convention.
Before/after robots: all 3 copies had NO explicit <meta name="robots"> tag at all (defaulted indexable but unverifiable) -> added explicit <meta name="robots" content="index, follow"> to all 3, directly after <title>. This is the only change made tonight.
Change summary: page was already substantial (1816 words, existing schema markup present) and already ranking as a genuine winner for its target query — confirmed via live GSC data, not assumed. The only real gap found was the missing explicit robots directive, which the skill's checklist requires on money/singular pages regardless of ranking status. No title, H1, meta description, schema, or body content was touched — this is a minimal, targeted fix matching the "verify robots/schema only" instruction for winner pages, not a full rewrite.
Internal links: not modified this run — scripts/internal_linking.js and homepage links are the publish job's responsibility per skill rules; no evidence tonight that this page needs new internal link weight (it is already winning for its target query).
Reason category: winner (confirmed via real GSC data: position 3.36, CTR 90.9%, meeting both the position<5 AND CTR>40% winner criteria) — fix was a compliance gap (missing robots meta), not a ranking-opportunity rewrite.

### Skipped / not touched tonight (1-page-per-run limit)
- `commercial-fridge-repair-north-london.html`, `commercial-freezer-repair-tottenham.html`, the `cold-room-repair-{borough}.html` batch: still no individual GSC query/page row in tonight's gsc_report.csv grounding a keyword choice for any of these specific URLs.
- This draft pass was run manually (not via the cron job) specifically to test whether removing the free-form final-response step (per the LESSONS-LEARNED.md 2026-10-05 fix) resolves the standing truncation bug — see LESSONS-LEARNED.md for the outcome of this test.

### Publish verification — 2026-10-05 21:22
Committed 0e0aa88, pushed to main. GitHub Actions "Deploy to WHUK Plesk" run 37375444842 completed success (20s). Live https://www.colddirect.co.uk/commercial-freezer-repair-north-london/ checked post-deploy: title unchanged ("Commercial Freezer Same-Day Repair | North London | Cold Direct"), new `<meta name="robots" content="index, follow">` present, canonical unchanged (`https://www.colddirect.co.uk/commercial-freezer-repair-north-london/`). GSC URL Inspection API (service account) verdict: PASS, coverageState "Submitted and indexed", robotsTxtState ALLOWED, indexingState INDEXING_ALLOWED, googleCanonical/userCanonical both match the live URL, pageFetchState SUCCESSFUL. No DO-NOT-TOUCH files were touched (verified via `git diff --name-only` against the exclusion list before commit); internal link check on the page (all outbound hrefs) found no broken (4xx/5xx) links — logged to logs/overnight-seo-404.log.
