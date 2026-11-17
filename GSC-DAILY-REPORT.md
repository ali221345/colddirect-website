# Google Search Console daily report — Cold Direct

- **Date generated:** 16 November 2026 (09:04 UTC)
- **Date range requested:** last 28 days (19 October 2026 – 15 November 2026) vs previous 28 days (21 September 2026 – 18 October 2026). End date = yesterday (15 November 2026).
- **Property:** `https://www.colddirect.co.uk/`
- **Search type:** web
- **Lag:** Search Console data is usually 2–3 days behind, so the latest days in any live pull are often incomplete.

## Status: Search Console tools unavailable in this run

This reporter **did not pull live 28-day analytics**. No totals, query tables, page tables, country/device splits, movers, or CTR-risk lists are shown below, because inventing figures or recycling a different window would be misleading.

### What was checked

1. **Cursor Search Console MCP** — not present in this automation. There is no Google Search Console tool namespace to call `sites.list` or `searchanalytics.query`.
2. **Credentials in this environment** — `GSC_CREDENTIALS_JSON`, `GOOGLE_APPLICATION_CREDENTIALS`, and local key files (`gsc-key.json`, `gsc-oauth.json`, `credentials.json`) are all missing. `google-auth` / `googleapiclient` are not installed here either. This cloud agent cannot authenticate to the Search Console API.
3. **Property existence (confirmed via GitHub Actions, not this reporter’s own API call)** — this run could not list sites itself. GSC Weekly Sync **scheduled** run `42637642714` on 9 November 2026 at 14:44 UTC (head `46adc91`) authenticated with repo secret `GSC_CREDENTIALS_JSON`, resolved URL-prefix property `https://www.colddirect.co.uk/`, wrote a weekly performance Step Summary, submitted `https://www.colddirect.co.uk/sitemap.xml` (HTTP 204), and inspected URLs. Nightly auto-seo **workflow_dispatch** run `42907266129` on 10 November 2026 at 21:40 UTC (GSC ping 21:50 UTC, head `715c04e`) reached the same property. That is evidence the property exists and is reachable from GitHub Actions.
4. **Performance confirmation is 7-day only** — the 9 November Weekly Sync Step Summary covers **1–7 November 2026** vs **25–31 October 2026**. Those weekly figures are **not** 28-day search analytics and are **not** copied into the tables below. The 2 November Weekly Sync `41460495342` (window 25–31 October vs 18–24 October) is superseded for property/performance confirmation.
5. **Today’s scheduled Weekly Sync did not run** — `.github/workflows/gsc-weekly-sync.yml` is still **active** (`cron: 0 6 * * 1`). As of 09:04 UTC on Monday 16 November 2026 there is **no** 16 November run (queued, in progress, or completed). The newest Weekly Sync remains `42637642714` on 9 November. GitHub scheduled workflows can delay, but this job is about three hours past 06:00 UTC with no run recorded.
6. **Earlier Daily SEO confirmation** — ColdDirect Daily SEO last listed the same property on 18 October 2026 at 09:19 UTC (scheduled run `39114885014`). That Action used a 7-day window (11–17 October) and is still not a 28-day pull.
7. **Today’s scheduled Daily SEO** — as of 09:04 UTC on 16 November 2026 there is **no** `colddirect-daily-seo.yml` run for 19 October–16 November. On current `main` that workflow is **workflow_dispatch only** (cron disabled) and no longer references `GSC_CREDENTIALS_JSON` or a Search Console query step.

### What was not used

