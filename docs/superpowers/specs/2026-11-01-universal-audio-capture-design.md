# Universal Audio Capture and Single-Call Diagnosis

## Scope

Replace browser speech recognition with direct microphone audio submission for every spoken-language interaction. Preserve typed diagnosis, server TTS, playback, existing visual behavior, and all locked HTML and SEO files.

## Frontend

- `SPEAK` always starts `MediaRecorder`; `SpeechRecognition` and `webkitSpeechRecognition` are removed from the capture path and supporting code.
- Record the browser-supported `audio/webm` or `audio/mp4` format, retaining the existing silence detection, manual stop, maximum duration, final-chunk flush, and microphone cleanup.
- Send the recording as base64 with its detected MIME type to `/api/voice-diagnose` using `language: "auto"` and audio mode.
- Render the returned transcript and reply, and use the returned BCP-47 language for speech. Never infer the spoken language from browser locale.

## Backend

- For each audio request, make exactly one Gemini multimodal `generateContent` request with the audio inline. Do not try alternate models after an audio-request failure.
- Ask the model to auto-detect any spoken language without a predefined language list and return JSON containing the exact transcript, a valid BCP-47 code, and a native display/spoken reply.
- Require the natural Head Engineer greeting, fault-specific commercial-refrigeration guidance, `0203 952 4822`, `07983 759320`, `info@colddirect.co.uk`, and a native five-star review request.
- Accept syntactically valid BCP-47 codes beyond the existing template languages. Do not replace Greek, Chinese, Tagalog/Filipino, Italian, or other model-detected languages with English merely because no local template exists.
- Retain deterministic templates only where already defined; for other languages, preserve the model's complete native greeting and CTA after validating required contact details and output consistency.
- Expose `language` for compatibility and `languageCode` as the explicit BCP-47 field, alongside `transcript`, `reply`, `display_text`, and `spoken_text`.
- On upstream, parsing, or validation failure, return an honest transcription-unavailable response without claiming that audio was understood.

## Verification

Add one consolidated mocked regression test covering a language outside the existing templates, exactly one inline-audio model call, the BCP-47 response contract, mandatory contact details, and complete removal of browser speech recognition. Run the normal test suite and locked-state check once, inspect the diff, then commit, push, and verify deployment. Do not run live multi-language API loops.
