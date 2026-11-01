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

### LOCKED #4 — Voice AI RULE 0 (owner 2026-10-26c — microphone audio)
Ask Your Fault records with MediaRecorder (`?v=20261026d`). STOP & SEND posts `audio_base64` to Vercel `/api/voice-diagnose`, which returns text first. The widget then calls `/api/voice-tts`. Do not use browser SpeechRecognition for Lang Auto. Never return the canned brand/error-code fallback. Never speak a slash or "Read this exactly". The widget must still speak the answer aloud.

---

### [2026-10-26c] — Vercel voice API live
- `https://colddirect-website.vercel.app/api/voice-diagnose` 200. CORS www + apex. Title/H1/meta unchanged.

### [2026-10-26b] — PTT + Vercel diagnose/TTS (`?v=20261026b`)
- Mic dies on STOP & SEND and during TTS. Title/H1/meta unchanged.

### [2026-10-26a] — Unify compact Ask Your Fault bar (`?v=20261026a`)
- SPEAK + LISTEN on all 9 money pages. Title/H1/meta unchanged.

### [2026-10-25al] — Mute EL ASR + original-language STT loop (`?v=20261025al`)
- You bubble keeps Persian/etc. Original text goes to the Head Engineer. Title/H1/meta unchanged.

### [2026-10-25ak] — STT transcribe never translate (`?v=20261025ak`)
- Original-language transcript to the agent. Title/H1/meta unchanged.

### [2026-10-25aj] — Correct public agent ID (`?v=20261025aj`)
- Typo `9am` → `9kam`. ID `agent_2901m5th5arfe9kamcec9ef2p42q`. Public start, no key wait. Title/H1/meta unchanged.

### [2026-10-25ai] — ConvAI token proxy (`?v=20261025ai`)
- `/colddirect-elevenlabs-token.aspx` for private agent tokens. Title/H1/meta unchanged.

### [2026-10-25ah] — ElevenLabs ConvAI live voice (`?v=20261025ah`)
- `@elevenlabs/client` + agent `agent_2901m5th5arfe9amcec9ef2p42q`. SPEAK starts live session in the existing modal. Title/H1/meta unchanged.

### [2026-10-25ag] — FaridNeural only, no SR junk, one greeting (`?v=20261025ag`)
- No OpenAI TTS. Persian Azure/Edge FaridNeural. Two-sentence LLM + wrapper greet/close. Recording placeholder. Title/H1/meta unchanged.

### [2026-10-25af] — Universal multilingual voice JSON (`?v=20261025af`)
- One JSON schema for every language. Phones + Like close guaranteed. Translate-to-X wins. Persian TTS FaridNeural/Edge/Piper only. Title/H1/meta unchanged.

### [2026-10-25ae] — Exact vocalized FA wrap (`?v=20261025ae`)
- Hardcoded display + TTS scripts. FaridNeural/onyx. No English audio on Persian. Title/H1/meta unchanged.

### [2026-10-25ad] — درود greeting + green Like close (`?v=20261025aa`)
- Custom TTS, not Vapi. Display `کولد دایرکت` / digit phones; audio `کُلد دایرِکت` + number-word groups. Title/H1/meta unchanged.

### [2026-10-25ac] — Persian display vs TTS brand/phones (`?v=20261025z`)
- Transcript digits stay clickable. TTS uses phonetic brand and Persian number words. Title/H1/meta unchanged.

### [2026-10-25ab] — Instant record-stop-reply (`?v=20261025y`)
- Mic off before playback. Title/H1/meta unchanged.

### [2026-10-25aa] — SPEAK starts with assistant id only (`?v=20261025x`)
- No assistantOverrides. Title/H1/meta unchanged.

### [2026-10-25z] — Start Vapi with assistant id only (`?v=20261025w`)
- No partial assistantOverrides. Title/H1/meta unchanged.

### [2026-10-25y] — Finish closing sentence; no auto-stop; mobile LISTEN fit (`?v=20261025v`)
- maxTokens 600, silence 45s, merge final transcript + conversation-update. Title/H1/meta unchanged.

### [2026-10-25x] — Mobile widget strip, Welcome left / Ask Your Fault right (`?v=20261025u`)
- In-flow strip under logo/menu. No overlay on phones/logo/menu. Title/H1/meta unchanged.

