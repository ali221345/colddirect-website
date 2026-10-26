# ColdDirect Agent Memory and Lessons

Last verified: 2026-10-26. Machine-readable state: `docs/ai-memory/agent-state.json`.

## Read before every task or deployment

1. Read this file, `.cursorrules`, `docs/ai-memory/OWNER_MASTER_PROMPT.md`, and `docs/ai-memory/agent-state.json`.
2. Run `python tools/check_locked_state.py` and the regression checks listed below before editing.
3. Pull live Plesk state before HTML edits with `python tools/pull_live_plesk_v4.py`; never overwrite newer server work.
4. After deployment, test the live site rather than treating a successful Git push as proof of publication.

## Never Repeat Mistakes

- Keep exactly one unified business entity per page: `HVACBusiness` / `LocalBusiness`, stable `#business` ID, ColdDirect, 27 Felixstowe Road, London N9 0DX, `+447983759320`, `+442039524822`, and `info@colddirect.co.uk`. Remove duplicate business blocks, not unrelated service or FAQ schema.
- Never let scheduled jobs randomly rewrite curated titles, H1s, or descriptions. Money-page copy changes only through `tools/money_data.py` and its checked generator.
- Keep root `.html`, root `/index.html`, and both `colddirect-public-html/` copies synchronized.
- Use final trailing-slash internal URLs. Do not introduce redirect chains, broken relative links, or canonical/host loops.
- Never add `<!-- AUTO-SEO-LOCKED -->` without explicit permission for that page.
- Never accept a microphone HTTP 502 as “handled.” A friendly fallback is required, but the endpoint must also return its expected structured response. Recheck real microphone input and spoken playback after every Vercel deployment.
- `auto-seo.aspx` and `sitemap.xml` are excluded from normal deployment. After changing either, explicitly run `python tools/upload_plain.py auto-seo.aspx sitemap.xml` (or only the changed file) and verify live.
- Never print, commit, archive, or report FTP, GSC, Vercel, AI, `AUTO_SEO_KEY`, or notification credentials. Keep customer data and private keys out of backups.
- Rankings are measured outcomes, not guarantees. Use fresh GSC evidence; do not promise Page 1 or #1 positions.

## Verified work on 2026-10-26

- Unified business schema across 541 deployable HTML copies; independent local audit found zero business-schema problems.
- Added eight service/local landing pages and their synchronized copies, navigation links, sitemap entries, and clean server routes.
- Repaired ice-machine links, canonical targets, legacy internal links, and `/index.html` to `/` permanent redirect behavior.
- Preserved curated metadata and shortened three overlong money-page titles through the single-source generator.
- Main SEO commit: `83044be3b96d43d3e67173fc3fa83bd20a40aa91`; corrective deployment commit: `c751b601f7561e79bd50415ad9b96fe12b73d61a`.
- Live sitemap verified with 133 unique URLs and valid lastmod values. Live smoke tests, production pages, and live config parity passed.
- Vercel voice mirror commit: `7100b646`; deployment run `40369714526` completed successfully for merged SHA `d30991dd`.
- Final browser audit passed: microphone diagnosis returned HTTP 200 twice, spoken playback was observed, typed diagnosis worked, booking and empty-form validation worked, and no JavaScript errors, failed requests, or audio 502 responses were recorded. Evidence: local `audit-results/browser-widget-audit.json` (not committed).

## Regression checks

Run the applicable checks before committing and after deployment:

```text
npm test
python tools/html_preflight.py --strict
python tools/config_parity.py
python tools/deploy_guard.py
python tools/area_pages_audit.py --check
python tools/contact_sweep.py --check
python agent/scripts/protect_fixed_pages.py check
python tools/money_keywords_apply.py --check
python tools/blog_related_services.py --check
python tools/live_smoke_test.py
python tools/config_parity.py --live
python tools/verify-production-pages.py
python tools/voice_api_check.py --selftest
```

The browser microphone/playbook audit remains required after voice changes; HTTP-only checks do not prove browser audio playback.

## Recurring operations

- Nightly live auto-SEO: preserves curated metadata, performs integrity checks and limited GSC pings.
- Every 48 hours: source/Plesk backup and verified scrubbed live backup; live health, redirect/config, SEO integrity, voice API, GSC report, and bilingual outcome-based mobile notification.
- Review GSC strike-distance queries before deliberate content or internal-link changes. Measure later; never churn metadata on a timer.
