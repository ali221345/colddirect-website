# SEO history

Read seo_fixes.md and seo_fixes_archive.md for full page-level evidence and chronology.
The entries below are an index of reviewed existing work, not changes made in this session.

| Date | Existing work / URLs | Evidence and limits |
|---|---|---|
| 2026-09-16 | AC/supermarket indexability, utility sitemap cleanup, near-duplicate routing, Liebherr, hubs, metadata/schema and lab performance work | docs/change-log.md; some older branch notes and live-copy claims require reconciliation |
| 2026-09-19 | Singular money-page noindex repairs; plural/ice blog indexing decisions | seo_fixes.md; do not mass remove existing noindex/canonicals |
| 2026-09-23–27 | Freezer-room, freezer and commercial-fridge content work | seo_fixes_archive.md and summary pointers |
| 2026-09-28 | fridge-repair-london title/H1/meta/schema/FAQ updates across four copies | bbf007c, seo_fixes.md; existing homepage internal links retained |
| 2026-10-01 | Protected fridge-page title fingerprint synchronized | ca67097; LESSONS-LEARNED.md |
| 2026-10-02 | Rank history and backup tooling introduced | 1d5719d; ranking guard requires meaningful impressions |
| 2026-10-05 | commercial-freezer-repair-north-london robots tag added; winner title/content preserved | 0e0aa88 plus facd4d8 verification log |
| 2026-10-07 | Crawl-policy improvement already proposed | Open draft PR #14; not merged/deployed as of review |
| 2026-10-07 | Read-only onboarding, baseline and project memory | No content/routing/schema changes; no uplift claimed |

Latest stored seven-day baseline: 42 clicks, 8,655 impressions, CTR 0.49%, average
position 29.9 (30 September–6 October). Cold-room query position 2.7 on 22 impressions;
commercial-fridge query 7.2 on 49 impressions. This window cannot be directly compared
to old 28/90-day totals as proof of improvement.

The 2026-10-05 gsc_followup report still attributes cold-room clicks to
/cold-room-repairs-london while current web.config redirects that alias to the singular
route and the live homepage links singular. Establish current canonical/redirect/GSC
state before altering either URL.

SEO results from this session: none measured; memory only.

## 2026-10-07 — Services routing repair
Before: GET/HEAD /services/ -> 301 homepage. After: 200 Services content, canonical
https://www.colddirect.co.uk/services/, no noindex/nofollow, JSON-LD parses. Bare and
.html aliases lead directly to the canonical route. Removes a concrete crawl obstacle;
does not prove Google indexation or ranking improvement. Report: reports/services-routing-2026-10-07.json.

## 2026-10-07 — Crawl policy continuation and current status
Fresh live robots.txt confirmed the old named Allow-only groups on 2026-10-07. Google's documented group-selection rules confirm named groups do not inherit wildcard rules (https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec). Existing PR #14 shared-group policy passes 192 bot/path checks across identical root/mirror copies. No ranking/indexation uplift measured; release not yet verified. Services PR #15 is merged/deployed and ten live checks passed.

## 2026-10-07 — Sitemap inventory correction
PR #14 was explicitly approved, merged as 9453f995 and successfully deployed; 112 live robot policy checks and ten route checks passed. This supersedes earlier pending approval notes.

Fresh live sitemap: 362 entries, all unique: 226 redirects, 132 HTTP 500, two HTTP 404, two HTTP 200; those two declare other canonicals. The existing generator walked mirrors/internal repository paths and advertised raw .html/index.html aliases. Replaced it with public canonical discovery, robots/noindex filtering, live redirect/canonical resolution, deduplication and fail-before-write on transport/429/5xx. Both sitemap copies are identical. Daily workflow now stages the root sitemap it actually generates. Unverified lastmod dates omitted rather than marking every page freshly changed each run.

Prepared sitemap: 112 unique URLs, all freshly checked HTTP 200 with no noindex. Four focused regression tests pass. This is discovery-list cleanup, no page deletion or route/content change. No search ranking/indexation gain claimed; production release is pending. Some served pages declare a bare canonical that redirects to their slash URL; normalized served URLs are listed, while metadata consistency remains a separate task.

