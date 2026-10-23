# Google Search Console daily report — Cold Direct

- **Date generated:** 23 October 2026 (09:03 UTC)
- **Date range requested:** last 28 days (25 September 2026 – 22 October 2026) vs previous 28 days (28 August 2026 – 24 September 2026). End date = yesterday (22 October 2026).
- **Property:** `https://www.colddirect.co.uk/`
- **Search type:** web
- **Lag:** Search Console data is usually 2–3 days behind, so the latest days in any live pull are often incomplete.

## Status: Search Console tools unavailable in this run

This reporter **did not pull live 28-day analytics**. No totals, query tables, page tables, country/device splits, movers, or CTR-risk lists are shown below, because inventing figures or recycling a different window would be misleading.

### What was checked

1. **Cursor Search Console MCP** — not present in this automation. There is no Google Search Console tool namespace to call `sites.list` or `searchanalytics.query`.
2. **Credentials in this environment** — `GSC_CREDENTIALS_JSON`, `GOOGLE_APPLICATION_CREDENTIALS`, and local key files (`gsc-key.json`, `gsc-oauth.json`, `credentials.json`) are all missing. `google.auth` and `googleapiclient` are not installed here. A trial `searchanalytics.query` client could not authenticate. This cloud agent cannot call the Search Console API.
3. **Property existence (confirmed via GitHub Actions, not this reporter’s own API call)** — this run could not list sites itself. Nightly auto-seo **workflow_dispatch** run `39850829998` on 22 October 2026 at 20:40 UTC authenticated with repo secret `GSC_CREDENTIALS_JSON`, submitted `https://www.colddirect.co.uk/sitemap.xml` (HTTP 204), and inspected URLs on the URL-prefix property `https://www.colddirect.co.uk/`. That is evidence the property exists and is reachable from GitHub Actions. Those results are sitemap and URL Inspection only — **not** 28-day search analytics. They are not copied into the tables below.
4. **Earlier performance-report confirmation** — GSC Weekly Sync last wrote a performance Step Summary on 20 October 2026 at 23:03 UTC (`workflow_dispatch` run `39512458941`, head `469e986`). That weekly script resolves the same verified URL-prefix property before querying web search analytics. Those weekly figures are a **7-day** window and are **not** copied here. No newer Weekly Sync run exists as of 23 October 09:03 UTC.
5. **Earlier Daily SEO confirmation** — ColdDirect Daily SEO last listed the same property on 18 October 2026 at 09:19 UTC (scheduled run `39114885014`, head `0dae4e8`) with service account `github-seo-bot@colddirect-live.iam.gserviceaccount.com`, site URL `https://www.colddirect.co.uk/`, 7-day window 11–17 October 2026. That is still not a 28-day pull.
6. **Today’s scheduled Daily SEO** — as of 09:03 UTC on 23 October 2026 there is **no** `colddirect-daily-seo.yml` run for 19–23 October. On current `main` that workflow is **workflow_dispatch only** (cron disabled) and no longer references `GSC_CREDENTIALS_JSON` or a Search Console query step.

### What was not used

