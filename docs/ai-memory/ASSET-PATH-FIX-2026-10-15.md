# Permanent asset path correction — 15 October 2026

Owner explicitly authorized applying and publishing the permanent repair. Based on main e2e6a69. Relative js/main.js and js/booking.js references were embedded in individual page sources, not a single shared footer. Converted them to root-relative paths across maintained HTML/PHP copies, including the excluded public mirror. Also corrected css/styles.css references in the same affected files, preserving query strings. Backup and test fixtures excluded.

Validation: normalization proves only the approved asset-path slash insertions; existing content, schema, script order, booking endpoints and contact information are preserved. Root assets already returned HTTP200. JSON-LD validation and deployment guards checked before release; live checks follow deployment. No genuine booking submissions authorized or sent. Ahrefs API returns Insufficient plan; recrawl/health score cannot be confirmed here.

The temporary redirect pasted by the owner is absent from repository .htaccess. No routing edit is included. Live hosting-only changes cannot be removed selectively without reading the actual live configuration; deployment may synchronize the tracked file. Do not claim direct Plesk configuration inspection.

Lesson: test asset URLs resolved against slash service URLs, not only root .html files. Similar visual headers do not imply shared includes. Keep mirror copies synchronized without changing backup/test fixtures.

Release scope narrowed to 17 source files and their 9 matching maintained mirror copies. Other mirror-only pages deferred. Automatic approval rejected embedded GSC analytics disclosure. Removed pre-existing analytics-bearing HTML comments from affected files before publication; no metrics copied to this note. Page copy and metadata otherwise preserved.
