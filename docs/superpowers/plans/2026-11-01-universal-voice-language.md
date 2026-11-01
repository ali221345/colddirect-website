# Universal Voice Language Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Answer every customer natively in the detected language, always include both contact channels, and make speech synthesis recover from retryable upstream failures.

**Architecture:** Extend the existing shared voice core with validated BCP-47 routing and six native fallback profiles. Keep Gemini as the model-led universal diagnosis/speech provider, preserve its documented automatic TTS language detection, pass explicit locales to Azure, and reuse the same routing rules in the browser widget. Add bounded provider retries within the existing 22-second budget.

**Tech Stack:** Node.js/CommonJS, Vercel serverless functions, browser JavaScript, Gemini REST API, Azure SSML, Node `assert`, Prettier.

## Global Constraints

- Do not modify locked HTML, sitemap files, SEO pipelines, or unrelated dependencies.
- Arabic must never default to Persian; browser locale must not determine customer language.
- Always include `07983 759320` and `info@colddirect.co.uk` in written and spoken responses.
- Retain native fallbacks for English, Persian, Turkish, Arabic, Spanish, and French; other languages remain model-led.
- Gemini 3.8 TTS automatically detects input language; do not add an unsupported `languageCode` field to `speechConfig`.
- Keep CORS and HTTP response contracts intact and retain native browser speech fallback.
- Finish with `npm test`, `python tools/check_locked_state.py`, four-language live checks, commit/push, and deployment verification.

---

### Task 1: Shared language routing and native response profiles

**Files:**
- Modify: `lib/cd-voice-core.js:89-207`
- Test: `tools/test_voice_diagnose.js:49-60`

**Interfaces:**
- Produces: `lockLang(text, hint) -> { code, bcp, label }`, preserving validated model hints when no stronger text evidence exists.
- Produces: native `ensureGreeting`, `displayCta`, `spokenCta`, `withoutClose`, `ensureClose`, and `ttsScript` behavior for `en`, `fa`, `tr`, `ar`, `es`, and `fr`.

- [ ] **Step 1: Write failing language and contact regression tests**

Add assertions equivalent to:

```js
const languageCases = [
  ["یخچال صنعتی سرد نمی‌کند", "", "fa-IR"],
  ["التجارية لا تبرد", "", "ar-SA"],
  ["Merhaba, ticari buzdolabı soğutmuyor", "", "tr-TR"],
  ["Mi nevera comercial no enfría", "", "es-ES"],
  ["Bonjour, mon réfrigérateur ne refroidit pas", "", "fr-FR"],
  ["Das Kühlgerät ist warm", "de-DE", "de-DE"]
];
for (const [text, hint, expected] of languageCases) {
  assert.strictEqual(core.lockLang(text, hint).bcp, expected);
}
for (const lang of ["en", "fa", "tr", "ar", "es", "fr"]) {
  const display = core.ensureClose(core.ensureGreeting("Technical diagnosis.", lang, false), lang);
  const spoken = core.ttsScript(core.ensureGreeting("Technical diagnosis.", lang, true), lang);
  for (const value of [display, spoken]) {
    assert.ok(value.includes("07983 759320"));
    assert.ok(value.includes("info@colddirect.co.uk"));
  }
}
```

- [ ] **Step 2: Run the tests and confirm the expected failure**

Run: `node tools/test_voice_diagnose.js`

Expected: FAIL because Arabic currently returns `fa-IR`, Turkish/Spanish/French return `en-GB`, and CTAs omit the email.

- [ ] **Step 3: Implement the minimal shared routing profiles**

Add a `LANGS` profile map keyed by `en`, `fa`, `tr`, `ar`, `es`, and `fr`. Each profile contains `bcp`, `label`, native `greeting`, native `display` CTA, and native `spoken` CTA. Use these exact contact tokens in every CTA: `0203 952 4822`, `07983 759320`, and `info@colddirect.co.uk`.

Implement routing in this order:

```js
function normalizeBcp(value) {
  var tag = String(value || "").trim().replace(/_/g, "-");
  if (!/^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$/.test(tag)) return "";
  try { return Intl.getCanonicalLocales(tag)[0] || ""; }
  catch (e) { return ""; }
}

function lockLang(text, hint) {
  var raw = String(text || "");
  var normalized = normalizeBcp(hint);
  var hinted = normalized.split("-")[0].toLowerCase();
  var code = "";
  if (/[\u067E\u0686\u0698\u06AF]/.test(raw) || /(?:سلام|یخچال|سرد|دستگاه|مهندس)/.test(raw)) code = "fa";
  else if (/[\u0600-\u06FF]/.test(raw)) code = hinted === "fa" ? "fa" : "ar";
  else if (/[ışğİŞĞ]/.test(raw) || /\b(?:merhaba|buzdolabı|soğutmuyor|çalışmıyor|arıza)\b/i.test(raw)) code = "tr";
  else if (/[¿¡ñÑ]/.test(raw) || /\b(?:hola|nevera|enfría|funciona|avería)\b/i.test(raw)) code = "es";
  else if (/[àâçéèêëîïôûùüÿœ]/i.test(raw) || /\b(?:bonjour|réfrigérateur|refroidit|fonctionne|panne)\b/i.test(raw)) code = "fr";
  else if (/\b(?:the|and|is|not|fridge|freezer|compressor|engineer)\b/i.test(raw)) code = "en";
  else if (hinted) code = hinted;
  else code = "en";
  if (LANGS[code]) return { code: code, bcp: LANGS[code].bcp, label: LANGS[code].label };
  return { code: code, bcp: normalized, label: normalized };
}
```

