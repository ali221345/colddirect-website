# Repair-cost routing release — 2026-10-07

Fresh live GETs confirmed a 301 cycle between the cost slash URL and its HTML alias; brands slash remains 404. Cost page source already declares the slash canonical. Add three exact early rules (HTML pass-through, bare-to-slash301, slash-to-HTMLinternal) and remove only the conflicting later external redirect in each existing root/mirror .htaccess. Direct HTML remains a200 canonical alias. Page text/prices/titles untouched. Existing differences between the two configs preserved.

Independent reviewer: 204 limited rewrite-model checks pass, reproduce the old cycle and preserve all non-cost directives and unrelated modeled routes. This is not Apache/IIS server proof; actual hosting translation and DirectoryIndex are not modeled. After deployment check GET/HEAD, queries, article identity/canonical/JSON-LD, HTTP-to-HTTPS and unrelated core/directory-blog routes. Main push automatically deploys through Plesk as well as GitHub; skipping Actions does not stop Plesk. No live fix or SEO uplift is claimed before successful release verification.

Run: python tools/check-repair-cost-routing.py (or --directory with standalone prepared files). Baseline fixtures retain exact pre-change root/mirror configs. Team operation/technical monitoring records continue in PR17 and workspace website-team-guide-fa.md.