The 9 November weekly Action wrote a 7-day Step Summary (1–7 November vs 25–31 October). Agent-state and later SEO jobs also record other 7-day money-keyword windows. The 18 October Daily SEO Action wrote `seo-audit/daily-report-2026-10-18.md` using a **7-day** window (11–17 October 2026). Those figures are **not** copied here. Older 7-day files under `seo-audit/daily-report-*.md`, older 28-day files under `reports/gsc/`, and CSV logs (including `gsc_report.csv` / `gsc_followup.md`) were also left unused, because they are not a live pull for today’s 28-day windows.

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
- GitHub Actions last reached the property for a **performance** report on 9 November 14:44 UTC (Weekly Sync `42637642714`, 7-day window 1–7 November only). That Step Summary is not copied into the 28-day tables above. Unlike the 2 November weekly job, this run’s overall conclusion was **success** (performance report, sitemap PUT, and URL Inspection all completed). The Monday 16 November 06:00 UTC Weekly Sync had **not** started by 09:04 UTC.
- Nightly auto-seo on 10 November 21:50 UTC (run `42907266129`, head `715c04e`) remains the last successful GSC sitemap/inspect call (`lastSubmitted` 2026-11-10T21:50:49.861Z, `last downloaded` 2026-11-09T21:49:38.335Z, pending `True`) with **138** submitted URLs and **0** indexed (`type: web`). The same run’s live smoke test counted **138** sitemap URLs. That is a sitemap-API note, not a 28-day search-analytics pull. The same run logged Indexing API calls **11/25** as OK in its table; this reporter did not request indexing.
- URL Inspection from that same 10 November 21:50 UTC step (11 of 60 inspection calls; not 28-day performance): homepage, `/fridge-repair-london/`, `/freezer-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`, `/cold-room-repair-london/`, `/catering-repair-london/`, `/commercial-appliances-repair-london/`, `/air-conditioning-repair-london/`, and `/cellar-cooler-repair-london/` were `PASS` / Submitted and indexed. `/commercial-fridge-repair-enfield/` remains `NEUTRAL` / Not found (404) in Search Console; this reporter’s live fetch of that URL on 16 November 09:04 UTC returned HTTP 200. The 11 November 21:40 UTC nightly (`43105076154`) and the 12 November 21:40 UTC nightly (`43312507239`) both **skipped** the GSC ping after SEO integrity failed, so those inspection statuses were not refreshed. Extra PASS URLs from the 9 November weekly inspect (`42637642714`: `/commercial-catering-repair-london/`, district refrigeration URLs, Foster/Polar/Williams, `/chiller-repair-london/`) and `/display-cabinet-repair-london/` (`NEUTRAL` / Discovered - currently not indexed in that weekly inspect; live HTTP 200 on 16 November 09:04 UTC) were not re-checked. The 13-URL weekly watchlist in the 9 November performance report showed **1 of 13 PASS** (`/cold-room-repair-barnet/`; 12 waiting). This reporter did not request indexing.
- There was **no** 13, 14, 15, or 16 November 21:40 UTC nightly auto-seo run (16 November 21:40 UTC has not arrived yet). GitHub reports `.github/workflows/auto-seo-nightly.yml` as **disabled_manually** (`updated_at` 13 November 2026 12:33:38 UTC). The last GitHub nightly that reached live auto-seo, smoke, and preflight was `43312507239` on 12 November 21:40 UTC (head `548f884`); it then failed SEO integrity on `/catering-repair-london/`, `/air-conditioning-repair-london/`, `/cellar-cooler-repair-london/`, and watch page `/freezer-repair-london/` (live titles/meta/og differed from the integrity baseline) and **skipped** the GSC ping. That smoke test counted **139** sitemap URLs (`auto-seo.aspx` also reported 139).
- Live-site alert issue **#135** is still **closed** (closed at 14 November 2026 11:55:48 UTC after Deploy to WHUK Plesk run `43592005480`). Later successful Plesk deploys on 14 November include `43643032040` (21:28 UTC) and `43652052328` (23:12 UTC). Those deploy workflows are **not** Search Console sitemap/inspect pings, so the last GSC API confirmation remains the 10 November nightly.
- Scheduled nightly auto-seo failed at 13 November 01:11 UTC (run `43342935064`) and 13 November 02:09 UTC (run `43350098812`) on the “already succeeded today” skip path (exit code 1) and skipped the GSC ping. No scheduled fallback ran after the workflow was disabled.
- Live `https://www.colddirect.co.uk/sitemap.xml` fetched for this report (16 November 09:04 UTC) returned HTTP 200, `last-modified: Sun, 15 Nov 2026 11:18:30 GMT`, **137** unique `<loc>` values, and **0** `/_old_site_backup/` URLs. Watch pages present and live HTTP 200: homepage, `/cold-room-repair-london/`, `/fridge-repair-london/`, `/freezer-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`. Search Console’s last sitemap-API read (10 November 21:50 UTC) showed **138** submitted / **0** indexed; the 12 November 21:40 UTC smoke test counted 139. This live-file check is not a 28-day Search Console metric.
- Previous Search Console-unavailable daily PRs through **#139** (15 November) were still unmerged at report time. No 2 November daily-report pull request was opened.