### [2026-10-25w] — Ask Your Fault fixed at top-left while scrolling (`?v=20261025s`)
- `position:fixed; top:10px; left:10px; z-index:99999`. Transcript ✕. Audio dock top-right. Title/H1/meta unchanged.

### [2026-10-25v] — Mobile Ask Your Fault in the dark top bar (`?v=20261025r`)
- On `max-width:768px` the widget is in `.cd-topbar`, not fixed at the bottom. Desktop layout unchanged. Title/H1/meta unchanged.

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

## 2026-10-26 - Delegated Owner verification (run 40421085010, success)
- Owner changed the CI service account from Full to Owner on the URL-prefix property. A new manual-only targeted workflow used the unchanged GSC_CREDENTIALS_JSON secret and made exactly one Indexing API diagnostic call: HTTP 200, proving the former HTTP 403 permission failure is resolved. No recurring Indexing API submission was enabled for ordinary commercial pages; Google's supported use remains JobPosting/BroadcastEvent.
- Sitemap PUT returned HTTP 204; status GET returned HTTP 200 with zero errors/warnings and isPending=true at verification time. Live sitemap, local sitemap, and the verified 48-hour backup all contain the same 131 unique URLs, including all eight new landing pages. This corrects the earlier unverified 133 count; no URLs were added to force 133.
- All 13 targeted URL Inspection calls returned HTTP 200. Current verdicts remain NEUTRAL: one stale Not found (404) for Enfield with last crawl 2026-10-19 despite the live URL returning HTTP 200, one URL unknown, seven Discovered - currently not indexed, and four Alternate page with proper canonical tag. HTTP 200 from the diagnostic or inspection APIs does not claim indexing.

## 2026-10-27 - Six watchlist canonical and internal-link verification
- Audited `/cold-room-repair-harrow/`, `/cold-room-repair-palmers-green/`, `/cold-room-repair-southgate/`, `/cold-room-repair-wood-green/`, `/commercial-fridge-repair-enfield/`, and `/commercial-fridge-repair-central-london/`. Every local copy and live page had exactly one exact self-canonical, HTTP 200 without redirect, and no `noindex`; no canonical repair was needed.
- Repaired the confirmed link gap in commit `0eb3a50587ba714dc36504af2531aff66685b195`; deploy run `40423158288` succeeded. The homepage now links directly and descriptively to all six, and each live page footer links to all six clean URLs. Added repeatable `tools/watchlist_internal_links.py --check`; synchronized 26 HTML copies; strict preflight passed 290 files with zero issues. Live post-deploy checks passed all six. Recrawl/indexing remains an outcome to measure, not a guarantee.

## 2026-10-27 - Recurring 48-hour bilingual watchlist reporting
- Kept the existing `17 3 */2 * *` schedule; no separate automation or manual run. The 48-hour GSC step now offline-selftests and inspects the exact shared 13-URL list, with the six priority pages marked. Removed commercial-page Indexing API submissions and the stale extra fourteenth URL.
- The GSC step writes machine-readable `backup-out/gsc-watchlist.json`; the bilingual mobile report includes 13-URL PASS/waiting/error totals, six-page PASS totals, and every URL verdict. Pending text continues until 13/13 PASS, then switches to completion text. Offline tests cover pending, all-PASS, missing-data, exact-list and bilingual-message behavior; YAML schedule and Python compilation checks passed.

## 2026-10-27 - Mobile voice MP3, gesture unlock and cached LISTEN
- **English:** Final commit `f61d83da88eec7fe3910a19580a73790c208d97f`; Plesk deployment run `40522462940` succeeded, and both production hosts served `20261027e` with diagnostics removed. The widget uses a persistent gesture-unlocked inline player, short MP3 chunks with prefetch, and direct cached LISTEN replay. Controlled browser replay passed with four cached chunks and no additional TTS request. Earlier live MP4/WebM checks produced the exact transcript and 173,376/193,824-byte MP3 responses; the 21,168-byte first chunk measured 2.52 seconds. `npm test` passed. Final live rechecks still passed MP4/WebM transcription but upstream TTS returned `429 RESOURCE_EXHAUSTED` and zero audio bytes, so current TTS availability is not confirmed. No physical iPhone hardware test was performed.
- **فارسی:** کامیت نهایی `f61d83da88eec7fe3910a19580a73790c208d97f` منتشر شد؛ اجرای Plesk با شناسه `40522462940` موفق بود و هر دو میزبان نسخه `20261027e` را بدون ابزار تشخیص موقت ارائه کردند. پخش‌کننده دائمی با لمس کاربر فعال می‌شود، قطعات کوتاه MP3 را پیش‌بارگیری می‌کند و LISTEN بدون درخواست تازه از نسخه ذخیره‌شده پخش می‌کند. آزمایش کنترل‌شده با چهار قطعه صوتی موفق بود و شمار درخواست TTS تغییر نکرد. بررسی‌های قبلی MP4/WebM متن دقیق و پاسخ‌های MP3 با حجم ۱۷۳٬۳۷۶ و ۱۹۳٬۸۲۴ بایت را تأیید کردند؛ قطعه اول ۲۱٬۱۶۸ بایتی در ۲٫۵۲ ثانیه رسید. آزمون‌های `npm test` موفق بودند. در بررسی نهایی، رونویسی هر دو قالب موفق بود اما TTS با خطای `429 RESOURCE_EXHAUSTED` و بدون داده صوتی پاسخ داد؛ بنابراین دسترسی فعلی TTS تأیید نمی‌شود و آزمایش روی iPhone واقعی انجام نشده است.

