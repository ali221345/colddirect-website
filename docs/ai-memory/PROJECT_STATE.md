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

## 2026-10-07 — Coordinated technical audit and first team repair
User authorized teamwork and automatic continuation. Head agent coordinated read-only workflow inventory, implementation and independent routing review. Existing GitHub writers: sitemap/robots02:00UTC, dailySEO05:00UTC, protected-page restore05:45UTC, root deploy on main/master push. Hermes evening schedules are documented, not fresh scheduler proof. Do not add a competing production writer.
Daily existing heartbeat colddirect-google-indexing-check updated ACTIVE at09:00London, name ColdDirect website SEO and engineering. It runs local website-health.py and gsc-monitor.py independently, reports meaningful changes/errors in Farsi, and can research/prepare isolated tested P0/P1 PRs with independent specialist review. It does not publish/merge unattended and must respect access/approval boundaries. First scheduled run remains unverified.
Public technical audit:112sitemap URLs,120unique requested paths;14issue records:three aliases of one cost redirect loop, brands404, nine bare/slash canonical inconsistencies, news missingH1. Eight fixturetests pass. Known Services/index.html canonical alias explicitly handled. Initial Accept header omitted the server XMLtype and was fixed to */*; no incomplete snapshot saved. Earlier falseServices canonical issue was audit correction, not website improvement. Snapshot currently at workspace reports/website-health/latest.json. PHP/operational routes excluded; reviewed publicASP canonicals only. Fourworkers30sec/2MB/samehost/8redirecthop bounds; transport/prerequisite failures preserve prior complete baseline.
Prepared PR18 https://github.com/ali221345/colddirect-website/pull/18 commit32a016383e7807ec6f581d5c2208143c296cc8de: exact cost article HTML pass-through, bare301slash, slash internalHTML; remove conflicting later external redirect in both existingconfigs. Article canonical slash retained; HTML alias200; otherrules/pagecontents untouched. Independent204 limited rewrite-modelchecks pass, reproduce oldcycle and preserve unrelated directives. This is not actualApache/IIS proof. Production verification GET/HEAD/queries/pageidentity/canonical/JSONLD/HTTPS/core/directoryblogs pending.
Automatic approval review rejected PR18 merge because it triggers Plesk/GitHub productiondeployment and exactapproval is missing. No retry, bypass, deployment or livefix performed. Requires specific userapproval before productionmerge; unaffectedmonitoringwork completed. Brands404 remains next separateP0. No ranking/indexationuplift claimed. Currentteam SOP is docs/website-team-guide-fa.md (workspacecopy alsoactive).

## 2026-10-07 — PR18 production release complete
User explicitly approved the exact PR18 productionmerge after automaticreview rejection. Verified unchanged approvedhead32a0163; merged6d0a4570e7f8c86876e0bade9fe2522c37efd777. Deploy run37663467843 completed success. This supersedes the earlier blocked/pendingPR18 status; do not retry completedfix.
Live cost canonical slash200; HTMLalias200canonicalslash; bare301slash. GET/HEAD/plainqueries/articleH1/canonical/JSONLD and hostingHTTP-to-HTTPS verified.24releasechecks pass with two separatelyrecorded limitations: barealias GET/HEAD doubleescape percentencodedquery %2F→%252F. Ordinaryquerypreserved. Ten separateServices/corechecks pass; both legacydirectoryblogs200. No pagecontent/price/titlechanges. Two outdatedIISredirect explanations remain visible inarticle, separatecleanupcandidate.
Complete publichealth audit120URLs confirms all threecostloopissuesresolved;11recordsremain: brands404, ninebare/slashcanonicalmismatches, newsmissingH1. Currentmapstill112; verify nextactualgeneratorrun includesrestoredcostcanonical, do notclaimdiscoveryupdateyet. No ranking/indexationupliftclaimed. Browserproof reports/repair-cost-live.jpg; reportrepair-cost-report-fa.md; detailedreleaseverification JSON retained.
Existing09:00Londonheartbeat updated to completedPR18status and nextbrandsP0; firstscheduledrunstillunverified. PreserveHermes jobs. Releaseevidence/memorycommitted on monitoringbranchPR17 to avoid documentation-onlyproductiondeployment.

## 2026-10-07 — Public 404 repair prepared
User requested any404fix. Read currentmemory, main6d0a457 and openPRs. Live bounded one-levelaudit253URLs:215HTTP200,38HTTP404, no otherHTTP/transport/loops, no inventorytruncation. Sixpublic404routes: brands slash plus fivebarealiases. Remaining32 are relativeanchorURLs within previewhomepage.
Restore exactexistingroot brandsHTML at root/mirror directoryindex, preserving content/title/H1/slashcanonical/schema/assets. MirrorrootbrandsHTML absent, so copyroot source. Exactdirectoryindexexception before genericHTMLredirect in bothApachecopies. Physicalfolder bypasses existingIIS !IsDirectory ASPfallback; no protectedpageentry.
Five exact bare301aliases in currentIIS/Apachecopies: appliances/catering/chiller-repair-london ->same slash; bottle-cooler-repair ->bottle-cooler-repair-london/; display-fridge-repair ->display-fridge-repair-london/. Alltargets freshly200/selfcanonical. GenericIISbrandrule sent firstthreebare names toward nonexistent *-fridge-repair-london.asp. OnlytwoIISwhitelistrules added beforeit, explicitquerypreservation; allotherXMLnodes/order preserved. ExistingchillerASP/core/cost/Services untouched.108 independentstaticchecks pass; serverreleaseproofpending.
Previewindex changes only32 provenbrokenanchorhrefs; all32destinations freshly200, reverseexacthrefchanges recoversoriginaltext/assets/otherlinks. No mirrorpreview sourceexists. Knownfreezer-room-north barecanonical301 resolves servedslash; usethatservedURL withoutchangingmetadataissue. OldunlinkedpreviewURLs maylegitimatelyremain404; no broadredirectorpage deletion.
Prepared ai/seo-public-404-repairs. No livefix or ranking/indexationgain yet. Release requires GET/HEAD/query/identity/schema/HTTPS/core plus fullboundedlinkaudit. Dailyheartbeat changed by explicituser to21:00Europe/London startingtonight; earlier09:00notes superseded; firstscheduledrun unverified. PreserveHermes jobs/approvalboundaries.

## PR19 production release gate
PR19 https://github.com/ali221345/colddirect-website/pull/19 prepared;108staticchecks and32livepreviewdestinationchecks pass. Automaticapprovalreview rejected mainmerge because it triggers automaticproductiondeployment with routing/content changes and specificPR19 releaseapproval is missing. No merge/deployment/bypass performed. Requestexactuserapproval; afterapprovalverifyunchanged sourcehead thenreleaseGET/HEAD/chains/queries/brandsidentity/schema/core/cost/Services and rerun253URLboundedlinkaudit. Do not duplicate existingPR19.

## 2026-10-07 PR19 released; Liebherr follow-up prepared
User specifically approved PR19. Head471000b8b54377d76bacc384afd6ff9a8e1ed383 merged as827b9161aa541678cb0a003f3cb8382ceea4b4e4; production workflow37666137427 succeeded.63 live release checks passed; Services10 and cost24 regression checks passed. Existing encoded-query cost limitation remains separately recorded. Post-release bounded internal link audit checked222 URLs:221 HTTP200, one HTTP404 at /liebherr-fridge-repair-london/ linked by the restored brands article. Inventory changed from253; this is not a full-site crawl or indexing/ranking claim. PR19 pending-release notes above are historical and superseded.
Follow-up branch ai/seo-liebherr-404 restores existing mirror Liebherr content in root/mirror HTML and directory index (only stylesheet/script paths gain leading slash), copies existing image blob5fa6655a8eac924e025a54dba7dd8e81122b9fc4 to root, and adds only two exact Apache exceptions in both configs.24 independent static checks pass. No new claims or image generation. Live verification required after approved release: slash/index200, bare/HTML redirects, queries/HTTPS, image/assets, canonical/H1/JSON-LD, protected services/cost/brands and bounded link audit. Daily heartbeat remains21:00 Europe/London; first scheduled run unverified. No unattended production merge.

## PR20 approval gate
PR20 https://github.com/ali221345/colddirect-website/pull/20 prepared;24 static checks and Git-tree page/image/config fixture identity checks pass. Automatic approval review denied production merge because the user approved PR19, but has not specifically approved PR20's automatic production release. No deployment or bypass occurred. Obtain exact PR20 release approval, then verify unchanged head and run live checks. Existing daily heartbeat now records PR19 completion/PR20 pending and independently runs the tested bounded internal-link audit along with website/GSC monitoring;21:00 Europe/London ACTIVE, first actual scheduled run remains unverified. Supersedes older pending PR19 notes.

## 2026-10-07 PR20 approved, released and verified
The user specifically approved PR20 head56d34456d9aa1d1fec077c5b1bc89c8bf311d2aa. Merged as51eb8251e3a2c1dd60bbc3707f9bee806507e914; Plesk workflow37668372434 completed successfully.20 live Liebherr route/identity/assets checks passed: slash/index200, bare/HTML301 chains, ordinary queries retained, HTTP->HTTPS, canonical/H1/valid JSON-LD, CSS/JS200 and published image byte-for-byte existing Git blob5fa6655a8eac924e025a54dba7dd8e81122b9fc4. PR19 live regressions63, Services10, cost24 passed. Previously recorded encoded-query cost limitation remains; not counted as passes.
Post-release same bounded internal-link inventory:119 seeds,203 discovered checked,222 total;222 HTTP200, zero404, no truncation/transport failures. This verifies discovered public links, not all possible URLs or indexation/rank changes. Earlier pending PR19/PR20 notes are historical and superseded. Browser proof reports/liebherr-live.png and local reports/liebherr-release.json. Daily21:00Europe/London heartbeat ACTIVE now records completed releases and independently runs health, GSC and bounded link audit. First actual scheduled run remains unverified. Check next real sitemap generation discovers restored cost/brands/Liebherr canonicals before claiming sitemap updated. Preserve Hermes, avoid unattended releases or repeated index requests. PR17 remains draft tool/memory source only; updating its branch does not request a production merge.

## 2026-10-07 Restored discovery and indexing follow-up completed
Read-only targeted GSC inspection: all three restored URLs absent from112-URL live map. Cost canonical PASS/Submitted and indexed, Google/user canonical match, lastCrawl2026-09-05; brands and Liebherr NEUTRAL/URL unknown. Current sitemap submission pending with0errors/warnings and stale prior downloaded counts; not proof of current indexation. Manual Request indexing accepted in GSC UI for brands and Liebherr on2026-10-07 after live eligibility testing; cost already indexed, no duplicate request. Never repeat accepted requests or use Indexing API for normal service pages.
Prepared PR21 adds exactly3 verified direct200/selfcanonical/robots-allowed/non-noindex URLs to both maps, no removals or fabricated lastmod. Fixed shell CRLF output normalization before approval; final diff9 added lines/0deletions per map. Auto-review initially denied production merge; user specifically approved afterward. Head872c328856bf0f5eb46e1536cacd17a52ac5ebd0 merged5309e3dc05bcf3849ac9468fb3c5816d4bc46712; deployment37670183080 completed/success. Live map115uniqueURLs, every listedURL200, exactly3new entries/0removals. Fullhealth121checks retains10 existing canonical/newsH1 records, no new regressions. docs/indexing-report-fa.md and local reports/restored-indexing.json/restored-sitemap-release.json/brands-index-request.png/liebherr-index-request.png hold evidence. Existing pending sitemap submission not duplicated. Next scheduled generator must retain all3 now available root canonicals; preserveHermes writers. Daily21:00London heartbeat updated to watch actualGSCstatus of these now-listed URLs, remainquiet unchanged; firstscheduledrununverified. Indexing queue acceptance is not indexed/ranking gain. Pending-map notes above superseded. Next P1 is existing canonical mismatch/newsH1 cleanup; inspect before changing.

## 2026-10-07 Final GSC evidence supersedes pending indexing
Complete115-URL GSC snapshot successfully saved:60PASS/55NEUTRAL, preserve as new monitoring baseline. Exact3targets now PASS/Submitted and indexed with Google/user canonical matching: brands lastCrawl2026-10-07T18:52:00Z, Liebherr18:54:01Z, cost2026-09-05T17:56:27Z. Direct earlier3target inspection showed brands/Liebherr unknown; thus their transition to indexed is confirmed from actual API data, not queue acceptance inference. Earlier unknown/pending statements above are historical and superseded. Broader57->60PASS comparison changes inventory112->115, so don't use it as rankings/click growth. PR21 approvedsuccessfulrelease,115mapall200, UIacceptedrequestsalreadyrecorded. No repeated indexing requests. Updated Persian report and21:00heartbeat record indexed status. UI inspection pages may retain old result IDs; re-inspect to retrieve fresh data rather than RequestAgain.
