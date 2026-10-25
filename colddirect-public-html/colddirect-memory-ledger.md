## ⛔ DO NOT REPEAT — COMPLETED & LOCKED MILESTONES (AS OF OCT 2026)

Read this section first. Then run `python tools/check_locked_state.py`. If a milestone prints LOCKED, skip it. These are finished and live on https://www.colddirect.co.uk/. Rebuilding them wastes a ranking cooldown.

### LOCKED #1 — 9 Money Pages V4.7/V4.9 Domination (PR #81 merged 2026-10-20 09:07 UTC, PR #82 merged 2026-10-20 09:38 UTC)
Homepage `/` plus the 9 money pages are optimized and were re-audited live on 2026-10-21 (10/10 HTTP 200):
`/fridge-repair-london/`, `/freezer-repair-london/`, `/commercial-fridge-repair-london/`, `/commercial-freezer-repair-london/`, `/cold-room-repair-london/`, `/catering-repair-london/`, `/commercial-appliances-repair-london/`, `/air-conditioning-repair-london/`, `/cellar-cooler-repair-london/`.
In place: exact-match titles, CTR meta descriptions, `CD-HERO-KEYWORD-MATRIX`, `CD-9-MONEY-TECH-MATRIX-V47`, `CD-9-MONEY-KEYWORD-SILO-V47`, homepage `CD-HOMEPAGE-6-BLOG-HUB`, descriptive image `alt` text, and `#business` JSON-LD (`HVACBusiness` + `LocalBusiness`).
**Indexing cooldown is active until 2026-10-31. Do not re-edit `<title>`, `<h1>`, or meta descriptions on these 10 pages.** A title change after that still goes through `tools/money_data.py` only, and only when the owner names the page.

### LOCKED #2 — Single-hop 301 trailing-slash redirects (commits `87e96a0` and `5aad3d0`, deploy 39588254766 passed on attempt 1)
All 117 top-level directories are classified. 102 bare URLs that answered HTTP 200 now 301 in one hop to their own slash folder (explicit rule per slug in `.htaccess` and `web.config`, root and mirror). 8 already 301'd to their own slash, including fridge, freezer, and williams from `87e96a0`. 7 must stay pointed somewhere else so they do not become a second hop: `about` -> `/about-us/`, `news` -> `/blog/`, `cold-room-repairs-london` and `walk-in-cold-room-repair-london` -> `/cold-room-repair-london/`, `commercial-dishwasher-repair-london` -> `/commercial-catering-repair-london/`, and the three bottle-cooler aliases -> `/bottle-cooler-repair-london/`.
Verified: `config_parity` 371 rules, 746 probes, 708 one-hop 301s, 0 chains. Live smoke test 895 probes, `ALL PASSED` on attempt 1.
**Do not rewrite `.htaccess` or `web.config` redirect rules unless the owner explicitly asks for a named redirect change.**

### LOCKED #3 — Automated background pipelines
`auto-seo.aspx` V4.9 (key in `App_Data/auto-seo.key`, never printed), the 24h workflow `auto-seo-nightly.yml`, the 48h workflow `site-backup-48h.yml`, and `tools/live_production_audit.py` are on `main` and were in sync with live Plesk `/httpdocs` on 2026-10-21 (pull reported 0 diff). Do not rebuild them.

### LOCKED #4 — Voice AI RULE 0 (owner 2026-10-25s — compact header-left widget)
The live widgets are: compact **Ask Your Fault** top-left of the white header (`?v=20261025q`), and **Listen · Welcome to Cold Direct** top-right of the same header. Do not hide `#cd-audio-dock`.

---

### [2026-10-25u] — Restore top-right Listen welcome player (`?v=20261025q`)
- `#cd-audio-dock` visible in the white header, right of WRITE A REVIEW. Ask Your Fault stays top-left. Title/H1/meta unchanged.

