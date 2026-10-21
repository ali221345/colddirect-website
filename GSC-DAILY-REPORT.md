# Google Search Console daily report — Cold Direct

- **Date generated:** 21 October 2026 (09:05 UTC)
- **Date range requested:** last 28 days (23 September 2026 – 20 October 2026) vs previous 28 days (26 August 2026 – 22 September 2026). End date = yesterday (20 October 2026).
- **Property:** `https://www.colddirect.co.uk/`
- **Search type:** web
- **Lag:** Search Console data is usually 2–3 days behind, so the latest days in any live pull are often incomplete.

## Status: Search Console tools unavailable in this run

This reporter **did not pull live 28-day analytics**. No totals, query tables, page tables, country/device splits, movers, or CTR-risk lists are shown below, because inventing figures or recycling a different window would be misleading.

### What was checked

1. **Cursor Search Console MCP** — not present in this automation. There is no Google Search Console tool namespace to call `sites.list` or `searchanalytics.query`.
2. **Credentials in this environment** — `GSC_CREDENTIALS_JSON`, `GOOGLE_APPLICATION_CREDENTIALS`, and local key files (`gsc-key.json`, `gsc-oauth.json`, `credentials.json`) are all missing. A trial `searchanalytics.query` client could not authenticate. This cloud agent cannot call the Search Console API.
3. **Property existence (confirmed via GitHub Actions, not this reporter’s own API call)** — this run could not list sites itself. The GitHub Action **GSC Weekly Sync** last authenticated on 20 October 2026 at 23:03 UTC (`workflow_dispatch` run `39512458941`, head `469e986`). The **Weekly SEO performance report** step succeeded and wrote a 98-line Step Summary using repo secret `GSC_CREDENTIALS_JSON`. That weekly script resolves the verified URL-prefix property `https://www.colddirect.co.uk/` before querying web search analytics. That is evidence the property exists and is reachable from GitHub Actions. That job skipped sitemap submission and URL inspection (`report_only` path). Those weekly figures are a **7-day** window and are **not** copied here.
4. **Earlier Action confirmation** — ColdDirect Daily SEO last listed the same property on 18 October 2026 at 09:19 UTC (scheduled run `39114885014`, head `0dae4e8`) with service account `github-seo-bot@colddirect-live.iam.gserviceaccount.com`, site URL `https://www.colddirect.co.uk/`, 7-day window 11–17 October 2026, sitemap `type: web`, `submitted: 119`, `indexed: 0`. That is still not a 28-day pull.
5. **Today’s scheduled Daily SEO** — as of 09:05 UTC on 21 October 2026 there is **no** `colddirect-daily-seo.yml` run for 19, 20 or 21 October. On current `main` that workflow is **workflow_dispatch only** (cron disabled) and no longer references `GSC_CREDENTIALS_JSON` or a Search Console query step.

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
- GitHub Actions last reached the property on 20 October (weekly 7-day report only), so movers and risks for the required 28-day vs previous-28 windows stay unknown.
- The latest Daily SEO sitemap snapshot (18 October 09:19 UTC) reports `indexed: 0` against `submitted: 119` (`type: web`). That is a process note from the Action, not a 28-day analytics finding.
- Live `https://www.colddirect.co.uk/sitemap.xml` fetched for this report (21 October 09:04 UTC) returned HTTP 200, `last-modified: Wed, 21 Oct 2026 09:03:24 GMT`, **122** unique `<loc>` values, and **0** `/_old_site_backup/` URLs. Repository `sitemap.xml` and `colddirect-public-html/sitemap.xml` currently have **123** unique URLs and 0 backup paths. This live-file check is not a 28-day Search Console metric.
- The 18 October Daily SEO Action recorded **no** 7-day position alerts (`alerts=0`). The 12 October 7-day alert for `commercial fridge repair london` (8.0 → 14.0) was not repeated on 13–18 October. That is still not a 28-day mover and is not copied into the tables above.
- URL Inspection results from the 18 October 09:19 Action (not 28-day performance): homepage, `/fridge-repair-london/`, `/freezer-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`, and `/cold-room-repair-london/` were `PASS` / Submitted and indexed. `/freezer-room-repair-london/` and `/commercial-appliances-repair-london/` were `NEUTRAL` / Discovered - currently not indexed. This reporter did not request indexing.

## Recommended next actions (no HTML edits in this run)

1. Add Search Console access to this Cursor automation: either a Google Search Console MCP server, or the same `GSC_CREDENTIALS_JSON` secret already used by `.github/workflows/gsc-weekly-sync.yml`.
2. Re-run this reporter once credentials or MCP are attached, then fill last-28 vs previous-28 totals, top 25 tables, country/device splits, movers, and watch lists from live API data.
3. Keep HTML, titles, and marketing copy unchanged until a live 28-day pull exists. Do not request indexing from this report.
4. Separately: keep the public sitemap free of `/_old_site_backup/` paths (live is 122 URLs today; repo copies are 123); confirm why GSC still last showed 0 indexed URLs against 119 submitted; note that Daily SEO on `main` is still dispatch-only and no longer queries Search Console in YAML; and re-check `commercial fridge repair london` plus the two discovered-not-indexed URLs (`/freezer-room-repair-london/`, `/commercial-appliances-repair-london/`) on a proper 28-day window. Do not repeat indexing requests from this reporter.

## Short summary

- **Totals:** not available (Search Console MCP and credentials missing in this environment).
- **3 biggest wins:** not available — no live 28-day query or page rows. Process note only: GSC Weekly Sync on 20 October 23:03 UTC still authenticated and wrote a 7-day report for property `https://www.colddirect.co.uk/`, and the live sitemap remains public-only (122 URLs, no backup paths).
- **3 biggest risks:** (1) this daily GSC report cannot run without API access in the Cursor automation, and Daily SEO on `main` is still dispatch-only without a GSC query step (no 19–21 October Daily SEO run); (2) 28-day movers and high-impression low-CTR queries are unknown until a live pull; (3) Search Console still last showed 0 indexed URLs against 119 submitted, and watch queries / money pages cannot be monitored here until credentials or MCP are added.
