# ColdDirect Agent Memory and Lessons

Last verified: 2026-10-27. Machine-readable state: `docs/ai-memory/agent-state.json`.

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
- Live sitemap verified with 131 unique URLs and valid lastmod values. Live smoke tests, production pages, and live config parity passed. The earlier 133 count was corrected after live, local, and verified-backup comparisons all showed the same 131 URLs, including all eight new landing pages.
- Vercel voice mirror commit: `7100b646`; deployment run `40369714526` completed successfully for merged SHA `d30991dd`.
- Voice production fix verified after reconnecting Vercel to GitHub: production is Ready on `1ed0ef07`. Three consecutive live API checks passed and two complete browser audits passed with microphone HTTP 200, useful typed diagnosis, spoken playback, booking and contact controls, and zero console/HTTP errors. Common typed faults have a local diagnostic fallback; unclear microphone input returns structured HTTP 200. Vercel had been disconnected, so earlier Git pushes did not update production—always verify the displayed production commit.
- First full 48-hour run `40371951644`: live health, redirect/config parity, schema/SEO integrity, GSC performance retrieval, and bilingual ntfy delivery succeeded. Backup failed integrity because live files changed between FTP SIZE and RETR. Indexing API submission returned HTTP 403, although URL Inspection and performance queries worked.
- Third run `40378611708`: verified 629-file backup (292 HTML, zero skips), independent SHA-256 manifest re-check, 90-day artifact, auto-SEO, health, redirects/config, schema, GSC, and ntfy delivery succeeded. Voice remained failed. The run predated the corrected headline logic, so a corrected warning notification was sent separately; future reports derive their status from every step outcome.
- Final verification run `40410829821` completed successfully with every individual step passing: 629-file backup (292 HTML, zero skips), independent SHA-256 manifest re-check, 90-day artifact, auto-SEO, live health, redirects/config, schema/SEO integrity, voice API, GSC, bilingual report, and job report. Downloaded logs confirm both headlines correctly state that all requested checks passed; ntfy accepted the report with HTTP 200. GSC reported 1 of 14 watchlist URLs indexed and 13 still waiting; Indexing API submission remains unavailable with HTTP 403.
- The unused Vercel deployment token named `ColdDirect production deploy 2026-10-26` was permanently revoked after GitHub reconnection had restored production deployment.
- Targeted GSC Owner verification run `40421085010` passed after the CI account was changed from Full to Owner: one Indexing API permission diagnostic returned HTTP 200, sitemap PUT returned 204, sitemap status returned 200 with zero errors/warnings, and all 13 URL Inspection calls returned 200. All 13 verdicts remain NEUTRAL (one stale 404 inspection, one unknown, seven discovered-not-indexed, four proper-canonical alternates). Do not enable recurring Indexing API calls for ordinary commercial pages; supported use is limited to JobPosting/BroadcastEvent.

## Verified work on 2026-10-27

