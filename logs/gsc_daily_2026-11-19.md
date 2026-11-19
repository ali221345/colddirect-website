# Google Search Console daily report — Cold Direct

- **Date generated:** 19 November 2026 (09:04 UTC)
- **Date range requested:** last 28 days (22 October 2026 – 18 November 2026) vs previous 28 days (24 September 2026 – 21 October 2026). End date = yesterday (18 November 2026).
- **Property:** `https://www.colddirect.co.uk/`
- **Search type:** web
- **Lag:** Search Console data is usually 2–3 days behind, so the latest days in any live pull are often incomplete.

## Status: Search Console tools unavailable in this run

This reporter **did not pull live 28-day analytics**. No totals, query tables, page tables, country/device splits, movers, or CTR-risk lists are shown below, because inventing figures or recycling a different window would be misleading.

### What was checked

1. **Cursor Search Console MCP** — not present in this automation. There is no Google Search Console tool namespace to call `sites.list` or `searchanalytics.query`.
2. **Credentials in this environment** — `GSC_CREDENTIALS_JSON`, `GOOGLE_APPLICATION_CREDENTIALS`, and local key files (`gsc-key.json`, `gsc-oauth.json`, `credentials.json`) are all missing. `google-auth` / `googleapiclient` are not installed here either. This cloud agent cannot authenticate to the Search Console API.
3. **Property existence (confirmed via GitHub Actions, not this reporter’s own API call)** — this run could not list sites itself. GSC Weekly Sync **scheduled** run `43884817807` on 16 November 2026 at 14:21 UTC (head `e014688`, job finished 14:28 UTC) authenticated with repo secret `GSC_CREDENTIALS_JSON`, resolved URL-prefix property `https://www.colddirect.co.uk/`, wrote a weekly performance Step Summary, submitted `https://www.colddirect.co.uk/sitemap.xml` (HTTP 204), and inspected URLs. Overall conclusion **success**. That is evidence the property exists and is reachable from GitHub Actions. No newer Weekly Sync has run (next schedule is Monday 23 November, `cron: 0 6 * * 1`).
4. **Performance confirmation is 7-day only** — the 16 November Weekly Sync Step Summary covers **8–14 November 2026** vs **1–7 November 2026**. Those weekly figures are **not** 28-day search analytics and are **not** copied into the tables below. The 9 November Weekly Sync `42637642714` (window 1–7 November vs 25–31 October) is superseded for property/performance confirmation.
5. **Monday Weekly Sync remains the latest GSC API call** — `.github/workflows/gsc-weekly-sync.yml` is still **active**. Run `43884817807` started late at **14:21 UTC** on 16 November and succeeded. There is no 17, 18, or 19 November Weekly Sync (weekly job only).
6. **Earlier Daily SEO confirmation** — ColdDirect Daily SEO last listed the same property on 18 October 2026 at 09:19 UTC (scheduled run `39114885014`). That Action used a 7-day window (11–17 October) and is still not a 28-day pull.
7. **Today’s scheduled Daily SEO** — as of 09:04 UTC on 19 November 2026 there is **no** `colddirect-daily-seo.yml` run for 19 October–19 November. On current `main` that workflow is **workflow_dispatch only** (cron disabled) and no longer references `GSC_CREDENTIALS_JSON` or a Search Console query step.

### What was not used

