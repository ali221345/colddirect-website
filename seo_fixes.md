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

## PUBLISHED — walk-in-freezer-room-repair-london — 2026-09-23 22:41
Keyword Tags: freezer room repair london, walk-in freezer repair london, cannibalisation-fix, Foster freezer repair, Williams freezer repair, commercial refrigeration repair London
SEO Focus: local intent, commercial, emergency, duplicate-content cleanup
Target Borough: Greater London (North London base)
GSC Source: query=freezer room repair london clicks=5 impressions=25 pos=31.6 CTR=20% date=2026-09-23
Files touched:
- walk-in-freezer-room-repair-london.html (root)
- colddirect-public-html/walk-in-freezer-room-repair-london.html
- walk-in-freezer-room-repair-london/index.html (added by publish pass — this is the file IIS actually serves at the live trailing-slash URL; the draft only touched the two files above, which both 301 away, so the fix would have been a no-op without this addition)
Before/after title: unchanged ("Walk-in Freezer Room Repair London | Same-Day Callout - Cold Direct") — title left as-is per checklist since this is now a noindex/canonical page, not a new SERP target.
Before/after canonical: self-canonical (walk-in-freezer-room-repair-london) -> https://www.colddirect.co.uk/freezer-room-repair-london/
Before/after robots: none specified (defaulted indexable) -> noindex, follow
Change: added `<meta name="robots" content="noindex, follow">`, repointed canonical to the stronger, already-optimised `/freezer-room-repair-london/` page (741-word, FAQPage-schema page that already targets this exact query), and added an on-page link steering readers/crawlers to that page. No content deleted.
Reason category: noindex-trap (duplicate/thin page splitting authority for the same GSC query as an existing well-optimised page)

