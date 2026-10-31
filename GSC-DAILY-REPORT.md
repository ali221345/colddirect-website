# Google Search Console daily report — Cold Direct

- **Date generated:** 31 October 2026 (09:06 UTC)
- **Date range requested:** last 28 days (3 October 2026 – 30 October 2026) vs previous 28 days (5 September 2026 – 2 October 2026). End date = yesterday (30 October 2026).
- **Property:** `https://www.colddirect.co.uk/`
- **Search type:** web
- **Lag:** Search Console data is usually 2–3 days behind, so the latest days in any live pull are often incomplete.

## Status: Search Console tools unavailable in this run

This reporter **did not pull live 28-day analytics**. No totals, query tables, page tables, country/device splits, movers, or CTR-risk lists are shown below, because inventing figures or recycling a different window would be misleading.

### What was checked

1. **Cursor Search Console MCP** — not present in this automation. There is no Google Search Console tool namespace to call `sites.list` or `searchanalytics.query`.
2. **Credentials in this environment** — `GSC_CREDENTIALS_JSON`, `GOOGLE_APPLICATION_CREDENTIALS`, and local key files (`gsc-key.json`, `gsc-oauth.json`, `credentials.json`) are all missing. The `google` / `google.auth` and `googleapiclient` libraries are not installed here. A trial Search Analytics client could not authenticate. This cloud agent cannot call the Search Console API.
3. **Property existence (confirmed via GitHub Actions, not this reporter’s own API call)** — this run could not list sites itself. GSC Weekly Sync **scheduled** run `40318782178` on 26 October 2026 at 11:56 UTC authenticated with repo secret `GSC_CREDENTIALS_JSON`, resolved the URL-prefix property `https://www.colddirect.co.uk/`, and wrote a **7-day** performance Step Summary (window 18–24 October vs 11–17 October). That is evidence the property exists and is reachable from GitHub Actions. Those weekly figures are **not** 28-day search analytics and are **not** copied into the tables below. There is still no newer Weekly Sync run as of 09:06 UTC on 31 October.
4. **Later sitemap / URL Inspection confirmation** — Nightly auto-seo run `41132725477` on 30 October 2026 at 21:40 UTC (workflow_dispatch, head `ece0270`) submitted `https://www.colddirect.co.uk/sitemap.xml` (HTTP 204 at 21:49 UTC) and inspected URLs on the same property. That step is sitemap plus URL Inspection only — **not** 28-day search analytics.
5. **Earlier Daily SEO confirmation** — ColdDirect Daily SEO last listed the same property on 18 October 2026 at 09:19 UTC (scheduled run `39114885014`). That Action used a 7-day window (11–17 October) and is still not a 28-day pull.
6. **Today’s scheduled Daily SEO** — as of 09:06 UTC on 31 October 2026 there is **no** `colddirect-daily-seo.yml` run for 19–31 October. On current `main` that workflow is **workflow_dispatch only** (cron disabled) and no longer references `GSC_CREDENTIALS_JSON` or a Search Console query step.

### What was not used

