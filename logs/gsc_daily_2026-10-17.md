# Google Search Console daily report — Cold Direct

- **Date generated:** 17 October 2026 (09:04 UTC)
- **Date range requested:** last 28 days (19 September 2026 – 16 October 2026) vs previous 28 days (22 August 2026 – 18 September 2026). End date = yesterday (16 October 2026).
- **Property:** `https://www.colddirect.co.uk/`
- **Search type:** web
- **Lag:** Search Console data is usually 2–3 days behind, so the latest days in any live pull are often incomplete.

## Status: Search Console tools unavailable in this run

This reporter **did not pull live 28-day analytics**. No totals, query tables, page tables, country/device splits, movers, or CTR-risk lists are shown below, because inventing figures or recycling a different window would be misleading.

### What was checked

1. **Cursor Search Console MCP** — not present in this automation. There is no Google Search Console tool namespace to call `sites.list` or `searchanalytics.query`.
2. **Credentials in this environment** — `GSC_CREDENTIALS_JSON`, `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_CLIENT_ID` / `GSC_REFRESH_TOKEN`, and local key files (`gsc-key.json`, `gsc-oauth.json`, `credentials.json`) are all missing. `python gsc_report.py` cannot authenticate (no `google` client library and no key). This cloud agent cannot call the Search Console API.
3. **Property existence (confirmed via GitHub Actions, not this reporter’s own API call)** — this run could not call Search Console itself. The GitHub Action **ColdDirect Daily SEO** authenticated today, 17 October 2026, at 09:00 UTC with service account `github-seo-bot@colddirect-live.iam.gserviceaccount.com`, listed sites, and resolved site URL `https://www.colddirect.co.uk/`. It then queried web search analytics for a **7-day** window (10–16 October 2026) and sitemaps (`type: web`, `submitted: 116`, `indexed: 0`). That is evidence the property exists and is reachable from GitHub Actions. It finished with `changes=0`, `alerts=0`.
4. **Today’s scheduled Action** — `colddirect-daily-seo.yml` run `39019470889` started at 09:00 UTC (still late against the 05:00 UTC schedule, but earlier than 16 October 09:29 and 15 October 09:36). A separate **Daily Sitemap and HTML Checks** workflow ran at 06:22 UTC today, counted 116 unique public canonical URLs in the repository sitemap, and committed nothing. It does not pull 28-day Search Console analytics.

### What was not used

The 17 October Action wrote `seo-audit/daily-report-2026-10-17.md` on the runner only (7-day window 10–16 October 2026); that file is not in this repository. Those figures are **not** copied here. Older 7-day files under `seo-audit/daily-report-*.md`, older 28-day files under `reports/gsc/`, and CSV logs (including `gsc_report.csv` / `gsc_followup.md` and `logs/gsc_report_2026-10-07.csv`) were also left unused, because they are not a live pull for today’s 28-day windows.

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

Could not be scored for these windows:

- Queries: cold room repair london; commercial fridge repair london; fridge repair london; freezer repair london; commercial freezer repair london
- Pages: homepage; cold-room repairs; fridge-repair-london; freezer-repair-london; commercial-fridge-repair-london; commercial-freezer-repair-london

## Movers and risks

- Live 28-day click, impression, and position movers could not be calculated.
- High-impression, low-CTR queries (impressions > 300, CTR < 2%) could not be listed.
- Watch-query and watch-page movement could not be listed.
- GitHub Actions can reach the property, but this daily reporter still cannot run the required 28-day vs previous-28 query, so movers and risks stay unknown.
- The 17 October Action reports GSC sitemap `indexed: 0` against `submitted: 116` (submitted rose from 112 on 9–16 October to 116 today; indexed remains 0). That is a process note from the Action, not a 28-day analytics finding.
- The same Action’s live HTTP sitemap fetch succeeded (`200`) but counted **484** `<loc>` entries, up from 116 on 6–16 October. A same-day fetch of `https://www.colddirect.co.uk/sitemap.xml` also returned 484 unique `<loc>` values, all `lastmod` 17 October 2026, including 102 `/_old_site_backup/` URLs and `_backup_index_old.html`. The repository sitemaps still list 116 URLs. This live-file drift is not a 28-day Search Console metric.
- The 17 October Action recorded **no** 7-day position alerts (`alerts=0`). The 12 October 7-day alert for `commercial fridge repair london` (8.0 → 14.0) was not repeated on 13–17 October. That is still not a 28-day mover and is not copied into the tables above.

## Recommended next actions (no HTML edits in this run)

1. Add Search Console access to this Cursor automation: either a Google Search Console MCP server, or the same `GSC_CREDENTIALS_JSON` secret already used by `.github/workflows/colddirect-daily-seo.yml`.
2. Re-run this reporter once credentials or MCP are attached, then fill last-28 vs previous-28 totals, top 25 tables, country/device splits, movers, and watch lists from live API data.
3. Keep HTML, titles, and marketing copy unchanged until a live 28-day pull exists. Do not request indexing from this report.
4. Separately: restore the live `sitemap.xml` to the intended public set (repository still has 116 canonical URLs; live file now lists 484, including backup paths), confirm why GSC still shows 0 indexed URLs against 116 submitted, and re-check `commercial fridge repair london` on a proper 28-day window after the 12 October 7-day Action alert (8.0 → 14.0).

## Short summary

- **Totals:** not available (Search Console MCP and credentials missing in this environment).
- **3 biggest wins:** not available — no live 28-day query or page rows.
- **3 biggest risks:** (1) this daily GSC report cannot run without API access in the Cursor automation; (2) 28-day movers and high-impression low-CTR queries are unknown until a live pull; (3) watch queries and money pages cannot be monitored here until credentials or MCP are added, Search Console still shows 0 indexed URLs against 116 submitted, and the live sitemap has ballooned to 484 URLs including old-site backup paths.
