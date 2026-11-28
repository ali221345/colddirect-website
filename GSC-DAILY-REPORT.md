# Google Search Console daily report — Cold Direct

- **Date generated:** 27 November 2026 (09:05 UTC)
- **Date range requested:** last 28 days (30 October 2026 – 26 November 2026) vs previous 28 days (2 October 2026 – 29 October 2026). End date = yesterday (26 November 2026).
- **Property:** `https://www.colddirect.co.uk/`
- **Search type:** web
- **Lag:** Search Console data is usually 2–3 days behind, so the latest days in any live pull are often incomplete.

## Status: Search Console tools unavailable in this run

This reporter **did not pull live 28-day analytics**. No totals, query tables, page tables, country/device splits, movers, or CTR-risk lists are shown below, because inventing figures or recycling a different window would be misleading.

### What was checked

1. **Cursor Search Console MCP** — not present in this automation. There is no Google Search Console tool namespace to call `sites.list` or `searchanalytics.query`.
2. **Credentials in this environment** — `GSC_CREDENTIALS_JSON`, `GOOGLE_APPLICATION_CREDENTIALS`, and local key files (`gsc-key.json`, `gsc-oauth.json`, `credentials.json`) are all missing. `google-auth` / `googleapiclient` are not installed here either. This cloud agent cannot authenticate to the Search Console API.
3. **Property existence (confirmed via GitHub Actions, not this reporter’s own API call)** — this run could not list sites itself. GSC Weekly Sync **scheduled** run `45221689093` on 23 November 2026 at 16:54 UTC (head `2b7655e`, finished 17:00 UTC) authenticated with repo secret `GSC_CREDENTIALS_JSON`, resolved URL-prefix property `https://www.colddirect.co.uk/`, wrote a weekly performance Step Summary, submitted `https://www.colddirect.co.uk/sitemap.xml` (HTTP 204), and inspected URLs. Overall conclusion **success**. That is evidence the property exists and is reachable from GitHub Actions. There is no newer Weekly Sync as of 09:05 UTC on 27 November (next cron is Monday 30 November 06:00 UTC). The 16 November Weekly Sync `43884817807` is superseded for this confirmation.
4. **Performance confirmation is 7-day only** — the 23 November Weekly Sync Step Summary covers **15–21 November 2026** vs **8–14 November 2026**. Those weekly figures are **not** 28-day search analytics and are **not** copied into the tables below.
5. **Monday Weekly Sync remains the latest GSC API call** — `.github/workflows/gsc-weekly-sync.yml` is still **active**. Run `45221689093` started late at **16:54 UTC** on 23 November and succeeded. There is no 24, 25, 26, or 27 November Weekly Sync as of 09:05 UTC.
6. **Earlier Daily SEO confirmation** — ColdDirect Daily SEO last listed the same property on 18 October 2026 at 09:19 UTC (scheduled run `39114885014`). That Action used a 7-day window (11–17 October) and is still not a 28-day pull.
7. **Today’s scheduled Daily SEO** — as of 09:05 UTC on 27 November 2026 there is **no** `colddirect-daily-seo.yml` run for 19 October–27 November. On current `main` that workflow is **workflow_dispatch only** (cron disabled) and no longer references `GSC_CREDENTIALS_JSON` or a Search Console query step.

### What was not used

The 23 November weekly Action wrote a 7-day Step Summary (15–21 November vs 8–14 November). Agent-state and later SEO jobs also record other 7-day money-keyword windows. The 18 October Daily SEO Action wrote `seo-audit/daily-report-2026-10-18.md` using a **7-day** window (11–17 October 2026). Those figures are **not** copied here. Older 7-day files under `seo-audit/daily-report-*.md`, older 28-day files under `reports/gsc/`, and CSV logs (including `gsc_report.csv` / `gsc_followup.md`) were also left unused, because they are not a live pull for today’s 28-day windows.

## Site totals vs previous period

| Metric | Last 28 days | Previous 28 days | Change |
|---|---:|---:|---|
| Clicks | — | — | — |
| Impressions | — | — | — |
| CTR | — | — | — |
| Average position | — | — | — |

*No live Search Console rows for these windows.*

## Top queries and top pages

- Top 25 queries by clicks: **not available**
- Top 25 pages by clicks: **not available**
- Top 25 queries by impressions: **not available**
- Country split (row limit 20): **not available**
- Device split (row limit 20): **not available**

## Watch queries and watch pages

Could not be scored for these 28-day windows:

- Queries: cold room repair london; commercial fridge repair london; fridge repair london; freezer repair london; commercial freezer repair london
- Pages: homepage; cold-room repairs; fridge-repair-london; freezer-repair-london; commercial-fridge-repair-london; commercial-freezer-repair-london

## Movers and risks

