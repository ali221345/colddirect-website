# Google Search Console daily report — Cold Direct

- **Date generated:** 8 November 2026 (09:03 UTC)
- **Date range requested:** last 28 days (11 October 2026 – 7 November 2026) vs previous 28 days (13 September 2026 – 10 October 2026). End date = yesterday (7 November 2026).
- **Property:** `https://www.colddirect.co.uk/`
- **Search type:** web
- **Lag:** Search Console data is usually 2–3 days behind, so the latest days in any live pull are often incomplete.

## Status: Search Console tools unavailable in this run

This reporter **did not pull live 28-day analytics**. No totals, query tables, page tables, country/device splits, movers, or CTR-risk lists are shown below, because inventing figures or recycling a different window would be misleading.

### What was checked

1. **Cursor Search Console MCP** — not present in this automation. There is no Google Search Console tool namespace to call `sites.list` or `searchanalytics.query`.
2. **Credentials in this environment** — `GSC_CREDENTIALS_JSON`, `GOOGLE_APPLICATION_CREDENTIALS`, and local key files (`gsc-key.json`, `gsc-oauth.json`, `credentials.json`) are all missing. The `google` / `google.auth` and `googleapiclient` libraries are not installed here. A trial Search Analytics client could not authenticate. This cloud agent cannot call the Search Console API.
3. **Property existence (confirmed via GitHub Actions, not this reporter’s own API call)** — this run could not list sites itself. Nightly auto-seo **workflow_dispatch** run `42416941194` on 7 November 2026 at 21:40 UTC (GSC ping 21:50 UTC, head `6084a2b`) authenticated with repo secret `GSC_CREDENTIALS_JSON`, submitted `https://www.colddirect.co.uk/sitemap.xml` (HTTP 204 at 21:50 UTC), and inspected URLs on the URL-prefix property `https://www.colddirect.co.uk/`. That is evidence the property exists and is reachable from GitHub Actions. That step is sitemap plus URL Inspection only — **not** 28-day search analytics.
4. **Earlier performance confirmation** — GSC Weekly Sync **scheduled** run `41460495342` on 2 November 2026 at 14:17 UTC resolved the same property and wrote a **7-day** performance Step Summary (window **25–31 October 2026** vs **18–24 October 2026**). Those weekly figures are **not** 28-day search analytics and are **not** copied into the tables below.
5. **Earlier Daily SEO confirmation** — ColdDirect Daily SEO last listed the same property on 18 October 2026 at 09:19 UTC (scheduled run `39114885014`). That Action used a 7-day window (11–17 October) and is still not a 28-day pull.
6. **Today’s scheduled Daily SEO** — as of 09:03 UTC on 8 November 2026 there is **no** `colddirect-daily-seo.yml` run for 19 October–8 November. On current `main` that workflow is **workflow_dispatch only** (cron disabled) and no longer references `GSC_CREDENTIALS_JSON` or a Search Console query step.

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
- GitHub Actions last reached the property for a **performance** report on 2 November 14:17 UTC (Weekly Sync `41460495342`, 7-day window 25–31 October only). That Step Summary is not copied into the 28-day tables above. The same weekly job later failed on a URL Inspection read timeout after a successful sitemap PUT. Overall conclusion: failure. The performance report step itself succeeded.
- Nightly auto-seo on 7 November 21:50 UTC (run `42416941194`, head `6084a2b`) recorded a later GSC sitemap PUT (`lastSubmitted` 2026-11-07T21:50:51.917Z, `last downloaded` 2026-11-06T21:50:48.920Z, pending `True`) with **138** submitted URLs and **0** indexed (`type: web`). The same run’s live smoke test counted **138** sitemap URLs. That is a sitemap-API note, not a 28-day search-analytics pull. The same run logged Indexing API calls **21/25** as OK in its table; this reporter did not request indexing.
- URL Inspection from that same 7 November 21:50 UTC step (21 of 60 inspection calls; not 28-day performance): homepage, `/fridge-repair-london/`, `/freezer-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`, `/cold-room-repair-london/`, `/catering-repair-london/`, `/commercial-appliances-repair-london/`, `/air-conditioning-repair-london/`, and `/cellar-cooler-repair-london/` were `PASS` / Submitted and indexed. `/commercial-fridge-repair-enfield/` remains `NEUTRAL` / Not found (404) in Search Console; this reporter’s live fetch of that URL on 8 November 09:04 UTC returned HTTP 200. Also `PASS` / Submitted and indexed in this batch: `/commercial-catering-repair-london/`, `/commercial-refrigeration-repair-canary-wharf/`, `/commercial-refrigeration-repair-mayfair/`, `/commercial-refrigeration-repair-park-royal/`, `/commercial-refrigeration-repair-shoreditch/`, `/commercial-refrigeration-repair-soho/`, `/foster-fridge-repair-london/`, `/polar-fridge-repair-london/`, `/williams-freezer-repair-london/`, and `/williams-fridge-repair-london/`. Last night’s inspect batch did not include `/chiller-repair-london/` (PASS on 5 November) or `/display-cabinet-repair-london/` (NEUTRAL / Discovered - currently not indexed on 5 November; live HTTP 200 on 8 November 09:04 UTC). It also did not include `/adexa-fridge-repair-london/`, `/air-conditioning-repair-north-london/`, `/carpigiani-ice-cream-machine-repair-london/`, `/blast-chiller-repair-north-london/`, `/chiller-repair-north-london/`, `/freezer-room-repair-london/`, `/commercial-fridge-repair-central-london/`, `/commercial-refrigeration-repair-harlesden/`, `/commercial-refrigeration-repair-tower-hamlets/`, or `/commercial-refrigeration-repair-willesden/`. The 13-URL weekly watchlist last inspected on 2 November (Weekly Sync performance report, 14:18 UTC) still showed **0 of 13 PASS**. This reporter did not request indexing.
- Scheduled nightly auto-seo then failed at 7 November 23:40 UTC (run `42426270083`) and 8 November 00:55 UTC (run `42431984395`) on the “already succeeded today” skip path (exit code 1) and skipped the GSC ping. The last successful GSC sitemap/inspect call is the 7 November 21:50 UTC run `42416941194`.
- Live `https://www.colddirect.co.uk/sitemap.xml` fetched for this report (8 November 09:04 UTC) returned HTTP 200, `last-modified: Sat, 07 Nov 2026 21:53:54 GMT`, **136** unique `<loc>` values, and **0** `/_old_site_backup/` URLs. Search Console’s last sitemap-API read (7 November 21:50 UTC) showed **138** submitted / **0** indexed, matching that run’s smoke-test count of 138. The live file’s last-modified is just after that GSC PUT (21:50:51 UTC). This live-file check is not a 28-day Search Console metric.
- Previous Search Console-unavailable daily PRs through **#124** (7 November) were still unmerged at report time. No 2 November daily-report pull request was opened.