## Recommended next actions (no HTML edits in this run)

1. Add Search Console access to this Cursor automation: either a Google Search Console MCP server, or the same `GSC_CREDENTIALS_JSON` secret already used by `.github/workflows/gsc-weekly-sync.yml` and nightly auto-seo.
2. Re-run this reporter once credentials or MCP are attached, then fill last-28 vs previous-28 totals, top 25 tables, country/device splits, movers, and watch lists from live API data.
3. Keep HTML, titles, and marketing copy unchanged until a live 28-day pull exists. Do not request indexing from this report.
4. Separately (process notes, not 28-day analytics): check why today’s Weekly Sync (Monday 06:00 UTC) had not started by 09:04 UTC, then re-enable the Nightly auto-seo GitHub workflow (currently disabled_manually, so no GSC ping can run from Actions); the four drifted hubs from the 12 November integrity failure appear to have been recovered enough for later Plesk deploys to keep alert **#135** closed, but that is not a GSC ping — the next nightly still needs to reach sitemap/inspect; read the 9 November Weekly Sync Step Summary in run `42637642714` for the 7-day window 1–7 November; re-check `/commercial-fridge-repair-enfield/` (inspection 404 despite a live HTTP 200), `/display-cabinet-repair-london/` (Discovered - currently not indexed on 9 November weekly inspect; live HTTP 200), the remaining 12 URLs on the weekly watchlist, and note that Daily SEO on `main` is still dispatch-only and no longer queries Search Console in YAML. Do not repeat indexing requests from this reporter.

## Short summary

- **Totals:** not available (Search Console MCP and credentials missing in this environment).
- **3 biggest wins:** not available — no live 28-day query or page rows. Process notes only: the URL-prefix property `https://www.colddirect.co.uk/` was last reached for sitemap/inspect on 10 November (nightly `42907266129` at 21:50 UTC) and for a 7-day performance report on 9 November (Weekly Sync `42637642714` at 14:44 UTC); URL Inspection still last showed the homepage and nine money hubs as PASS / Submitted and indexed; live-site alert **#135** remains closed after later 14 November Plesk deploys; and the weekly 13-URL watchlist remains at 1 PASS (`/cold-room-repair-barnet/`).
- **3 biggest risks:** (1) this daily GSC report cannot run without API access in the Cursor automation, Daily SEO on `main` is still dispatch-only without a GSC query step (no 19 October–16 November Daily SEO run), the Nightly auto-seo workflow is **disabled_manually** so there was no 13–16 November 21:40 UTC GSC ping, today’s Monday Weekly Sync had not started by 09:04 UTC, and the 2 November daily report PR was not opened; (2) 28-day movers and high-impression low-CTR queries are unknown until a live pull; (3) Search Console still last showed 0 indexed URLs against 138 submitted, the live sitemap XML now parses as 137 URLs (`last-modified` 15 November 11:18:30 GMT), `/commercial-fridge-repair-enfield/` is still an inspection 404 despite a live HTTP 200, `/display-cabinet-repair-london/` remains Discovered - currently not indexed, 12 of 13 weekly-watchlist URLs are still waiting, and watch queries / money pages cannot be monitored here until credentials or MCP are added.