- Audited Harrow, Palmers Green, Southgate and Wood Green cold-room pages plus Enfield and Central London commercial-fridge pages. All local deployable copies and live pages already had exactly one exact self-referencing canonical, HTTP 200 without redirects, and no `noindex`; the GSC alternate/404/unknown verdicts were not evidence of a current canonical defect.
- Found and repaired the real internal-link gap: the homepage originally linked only to Enfield, and none of the six pages had direct footer links to the set. Commit `0eb3a50587ba714dc36504af2531aff66685b195`, deployment run `40423158288` succeeded. Live post-deployment verification passed for all six: direct descriptive homepage links and footer navigation containing all six final trailing-slash URLs. Added idempotent `tools/watchlist_internal_links.py --check` and synchronized 26 HTML copies. Strict preflight checked 290 files with zero issues. Indexing on the next crawl is not guaranteed; re-inspect GSC after recrawl.
- Updated the existing 48-hour workflow (schedule remains `17 3 */2 * *`) to inspect the exact shared 13-URL watchlist, including the six priority pages, on every run. Removed recurring Indexing API submissions for these commercial pages. `gsc_weekly_report.py` writes `backup-out/gsc-watchlist.json`; `report_48h.py` turns it into bilingual mobile totals plus every URL verdict, marks the six pages, continues pending updates until 13/13 PASS, and then reports completion. Offline pending/all-PASS/mobile tests and YAML schedule validation passed; no manual 48-hour run was triggered.
- Mobile voice playback fix finalized in `f61d83da88eec7fe3910a19580a73790c208d97f`; Plesk deployment run `40522462940` succeeded, and both Plesk and Vercel served widget cache version `20261027e` with temporary diagnostics removed. The widget primes a persistent inline audio element from user gestures, uses chunked/prefetched MP3 audio, and starts cached LISTEN replay directly. A controlled browser test cached four chunks and replayed them with the TTS request count unchanged at 4; playback was active at inspection time.
- Earlier live spoken-fixture verification returned the exact MP4/WebM transcript and full MP3 payloads of 173,376 and 193,824 bytes; the short first chunk was 21,168 bytes with a measured 2.52-second API round trip. `npm test` passed all voice, asset-path and JSON-LD checks. Final repeated live checks still transcribed both MP4 and WebM correctly, but TTS returned upstream `429 RESOURCE_EXHAUSTED` with zero audio bytes. Do not claim current end-to-end TTS availability from HTTP 200 alone; no physical iPhone hardware test was performed.
- Zero-silence fallback finalized in `4e6fc42e8949934d7874d358b77e828c80ab4f49`; Plesk run `40530373086` succeeded and both production hosts served `20261027f`. Removed per-sentence TTS calls: each diagnosis now has one concise summary capped at three sentences and 45 words. The live real-429 response contained exactly one Gemini attempt and 37 summary words. Optional secondary Gemini/Azure/ElevenLabs/OpenAI failover is implemented for configured keys; Vercel environment-name inspection found only the primary Gemini key, so no live secondary-provider success is claimed.
- Native `speechSynthesis` is gesture-primed and used on TTS failure, empty audio, or MP3 playback failure on desktop and mobile. Forced-429 browser verification produced one TTS request and one native en-GB summary; LISTEN replayed it with the TTS count unchanged. A separate controlled MP3 test used one request and cached LISTEN replay without another request. `npm test` passed, including mocked provider failover. These are browser/API pipeline checks, not physical-iPhone or audible-hardware verification; never promise 100% uptime.
- Speech-first mobile capture and quota-safe diagnosis finalized in `dc845e8984342b3e6978e144c46c367fd1194dce`; Plesk run `40554823797` succeeded and both hosts served `20261027g`. Native SpeechRecognition now provides live interim input and submits text after 1.5 seconds of silence; MediaRecorder is fallback-only with a 6-second limit, 2-second silence detection, countdown, and `requestData` before `stop`. Live browser tests proved text-only submission with zero audio bytes, native en-GB playback after forced TTS 429, cached LISTEN without another request, and non-empty MP4 upload with correct flush ordering. Backend forced-429 tests tried five models then returned HTTP 200 expert guidance; the final real live MP3 transcription succeeded through Gemini, so do not describe that final check as a real 429. Physical-iPhone capture/audible playback remains untested.
- فارسی: اصلاح ورودی صوتی و تشخیص در کامیت `dc845e8984342b3e6978e144c46c367fd1194dce` منتشر شد؛ اجرای Plesk با شناسه `40554823797` موفق بود و هر دو میزبان نسخه `20261027g` را ارائه کردند. تشخیص گفتار بومی متن زنده می‌سازد و پس از ۱٫۵ ثانیه سکوت آن را بدون آپلود صوت ارسال می‌کند. ضبط جایگزین پس از ۶ ثانیه یا ۲ ثانیه سکوت متوقف می‌شود و داده نهایی MP4 پیش از توقف تخلیه می‌گردد. خطای اجباری 429 در آزمون‌ها با راهنمای مهندسی و صدای بومی پاسخ داده شد، اما رونویسی نهایی MP3 واقعی از طریق Gemini موفق بود؛ این آزمون نهایی خطای واقعی 429 نبود. ضبط و پخش شنیداری روی iPhone واقعی هنوز تأیید نشده است.
- Mandatory written/spoken phone and review CTA finalized in `a4e3623b7989fda0a0ea7b9c17c8b5bc57905be3`; Plesk run `40562705351` succeeded and both hosts served `20261027h`. The TTS summary cap is now 72 words, with the technical budget reduced dynamically so the CTA is never truncated. Live browser verification produced one diagnosis, one real Gemini TTS attempt returning `429 RESOURCE_EXHAUSTED`, and one 68-word native utterance containing technical advice, both formatted phone numbers, and the exact green Like/5-Star Review close. The written Head Engineer bubble ended with the display CTA and both `tel:` links. LISTEN repeated the identical utterance with the TTS count unchanged. This verifies native fallback, not generated-MP3 success or physical-device audible playback.
- فارسی: فراخوان تلفن و نظر پنج‌ستاره در پاسخ نوشتاری و گفتاری در کامیت `a4e3623b7989fda0a0ea7b9c17c8b5bc57905be3` نهایی شد؛ اجرای Plesk با شناسه `40562705351` موفق بود و هر دو میزبان نسخه `20261027h` را ارائه کردند. سقف خلاصه گفتاری ۷۲ کلمه است و بودجه متن فنی به‌صورت پویا کم می‌شود تا فراخوان پایانی حذف نشود. آزمون مرورگر زنده یک تشخیص، یک تلاش واقعی Gemini TTS با خطای `429 RESOURCE_EXHAUSTED` و یک گفتار بومی ۶۸ کلمه‌ای شامل راهنمای فنی، هر دو شماره و درخواست Like/نظر پنج‌ستاره را تأیید کرد. حباب نوشتاری نیز با فراخوان و هر دو پیوند تلفن پایان یافت و LISTEN همان متن را بدون درخواست TTS تازه تکرار کرد. این نتیجه پخش بومی را تأیید می‌کند، نه تولید موفق MP3 یا پخش شنیداری روی دستگاه واقعی.

