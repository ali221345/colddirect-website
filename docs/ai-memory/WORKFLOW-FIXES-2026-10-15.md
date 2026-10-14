# Workflow fixes — 15 October 2026

Owner instructed application of the multi-agent workflow audit fixes. Lead integrated YAML implementation and independent offline safety tests.

## Changes
- Four existing jobs share GitHub concurrency with cancel-in-progress false and check out the latest default branch. Running FTP jobs are not interrupted. GitHub may replace pending jobs; this is not a durable queue and cannot coordinate external Plesk/Hermes writers.
- Scheduled Daily SEO now prepares candidate changes and a dated report only in its runner. Only a non-sensitive proposed-filename list and operational status are retained as a 30-day Actions artifact. It does not FTP, submit a sitemap, commit proposals to main or advance applied-change state. It has read-only repository permissions and no FTP secrets. No duplicate schedule created. Review artifacts named colddirect-seo-review-RUN_ID; these replace new public Git commits of daily reports. Analytics reports and content patches are NOT uploaded because artifacts in this public repository are not confidential storage.
- A filename manifest and explicit prepared-only status are the only artifact contents. Full analytics retention requires an appropriate private destination; none is configured in this change. Automatic review rejected the original report-and-patch artifact design as potential analytics disclosure; it was replaced with the non-sensitive filename/status-only design. Root/directory reconciliation remains a reviewed promotion step; older mirror content is not propagated automatically.
- Legacy explicit publishing mode now throws on FTP failure. Scheduled mode has no git push whose failure could be swallowed.
- Deploy protected-page restoration failures are no longer ignored. New read-only post-deploy verification checks HTTP200, unchanged URL, source H1/canonical, all contact numbers and protected content on four critical pages, with bounded retries.
- Sitemap workflow name describes its actual work, removes stale GSC report staging and stages root robots alongside sitemap copies. It still uses the existing git push; failure is visible. A GITHUB_TOKEN push does not prove a separate deployment was triggered, and external Plesk state remains unverified.
- Backup schedule and archive implementation unchanged. No full-host backup or restore test claimed.

## Verification and lessons
Independent VM tests exercise actual daily main logic offline: candidate content/report generated without FTP, sitemap submission or applied-state changes; simulated FTP failure rejects publication. YAML parsing and whitespace checks pass. No secrets or real GSC connection used in tests.

Initial smoke-check test incorrectly required telephone links inside the Services source file, which obtains them from a shared include. Corrected the assertion to require the known public telephone trio on the served page plus any source links. Do not confuse SSI source with rendered HTML. Live test result and production run must be recorded after completion.

Scheduled GSC execution, artifact generation and external Plesk/Hermes coordination are not proven by offline tests. Continue daily oversight using actual workflow step results and artifacts; do not mistake a prepared change for a published improvement or ranking gain.