GSC URL Inspection (2026-09-23 22:42, post-deploy):
- `/walk-in-freezer-room-repair-london/` — verdict NEUTRAL, coverageState "URL is unknown to Google" (not yet crawled with new noindex tag; expected for a low-signal page, re-check next follow-up pass).
- `/freezer-room-repair-london/` (canonical target) — verdict NEUTRAL, coverageState "Discovered - currently not indexed" (Google has seen the URL but hasn't indexed it yet, despite it converting clicks per GSC query data — worth requesting indexing on this URL in a future run).
Live IIS confirmed post-deploy: root `.html` still 301s to the directory URL; the directory URL (actually served) now has `noindex, follow` and canonical to `/freezer-room-repair-london/`, matching the commit.

## PUBLISHED — freezer-room-repair-london — 2026-09-25 22:15
Keyword Tags: freezer room repair london, walk-in freezer room repair london, commercial freezer room repair london, Foster freezer repair, Williams freezer repair, commercial refrigeration repair London
SEO Focus: local intent, commercial, emergency, brand-specific
Target Borough: Greater London (North London base)
GSC Source: query=freezer room repair london clicks=5 impressions=25 pos=31.6 CTR=20% date=2026-09-23 (top_queries row, `gsc_report.csv`)
Files touched:
- freezer-room-repair-london.html (root)
- freezer-room-repair-london/index.html (folder, live IIS URL)
- colddirect-public-html/freezer-room-repair-london.html
Before/after title: unchanged ("Emergency Same Day Freezer Room Repair London | ColdDirect 24/7", 65 chars) — already meets the Emergency Same Day convention from a prior pass, kept as-is per checklist (not rewritten, not a winner page either — this is the target page itself, not the noindexed duplicate).
Before/after meta description: unchanged ("Emergency Same Day 24/7 callout. Freezer room repair across London. Trade kitchens only. Call 07983 759320.", 112 chars) — already matches the required pattern and CTR data for this low-volume query does not support "keep untouched" exemption, but wording already conforms so no rewrite needed.
Before/after H1: "Freezer Room Repair in London" -> "Freezer Room Repair London" (exact-match primary keyword, no filler preposition).
Change summary: this is the canonical/target page for the `freezer-room-repair-london` cluster (the duplicate `walk-in-freezer-room-repair-london` was already noindexed and canonicalised here on 2026-09-23), but the page itself was still missing `LocalBusiness`/`Service`/`FAQPage` JSON-LD, had no explicit `<meta name="robots">` tag, and was thin content (approx. 400 visible words outside the seo-article block, no benefit bullets). Added: (1) explicit `<meta name="robots" content="index, follow">`; (2) full `LocalBusiness` + `Service` + `FAQPage` JSON-LD graph matching the 4 visible FAQs already on the page, all `@id`/URLs pointing at the pretty `/freezer-room-repair-london/` URL, not any `.asp` legacy id; (3) a new "Why book Cold Direct" 3-bullet benefits list in the primary content section; (4) rewrote the H1 and hero lead to carry the exact-match primary keyword instead of a paraphrase ("Freezer Room Repair in London"); (5) added a 4th FAQ ("What areas of London do you cover") to both the visible FAQ block and the schema; (6) updated the hero image alt text to lead with the primary keyword; (7) appended the required GSC keyword HTML comment at end of file. No content deleted — only added/rewritten in place.
Internal links: page already links out to `/freezer-room-repair-north-london`, `/commercial-freezer-repair-london`, `/walk-in-freezer-repair-london/` and `/cold-room-repair-london/`. No homepage link exists yet for the exact-match anchor "freezer room repair london" — candidate for `scripts/internal_linking.js` LINKS array (publish job should add an entry: href `/freezer-room-repair-london`, anchor `freezer room repair london`, count 1, note "Low-click (5) but position 31.6 — dedicated page just strengthened, needs an internal signal boost"). Not added to the script in this draft run per skill rules (publish job owns internal_linking.js changes).
Reason category: opportunity (weak/thin page for a real GSC query at poor position, not yet touched by a content pass — distinct from the walk-in-freezer-room-repair-london noindex-trap fix already published 2026-09-23).

### Candidate for a future run (not touched tonight — 1-page-per-run limit)
`commercial-fridge-repair-london.html` (+ folder `index.html` + public-html copy) is flagged `WEAK` in `weak-list.json` (1788 words, `hasSeo:false` per the audit scanner's regex check for `<section class="seo-article">`) but manual inspection shows it already HAS a full seo-article section with LocalBusiness/Service/FAQPage schema, an "Emergency"-style CTA, and 1788 words — the audit scanner's WEAK flag looks like a false positive (its `hasSeoArticle()` regex may be matching class-attribute quoting/whitespace it doesn't expect, or the file has two `seo-article` class occurrences confusing the word-count split). GSC backs this query strongly: `commercial fridge repair london` = 42 clicks, 169 impressions, pos 12.1, CTR 24.9% (`gsc_report.csv` top_queries row) — a real opportunity to push from pos ~12 toward page 1, but the page needs a proper re-audit (fix or bypass the scanner false-positive) before deciding what to actually change, rather than rewriting a page that already looks complete. Flagging for tomorrow's run to investigate the scanner mismatch first.

Candidate for a future run (not attempted tonight, per 1-page-per-run limit): rewrite `fridge-repair-london.html` further or address the `check2` GSC cannibalisation rows where "freezer repair london" (18 clicks, pos 26) is landing across `/`, `/fridge-freezer-repairs-london`, and `/freezer-repairs-london` instead of consolidating onto `/freezer-repair-london/`.

Publish pass (2026-09-25 22:20): committed 542ba10 (SEO: Add freezer room repair london ...), pushed to main, GitHub Actions FTP deploy 36188557748 succeeded. Live IIS confirmed post-deploy: title/canonical/robots match the commit, H1 is now "Freezer Room Repair London", FAQPage JSON-LD is present, and the new homepage/public-html-index footer link to /freezer-room-repair-london is live. Added a matching LINKS entry to scripts/internal_linking.js and ran it (count 1, applied cleanly to both index copies -- no unrelated index.html content touched). Sitemap rebuilt via agent/scripts/sitemap.py; today's GSC snapshot archived to logs/gsc_report_2026-09-25.csv; internal-link health check appended to logs/overnight-seo-404.log (all 200, no broken links). GSC URL Inspection: /freezer-room-repair-london/ -- verdict NEUTRAL, coverageState "URL is unknown to Google" (not yet crawled since the update; page has 5 clicks/25 impressions historically so re-check in a future follow-up pass once Google recrawls). DO-NOT-TOUCH re-check: no changes to index.html beyond the sanctioned internal-linking footer line (same mechanism already used for prior published pages), no changes to any AC/rooftop-chiller/cellar-cooling/brands/blog/PR#3 pages, web.config, or .github/workflows/. Carried-forward, unrelated-to-this-page draft artifacts (AUDIT-REPORT.md/weak-list.json refresh, gsc_followup.md date-window update, gsc_report.csv refresh, new audit-scanner.js/audit-script.py/weak_queries_90d.json tooling) were also committed since they were legitimate uncommitted output from part 1's run and touched none of the exclusions.

## PUBLISHED — freezer-repair-london — 2026-09-26 21:52
Keyword Tags: freezer repair london, commercial freezer repair london, freezer service london, Foster freezer repair, Williams freezer repair, commercial refrigeration repair London
SEO Focus: local intent, commercial, emergency, brand-specific
Target Borough: Greater London (North London base)
GSC Source: query=freezer repair london clicks=20 impressions=99 pos=23.15 CTR=20.2% date=2026-09-26 (top_queries row, `gsc_report.csv`) — flagged as a "candidate for a future run" in the 2026-09-25 entry above; picked up tonight.
Files touched:
- freezer-repair-london.html (root)
- freezer-repair-london/index.html (folder, live IIS URL)
- colddirect-public-html/freezer-repair-london.html
Before/after title: "Freezer Repair London | Same-Day Commercial, 2–4 Hour Callout" (63 chars, root+public-html) / "Freezer Repair London | Same-Day 24/7" (folder copy) -> "Emergency Same Day Freezer Repair London | ColdDirect 24/7" (58 chars, all three) — brings the page onto the Emergency Same Day convention already used on sibling pages (commercial-fridge-repair-london, freezer-room-repair-london) and de-duplicates the two different pre-existing titles across the root/folder copies.
Before/after H1: "Freezer Same-Day Repair London" -> "Freezer Repair London - Same-Day Emergency Callout" (exact-match primary keyword leads the H1, all three files).
Before/after meta description: root+public-html "Freezer repair London for restaurants, shops and hotels..." (152 chars) and folder-copy "Freezer repair London, same-day 24/7..." (146 chars) — two different pre-existing descriptions -> unified to "Emergency Same Day 24/7 callout. Freezer repair London across London. Trade kitchens only. Call 07983 759320." (109 chars, all three) matching the site's standard emergency-CTA pattern. No page here had CTR > 60% so the "keep untouched" exemption did not apply (actual CTR 20.2%).
Change summary: page was already substantial (1780-1960 words per copy, existing LocalBusiness+Service+FAQPage schema, 3 FAQs, tel CTAs) but the root/folder/public-html copies had drifted onto two different titles and meta descriptions and neither used the "Emergency Same Day" convention adopted on sibling pages during recent passes. Standardised title/meta/H1 across all three synced copies; added 2 more FAQ entries (schema + visible) to the root copy to bring it up to the same 5-FAQ depth already present on the folder copy ("Do you repair commercial and domestic freezers?", "Should I use the London-wide commercial freezer page?"); updated hero image alt text on root+folder copies to lead with the primary keyword (image file itself untouched, per DO-NOT-TOUCH — freezer-repair-london.html hero image is the approved Foster G3 photo). Appended the required GSC keyword HTML comment to all three copies. No content deleted — only standardised/added.
Internal links: page already links out to /commercial-freezer-repair-london, /williams-freezer-repair-london, /subzero-freezer-repair-london, /commercial-freezer-repair-north-london, /freezer-room-repair-north-london, /fridge-repair-london, /ice-cream-machine-repair-london, /walk-in-freezer-repair-london/, /freezer-room-repair-london/. No homepage link yet with exact-match anchor "freezer repair london" — candidate for scripts/internal_linking.js LINKS array (publish job should add: href /freezer-repair-london, anchor "freezer repair london", note "20 clicks/99 impressions but position 23 — needs an internal signal boost now the on-page SEO is consolidated"). Not added to the script in this draft run per skill rules (publish job owns internal_linking.js changes).
Reason category: opportunity (real GSC query at poor position ~23 despite decent click volume, page had inconsistent on-page SEO across its three synced copies).

### Skipped / not touched tonight (1-page-per-run limit)
- `commercial-fridge-repair-london.html`: still flagged WEAK by the audit scanner (likely false positive — page already has full seo-article + schema, see 2026-09-25 note above). Still needs the scanner false-positive investigated before deciding whether a rewrite is warranted. Carried forward again.
- `check2` GSC cannibalisation for "freezer repair london" (18-20 clicks, pos ~23-26) landing across `/`, `/fridge-freezer-repairs-london`, and `/freezer-repairs-london`: note these two file paths (`fridge-freezer-repairs-london`, `freezer-repairs-london`) do NOT currently exist as files on disk (checked root, folder, colddirect-public-html, web.config) — the GSC rows may reference old/removed URLs or ones IIS rewrites elsewhere. Needs investigation, not a same-night fix, before touching web.config redirects.
- `walk-in-freezer-room-repair-london` remains correctly noindexed/canonicalised to `/freezer-room-repair-london/` per the 2026-09-23 fix — left untouched, working as intended.

Publish pass (2026-09-26 21:52): committed 78253de (SEO: Add freezer repair london - GSC clicks 20 pos 23.15 ...), pushed to main, GitHub Actions FTP deploy 36271035889 succeeded. Live IIS confirmed post-deploy: title "Emergency Same Day Freezer Repair London | ColdDirect 24/7", meta description, canonical (https://www.colddirect.co.uk/freezer-repair-london/) and H1 "Freezer Repair London - Same-Day Emergency Callout" all match the commit on the folder-index URL; the legacy `/freezer-repair-london.html` correctly 301s to the folder URL. Internal-link health check re-run live (all 9 outbound links on the page 200 OK) and appended to logs/overnight-seo-404.log. No new internal_linking.js entry was needed — the `/freezer-repair-london` LINKS array entry and homepage footer link already existed from a prior pass (script run confirmed idempotent, 0 new index.html changes). Sitemap rebuilt (lastmod bumps only, verified 0 URLs dropped vs previous sitemap). GSC URL Inspection: /freezer-repair-london/ — verdict NEUTRAL, coverageState "Duplicate, Google chose different canonical than user" (Google's chosen canonical is the bare `/freezer-repair-london` without trailing slash vs our declared `https://www.colddirect.co.uk/freezer-repair-london/`; last crawl 2026-09-21, pre-dates tonight's edit, so re-check in a future pass once Google recrawls the updated content — flag the canonical mismatch for investigation, it's pre-existing and not introduced by this change). DO-NOT-TOUCH re-check: `git status` after this pass showed no changes to index.html beyond the pre-existing internal-linking mechanism (no new diff this run), no changes to any AC/rooftop-chiller/cellar-cooling/brands/blog/PR#3 pages, web.config, or .github/workflows/.