Make greeting/CTA helpers select `LANGS[lang]`. For an unknown model-led language, preserve the model's native greeting/close rather than inserting English; `parseOut` will still require the contact details and review request. Keep legacy English/Persian CTA removal and extend removal to all six current profiles.

- [ ] **Step 4: Run the shared tests**

Run: `node tools/test_voice_diagnose.js`

Expected: the new language/contact assertions pass; any old assertions that intentionally omit email are updated to require it before proceeding.

### Task 2: Universal diagnosis and native local fallbacks

**Files:**
- Modify: `api/voice-diagnose.js:11-57,120-161,203-237`
- Test: `tools/test_voice_diagnose.js`

**Interfaces:**
- Consumes: Task 1 `lockLang`, native greeting/CTA helpers.
- Produces: `parseOut(modelText, audioMode, inputText)` and native `language`, `display_text`, and `spoken_text` responses.

- [ ] **Step 1: Add failing diagnosis routing tests**

Mock `core.geminiJson` to return Turkish, Arabic, Spanish, and French JSON with matching `language`, transcript, display, and spoken fields. Post each query and assert:

```js
assert.strictEqual(reply.json.language, expectedBcp);
assert.ok(reply.json.display_text.includes("07983 759320"));
assert.ok(reply.json.display_text.includes("info@colddirect.co.uk"));
assert.ok(reply.json.spoken_text.includes("info@colddirect.co.uk"));
```

Add a conflict case with Turkish input, an English model answer, and a false `tr-TR` model hint; assert that the answer is rejected rather than returned as Turkish. Add local-fallback cases for all six profiles and assert the expected BCP-47 code plus both contact channels.

- [ ] **Step 2: Run the diagnosis tests and confirm failure**

Run: `node tools/test_voice_diagnose.js`

Expected: FAIL on universal prompt/routing, native fallback content, and mandatory email.

- [ ] **Step 3: Update the system prompt and output validation**

Replace the English/Persian-only instructions with:

```js
"Detect the customer's language independently from any browser or interface locale. Answer 100% natively in that exact language; never translate it into English or Persian. Arabic is ar-SA and Persian is fa-IR.",
"Start with a polite natural greeting identifying yourself as the Head Engineer at ColdDirect in the customer's language.",
"Finish in the customer's language with 0203 952 4822, 07983 759320, info@colddirect.co.uk, and a polite request to tap the green Like and 5-Star Review button.",
"JSON only: {\"language\":\"validated BCP-47 code\",\"transcript\":\"exact spoken words\",\"display_text\":\"native on-screen answer\",\"spoken_text\":\"same native answer for speech\"}"
```

Pass typed input into `parseOut`. Determine expected input language from typed text, or from the transcript for audio, and reject high-confidence language conflicts. Require `/info@colddirect\.co\.uk/i` plus the existing phone check in display and spoken output. Keep structured diagnostics and existing model failover.

Add concise native generic safety/diagnosis text for Turkish, Arabic, Spanish, and French in `localDiagnosis`; retain the existing English equipment-specific rules and Persian fallback. Use the Task 1 helpers so greeting, contact details, and review request are appended exactly once.

- [ ] **Step 4: Run the diagnosis tests**

Run: `node tools/test_voice_diagnose.js`

Expected: PASS, including language-conflict rejection, native fallbacks, redaction, and existing audio/model tests.

### Task 3: Reliable dynamic TTS and widget playback

**Files:**
- Modify: `api/voice-tts.js:46-149,170-231`
- Modify: `assets/js/colddirect-voice-bar.js:431-452,611-644,736-859,1044-1056`
- Synchronize: `colddirect-public-html/assets/js/colddirect-voice-bar.js`
- Test: `tools/test_voice_tts.js`
- Test: `tools/test_voice_frontend.js`

**Interfaces:**
- Consumes: validated BCP-47 values from Task 1.
- Produces: TTS responses retaining the request language, explicit Azure `xml:lang`/voice selection, and at most two attempts per provider within 22 seconds.

- [ ] **Step 1: Add failing TTS and widget tests**

Add a Gemini `NO_AUDIO` response followed by valid audio and assert two upstream calls and `ok === true`. Keep a permanent `429` case but expect two bounded attempts before failure/fallback. Capture Azure SSML for `tr-TR` and `ar-SA` and assert matching `xml:lang` and language-appropriate neural voices. Assert spoken text retains the greeting and contains the email.

Add frontend source assertions that:

```js
assert.ok(!source.includes("navigator.language"), "Browser locale must not select the customer language");
assert.ok(source.includes("u.lang = lang"), "Native speech must preserve the response BCP-47 tag");
assert.ok(source.includes("info@colddirect.co.uk"), "Browser speech must include email");
assert.ok(!/replace\(\/Hello\\\. I am the Head Engineer/.test(source), "The greeting must remain in speech");
```