### [2026-10-25t] — Spoken like/review closing + CTA pulse (`?v=20261025p`)
- `vapi.start(assistantId, assistantOverrides)` plus a system `add-message`. CTA pulses on `speech-end`. Title/H1/meta unchanged.

### [2026-10-25s] — Header-left widget dropdown not clipped (`?v=20261025n`)
- Compact box left of the logo. SPEAK dropdown paints over the hero. Title/H1/meta unchanged.

### [2026-10-25o] — Vapi Ask Your Fault (`?v=20261025g`)
- Replaced custom top voice bar. Title `Ask Your Fault`. Badge `Lang: Auto`. SEO tags untouched.

### [2026-10-25n] — Same-language greeting (`?v=20261025e`)
- `Auto` label only. No English greeting before Persian. `کولد دایرکت`. Like-CTA. SEO tags untouched.

### [2026-10-25m] — Voice autoplay after SPEAK (`?v=20261025d`)
- RULE 0 locked. Mic tracks + analyser ctx released before play. Diagnose embeds audio. `__cdPlayCtx` buffer playback. Greeting restored. SEO tags untouched.

### [2026-10-25k] — Voice same-language I/O (`?v=20261025c`)
- Lang select + fa-IR SR + localized instant engine + vault langHint. SEO tags untouched. Commit `9f7792f`, deploy `40185770673`.

### [2026-10-25j] — Voice cutoff / filler / delay (`?v=20261025b`) — supersedes 25i
- 3800ms silence after speech, `continuous=true`, 60s max, TAP WHEN DONE. No Head Engineer intro. Instant local diagnosis + speak; API 1800ms background only. SEO tags untouched. Commit `bc85a1e`, deploy `40184436415`.

### [2026-10-25i] — Voice latency cut (`?v=14`)
- 700ms end-of-speech, first-sentence TTS, voice prewarm, local fault KB, instant "Diagnosing fault...". SEO tags untouched. Commit `f2770bf`, deploy `40183369543`.

### [2026-10-25h] — TOP3 double-`commercial` typo + Dispatch popover stub
- Generator skips the extra `commercial` prefix. Live homepage + commercial hubs: 0 `commercial commercial`. Hover JS is a stub; no `#cd-hover-popover` element on cold-room or fridge. SEO tags untouched. Commit `5c4cb87`, deploy `40180065273`.

### [2026-10-25g] — Voice bar on every public HTML page (`?v=13`)
- Homepage-only guard removed. Script injected sitewide. SEO tags untouched.

### [2026-10-25f] — Universal polite opening, no slang, `?v=13`
- Exact FA/EN/TL greetings verified live. Playback at 1.0. Slang openings deleted.

### [2026-10-25e] — Any-language diagnose + spoken audio (`?v=11`)
- Native Gemini copy for every language. TTS: OpenAI onyx (optional key) → Puck → Piper fa/en/tr/ar → Azure → translate_tts for Tagalog and other languages without Piper. Persian stays on Ganji. Live 7/7 PASS.

### [2026-10-25d] — Ganji Persian male (no pitch shift) + `NormalizePersianForSpeech`, `?v=10`
- Amir + 7% pitch-down removed. Live: `piper-fa_IR-ganji-medium`, 22050 Hz, F0 95 Hz, `ColdDirect` → `کُلد دایرِکت`, zero Latin in TTS text.

### [2026-10-25c] — Male-only: Piper on the server (fa Amir / en Alan / tr dfki / ar Kareem), `translate_tts` deleted, `?v=9`
- The voice is always male; Google `translate_tts` was female and is removed for good. Piper lives in `App_Data/piper/` (`tools/upload_piper_ftp.py`), streamed sentence by sentence (`more` + `engine:"piper"`). The browser fallback is a strict male allowlist.