- Live 28-day click, impression, and position movers could not be calculated.
- High-impression, low-CTR queries (impressions > 300, CTR < 2%) could not be listed.
- Watch-query and watch-page movement could not be listed.
- GitHub Actions last reached the property for a **performance** report on 23 November 16:54 UTC (Weekly Sync `45221689093`, 7-day window 15–21 November only). That Step Summary is not copied into the 28-day tables above. Overall conclusion was **success** (performance report, sitemap PUT HTTP 204, and URL Inspection completed). The 16 November weekly job `43884817807` is superseded for this confirmation.
- Nightly auto-seo on 10 November 21:50 UTC (run `42907266129`, head `715c04e`) is no longer the latest GSC sitemap/inspect call. Weekly Sync `45221689093` at 16:56 UTC on 23 November submitted `https://www.colddirect.co.uk/sitemap.xml` (HTTP 204); `lastSubmitted` 2026-11-23T16:56:03.549Z; `last downloaded` 2026-11-23T16:14:43.850Z; pending `True`; type `web` **136** submitted / **0** indexed. The same run’s live sitemap count was **136** URLs, duplicates 0, core pages missing: none. That is a sitemap-API note, not a 28-day search-analytics pull. The same run logged Indexing API calls **36/80** as OK in its table; this reporter did not request indexing.
- URL Inspection from that same 23 November 16:56–17:00 UTC step (36 of 150 inspection calls; not 28-day performance): homepage, `/fridge-repair-london/`, `/freezer-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`, `/cold-room-repair-london/`, `/catering-repair-london/`, `/commercial-appliances-repair-london/`, `/air-conditioning-repair-london/`, and `/cellar-cooler-repair-london/` were `PASS` / Submitted and indexed. `/commercial-fridge-repair-enfield/` remains `PASS` / Submitted and indexed. `/blast-chiller-repair-north-london/` and `/chiller-repair-north-london/` are now `PASS` / Submitted and indexed in this 36-URL set (they were `NEUTRAL` / Discovered - currently not indexed on 29 October). `/display-cabinet-repair-london/` was **not** in this 36-URL inspect set (last known weekly inspect on 9 November: `NEUTRAL` / Discovered - currently not indexed; live HTTP 200 on 27 November 09:05 UTC). `/commercial-refrigeration-repair-harlesden/` and `/commercial-refrigeration-repair-willesden/` were also **not** in this 36-URL inspect set (last known 16 November 41-URL inspect: Harlesden `NEUTRAL` / URL is unknown to Google; Willesden `NEUTRAL` / Discovered - currently not indexed). Both returned live HTTP 200 on 27 November 09:05 UTC. The 13-URL weekly watchlist in the 23 November performance report still showed **9 of 13 PASS**, 4 waiting (duplicate canonicals on `/cold-room-repair-edgware/`, `/cold-room-repair-finchley/`, `/cold-room-repair-tottenham/`, `/cold-room-repair-wembley/`), 0 inspection failed. This reporter did not request indexing.
- There was **no** 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, or 26 November 21:40 UTC nightly auto-seo run. GitHub reports `.github/workflows/auto-seo-nightly.yml` as **disabled_manually** (`updated_at` 13 November 2026 12:33:38 UTC). The 26 November 21:40 UTC slot has now passed with no run. The last GitHub nightly that reached live auto-seo, smoke, and preflight was `43312507239` on 12 November 21:40 UTC (head `548f884`); it then failed SEO integrity and **skipped** the GSC ping. That smoke test counted **139** sitemap URLs.
- Live-site alert issue **#135** is still **closed** (closed at 14 November 2026 11:55:48 UTC after Deploy to WHUK Plesk run `43592005480`). Later successful Plesk deploys include `43643032040` (14 November 21:28 UTC), `43652052328` (14 November 23:12 UTC), **`44555490054`** (19 November 15:30 UTC, head `9f2992e`, blog consolidation retiring `/blog/why-commercial-freezer-icing-up/` with a 301 to `/blog/commercial-freezer-ice-buildup-causes/`), and **`45814210292`** (26 November 11:50–11:55 UTC, head `d0cfc5a`, “Rewrite hero money-page copy in human engineer voice (11 pages)”). There has been **no** Deploy to WHUK Plesk run on 15–18 November, none on 20–25 November, and none yet on 27 November as of 09:05 UTC. Those deploy workflows are **not** Search Console sitemap/inspect pings. The latest GSC API confirmation is the 23 November Weekly Sync.
- Live `https://www.colddirect.co.uk/sitemap.xml` fetched for this report (27 November 09:05 UTC) returned HTTP 200, `last-modified: Thu, 26 Nov 2026 11:55:21 GMT` (**changed** from yesterday’s 25 November 13:16:37 GMT), **136** unique `<loc>` values, and **0** `/_old_site_backup/` URLs. Retired blog URL `/blog/why-commercial-freezer-icing-up/` is **absent**; survivor `/blog/commercial-freezer-ice-buildup-causes/` is **present**. Watch pages present and live HTTP 200: homepage, `/cold-room-repair-london/`, `/fridge-repair-london/`, `/freezer-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`. Extra live HTTP 200: `/commercial-fridge-repair-enfield/`, `/display-cabinet-repair-london/`, `/commercial-refrigeration-repair-harlesden/`, `/commercial-refrigeration-repair-willesden/`. The 11:55 UTC timestamp on 26 November matches Deploy to WHUK Plesk run `45814210292` (started 11:50 UTC, finished 11:55:19 UTC, conclusion **success**, head `d0cfc5a`). Skip-ci docs commit `3ca19a9` (“docs: autopilot job report”) landed at 11:55:15 UTC on the same push. Unique URL count is unchanged at **136**. Treat the timestamp as a live-file / Plesk-deploy note, not a 28-day Search Console metric and not evidence that last night’s Plesk `auto-seo.aspx` rewrite ran (the 26 November 20:21 slot is not confirmed by GitHub). Search Console’s last sitemap-API read (23 November 16:56 UTC) showed **136** submitted / **0** indexed, still matching the live file count. Last Site backup (48h) remains `45619354854` on 25 November 13:01 UTC; the next 48-hour slot had not started as of 09:05 UTC on 27 November.
- Previous Search Console-unavailable daily PRs through **#150** (26 November) were still unmerged at report time. No 2 November daily-report pull request was opened.