- [ ] **Step 2: Run the TTS and frontend tests and confirm failure**

Run: `node tools/test_voice_tts.js && node tools/test_voice_frontend.js`

Expected: FAIL on `NO_AUDIO` retry, dynamic Azure locale, preserved greeting, and email coverage.

- [ ] **Step 3: Implement bounded retries and dynamic language propagation**

Use nested provider/attempt loops with at most two attempts per provider. Retry only network/empty-audio/retryable upstream failures:

```js
function retryable(result) {
  return !result.http || result.http === 408 || result.http === 429 || result.http >= 500 ||
    (result.http === 200 && /^(?:NO_AUDIO|EMPTY_AUDIO)$/.test(result.status));
}
```

Keep `remaining = 22000 - elapsed`, stop when less than 1500 ms remains, and cap each request at 9000 ms. Do not retry non-retryable 4xx responses. Treat HTTP 200 with no audio as a failure and record every attempt.

Change provider closures to pass `locked.bcp`. Leave Gemini `speechConfig` limited to the documented voice configuration because Gemini auto-detects language. For Azure, use the BCP-47 tag in SSML and this default voice map: `en-GB-RyanNeural`, `fa-IR-FaridNeural`, `tr-TR-AhmetNeural`, `ar-SA-HamedNeural`, `es-ES-AlvaroNeural`, `fr-FR-HenriNeural`. Preserve explicit `AZURE_SPEECH_VOICE` override behavior.

Remove greeting-stripping regexes from server and widget summaries while retaining the 72-word budget. Mirror the six native CTA profiles in the widget, use `u.lang = lang`, select native voices by the language's base code, and replace the `navigator.language` recognition fallback with `sessionLang || "en-GB"`. Copy the final root widget file byte-for-byte to `colddirect-public-html/assets/js/colddirect-voice-bar.js`.

- [ ] **Step 4: Run targeted and full local verification**

Run: `node tools/test_voice_tts.js && node tools/test_voice_frontend.js && npm test && python tools/check_locked_state.py`

Expected: all tests PASS and lock check prints `ALL LOCKS INTACT` with `HTML Updated: 0`.

Run: `npx prettier --check lib/cd-voice-core.js api/voice-diagnose.js api/voice-tts.js assets/js/colddirect-voice-bar.js colddirect-public-html/assets/js/colddirect-voice-bar.js tools/test_voice_diagnose.js tools/test_voice_tts.js tools/test_voice_frontend.js`

Expected: all listed files pass formatting.

### Task 4: Live verification and deployment

**Files:**
- Verify only; no locked HTML changes.

**Interfaces:**
- Consumes: the completed local implementation.
- Produces: a pushed `main` commit and verified production behavior.

- [ ] **Step 1: Commit and push the approved scope**

Run:

```bash
git add lib/cd-voice-core.js api/voice-diagnose.js api/voice-tts.js assets/js/colddirect-voice-bar.js colddirect-public-html/assets/js/colddirect-voice-bar.js tools/test_voice_diagnose.js tools/test_voice_tts.js tools/test_voice_frontend.js docs/superpowers/plans/2026-11-01-universal-voice-language.md docs/superpowers/specs/2026-11-01-universal-voice-language-design.md
git commit -m "fix: universal multilingual voice diagnosis and TTS"
git pull --rebase origin main
git push origin main
```

Expected: pre-commit formatting succeeds and the branch is pushed without changing locked HTML.

- [ ] **Step 2: Verify deployment workflows**

Use the repository's GitHub CLI authentication to inspect the latest `deploy` run for the pushed commit and the live Vercel health endpoints. Expected: workflow conclusion `success`; diagnosis and TTS health GET return 200 with the expected service names.

- [ ] **Step 3: Run four-language live API and speech checks**

For English, Persian, Turkish, and Arabic, POST one commercial refrigeration fault to `https://colddirect-website.vercel.app/api/voice-diagnose` using origin `https://www.colddirect.co.uk`. Assert `ok`, expected BCP-47 language, native greeting/technical text/review request, phone, and email. POST each `spoken_text` and returned `language` to `/api/voice-tts`; require `ok: true`, non-empty decodable audio, and the same returned language. Do not treat HTTP 200 alone as success. Save audio under the workspace and run the existing transcription round-trip tooling where available.

- [ ] **Step 4: Recheck CORS and the live widget**

Verify preflight remains 204 and `Access-Control-Allow-Origin` is exactly `https://www.colddirect.co.uk`. In the live widget, submit the four typed faults, confirm rendered native responses, audio or native-language fallback, no failed network requests, and no console errors. Microphone capture may be reported as unverified if browser permission is unavailable; do not claim it passed.

- [ ] **Step 5: Final integrity check and report**

Run `npm test` and `python tools/check_locked_state.py` once more on the final rebased tree. Report only observed outcomes, including commit/run identifiers, four-language results, any unverified microphone limitation, and confirmation that locked HTML remained unchanged.
