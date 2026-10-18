# Google Search Console daily report — Cold Direct

- **Date generated:** 8 October 2026 (09:04 UTC)
- **Date range requested:** last 28 days (10 September 2026 – 7 October 2026) vs previous 28 days (13 August 2026 – 9 September 2026). End date = yesterday (7 October 2026).
- **Property:** `https://www.colddirect.co.uk/`
- **Search type:** web
- **Lag:** Search Console data is usually 2–3 days behind, so the latest days in any live pull are often incomplete.

## Status: Search Console tools unavailable in this run

This reporter **did not pull live 28-day analytics**. No totals, query tables, page tables, country/device splits, movers, or CTR-risk lists are shown below, because inventing figures or recycling a different window would be misleading.

### What was checked

1. **Cursor Search Console MCP** — not present in this automation. There is no Google Search Console tool namespace to call `sites.list` or `searchanalytics.query`.
2. **Credentials in this environment** — `GSC_CREDENTIALS_JSON`, `GOOGLE_APPLICATION_CREDENTIALS`, `GOOGLE_CLIENT_ID` / `GSC_REFRESH_TOKEN`, and local key files (`gsc-key.json`, `gsc-oauth.json`, `credentials.json`) are all missing. `python gsc_report.py` cannot authenticate (no `google` client library and no key). This cloud agent cannot call the Search Console API.
3. **Property existence (confirmed via GitHub Actions, not this reporter’s own API call)** — this run could not call Search Console itself. The GitHub Action **ColdDirect Daily SEO** last authenticated on 7 October 2026 at 11:31 UTC with service account `github-seo-bot@colddirect-live.iam.gserviceaccount.com`, listed sites, and resolved site URL `https://www.colddirect.co.uk/`. It then queried web search analytics for a **7-day** window (30 September – 6 October 2026) and sitemaps (`type: web`, `submitted: 362`, `indexed: 0`). That is evidence the property exists and is reachable from GitHub Actions. The Action’s live HTTP sitemap check that run returned status `200` and `362` `<loc>` entries.
4. **Today’s scheduled Action** — as of this report (8 October 2026, 09:04 UTC) there is no 8 October run of `colddirect-daily-seo.yml`. The workflow is scheduled for 05:00 UTC. The newest completed run is 7 October 2026 (it started at 11:31 UTC, not 05:00). A separate **Daily SEO Agent** workflow did run at 08:09 UTC today; that job rebuilds the sitemap and scores HTML. It does not pull 28-day Search Console analytics.

### What was not used

`seo-audit/daily-report-2026-10-07.md` is a **7-day** snapshot (30 September – 6 October 2026), not the 28-day vs previous-28 comparison this report requires. Those figures are **not** copied here. Older 28-day files under `reports/gsc/` and CSV logs (including `gsc_report.csv` / `gsc_followup.md`, window ending 6 October) were also left unused, because they are not a live pull for today’s windows.

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
- The 7 October Action still reports GSC sitemap `indexed: 0` against `submitted: 362`. Its live HTTP sitemap fetch succeeded that run (`200` / 362 `<loc>`). That is a process note from the Action, not a 28-day analytics finding.
- The scheduled 8 October ColdDirect Daily SEO Action had not appeared by 09:04 UTC, so there is also no same-day 7-day snapshot. Yesterday’s run was late (11:31 UTC rather than 05:00), as were the 4–6 October runs.

## Recommended next actions (no HTML edits in this run)

1. Add Search Console access to this Cursor automation: either a Google Search Console MCP server, or the same `GSC_CREDENTIALS_JSON` secret already used by `.github/workflows/colddirect-daily-seo.yml`.
2. Re-run this reporter once credentials or MCP are attached, then fill last-28 vs previous-28 totals, top 25 tables, country/device splits, movers, and watch lists from live API data.
3. Keep HTML, titles, and marketing copy unchanged until a live 28-day pull exists. Do not request indexing from this report.
4. Separately, investigate GSC sitemap `indexed: 0` against 362 submitted URLs, even though the 7 October Action could fetch the live sitemap (`200` / 362 `<loc>`). Also confirm why the Daily SEO workflow keeps starting late (11:31 UTC on 7 October rather than 05:00).

## Short summary

- **Totals:** not available (Search Console MCP and credentials missing in this environment).
- **3 biggest wins:** not available — no live 28-day query or page rows.
- **3 biggest risks:** (1) this daily GSC report cannot run without API access in the Cursor automation; (2) 28-day movers and high-impression low-CTR queries are unknown until a live pull; (3) watch queries and money pages cannot be monitored here until credentials or MCP are added, and Search Console still shows 0 indexed URLs against 362 submitted.