### [2026-10-25b] — Free Persian voice: Urdu/Arabic `translate_tts` bridge (homepage `?v=8`)
- Persian `mode=tts` never returns ok:false any more (`voice:"cloud-neural-fallback-fa"`). Verified live 5/5. Edge `Sec-MS-GEC` was not used.

### [2026-10-25a] — TTS chain Puck → Azure → Google Translate (homepage `?v=7`)
- Google `translate_tts` has no Persian (400). en/tr/ar etc. now always get audio. Persian needs Gemini billing or an Azure Speech key (`tools/upload_azure_speech_key_ftp.py`). iOS: one primed `window.__cdVoicePlayer` + a "▶ Listen Answer" button.

### [2026-10-24k] — Multi-language voice input (homepage `?v=6`)
- SPEAK records real audio (MediaRecorder; 3s silence auto-send; STOP & SEND). Gemini transcribes and detects the language, then answers 100% in it (fa/en/tr verified). Text first, then Puck via `mode:"tts"`. Gemini free tier = 10 Puck/day; enable billing for production.

### [2026-10-24j] — Gemini + Puck live on homepage voice bar
- Key uploaded. Text model `gemini-3.5-flash-lite` (2.x models are 404 for new keys), TTS Puck. The vault rejects Gemini replies with a wrong phone, Tehran/Iran, or mixed-script words.

### [2026-10-24i] — Gemini key uploader + Puck TTS in ASPX vault
- Paste the key into git-ignored `App_Data/gemini-voice.key`, then run `python tools/upload_gemini_key_ftp.py` (uploads only that file and verifies `voice=Puck`). The vault now does Puck TTS itself.

### [2026-10-24h] — Voice bar warm British persona
- English vault replies now sound like a friendly London engineer, with a per-symptom intro and urgency line. Browser voice prefers UK male natural voices, rate 0.94, pitch 0.96. Script `?v=5`. Persian untouched.

### [2026-10-24g] — Voice bar: symptom engine + mobile mic fix
- Vault answers the actual symptom (noise/warm/leak/trip/ice/code/general top-3) in EN/FA, never "describe the make". Mic: continuous, 3.5s silence, STOP button; mobile 100vw + 16px input. Never combine `CodePage` with `ResponseEncoding` in the ASPX directive (500).

### [2026-10-24f] — Homepage-only Voice AI top bar (test, no site rollout)
- **Summary**: Compact 44px Voice AI bar on root `index.html` only. Speak/Listen/Ask, 3 chips, diagnosis card, 07983 759320, Helpful + stars, UK IP Shield. Live vault is IIS `colddirect-voice-vault.aspx` (PHP POST 405 on this host). Domain lock 403. Gemini/Puck waits for `App_Data/gemini-voice.key`.
- **SEO safety**: title/H1/meta/V4 untouched; other pages unchanged.
- **Git**: `d1407c6` + `a020be8`.

### [2026-10-23] — Top-right welcome audio sole player + 30+ years body copy
- **Summary**: Unified `CD-TOP-RIGHT-AUDIO` (`/audio/colddirect-welcome.mp3`) as the only visible player sitewide. `CD-AUDIO-V1` is now schema-only (hidden transcript + AudioObject/Speakable). Body/trust copy 15+ years became 30+ years. Updated `seo_integrity_check` / smoke to expect welcome embed + hub schema stem.
- **SEO safety**: title/H1/meta/canonical/redirects/sitemap 122 untouched; all 3 locks intact; protect check OK.
- **Git**: `0f614b6` (audio+years) + `1f85399` (integrity align). Deploy `39924845031` success.
- **Live verify (5/5)**: `/`, `/commercial-fridge-repair-london/`, `/fridge-repair-london/`, `/commercial-freezer-repair-london/`, `/cold-room-repair-london/` → TOPRIGHT=True, no Listen mid-page, no V1 audio tag, no 15y, 30y present.