## Recommended next actions (no HTML edits in this run)

1. Add Search Console access to this Cursor automation: either a Google Search Console MCP server, or the same `GSC_CREDENTIALS_JSON` secret already used by `.github/workflows/gsc-weekly-sync.yml` and nightly auto-seo.
2. Re-run this reporter once credentials or MCP are attached, then fill last-28 vs previous-28 totals, top 25 tables, country/device splits, movers, and watch lists from live API data.
3. Keep HTML, titles, and marketing copy unchanged until a live 28-day pull exists. Do not request indexing from this report.
4. Separately (process notes, not 28-day analytics): read the 2 November Weekly Sync Step Summary in run `41460495342` for the 7-day window 25–31 October; retry the weekly URL Inspection path that timed out after a successful sitemap PUT; inspect why the scheduled nightly auto-seo fallback still fails after a same-day success; re-check `/commercial-fridge-repair-enfield/` (inspection 404 despite a live HTTP 200), `/display-cabinet-repair-london/` (last known Discovered - currently not indexed on 5 November; not in last night’s 21-URL inspect), the district URLs not in last night’s inspect, and the 13-URL weekly watchlist that still showed 0 PASS on 2 November; and note that Daily SEO on `main` is still dispatch-only and no longer queries Search Console in YAML. Do not repeat indexing requests from this reporter.

## Short summary

- **Totals:** not available (Search Console MCP and credentials missing in this environment).
- **3 biggest wins:** not available — no live 28-day query or page rows. Process notes only: the URL-prefix property `https://www.colddirect.co.uk/` was reached again on 7 November 21:50 UTC (nightly sitemap/inspect `42416941194`); URL Inspection still shows the homepage and nine money hubs as PASS / Submitted and indexed; and ten recently modified service/brand pages in last night’s 21-URL inspect were also PASS / Submitted and indexed.
- **3 biggest risks:** (1) this daily GSC report cannot run without API access in the Cursor automation, Daily SEO on `main` is still dispatch-only without a GSC query step (no 19 October–8 November Daily SEO run), and the 2 November daily report PR was not opened; (2) 28-day movers and high-impression low-CTR queries are unknown until a live pull; (3) Search Console still last showed 0 indexed URLs against 138 submitted, the live sitemap XML now parses as 136 URLs, scheduled nightly auto-seo failed after the 21:40 UTC success and skipped GSC, `/commercial-fridge-repair-enfield/` is still an inspection 404 despite a live HTTP 200, `/display-cabinet-repair-london/` was not re-inspected last night (last known Discovered - currently not indexed on 5 November), the 13-URL weekly watchlist still showed 0 PASS on 2 November, and watch queries / money pages cannot be monitored here until credentials or MCP are added.
