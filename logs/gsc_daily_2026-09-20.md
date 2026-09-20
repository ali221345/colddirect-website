# Google Search Console daily report — Cold Direct

- **Date generated:** 20 September 2026 (14:30 UTC)
- **Date range requested:** last 28 days (23 August 2026 – 19 September 2026) vs previous 28 days (26 July 2026 – 22 August 2026). End date = yesterday (19 September 2026).
- **Property:** `https://www.colddirect.co.uk/`
- **Search type:** web
- **Lag:** Search Console data is usually 2–3 days behind, so the latest days in any live pull are often incomplete.

## Status: Search Console tools unavailable in this run

This reporter **did not pull live 28-day analytics**. No totals, query tables, page tables, country/device splits, movers, or CTR-risk lists are shown below, because inventing or recycling the wrong window would be misleading.

### What was checked

1. **Cursor Search Console MCP** — not present in this automation. There is no Google Search Console tool namespace to call `sites.list` or `searchanalytics.query`.
2. **Credentials in this environment** — `GSC_CREDENTIALS_JSON`, `GSC_KEY_FILE`, `GSC_REFRESH_TOKEN`, and local key files (`gsc-key.json`, `credentials.json`) are all missing. This cloud agent cannot authenticate to the Search Console API.
3. **Property existence (indirect confirmation only)** — this run could not call Search Console itself. The GitHub Action **ColdDirect Daily SEO** did authenticate this morning (20 September 2026, 05:09 UTC) with service account `github-seo-bot@colddirect-live.iam.gserviceaccount.com`, resolved site URL `https://www.colddirect.co.uk/`, and queried web search analytics plus sitemaps (`submitted: 118`). That is evidence the property exists and is reachable from GitHub Actions, not a live confirmation from this reporter.

### What was not used

`seo-audit/daily-report-2026-09-20.md` is a **7-day** snapshot (13–19 September 2026), not the 28-day vs previous-28 comparison this report requires. Those figures are **not** copied here.

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

## Recommended next actions (no HTML edits in this run)

1. Add Search Console access to this Cursor automation: either a `google-search-console` MCP server, or the same `GSC_CREDENTIALS_JSON` secret already used by `.github/workflows/colddirect-daily-seo.yml`.
2. Re-run this reporter once credentials or MCP are attached, then fill last-28 vs previous-28 totals, top 25 tables, country/device splits, movers, and watch lists from live API data.
3. Keep HTML, titles, and marketing copy unchanged until a live 28-day pull exists. Do not request indexing from this report.

## Short summary

- **Totals:** not available (Search Console MCP and credentials missing in this environment).
- **3 biggest wins:** not available — no live 28-day query or page rows.
- **3 biggest risks:** (1) this daily GSC report cannot run without API access; (2) 28-day movers and high-impression low-CTR queries are unknown until a live pull; (3) watch queries and money pages cannot be monitored here until credentials or MCP are added.
