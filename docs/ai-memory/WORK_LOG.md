## ⛔ DO NOT REPEAT — COMPLETED & LOCKED MILESTONES (AS OF OCT 2026)

Read this section first. Then run `python tools/check_locked_state.py`. If a milestone prints LOCKED, skip it. These are finished and live on https://www.colddirect.co.uk/. Rebuilding them wastes a ranking cooldown.

### LOCKED #1 — 9 Money Pages V4.7/V4.9 Domination (PR #81 merged 2026-10-20 09:07 UTC, PR #82 merged 2026-10-20 09:38 UTC)
Homepage `/` plus the 9 money pages are optimized and were re-audited live on 2026-10-21 (10/10 HTTP 200):
`/fridge-repair-london/`, `/freezer-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`, `/cold-room-repair-london/`, `/catering-repair-london/`, `/commercial-appliances-repair-london/`, `/air-conditioning-repair-london/`, `/cellar-cooler-repair-london/`.
In place: exact-match titles, CTR meta descriptions, `CD-HERO-KEYWORD-MATRIX`, `CD-9-MONEY-TECH-MATRIX-V47`, `CD-9-MONEY-KEYWORD-SILO-V47`, homepage `CD-HOMEPAGE-6-BLOG-HUB`, descriptive image `alt` text, and `#business` JSON-LD (`HVACBusiness` + `LocalBusiness`).
**Indexing cooldown is active until 2026-10-31. Do not re-edit `<title>`, `<h1>`, or meta descriptions on these 10 pages.** A title change after that still goes through `tools/money_data.py` only, and only when the owner names the page.

### LOCKED #2 — Single-hop 301 trailing-slash redirects (commits `87e96a0` and `5aad3d0`, deploy 39588254766 passed on attempt 1)
All 117 top-level directories are classified. 102 bare URLs that answered HTTP 200 now 301 in one hop to their own slash folder (explicit rule per slug in `.htaccess` and `web.config`, root and mirror). 8 already 301'd to their own slash, including fridge, freezer, and williams from `87e96a0`. 7 must stay pointed somewhere else so they do not become a second hop: `about` -> `/about-us/`, `news` -> `/blog/`, `cold-room-repairs-london` and `walk-in-cold-room-repair-london` -> `/cold-room-repair-london/`, `commercial-dishwasher-repair-london` -> `/commercial-catering-repair-london/`, and the three bottle-cooler aliases -> `/bottle-cooler-repair-london/`.
Verified: `config_parity` 371 rules, 746 probes, 708 one-hop 301s, 0 chains. Live smoke test 895 probes, `ALL PASSED` on attempt 1.
**Do not rewrite `.htaccess` or `web.config` redirect rules unless the owner explicitly asks for a named redirect change.**

### LOCKED #3 — Automated background pipelines
`auto-seo.aspx` V4.9 (key in `App_Data/auto-seo.key`, never printed), the 24h workflow `auto-seo-nightly.yml`, the 48h workflow `site-backup-48h.yml`, and `tools/live_production_audit.py` are on `main` and were in sync with live Plesk `/httpdocs` on 2026-10-21 (pull reported 0 diff). Do not rebuild them.

---

### [2026-10-23] — Top-right welcome audio sole player + 30+ years body copy
- **Summary**: Unified `CD-TOP-RIGHT-AUDIO` (`/audio/colddirect-welcome.mp3`) as the only visible player sitewide. `CD-AUDIO-V1` is now schema-only (hidden transcript + AudioObject/Speakable). Body/trust copy 15+ years became 30+ years. Updated `seo_integrity_check` / smoke to expect welcome embed + hub schema stem.
- **SEO safety**: title/H1/meta/canonical/redirects/sitemap 122 untouched; all 3 locks intact; protect check OK.
- **Git**: `0f614b6` (audio+years) + `1f85399` (integrity align). Deploy `39924845031` success.
- **Live verify (5/5)**: `/`, `/commercial-fridge-repair-london/`, `/fridge-repair-london/`, `/commercial-freezer-repair-london/`, `/cold-room-repair-london/` → TOPRIGHT=True, no Listen mid-page, no V1 audio tag, no 15y, 30y present.

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

## 2026-10-07 PR22 canonical and news follow-up prepared, not released
Fresh health121paths/map115 reconfirms9canonical_mismatch and newsH1record, no new regressions.9rootservedindexfiles declarebareURLbutbarealiasesredirectto servedslash.17rootHTML/indexcanonicaltag edits only; correct mirrorcanonicals untouched, differing title/content versions preserved. No protected-pages entry matches these changedpages; all titles/text/schema/assets preserved. RawOG/schemaURLvariants intentionally out of scope.
NewsrootHTML/index423byte stub has0secondmeta-refresh/blog butcanonical/news; mirroralready/blog. Rather than addfakeH1, prepareexactHTTP301news/newsslash/news.html/news/index.html->https://www.colddirect.co.uk/blog/ in2Apache(beforegenericHTML) and2IIS(firstbeforehtmlpass-through) configs, preservequeries. Align2rootstubcanonicals only; preserverefreshfallback. Removeonlynewsaliasfrom2maps115->114;blog/restoredindexed3 remain. No page deletion or unrelated directives changed.
PR22 https://github.com/ali221345/colddirect-website/pull/22 branchai/seo-canonical-news:25productionfiles.118staged/static+freshpublicdestinationchecksPASS;independentreview110staticchecksPASS. Routing model not actualdeployment. Automaticapprovalreview denied productionmerge becauseexactPR22releaseapprovalmissing; no publication/bypass. OnapprovalverifyheadthenGET/HEADall9selfcanonicals,4newsvariantsone301withqueries+HTTPSblogidentity/schema,114mapall200,Services/cost/brands/Liebherr andboundedhealthaudit. Prior indexingstatus3PASS remains confirmed; no repeatrequest. Daily21Londonheartbeat mustnotduplicatependingPR22.

## 2026-10-07 Mobile navigation and honest booking confirmation prepared
PR22 already released as ee7c5848f3291299ad58470f8f44ab830188d079; deployment37672669674 succeeded. Live map114, health120 checks/0issues, bounded links221/221 HTTP200 and zero404. Prior PR22 pending notes are superseded.
Live mobile homepage/contact reveal hidden .cd-nav with no menu toggle, and booking modal z60 obscured by sticky header99. All four booking JS copies report success/reset on HTTP rejection or malformed response and report success on network failure. Backend JSON contract requires boolean ok true; no real booking POST or operational endpoint invoked.
Prepared 10 targeted root/mirror frontend files: mobile Menu with aria-controls/expanded and Escape/focus; mobile Services/Brands links navigate hubs while desktop/tablet dropdowns remain; responsive logo/navigation sizing; modal z1000 above header; only successful HTTP plus JSON boolean ok:true confirms/reset. Failure shows safe retry/telephone message and retains fields. Distinct mirror header content preserved.
Independent actual-JS mocked/static review300 checks passed, including four booking copies and accepted/rejected/HTTP/nonJSON/empty/null/truthystring/network/validation scenarios, mobile/desktop/legacy nav and both inline headers. Local preview server could not be reached from shell/browser; staged visual verification is NOT claimed. Deployment browser/mobile geometry/focus/routes still requires verification; backend email delivery is untested.
Google PageSpeed mobile lab baseline7Oct: homepage20:20London performance99,FCP0.9s,LCP2.0s,TBT0ms,CLS0,SI2.2s; contact20:27London performance67,FCP3.0s,LCP5.4s,TBT310ms,CLS0,SI3.7s. Both MotoGPower/Lighthouse13.5.0/Slow4G, no CrUX field data. API429 fallback to public UI succeeded. No measured ranking/conversion improvement or field CWV pass claimed. Contact performance/third-party map cost is next separate investigation, not a proven root cause yet.
Branch ai/cro-mobile-booking is isolated; production release pending exact approval if required. Preserve all routing, metadata, claims, Hermes writers and accepted GSC indexing requests. Daily heartbeat21:00 Europe/London; first actual scheduled run still unverified.

## PR23 release gate
PR23 head52d3fa624d57e36a9f47c79ec7f8d9649cde0e11 prepared. Automatic approval review rejected production merge because exact PR23 owner approval is missing and staged visual verification is incomplete. No merge/deploy/bypass.300 independent checks passed; local mobile-booking-report-fa.md and screenshots reports/mobile-booking-before.png/mobile-speed-home.png/mobile-speed-contact.png hold evidence. Existing21:00London heartbeat records PR23 pending and must not duplicate it. First scheduled run remains unverified.

## 2026-10-07 PR23 approved and released; visual validation remains limited
User explicitly approved exact PR23 release after gate. Verified head4034de2cf81f998f67d023d9dcf53e89c3b82b51/baseee7c5848 unchanged; merged3f5afa38c14b2b8f4ea18f57fbe968fc4561cc4d. Plesk workflow37676548949 completed/success. Earlier pending approval notes superseded; do not retry completed merge.
Four public JS/CSS assets freshly GET/HEAD200 match approved tested source after CRLF normalization; seven public/core/contact/service/brand paths200 and served header contains the approved mobile dropdown guards. Full health114map/120paths zeroissues/no new or resolved issues.300 independent pre-release mocked/static checks already passed, no real bookingPOST. Form email delivery remains untested.
IAB continues displaying pre-release resources: no Menu and computed modal60 despite server CSS1000 and public JS containing Menu code. Normal reload and documented hard-reload attempt did not refresh them; direct JS navigation blocked by client; separate Chrome unavailable. This suggests browser cache/resource-access limitation, not proven root cause. DO NOT claim live visual interaction PASS or all user browsers fixed yet; fresh-browser visual mobile/desktop/menu/modal verification remains open, and investigate versioned assets if cache persists. Do not bypass browser policy or change browser security settings.
Current local evidence reports/mobile-booking-release.json plus updated mobile-booking-report-fa.md. Contact speed baseline67/LCP5.4s/TBT310ms, homepage99/LCP2.0s, no field data or ranking gain. Preserve Hermes writers and daily21:00Europe/London monitoring; first actual scheduled run still unverified.

Fresh independent Google PageSpeed contact report20:49London https://pagespeed.web.dev/analysis/https-www-colddirect-co-uk-contact/ui9ljt4yrb?form_factor=mobile renders the new compact logo and Menu button in its Final Screenshot, confirming fresh mobile header render separately from stale IAB resources. Lab performance100,FCP0.8s,LCP1.5s,TBT0ms,CLS0,SI1.9s. Earlier contact67 run differs; no targeted speed change and only one post-release run, so do not attribute a stable performance gain to PR23. Actual menu clicks/Escape/booking overlay remain mocked only until fresh interactive browser validation.

## 2026-10-07 First scheduled heartbeat completed successfully
Automation colddirect-google-indexing-check actually dispatched at2026-10-07T20:02:21Z (21:02London). All three independent monitors completed: publichealth114map/120paths zeroissues and no new/resolvedchanges; boundedlinks119seeds/203discovered/221checked allHTTP200, zeroerrors/truncation; GSC114URLs PASS60/NEUTRAL54 and changes[].
Previous GSC inventory115 had60PASS/55NEUTRAL; current114 removal is the planned newsalias fromPR22. Difference in NEUTRAL count reflects inventory change, not a matched indexing gain. Brands/Liebherr/cost remain PASS/Submitted and indexed. No indexing/sitemap submission or production edit/deployment occurred.
First website attempt failed transport with no baseline overwrite. Network permission then granted for this turn; retry succeeded; GSC/link jobs ran independently and completed. Future local runs still require computer/app/access/network availability; this one successful execution does not guarantee unattended future permission grants. Earlier firstscheduledrun-unverified notes are historical and superseded. Keep daily21:00Europe/London and stayquiet on unchanged future runs.
PR23 release remains completed; independent Google screenshot confirms fresh Menu render, but fresh interactive menu/modal/email delivery checks remain open due known IAB old-resource/access limitation. Do not repeat blocked browser work without a changed condition or bypass its policy. Local nightly report reports/heartbeat-20261007-fa.md records actual run. No ranking/conversion claim.

## 2026-10-07 Booking backend acceptance follow-up prepared
PR23 frontend release remains complete. Current main3f5afa38 has booking.asp root/mirror identical, On Error Resume Next and unconditional final ok:true even if both persistence writes, notify and mail all fail. This is a proven source control-flow defect, not evidence that production delivery currently fails. No real bookingPOSTs performed.
Isolated ai/cro-booking-acceptance prepares same targeted source in root/mirror. Track accepted=False; log/JSON storage requires immediately captured WriteLine success and successfulClose; notify requires setup/send/getter success+HTTP2xx; mail requires configuration/send success. Any accepted channel retains existing success wording; if none accepted, return503/JSONokfalse before final response. Existing honeypot/GET/OPTIONS/validation/payload/privacy/notification/config/log paths preserved; no new credentials or destinations. Acceptance is storage/provider handoff, never inbox-delivery proof.
Independent review15staticinvariants and2816contractmodelcombinations passed. Installedcscript could not load settings (accessdenied), so actualASP/VBScript runtime is UNVERIFIED; model is not server proof. All15If/EndIf blocks balanced. Existing300frontendchecks rerunPASS; serverassets4 and7paths freshlyverify unchangedapprovedPR23. CurrentIAB stillnoMenu/modal60; local preview withTTYserverstarted but localhost unreachable fromshell/browser. Do notbypass accessrules orclaiminteractivevalidationdone.
Owner asked which next and authorized starting follow-up. Exactproductionrelease of newbackendchange remains pending. Test-request draft prepared withTEST/do-not-call/do-not-dispatch message; owner's own email/phone requested, no reply yet and no realPOST authorized from placeholderdata. After approved release validate realASP response on explicitly approved single test only and confirm reception separately with owner. No realcustomerdata logs/files read.
First scheduled21:02London heartbeat already VERIFIED:114map/120healthzeroissues,221linksall200,GSC11460PASS54NEUTRALchanges[],3restoredindexed. Do notclaimranking/conversiongain orrepeatindexrequests. PreserveHermes writers, daily21London.


