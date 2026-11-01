# Universal multilingual voice diagnosis and TTS design

Date: 2026-11-01

## Scope

Fix three verified production issues without modifying locked HTML pages:

1. Turkish is answered in English and Arabic is misclassified as Persian.
2. Responses omit `info@colddirect.co.uk`.
3. TTS intermittently returns `TIMEOUT`, `NO_AUDIO`, or `TTS_UNAVAILABLE`.

The implementation is limited to the voice core, diagnosis and TTS serverless handlers, widget JavaScript, and their tests.

## Selected approach

Use model-led universal language routing rather than a fixed language-only allowlist or a new translation dependency.

### Language routing

- Detect and preserve a validated BCP-47 language code through diagnosis, response rendering, widget fallback speech, and TTS.
- Detect Arabic and Persian independently. Persian-specific letters and words indicate Persian; Arabic script without such evidence must not default to Persian.
- Recognize common Latin-script languages, including Turkish, Spanish, and French, while allowing the model's validated language code for other languages.
- Reject model output whose detected language conflicts with high-confidence input detection instead of silently translating it into English or Persian.
- Keep browser locale out of input-language detection; the customer's text or transcript determines the response language.

### Native response structure

- Require the model to produce the Head Engineer greeting, technical diagnosis, contact information, and five-star review request in the input language.
- Retain concise native fallback templates for English, Persian, Turkish, Arabic, Spanish, and French. Other languages remain model-led rather than falling back to English merely because no template exists.
- Include `07983 759320` and `info@colddirect.co.uk` in every written and spoken response. Keep the existing landline where already present.
- Preserve the existing technical and safety behavior and the green review-button request.

### TTS reliability

- Pass the dynamic BCP-47 language code to speech synthesis and select language-appropriate fallback voices where supported.
- Keep greeting, diagnosis, contact details, and review request in the spoken text while limiting unnecessary verbosity.
- Use a bounded overall time budget compatible with the Vercel function limit.
- Retry retryable upstream failures, including `NO_AUDIO`, timeouts, rate limits, and server errors; do not stop immediately on `NO_AUDIO`.
- Preserve provider fallback and native browser speech when no audio provider succeeds.

## Data flow

1. Widget sends typed text or recorded audio to `/api/voice-diagnose` with the production origin.
2. Diagnosis detects the input language independently of the UI and returns `language`, `transcript`, `display_text`, and `spoken_text` in that language.
3. Widget displays `display_text` and sends `spoken_text` plus `language` to `/api/voice-tts`.
4. TTS synthesizes the supplied native-language text or reports a diagnostic failure; the widget then uses native speech with the same language code.

## Error handling

- Preserve CORS behavior and HTTP contracts.
- Return structured upstream diagnostics rather than treating HTTP 200 alone as proof of audio success.
- Do not invent a translation when a model response is unusable. Use a native fallback when available; otherwise retain the existing safe failure path.
- Do not modify SEO pipelines, locked HTML, sitemap files, or unrelated dependencies.

## Verification

- Add failing regression tests before implementation for Arabic/Persian separation, Turkish/Spanish/French preservation, mandatory email, dynamic TTS language codes, and `NO_AUDIO` retry behavior.
- Run the complete `npm test` suite and `python tools/check_locked_state.py`.
- Repeat live English, Persian, Turkish, and Arabic diagnosis and TTS tests, including CORS and speech round-trips where available.
- Recheck the live widget, console, network, and native playback.
- Commit and push only after local checks pass, then verify the Plesk workflow and live Vercel deployment.
