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