## 2026-10-07 PR24 approved and released
Owner explicitly approved exact PR24 after proposal and limitations. Verified head ccd958b1fff176c095022d5dea184493747108af/base3f5afa38c14b2b8f4ea18f57fbe968fc4561cc4d unchanged. Merged5b124dd1862236c8d96af5223b40e928270b9211; Plesk workflow37684950255 completed/success. Earlier pending approval notes superseded; do not repeat merge/release. Root/mirror booking.asp approved blobs identical51d9a4c97e5246c2231bff6a17fc0e5b9ca63942. Independent15static+2816contract model tests passed before release; actual ASP acceptance branch and email delivery remain UNVERIFIED. Public GET booking.asp200 returns ok:true/live:true, confirming basic endpoint runtime only, not request acceptance. OPTIONS observed200 empty body versus source204; no pre-release matched baseline, so do not label new regression or acceptance proof. No POST/customer data/mail operations performed. One intended read-only check initially failed due network access, then completed after renewed permission. Four frontend assets GET/HEAD200 still approved PR23 match and seven core pages200 (11checks). Complete health2026-10-07T21:02:24Z:114sitemap/120paths,zeroissues,no new/resolved. This is bounded health, not every URL, ranking or delivery proof.
Remaining: owner's own email/phone and approval of exact TEST/do-not-call/do-not-dispatch request before a single real delivery test; fresh interactive menu/modal validation still limited by stale IAB. Preserve daily21Europe/London and verified first21:02London heartbeat; no duplicate indexing requests, credentials, operational endpoints or writers.


## 2026-10-07 keyword performance research and bounded Services proposal
Owner requested keyword SEO and instructed autonomy for routine work, asking only on important matters. Read latest main5b124dd1862236c8d96af5223b40e928270b9211/open PRs, all six latest PR17 memory files and team guide before preparing. Real readonly Search Analytics web/final API collected complete bounded calls: current2026-09-07..10-04 vs previous2026-08-10..09-06, equal28days/PT. Totals585clicks/45925impressions vs295/80414. Queryrows3750/5109; no local10000row cap hit, but API top-row/anonymized limits remain. Not market search volume, fixed ranking or conversion data; period predates today's releases so no attribution.
Priority queries currentclicks/impressions: cold room repair london96/177; commercial fridge repair london43/192; commercial freezer repair london10/11(small); ice cream machine repair8/61; foster fridge repair3/24. Cold room repairs0/151 and commercial refrigeration london0/117 are subsequent intent opportunities. General types of ice1/653 and fridge brands0/534 not primary repair goals. UK query/page rows inspected separately; don't add page totals to property/query totals. Services itself0clicks/1impression, not proven high-traffic.
Prepared narrow3file change on ai/seo-keyword-service-links: rootservices.html andservices/index.html add five explained service links plusbrand/contact(7bodylinks) and replace one guidance sentence; preserved identical roots. Richmirroredservices.html kept intact excepticecreamlinkbullet. Titles,H1,canonicals,schema,claims,prices,JS,header,redirects preserved. Header already linked targets, so not new crawl-discovery proof. Independent36static checksPASS. Eightlivebaseline pathsall200withintendedcanonical; historicalcoldroom/icecreamroutesalreadyredirectcorrectly, don'tduplicatefix. Localreports/gsc-keywords/latest.json raw complete baseline and keyword-seo-report-fa.md methodology. No indexing request/realenquiry/credentials/writer executed. Keyword data baseline and navigation improvement do not prove SEO gain. PR24 alreadyreleased5b124/workflow37684950255success; do not repeat; acceptance/delivery test and freshinteractivefrontend remain unverified.


## 2026-10-07 PR25 routine keyword SEO released and checked
Within owner's direct keyword-SEO request and standing instruction to complete routine work without repeated approval, independently reviewed PR25 released. Finalhead175f547e3331cbe3c0e7fa3e0c6526e4dfcb32a8/base5b124dd1862236c8d96af5223b40e928270b9211 verified; merged66f1cd2a798e9c328bea6f0f4dc9a3ff942e31a2. Pleskworkflow37688011810completed/success. Independent36staticchecks passed before release. Twelve public live checks passed:3Servicesvariants show new service-selection section and7contextualbodylinks with originalH1/canonical;7linktargetsHTTP200;2historicaltrafficroutes reach intended destinations. Existingrichmirrorcontentpreservedexcept1icecreamlink. Earlier prepared/pending notes superseded; do not duplicate release. Saved reports/keyword-seo-release.json. Actualchange is contextual equipment selection; not newcrawl-discovery proof sinceheaderalreadylinkedtargets. No search/ranking/conversiongain measured. New readonly gsc-keyword-research.py stores complete boundedperformance baseline locally, preservessnapshot onfailure, onlywebmasters.readonlyscope. Performance28dayperiods Sep7-Oct4 vsAug10-Sep6 precedetoday'schanges. Keyword report nowreleased. Next: weeklyreadonlyrefresh (notmorethanonce7days) and compare matched28dayperiods/UKintent, choose subsequent bounded changes with evidence; donotmassrewritewinningcoldroomtitles/routes orinventprice/certifications/offers. No newautomation, daily21London maintained; preserveHermes andexistingwriters.


## 2026-10-07 exact fridge/freezer London keyword focus
Owner explicitly prioritised 'fridge repair London' and 'freezer repair London' with page-one goal. Read main66f1cd2a798e9c328bea6f0f4dc9a3ff942e31a2/openPRs/all6latestmonitor67ab memory/teamguide before coding. Existing complete GSC Web/final baseline Sep7-Oct4 vsAug10-Sep6: fridge27clicks187impressionsavg14.37 versus7/272/19.57; freezer22/89/16.97 versus0/119/29.53. UKhomepage fridge25clicksavg9.89/freezer10avg13.67; historical combinedalias freezer11/fridge2. Aggregate historical averages are not fixed page1proof; no marketvolume or releaseattribution. Preservehomepage andwinninglegacyroutes.
Public10-routebaseline allHTTP200;slashpagesexactkeywordrich,currenttitles/H1/canonicalalreadyappropriate. Livelead/body contradict hero+FAQcommercialonlypolicy with maybehouseholdcallout statements. Prepared boundedbody-onlyconsistency correction on ai/seo-fridge-freezer-intent,9served/sourcevariantfiles for2logicalpages. CanonicalfolderHTML/rootHTML/mirrors andsingularASPbodyedited. PluralASPsourcefilesare301redirects; existingwebconfig rewrites publicpluralpath tosingularASP; preservethem. Replaces contradictorydomesticacceptance sentences/headings withestablishedcommercialonlypolicy. Newserviceoffers/prices/certifications/responseclaims notinvented; existinghead/title/H1/canonical/schema/assets/anchors/phone/home/redirects unchanged. No repeatedkeywordparagraphs/newpages/indexrequests/writerchanges/realPOST. GSCsource and reportfridge-freezer-seo-report-fa.md retainlimitations. Routineworkauthorizedbyowner; independentreviewbefore release. This correctsintent/clarity, notproofpage1/ranking/conversiongain. Next priorityweeklymeasurementexact2queries andUKlandingrows, supportedbyread-onlyexistingresearchscript; preserve generalcommercialtargets and acceptedindexing.

Independentreview391staticchecks across9filesPASS; only7fridge/8freezerbodylines perfilechanged, head andmarkup attributespreserved. Inheritedschema'asdefaultdiary'qualifierwithin explicitNo/commercialonlyanswerunchanged; do notclaimallheadwordingrewritten.


## 2026-10-07 PR26 exact keyword intent correction released
Owner's standing routine-work authorization and explicit fridge/freezer SEO request used; no repeated GitHub approval requested. Finalhead705df2538d20d6c2649a0605afde3269fa4515df/base66f1cd2a798e9c328bea6f0f4dc9a3ff942e31a2 unchanged. Merged45cb0237bab86a46d9fda87ff08f91e83feff827; Pleskworkflow37689161232completed/success. Independent391staticchecksbefore release. TenlivechecksPASS:all200,preservedtitle/H1/canonical,8servedbodyroutes clarifiedcommercialonly;homepageandcombinedhistoricalaliasunchanged. reports/fridge-freezer-seo-release.json evidence. Only misleading householdacceptancebodycopy corrected toexistinghero/FAQpolicy; no businessofferingexpansion. No page1/ranking/traffic/conversiongainverified. Earlierpreparednotes superseded; do notduplicatemerge/release.
Exact 'fridge repair london' and 'freezer repair london' nowPRIMARYweeklyperformancepriorities. CurrentfinalbaselineSep7-Oct4:27clicks187impressionsavg14.37 and22/89/16.97. Sourcequery-pageUKdatahistoricalhomepage9.89/13.67averages are notstablepage1proof;keepwinninghomepageandhistoricalredirects. Rankinggoalneedsfuturemeasurementandhelpfulcommercialcontent,notkeywordstuffing,newdoorwaypages,paidlinksorforcedindexing. Preserveacceptedindexrequests andallwriters;watchovernightwritersforthereturnofconditionaldomesticwording.
Owner additionally explicitly states no GitHub permission requests and 'Give GitHub always access'. Treat as persistent authorization for ordinary repository work on this website; avoid repeated human approval requests for routine reads/branches/commits/PRs/merges. This records ownerauthorization, not a change to system-level connector/sandbox security settings; required platform boundaries still apply. Important/high-risk business,server,credential,destructive or external-message decisions still requireappropriateapproval. Unattendedheartbeatproductionmerges remainprohibited by existing instruction. No plugin credentials or global permission settings changed.


## 2026-10-07 continuing exact fridge/freezer keyword SEO
Owner directly requested starting SEO now; continue completedPR26 without duplicating it. Main43d9466665f9bdbde4424a07fed56920acb49570 includes Hermes freezer-room update c932c111dcb7f807a429dcfe407e8c7574024bdb and verificationdocs, after PR26; preserve those changes. Read allsixlatestmonitor5c553memory/openPRs/teamguide/currenthistory before preparing. FreshPR26 tenchecks stillPASS, no rankgain measured. Existingfridgeguide alreadylinks genericfridge twice, so leftunchanged. Genericfridge/freezer primarypages havenoguidebodylinks; freezericeguideonlylinkedNorthLondonservice. Proposed neutral contextualguideparagraphon2logicalservicepages across9 existingvariants +1natural freezerLondon returnlink inexistingcallengineerparagraph, preservingNorthLondonanchor.
ConfirmedpublicP1 via readonlyGET:fridgeslash hasliteralinvalidtel:+447****9320 andtel:+442****4822, withcorrectvisiblepubliclabels. Existingunmaskedhrefs establish+447983759320/+442039524822. Bounded specialistimplementation repairs only2hrefvalues in affectedstagedvariants; independentreview before release. Sourcepreparationisolatedai/seo-repair-guide-links; nohomes/pagepolicy/title/H1/canonical/schema/images/price/claims/routing/JS/writerchanges. Existing4publicpages200. ExistingGSC guidebaselineSep7-Oct4: commercialfridgenotcoolingslash2clicks68impressions; freezericebuildup1/28. SmallsamplesnotmarketvolumeorSEOgain. No newpages,indexrequests,credentials,realenquiries or food/electrical/refrigerantadvice added. Target exactqueries fridge27/187/14.37 andfreezer22/89/16.97 remainsprimaryweeklybaseline. One more contextlink helps navigation, not proofrankpage1. Keep quietonunchangedmonitoring.

Bounded specialistphoneimplementation8exacthrefrepairs4fridgeHTMLvariants completed; visiblelabelsandbeforefilesunchanged. Independent92checks all10filesPASS; reversingonlycontextlinks+8phonerepairsrecoversexactbeforebytes. Preparedforroutineowner-authorizedrelease; livechecksrequiredafterpublication.


## 2026-10-11 — Freezer repair London page cleanup prepared
Owner requested more SEO work for the exact freezer repair London query. Latest available GSC evidence is not a fresh 28-day pull: the 7-day report for 2026-10-04 to 2026-10-10 records 2 clicks / 8 impressions / average position 14.5 (small sample). Final 28-day report collected 2026-10-07 covers 2026-09-07 to 2026-10-04 and records 22 / 89 / 16.97. Its exact query/page rows show the old combined fridge-freezer URL (11 / 33 / 29.79), homepage (10 / 42 / 13.67), and old plural freezer alias (1 / 23 / 14.91); these predate recent route/content releases and are evidence of historical URL ambiguity, not a current matched landing-page baseline. Existing dedicated slash URL remains indexed (last inspected 2026-10-09); do not repeat its accepted inspection/index request.

