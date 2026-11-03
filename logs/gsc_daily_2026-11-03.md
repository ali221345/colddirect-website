# Google Search Console daily report — Cold Direct

- **Date generated:** 3 November 2026 (09:03 UTC)
- **Date range requested:** last 28 days (6 October 2026 – 2 November 2026) vs previous 28 days (8 September 2026 – 5 October 2026). End date = yesterday (2 November 2026).
- **Property:** `https://www.colddirect.co.uk/`
- **Search type:** web
- **Lag:** Search Console data is usually 2–3 days behind, so the latest days in any live pull are often incomplete.

## Status: Search Console tools unavailable in this run

This reporter **did not pull live 28-day analytics**. No totals, query tables, page tables, country/device splits, movers, or CTR-risk lists are shown below, because inventing figures or recycling a different window would be misleading.

### What was checked

1. **Cursor Search Console MCP** — not present in this automation. There is no Google Search Console tool namespace to call `sites.list` or `searchanalytics.query`.
2. **Credentials in this environment** — `GSC_CREDENTIALS_JSON`, `GOOGLE_APPLICATION_CREDENTIALS`, and local key files (`gsc-key.json`, `gsc-oauth.json`, `credentials.json`) are all missing. The `google` / `google.auth` and `googleapiclient` libraries are not installed here. A trial Search Analytics client could not authenticate. This cloud agent cannot call the Search Console API.
3. **Property existence (confirmed via GitHub Actions, not this reporter’s own API call)** — this run could not list sites itself. GSC Weekly Sync **scheduled** run `41460495342` on 2 November 2026 at 14:17 UTC authenticated with repo secret `GSC_CREDENTIALS_JSON`, resolved the URL-prefix property `https://www.colddirect.co.uk/`, and wrote a **7-day** performance Step Summary (window **25–31 October 2026** vs **18–24 October 2026**). That is evidence the property exists and is reachable from GitHub Actions. Those weekly figures are **not** 28-day search analytics and are **not** copied into the tables below.
4. **Later sitemap / URL Inspection confirmation** — Nightly auto-seo run `41530435622` on 2 November 2026 at 21:40 UTC (workflow_dispatch, head `afe3d8a`) submitted `https://www.colddirect.co.uk/sitemap.xml` (HTTP 204 at 21:49 UTC) and inspected URLs on the same property. That step is sitemap plus URL Inspection only — **not** 28-day search analytics.
5. **Earlier Daily SEO confirmation** — ColdDirect Daily SEO last listed the same property on 18 October 2026 at 09:19 UTC (scheduled run `39114885014`). That Action used a 7-day window (11–17 October) and is still not a 28-day pull.
6. **Today’s scheduled Daily SEO** — as of 09:03 UTC on 3 November 2026 there is **no** `colddirect-daily-seo.yml` run for 19 October–3 November. On current `main` that workflow is **workflow_dispatch only** (cron disabled) and no longer references `GSC_CREDENTIALS_JSON` or a Search Console query step.

### What was not used

