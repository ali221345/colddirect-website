# Google Search Console daily report — Cold Direct

- **Date generated:** 28 October 2026 (09:02 UTC)
- **Date range requested:** last 28 days (30 September 2026 – 27 October 2026) vs previous 28 days (2 September 2026 – 29 September 2026). End date = yesterday (27 October 2026).
- **Property:** `https://www.colddirect.co.uk/`
- **Search type:** web
- **Lag:** Search Console data is usually 2–3 days behind, so the latest days in any live pull are often incomplete.

## Status: Search Console tools unavailable in this run

This reporter **did not pull live 28-day analytics**. No totals, query tables, page tables, country/device splits, movers, or CTR-risk lists are shown below, because inventing figures or recycling a different window would be misleading.

### What was checked

1. **Cursor Search Console MCP** — not present in this automation. There is no Google Search Console tool namespace to call `sites.list` or `searchanalytics.query`.
2. **Credentials in this environment** — `GSC_CREDENTIALS_JSON`, `GOOGLE_APPLICATION_CREDENTIALS`, and local key files (`gsc-key.json`, `gsc-oauth.json`, `credentials.json`) are all missing. The `google` / `google.auth` and `googleapiclient` libraries are not installed here. A trial Search Analytics client could not authenticate. This cloud agent cannot call the Search Console API.
3. **Property existence (confirmed via GitHub Actions, not this reporter’s own API call)** — this run could not list sites itself. GSC Weekly Sync **scheduled** run `40318782178` on 26 October 2026 at 11:56 UTC authenticated with repo secret `GSC_CREDENTIALS_JSON`, resolved the URL-prefix property `https://www.colddirect.co.uk/`, and wrote a **7-day** performance Step Summary (window 18–24 October vs 11–17 October). That is evidence the property exists and is reachable from GitHub Actions. Those weekly figures are **not** 28-day search analytics and are **not** copied into the tables below. There is no newer Weekly Sync run as of 09:02 UTC on 28 October.
4. **Later sitemap / URL Inspection confirmation** — Nightly auto-seo run `40588680581` on 27 October 2026 at 21:40 UTC submitted `https://www.colddirect.co.uk/sitemap.xml` (HTTP 204 at 21:49 UTC) and inspected URLs on the same property. That step is sitemap plus URL Inspection only — **not** 28-day search analytics.
5. **Earlier Daily SEO confirmation** — ColdDirect Daily SEO last listed the same property on 18 October 2026 at 09:19 UTC (scheduled run `39114885014`). That Action used a 7-day window (11–17 October) and is still not a 28-day pull.
6. **Today’s scheduled Daily SEO** — as of 09:02 UTC on 28 October 2026 there is **no** `colddirect-daily-seo.yml` run for 19–28 October. On current `main` that workflow is **workflow_dispatch only** (cron disabled) and no longer references `GSC_CREDENTIALS_JSON` or a Search Console query step.

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
- Nightly auto-seo on 27 October 21:49 UTC (run `40588680581`) recorded a GSC sitemap PUT (`lastSubmitted` 2026-10-27T21:49:36.729Z, `last downloaded` 2026-10-26T23:38:20.298Z, pending `True`) with **133** submitted URLs and **0** indexed (`type: web`). The same run’s live smoke test counted **133** sitemap URLs. That is a sitemap-API note, not a 28-day search-analytics pull. The same run logged Indexing API calls **25/25** as OK in its table; this reporter did not request indexing.
- URL Inspection from that same 27 October 21:52 UTC step (25 of 60 inspection calls; not 28-day performance): homepage, `/fridge-repair-london/`, `/freezer-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`, `/cold-room-repair-london/`, `/catering-repair-london/`, `/commercial-appliances-repair-london/`, `/air-conditioning-repair-london/`, and `/cellar-cooler-repair-london/` were `PASS` / Submitted and indexed. `/commercial-fridge-repair-enfield/` remains `NEUTRAL` / Not found (404) even though the same run’s live smoke test recorded HTTP 200 for that URL. Other inspection notes from the 25-URL batch: `/adexa-fridge-repair-london/` still `NEUTRAL` / Discovered - currently not indexed; `/air-conditioning-repair-north-london/`, `/carpigiani-ice-cream-machine-repair-london/`, `/commercial-fridge-repair-brent/`, `/commercial-refrigeration-repair-harlesden/`, `/commercial-refrigeration-repair-willesden/`, `/freezer-repair-north-london/`, and `/write-a-review/` `NEUTRAL` / Discovered - currently not indexed. `/blast-chiller-repair-london/`, `/cold-room-installation-london/`, `/faqs/`, `/taylor-ice-cream-machine-repair-london/`, `/about-us/`, and `/appliances-repair-london/` were `PASS` / Submitted and indexed. `/blast-chiller-repair-north-london/`, `/chiller-repair-north-london/`, and `/freezer-room-repair-london/` were not in this 25-URL nightly batch; the last weekly inspect on 26 October 12:07 UTC had recorded north-London blast-chiller as unknown and freezer-room as Discovered - currently not indexed. This reporter did not request indexing.
- Scheduled nightly auto-seo then failed at 27 October 23:49 UTC (run `40604769510`) and 28 October 00:45 UTC (run `40610809603`) on the “already succeeded today” skip path (exit code 1) and skipped the GSC ping (`S_GSC: skipped`). The last successful GSC sitemap/inspect call remains the 27 October 21:49 UTC run `40588680581`.
- Live `https://www.colddirect.co.uk/sitemap.xml` fetched for this report (28 October 09:02 UTC) returned HTTP 200, `last-modified: Tue, 27 Oct 2026 22:03:36 GMT`, **131** unique `<loc>` values, and **0** `/_old_site_backup/` URLs. Repository root `sitemap.xml` also has **131** unique URLs. Mirror `colddirect-public-html/sitemap.xml` still has **122**. Search Console’s last sitemap-API read showed **133** submitted / **0** indexed. This live-file check is not a 28-day Search Console metric.
- The 18 October Daily SEO Action recorded **no** 7-day position alerts (`alerts=0`). The 12 October 7-day alert for `commercial fridge repair london` (8.0 → 14.0) was not repeated on 13–18 October. That is still not a 28-day mover and is not copied into the tables above.