Live /freezer-repair-london/ inspection found a visible internal design note (Navy buttons use #1B263B) and a 110-word paragraph repeating equipment, coverage, phone, brand, response and freezer-room details already presented in nearby sections. Removed only those two paragraphs from the served directory page and its root HTML, ASP, and excluded public mirror copies; retained title/H1/canonical, structured data, internal links, service scope, and all other text. Competitor review: Sun Meter Cooling’s commercial refrigeration and freezer pages separate equipment types and faults; we retain ColdDirect’s existing faults/brands/service detail without copying unverifiable claims. Independent source checks confirmed exactly one occurrence of each removed block in all four files before change and none afterward; no metadata, routes, claims, indexing, or writers changed. This is a readability/accuracy cleanup, not evidence of improved ranking. Recheck a matched query/page 28-day report after the next eligible weekly refresh.

## 2026-10-17 — Full Autonomous Multi-Workflow Setup, Bilingual Mobile Push & 48-Hour Backup
- Implemented the owner's 9 standing instructions for autonomous operation on `colddirect.co.uk`:
  1. Persistent memory recorded in `.cursor/rules/colddirect-agent-memory.mdc`, `docs/ai-memory/*`, and Cursor Personal AgentStore (`u420035230`).
  2. Multi-agent & automated tooling (`scripts/daily-seo-update.js`, `tools/daily_auto_seo.py`, `scripts/internal_linking.js`, `agent/scripts/protect_fixed_pages.py`, `tools/verify-production-pages.py`) integrated into daily GitHub Actions.
  3. Internal links, canonicals, and metadata optimized for Page 1 target queries (`fridge repair london`, `freezer repair london`, `freezer room repair london`, `commercial appliances repair london`, `chiller repairs london`).
  4. Upgraded `.github/workflows/colddirect-source-backup.yml` and added `tools/backup_plesk_live.py` to archive both Git source and live WHUK Plesk `/httpdocs` files every 48 hours with 90-day retention and mobile push notification.
  5. Added `tools/send_bilingual_report.py` and integrated it into `.github/workflows/colddirect-daily-seo.yml` to generate Persian + English reports (`seo-audit/LATEST-REPORT-FA-EN.md`), push notifications to mobile (`ntfy.sh/colddirect-seo-khora-8492`, Telegram, WhatsApp), and update a pinned GitHub Mobile Issue dashboard.

## 2026-10-18 — Phase 1 Top-3 Google Ranking Optimization & Cannibalization Cleanup
- Executed Phase 1 for the 4 near-Top-3 queries (`cold room repair london`, `commercial appliances repair london`, `freezer repair london`, `fridge repair london` / `commercial fridge repair london`):
  1. **Cannibalization & Redirect Fixes**: Fixed `.htaccess` and `colddirect-public-html/.htaccess` so plural URLs (`/cold-room-repairs-london`, `/commercial-freezer-repairs-london`, `/ice-machine-repairs-london`) 301-redirect directly to their canonical London hubs (`/cold-room-repair-london/`, `/commercial-freezer-repair-london/`, `/ice-machine-repair-london/`) instead of `-north-london.html`. Removed duplicate `/cold-room-repairs-london` from `sitemap.xml` and synced `web.config`.
  2. **Landing Page Upgrades**:
     - `/cold-room-repair-london/`: Updated `<title>`, `<meta name="description">`, `<h1>`, FAQ JSON-LD, and added a technical walk-in cold room fault & controller alarm section (`HA`/`Hi`, `P1`/`P2`, Dixell/Carel/Eliwell).
     - `/commercial-appliances-repair-london/`: Updated `<title>`, `<meta name="description">`, `<h1>`, FAQ JSON-LD, clean slash internal links, and first-visit diagnostic fault breakdown.
     - `/freezer-repair-london/`: Enhanced meta description, normalized all internal links to trailing-slash canonicals, and added commercial freezer controller alarm codes (`HA`, `P1`, `P2`, `dEF`).
  3. **Internal Link Equity Consolidation**: Updated `index.html`, `index.php`, `chiller-repairs-london`, `fridge-repair-london.asp`, and `freezer-repair-london.asp` so 100% of internal links point directly to canonical trailing-slash URLs.
  4. **Validation**: Passed `npm test` (426 files JSON-LD + 221 asset paths) and `protect_fixed_pages.py check` (12/12 protected files).

## 2026-10-18 — Phase 2 Brand Pages, Blog Link Equity & One-Hop Redirect Architecture
- Executed Phase 2 to consolidate brand/blog authority and eliminate multi-hop redirects discovered in live GSC 28-day page analytics:
  1. **Critical Bug Fix in `.htaccess`**: Moved the `# --- Core / nav ---` and `# Live blog` rewrite rules ABOVE the generic `RewriteRule ^(.+?)/?$ /$1.html [L]` catch-all so `/blog/<slug>/` routes and legacy blog redirects (`smeg-fridge-freezer-control-panel`, `samsung-fridge-freezer-not-freezing`, `best-ice-cream-makers`, `cold-room-troubleshooting`, `chiller-not-cooling`) execute properly instead of falling through to `index.php`.
  2. **One-Hop Brand & Service Alias 301s**: Consolidated all plural and legacy brand URLs (`wine-cooler-repairs-london`, `walk-in-fridge-repairs-london`, `liebherr-repairs-london`, `sub-zero-repairs-london`, `polar-repairs-london`, `foster-repairs-london`, `williams-repairs-london`, `william-fridge-repair-london`, `empire-repairs-london`, `koldbox-repairs-london`, etc.) into single-hop 301 redirects directly to their trailing-slash canonicals (`/williams-fridge-repair-london/`, `/foster-fridge-repair-london/`, `/commercial-fridge-repair-london/`, etc.).
  3. **Fixed Masked Phone Numbers on Williams Page**: Removed `tel:+447****9320` and `tel:+442****4822` from `williams-fridge-repair-london.html` and `williams-fridge-repair-london/index.html` (zero masked `tel:` links remaining in codebase).
  4. **Upgraded Phase 2 Service, Brand & Blog Pages**:
     - `/ice-machine-repair-london/`: Focused `<title>` and meta description on commercial ice machine repair (`Ice Machine Repair London | Same-Day 24/7 Commercial Engineers | Cold Direct`).
     - `/chiller-repair-london/`: Focused `<title>` and meta description on exact keyword `Chiller Repair London | Same-Day 24/7 Commercial & Rooftop | Cold Direct`.
     - `/commercial-freezer-repair-london/`, `/foster-fridge-repair-london/`, `/williams-fridge-repair-london/`, `/true-fridge-repair-london/`, `/gram-fridge-repair-london/`, and blog guides (`commercial-fridge-not-cooling`, `why-commercial-freezer-not-freezing`, `why-commercial-fridge-not-cold-enough`): normalized all internal links to trailing-slash London canonical hubs.

## 2026-10-18 — Phase 3 London Borough & North London Area Hub Optimization
- Executed Phase 3 across all 20 London Borough pages (`commercial-refrigeration-repair-<borough>`) and 10 North London Cold Room town pages (`cold-room-repair-<town>`), updating 90 files in total (`<slug>.html`, `<slug>/index.html`, and `colddirect-public-html/` copies):
  1. **20 London Borough Pages**:
     - Replaced generic `<Borough> Cold Chain Same-Day Repair | ColdDirect` titles with high-CTR `Commercial Refrigeration Repair <Borough> | Same-Day 24/7 | Cold Direct`.
     - Upgraded meta descriptions and JSON-LD descriptions/canonical URLs (added trailing slashes).
     - Redirected internal link equity from secondary `-north-london` aliases directly to the primary London canonical hubs (`/cold-room-repair-london/`, `/freezer-room-repair-london/`, `/commercial-fridge-repair-london/`, `/fridge-repair-london/`, `/commercial-freezer-repair-london/`, `/freezer-repair-london/`, `/commercial-appliances-repair-london/`, `/cellar-cooler-repair-london/`).
     - Normalized all 20 borough cross-links to trailing slashes (`/commercial-refrigeration-repair-<borough>/`) and fixed footer copyright encoding (`Â©` -> `&copy;`).
  2. **10 North London Cold Room Town Pages (`enfield`, `barnet`, `edgware`, `finchley`, `harrow`, `palmers-green`, `southgate`, `tottenham`, `wembley`, `wood-green`)**:
     - Replaced every instance of the legacy phone number `020 8050 2374` (`tel:+442080502374`) with the official London Office number `0203 952 4822` (`tel:+442039524822`). Verified 0 occurrences of `020 8050 2374` remain across all HTML files.
     - Converted plain-text service bullet items into rich contextual anchor links pointing to `/cold-room-repair-london/`, `/freezer-room-repair-london/`, `/chiller-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`, and `/cellar-cooler-repair-london/`.
     - Normalized all town cross-links and JSON-LD URLs to trailing slashes.
  3. **Validation**: Passed `npm test` (426 JSON-LD files + 221 asset paths) and `protect_fixed_pages.py check` (12/12 protected files).

## 2026-10-18 — Full Live Plesk `auto-seo.aspx` V4 Pull & Non-Conflicting Workflow Setup
- Pulled tonight's 20:21 (`08:21 PM`) `auto-seo.aspx` V4 live changes directly from WHUK Plesk FTP (`5.77.41.163`, `/httpdocs`) into the local workspace via `tools/pull_live_plesk_v4.py` and mirrored them to `colddirect-public-html/`:
  - Downloaded `auto-seo.aspx`, `sitemap.xml` (242 URLs with Priority 1.0 on Cellar, Catering, Cold Room, Commercial Fridge & Freezer), and all live `.html` and `.asp` files (`358` live root/subfolder files mirrored across `483+` total workspace files).
  - Verified 100% preservation of `<!-- AUTO-SEO-V4-2026 -->`, `<!-- AUTO-SEO-V4-SCHEMA -->`, `<!-- AUTO-SEO-V4-BLOGHUB -->`, V4 `<title>` / `<meta description>` / `<meta keywords>`, and image `alt` tags.
  - Updated `protected-pages.json` fingerprints to match `auto-seo.aspx` V4 titles (`Commercial Fridge Repair London | 24/7 Emergency Service & Repairs` and `Fridge Repair & Service London (2-Hr Emergency) | Commercial & Catering`) and `<!-- AUTO-SEO-V4-2026 -->`.
  - Excluded `auto-seo.aspx` and `sitemap.xml` in `.github/workflows/deploy.yml`, removed `restore-live` overwrites, and disabled conflicting scheduled crons in `.github/workflows/seo-agent.yml`, `.github/workflows/colddirect-daily-seo.yml`, and `.github/workflows/protect-fixed-pages.yml`.
  - Created root `.cursorrules` and updated `.cursor/rules/colddirect-agent-memory.mdc` with the 4 strict coexistence rules.

## 2026-10-18 — Core London Commercial Pages CRO, Body Content Depth & FAQ Accordion Upgrade
- Merged [PR #69](https://github.com/ali221345/colddirect-website/pull/69) into `main`, pulled the live Plesk `/httpdocs` state via `python tools/pull_live_plesk_v4.py`, and executed the 5 CRO & on-page authority deliverables across `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`, `/cold-room-repair-london/`, `/catering-repair-london/`, `/cellar-cooler-repair-london/`, and `/cellar-cooler-repair-london.asp`:
  1. **Above-the-Fold Emergency Dispatch Trust Bar (`<!-- CD-CRO-TRUST-BAR -->`)**: Added immediately below the hero section with `60–90 Min London Emergency Response`, `F-Gas Certified Commercial Engineers`, `24/7 Same-Day Repairs — All London Postcodes`, and direct click-to-call CTA buttons (`0203 952 4822` & `07983 759320`).
  2. **Body Content & Keyword Depth Boost**:
     - Added the 6-card "Common Commercial Breakdowns We Fix Same-Day" grid (compressors, evaporator fans, digital controller alarms `HA`/`Hi`/`P1`/`P2`/`dEF`, split door gaskets, F-Gas leak detection, condensate drains) + "Commercial Brands We Repair" strip (`Williams`, `Foster`, `True`, `Polar`, `Gram`, `Rational`, `Hoshizaki`, `Liebherr`, `Blizzard`, `Tefcold`) to Commercial Fridge, Commercial Freezer, and Cold Room pages.
     - Added dedicated H2/H3 trade sections for pub beer cellar cooling (`11–13°C` keg/cask temperature maintenance, remote beer line chillers, back-bar bottle coolers) and commercial catering refrigeration (prep counters, saladettes, blast chillers, undercounter chillers) to the Cellar and Catering pages.
  3. **Visible On-Page HTML FAQ Accordion (`<!-- CD-CRO-FAQ-ACCORDION -->`)**: Added 5 interactive `<details>/<summary>` trade FAQs per page right above the footer while keeping `<!-- AUTO-SEO-V4-SCHEMA -->`, `<!-- AUTO-SEO-V4-2026 -->`, `<title>`, `<meta description>`, `auto-seo.aspx`, and `sitemap.xml` 100% untouched.
  4. **Validation & Live Plesk Deployment**: Passed `npm test` (435 files, 0 errors), `protect_fixed_pages.py check` (12/12 OK), and `verify-production-pages.py` (4/4 PASS), and deployed directly to WHUK Plesk `/httpdocs`.

## 2026-10-19 — Pulled & Synced Live Plesk `auto-seo.aspx` V4.2 Updates
- Pulled `auto-seo.aspx` V4.2, `sitemap.xml` (498 URLs), and the updated freezer/service `.html` files from WHUK Plesk `/httpdocs` into the local workspace via `python tools/pull_live_plesk_v4.py`.
- Verified `auto-seo.aspx` V4.2 explicitly separates `commercial-freezer-repair` (`Commercial Freezer Repair London | 24/7 Emergency Freezer Service & Repairs`) and `freezer-repair` (`Freezer Repair London | 24/7 Same-Day Emergency Freezer Service & Repairs`), cleans UTF-8 mojibake on every run, and preserves all Cursor CRO Trust Bar and FAQ Accordion blocks.
- Verified `protect_fixed_pages.py check` (12/12 OK) and `npm test` (435 files, 0 errors).

## 2026-10-19 — V4.4 Deep GSC Keyword Mining, Dishwasher Exclusion, 18 Money/Brand Page Symptom Clusters & Blog Silo
- **Dishwasher Exclusion**: Redirected `/commercial-dishwasher-repair-london/` and `/dishwashers-london` (in `.htaccess`, `vercel.json`, and HTML meta/JS redirects) to `/commercial-catering-repair-london/` and excluded `dishwasher` URLs from `sitemap.xml` and `auto-seo.aspx` V4.4 (Cold Direct repairs commercial refrigeration & AC only).
- **Deep 90-Day GSC Keyword Mining (`2026-07-20` to `2026-10-18`)**: Extracted 710 queries in Positions 2–50 across 5 B2B intent buckets (Urgency/Near-Me, Symptom/Faults, Equipment Types, Brands, B2B Venues).
- **18 Core Money & Brand Pages Upgraded**: Injected `<!-- CD-GSC-SYMPTOM-CLUSTER -->`, `<!-- CD-CRO-TRUST-BAR -->`, and 5-question `<!-- CD-CRO-FAQ-ACCORDION -->` across all 18 core refrigeration, catering, AC, specialty, and brand pages (`commercial-fridge-repair-london`, `fridge-repair-london`, `commercial-freezer-repair-london`, `freezer-repair-london`, `cold-room-repair-london`, `air-conditioning-repair-london`, `commercial-catering-repair-london`, `catering-repair-london`, `ice-machine-repair-london`, `chiller-repair-london`, `display-fridge-repair-london`, `prep-fridge-repair-london`, `walk-in-freezer-repair-london`, `dairy-cabinet-repair-london`, `williams-freezer-repair-london`, `liebherr-fridge-repair-london`, `ice-o-matic-fridge-repairs`, `refrigeration-brands-repair-london`).
- **Blog-to-Money-Page Internal Link Silo (`<!-- CD-BLOG-CTA-BOX -->`)**: Injected Emergency Dispatch Callout Box with direct exact-match anchor links across all 15 `/blog/` articles.
- **Upgraded `auto-seo.aspx` to V4.4 on Live Plesk**: Added high-CTR titles & descriptions for `dairy-cabinet`, `cellar`, `blast-freezer`/`blast-chiller`, `supermarket`, and all commercial brand pages (`williams`, `liebherr`, `ice-o-matic`, `hoshizaki`, `subzero`, `foster`, `true`, `polar`, `gram`, `refrigeration-brands`), excluded non-indexable/dishwasher URLs from `sitemap.xml` (120 clean canonical URLs), triggered live on Plesk (`HTML Updated: 227`), and pulled back locally.
- **Validation**: `npm test` (440 files scanned, 0 errors) and `protect_fixed_pages.py check` (12/12 OK).









### [2026-10-19 16:58:13 UTC] — 24-HOUR AUTOMATED WEBSITE UPDATE & HEALTH CHECK
- **Summary**: Executed daily 24h V4.4 auto-seo refresh on Plesk, synced live files locally, verified HTTP 200 on core money pages, and pinged GSC sitemap.
- **Git Commit**: `f39c52e`
- **Affected Files / Scope**: 19 core money/brand pages + sitemap.xml + 363 live Plesk files
- **GSC / Live Status**: HTTP 200: 19/19 core pages | GSC Sitemap PUT=204
- **Details**: Server response: `AUTO-SEO V4.4 RANKING PUSH OK | HTML Updated: 227 | Sitemap URLs: 120 | Time: 2026-10-19T16:57:32.3292480Z` | Sync: `Sync complete! Downloaded 363 total files (245 .html, 117 .asp/.aspx, plus sitemap.xml) and mirrored to colddirect-public-html/.`

### [2026-10-19 16:58:59 UTC] — 48-HOUR FULL WEBSITE & PLESK SERVER BACKUP
- **Summary**: Created verified full snapshot `colddirect-live-backup-2026-10-19_1658.zip` (531 files, 2.00 MB) and pushed Git tag `backup-2026-10-19-1658`.
- **Git Commit**: `f39c52e`
- **Affected Files / Scope**: 531 files archived (.html, .asp, .aspx, .css, .js, .htaccess, web.config, sitemap.xml)
- **GSC / Live Status**: SHA-256: `1212c98c3d1f4172f85eb6e7a210f3ea292839fa15dd7545d821d84796f02344` | Retention: 1/15 kept
- **Details**: Archive path: `C:\Users\khora\Documents\colddirect-website\colddirect-public-html\backups\colddirect-live-backup-2026-10-19_1658.zip` | Plesk sync: `Sync complete! Downloaded 363 total files (245 .html, 117 .asp/.aspx, plus sitemap.xml) and mirrored to colddirect-public-html/.`

### [2026-10-19 22:50:30 UTC] — UNIQUE ENGINEER IMAGES & SCHEMA UPGRADE
- **Summary**: Generated 3 distinct photorealistic human-engineer photos (<180KB, unique hashes), replaced duplicate images on supermarket-fridge-repair-london, prep-fridge-repair-london & bottle-cooler-repair-london, updated og:image & JSON-LD ImageObject schema, uploaded to live Plesk, and pinged GSC Indexing API.
- **Git Commit**: `4e6b309`
- **Affected Files / Scope**: images/engineer-supermarket-multideck-fridge-repair-london.jpg, images/engineer-commercial-kitchen-prep-fridge-repair-london.jpg, images/engineer-bottle-cooler-bar-fridge-repair-north-london.jpg, supermarket-fridge-repair-london, prep-fridge-repair-london, bottle-cooler-repair-london
- **GSC / Live Status**: HTTP 200 OK (6/6 live URLs) + GSC Indexing API 200 OK

### [2026-10-19 23:13:41 UTC] — 3 EQUIPMENT-ONLY IMAGES (NO HUMANS) & SCHEMA DEPLOY
- **Summary**: Generated and optimized 3 photorealistic equipment-only images (zero humans, <180KB JPG+WebP: supermarket-large-multideck-fridge-repair-london, commercial-kitchen-prep-fridge-repair-london, large-double-door-bottle-cooler-repair-north-london), updated HTML, og:image, twitter:image & JSON-LD ImageObject schema across Supermarket Fridge/Freezer/Dairy Cabinet, Prep Fridge, and Bottle Cooler North London pages, deployed to live WHUK Plesk (11/11 HTTP 200 OK), merged PR #78 (commit 12a093d), and pinged GSC Indexing API.
- **Git Commit**: `12a093d`
- **Affected Files / Scope**: images/supermarket-large-multideck-fridge-repair-london.jpg, images/commercial-kitchen-prep-fridge-repair-london.jpg, images/large-double-door-bottle-cooler-repair-north-london.jpg, supermarket-fridge-repair-london, supermarket-freezer-repair-london, dairy-cabinet-repair-london, prep-fridge-repair-london, bottle-cooler-repair-london
- **GSC / Live Status**: HTTP 200 OK (11/11 live URLs) + GSC Indexing API 200 OK (5/5 URLs)

### [2026-10-19 23:34:23 UTC] — INTERACTIVE SERVICE POPOVER / HOVER CARD ENGINE (V4.5)
- **Summary**: Built and deployed Zero-CLS interactive B2B service popover/hover card engine (css/cd-hover-card.css + js/cd-hover-card.js) with 260ms hover bridge, live 24/7 dispatch badge, and direct phone/hub CTAs across 14 /blog/ pages and 35 core commercial service/brand pages on live WHUK Plesk (HTTP 200 OK), opened PR #79 (commit dfa62cc), and pinged Google Indexing API.
- **Git Commit**: `dfa62cc`
- **Affected Files / Scope**: css/cd-hover-card.css, js/cd-hover-card.js, blog/*, 35 core service/brand HTML pages
- **GSC / Live Status**: HTTP 200 OK (9/9 verified live URLs) + GSC Indexing API 200 OK (7/7 URLs)

### [2026-10-20 09:05:03 UTC] — seo-ctr-v45
- **Summary**: V4.5 live audit fix: auto-seo.aspx upgraded to V4.5 (new home/freezer titles, 60-90 Min Target Response meta descriptions on 5 core pages, unified #business HVACBusiness+LocalBusiness JSON-LD with aggregateRating 4.9/38, 25-mile GeoCircle, 3 phones, core-page-only rating, mojibake safeguards). Added CD-HERO-KEYWORD-MATRIX to 5 pages, CD-HOMEPAGE-6-BLOG-HUB (6 articles) on homepage, descriptive alt tags, Trade-serviced byline grammar fix in 2 blogs, mojibake fix on 2 ice-machine pages. Live audit found NO 'circuit level' mojibake and NO missing trust bar/FAQ/symptom modules on fridge/freezer pages (already live). Lesson: PowerShell Get-Content shows UTF-8 as mojibake - verify with Python utf-8. Hub card titles corrected to match real articles (5 checks, not 7 faults). PR #79 hover cards still unmerged on main (auto-review blocks merge).
- **Git Commit**: `dfa62cc`
- **Affected Files / Scope**: index.html,fridge-repair-london,commercial-fridge-repair-london,commercial-freezer-repair-london,cold-room-repair-london,auto-seo.aspx
- **GSC / Live Status**: Indexing API 11/11 URL_UPDATED 200
- **Details**: npm test OK; protect_fixed_pages check 0 errors; auto-seo V4.5 trigger OK 233 pages, sitemap 123 URLs; live verified 5 pages

### [2026-10-20 09:37:50 UTC] — V4.7 Top-3 Money Keywords Domination Push
- **Summary**: 9 money pages (fridge/freezer/commercial fridge/commercial freezer/cold room/catering/commercial appliances/air conditioning/cellar) got exact-match titles, H1/H2s, hero keyword matrix, CD-9-MONEY-TECH-MATRIX-V47 fault-code/OEM-part/F-Gas matrix, and sitewide CD-9-MONEY-KEYWORD-SILO-V47 exact-match internal links (402 files) + homepage silo + 9 hover-card entries. auto-seo.aspx V4.7 deployed (per-page Service+OfferCatalog+FAQPage graph, sitemap excludes noindex/canonical-elsewhere). commercial-catering-repair-london canonicalised to commercial-appliances-repair-london (anti-cannibalisation).
- **Git Commit**: `b8aaa45`
- **Affected Files / Scope**: 9 money pages x4 paths, index.html, ~240 silo pages, js/cd-hover-card.js, auto-seo.aspx, protected-pages.json
- **GSC / Live Status**: Live HTTP 200 on 9 pages + home; auto-seo V4.7 OK (233 html updated, 114 sitemap URLs); npm test 0 JSON-LD errors
- **Details**: Fridge title changed again within 7-day cooldown on explicit owner request (title ~83 chars, may truncate in SERP). Legacy plural/.asp URLs untouched. 55 BOMs stripped; one mojibake fixed in walk-in-cold-room mirror.

## 2026-10-20 (late) - V4.9 end-to-end pass: Enfield, blog sitemap, redirects, idempotent auto-seo, post-deploy CI
- auto-seo.aspx **V4.9**: dn.Equals("logs") (blog now scanned + in sitemap: hub + 12 articles; duplicate /blog/commercial-freezer-ice-buildup-causes/ stays out via canonical-elsewhere); 
edirectedSlugs (about, news, refrigeration-brands-repairs-london) never in sitemap; /blog/ pages get NO V4 footer/schema/bloghub/mojibake rewrite, only a fill-only description when empty; removal regexes + injection points now consume surrounding whitespace so the run is idempotent from run 1 (live run 2 = "HTML Updated: 0"); stray \r\r\n removed from the script itself.
- Tests: python tools/test_auto_seo.py compiles the REAL aspx body with csc (fake Request/Response/Server) and runs synthetic + real-tree idempotency/sitemap tests. Run it after every aspx edit.
- /commercial-fridge-repair-enfield/ was a live 404 (only .html existed, no folder index, non-slash canonical). Fixed with folder index + slash canonical + contactPoint 07983 759320 (4 copies).
- web.config + .htaccess: 301 /about/, /about.html, /about/index.html -> /about-us/ and /refrigeration-brands-repairs-london(/|.html|.asp) -> /refrigeration-brands-repair-london/ (plural-only rule; do NOT make the pattern match the singular or it loops). Rules sit at the TOP of the IIS rules so the 'pass through existing .html' rule cannot swallow them.
- Blog linking: 	ools/blog_related_services.py (idempotent, marker CD-BLOG-RELATED-SERVICES). All 52 article files already had 6-9 contextual core links -> no-op today; CI runs it with --check.
- deploy.yml: after FTP, sleep 10 -> curl auto-seo (retries) must return AUTO-SEO + OK -> 	ools/live_smoke_test.py (200s, sitemap asserts, 301s, URL count to $GITHUB_STEP_SUMMARY), up to 3 rounds because the Plesk webhook can lag.
- LESSON: deploy_to_plesk.diagnose() (FTPS) hangs on this host - upload with plain ^Ltplib.FTP() reading .vscode/sftp.json (script: temp upload_plain.py pattern).
- LESSON: parallel Write + Shell calls race - run the script only after the Write call has returned.
- LESSON: auto-seo key cd2026 is visible in the public repo; optional secret AUTO_SEO_KEY is read by deploy.yml if you add it (then also change the key in auto-seo.aspx).

## 2026-10-20 (night) - auto-seo.aspx access key rotated (old public key revoked)
- The old hard-coded key (visible in the public repo + git history) is REVOKED. New 32-char random key lives ONLY in: GitHub secret AUTO_SEO_KEY, server file /httpdocs/App_Data/auto-seo.key, and a gitignored local copy App_Data/auto-seo.key. Never print, commit or paste it.
- auto-seo.aspx reads the server file (trim, constant-time compare) and FAILS CLOSED (403) if the file is missing or shorter than 24 chars. IIS answers 404 for /App_Data/*; web.config also denies the .key extension.
- Guard rails: .gitignore (App_Data/, *.key), 	ools/deploy_guard.py (App_Data + .key blocked for every upload script), deploy.yml excludes App_Data/*.key. The key file is uploaded once, out of band, with plain ftplib (that one-off script bypasses the guard on purpose). The Plesk push webhook does NOT delete untracked server files (verified after push).
- deploy.yml and the new nightly workflow use secrets.AUTO_SEO_KEY only (no fallback; empty = hard fail). tools/test_auto_seo.py generates a random key per run and asserts that cd2026, empty, truncated, extended and missing-file cases are all rejected.
- LESSON: the nightly Plesk Scheduled Task (not readable over FTP) probably still calls auto-seo.aspx with the old key and now gets 403. .github/workflows/auto-seo-nightly.yml (20:21 UTC) takes over; the Plesk task can be deleted or updated whenever convenient.
- To rotate again: generate a new key, gh secret set AUTO_SEO_KEY, overwrite App_Data/auto-seo.key on Plesk via FTP (no code change needed).

## 2026-10-20 (night) - weekly executive GSC report (tools/gsc_weekly_report.py)
- Runs FIRST in gsc-weekly-sync.yml (Mon 06:00 UTC + workflow_dispatch; input 
eport_only skips the slow sitemap/inspection pass). Writes only to $GITHUB_STEP_SUMMARY (local runs: gitignored logs/). Step is continue-on-error; script exits non-zero only for missing/invalid credentials or no accessible property.
- Windows: newest day with FINAL data (never later than today-2) = end of current 7 days; previous 7 days compared. Property: URL-prefix https://www.colddirect.co.uk/ first (verified), then sc-domain:colddirect.co.uk.
- Pages are matched by normalised slug (legacy .html/.asp/no-slash merged); "commercial catering" row = commercial-appliances-repair-london + commercial-catering-repair-london.
- python tools/gsc_weekly_report.py --selftest is offline (synthetic data, also tests API-failure degradation) and runs in CI before the real report.
- First real data (w/e 2026-10-18): 62 clicks (-5%), 6,870 impressions (-13%), avg pos 31.1; homepage drives most clicks; 9 core pages = 11 clicks; Enfield page 0 impressions (just fixed, Google not re-crawled yet); many strike-distance queries land on / instead of the money pages.
- PRIVACY: Step Summaries of a PUBLIC repo are world-readable, so traffic/keyword data in the report is public.

## 2026-10-21 - de-cannibalisation + strike-distance pass (homepage vs money pages, cold room, ice machine, ice cream)
- Data (GSC w/e 2026-10-18): money queries (commercial fridge/fridge/freezer repair london) ranked pos 8-12 but landed on / instead of the dedicated pages; 'cold room repair london' pos 4.2, 'cold room repair near me' 4.6, 'ice machine repairs' 6.0, 'ice machine service' 6.7, 'refrigeration engineers london' 5.3; consumer query 'best ice cream maker uk' landed on /blog/best-ice-cream-makers/ which is a LIVE 404 (only .htaccess had a redirect, IIS/web.config did not).
- Homepage: title/description (auto-seo.aspx index rule) + og tags + H1 now hub/brand: 'Commercial Refrigeration & Air Conditioning Engineers London'. Hero keyword matrix rewritten as hub copy that links (exact-match anchors) to all dedicated pages; 'cheap commercial fridge repair London' removed from the homepage; cards use slash URLs.
- Money pages (commercial fridge/fridge/freezer/commercial freezer): bold exact keyword in the hero lead, brand back-link 'ColdDirect London Refrigeration Engineers' (class cd-brand-backlink, never the page's own keyword), 2 tailored FAQs each (visible accordion AND data-cd-schema=local-service-faq FAQPage are generated from the same list), Service node with description. Titles left UNCHANGED on purpose (already exact-match; rewritten 2026-10-19/20 = inside the 7-day cooldown). Commercial fridge/freezer H1 now carry 'Same-Day Walk-In & Display Chiller / Walk-In & Kitchen Freezer Engineers'.
- Cold room: new title 'Cold Room Repair London | 24/7 Cold Room Repairs, No Hidden Fees', description with 07983 759320, H2s with 'cold room repairs London' / 'cold room repair near me', coverage section + 2 FAQs.
- Ice machine: primary = /ice-machine-repair-london/ ('Ice Machine Repairs & Service London' in title, H1, H2s, Service schema); extra title rules in auto-seo for commercial-ice-machine / north-london / ice-machine-repairs variants so they stop duplicating the main title; strong links from homepage card + catering-repair-london + commercial-appliances-repair-london + commercial-catering-repair-london.
- Ice cream: /ice-cream-machine-repair-london/ pivoted to 'Commercial Ice Cream & Soft Serve Machine Repair London' (title rule in auto-seo, H1, lead, CTA block with links to commercial pages, FAQ); the stale folder index (mojibake meta) was replaced and the missing colddirect-public-html/ice-cream-machine-repair-london/ folder created. web.config: 301 /blog/best-ice-cream-makers(/|.html|.asp) -> /ice-cream-machine-repair-london/ (consumer page stays out of the index, B2B page gets the equity).
- Tooling: tools/seo_decannibalise_pass.py (idempotent, --check), tools/upload_plain.py (plain-FTP uploader that honours deploy_guard + preflight). auto-seo.aspx uploaded by plain FTP BEFORE the push so the CI post-deploy auto-seo run already uses the new rules.
- LESSON: Service schema is emitted twice per money page (page-local data-cd-schema block + auto-seo V4 block, same @id) - keep moneyMeta offers identical to the local block or they diverge. FAQ schema must be generated from the visible accordion (never hand-edited separately).
- LESSON: the Auto-review blocks Shell calls that run scripts from %TEMP% or chain many operations - keep helper tools inside the repo (tools/) and run one operation per call.
- VERIFIED LIVE 2026-10-21: deploy run 39516344946 green (post-deploy auto-seo V4.9 'HTML Updated: 14', smoke test ALL PASSED, 123 sitemap URLs); second auto-seo run = 'HTML Updated: 0' (idempotent); tools/verify_live_pass.py: 8 pages 200 with new title/H1/Service+FAQPage; /blog/best-ice-cream-makers/ and .html -> 301 -> /ice-cream-machine-repair-london/; best-ice-cream not in sitemap. Live-pulled auto-seo output (V4 Service offers, ice-machine variant titles) committed so repo == live.

## 2026-10-21 - Indexing guarantee pass (appliances + Enfield)
- GSC inspect (tools/gsc_inspect_urls.py): appliances = NEUTRAL / URL is unknown to Google / no crawl; Enfield = NEUTRAL / Not found (404) / last crawl 2026-10-19 (pre-fix 404).
- tools/internal_link_boost.py: idempotent (marker CD-LINK-BOOST-APPLIANCES/ENFIELD + exact-anchor check) in-body links on index, commercial-fridge, fridge, cold-room, coverage, 3 north-london pages, 2 blogs. Commit 0f65120, deploy + smoke test OK, live pull = no diff.
- Sitemap PUT 204 + Indexing API notified 15 URLs. Google still needs to recrawl; indexing cannot be forced.

## 2026-10-21 - Area/suburb pages audit + sync
- tools/area_pages_audit.py (--fix/--check, marker CD-AREA-LINKS-V1): 42 area pages in sitemap. Synced 4 copies for all (created 40 missing mirror /index.html, normalised commercial-freezer-repair-north-london/index.html, created .html + mirror for folder-only central/east-london). Orphans (0 inbound): blast-chiller-north, chiller-north, ice-machine-north, commercial-freezer-tottenham, central-london -> linked from /coverage/ and parent hub (hub pages: blast-chiller/chiller/cold-room/ice-machine-repair-london, commercial-fridge-repair-london, commercial-freezer-repair-north-london). Enfield link added on commercial-freezer-repair-north-london.
- Fixed fake placeholder phone 0207 123 4567 on central/east-london pages -> 0800 112 3427.

## 2026-10-21 - Unique area titles + contact sweep (auto-seo V4.10 areaMeta)
- auto-seo.aspx: areaMeta dictionary (19 rules: 11 cold-room-*, fridge central/east/north/enfield, freezer north/tottenham, blast-chiller-north, chiller-north) = single source of truth; tools/area_titles_apply.py mirrors titles/descriptions into all HTML copies; tools/title_h1_audit.py --area --check = 0 duplicate groups.
- tools/contact_sweep.py (--fix/--check): normalised legacy 020 8050 2374 (10 cold-room area pages) -> 0203 952 4822, tel:07983759320 / tel:02039524822 -> international form, injected CD-AREA-CONTACT-V1 block (mobile + 0800 + office + info@colddirect.co.uk) on 36 area pages lacking them.
- tools/html_preflight.py: new dummy-contact rule (123 4567, 1234567, 123456, 0000/9999 phone runs, example.com) + tools/test_preflight_dummy.py regression test.
- auto-seo.aspx uploaded by plain FTP before push.

## 2026-10-21 - Title trim + full-site unique titles
- areaMeta in auto-seo.aspx now 33 rules (19 area + 14 de-duplicated service pages: blast-*, chiller-*, walk-in-chiller-repair, adexa/cabinet/empire/multideck/undercounter/walk-in fridge). All titles 50-65 chars. tools/area_titles_apply.py writes them to all copies (warns outside 50-65).
- tools/html_preflight.py: site-wide unique <title> and <h1> rule for indexable non-redirect pages (by canonical, full scan only); tests in tools/test_preflight_dummy.py. title_h1_audit.py = 0 duplicates site-wide.
- NOTE: titles were re-written <7 days after the previous area title change at the owner's explicit request.


## 2026-10-21 - Live HTML content integrity checks + standing full-autonomy directive
- tools/live_smoke_test.py (commit 787f3ca): `check_page_integrity` / `integrity_checks` validate homepage + 9 core money pages + /commercial-fridge-repair-enfield/ on the LIVE response: no noindex (X-Robots-Tag + robots/googlebot/bingbot meta), exactly one self-referencing canonical, non-empty title + h1, >=1 JSON-LD block and every block parses with json.loads, official phone 07983 759320 present and no dummy 123 4567 / 1234567. Row text `HTTP 200 + Schema + Canonical + Phone OK` (or exact failing check). Offline `--selftest` covers valid page, noindex, canonical, title/h1, JSON-LD, phone, dummy phone. /blog/ is HTTP 200 only.
- Earlier this session (tooling only, under the freeze): weekly report Table 4 Indexing Watchlist (d3fe14a), issue alert/recovery workflows (542055a), smoke test SSL expiry + canonical host redirect + robots.txt health checks (27e1bcc and predecessors).
- Owner issued a STANDING FULL-AUTONOMY DIRECTIVE (see .cursorrules section 3): never ask for confirmation; end-to-end code -> selftest -> preflight -> deploy -> live verify -> report; safety guards and the 7-day freeze (until 2026-10-26) still apply.


## 2026-10-21 - Read-only dashboard tools/site_status.py
- `python tools/site_status.py [--skip-gsc] [--skip-gh] [--selftest]`: one terminal view of live state. Sections: (1) live_smoke_test checks (11 core pages integrity, latency avg/max, 13/13 homepage assets, sitemap URLs, robots, canonical + 301 redirects), (2) SSL expiry/issuer/days_remaining for both hosts, (3) latest Deploy / Nightly auto-seo / GSC Weekly Sync runs + open [LIVE SITE ALERT] issues via gh, (4) GSC URL Inspection of the 14 WATCHLIST URLs (Verdict / Coverage State / Last Crawl + scoreboard).
- Strictly read-only: `ReadOnlySession` guard only allows POST to the URL Inspection endpoint (Indexing API, sitemap pings, PUT, GET blocked); read-only OAuth scope; falls back with a message when no local GSC credentials. Exit 1 if a live check fails or an alert issue is open (GSC never affects exit code). GSC section takes ~90 s (14 sequential inspections).
- tools/live_smoke_test.py refactored: `run_all_checks()` returns the structured result; `main()` unchanged in behaviour.


## 2026-10-21 - Post-freeze audit requested early (freeze NOT over: system date is Wed 2026-10-21, freeze ends Mon 2026-10-26)
- Owner message said "freeze ended today, Monday Oct 26"; the real date is 2026-10-21, and the owner's own directive says freeze until 2026-10-26. HTML / title / auto-seo.aspx / og:image changes were therefore NOT applied; read-only audit done instead.
- GSC weekly window 2026-10-12..18 (pre-dates the 2026-10-21 title rewrite, so no freeze effect is measurable yet): sitewide clicks 62 (-5%), impr 6,870 (-13%), avg pos 31.1. Homepage 35 clk (+75%), pos 19.6; cold-room 7 clk, pos 12.3; cellar 4 clk (+300%); commercial fridge repair london pos 8.0 (-5.9), cold room repair london pos 4.2, ice machine repairs pos 6.0 (-5.5).
- WATCHLIST: 0/14 PASS (4 'Alternate page with proper canonical', 3 'Discovered - currently not indexed', 6 'URL is unknown to Google', Enfield 'Not found (404)'); nothing removed. Last Indexing API ping = Weekly Sync run 2026-10-20 23:03Z; no re-ping.
- Baseline checks all green: test_auto_seo, html_preflight --strict (0 issues), area_pages_audit --check, contact_sweep --check, deploy_guard.
- Prepared plan for 2026-10-26: og:image/twitter:image on homepage + core pages (candidate hero images/commercial-refrigeration-kitchen-20261014.webp 1279x720, or a generated 1200x630 JPEG), auto-seo.aspx idempotent enforcement without touching title/h1; smoke test will then report 14/14 homepage assets.


## 2026-10-21 - Pre-staged og:image activation for the end of the freeze (no live HTML / title / auto-seo.aspx change)
- tools/gsc_weekly_report.py: emit() now ALSO prints the full Markdown report to stdout (inside ::group::) so `gh run view --log` shows the tables and ping counts; selftest covers it.
- images/og-colddirect-london.jpg (+ colddirect-public-html mirror): 1200x630 JPEG, 143 KB, centre-cropped from images/commercial-refrigeration-kitchen-20261014.webp via tools/make_og_image.py (--check verifies size/dimensions/mirror). Image only; no HTML references it yet.
- tools/apply_og_image.py (--check / --selftest / apply): refuses before 2026-10-26T00:00:00Z (--force works only with --root on an isolated temp dir, never on the real repo); idempotent; inserts exactly og:image + twitter:image after the last og:/twitter: meta (else after canonical, else before </head>), keeps CRLF + indentation, never touches title/h1. Finding: 6 core pages (commercial fridge, commercial freezer, fridge, freezer, air conditioning, cellar) ALREADY have page-specific og:image/twitter:image -> state KEPT (not overwritten); 14 files (homepage, cold-room, catering, commercial-appliances in root + mirror) are pending. auto-seo.aspx contains no og:/twitter: logic, so it already preserves them: no aspx change/upload needed.
- .github/workflows/post-freeze-oct26.yml: cron '0 7 26 10 *' + workflow_dispatch, windows-latest (csc for test_auto_seo). Gate: year 2026, now >= 2026-10-26, og:image not yet live, image URL HTTP 200; then live pull, apply, preflight --strict, deploy_guard, test_auto_seo, contact_sweep/area_pages_audit checks, commit tracked files to main, dispatch deploy.yml (GITHUB_TOKEN pushes do not trigger it; needs actions: write), verify live_smoke_test 14/14 + og:image live, log to WORK_LOG, close/open alert issue "[LIVE SITE ALERT] Post-freeze og:image activation failed". Own concurrency group (NOT colddirect-production, or the dispatched deploy would deadlock).
- Note: with the 6 pages keeping their own images the homepage becomes the only page whose og:image is the new JPEG among the 9+1 core pages that had none; smoke test asset count should go 13 -> 14 after the homepage change.

## 2026-10-21 - MASTER DIRECTIVE executed (freeze lifted by owner): money hubs, audio, blog links, 24h/48h automation, job reports
- Memory: docs/ai-memory/OWNER_MASTER_PROMPT.md (verbatim), .cursorrules + .cursor/rules mdc section 4, DECISIONS.md, user store colddirect-memory.md.
- Money hubs (9): tools/money_data.py = source of truth; tools/money_keywords_apply.py mirrored titles/descriptions (07983 759320, same-day / 24/7 / affordable / fixed diagnostic call-out / London engineers) into auto-seo.aspx moneyMeta (+3 OfferCatalog variations per hub; uploaded with upload_plain.py) and all 4 copies of each hub, plus og:title/og:description/twitter:title/twitter:description and a `CD-MONEY-V1` H2/H3/FAQ block. Titles changed: fridge, freezer, catering, commercial-appliances ("Commercial Catering Repair London"), cold-room, air-conditioning, cellar; commercial fridge/freezer titles unchanged. protected-pages.json: fridge-repair-london expected_title updated.
- og:image: tools/apply_og_image.py FREEZE_END -> 2026-10-21; 14 files got og:image/twitter:image (homepage, cold-room, catering, commercial-appliances; root + mirror). post-freeze-oct26.yml deleted.
- Audio: tools/generate_seo_audio.py (edge-tts en-GB-SoniaNeural, ~25-30 s MP3 per hub + homepage, audio/ + mirror, tools/audio_manifest.json), `CD-AUDIO-V1` block (HTML5 audio preload=none, transcript details, AudioObject + SpeakableSpecification JSON-LD) in 10 pages x copies.
- Blog: tools/blog_money_links.py `CD-BLOG-MONEY-LINKS-V1` on /blog/ + 13 posts (54 files) linking all 9 hubs with modifier anchors; commercial catering anchor -> /commercial-appliances-repair-london/.
- Automation: auto-seo-nightly.yml (24h: auto-seo + smoke test + live pull + html_preflight --strict + seo_integrity_check + GSC ping + alert + report; never rewrites titles/H1), NEW site-backup-48h.yml + tools/backup_site.py (zip + SHA-256 manifest, scrub, no App_Data/*.key/bookings, 90-day artifact), tools/send_job_report.py wired into deploy.yml, auto-seo-nightly.yml, site-backup-48h.yml, gsc-weekly-sync.yml (rolling issue "📊 [ColdDirect Autopilot] Automated Job Reports & SEO Log" + WORK_LOG via Contents API).
- Checks run green: all new/old --selftest, html_preflight --strict (268 files), deploy_guard, area_pages_audit --check, contact_sweep --check, blog_related_services --check, protect_fixed_pages check, test_auto_seo, npm test (JSON-LD).
- Lessons: a persistent shell may keep GITHUB_STEP_SUMMARY set -> tools that write summaries create stray files in the repo root (tmp_summary.md was caught before commit); parallel Write+Shell calls race (run scripts in a separate call).

## 2026-10-21 02:18 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39532118422 | commit 12cd8eb
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=failure

## 2026-10-21 02:21 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39532419865 | commit 88ff6fc
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-21 02:26 UTC - Autopilot: 48h full site backup - SUCCESS
- Workflow: Site backup (48h) (workflow_dispatch) | run: https://github.com/ali221345/colddirect-website/actions/runs/39532427319 | commit 88ff6fc
- Metrics: archive=colddirect-backup-20261021-022013.zip; SHA-256=8a74462f02282d38b2fcf4d881791c805d6abda5a6dfd5e8879de9aba1f87f43; files=575 (258 html); integrity verified=True; manifest re-check=success; artifact (90 days)=colddirect-site-backup-39532427319

## 2026-10-21 02:31 UTC - Autopilot: 24h SEO sync & site update (auto-seo) - SUCCESS
- Workflow: Nightly auto-seo (live) (workflow_dispatch) | run: https://github.com/ali221345/colddirect-website/actions/runs/39532443850 | commit 88ff6fc
- Metrics: auto-seo + smoke test (sitemap/robots/latency/assets)=success; live strict preflight=success; SEO integrity (no title/H1 rewrite)=success; GSC ping=success

## 2026-10-21 02:37 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39533878260 | commit 39aee9b
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-21 02:40 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39534220365 | commit 617fcff
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-21 - Lessons from the master-directive rollout (money hubs / audio / backup / reports)
- aspx writes `<title>`/description RAW into the HTML; any '&' (or other escapable char) in tools/money_data.py would make the repo copy (escaped) and the aspx output (raw) flip-flop every run. money_data.selftest now forbids & < > " in titles/descriptions (cellar title uses "Pub and Bar").
- The Plesk Git webhook can re-deploy repo copies AFTER a workflow's auto-seo run (webhook lag): after pushing HTML, re-run auto-seo (`logs/_aspx.py`-style call with App_Data/auto-seo.key, never print the key), then `python tools/pull_live_plesk_v4.py` and commit the synced live state so repo == live (0 diff).
- Marker-block tools must keep the file's own line-ending style (Windows autocrlf working trees are CRLF, runner/live files are LF/mixed) and regexes must accept `\r?\n`; all three (money_keywords_apply, generate_seo_audio, blog_money_links) do now.
- The V4 schema (Service/OfferCatalog) is regenerated by the aspx on each run from moneyMeta; modifier offers live in moneyMeta (tools/money_keywords_apply.py appends them), never hand-edited into the HTML.
- Backup artifacts of a public repo are downloadable: bookings/ (customer data), App_Data, *.key and private keys are never archived; config secrets are redacted.
- A persistent shell may keep GITHUB_STEP_SUMMARY set: tools that write summaries then create stray files in the repo root (caught tmp_summary.md before commit). Check `git status` before every commit.
- /blog/smeg-fridge-freezer-control-panel/ is intentionally 301-redirected live to the commercial fridge hub (domestic topic); seo_integrity_check skips intentionally redirected pages.

## 2026-10-21 02:50 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39535159709 | commit 8b4e27a
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-21 - Live SEO audio verification added to every post-deploy and 24h nightly run
- `tools/seo_integrity_check.py` is now the single source of truth: `audio_targets()` (homepage + 9 money hubs = 10), `check_audio_page()` (local `/audio/*.mp3` in `<audio src>`/nested `<source>`, JSON-LD `AudioObject.contentUrl` == that URL, `SpeakableSpecification`, expected stem), `verify_mp3()` (HTTP 200, Content-Type audio/mpeg|audio/mp3 and never text/html soft-404, > 10000 bytes, Content-Length == received bytes, starts with `ID3` or MPEG sync 0xFF 0xEx), `audio_check()` (each unique MP3 fetched once). It replaces the old per-hub HEAD rows with ONE row `🔊 SEO Audio Assets` (`PASS — 10/10 MP3 audio summaries HTTP 200, audio/mpeg & AudioObject schema intact`).
- `tools/live_smoke_test.py` imports it (`audio_checks(bodies)`, `AUDIO_ROW`), reuses the HTML it already fetched and appends the row + `SEO audio: ...` failures, so a miss exits non-zero and fires `[LIVE SITE ALERT]`; the row lands in console + `$GITHUB_STEP_SUMMARY`. `tools/site_status.py` prints it as "SEO audio assets (home + 9 money pages)".
- Offline selftests (`sic.audio_selftest()`, 17 scenarios, shared by both scripts): 10/10 valid ID3, MPEG-sync variant, de-duplication, missing `<audio>`, mismatched contentUrl, missing AudioObject/Speakable, nested `<source>`, HTTP 404, truncated < 10 KB / short Content-Length, HTML soft-404 (text/html and html body under audio/mpeg), wrong Content-Type, bad magic bytes, 301, network failure, page not fetched.
- Live: IIS serves `/audio/*.mp3` as `audio/mpeg`; all 10 pass. No HTML/`<title>`/`<h1>` touched; only Python tools + this log changed.

## 2026-10-21 03:02 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39536276321 | commit c5c0007
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-21 08:25 UTC - Autopilot: 48h full site backup - SUCCESS
- Workflow: Site backup (48h) (schedule) | run: https://github.com/ali221345/colddirect-website/actions/runs/39568379457 | commit 085f0da
- Metrics: archive=colddirect-backup-20261021-081927.zip; SHA-256=9c55c0d2907d8277c7071da6d74e0308150102e3adf10f0f73a8adcb42ea66fe; files=588 (270 html); integrity verified=True; manifest re-check=success; artifact (90 days)=colddirect-site-backup-39568379457

## 2026-10-21 - Strict sitemap.xml coverage + lastmod validation in the live smoke test
- `tools/live_smoke_test.py`: new row `🗺️ Sitemap Integrity` (`sitemap_checks()` -> `sitemap_integrity()`, `classify_blog_posts()`, `required_sitemap_urls()`, `parse_lastmod()`), inherited by `tools/site_status.py` ("sitemap coverage + lastmod integrity"). Existing rows (HTTP 200 / contains / excludes) are unchanged.
- Fails (exit 1 -> `[LIVE SITE ALERT]`) when: sitemap is not a valid `<urlset>` XML; any required URL is not a `<loc>` (homepage, the 9 money pages = `CORE`, asserted equal to `money_data.HUB_ORDER`, `/commercial-fridge-repair-enfield/`, `/blog/`, every ACTIVE blog post); duplicate `<loc>` (also trailing-slash/case variants); a `<url>` without exactly one valid ISO-8601 `<lastmod>` (`YYYY-MM-DD` or `YYYY-MM-DDThh:mm[:ss[.s]][Z|+hh:mm]`, real calendar date/time), a `<lastmod>` in the future (1 day tolerance: Plesk runs UK time, runners UTC) or before 2020-01-01; any `<loc>` not starting with `https://www.colddirect.co.uk/` (http://, non-www, look-alike hosts).
- "Active" blog post = candidate (repo `blog/*.html` + links on the live `/blog/` index) that is live HTTP 200 (no redirects followed) with a self-referencing canonical. 301/404 stubs (smeg) and canonicalised duplicates (`commercial-freezer-ice-buildup-causes` -> `why-commercial-freezer-icing-up`) are not required. An HTTP 5xx / network error on a candidate fails the check (cannot classify).
- Redirect/canonicalised-away URLs still listed in the sitemap are a WARNING in the row, not a failure. Live finding: `auto-seo.aspx` still lists the 301 stub `/blog/smeg-fridge-freezer-control-panel/` in sitemap.xml (open follow-up: let the aspx skip redirected posts; sitemap.xml/aspx are owned by the live server and were not touched).
- Live result: 123 URLs, 23 required present, 0 duplicates, 123/123 valid lastmod (2026-10-21), all https://www. No HTML/`<title>`/`<h1>` changed.

## 2026-10-21 08:49 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39571992811 | commit c6e4d9d
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-21 - auto-seo.aspx: redirected blog stubs removed from sitemap.xml (owner approved)
- Cause: `.htaccess` 301-redirects retired/domestic blog URLs but their `.html` files still exist, so the aspx sitemap builder kept listing them (the new smoke-test row `🗺️ Sitemap Integrity` warned about `/blog/smeg-fridge-freezer-control-panel/`).
- Fix (auto-seo.aspx only, no HTML/title/h1 touched): `redirectedSlugs` now also holds `smeg-fridge-freezer-control-panel`, `samsung-fridge-freezer-not-freezing`, `best-ice-cream-makers`, `cold-room-troubleshooting`, `chiller-not-cooling` (the blog 301 rules in `.htaccess`). Keep this list in sync when adding a blog 301 to `.htaccess`.
- Rollout: `python tools/pull_live_plesk_v4.py` first (repo == live), edit, `python tools/upload_plain.py auto-seo.aspx`, ran the live aspx twice (stable: 122 sitemap URLs, was 123), re-pulled live state (sitemap.xml + mirrors committed). Live: Sitemap Integrity PASS with no warning, SEO integrity ALL INTACT.

## 2026-10-21 09:04 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39573927888 | commit 5b30306
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-21 - Blog stub 301s verified/enforced + "HTML Updated: 3" post-deploy drift eliminated
- Live test (no redirect following) of the 5 retired blog slugs x `/blog/<slug>/` and `/blog/<slug>.html`: only `best-ice-cream-makers` (web.config rule) was a clean single hop; smeg `.html` took 2 hops (`.htaccess` generic `.html -> /slug/` rule fired before the stub rule) and samsung / cold-room-troubleshooting / chiller-not-cooling answered 404 (+ 2-hop for `.html`). The host answers `Microsoft-IIS/10.0` yet honours part of `.htaccess`, so BOTH files are now kept in sync.
- Fix: 4 new `<rule>`s at the top of `web.config` (`^blog/<slug>(?:/index\.html|\.html|\.asp|/)?$` -> absolute `https://www.colddirect.co.uk/<target>` 301, targets: smeg -> `/commercial-fridge-repair-london/`, samsung -> `/commercial-freezer-repair-london/`, cold-room-troubleshooting -> `/blog/cold-room-temperature-fluctuation/`, chiller-not-cooling -> `/chiller-repair-london/`; ice-cream already existed) + one-hop `.htaccess` lines above the generic `.html` rule. Live after upload: 15/15 variants = single-hop 301.
- `tools/live_smoke_test.py`: new row `↪️ Blog Stub 301s` (`blog_stub_checks`, `BLOG_STUB_REDIRECTS`): both URL variants of the 5 slugs must be a TRUE 301 (not 200 / meta-refresh / 302 / 307 / 404 / 2-hop / wrong or http:// target) and each destination must be HTTP 200; selftest also asserts web.config, `.htaccess` and auto-seo.aspx `redirectedSlugs` list the same 5 slugs/targets. `site_status.py` prints it.
- ROOT CAUSE of "HTML Updated: 3": two mechanisms. (1) Plesk's git deploy resets every page whose committed text differs from the auto-seo fixed point by more than line endings; `preview-colddirect-homepage.html` + `/index.html` (noindex preview) were stale in git (extra blank line before `<!-- AUTO-SEO-V4-SCHEMA -->`, `Â£Â£` mojibake in priceRange, old V4 footer link block), so the first run after EVERY deploy re-rewrote them. (2) A push that uploads changed pages (CI checkout is LF-only, the agent writes its V4 blocks with CRLF) made the first run rewrite pages for a CRLF/LF-only difference (the "21" runs).
- Fixes: synced the aspx fixed-point version of the 2 preview pages into git (`python tools/test_auto_seo.py --sync`); `auto-seo.aspx` now uses `ContentDiffers()` (CRLF/LF-only differences are no change: no rewrite, not counted) and reports `| Changed: <file>@<offset> [old] -> [new]` whenever it rewrites something; `tools/test_auto_seo.py` real-tree test now FAILS on any page that is not at the fixed point (DRIFT) and asserts an LF-only checkout gives `HTML Updated: 0` on the very first run.
- Lesson: after changing page bodies or V4 footer/schema output in auto-seo.aspx, run `python tools/test_auto_seo.py` (it names drifting pages) and `--sync` + commit, otherwise every deploy shows "HTML Updated: N" and live pages flip back and forth.

## 2026-10-21 09:23 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39576409161 | commit e3331a8
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success
- Addendum (same day): the first deploy after the preview-page sync still showed `HTML Updated: 1` - the 3rd drift file was `public/brands.html` (tracked, deployed, but the old test harness skipped `public/`). Harness now includes `public/`; the aspx fixed-point version (V4 schema block, +33 lines) is committed. Deploy workflows now log up to 1500 chars of the auto-seo response so `| Changed: <file>@<offset> [old] -> [new]` is visible in Actions. Expected from now on: first auto-seo run after a deploy = `HTML Updated: 0`.

## 2026-10-21 09:27 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39576866835 | commit f6bbb49
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-21 - .htaccess <-> web.config parity audit (IIS native enforcement)
- FINDING: the live host is Microsoft-IIS/10.0 but ALSO runs an Apache-syntax `.htaccess` engine (requests carry `X-REWRITE-URL`/`X-ORIGINAL-URL`; HTTPS is native, no proxy). It hid gaps: with `.htaccess` renamed away the old `web.config` failed ~210 of 391 enumerated legacy URLs (plural -> singular 301s answered 200, `.html` -> `/slug/` missing, `/x/index.html` -> `/x/index/` 404, 58 two-hop chains via `.html` targets, no security/caching headers, no https/www rule).
- Fix: `web.config` now enforces everything ALONE: canonical https/www rules (apex host + http), generated rewrite map `HtaccessParity` (224 gap entries, one hop straight to the final canonical URL), `dir/index.html` -> `/dir/`, generic `.html` -> `/slug/` (same exclusions as .htaccess), pretty-URL rule serving `slug.html`, 5 hand-written two-hop redirects re-pointed to slash targets, `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy: strict-origin-when-cross-origin`, `X-Powered-By` removed, mimeMaps (webp, avif, mp3, woff, woff2, json, webmanifest, svg), `clientCache` per asset folder (css/js/assets 1 day, images/audio 7 days; HTML never long-cached).
- `.htaccess` aligned: generic `.html` rule moved BELOW all specific `.html` rules (they were unreachable -> 2 hops / dead targets), added `^(.+)/index\.html$`, `blog/*.html`/`blog/*/index.html` single-hop rules, unknown `/blog/<slug>` -> real 404 (was soft-404 to homepage), removed the stale `ice-machine-repairs-london` 301 rules (live indexed page, in sitemap, title owned by auto-seo.aspx).
- New `tools/config_parity.py` (+ `--selftest`, `--live`, `-g` regenerate map): parses every `.htaccess` rule, enumerates finite regexes into concrete URLs (sre_parse), simulates IIS URL Rewrite on the repo tree, compares one-hop 301 -> 200; also web.config self-audit (no chains / dead targets), static contract (headers, MIME, caching, https/www rule), live prober (no redirect following).
- `tools/live_smoke_test.py` rows: `Config Parity (.htaccess <-> web.config)` (offline, fails when a redirect exists in only one file), `Legacy 301s (single hop -> 200)` (~660 URLs + destinations live), `Security & Cache Headers`; all in `--selftest` and `tools/site_status.py`; `deploy.yml` and `auto-seo-nightly.yml` run `config_parity.py`.
- Verified live: web.config ALONE (`.htaccess` temporarily renamed on /httpdocs, restored) answered 643/644 probes (the 1 miss was the vacuous WordPress `index.php` pass-through, now excluded); both layers active: 788 probes + headers PARITY OK; woff2/woff/json/webmanifest/svg/avif/mp3 MIME probed with temporary files (deleted).
- LESSON: never assume the visible server layer; probe with the other layer disabled (rename `.htaccess` via FTP for seconds, always restore in `finally`). An `.htaccess` redirect rule is only a contract if it is reachable: check rule ORDER (a generic `.html` rule above specific ones shadows them).
- LESSON: XML comments must not contain `--` (web.config marker comments broke the parser). Rewrite-map keys are case-insensitive; map lookups of an unknown map must evaluate to "no match" in the simulator.
- OPEN (owner decision): `/ice-machine-repairs-london/` is a live sitemap page (kept; .htaccess rule removed). Stray `_backup_index_old.html` is deployed at the root (live 301 -> `/_backup_index_old/` 404; excluded from probes) - delete it from the repo/server when the owner agrees.

## 2026-10-21 10:03 UTC - Autopilot: Deploy to WHUK Plesk - FAILED
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39580824873 | commit 40301ad
- Metrics: auto-seo + live smoke test=failure; critical live pages=skipped; SEO integrity (live)=skipped

## 2026-10-21 10:32 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39584912389 | commit 87e96a0
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-21 - Frozen-chat recovery: 3 unreachable bare-slug 301s fixed, deploy green, live audit 10/10
- Workspace state: the previous chat ("Error resuming chat") had already committed and deployed its 106 files - working tree 100% clean, `main` only needed a fast-forward of `ca4e0be`. Nothing to re-commit or reset.
- The only real outstanding item was the RED deploy run 39580824873 (commit `40301ad`): FTP upload succeeded, but the post-deploy smoke test failed all 3 attempts on `↩️ Legacy 301s (single hop -> 200)`, 3 of 791 - `/freezer-repair-london`, `/fridge-repair-london` and `/williams-fridge-repair-london` (bare, no trailing slash) answered 200 instead of a 301 to their slash canonical.
- Root cause, both layers: in `.htaccess` the generic pretty-URL rule (`RewriteCond %{DOCUMENT_ROOT}/$1.html -f` + `RewriteRule ^(.+?)/?$ /$1.html [L]`) served the bare slug from `slug.html`; in `web.config` the three matching redirect rules sat BELOW `Serve real service directory index` (`^([a-z0-9-]+)/?$` + `{R:1}\index.html` IsFile, `stopProcessing="true"`), which matches a bare slug as well and shadowed them. The redirects were declared but unreachable.
- Fix (commit `87e96a0`): three bare-slug `[R=301,L]` rules added in `.htaccess` above the pretty-URL rule (no `/?` in the pattern, so `/slug/` still serves the folder index) and the three `web.config` rules moved above `Serve real service directory index`; both mirrored into `colddirect-public-html/`.
- Deploy run 39584912389 success: `Legacy 301s` PASS (667 legacy URLs, 627 x 301, 795 probes), `ALL PASSED` on attempt 1, auto-seo `HTML Updated: 0` (no drift), sitemap 122 URLs. Independently verified live: all three are single-hop 301s to the slash canonical.
- LESSON: `config_parity.py` reporting PARITY OK does not prove a redirect is reachable - it only compares `.htaccess` redirects against `web.config`. A rule shadowed by an earlier `stopProcessing="true"` rule is caught only by the live `Legacy 301s` prober. Before adding a bare-slug redirect, check everything that matches `^([a-z0-9-]+)/?$` above it in both files.
- New `tools/live_production_audit.py` (read-only; `--json`, `--selftest` = 11 offline checks): fetches the homepage + 9 money hubs over HTTPS and reports status, `<title>`, meta description with CTR-hook count, the marker blocks (`CD-HERO-KEYWORD-MATRIX`, `CD-9-MONEY-TECH-MATRIX-V47`, `CD-9-MONEY-KEYWORD-SILO-V47`, homepage `CD-HOMEPAGE-6-BLOG-HUB`), `<img>` alt coverage (>= 3 words = descriptive) and the `#business` JSON-LD node; exit 1 on any problem.
- Live audit: 10/10 clean. All HTTP 200, all markers present, 43/43 images carry a descriptive alt, `#business` = `["HVACBusiness","LocalBusiness"]` with `+442039524822` on every page, 2-5 CTR hooks per description.
- Guards green: `npm test` (460 files, 0 JSON-LD errors), `agent/scripts/protect_fixed_pages.py check` 12/12, `html_preflight --strict` 268 files / 0 issues, `deploy_guard`, `config_parity --selftest`, `live_smoke_test --selftest`, `test_auto_seo` (real tree runs 1-3 updated=0).
- OPEN FINDING (fixed below, owner approved): 102 of 117 top-level folders with an `index.html` still served their bare URL as HTTP 200.

## 2026-10-21 - Explicit one-hop trailing-slash 301s for the 102 directory slugs
- Owner approved enumerating the 102 bare directory URLs that answered HTTP 200. Each now has its own rule in `.htaccess` and `web.config` (root + `colddirect-public-html/` mirror): `^slug$` -> `/slug/` with no optional slash, so `/slug/` still serves the folder index.
- Excluded on purpose (already a single hop somewhere else, so a slash redirect would be a second hop): `about`, `news`, `bottle-cooler-repair`, `bottle-fridge-repair`, `cold-room-repairs-london`, `commercial-bottle-cooler-repair`, `commercial-dishwasher-repair-london`, plus the 8 that already 301 to their own slash (`appliances-repair-london`, `catering-repair-london`, `chiller-repair-london`, `fridge-repair-london`, `freezer-repair-london`, `refrigeration-brands-repair-london`, `services`, `williams-fridge-repair-london`). `walk-in-cold-room-repair-london` still 301s straight to `/cold-room-repair-london/`.
- Five of the 102 (`cabinet-fridge-repair-london`, `dairy-cabinet-repair-london`, `display-fridge-repair-london`, `hoshizaki-ice-machine-repair-london`, `walk-in-freezer-repair-london`) had to sit ABOVE the existing `Hoshizaki cold-storage blast extensionless to html` rewrite, which matches `/?` and was serving the bare URL as `slug.html`. Their slash URL is still an internal rewrite to `.html` (HTTP 200, zero extra hop).
- Offline: `config_parity` PARITY OK (371 rules, 746 probes, 708 x 301, 0 chains), `webconfig_self_audit` 0 problems, `deploy_guard` OK, `npm test` 0 JSON-LD errors, `html_preflight --strict` 268 files / 0 issues, `protect_fixed_pages` 12/12, `live_smoke_test --selftest` OK.

## 2026-10-21 10:40 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39586019083 | commit 715f3d6
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-21 10:46 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39586631797 | commit bad6e2b
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-21 10:59 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39588254766 | commit 5aad3d0
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-21 - Permanent lock + hands-free auto-run
- Banner `DO NOT REPEAT — COMPLETED & LOCKED MILESTONES` prepended to this file, `colddirect-public-html/colddirect-memory-ledger.md`, and the user-store `colddirect-memory.md`. Three locks: money pages (PR #81, PR #82, title/H1/meta cooldown until 2026-10-31), trailing-slash 301s (`87e96a0`, `5aad3d0`), and the V4.9 / 24h / 48h / live-audit pipelines.
- `tools/check_locked_state.py` (`--selftest`, then a real run) prints LOCKED and exits 0 while those artifacts are intact. `.cursorrules` and `.cursor/rules/colddirect-agent-memory.mdc` (`alwaysApply: true`) now require that check before any SEO or redirect edit.
- Workspace auto-run: `.vscode/settings.json` (YOLO / autoRun on, command denylists empty) and `.cursor/cli.json` (`approvalMode: unrestricted`, `deny: []`). `.vscode/**` excluded from the FTP deploy. `.cursor/mcp.json` was not edited (gitignored Search Console server config). User-level Cursor settings gained the same autoRun keys.

## 2026-10-21 11:13 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39589990233 | commit 44ba8f1
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-21 22:00 UTC - Autopilot: 24h SEO sync & site update (auto-seo) - SUCCESS
- Workflow: Nightly auto-seo (live) (workflow_dispatch) | run: https://github.com/ali221345/colddirect-website/actions/runs/39681986984 | commit 423434e
- Metrics: auto-seo + smoke test (sitemap/robots/latency/assets)=success; live strict preflight=success; SEO integrity (no title/H1 rewrite)=success; GSC ping=success

## 2026-10-21 - Nightly schedule miss diagnosed + dual-cron fallback
- Cause: `Nightly auto-seo (live)` was created 2026-10-20 23:47 local and stayed `state=active`, but GitHub never recorded an `event=schedule` run. This repo's cron does work (`Site backup (48h)` scheduled at 08:19 UTC today). The nightly's first 20:21 UTC slot was tonight; GitHub skipped it (known first-window / best-effort cron). Plesk's old 20:21 task is not a substitute after the key rotation (it would 403).
- Tonight filled by `workflow_dispatch` run 39681986984: `AUTO-SEO V4.9 ... HTML Updated: 0 | Sitemap URLs: 122` at 21:50:48Z. GSC sitemap PUT: lastSubmitted 2026-10-21T21:57:24Z, submitted **122** (was 123), 0 errors. Indexing API still 403 for the CI service account; URL Inspection passed on core pages. No title/H1/meta/redirect edits.
- Fix (no HTML/redirect change): second cron `51 21 * * *`, `repository_dispatch` type `nightly-auto-seo`, `actions: read` so the skip-gate can see today's successful run, `tools/trigger_nightly_auto_seo.ps1` + Windows task `ColdDirect-Nightly-AutoSEO-Fallback` at 21:40 local. Fallback skips when a success already exists today UTC / in the last 6 hours.

## 2026-10-21 22:05 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39683514139 | commit 6db2245
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success
## 2026-10-22 - Sitewide British welcome audio + top-right player layout
- Audit: 10 pages already had `CD-AUDIO-V1` (homepage + 9 money hubs); 127 eligible pages lacked audio; 9 stubs/noindex/no-H1 skipped.
- New shared MP3 `audio/colddirect-welcome.mp3` (~210 KB, en-GB-SoniaNeural) with the owner's exact welcome script. Tool: `tools/sitewide_welcome_audio.py` (`--generate`/`--inject`/`--check`/`--selftest`). Marker `<!-- CD-AUDIO-SITEWIDE-V1 -->` + AudioObject/Speakable JSON-LD (`#welcome-audio`). Money hubs never receive the sitewide marker.
- All players (money + sitewide) use the same compact **fixed top-right** CSS (bottom dock on ≤720px). Updated in `tools/generate_seo_audio.py` and reinjected on the 10 hubs. No `<title>`/`<h1>`/meta/canonical/redirect/sitemap changes. `check_locked_state` ALL LOCKS INTACT; protect_fixed_pages 12/12; npm test 0 JSON-LD errors; html_preflight --strict 0; config_parity OK.

## 2026-10-21 23:14 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39691390139 | commit 9c016cf
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-21 23:25 UTC - Autopilot: 24h SEO sync & site update (auto-seo) - FAILED
- Workflow: Nightly auto-seo (live) (schedule) | run: https://github.com/ali221345/colddirect-website/actions/runs/39693355702 | commit 24cc0f9
- Metrics: auto-seo + smoke test (sitemap/robots/latency/assets)=skipped; live strict preflight=skipped; SEO integrity (no title/H1 rewrite)=skipped; GSC ping=skipped

## 2026-10-22 — 100% pages top-right welcome audio (CD-TOP-RIGHT-AUDIO)
- Live audit after prior sitewide run: 119/122 sitemap URLs had `<audio>`; missing html-only pages `blast-freezing.html`, `cold-storage.html`, `walk-in-fridge-repair-london.html` (no `/index.html` twin). Mobile CSS still docked bottom on ≤720px — owner required top-right on ALL screens.
- New tool `tools/top_right_welcome_audio.py`: injects `<!-- CD-TOP-RIGHT-AUDIO -->` immediately after `<body>` with inline `<style id="cd-top-right-audio">` (`position:fixed !important; top/right; never bottom`), `#cd-audio-dock` + `/audio/colddirect-welcome.mp3`, strips `CD-AUDIO-SITEWIDE-V1`, hides legacy `.cd-audio-summary` so only one visible player. 504 HTML files updated (root + mirror). `seo_integrity_check.check_audio_page` prefers hub stem when both welcome + hub MP3 present.
- No title/H1/meta/canonical/redirect/sitemap edits. Locks intact; protect 12/12; npm test / preflight / parity / deploy_guard OK.
- Deploy: commit `3f76c2f`, run https://github.com/ali221345/colddirect-website/actions/runs/39694470611 SUCCESS. Live verify: **122/122** sitemap URLs contain `<audio`, `#cd-top-right-audio`, `#cd-audio-dock`, and `/audio/colddirect-welcome.mp3`.

## 2026-10-21 23:42 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39694470611 | commit 3f76c2f
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-21 23:46 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39695320419 | commit f3bc3e9
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-22 — NAP / GeoCoordinates / Maps pin to 27 Felixstowe Road, N9 0DX
- Audit: no NW10 5SR / College Park office address. All `postalCode` JSON already `N9 0DX`. Wrong pin was Enfield Town `51.6478,-0.0701` (and Enfield fridge `51.6515,-0.0786`) on `#business` / HVACBusiness / GeoCircle, not the depot.
- Fix: business + service-radius geo now `51.6256,-0.0561`. V4 short schema gained a `geo` block. Contact/coverage embeds now query `27 Felixstowe Road, Enfield, London N9 0DX`. Borough service maps left as area maps (not office). `auto-seo.aspx` schemaBlock + bizNode updated so nightly does not revert.
- No title/H1/meta/canonical/redirect/sitemap edits. Locks intact; protect 12/12; npm test 0 JSON-LD errors.

## 2026-10-22 09:38 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39756527892 | commit 05d525e
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-22 (evening) — leftover repo geo sweep (NW10 5SR / Felixstowe Rd)
- Re-scan: **zero** `NW10 5SR` or `Felixstowe Rd` in production HTML/schema/maps. Brent `NW10` mentions are service-area postcodes, not the office. Live homepage/contact/coverage/fridge already `N9 0DX` + `51.6256`.
- Cleared the last Enfield Town pin `51.6478,-0.0701` from `_backup_index_old.html` and `tools/tests/liebherr-404` fixtures.

## 2026-10-22 18:55 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39835191729 | commit 1d3ca65
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-22 20:51 UTC - Autopilot: 24h SEO sync & site update (auto-seo) - SUCCESS
- Workflow: Nightly auto-seo (live) (workflow_dispatch) | run: https://github.com/ali221345/colddirect-website/actions/runs/39850829998 | commit c138357
- Metrics: auto-seo + smoke test (sitemap/robots/latency/assets)=success; live strict preflight=success; SEO integrity (no title/H1 rewrite)=success; GSC ping=success

## 2026-10-22 — Top-3 rank booster V5 + internal anchor mesh V5
- `<!-- CD-TOP3-RANK-BOOSTER-V5 -->` + `<!-- CD-TOP3-SCHEMA-V5 -->` on homepage + 9 money hubs (4 copies each): H2/H3/table covering repair/repairs/service/services/emergency/same day/24/7/cheap/near me; Service+FAQPage JSON-LD (no `#business` duplicate). Titles/H1/meta untouched.
- `<!-- CD-INTERNAL-ANCHOR-MESH-V5 -->` on 430 supporting HTML files (root+mirror) with rotated exact/partial anchors into `/slug/` money hubs.
- `money_data.py` offers expanded; `auto-seo.aspx` moneyMeta OfferCatalog expanded; aspx comment lists body markers to preserve. Locks intact; protect 12/12; npm test 0 JSON-LD errors.

## 2026-10-22 21:15 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39854999305 | commit 80eecdd
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-22 23:27 UTC - Autopilot: 24h SEO sync & site update (auto-seo) - FAILED
- Workflow: Nightly auto-seo (live) (schedule) | run: https://github.com/ali221345/colddirect-website/actions/runs/39871836194 | commit f166ddd
- Metrics: auto-seo + smoke test (sitemap/robots/latency/assets)=skipped; live strict preflight=skipped; SEO integrity (no title/H1 rewrite)=skipped; GSC ping=skipped

## 2026-10-23 00:10 UTC - Autopilot: 24h SEO sync & site update (auto-seo) - FAILED
- Workflow: Nightly auto-seo (live) (schedule) | run: https://github.com/ali221345/colddirect-website/actions/runs/39876538152 | commit 8e84e65
- Metrics: auto-seo + smoke test (sitemap/robots/latency/assets)=skipped; live strict preflight=skipped; SEO integrity (no title/H1 rewrite)=skipped; GSC ping=skipped

## 2026-10-23 08:26 UTC - Autopilot: Deploy to WHUK Plesk - FAILED
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39923744920 | commit 0f614b6
- Metrics: auto-seo + live smoke test=failure; critical live pages=skipped; SEO integrity (live)=skipped

## 2026-10-23 08:26 UTC - Autopilot: 48h full site backup - FAILED
- Workflow: Site backup (48h) (schedule) | run: https://github.com/ali221345/colddirect-website/actions/runs/39923665744 | commit caac2ab
- Metrics: archive=colddirect-backup-20261023-081808.zip; SHA-256=8e8f161616286e3a73aa50467746d7e4a710a530e805eeb78da07f7e75d3a77e; files=445 (128 html); integrity verified=False; manifest re-check=skipped; artifact (90 days)=colddirect-site-backup-39923665744

## 2026-10-23 08:31 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39924845031 | commit 1f85399
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success

## 2026-10-23 08:35 UTC - Autopilot: Deploy to WHUK Plesk - SUCCESS
- Workflow: Deploy to WHUK Plesk (push) | run: https://github.com/ali221345/colddirect-website/actions/runs/39925428050 | commit 9e112cf
- Metrics: auto-seo + live smoke test=success; critical live pages=success; SEO integrity (live)=success
