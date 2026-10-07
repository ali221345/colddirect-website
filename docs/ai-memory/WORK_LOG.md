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