### [2026-10-23b] — Freezer-visual unify (hero + top-right audio + hide sticky-cta)
- **Summary**: Matched sitewide above-the-fold to `/commercial-freezer-repair-london/`: audio dock `top:44px; right:16px`, hero order kicker→H1→lead→3 CTAs→image, keyword matrix/TOP3 below hero, hide `.sticky-cta` (keep Book a Consultation FAB), CSS `?v=20261023b`, auto-seo guard against above-hero injects.
- **SEO safety**: title/H1/meta/canonical/redirects/sitemap 122 untouched; locks intact.
- **Git/Deploy**: `af8fc9d`, deploy `39957034276` success. Live 10/10 core pages DOM-order match.

### [2026-10-23c] — Removed dark navy CD-CRO-TRUST-BAR under hero
- **Summary**: Deleted the full-width dark trust strip (60-90 Min / F-Gas / 24/7 pills + duplicate phone CTAs) from all HTML; disabled re-inject in upgrade_core_cro_pages.py and auto-seo; CSS kill-switch + cache-bust v=20261023c.
- **SEO safety**: title/H1/meta/canonical/redirects/sitemap 122 untouched; locks intact.
- **Git/Deploy**: `1f2471a`, deploy `39964152521` success. Live 5/5 verified no trust bar.

### [2026-10-24a] — Services pill + mobile audio overlap fix
- Stripped/hid `.svc-tagbar`; mobile audio relative under header; desktop fixed `top:52px;right:24px`; cache `v=20261024a`.
- Commit `710de13`, deploy `40038035210` OK. Locks intact.

### [2026-10-24b] — Compact mobile audio dock
- Desktop 240px @48px; mobile 175×48 relative under header; transcript hidden on mobile.
- Commit `89084dc`, deploy `40039278302` OK. Locks intact.

### [2026-10-24c] — Clean layout sync + Dispatch popover off
- Disabled `cd-hover-card.js` Dispatch Active popover; cold-room 30+ years; compact audio kept.
- Commit `ba3cc9f`, deploy `40076881572` OK. Locks intact.

### [2026-10-24d] — Homepage static fridge removed above carousel
- Commit `134340e`, deploy `40078732981` OK. Locks intact.

### [2026-10-24e] — freezer-repair-london one kitchen hero
- Commit `662a6af`, deploy `40080124395` OK. Locks intact.

# Cold Direct Permanent Automated Action & Backup Ledger

### [2026-10-22] — NAP / GeoCoordinates pinned to 27 Felixstowe Road, N9 0DX
- **Summary**: Replaced Enfield Town `51.6478,-0.0701` (and Enfield fridge `51.6515,-0.0786`) with depot `51.6256,-0.0561` on `#business` / HVACBusiness / GeoCircle. Added `geo` to V4 short schema. Contact/coverage Maps query is now `27 Felixstowe Road, Enfield, London N9 0DX`. `auto-seo.aspx` updated so nightly keeps the pin.
- **SEO safety**: no title/H1/meta/canonical/redirect/sitemap changes; locks intact; protect 12/12

### [2026-10-19 16:58:13 UTC] — 24-HOUR AUTOMATED WEBSITE UPDATE & HEALTH CHECK
- **Summary**: Executed daily 24h V4.4 auto-seo refresh on Plesk, synced live files locally, verified HTTP 200 on core money pages, and pinged GSC sitemap.
- **Git Commit**: `f39c52e`
- **Affected Files / Scope**: 19 core money/brand pages + sitemap.xml + 363 live Plesk files
- **GSC / Live Status**: HTTP 200: 19/19 core pages | GSC Sitemap PUT=204
- **Details**: Server response: `AUTO-SEO V4.4 RANKING PUSH OK | HTML Updated: 227 | Sitemap URLs: 120 | Time: 2026-10-19T16:57:32.3292480Z` | Sync: `Sync complete! Downloaded 363 total files (245 .html, 117 .asp/.aspx, plus sitemap.xml) and mirrored to colddirect-public-html/.`

