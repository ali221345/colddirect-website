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