The 2 November weekly Action wrote a 7-day Step Summary (25–31 October vs 18–24 October). Agent-state and later SEO jobs also record other 7-day money-keyword windows. The 18 October Daily SEO Action wrote `seo-audit/daily-report-2026-10-18.md` using a **7-day** window (11–17 October 2026). Those figures are **not** copied here. Older 7-day files under `seo-audit/daily-report-*.md`, older 28-day files under `reports/gsc/`, and CSV logs (including `gsc_report.csv` / `gsc_followup.md`) were also left unused, because they are not a live pull for today’s 28-day windows.

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
- GitHub Actions last reached the property for a **performance** report on 2 November 14:17 UTC (Weekly Sync `41460495342`, 7-day window 25–31 October only). That Step Summary is not copied into the 28-day tables above. The same job submitted the sitemap (HTTP 204) with Search Console showing **138** submitted URLs and **0** indexed (`type: web`, `lastSubmitted` 2026-11-02T14:18:57.540Z, `last downloaded` 2026-11-01T21:48:31.593Z, pending `True`), then failed on a URL Inspection read timeout (`searchconsole.googleapis.com`, 30 seconds). Overall conclusion: failure. The performance report step itself succeeded.
- Nightly auto-seo on 2 November 21:49 UTC (run `41530435622`) recorded a later GSC sitemap PUT (`lastSubmitted` 2026-11-02T21:49:35.476Z, `last downloaded` 2026-11-02T14:19:15.012Z, pending `True`) with **136** submitted URLs and **0** indexed (`type: web`). The same run’s live smoke test counted **138** sitemap URLs. That is a sitemap-API note, not a 28-day search-analytics pull. The same run logged Indexing API calls **25/25** as OK in its table; this reporter did not request indexing.
- URL Inspection from that same 2 November 21:49 UTC step (25 of 60 inspection calls; not 28-day performance): homepage, `/fridge-repair-london/`, `/freezer-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`, `/cold-room-repair-london/`, `/catering-repair-london/`, `/commercial-appliances-repair-london/`, `/air-conditioning-repair-london/`, and `/cellar-cooler-repair-london/` were `PASS` / Submitted and indexed. `/commercial-fridge-repair-enfield/` remains `NEUTRAL` / Not found (404) in Search Console, even though the same nightly smoke test fetched that URL as HTTP 200. New or still-open NEUTRAL in this batch: `/commercial-fridge-repair-central-london/` Discovered - currently not indexed; `/commercial-refrigeration-repair-harlesden/` URL is unknown to Google; `/commercial-refrigeration-repair-tower-hamlets/` and `/commercial-refrigeration-repair-willesden/` Discovered - currently not indexed. Last night’s inspect batch did not include `/adexa-fridge-repair-london/`, `/air-conditioning-repair-north-london/`, `/carpigiani-ice-cream-machine-repair-london/`, `/blast-chiller-repair-north-london/`, `/chiller-repair-north-london/`, or `/freezer-room-repair-london/`. The 13-URL weekly watchlist inspected earlier the same day (Weekly Sync performance report, 14:18 UTC) still showed **0 of 13 PASS**. This reporter did not request indexing.
- Scheduled nightly auto-seo then failed at 3 November 02:24 UTC (run `41565963464`) and 3 November 03:05 UTC (run `41570044382`) on the “already succeeded today” skip path (exit code 1) and skipped the GSC ping. The last successful GSC sitemap/inspect call is the 2 November 21:49 UTC run `41530435622`.
- Live `https://www.colddirect.co.uk/sitemap.xml` fetched for this report (3 November 09:03 UTC) returned HTTP 200, `last-modified: Tue, 03 Nov 2026 04:33:04 GMT`, **136** unique `<loc>` values, and **0** `/_old_site_backup/` URLs. Search Console’s last sitemap-API read (2 November 21:49 UTC) showed **136** submitted / **0** indexed, after the earlier 14:18 UTC weekly ping had shown **138** submitted. This live-file check is not a 28-day Search Console metric.
- No 2 November GSC daily-report pull request was opened. Previous Search Console-unavailable daily PRs through **#113** (1 November) were still unmerged at report time.

## Recommended next actions (no HTML edits in this run)

1. Add Search Console access to this Cursor automation: either a Google Search Console MCP server, or the same `GSC_CREDENTIALS_JSON` secret already used by `.github/workflows/gsc-weekly-sync.yml` and nightly auto-seo.
2. Re-run this reporter once credentials or MCP are attached, then fill last-28 vs previous-28 totals, top 25 tables, country/device splits, movers, and watch lists from live API data.
3. Keep HTML, titles, and marketing copy unchanged until a live 28-day pull exists. Do not request indexing from this report.
4. Separately (process notes, not 28-day analytics): read the 2 November Weekly Sync Step Summary in run `41460495342` for the 7-day window 25–31 October; retry the weekly URL Inspection path that timed out after a successful sitemap PUT; inspect why the scheduled nightly auto-seo fallback still fails after a same-day success; re-check `/commercial-fridge-repair-enfield/` (inspection 404 despite a live HTTP 200), the NEUTRAL district URLs from last night’s 25-URL inspect, and the 13-URL weekly watchlist that still showed 0 PASS; and note that Daily SEO on `main` is still dispatch-only and no longer queries Search Console in YAML. Do not repeat indexing requests from this reporter.

## Short summary

- **Totals:** not available (Search Console MCP and credentials missing in this environment).
- **3 biggest wins:** not available — no live 28-day query or page rows. Process notes only: the URL-prefix property `https://www.colddirect.co.uk/` was reached again on 2 November (Weekly Sync performance report at 14:17 UTC, then nightly sitemap/inspect at 21:49 UTC); URL Inspection still shows the homepage and nine money hubs as PASS / Submitted and indexed; and the live sitemap XML now parses as 136 URLs, matching Search Console’s last submitted count from the 21:49 UTC ping.
- **3 biggest risks:** (1) this daily GSC report cannot run without API access in the Cursor automation, Daily SEO on `main` is still dispatch-only without a GSC query step (no 19 October–3 November Daily SEO run), and yesterday’s 2 November daily report PR was not opened; (2) 28-day movers and high-impression low-CTR queries are unknown until a live pull; (3) Search Console still last showed 0 indexed URLs against 136 submitted, the 2 November Weekly Sync failed after sitemap submit on an inspection timeout, scheduled nightly auto-seo failed after the 21:40 UTC success and skipped GSC, `/commercial-fridge-repair-enfield/` is still an inspection 404 despite a live HTTP 200, the 13-URL weekly watchlist still showed 0 PASS, and watch queries / money pages cannot be monitored here until credentials or MCP are added.
