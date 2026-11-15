# Google Search Console daily report — Cold Direct

- **Date generated:** 14 November 2026 (09:08 UTC)
- **Date range requested:** last 28 days (17 October 2026 – 13 November 2026) vs previous 28 days (19 September 2026 – 16 October 2026). End date = yesterday (13 November 2026).
- **Property:** `https://www.colddirect.co.uk/`
- **Search type:** web
- **Lag:** Search Console data is usually 2–3 days behind, so the latest days in any live pull are often incomplete.

## Status: Search Console tools unavailable in this run

This reporter **did not pull live 28-day analytics**. No totals, query tables, page tables, country/device splits, movers, or CTR-risk lists are shown below, because inventing figures or recycling a different window would be misleading.

### What was checked

1. **Cursor Search Console MCP** — not present in this automation. There is no Google Search Console tool namespace to call `sites.list` or `searchanalytics.query`.
2. **Credentials in this environment** — `GSC_CREDENTIALS_JSON`, `GOOGLE_APPLICATION_CREDENTIALS`, and local key files (`gsc-key.json`, `gsc-oauth.json`, `credentials.json`) are all missing. The `google.oauth2` library is not installed here, so `tools/request_indexing.get_credentials()` cannot run. This cloud agent cannot call the Search Console API.
3. **Property existence (confirmed via GitHub Actions, not this reporter’s own API call)** — this run could not list sites itself. GSC Weekly Sync **scheduled** run `42637642714` on 9 November 2026 at 14:44 UTC (head `46adc91`) authenticated with repo secret `GSC_CREDENTIALS_JSON`, resolved URL-prefix property `https://www.colddirect.co.uk/`, wrote a weekly performance Step Summary, submitted `https://www.colddirect.co.uk/sitemap.xml` (HTTP 204), and inspected URLs. Nightly auto-seo **workflow_dispatch** run `42907266129` on 10 November 2026 at 21:40 UTC (GSC ping 21:50 UTC, head `715c04e`) reached the same property. That is evidence the property exists and is reachable from GitHub Actions.
4. **Performance confirmation is 7-day only** — the 9 November Weekly Sync Step Summary covers **1–7 November 2026** vs **25–31 October 2026**. Those weekly figures are **not** 28-day search analytics and are **not** copied into the tables below. The 2 November Weekly Sync `41460495342` (window 25–31 October vs 18–24 October) is superseded for property/performance confirmation. No newer weekly performance report exists (next scheduled Weekly Sync is Monday 16 November 2026 at 06:00 UTC).
5. **Earlier Daily SEO confirmation** — ColdDirect Daily SEO last listed the same property on 18 October 2026 at 09:19 UTC (scheduled run `39114885014`). That Action used a 7-day window (11–17 October) and is still not a 28-day pull.
6. **Today’s scheduled Daily SEO** — as of 09:08 UTC on 14 November 2026 there is **no** `colddirect-daily-seo.yml` run for 19 October–14 November. On current `main` that workflow is **workflow_dispatch only** (cron disabled) and no longer references `GSC_CREDENTIALS_JSON` or a Search Console query step.

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
- GitHub Actions last reached the property for a **performance** report on 9 November 14:44 UTC (Weekly Sync `42637642714`, 7-day window 1–7 November only). That Step Summary is not copied into the 28-day tables above. Unlike the 2 November weekly job, this run’s overall conclusion was **success** (performance report, sitemap PUT, and URL Inspection all completed).
- Nightly auto-seo on 10 November 21:50 UTC (run `42907266129`, head `715c04e`) remains the last successful GSC sitemap/inspect call (`lastSubmitted` 2026-11-10T21:50:49.861Z, `last downloaded` 2026-11-09T21:49:38.335Z, pending `True`) with **138** submitted URLs and **0** indexed (`type: web`). The same run’s live smoke test counted **138** sitemap URLs. That is a sitemap-API note, not a 28-day search-analytics pull. The same run logged Indexing API calls **11/25** as OK in its table; this reporter did not request indexing.
- URL Inspection from that same 10 November 21:50 UTC step (11 of 60 inspection calls; not 28-day performance): homepage, `/fridge-repair-london/`, `/freezer-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`, `/cold-room-repair-london/`, `/catering-repair-london/`, `/commercial-appliances-repair-london/`, `/air-conditioning-repair-london/`, and `/cellar-cooler-repair-london/` were `PASS` / Submitted and indexed. `/commercial-fridge-repair-enfield/` remains `NEUTRAL` / Not found (404) in Search Console; this reporter’s live fetch of that URL on 14 November 09:08 UTC returned HTTP 200. The 11 November 21:40 UTC nightly (`43105076154`) and the 12 November 21:40 UTC nightly (`43312507239`) both **skipped** the GSC ping after SEO integrity failed, so those inspection statuses were not refreshed. Extra PASS URLs from the 9 November weekly inspect (`42637642714`: `/commercial-catering-repair-london/`, district refrigeration URLs, Foster/Polar/Williams, `/chiller-repair-london/`) and `/display-cabinet-repair-london/` (`NEUTRAL` / Discovered - currently not indexed in that weekly inspect; live HTTP 200 on 14 November 09:08 UTC) were not re-checked. The 13-URL weekly watchlist in the 9 November performance report showed **1 of 13 PASS** (`/cold-room-repair-barnet/`; 12 waiting). This reporter did not request indexing.
- There was **no** 13 November 21:40 UTC nightly auto-seo run. GitHub reports `.github/workflows/auto-seo-nightly.yml` as **disabled_manually** (`updated_at` 13 November 2026 12:33:38 UTC). The last GitHub nightly that reached live auto-seo, smoke, and preflight was `43312507239` on 12 November 21:40 UTC (head `548f884`); it then failed SEO integrity on `/catering-repair-london/`, `/air-conditioning-repair-london/`, `/cellar-cooler-repair-london/`, and watch page `/freezer-repair-london/` (live titles/meta/og differed from the integrity baseline) and **skipped** the GSC ping. That smoke test counted **139** sitemap URLs (`auto-seo.aspx` also reported 139). Live-site alert issue **#135** is still open (last GitHub comment 13 November 02:09 UTC). This is not a 28-day analytics pull.
- Scheduled nightly auto-seo failed at 13 November 01:11 UTC (run `43342935064`) and 13 November 02:09 UTC (run `43350098812`) on the “already succeeded today” skip path (exit code 1) and skipped the GSC ping. Earlier same-path failures after the 10 November success: 12 November 01:55 UTC (`43137821724`); 12 November 02:31 UTC (`43142018827`); 11 November 00:42 UTC (`42933385482`); 11 November 01:29 UTC (`42939263778`). No scheduled fallback ran after the workflow was disabled.
- Live `https://www.colddirect.co.uk/sitemap.xml` fetched for this report (14 November 09:08 UTC) returned HTTP 200, `last-modified: Fri, 13 Nov 2026 11:21:49 GMT`, **137** unique `<loc>` values, and **0** `/_old_site_backup/` URLs. Watch pages present and live HTTP 200: homepage, `/cold-room-repair-london/`, `/fridge-repair-london/`, `/freezer-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`. Search Console’s last sitemap-API read (10 November 21:50 UTC) showed **138** submitted / **0** indexed; the 12 November 21:40 UTC smoke test counted 139. This live-file check is not a 28-day Search Console metric.
- Previous Search Console-unavailable daily PRs through **#136** (13 November) were still unmerged at report time. No 2 November daily-report pull request was opened.

