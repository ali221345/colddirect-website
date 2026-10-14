# ColdDirect private website review

Focused presentation and usability upgrade based on the connected GitHub repository `ali221345/colddirect-website`, main commit `f3cff3f296dcd91dea2d1d3a165cd67668eedd43` (inspected 14 October 2026).

The original repository's main/master push workflow deploys to Plesk. This independent Sites repository does not contain those workflows, deployment scripts, account configuration or server-side booking code. No change has been pushed to the original repository or live website.

`dist/` is a complete static site. Existing public service, brand, area and advice routes are retained with a consistent accessible shell. The homepage, service finder and contact page receive focused content and layout changes. Existing brand colours and refrigeration imagery are reused; illustrative imagery is labelled.

Phone and email links remain active. The contact form creates an editable email draft; the visitor explicitly sends it in their email application. It never claims to submit a booking. The Plesk ASP booking endpoint is not available on this static host and has not been changed on the live site.

Design references:
- https://becoolrefrigeration.co.uk/refrigeration/ — equipment-led services, clear repair and maintenance choices.
- https://adk.co.uk/commercial-refrigeration/ — equipment descriptions, maintenance context and direct repair calls to action.
- https://www.cool-service.co.uk/services — concise service categories and clear scope.

The site is owner-private on Sites and all pages include `noindex, nofollow` with a disallow-all robots file. Public release or changes to colddirect.co.uk require explicit owner approval.

Run structural checks with the primary runtime Python: `python scripts/validate.py`. See `VALIDATION.md` for verification scope and limitations.

Continuation details and production blockers: see PROGRESS.md. The review now links to the existing live booking page; it does not replace or test the Plesk booking backend.