## Recommended next actions (no HTML edits in this run)

1. Add Search Console access to this Cursor automation: either a Google Search Console MCP server, or the same `GSC_CREDENTIALS_JSON` secret already used by `.github/workflows/gsc-weekly-sync.yml` and nightly auto-seo.
2. Re-run this reporter once credentials or MCP are attached, then fill last-28 vs previous-28 totals, top 25 tables, country/device splits, movers, and watch lists from live API data.
3. Keep HTML, titles, and marketing copy unchanged until a live 28-day pull exists. Do not request indexing from this report. The 26 November Plesk deploy of money-page copy is already live; this reporter is not scoring its Search Console effect.
4. Separately (process notes, not 28-day analytics): re-enable the Nightly auto-seo GitHub workflow (currently disabled_manually, so no 21:40 UTC GSC ping can run from Actions); read the 23 November Weekly Sync Step Summary in run `45221689093` for the 7-day window 15–21 November; check the four duplicate-canonical cold-room borough URLs on the weekly watchlist (`/cold-room-repair-edgware/`, `/cold-room-repair-finchley/`, `/cold-room-repair-tottenham/`, `/cold-room-repair-wembley/`); re-check `/display-cabinet-repair-london/` (not in the 23 November 36-URL inspect set), `/commercial-refrigeration-repair-harlesden/` (not re-inspected; last known unknown to Google), and `/commercial-refrigeration-repair-willesden/` (not re-inspected; last known Discovered - currently not indexed); note that Daily SEO on `main` is still dispatch-only and no longer queries Search Console in YAML. Do not repeat indexing requests from this reporter.

## Short summary

- **Totals:** not available (Search Console MCP and credentials missing in this environment).
- **3 biggest wins:** not available — no live 28-day query or page rows. Process notes only: the URL-prefix property `https://www.colddirect.co.uk/` was last reached on 23 November (Weekly Sync `45221689093` at 16:54 UTC) for a 7-day performance report plus sitemap/inspect; homepage and nine money hubs remain PASS / Submitted and indexed from that inspect; `/commercial-fridge-repair-enfield/` remains PASS; sitemap API still shows 136 submitted (matching the live file count); live sitemap still has 136 URLs (last-modified now 26 November 11:55:21 GMT after Plesk deploy `45814210292`, unique count unchanged), and all six watch pages HTTP 200.
- **3 biggest risks:** (1) this daily GSC report cannot run without API access in the Cursor automation, Daily SEO on `main` is still dispatch-only without a GSC query step (no 19 October–27 November Daily SEO run), the Nightly auto-seo workflow is **disabled_manually** so there was no 13–26 November 21:40 UTC GSC ping, and the 2 November daily report PR was not opened; (2) 28-day movers and high-impression low-CTR queries are unknown until a live pull, including any effect of the 26 November money-page copy deploy; (3) Search Console still shows 0 indexed URLs against 136 submitted, `/display-cabinet-repair-london/` was not re-inspected, `/commercial-refrigeration-repair-harlesden/` and `/commercial-refrigeration-repair-willesden/` were not in this week’s inspect set, four cold-room borough URLs are duplicate-canonical, and watch queries / money pages cannot be monitored here until credentials or MCP are added.