Next P0 routing investigations: /blog/commercial-fridge-repair-cost-london/ and its .html alias redirect to each other; /refrigeration-brands-repair-london/ returns 404. Both are excluded from this sitemap, not deleted. Recheck current policy before fixing routes. Also retain the current public ASP canonicals for chiller/ice-machine pages pending a separate canonical review.

## PR16 release complete — 2026-10-07
User explicitly approved PR16 merge and Plesk release. Merge 500634e3dda456d27b04e1d178f9785ff90dddc8; deployment run 37652640835 completed successfully. Live map matches approved 112 URLs; all return HTTP 200 without noindex. Ten core route/Services content and 112 robots policy checks pass. Earlier pending/rejected release notes are superseded. No Google ranking/indexation uplift measured. Next daily scheduled run is unverified. Post-release memory is committed on ai/seo-canonical-sitemap to avoid an additional documentation-only production deployment.

## 2026-10-07 — Search Console connected and discovery submitted
User signed into Search Console; URL-prefix property https://www.colddirect.co.uk/ is accessible. Resubmitted sitemap.xml through the UI; Google confirmed successful submission. Table still shows old 362 discovered URLs/last read 2026-10-06; do not treat this as failure of the deployed 112-URL map.
Existing local service-account credential verified using webmasters.readonly API calls; property permission siteOwner. No new credential/access grant, no secrets logged. URL Inspection: Services unknown to Google; fridge/freezer/cold-room London slash URLs PASS, Submitted and indexed. Requested Services indexing through Search Console; Google completed its live check and confirmed Indexing requested/priority crawl queue. Request accepted does not mean indexed; do not repeatedly resubmit it.
Google processes submitted sitemaps periodically. No new recurring automation created in this session. API read/report access works. Existing tools/request_indexing.py and agent/scripts/bulk_request_indexing.py use Indexing API for ordinary repair URLs; do not execute them for these pages. Official API eligibility is JobPosting or qualifying BroadcastEvent in VideoObject, not service pages. Next integration task is to replace unsupported notification calls with sitemap submission and URL Inspection reporting, preserving any existing scheduler after inventory review.
Evidence: local gsc-connection-result.json, gsc-sitemap-submitted.jpg, gsc-services-indexing-requested.jpg and gsc-report-fa.md. Post-release memory retained on ai/seo-canonical-sitemap; no documentation-only main deployment.

## 2026-10-07 — Daily Search Console monitoring active
Existing GSC service account reused with webmasters.readonly. No new access/key or unsupported Indexing API call. Codex automation colddirect-google-indexing-check is ACTIVE, daily at 09:00 Europe/London, in the existing chat. It executes the local C:\Users\khora\Documents\Codex\2026-10-07\c\gsc-monitor.py and compares completed snapshots in reports/gsc-monitor. Reports meaningful index/sitemap/API changes in Farsi; stays quiet on unchanged state. Google already accepted sitemap submission and Services indexing request; do not repeatedly submit it.
First full manual monitor run passed on 2026-10-07: 112 sitemap URLs, PASS=57, NEUTRAL=55. This is a first baseline, not newly gained rankings/indexation. First scheduled run is unverified. Local machine/app and required permissions/network must be available for future runs.
Alert checks pass for unchanged state, newly indexed page, loss of indexing and first baseline. An initial sequential run was stopped after 25 inspected URLs due to latency; no partial baseline was saved. Final implementation uses four independent HTTP clients with 30-second timeouts, bounded retries and writes only after all inspections succeed. Routine last-crawl timestamp changes do not trigger alerts. No production edits/deployment performed. Preserve existing Hermes/GitHub scheduled jobs; inventory found no existing Codex automation directory.
Next P0 website work remains the blog repair-cost redirect loop and brands canonical 404; monitoring is not their repair. Existing bulk Indexing API scripts are not invoked and still require separate correction/inventory before use.
