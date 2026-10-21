# OWNER MASTER PROMPT (verbatim, issued 2026-10-21) - permanent standing instructions

> Saved exactly as given by the owner. Status of the Oct 26 freeze: **LIFTED by explicit owner command on 2026-10-21.**
> Standing rule that remains: never randomly rewrite `<title>` / `<h1>` on a schedule (ranking churn).

MASTER AUTONOMOUS SEO, AUDIO, BACKUP & 24/48H AUTOMATION DIRECTIVE

1. STANDING FULL-AUTONOMY & freeze OVERRIDE (SAVE TO MEMORY IMMEDIATELY):
   - By explicit owner command today (Oct 21, 2026), I am overriding and lifting the temporary Oct 26 HTML/title freeze so you can execute this complete Money-Keyword & Automation upgrade right now.
   - You have 100% permanent, pre-approved permission across all files, GitHub (`gh` CLI, workflows, issues, releases/artifacts), Plesk FTP deployments, users, credentials, and Google Search Console APIs. NEVER stop to ask me for confirmation or permission - execute everything end-to-end automatically.
   - Save this exact master prompt and all architectural rules permanently into:
     a) `docs/ai-memory/OWNER_MASTER_PROMPT.md` (for easy access anytime)
     b) `.cursorrules` and `.cursor/rules/colddirect-agent-memory.mdc`
     c) `docs/ai-memory/WORK_LOG.md` and `docs/ai-memory/DECISIONS.md`

2. TARGET MONEY KEYWORDS & MODIFIERS (9 CORE REVENUE HUBS):
   Optimize our core money pages, internal blog clusters, and structured data for these exact primary keywords:
   1) `fridge repair London` (`/fridge-repair-london.html` & `/fridge-repair-london/index.html`)
   2) `freezer repair London` (`/freezer-repair-london.html` & `/freezer-repair-london/index.html`)
   3) `commercial fridge repair London` (`/commercial-fridge-repair-london.html` & `/commercial-fridge-repair-london/index.html`)
   4) `commercial freezer repair London` (`/commercial-freezer-repair-london.html` & `/commercial-freezer-repair-london/index.html`)
   5) `catering repair London` (`/catering-repair-london.html` & `/catering-repair-london/index.html`)
   6) `commercial catering repair London` (targeted cleanly on our Catering / Commercial Appliances hub and dedicated section/blog cluster without causing canonical cannibalization)
   7) `cold room repair London` (`/cold-room-repair-london.html` & `/cold-room-repair-london/index.html`)
   8) `air conditioning repair London` (`/air-conditioning-repair-london.html` & `/air-conditioning-repair-london/index.html`)
   9) `cellar repair London` (`/cellar-cooler-repair-london.html` & `/cellar-cooler-repair-london/index.html`)

   Required semantic & conversion modifiers to weave naturally (NO spammy keyword stuffing) across meta descriptions, H2/H3 subheadings, FAQ blocks, and JSON-LD `Service` / `OfferCatalog` schemas:
   - `repairs`, `service`, `services`, `emergency`, `same day`, `24 hours` / `24/7`, `cheap repair` / `affordable & transparent cost`, `fixed diagnostic call-out`, `London engineers`, and official phone `07983 759320`.

3. ON-PAGE TAGS, META TAGS, TITLES, BLOG & AUDIO SEO UPGRADE:
   - Titles & Meta Tags: Verify and refine `<title>`, `<meta name="description">`, `og:title`, `og:description`, `og:image` (`https://www.colddirect.co.uk/images/og-colddirect-london.jpg` where missing), and `twitter:image` across the Homepage and all money pages (both root and mirror) so every target keyword + high-CTR modifiers (`Same-Day`, `24/7 Emergency`, `07983 759320`) are locked in cleanly with zero duplicate titles/H1s.
   - Audio Overview & `AudioObject` / `SpeakableSpecification` Schema:
     * Build a deterministic Python generator (`tools/generate_seo_audio.py`) that creates lightweight, valid spoken audio summaries (MP3/WAV in `/audio/` using edge-tts / gTTS or clean synthesized audio - or if offline, valid playable audio files + HTML5 `<audio controls preload="none">` summary bars + transcript accordions) for our core money pages summarizing our 24/7 emergency same-day London repair service and phone number `07983 759320`.
     * Inject valid JSON-LD `AudioObject` and `SpeakableSpecification` schema into those pages so Google and AI voice assistants index our audio and key answers.
   - Blog Cluster & Internal Linking Boost:
     * Ensure our `/blog/` index and commercial refrigeration/catering/cold-room/cellar/AC blog posts contain contextual internal link blocks pointing directly to all 9 money pages using exact and natural anchor text with our modifiers (`24 hour emergency commercial freezer repair London`, `same day cold room repair London`, `affordable catering repair London`, etc.).