## Recommended next actions (no HTML edits in this run)

1. Add Search Console access to this Cursor automation: either a Google Search Console MCP server, or the same `GSC_CREDENTIALS_JSON` secret already used by `.github/workflows/gsc-weekly-sync.yml` and nightly auto-seo.
2. Re-run this reporter once credentials or MCP are attached, then fill last-28 vs previous-28 totals, top 25 tables, country/device splits, movers, and watch lists from live API data.
3. Keep HTML, titles, and marketing copy unchanged until a live 28-day pull exists. Do not request indexing from this report.
4. Separately: live sitemap XML still parses as 131 public URLs while Search Console last reported 133 submitted / 0 indexed, nightly smoke said 133 at 21:42 UTC, and the public-html mirror is still 122; confirm Google has recrawled the pending sitemap; note that Daily SEO on `main` is still dispatch-only and no longer queries Search Console in YAML; inspect why the scheduled nightly auto-seo fallback still fails after a same-day success; and re-check `fridge repair london`, `commercial fridge repair london`, `/commercial-fridge-repair-enfield/` (inspection 404 vs live HTTP 200), `/adexa-fridge-repair-london/` (still Discovered), and the north-London blast-chiller / freezer-room URLs that were not in last night’s 25-URL inspect batch, on a proper 28-day window. Do not repeat indexing requests from this reporter.

## Short summary

- **Totals:** not available (Search Console MCP and credentials missing in this environment).
- **3 biggest wins:** not available — no live 28-day query or page rows. Process notes only: the URL-prefix property `https://www.colddirect.co.uk/` was reached again on 27 October (nightly sitemap/inspect at 21:49 UTC, after the 26 October Weekly Sync performance report); Search Console’s sitemap API now shows 133 submitted URLs (was 122 on 26 October); URL Inspection still shows the homepage and money hubs as PASS / Submitted and indexed.
- **3 biggest risks:** (1) this daily GSC report cannot run without API access in the Cursor automation, and Daily SEO on `main` is still dispatch-only without a GSC query step (no 19–28 October Daily SEO run); (2) 28-day movers and high-impression low-CTR queries are unknown until a live pull; (3) Search Console still last showed 0 indexed URLs against 133 submitted while the live sitemap XML parses as 131, scheduled nightly auto-seo failed after the 27 October 21:40 UTC success and skipped GSC, `/commercial-fridge-repair-enfield/` is still an inspection 404, and watch queries / money pages cannot be monitored here until credentials or MCP are added.
