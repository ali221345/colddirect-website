# Prioritised backlog

Reviewed 2026-10-07. These are investigations/opportunities, not ten proven defects.
Before implementation check latest Git, ledgers and PRs again. P0 broken/dangerous;
P1 high impact; P2 growth; P3 experiments. Do not change live routing or infrastructure
without the required evidence and approval.

| Rank | Priority | Opportunity | Evidence / next verification | Status |
|---|---|---|---|---|
| 1 | P1 | Repair Services navigation destination | /services/ lands at homepage; inspect unfollowed HTTP responses and Plesk/IIS rules, validate a small fix in isolation | Confirmed navigation behaviour; cause open |
| 2 | P1 | Reconcile deployment copies and protection | Current root deploy differs from README mirror guidance; compare changed pages, fingerprint checks and live result | Open |
| 3 | P1 | Reconcile sitemap inventory | Latest report has 362 entries vs expected ~115; identify aliases, noindex/canonical targets and generator inputs before removal | Open; no blind URL deletion |
| 4 | P1 | Validate audit classification | AUDIT-REPORT marks all 107 pages weak; scripts rely on seo-article marker and local paths | Open; reproduce false positives first |
| 5 | P1 | Check enquiry flow on mobile | Telephone CTAs present; actual consultation/booking path and conversion data not yet checked | Open; no real customer enquiry submission |
| 6 | P1 | Resolve legacy fridge/freezer query landing paths | gsc_followup still shows homepage/legacy aliases; obtain current query/page rows, then inspect routing before targeted changes | Open |
| 7 | P1 | Check trusted business claims | Live homepage includes reviews, certifications and experience/job-count claims; authoritative evidence not reviewed | Needs owner/source records; do not invent or call them false |
| 8 | P1 | Reconcile live schema with intended entity | Homepage is HVACBusiness + FAQPage despite older ApplianceRepair claim; compare canonical entity IDs and copies | Open; no blind global replacement |
| 9 | P2 | Verify money-page mobile performance | Historical Lighthouse results were local lab with SSI limits; establish current live CWV/lab baseline | Open |
| 10 | P2 | Verify recent SEO Draft mitigation | Root ledger documents repeated failures and bounded-call fix on 6 October; check next genuine run result before more changes | Open; scheduler not accessed |

Existing work tracked separately: PR #14 named crawler exclusions is already implemented
on its branch and awaiting review. Do not duplicate it as a fresh opportunity.
Completed earlier work (metadata templates, broad noindex cleanup, homepage service
links, Liebherr page, backup/rank tooling) is not automatically a new task.

First completed foundation: six memory files on a dedicated branch. Highest-confidence
next website task is #1 investigation; implementation depends on proving the responsible
routing rule and testing for loops.

## 2026-10-07 update
Opportunity #1 is resolved: the Services home redirect was in .htaccess. Ten live route
checks passed after the focused production change. Keep the regression checker for
future deploys. Remaining separate work: make the Services hub more useful, then
validate indexation in Search Console; neither is claimed complete by this routing fix.

## 2026-10-07 — Crawl policy continuation and current status
Services routing task is completed: PR #15 merged/deployed, ten live routes pass. Continue existing crawl-policy PR #14: proven named-group exclusion bug, 192 checks pass; release verification pending. Sitemap inventory reconciliation remains the next priority; inspect canonical/noindex/redirect entries before removing URLs.

## 2026-10-07 — Sitemap inventory correction
PR #14 was explicitly approved, merged as 9453f995 and successfully deployed; 112 live robot policy checks and ten route checks passed. This supersedes earlier pending approval notes.

Fresh live sitemap: 362 entries, all unique: 226 redirects, 132 HTTP 500, two HTTP 404, two HTTP 200; those two declare other canonicals. The existing generator walked mirrors/internal repository paths and advertised raw .html/index.html aliases. Replaced it with public canonical discovery, robots/noindex filtering, live redirect/canonical resolution, deduplication and fail-before-write on transport/429/5xx. Both sitemap copies are identical. Daily workflow now stages the root sitemap it actually generates. Unverified lastmod dates omitted rather than marking every page freshly changed each run.

Prepared sitemap: 112 unique URLs, all freshly checked HTTP 200 with no noindex. Four focused regression tests pass. This is discovery-list cleanup, no page deletion or route/content change. No search ranking/indexation gain claimed; production release is pending. Some served pages declare a bare canonical that redirects to their slash URL; normalized served URLs are listed, while metadata consistency remains a separate task.

Next P0 routing investigations: /blog/commercial-fridge-repair-cost-london/ and its .html alias redirect to each other; /refrigeration-brands-repair-london/ returns 404. Both are excluded from this sitemap, not deleted. Recheck current policy before fixing routes. Also retain the current public ASP canonicals for chiller/ice-machine pages pending a separate canonical review.

## PR16 release complete — 2026-10-07
User explicitly approved PR16 merge and Plesk release. Merge 500634e3dda456d27b04e1d178f9785ff90dddc8; deployment run 37652640835 completed successfully. Live map matches approved 112 URLs; all return HTTP 200 without noindex. Ten core route/Services content and 112 robots policy checks pass. Earlier pending/rejected release notes are superseded. No Google ranking/indexation uplift measured. Next daily scheduled run is unverified. Post-release memory is committed on ai/seo-canonical-sitemap to avoid an additional documentation-only production deployment.
