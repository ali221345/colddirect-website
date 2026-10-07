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
