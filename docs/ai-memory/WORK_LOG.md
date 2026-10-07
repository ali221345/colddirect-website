# Work log

## 2026-10-07 — Initial current-state review and memory
Base: af339f118bfbd069c1deda91e4b589e3e241ac5b (main).
Branch: ai/docs-project-memory.

Read README, recent commits and branches, repository tree, deployment workflow,
LESSONS-LEARNED.md, seo_fixes.md, audit scripts/report, latest daily search report,
gsc_followup.md and previous competitive/change/upgrade documents.
Checked open PRs; found existing crawl-policy draft PR #14.

Signed into the user-provided Plesk and observed Active domain plus existing httpdocs.
Opened LESSONS-LEARNED.md; its visible opening matches the repository ledger.
Closed the editor using Cancel. No file save, hosting change or data mutation.

Viewed the live www homepage; checked canonical, description, H1, parseable JSON-LD
types and footer links. Direct /services/ navigation ended at /. Live robots access
was blocked by browser client. No HTTP-chain measurement or booking submitted.

Added these six memory files without replacing any historical ledgers.
Validation: checked six required paths, reviewed sources and diff scope; documentation
only, no production-code changes. Docs are excluded by current FTP deploy workflow.
No production deployment, SEO uplift or full technical audit claimed.

Commit: docs: establish ColdDirect operational project memory.
Use this commit message/branch to locate the commit in Git history; its SHA is assigned
after these files are committed. No self-referential SHA fabricated.

## 2026-10-07 — Authorized Services routing fix
Read root history, memory and deployed files. Reproduced 301 to / by GET and HEAD.
Proved exact .htaccess rule in /httpdocs; saved pre-change backup locally. Edited only
the services redirect and added an index.html exception. Applied via Plesk editor.
Verified ten live routes using tools/check-services-routing.py, Services H1/canonical/
indexing/schema, plus existing homepage and four service routes. JSON-LD validator
scanned 418 files with zero errors. Fresh browser query displays Services (old 301 cached).
Updated both repository .htaccess copies, six memory files and root lessons. Merge
uses [skip ci] to preserve unrelated live work while recording the already applied fix.
No SEO uplift claimed; no enquiry/payment submitted; no IIS/DNS/security settings changed.

## Merge status — 2026-10-07
PR #15 is ready for review but NOT merged. Automatic approval review rejected the
merge because main triggers automatic Plesk deployment and could overwrite unrelated
production files. Do not bypass or retry without approval/evidence resolving that risk.
The focused /httpdocs/.htaccess fix remains live and tested; source changes are on
ai/docs-project-memory. Main still contains the old rule until approved integration,
so a future deployment from main could reintroduce it. No deployment settings changed.

## 2026-10-07 — Crawl policy continuation and current status
Read all six memory files and root lessons; inspected existing PR #14 diff and main 15886fb. Fresh HTTP robots matched old policy. Re-ran PR #14 checker in an isolated validation directory: 192 checks passed. Continued the original branch, preserved current main including Services fix, and appended current memory. No content rewrite or ranking uplift claimed. PR #14 release verification pending.

## PR #14 release gate — 2026-10-07
Automatic approval review rejected the production merge: main triggers automatic Plesk deployment, risking overwrite of unrelated live files; exact PR14 production approval is required. No merge/deployment performed and no workaround attempted. Prepared policy passes 192 checks. Explicit approval requested; pending user response.

## 2026-10-07 — Sitemap inventory correction
PR #14 was explicitly approved, merged as 9453f995 and successfully deployed; 112 live robot policy checks and ten route checks passed. This supersedes earlier pending approval notes.

Fresh live sitemap: 362 entries, all unique: 226 redirects, 132 HTTP 500, two HTTP 404, two HTTP 200; those two declare other canonicals. The existing generator walked mirrors/internal repository paths and advertised raw .html/index.html aliases. Replaced it with public canonical discovery, robots/noindex filtering, live redirect/canonical resolution, deduplication and fail-before-write on transport/429/5xx. Both sitemap copies are identical. Daily workflow now stages the root sitemap it actually generates. Unverified lastmod dates omitted rather than marking every page freshly changed each run.

Prepared sitemap: 112 unique URLs, all freshly checked HTTP 200 with no noindex. Four focused regression tests pass. This is discovery-list cleanup, no page deletion or route/content change. No search ranking/indexation gain claimed; production release is pending. Some served pages declare a bare canonical that redirects to their slash URL; normalized served URLs are listed, while metadata consistency remains a separate task.

Next P0 routing investigations: /blog/commercial-fridge-repair-cost-london/ and its .html alias redirect to each other; /refrigeration-brands-repair-london/ returns 404. Both are excluded from this sitemap, not deleted. Recheck current policy before fixing routes. Also retain the current public ASP canonicals for chiller/ice-machine pages pending a separate canonical review.

## PR16 release complete — 2026-10-07
User explicitly approved PR16 merge and Plesk release. Merge 500634e3dda456d27b04e1d178f9785ff90dddc8; deployment run 37652640835 completed successfully. Live map matches approved 112 URLs; all return HTTP 200 without noindex. Ten core route/Services content and 112 robots policy checks pass. Earlier pending/rejected release notes are superseded. No Google ranking/indexation uplift measured. Next daily scheduled run is unverified. Post-release memory is committed on ai/seo-canonical-sitemap to avoid an additional documentation-only production deployment.