### [2026-10-19 16:58:59 UTC] — 48-HOUR FULL WEBSITE & PLESK SERVER BACKUP
- **Summary**: Created verified full snapshot `colddirect-live-backup-2026-10-19_1658.zip` (531 files, 2.00 MB) and pushed Git tag `backup-2026-10-19-1658`.
- **Git Commit**: `f39c52e`
- **Affected Files / Scope**: 531 files archived (.html, .asp, .aspx, .css, .js, .htaccess, web.config, sitemap.xml)
- **GSC / Live Status**: SHA-256: `1212c98c3d1f4172f85eb6e7a210f3ea292839fa15dd7545d821d84796f02344` | Retention: 1/15 kept
- **Details**: Archive path: `C:\Users\khora\Documents\colddirect-website\colddirect-public-html\backups\colddirect-live-backup-2026-10-19_1658.zip` | Plesk sync: `Sync complete! Downloaded 363 total files (245 .html, 117 .asp/.aspx, plus sitemap.xml) and mirrored to colddirect-public-html/.`

### [2026-10-19 22:50:30 UTC] — UNIQUE ENGINEER IMAGES & SCHEMA UPGRADE
- **Summary**: Generated 3 distinct photorealistic human-engineer photos (<180KB, unique hashes), replaced duplicate images on supermarket-fridge-repair-london, prep-fridge-repair-london & bottle-cooler-repair-london, updated og:image & JSON-LD ImageObject schema, uploaded to live Plesk, and pinged GSC Indexing API.
- **Git Commit**: `4e6b309`
- **Affected Files / Scope**: images/engineer-supermarket-multideck-fridge-repair-london.jpg, images/engineer-commercial-kitchen-prep-fridge-repair-london.jpg, images/engineer-bottle-cooler-bar-fridge-repair-north-london.jpg, supermarket-fridge-repair-london, prep-fridge-repair-london, bottle-cooler-repair-london
- **GSC / Live Status**: HTTP 200 OK (6/6 live URLs) + GSC Indexing API 200 OK

### [2026-10-19 23:13:41 UTC] — 3 EQUIPMENT-ONLY IMAGES (NO HUMANS) & SCHEMA DEPLOY
- **Summary**: Generated and optimized 3 photorealistic equipment-only images (zero humans, <180KB JPG+WebP: supermarket-large-multideck-fridge-repair-london, commercial-kitchen-prep-fridge-repair-london, large-double-door-bottle-cooler-repair-north-london), updated HTML, og:image, twitter:image & JSON-LD ImageObject schema across Supermarket Fridge/Freezer/Dairy Cabinet, Prep Fridge, and Bottle Cooler North London pages, deployed to live WHUK Plesk (11/11 HTTP 200 OK), merged PR #78 (commit 12a093d), and pinged GSC Indexing API.
- **Git Commit**: `12a093d`
- **Affected Files / Scope**: images/supermarket-large-multideck-fridge-repair-london.jpg, images/commercial-kitchen-prep-fridge-repair-london.jpg, images/large-double-door-bottle-cooler-repair-north-london.jpg, supermarket-fridge-repair-london, supermarket-freezer-repair-london, dairy-cabinet-repair-london, prep-fridge-repair-london, bottle-cooler-repair-london
- **GSC / Live Status**: HTTP 200 OK (11/11 live URLs) + GSC Indexing API 200 OK (5/5 URLs)