## Permanent Top-3 Ranking Target Matrix

Top 3 / Page 1 is the business target, never a guaranteed outcome. Measure Google Search Console results and do not churn healthy titles/H1s on a schedule. The machine-readable mapping and query classifier live in `tools/money_target_matrix.py`; curated body copy remains in `tools/money_data.py`.

1. `cold room repair london` → `/cold-room-repair-london/`
2. `commercial fridge repair london` → `/commercial-fridge-repair-london/`
3. `commercial freezer repair london` → `/commercial-freezer-repair-london/`
4. `fridge repair london` → `/fridge-repair-london/`
5. `freezer repair london` → `/freezer-repair-london/`
6. `cellar repair london` → `/cellar-cooler-repair-london/`
7. `cellar cooler repair london` → `/cellar-cooler-repair-london/` (same canonical hub as cellar repair)
8. `air conditioning repair london` → `/air-conditioning-repair-london/`
9. `catering repair london` → `/catering-repair-london/`
10. `commercial appliances repair london` → `/commercial-appliances-repair-london/` (also owns commercial catering equipment intent; never use the canonicalised commercial-catering duplicate)

Permanent semantic modifiers: repair/repairs, service/services, maintenance, appropriate installation intent, breakdown/fix/diagnostics/call-out, emergency/24-7/same-day/urgent/fast-response, near-me/local, engineer/engineers/technician/specialist/company/commercial/industrial. Use natural word orders and useful technical copy, never mechanical permutation lists or doorway pages.

The existing 48-hour GSC workflow reports clicks, impressions, and impressions-weighted average position for all ten families and their London/local variants. Specific-first classification prevents commercial fridge/freezer and commercial catering/appliance queries from also inflating generic rows. Full variant data goes to `backup-out/gsc-money-keywords.json`; `tools/report_48h.py` includes bilingual family metrics in the mobile report.

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
