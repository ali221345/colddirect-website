---
name: protect-fixed-pages
description: After a page is fixed, pin it so overnight Plesk/FTP deploy cannot revert it
---
ROLE: You pin Cold Direct pages so the overnight git→Plesk FTP cannot overwrite a live fix with an older stub.

WHEN TO RUN
- Immediately after any page is content-fixed or FTP-uploaded
- After overnight SEO / deploy if a hub page looks thin again
- When the user says a page "reverted"

RULES
- British English in page copy only. This agent does not rewrite marketing copy.
- Never bulk-FTP a protected file that fails the fingerprint in protected-pages.json
- Keep root HTML, folder index.html, and colddirect-public-html copies in sync
- Commit protected-pages.json with the page files (overnight deploy reads git)

AFTER A FIX
1. Identify the HTML that was edited (e.g. coverage.html)
2. Copy the same body to the folder index and colddirect-public-html twins
3. Register it:
   py agent/scripts/protect_fixed_pages.py register coverage.html --url https://www.colddirect.co.uk/coverage/ --reason "Hand-fixed; do not revert"
4. py agent/scripts/protect_fixed_pages.py check
5. Ask to commit protected-pages.json plus the HTML copies, then push main (deploy.yml must have the good files)

OVERNIGHT / REVERT CHECK
1. py agent/scripts/protect_fixed_pages.py check
2. py agent/scripts/protect_fixed_pages.py restore-live
   - Live matches fingerprint → leave it
   - Live failed, git is good → FTP the git files
   - Both failed → stop and tell the user; do not upload a stub
3. Open the live URL and confirm the expected title / required phrase

DO NOT
- Title-rewrite or SEO-thin a protected page
- Deploy from git if check fails for that file (exclude it from FTP instead)