## Recommended next actions (no HTML edits in this run)

1. Add Search Console access to this Cursor automation: either a Google Search Console MCP server, or the same `GSC_CREDENTIALS_JSON` secret already used by `.github/workflows/gsc-weekly-sync.yml` and nightly auto-seo.
2. Re-run this reporter once credentials or MCP are attached, then fill last-28 vs previous-28 totals, top 25 tables, country/device splits, movers, and watch lists from live API data.
3. Keep HTML, titles, and marketing copy unchanged until a live 28-day pull exists. Do not request indexing from this report.
4. Separately (process notes, not 28-day analytics): re-enable the Nightly auto-seo GitHub workflow (currently disabled_manually, so no GSC ping can run from Actions); restore SEO integrity on the four drifted hubs (`/freezer-repair-london/`, `/catering-repair-london/`, `/air-conditioning-repair-london/`, `/cellar-cooler-repair-london/`) so the next nightly can reach the GSC ping and close live-site alert **#135**; inspect why the scheduled nightly skip-path still fails after a same-day dispatch; read the 9 November Weekly Sync Step Summary in run `42637642714` for the 7-day window 1–7 November (next weekly job is Monday 16 November); re-check `/commercial-fridge-repair-enfield/` (inspection 404 despite a live HTTP 200), `/display-cabinet-repair-london/` (Discovered - currently not indexed on 9 November weekly inspect; live HTTP 200), the remaining 12 URLs on the weekly watchlist, and note that Daily SEO on `main` is still dispatch-only and no longer queries Search Console in YAML. Do not repeat indexing requests from this reporter.

## Short summary

- **Totals:** not available (Search Console MCP and credentials missing in this environment).
- **3 biggest wins:** not available — no live 28-day query or page rows. Process notes only: the URL-prefix property `https://www.colddirect.co.uk/` was last reached for sitemap/inspect on 10 November (nightly `42907266129` at 21:50 UTC) and for a 7-day performance report on 9 November (Weekly Sync `42637642714` at 14:44 UTC); URL Inspection still last showed the homepage and nine money hubs as PASS / Submitted and indexed; and the weekly 13-URL watchlist remains at 1 PASS (`/cold-room-repair-barnet/`).
- **3 biggest risks:** (1) this daily GSC report cannot run without API access in the Cursor automation, Daily SEO on `main` is still dispatch-only without a GSC query step (no 19 October–14 November Daily SEO run), the Nightly auto-seo workflow is **disabled_manually** so there was no 13 November 21:40 UTC GSC ping, and the 2 November daily report PR was not opened; (2) 28-day movers and high-impression low-CTR queries are unknown until a live pull; (3) Search Console still last showed 0 indexed URLs against 138 submitted, the live sitemap XML now parses as 137 URLs (`last-modified` 13 November 11:21:49 GMT), the last GitHub nightly that ran skipped GSC after integrity failed on four hubs including watch page `/freezer-repair-london/` (alert **#135** still open), `/commercial-fridge-repair-enfield/` is still an inspection 404 despite a live HTTP 200, `/display-cabinet-repair-london/` remains Discovered - currently not indexed, 12 of 13 weekly-watchlist URLs are still waiting, and watch queries / money pages cannot be monitored here until credentials or MCP are added.