The 16 November weekly Action wrote a 7-day Step Summary (8–14 November vs 1–7 November). Agent-state and later SEO jobs also record other 7-day money-keyword windows. The 18 October Daily SEO Action wrote `seo-audit/daily-report-2026-10-18.md` using a **7-day** window (11–17 October 2026). Those figures are **not** copied here. Older 7-day files under `seo-audit/daily-report-*.md`, older 28-day files under `reports/gsc/`, and CSV logs (including `gsc_report.csv` / `gsc_followup.md`) were also left unused, because they are not a live pull for today’s 28-day windows.

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
- GitHub Actions last reached the property for a **performance** report on 16 November 14:21 UTC (Weekly Sync `43884817807`, 7-day window 8–14 November only). That Step Summary is not copied into the 28-day tables above. Overall conclusion was **success** (performance report, sitemap PUT HTTP 204, and URL Inspection completed). The 9 November weekly job `42637642714` is superseded for this confirmation.
- Nightly auto-seo on 10 November 21:50 UTC (run `42907266129`, head `715c04e`) is no longer the latest GSC sitemap/inspect call. Weekly Sync `43884817807` at 14:22 UTC on 16 November submitted `https://www.colddirect.co.uk/sitemap.xml` (HTTP 204); `lastSubmitted` 2026-11-16T14:22:50.837Z; `last downloaded` 2026-11-14T23:16:10.922Z; pending `True`; type `web` **137** submitted / **0** indexed. The same run’s live sitemap count was **137** URLs, duplicates 0, core pages missing: none. That is a sitemap-API note, not a 28-day search-analytics pull. The same run logged Indexing API calls **41/80** as OK in its table; this reporter did not request indexing.
- URL Inspection from that same 16 November 14:22–14:28 UTC step (41 of 150 inspection calls; not 28-day performance): homepage, `/fridge-repair-london/`, `/freezer-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`, `/cold-room-repair-london/`, `/catering-repair-london/`, `/commercial-appliances-repair-london/`, `/air-conditioning-repair-london/`, and `/cellar-cooler-repair-london/` were `PASS` / Submitted and indexed. `/commercial-fridge-repair-enfield/` is now `PASS` / Submitted and indexed (last crawl 2026-11-15 18:39:28 UTC); it had been `NEUTRAL` / Not found (404) on 10 November. `/display-cabinet-repair-london/` was not in this 41-URL inspect set (last known weekly inspect on 9 November: `NEUTRAL` / Discovered - currently not indexed; live HTTP 200 on 19 November 09:05 UTC). New inspect notes from this 41-URL batch: `/commercial-refrigeration-repair-harlesden/` `NEUTRAL` / URL is unknown to Google; `/commercial-refrigeration-repair-willesden/` `NEUTRAL` / Discovered - currently not indexed. Both returned live HTTP 200 on 19 November 09:05 UTC. The 13-URL weekly watchlist in the 16 November performance report showed **9 of 13 PASS**, 4 waiting (duplicate canonicals on `/cold-room-repair-edgware/`, `/cold-room-repair-finchley/`, `/cold-room-repair-tottenham/`, `/cold-room-repair-wembley/`), 0 inspection failed. This reporter did not request indexing.
- There was **no** 13, 14, 15, 16, 17, or 18 November 21:40 UTC nightly auto-seo run. GitHub reports `.github/workflows/auto-seo-nightly.yml` as **disabled_manually** (`updated_at` 13 November 2026 12:33:38 UTC). The 18 November 21:40 UTC slot has now passed with no run. The last GitHub nightly that reached live auto-seo, smoke, and preflight was `43312507239` on 12 November 21:40 UTC (head `548f884`); it then failed SEO integrity and **skipped** the GSC ping. That smoke test counted **139** sitemap URLs.
- Live-site alert issue **#135** is still **closed** (closed at 14 November 2026 11:55:48 UTC after Deploy to WHUK Plesk run `43592005480`). Later successful Plesk deploys on 14 November include `43643032040` (21:28 UTC) and `43652052328` (23:12 UTC). There has been **no** Deploy to WHUK Plesk run on 15–19 November as of 09:04 UTC. Those deploy workflows are **not** Search Console sitemap/inspect pings. The latest GSC API confirmation is still the 16 November Weekly Sync.
- Live `https://www.colddirect.co.uk/sitemap.xml` fetched for this report (19 November 09:05 UTC) returned HTTP 200, `last-modified: Tue, 17 Nov 2026 12:15:28 GMT`, **137** unique `<loc>` values, and **0** `/_old_site_backup/` URLs. Watch pages present and live HTTP 200: homepage, `/cold-room-repair-london/`, `/fridge-repair-london/`, `/freezer-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`. Extra live HTTP 200: `/commercial-fridge-repair-enfield/`, `/display-cabinet-repair-london/`, `/commercial-refrigeration-repair-harlesden/`, `/commercial-refrigeration-repair-willesden/`. Search Console’s last sitemap-API read (16 November 14:22 UTC) also showed **137** submitted / **0** indexed, matching the live file count. The live last-modified stamp is **unchanged** from yesterday’s check (still 17 November 12:15:28 GMT); that is a live-file timestamp, not a 28-day Search Console metric.
- Previous Search Console-unavailable daily PRs through **#142** (18 November) were still unmerged at report time. No 2 November daily-report pull request was opened.