### [2026-10-19 23:34:23 UTC] — INTERACTIVE SERVICE POPOVER / HOVER CARD ENGINE (V4.5)
- **Summary**: Built and deployed Zero-CLS interactive B2B service popover/hover card engine (css/cd-hover-card.css + js/cd-hover-card.js) with 260ms hover bridge, live 24/7 dispatch badge, and direct phone/hub CTAs across 14 /blog/ pages and 35 core commercial service/brand pages on live WHUK Plesk (HTTP 200 OK), opened PR #79 (commit dfa62cc), and pinged Google Indexing API.
- **Git Commit**: `dfa62cc`
- **Affected Files / Scope**: css/cd-hover-card.css, js/cd-hover-card.js, blog/*, 35 core service/brand HTML pages
- **GSC / Live Status**: HTTP 200 OK (9/9 verified live URLs) + GSC Indexing API 200 OK (7/7 URLs)

### [2026-10-20 09:05:03 UTC] — seo-ctr-v45
- **Summary**: V4.5 live audit fix: auto-seo.aspx upgraded to V4.5 (new home/freezer titles, 60-90 Min Target Response meta descriptions on 5 core pages, unified #business HVACBusiness+LocalBusiness JSON-LD with aggregateRating 4.9/38, 25-mile GeoCircle, 3 phones, core-page-only rating, mojibake safeguards). Added CD-HERO-KEYWORD-MATRIX to 5 pages, CD-HOMEPAGE-6-BLOG-HUB (6 articles) on homepage, descriptive alt tags, Trade-serviced byline grammar fix in 2 blogs, mojibake fix on 2 ice-machine pages. Live audit found NO 'circuit level' mojibake and NO missing trust bar/FAQ/symptom modules on fridge/freezer pages (already live). Lesson: PowerShell Get-Content shows UTF-8 as mojibake - verify with Python utf-8. Hub card titles corrected to match real articles (5 checks, not 7 faults). PR #79 hover cards still unmerged on main (auto-review blocks merge).
- **Git Commit**: `dfa62cc`
- **Affected Files / Scope**: index.html,fridge-repair-london,commercial-fridge-repair-london,commercial-freezer-repair-london,cold-room-repair-london,auto-seo.aspx
- **GSC / Live Status**: Indexing API 11/11 URL_UPDATED 200
- **Details**: npm test OK; protect_fixed_pages check 0 errors; auto-seo V4.5 trigger OK 233 pages, sitemap 123 URLs; live verified 5 pages

### [2026-10-20 09:37:50 UTC] — V4.7 Top-3 Money Keywords Domination Push
- **Summary**: 9 money pages (fridge/freezer/commercial fridge/commercial freezer/cold room/catering/commercial appliances/air conditioning/cellar) got exact-match titles, H1/H2s, hero keyword matrix, CD-9-MONEY-TECH-MATRIX-V47 fault-code/OEM-part/F-Gas matrix, and sitewide CD-9-MONEY-KEYWORD-SILO-V47 exact-match internal links (402 files) + homepage silo + 9 hover-card entries. auto-seo.aspx V4.7 deployed (per-page Service+OfferCatalog+FAQPage graph, sitemap excludes noindex/canonical-elsewhere). commercial-catering-repair-london canonicalised to commercial-appliances-repair-london (anti-cannibalisation).
- **Git Commit**: `b8aaa45`
- **Affected Files / Scope**: 9 money pages x4 paths, index.html, ~240 silo pages, js/cd-hover-card.js, auto-seo.aspx, protected-pages.json
- **GSC / Live Status**: Live HTTP 200 on 9 pages + home; auto-seo V4.7 OK (233 html updated, 114 sitemap URLs); npm test 0 JSON-LD errors
- **Details**: Fridge title changed again within 7-day cooldown on explicit owner request (title ~83 chars, may truncate in SERP). Legacy plural/.asp URLs untouched. 55 BOMs stripped; one mojibake fixed in walk-in-cold-room mirror.

## 2026-10-20 - V4.7 Top-3 Money Keywords Domination Push (DEPLOYED + MERGED)
- 9 money keywords -> 9 hub pages optimised (exact-match title/H1/H2/hero matrix), CD-9-MONEY-TECH-MATRIX-V47 on all 9, CD-9-MONEY-KEYWORD-SILO-V47 sitewide (homepage, boroughs, brands, blog), hover-card entries for all 9 URLs (js/cd-hover-card.js MONEY_PAGES).
- auto-seo.aspx V4.7 live: `AUTO-SEO V4.7 RANKING PUSH OK | HTML Updated: 233 | Sitemap URLs: 114`. Per-page @graph: #business + Service/OfferCatalog (5 offers) + single FAQPage.
- Anti-cannibalisation: commercial-catering-repair-london canonical -> /commercial-appliances-repair-london/ and removed from sitemap by V4.7 logic.
- Caveats: fridge title changed twice in 2 days (owner request; ~83 chars). Pull live before editing; never touch auto-seo.aspx/sitemap.xml in deploy.

## 2026-10-20 - Guard branch merged (PR #83) + preflight baseline emptied to 0
- PR #83 merged; CI run 39497022864 green incl. new 'Deploy Guard & HTML/SEO Preflight' step.
- git rm gsc-analysis-2026-09-19.html + logs/overnight-seo-writer-2026-09-20.html; .gitignore += logs/, gsc-analysis-*.html; deploy.yml excludes logs/** and gsc-analysis-*.html (other already-tracked logs/ files remain tracked but are no longer uploaded).
- /preview-colddirect-homepage/ (.html + /index.html): added noindex,nofollow (page says PREVIEW ONLY, was live+indexable, self-canonical). Kept, not deleted.
- /about/ and /news/ (.html + /index.html): added meta descriptions. NOTE: both are meta-refresh redirect stubs (about -> /about-us.html, news -> /blog/; news canonical already /blog/). Real about page is /about-us/ (already has description).
- auto-seo.aspx V4.8: fill-only description fallback (fallbackDesc: about, news). Fills missing/empty tags, never overwrites non-empty ones, respects AUTO-SEO-LOCKED and blog/. Compile-checked with csc + 7 behaviour tests. Root cause of old gap: auto-seo only REPLACED an existing description tag and only for pages with a title rule.
- tools/html_preflight_baseline.txt emptied; `html_preflight.py --strict` exit 0 (271 files, 0 issues).

## 2026-10-20 - Redirect stubs /about/ + /news/ cleaned; auto-seo V4.8 excludes meta-refresh stubs from sitemap
- about.html + about/index.html: canonical -> https://www.colddirect.co.uk/about-us/ ; news.html + news/index.html: canonical https://www.colddirect.co.uk/blog/ ; all four: <meta name="robots" content="noindex, follow">. Mirror copies (about.html, news.html) updated too.
- auto-seo.aspx V4.8: `refreshStub` (meta http-equiv=refresh) removes the page from sitemap.xml (also dishwasher stubs). Compile-checked + tested on real pages.
- tools/html_preflight.py: redirect stubs need no description, canonical to another colddirect.co.uk URL passes, and a stub WITHOUT noindex is now an error; default scan skips logs/.
- git rm -r --cached logs/ (21 local files kept, ignored via .gitignore).
- Live-pull noise: nightly auto-seo adds blank lines to ~388 pages per run (whitespace only) - restored, not committed. Only sitemap.xml real diff.
- FINDING (not fixed, needs owner decision): auto-seo.aspx skips folders where dn.Contains("log") -> /blog/ and ALL blog articles are never processed nor in sitemap.xml. Fix = dn == "logs" (would start injecting V4 blocks into ~100 blog pages and adding them to the sitemap).
- FINDING: web.config has the /news -> /blog/ 301 but no /about/ -> /about-us/ rule (only .htaccess has it; live is IIS).

## 2026-10-20 - Weekly GSC sync workflow (.github/workflows/gsc-weekly-sync.yml + tools/gsc_weekly_sync.py)
- Cron '0 6 * * 1' (Mon 06:00 UTC) + workflow_dispatch (inputs: dry_run, lookback_days). permissions: contents read. Read-only for repo/live site; summary to $GITHUB_STEP_SUMMARY, no commits.
- Secret used: GSC_CREDENTIALS_JSON (already in repo secrets since 2026-09-15; same name tools/request_indexing.py reads). Service account needs Owner/Full on property https://www.colddirect.co.uk/ (URL-prefix; sc-domain: gave insufficient permission earlier).
- Steps: PUT sitemap + GET status; queue = homepage, 9 core pages, /commercial-fridge-repair-enfield/, then git-log (--since N days, --diff-filter=AMR) modified service pages, then blog pages. Filters: deploy_guard.should_skip_upload, html_preflight (validate_html_file, is_noindex, is_redirect_stub), canonical-elsewhere, live HTTP must be 200 with no redirect. Caps: Indexing 80/run (daily 200), Inspection 150/run (daily 2000); 429/quota/permission stops that API, never fails the run. Exit 1 only for auth/sitemap-submit failure.
- git log --since is used instead of HEAD@{7.days.ago}: CI clones have no reflog.
- Dry run on current repo: 138 candidates (11 priority/113 service/14 blog), 15 skipped (about/news stubs, noindex, canonical-elsewhere, enfield = live 404), 80 accepted, 43 deferred.
- html_preflight.py now exports is_noindex() and is_redirect_stub().
- OPEN: /commercial-fridge-repair-enfield/ is a live 404 (priority-queued but never submitted until fixed).

### [2026-10-22] — 100% sitewide top-right welcome audio live
- **Summary**: Every sitemap URL now has fixed top-right `<audio controls>` for `/audio/colddirect-welcome.mp3` via `<!-- CD-TOP-RIGHT-AUDIO -->` + inline `<style id="cd-top-right-audio">` (`!important`, never bottom). Tool: `tools/top_right_welcome_audio.py`. Prior gap: 3 html-only pages + mobile bottom dock.
- **Git Commit**: `3f76c2f` | Deploy run 39694470611 SUCCESS
- **Live verify**: **122/122** sitemap URLs PASS (`<audio` + `#cd-top-right-audio` + `#cd-audio-dock` + welcome.mp3)
- **SEO safety**: no title/H1/meta/canonical/redirect/sitemap changes; locks intact; protect 12/12

## 2026-10-20 - GSC weekly sync: first live test run + hardening (run 39500957264, success)
- Test run results: secret GSC_CREDENTIALS_JSON authenticates; sitemap PUT = HTTP 204 (0 errors/0 warnings); URL Inspection worked (80 calls: 56 'Submitted and indexed', 14 'Discovered - currently not indexed', 4 'Alternate page with proper canonical', 3 'URL is unknown to Google', 2 'Google chose different canonical'); Indexing API = HTTP 403 permission denied for the CI service account (workflow stopped after 1 call, run still green).
- ACTION for owner (Indexing API pings only): add the service account behind GSC_CREDENTIALS_JSON as OWNER of https://www.colddirect.co.uk/ in Search Console and enable 'Web Search Indexing API' in its Google Cloud project. Sitemap + Inspection already work. (Local key C:\Users\khora\gsc-oauth.json is a different account that got 200s earlier.)
- REPO IS PUBLIC: CI logs + Step Summary are world-readable - never print service-account email, project ids or any secret-derived text. Script scrubs numeric ids from API error messages.
- Hardening: error detail + owner hint in summary, TIME_BUDGET_SECONDS=1200 (inspection ~7s/call; first run took 9m46s), workflow timeout 30 min. 11 offline unit tests pass (403/429/5xx/cap/main exit code/step summary).
- ANOMALY found by the workflow's live-sitemap check: at 21:30:14-17 UTC auto-seo.aspx ran (about.html + sitemap.xml rewritten) NOT triggered by me and produced 112 URLs INCLUDING /about/ (stub, noindex). Manual V4.8 run right after gave 111 without /about/. Coincided with the push-deploy run (21:30:12). Under investigation: scheduler vs deploy-linked.
