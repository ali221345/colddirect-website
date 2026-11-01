# Universal Audio Capture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `MediaRecorder` the only speech listener and return an exact transcript, unrestricted BCP-47 language code, and native diagnosis from one inline-audio Gemini call.

**Architecture:** The existing widget keeps its recorder, silence detection, UI, and playback but loses the browser-recognition branch. The existing diagnosis handler keeps typed-input behavior while audio requests use one configured multimodal model and preserve model-detected languages beyond the local CTA templates.

**Tech Stack:** Browser JavaScript (`MediaRecorder`, `FileReader`), Node.js/Vercel serverless functions, Gemini `generateContent`, Node `assert`.

## Global Constraints

- Exactly one Gemini call per audio request; no audio model failover.
- No `SpeechRecognition` or `webkitSpeechRecognition` anywhere in the widget.
- No browser-locale language detection and no fixed output-language shortlist.
- Return `transcript`, `languageCode`, `language`, `reply`, `display_text`, and `spoken_text`.
- Preserve mandatory contact details and native greeting/review requirements.
- No locked HTML or sitemap edits; no live multi-language API loops.

---

### Task 1: Universal mocked audio contract

**Files:**

- Modify: `tools/test_voice_frontend.js`
- Modify: `tools/test_voice_diagnose.js`
- Test: `tools/test_voice_frontend.js`, `tools/test_voice_diagnose.js`

**Interfaces:**

- Consumes: existing `post(payload)` helper and mocked `core.geminiJson`.
- Produces: one mocked Tagalog/Filipino audio case asserting one model call and `fil-PH` output.

- [ ] **Step 1: Replace recognition-first frontend assertions**

Assert that the source contains neither recognition API, starts the recorder directly with `startRecorder(my)`, submits `audio_base64`, and retains the final-chunk flush:

```js
assert.ok(!source.includes("SpeechRecognition"));
assert.ok(!source.includes("webkitSpeechRecognition"));
assert.ok(/function startLive\(\)[\s\S]*?startRecorder\(my\);/.test(source));
assert.ok(source.includes("audio_base64: b64"));
assert.ok(source.includes("rec.requestData();"));
```

- [ ] **Step 2: Add the single mocked universal-audio case**

Mock a complete native Tagalog response, call the existing `post(mp4)` helper once, and assert:

```js
assert.strictEqual(calls, 1);
assert.strictEqual(result.json.languageCode, "fil-PH");
assert.strictEqual(result.json.language, "fil-PH");
assert.ok(result.json.transcript.includes("Hindi lumalamig"));
assert.ok(result.json.reply.includes("07983 759320"));
assert.ok(result.json.reply.includes("info@colddirect.co.uk"));
assert.strictEqual(
  requestBody.contents[0].parts[1].inlineData.mimeType,
  "audio/mp4",
);
```

Update the former audio-failover and quota expectations to one call; retain typed-text failover coverage separately.

- [ ] **Step 3: Run the focused tests once to establish the red baseline**

Run: `node tools/test_voice_frontend.js && node tools/test_voice_diagnose.js`
Expected: FAIL because recognition remains, `languageCode` is absent, and audio currently fails over.

### Task 2: MediaRecorder-only capture and one-call diagnosis

**Files:**

- Modify: `assets/js/colddirect-voice-bar.js`
- Modify: `colddirect-public-html/assets/js/colddirect-voice-bar.js`
- Modify: `api/voice-diagnose.js`

**Interfaces:**

- Consumes: `startRecorder(my)`, `sendFault()`, `core.geminiJson`, and existing response parser.
- Produces: `{ transcript, languageCode, language, reply, display_text, spoken_text }` for successful audio diagnosis.

- [ ] **Step 1: Remove browser recognition**

Delete recognition state, timers, stop/send helpers, and `startNativeRecognition`. Make startup and manual stop use only:

```js
function startLive() {
  // existing UI setup remains
  startRecorder(my);
}
// Manual stop: sendFault();
```

- [ ] **Step 2: Restrict only audio to one configured model**

After model-list de-duplication, use:

```js
if (audio) models = models.slice(0, 1);
```

The existing 30-second first-call timeout and inline `inlineData` part remain unchanged.

- [ ] **Step 3: Preserve arbitrary model-detected BCP-47 codes**

For audio, derive the expected/locked language from the validated model code rather than text heuristics. At the response boundary, canonicalize the result's existing language instead of re-detecting it from mixed transcript/reply text. Add the alias:

```js
languageCode: locked.bcp,
language: locked.bcp,
```

Existing templates still enrich known languages; unknown languages retain the model's complete native greeting and CTA, subject to contact validation.

- [ ] **Step 4: Mirror the widget byte-for-byte**

Run: `Copy-Item assets/js/colddirect-voice-bar.js colddirect-public-html/assets/js/colddirect-voice-bar.js` (or the equivalent Git Bash `cp` command).

### Task 3: Single verification and deployment pass

**Files:**

- Verify only; no locked HTML changes.

**Interfaces:**

- Consumes: Tasks 1–2.
- Produces: tested commit on `main` and a verified deployment.

- [ ] **Step 1: Run the normal checks once**

Run: `npm test`
Expected: all voice, asset, and LD+JSON checks pass.

Run: `python tools/check_locked_state.py`
Expected: `check_locked_state: ALL LOCKS INTACT`.

Run: `npx prettier --check` on changed JS/JSON/Markdown files.
Expected: all matched files use Prettier formatting.

- [ ] **Step 2: Inspect and commit**

Run: `git diff --check && git status --short`
Expected: no whitespace errors and no HTML/sitemap modifications.

Commit the implementation and plan with message: `fix: use universal single-call audio diagnosis`.

- [ ] **Step 3: Push and verify**

Push `main`, then verify the relevant GitHub/Plesk and Vercel deployments. Do not run live multi-language test loops.