## 2026-10-27 - Single-summary TTS and zero-silence native fallback
- **English:** Commit `4e6fc42e8949934d7874d358b77e828c80ab4f49`; Plesk run `40530373086` succeeded and both hosts served `20261027f`. One diagnosis now creates one TTS request for a maximum-three-sentence/45-word summary instead of four chunk requests. Live real-429 verification returned `TTS_UNAVAILABLE` after exactly one Gemini attempt with a 37-word summary. Only the primary Gemini key was present in Vercel; optional secondary Gemini/Azure/ElevenLabs/OpenAI support was regression-tested with mocks, not claimed as live provider success. Forced-429 browser testing invoked one native en-GB summary and LISTEN replayed it without another TTS request. Controlled MP3 caching and replay also passed with one request. `npm test` passed. Physical-iPhone/audible-hardware playback was not tested and 100% uptime is not guaranteed.
- **فارسی:** کامیت `4e6fc42e8949934d7874d358b77e828c80ab4f49` منتشر شد؛ اجرای Plesk با شناسه `40530373086` موفق بود و هر دو میزبان نسخه `20261027f` را ارائه کردند. هر تشخیص اکنون به‌جای چهار درخواست، فقط یک درخواست TTS برای خلاصه‌ای حداکثر سه‌جمله‌ای و ۴۵ کلمه‌ای ارسال می‌کند. بررسی زنده در شرایط واقعی 429 پس از فقط یک تلاش Gemini، پاسخ `TTS_UNAVAILABLE` با خلاصه ۳۷ کلمه‌ای داد. در Vercel فقط کلید اصلی Gemini موجود بود؛ پشتیبانی اختیاری از Gemini دوم، Azure، ElevenLabs و OpenAI با آزمون شبیه‌سازی‌شده بررسی شد، نه با سرویس زنده. در آزمایش اجباری 429، خلاصه بومی en-GB یک بار فراخوانی شد و LISTEN آن را بدون درخواست TTS جدید تکرار کرد. کش و پخش مجدد MP3 نیز با یک درخواست موفق بود و آزمون‌های `npm test` پاس شدند. پخش شنیداری روی iPhone واقعی آزمایش نشده و uptime صددرصدی تضمین نمی‌شود.

