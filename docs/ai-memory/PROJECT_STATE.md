# ColdDirect project state

Reviewed 2026-10-07 (Europe/London). Source revision: af339f118bfbd069c1deda91e4b589e3e241ac5b.

## Session start
Before any work, read all six files in this directory, then LESSONS-LEARNED.md,
seo_fixes.md, seo_fixes_archive.md, docs/change-log.md and recent Git history.
Check open PRs and current branch/working-tree state. Preserve all existing work.
Update this memory after meaningful work. Never put credentials or customer data here.

## Business and live site
ColdDirect is a commercial refrigeration repair/emergency callout business serving
London from North London, not an equipment ecommerce catalogue. This is documented in
docs/competitive-research.md and visibly confirmed on the live homepage. Do not invent
products, stock, prices, guarantees, reviews, certifications or coverage.

Plesk access verified; colddirect.co.uk is Active. File Manager shows production files
under httpdocs, including legacy ASP, static HTML, PHP helpers, directory index files,
shared includes, docs and agent files. Another session used the same Plesk username.
No production edits were made in this review.

## Architecture and deployment
Repository: https://github.com/ali221345/colddirect-website (main).
Static HTML, directory index.html routes, Classic ASP and PHP helpers; web.config
contains IIS routing. Shared includes and colddirect-public-html mirror also exist.
Historical notes call the stack Windows Plesk/IIS. Current server response headers
were not collected in this session.

Current .github/workflows/deploy.yml deploys the repository ROOT on main/master push,
excluding colddirect-public-html, docs, agent, tools, scripts and other paths. This
differs from README/older inventory notes describing mirror deployment. Inspect the
workflow and protection exclusions before each change; do not rely on old deployment notes.
protected-pages.json and agent/scripts/protect_fixed_pages.py guard selected pages.
Changing protected titles requires matching fingerprint updates in the same commit.
package.json test/build runs tools/validate-ldjson.js. It is not a full functional test.

## Operational history
Hermes has existing scheduled SEO drafting/publishing, reporting, page protection,
sitemap and backup work. Latest main commit is daily seo 2026-10-07. Exact current
scheduler state and next-run success were not independently verified.
SEO Draft failures and disproven remedies are recorded in LESSONS-LEARNED.md;
latest mitigation bounds research and retains a retry. Do not claim it resolved.

Open draft PR #14 already fixes named crawler utility exclusions:
https://github.com/ali221345/colddirect-website/pull/14
Do not duplicate its robots changes.

## Baseline
Stored seo-audit/daily-report-2026-10-07.md, window 2026-09-30 to 2026-10-06:
42 clicks; 8,655 impressions; CTR 0.49%; average position 29.9.
cold room repair london: 5 clicks / 22 impressions / position 2.7.
commercial fridge repair london: 5 / 49 / position 7.2.
fridge repair london: 0 / 50 / position 9.6.
freezer repair london: 3 / 9 / position 13.1 (small sample).
Zero-impression rows are no data, not a ranking of zero.
These are repository report values, not a fresh authenticated GSC query.

The same report states live sitemap HTTP 200 and 362 loc entries versus expected ~115.
That mismatch needs reconciliation with aliases and generator policy, not blind deletion.
GSC indexed=0 in that report is not evidence the whole site is unindexed.

Live homepage observed today:
- Canonical https://www.colddirect.co.uk/
- Title: Commercial Fridge & Freezer Same-Day Repair London | 24/7 Emergency | ColdDirect
- One H1: Emergency Commercial Refrigeration Repair London - Same Day Service
- Description and telephone CTA links present; no meta robots tag observed.
- Two JSON-LD blocks parse: HVACBusiness and FAQPage. Old notes claiming ApplianceRepair
  everywhere do not describe this live homepage.
- Initial /services/ navigation ended at the homepage. The focused fix below supersedes this finding.

Live robots access was blocked by the browser client; web fetches also failed earlier.
This is a tool limitation, not evidence of site downtime or blocked Google access.
No current Core Web Vitals, conversion baseline, booking submission test or Search
Console permissions checked. Existing business claims are not independently verified.

## Remaining first-review work
Full deployment-copy reconciliation, live HTTP redirect/404 checks, booking flow review,
fresh GSC query/page data and performance measurements remain outstanding.

## 2026-10-07 — Services redirect fixed
User requested the recurring Services/SEO bug be fixed. Production /httpdocs/.htaccess
contained an explicit services-to-home 301. Replaced it with a bare-path redirect to
/services/ and a pass-through for the directory. Added services/index.html exception
before generic HTML redirects to prevent default-document loops. No web.config or
Plesk infrastructure setting changed. Root and mirror .htaccess receive the same fix.
Live checks: ten routes passed; /services/ 200, /services and /services.html each 301
to /services/, index.html 200 with the same canonical. H1/JSON-LD/indexing checked.
Browser retained the old cached 301; a fresh query returned the corrected page.
SEO indexation/ranking changes are not yet measured. Services content remains sparse.

Plesk Git is configured for automatic main deployment to \\httpdocs (no post-deployment
actions). GitHub workflow skips do not disable this separate integration.

## Merge status — 2026-10-07
PR #15 is ready for review but NOT merged. Automatic approval review rejected the
merge because main triggers automatic Plesk deployment and could overwrite unrelated
production files. Do not bypass or retry without approval/evidence resolving that risk.
The focused /httpdocs/.htaccess fix remains live and tested; source changes are on
ai/docs-project-memory. Main still contains the old rule until approved integration,
so a future deployment from main could reintroduce it. No deployment settings changed.

## 2026-10-07 — Crawl policy continuation and current status
PR #15 merged as 15886fb82f8c3a40eaf60e4f5c59f629944af5a1 with explicit user approval; its deployment completed successfully and ten live route checks passed. This supersedes the earlier pending/rejected merge status. Live robots.txt still has named Allow-only groups that bypass wildcard utility exclusions. PR #14 is being continued with its existing shared-group fix; 192 policy checks pass. Production release of #14 is not yet verified.

## PR #14 release gate — 2026-10-07
Automatic approval review rejected the production merge: main triggers automatic Plesk deployment, risking overwrite of unrelated live files; exact PR14 production approval is required. No merge/deployment performed and no workaround attempted. Prepared policy passes 192 checks. Explicit approval requested; pending user response.
