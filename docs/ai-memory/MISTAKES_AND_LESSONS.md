# Mistakes and lessons

Always read the complete root LESSONS-LEARNED.md before similar work. It contains the
full evidence and subsequent corrections; this file does not replace it.

## Carry-forward safeguards (2026-10-07)
- Metadata insertion scripts previously corrupted 28 files by applying substring offsets
  to full HTML. Test edits in isolated copies and validate actual resulting markup.
- Legitimate protected title changes repeatedly caused false page-protection failures.
  Update protected-pages.json fingerprints with the content change, after verifying intent.
- Multiple SEO Draft root-cause claims were later disproven. Do not repeat disproven
  remedies or treat a plausible explanation as confirmed. Latest bounded-call mitigation
  still needs a genuine scheduled-run success.
- /services/ routing remains an open issue with prior redirect-loop risk. Inspect HTTP
  responses and configuration evidence before editing web.config.
- Older deployment and schema notes conflict with current workflow/live observations.
  Date every baseline and verify the authoritative deployed copy before editing.
- All-pages-WEAK in an audit report is not proof that all content needs rewriting.
  Validate detection logic and sample real files before feeding an automated backlog.
- Zero impressions do not imply position 0; small-sample rankings are unreliable.
- A tool failing to fetch the site/robots is not evidence of production downtime.

No new production mistake, failed content experiment or regression was introduced
or fixed in this onboarding session.

## 2026-10-07 — Diagnose all active rewrite files, even on IIS
The earlier Services investigation searched web.config and missed the explicit
.htaccess home redirect. The live IIS/Plesk response changed immediately when that
rule was corrected. Server headers alone do not establish which rewrite configuration
is active. Guard services/index.html before the generic HTML redirect; default documents
can re-enter rewrite handling. Test fresh HTTP responses and query URLs when a browser
has cached a permanent redirect. Do not replace live configuration with a stale mirror.

## 2026-10-07 — Crawl policy continuation and current status
Named robots groups do not inherit wildcard exclusions. Test both named bots and unknown bots, utility aliases, public routes and assets. A robots exclusion controls crawling and does not secure a file or guarantee deindexing. The earlier PR #15 rejection record was historical: the user explicitly approved deployment and merged it; deployment and ten live checks passed. Do not carry that old pending status forward as current.

## 2026-10-07 — Sitemap inventory correction
PR #14 was explicitly approved, merged as 9453f995 and successfully deployed; 112 live robot policy checks and ten route checks passed. This supersedes earlier pending approval notes.

Fresh live sitemap: 362 entries, all unique: 226 redirects, 132 HTTP 500, two HTTP 404, two HTTP 200; those two declare other canonicals. The existing generator walked mirrors/internal repository paths and advertised raw .html/index.html aliases. Replaced it with public canonical discovery, robots/noindex filtering, live redirect/canonical resolution, deduplication and fail-before-write on transport/429/5xx. Both sitemap copies are identical. Daily workflow now stages the root sitemap it actually generates. Unverified lastmod dates omitted rather than marking every page freshly changed each run.

Prepared sitemap: 112 unique URLs, all freshly checked HTTP 200 with no noindex. Four focused regression tests pass. This is discovery-list cleanup, no page deletion or route/content change. No search ranking/indexation gain claimed; production release is pending. Some served pages declare a bare canonical that redirects to their slash URL; normalized served URLs are listed, while metadata consistency remains a separate task.

Next P0 routing investigations: /blog/commercial-fridge-repair-cost-london/ and its .html alias redirect to each other; /refrigeration-brands-repair-london/ returns 404. Both are excluded from this sitemap, not deleted. Recheck current policy before fixing routes. Also retain the current public ASP canonicals for chiller/ice-machine pages pending a separate canonical review.

Local tooling lesson: importing agent.scripts collided with root agent.py and ran its HTML generator inside an isolated archive. Restored all archive HTML and removed exactly the six newly generated files; no production or repository HTML changes are included. Import script modules by explicit file path in tests. Workspace-local temporary test directories avoid sandbox temp write restrictions.

## PR16 release complete — 2026-10-07
User explicitly approved PR16 merge and Plesk release. Merge 500634e3dda456d27b04e1d178f9785ff90dddc8; deployment run 37652640835 completed successfully. Live map matches approved 112 URLs; all return HTTP 200 without noindex. Ten core route/Services content and 112 robots policy checks pass. Earlier pending/rejected release notes are superseded. No Google ranking/indexation uplift measured. Next daily scheduled run is unverified. Post-release memory is committed on ai/seo-canonical-sitemap to avoid an additional documentation-only production deployment.

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
