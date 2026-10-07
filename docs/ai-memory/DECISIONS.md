# Decisions

## 2026-10-07 — Preserve and extend
Continue the existing repair-service architecture. Existing history documents completed
indexability, metadata, internal linking, schema and performance work. Do not repeat
these tasks or rebuild the site based on a generic supplier SEO plan.

## 2026-10-07 — Separate observation from inference
Live browser navigation confirmed /services/ lands at /. It does not prove a 301,
the full chain or the responsible server rule. Keep routing changes pending an HTTP
investigation because prior IIS rewrite loops are documented.

## 2026-10-07 — Memory complements existing ledgers
These six files provide a current operating index. Keep LESSONS-LEARNED.md and both
seo_fixes ledgers intact as primary historical evidence. Preserve superseded entries
and record corrections rather than erasing history.

## 2026-10-07 — Respect existing work
PR #14 already contains a crawl-policy fix. Track it, do not recreate it. Make this
memory change on ai/docs-project-memory, based on af339f1. No main push or merge:
main/master pushes trigger production FTP deployment.

## 2026-10-07 — Evidence threshold for changes
Use fresh query/page data, preserve winning URLs and avoid content rewrites based solely
on AUDIT-REPORT.md. Its all-pages-WEAK result is a heuristic requiring validation.
Prior notes and the current workflow disagree about which deployment tree is authoritative.

## 2026-10-07 — Persist the authorized Services fix without a full redeploy
The user explicitly requested the routing bug be fixed. Apply only the proven .htaccess
change in production, retain a local pre-change backup, and commit both root/mirror
copies so future deployments retain it. Merge with [skip ci] because the full FTP push
can overwrite unrelated production work; the focused change is already live and tested.
This supersedes the onboarding-only decision to leave memory on a draft branch.

Plesk Git settings checked before merge: main automatically deploys to \\httpdocs,
with no post-deployment shell actions. [skip ci] suppresses GitHub workflows only;
it does not suppress Plesk's configured deployment. The reviewed diff changes two
routing files, documentation and the verification artifacts; core page files are unchanged.

## Merge status — 2026-10-07
PR #15 is ready for review but NOT merged. Automatic approval review rejected the
merge because main triggers automatic Plesk deployment and could overwrite unrelated
production files. Do not bypass or retry without approval/evidence resolving that risk.
The focused /httpdocs/.htaccess fix remains live and tested; source changes are on
ai/docs-project-memory. Main still contains the old rule until approved integration,
so a future deployment from main could reintroduce it. No deployment settings changed.

## 2026-10-07 — Crawl policy continuation and current status
Continue existing PR #14 rather than recreate Hermes' work. Share the existing named agents and wildcard in one group, retaining public crawl access and the sitemap declaration. Block only existing utility paths plus /agent-status/ alias. This is crawl policy, not access control or guaranteed search-result removal. Preserve all main changes from PR #15 while integrating the branch; no page/URL migration or hosting-setting change. PR #15's earlier blocked status is superseded by explicit user approval, merge 15886fb and successful deployment.

## PR #14 release gate — 2026-10-07
Automatic approval review rejected the production merge: main triggers automatic Plesk deployment, risking overwrite of unrelated live files; exact PR14 production approval is required. No merge/deployment performed and no workaround attempted. Prepared policy passes 192 checks. Explicit approval requested; pending user response.

## 2026-10-07 — Sitemap inventory correction
PR #14 was explicitly approved, merged as 9453f995 and successfully deployed; 112 live robot policy checks and ten route checks passed. This supersedes earlier pending approval notes.

Fresh live sitemap: 362 entries, all unique: 226 redirects, 132 HTTP 500, two HTTP 404, two HTTP 200; those two declare other canonicals. The existing generator walked mirrors/internal repository paths and advertised raw .html/index.html aliases. Replaced it with public canonical discovery, robots/noindex filtering, live redirect/canonical resolution, deduplication and fail-before-write on transport/429/5xx. Both sitemap copies are identical. Daily workflow now stages the root sitemap it actually generates. Unverified lastmod dates omitted rather than marking every page freshly changed each run.

Prepared sitemap: 112 unique URLs, all freshly checked HTTP 200 with no noindex. Four focused regression tests pass. This is discovery-list cleanup, no page deletion or route/content change. No search ranking/indexation gain claimed; production release is pending. Some served pages declare a bare canonical that redirects to their slash URL; normalized served URLs are listed, while metadata consistency remains a separate task.

Next P0 routing investigations: /blog/commercial-fridge-repair-cost-london/ and its .html alias redirect to each other; /refrigeration-brands-repair-london/ returns 404. Both are excluded from this sitemap, not deleted. Recheck current policy before fixing routes. Also retain the current public ASP canonicals for chiller/ice-machine pages pending a separate canonical review.