## Recommended next actions (no HTML edits in this run)

1. Add Search Console access to this Cursor automation: either a Google Search Console MCP server, or the same `GSC_CREDENTIALS_JSON` secret already used by `.github/workflows/gsc-weekly-sync.yml` and nightly auto-seo.
2. Re-run this reporter once credentials or MCP are attached, then fill last-28 vs previous-28 totals, top 25 tables, country/device splits, movers, and watch lists from live API data.
3. Keep HTML, titles, and marketing copy unchanged until a live 28-day pull exists. Do not request indexing from this report.
4. Separately (process notes, not 28-day analytics): re-enable the Nightly auto-seo GitHub workflow (currently disabled_manually, so no 21:40 UTC GSC ping can run from Actions); read the 16 November Weekly Sync Step Summary in run `43884817807` for the 7-day window 8–14 November; check the four duplicate-canonical cold-room borough URLs on the weekly watchlist (`/cold-room-repair-edgware/`, `/cold-room-repair-finchley/`, `/cold-room-repair-tottenham/`, `/cold-room-repair-wembley/`); re-check `/display-cabinet-repair-london/` (not in the 16 November 41-URL inspect set), `/commercial-refrigeration-repair-harlesden/` (unknown to Google), and `/commercial-refrigeration-repair-willesden/` (Discovered - currently not indexed); note that Daily SEO on `main` is still dispatch-only and no longer queries Search Console in YAML. Do not repeat indexing requests from this reporter.

## Short summary

- **Totals:** not available (Search Console MCP and credentials missing in this environment).
- **3 biggest wins:** not available — no live 28-day query or page rows. Process notes only: the URL-prefix property `https://www.colddirect.co.uk/` was last reached on 16 November (Weekly Sync `43884817807` at 14:21 UTC) for a 7-day performance report plus sitemap/inspect; homepage and nine money hubs remain PASS / Submitted and indexed; `/commercial-fridge-repair-enfield/` recovered from an inspection 404 to PASS / Submitted and indexed; live sitemap still has 137 URLs with all six watch pages HTTP 200, last-modified still 17 November 12:15:28 GMT.
- **3 biggest risks:** (1) this daily GSC report cannot run without API access in the Cursor automation, Daily SEO on `main` is still dispatch-only without a GSC query step (no 19 October–19 November Daily SEO run), the Nightly auto-seo workflow is **disabled_manually** so there was no 13–18 November 21:40 UTC GSC ping, and the 2 November daily report PR was not opened; (2) 28-day movers and high-impression low-CTR queries are unknown until a live pull; (3) Search Console still last showed 0 indexed URLs against 137 submitted, `/display-cabinet-repair-london/` was not re-inspected, `/commercial-refrigeration-repair-harlesden/` is unknown to Google, `/commercial-refrigeration-repair-willesden/` remains Discovered - currently not indexed, four cold-room borough URLs are duplicate-canonical, and watch queries / money pages cannot be monitored here until credentials or MCP are added.