The 20 October weekly Action wrote a 7-day Step Summary. The 18 October Daily SEO Action wrote `seo-audit/daily-report-2026-10-18.md` using a **7-day** window (11–17 October 2026). Those figures are **not** copied here. Older 7-day files under `seo-audit/daily-report-*.md`, older 28-day files under `reports/gsc/`, and CSV logs (including `gsc_report.csv` / `gsc_followup.md`) were also left unused, because they are not a live pull for today’s 28-day windows.

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
- GitHub Actions last reached the property for a **performance** report on 20 October (weekly 7-day report only). The newer 22 October auto-seo GSC step was sitemap submit plus URL Inspection only, so movers and risks for the required 28-day vs previous-28 windows stay unknown.
- Nightly auto-seo on 22 October 20:48 UTC (dispatch run `39850829998`) recorded a GSC sitemap PUT (`lastSubmitted` 2026-10-22T20:48:07Z, pending `True`) with **122** submitted URLs and **0** indexed (`type: web`). That is a sitemap-API note, not a 28-day search-analytics pull. Indexing API remains 403 for the CI service account.
- URL Inspection from that same 22 October 20:51 UTC step (not 28-day performance): homepage, `/fridge-repair-london/`, `/freezer-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`, `/cold-room-repair-london/`, and `/commercial-appliances-repair-london/` were `PASS` / Submitted and indexed. `/commercial-appliances-repair-london/` had been `NEUTRAL` / Discovered - currently not indexed on 18 October Daily SEO; that inspection change is not a 28-day click or position mover. `/commercial-fridge-repair-enfield/` was `NEUTRAL` / Not found (404). `/freezer-room-repair-london/` was not in this 25-URL inspection batch. This reporter did not request indexing.
- Scheduled nightly auto-seo then failed at 22 October 23:27 UTC (run `39871836194`) and 23 October 00:10 UTC (run `39876538152`); those jobs skipped the GSC ping. The last successful GSC sitemap/inspect call remains the 22 October 20:48 UTC dispatch.
- Live `https://www.colddirect.co.uk/sitemap.xml` fetched for this report (23 October 09:03 UTC) returned HTTP 200, `last-modified: Fri, 23 Oct 2026 08:35:40 GMT`, **122** unique `<loc>` values, and **0** `/_old_site_backup/` URLs. Repository `sitemap.xml` and `colddirect-public-html/sitemap.xml` also have **122** unique URLs and 0 backup paths. This live-file check is not a 28-day Search Console metric.
- The 18 October Daily SEO Action recorded **no** 7-day position alerts (`alerts=0`). The 12 October 7-day alert for `commercial fridge repair london` (8.0 → 14.0) was not repeated on 13–18 October. That is still not a 28-day mover and is not copied into the tables above.

## Recommended next actions (no HTML edits in this run)

1. Add Search Console access to this Cursor automation: either a Google Search Console MCP server, or the same `GSC_CREDENTIALS_JSON` secret already used by `.github/workflows/gsc-weekly-sync.yml` and nightly auto-seo.
2. Re-run this reporter once credentials or MCP are attached, then fill last-28 vs previous-28 totals, top 25 tables, country/device splits, movers, and watch lists from live API data.
3. Keep HTML, titles, and marketing copy unchanged until a live 28-day pull exists. Do not request indexing from this report.
4. Separately: live and repo sitemaps still show 122 public URLs and no `/_old_site_backup/` paths; confirm why Search Console still reports 0 indexed URLs against 122 submitted; note that Daily SEO on `main` is still dispatch-only and no longer queries Search Console in YAML; inspect why the scheduled nightly auto-seo runs failed after the 22 October 20:40 UTC success; and re-check `commercial fridge repair london`, `/commercial-fridge-repair-enfield/` (inspection 404), and `/freezer-room-repair-london/` on a proper 28-day window. Do not repeat indexing requests from this reporter.

## Short summary

- **Totals:** not available (Search Console MCP and credentials missing in this environment).
- **3 biggest wins:** not available — no live 28-day query or page rows. Process notes only: the URL-prefix property `https://www.colddirect.co.uk/` was reached again on 22 October 20:48 UTC; live and repo sitemaps still match at 122 public URLs with no backup paths; URL Inspection now shows `/commercial-appliances-repair-london/` as PASS / Submitted and indexed (it was discovered-not-indexed on 18 October).
- **3 biggest risks:** (1) this daily GSC report cannot run without API access in the Cursor automation, and Daily SEO on `main` is still dispatch-only without a GSC query step (no 19–23 October Daily SEO run); (2) 28-day movers and high-impression low-CTR queries are unknown until a live pull; (3) Search Console still last showed 0 indexed URLs against 122 submitted, scheduled nightly auto-seo failed twice after 22 October 20:40 UTC, and watch queries / money pages cannot be monitored here until credentials or MCP are added.