## 2026-10-27 - Speech-first mobile capture and quota-safe expert diagnosis
- **English:** Commit `dc845e8984342b3e6978e144c46c367fd1194dce`; Plesk run `40554823797` succeeded and both hosts served `20261027g`. SpeechRecognition is now the primary capture path with live interim input and automatic text submission after 1.5 seconds of silence. MediaRecorder is fallback-only, with a 6-second maximum, 2-second post-speech silence stop, visible countdown, and `requestData` before `stop`. Live browser verification proved one text-only diagnosis with zero audio bytes, one native en-GB utterance after forced TTS 429, and LISTEN replay without another TTS request. Recorder verification proved `requestData → stop`, a non-empty 344-character base64 MP4 payload, and native fallback speech. Backend forced-429 tests tried `3.6 → 2.5 → 2.0 → 2.0-lite → 1.5`, then returned HTTP 200 expert guidance rather than a hearing error. The final real live MP3 transcription succeeded through Gemini; it was not a real-429 test. `npm test`, HTML cache-only diff checks, asset paths, and JSON-LD validation passed. Physical-iPhone capture and audible playback were not tested.
- **فارسی:** کامیت `dc845e8984342b3e6978e144c46c367fd1194dce` منتشر شد؛ اجرای Plesk با شناسه `40554823797` موفق بود و هر دو میزبان نسخه `20261027g` را ارائه کردند. SpeechRecognition اکنون مسیر اصلی ورودی است، متن زنده نمایش می‌دهد و پس از ۱٫۵ ثانیه سکوت آن را بدون آپلود صوت ارسال می‌کند. MediaRecorder فقط پشتیبان است؛ حداکثر ۶ ثانیه، توقف پس از ۲ ثانیه سکوت، شمارش معکوس و تخلیه داده نهایی پیش از توقف دارد. آزمون مرورگر زنده یک تشخیص متنی بدون بایت صوتی، صدای بومی en-GB پس از خطای اجباری 429 و پخش LISTEN بدون درخواست تازه را تأیید کرد. در مسیر ضبط، ترتیب `requestData → stop` و بار غیرخالی MP4 با ۳۴۴ نویسه base64 تأیید شد. آزمون 429 پنج مدل را بررسی و سپس راهنمای مهندسی با HTTP 200 بازگرداند. رونویسی نهایی MP3 واقعی از طریق Gemini موفق بود و آزمون 429 واقعی نبود. تمامی آزمون‌ها و اعتبارسنجی‌ها پاس شدند، اما ضبط و پخش شنیداری روی iPhone واقعی انجام نشده است.

## 2026-10-27 - Mandatory phone and 5-Star Review CTA in every voice answer
- **English:** Commit `a4e3623b7989fda0a0ea7b9c17c8b5bc57905be3`; Plesk run `40562705351` succeeded and both production hosts served `20261027h`. Gemini, the rule-based engine, `/api/voice-tts`, and native browser speech now enforce the same written/spoken telephone and green Like/5-Star Review close. The spoken-summary cap is 72 words; the technical allowance shrinks dynamically so the close is retained. Live browser verification made one diagnosis request and one TTS request. Real Gemini TTS returned `429 RESOURCE_EXHAUSTED`/`TTS_UNAVAILABLE` with zero audio bytes, after which native speech used a 68-word utterance containing technical advice first, then both formatted phone numbers and the exact review close. The written Head Engineer bubble ended with the display CTA and clickable `tel:+442039524822` and `tel:+447983759320` links. LISTEN repeated the same utterance with the TTS request count unchanged at one. `npm test` passed. This was native-fallback pipeline verification, not live MP3 generation or physical-device audible playback.
- **فارسی:** کامیت `a4e3623b7989fda0a0ea7b9c17c8b5bc57905be3` منتشر شد؛ اجرای Plesk با شناسه `40562705351` موفق بود و هر دو میزبان نسخه `20261027h` را ارائه کردند. Gemini، موتور قاعده‌محور، `/api/voice-tts` و گفتار بومی مرورگر اکنون فراخوان یکسان تلفن و Like/نظر پنج‌ستاره را در پاسخ نوشتاری و گفتاری اعمال می‌کنند. سقف خلاصه گفتاری ۷۲ کلمه است و سهم متن فنی به‌صورت پویا کم می‌شود تا پیام پایانی حذف نشود. آزمون زنده یک درخواست تشخیص و یک درخواست TTS ثبت کرد. Gemini واقعی خطای `429 RESOURCE_EXHAUSTED` و `TTS_UNAVAILABLE` بدون بایت صوتی بازگرداند؛ سپس گفتار بومی ۶۸ کلمه‌ای ابتدا راهنمای فنی و سپس هر دو شماره و درخواست نظر پنج‌ستاره را ارائه کرد. حباب نوشتاری Head Engineer با فراخوان و پیوندهای تلفن کلیک‌پذیر پایان یافت. LISTEN همان متن را بدون افزایش شمار درخواست TTS تکرار کرد و `npm test` موفق بود. این آزمون مسیر پشتیبان بومی را تأیید کرد، نه تولید موفق MP3 یا پخش شنیداری روی دستگاه واقعی.