The 26 October weekly Action wrote a 7-day Step Summary (18–24 October vs 11–17 October). Agent-state and later SEO jobs also record a 7-day money-keyword window of 19–25 October. The 18 October Daily SEO Action wrote `seo-audit/daily-report-2026-10-18.md` using a **7-day** window (11–17 October 2026). Those figures are **not** copied here. Older 7-day files under `seo-audit/daily-report-*.md`, older 28-day files under `reports/gsc/`, and CSV logs (including `gsc_report.csv` / `gsc_followup.md`) were also left unused, because they are not a live pull for today’s 28-day windows.

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
- GitHub Actions last reached the property for a **performance** report on 26 October 11:56 UTC (Weekly Sync `40318782178`, 7-day window 18–24 October only). That Step Summary is not copied into the 28-day tables above.
- Nightly auto-seo on 30 October 21:49 UTC (run `41132725477`) recorded a GSC sitemap PUT (`lastSubmitted` 2026-10-30T21:49:09.483Z, `last downloaded` 2026-10-29T21:49:28.091Z, pending `True`) with **133** submitted URLs and **0** indexed (`type: web`). The same run’s live smoke test counted **133** sitemap URLs. That is a sitemap-API note, not a 28-day search-analytics pull. The same run logged Indexing API calls **11/11** as OK in its table; this reporter did not request indexing.
- URL Inspection from that same 30 October 21:50 UTC step (11 of 60 inspection calls; not 28-day performance): homepage, `/fridge-repair-london/`, `/freezer-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`, `/cold-room-repair-london/`, `/catering-repair-london/`, `/commercial-appliances-repair-london/`, `/air-conditioning-repair-london/`, and `/cellar-cooler-repair-london/` were `PASS` / Submitted and indexed. `/commercial-fridge-repair-enfield/` remains `NEUTRAL` / Not found (404) in Search Console, even though the same nightly smoke test fetched that URL as HTTP 200. Last night’s inspect batch did not include `/adexa-fridge-repair-london/`, `/air-conditioning-repair-north-london/`, `/carpigiani-ice-cream-machine-repair-london/`, `/blast-chiller-repair-north-london/`, `/chiller-repair-north-london/`, or `/freezer-room-repair-london/`. The last broader inspect was nightly run `40959713069` on 29 October 21:52 UTC (25 of 60 calls). This reporter did not request indexing.
- Scheduled nightly auto-seo then failed at 30 October 23:53 UTC (run `41147056274`) and 31 October 01:04 UTC (run `41153557248`) on the “already succeeded today” skip path (exit code 1) and skipped the GSC ping. The last successful GSC sitemap/inspect call is the 30 October 21:49 UTC run `41132725477`.
- Live `https://www.colddirect.co.uk/sitemap.xml` fetched for this report (31 October 09:05 UTC) returned HTTP 200, `last-modified: Sat, 31 Oct 2026 01:24:25 GMT`, **131** unique `<loc>` values, and **0** `/_old_site_backup/` URLs. Repository root `sitemap.xml` and mirror `colddirect-public-html/sitemap.xml` also have **131** unique URLs (the mirror was 122 on 30 October). Search Console’s last sitemap-API read showed **133** submitted / **0** indexed, and the 21:42 UTC smoke test on the same nightly run counted **133**. This live-file check is not a 28-day Search Console metric.

## Recommended next actions (no HTML edits in this run)

1. Add Search Console access to this Cursor automation: either a Google Search Console MCP server, or the same `GSC_CREDENTIALS_JSON` secret already used by `.github/workflows/gsc-weekly-sync.yml` and nightly auto-seo.
2. Re-run this reporter once credentials or MCP are attached, then fill last-28 vs previous-28 totals, top 25 tables, country/device splits, movers, and watch lists from live API data.
3. Keep HTML, titles, and marketing copy unchanged until a live 28-day pull exists. Do not request indexing from this report.
4. Separately: live sitemap XML still parses as 131 public URLs while Search Console last reported 133 submitted / 0 indexed and nightly smoke said 133 at 21:42 UTC; confirm Google has recrawled the pending sitemap; note that Daily SEO on `main` is still dispatch-only and no longer queries Search Console in YAML; inspect why the scheduled nightly auto-seo fallback still fails after a same-day success; and re-check `fridge repair london`, `commercial fridge repair london`, `/commercial-fridge-repair-enfield/` (inspection 404 despite a live HTTP 200), and `/freezer-room-repair-london/` (not in last night’s 11-URL inspect batch), on a proper 28-day window. Do not repeat indexing requests from this reporter.

## Short summary

- **Totals:** not available (Search Console MCP and credentials missing in this environment).
- **3 biggest wins:** not available — no live 28-day query or page rows. Process notes only: the URL-prefix property `https://www.colddirect.co.uk/` was reached again on 30 October (nightly sitemap/inspect at 21:49 UTC, after the 26 October Weekly Sync performance report); Search Console’s sitemap API still shows 133 submitted URLs; URL Inspection still shows the homepage and nine money hubs as PASS / Submitted and indexed, and the public-html sitemap mirror is now 131 URLs in line with the root file.
- **3 biggest risks:** (1) this daily GSC report cannot run without API access in the Cursor automation, and Daily SEO on `main` is still dispatch-only without a GSC query step (no 19–31 October Daily SEO run); (2) 28-day movers and high-impression low-CTR queries are unknown until a live pull; (3) Search Console still last showed 0 indexed URLs against 133 submitted while the live sitemap XML parses as 131, scheduled nightly auto-seo failed after the 30 October 21:40 UTC success and skipped GSC, `/commercial-fridge-repair-enfield/` is still an inspection 404 despite a live HTTP 200, and watch queries / money pages cannot be monitored here until credentials or MCP are added.