4. AUTOMATED SCHEDULES (24-HOUR SEO + 24-HOUR SITE UPDATE + 48-HOUR FULL BACKUP):
   - Every 24 Hours - Automated Site Update & SEO Sync (`.github/workflows/auto-seo-nightly.yml`):
     * Run daily every 24 hours.
     * Pull/sync live Plesk state, run `auto-seo.aspx`, run `html_preflight.py --strict`, verify `sitemap.xml` and `robots.txt`, ping GSC with updated sitemaps/unindexed Watchlist URLs (within safe quota), and run `live_smoke_test.py`.
     * IMPORTANT SEO SAFETY RULE: Do NOT randomly rewrite `<title>` or `<h1>` tags every 24 hours (which causes Google ranking churn). Instead, the 24-hour job must enforce idempotently that our optimized titles, meta tags, schemas, audio blocks, and internal links remain 100% intact.
   - Every 48 Hours - Automated Full Site Backup (`.github/workflows/site-backup-48h.yml` + `tools/backup_site.py`):
     * Create a new scheduled GitHub Actions workflow running every 48 hours (`cron: '0 3 */2 * *'`) plus `workflow_dispatch`.
     * Connect to the live Plesk FTP server, download/verify a complete snapshot of live HTML, `auto-seo.aspx`, `web.config`, `sitemap.xml`, `robots.txt`, CSS/JS, and config files, package it into a timestamped `.zip` archive with a SHA-256 manifest, upload it as a 90-day GitHub Actions Artifact (and/or rolling `backups/latest-manifest.json`), and verify archive integrity.

5. AUTOMATED REPORT AFTER EVERY FINISHED JOB:
   - Create a unified reporting helper (`tools/send_job_report.py`) and wire it into the end of `deploy.yml`, `auto-seo-nightly.yml` (24h SEO/update), `site-backup-48h.yml` (48h backup), and `gsc-weekly-sync.yml`.
   - After ANY job finishes (success or failure), automatically post a clear summary comment to a single rolling GitHub Issue titled `📊 [ColdDirect Autopilot] Automated Job Reports & SEO Log` (which automatically sends an email notification to the repo owner for every completed job without cluttering the repo with hundreds of separate issues), AND append the entry to `docs/ai-memory/WORK_LOG.md`.
   - Keep separate `[LIVE SITE ALERT]` issues strictly for critical failures.

6. EXECUTE, TEST & DEPLOY END-TO-END NOW:
   - Run all offline `--selftest` checks, `html_preflight.py --strict`, `deploy_guard.py`, `area_pages_audit.py --check`, and `contact_sweep.py --check`.
   - Deploy everything to the live Plesk server via FTP and Git push to `main`, run `live_smoke_test.py` against `https://www.colddirect.co.uk`, trigger a test run of the 48-hour backup and job-reporting issue so I receive my first automated report immediately, and give me the complete Persian summary report.

---
## Implementation map (kept in sync by the agent)
| Directive item | Implemented by |
|---|---|
| Money copy single source of truth | `tools/money_data.py` |
| Titles / meta / og / twitter / body block / aspx moneyMeta | `tools/money_keywords_apply.py` (`--check` / `--apply`) + `auto-seo.aspx` moneyMeta |
| og:image / twitter:image | `tools/apply_og_image.py` (FREEZE_END = 2026-10-21) |
| Audio + AudioObject + Speakable | `tools/generate_seo_audio.py`, `/audio/*.mp3`, `tools/audio_manifest.json` |
| Blog internal links | `tools/blog_money_links.py` |
| 24h integrity enforcement (read-only, live) | `tools/seo_integrity_check.py` in `auto-seo-nightly.yml` |
| 48h backup | `.github/workflows/site-backup-48h.yml` + `tools/backup_site.py` |
| Job reports | `tools/send_job_report.py` (rolling issue + WORK_LOG) |