## 2026-10-27 - Ten money-keyword coverage, links and bilingual GSC tracking
- **English:** Implementation commit `cd15fb7c60c56dae6456bbe6848c3aee8a2884b7`; deployment run `40576649545` succeeded. Nine canonical hubs cover all ten families (cellar and cellar cooler intentionally share one hub). Added concise semantic body copy to 36 money-page copies and varied internal anchors to 38 supporting-page copies; 462 mesh targets now have zero pending links. Added the permanent target matrix and specific-first query classifier, full family/variant GSC output, and bilingual metrics in the existing 48-hour mobile report (`17 3 */2 * *`). Protected titles, descriptions and H1s remained unchanged; no new URLs or sitemap submission were needed.
- **Live verification:** Smoke tests, config parity (939 URL probes), production pages, production audit and SEO integrity passed. All nine live hubs contain their new semantic copy, one self-canonical, no `noindex`, and valid Service/FAQPage JSON-LD; rendered-browser schema verification passed. The live sitemap remains intact at 131 URLs.
- **GSC 2026-10-19 to 2026-10-25 vs previous week:** Sitewide 99 clicks (+60%), 7,068 impressions (+3%), average position 29.9 (improved 1.2). Families: cold room 13/69/8.1; commercial fridge 16/112/14.1; commercial freezer 0/77/12.3; fridge 16/250/11.6; freezer 5/76/14.6; cellar 0/0/no data; cellar cooler 0/15/15.5; air conditioning 0/4/49.5; catering 0/3/10.3; commercial appliances 0/10/12.6 (clicks/impressions/impression-weighted position). Currently 0/10 average Top 3; URL Inspection remains 0/13 PASS and 13 waiting. Rankings and indexing are measured outcomes, not guarantees.
- **فارسی:** کامیت `cd15fb7c60c56dae6456bbe6848c3aee8a2884b7` با اجرای موفق انتشار `40576649545` زنده شد. هر ۹ صفحه canonical هر ده خانواده را پوشش می‌دهند؛ متن معنایی مفید، پیوندهای داخلی متنوع، ماتریس دائمی هدف و گزارش دوزبانه ۴۸ساعته اضافه شد. متادیتای سالم تغییر نکرد و URL تازه‌ای لازم نبود. تمامی بررسی‌های زنده و اسکیمای Service/FAQPage در ۹ صفحه موفق بود. در گزارش ۱۹ تا ۲۵ اکتبر، ۹۹ کلیک (+۶۰٪)، ۷٬۰۶۸ نمایش (+۳٪) و میانگین موقعیت ۲۹٫۹ ثبت شد. هنوز ۰ از ۱۰ خانواده میانگین Top 3 دارد و ۱۳ نشانی در انتظار نمایه‌سازی‌اند؛ رتبه و نمایه‌سازی تضمین نمی‌شود.

## 2026-10-27 - Ranking movement reporting and live voice CTA re-verification
- **English:** Kept the existing `17 3 */2 * *` schedule. Both GSC/report self-tests passed; the bilingual mobile family rows now include signed WoW position movement (negative means improvement), while the same report continues all 13 URL Inspection checks until 13/13 PASS. No manual run or notification was sent. Live `20261027h` browser verification submitted a refrigeration fault and received one diagnosis HTTP 200 plus one TTS HTTP 200. Upstream Gemini returned real `429 RESOURCE_EXHAUSTED` with zero audio bytes, then native browser speech produced a 68-word utterance containing technical advice, `0203 952 4822`, `07983 759320`, and the exact green Like/5-Star Review close. The written Head Engineer bubble had both clickable phone links and the display review CTA. LISTEN repeated the identical utterance with no additional TTS request. Voice regression tests passed. This confirms the browser/native-fallback pipeline, not physical-device audible playback or generated-MP3 success.
- **فارسی:** برنامه موجود `17 3 */2 * *` حفظ شد و گزارش دوزبانه اکنون تغییر هفتگی رتبه را هم نمایش می‌دهد؛ بررسی ۱۳ URL تا رسیدن به ۱۳/۱۳ PASS ادامه دارد. در آزمون زنده نسخه `20261027h`، پاسخ نوشتاری هر دو شماره کلیک‌پذیر و درخواست Like/نظر پنج‌ستاره را نشان داد. Gemini خطای واقعی 429 داد، اما گفتار بومی ۶۸ کلمه‌ای راهنمای فنی، هر دو شماره و فراخوان پایانی را ارائه کرد. LISTEN همان متن را بدون درخواست TTS جدید تکرار کرد و آزمون‌های رگرسیون موفق بودند. این نتیجه مسیر بومی مرورگر را تأیید می‌کند، نه پخش شنیداری روی دستگاه واقعی یا تولید MP3.
