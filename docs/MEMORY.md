# ColdDirect Voice AI — RULE 0 (permanent, never regress)

After `🎤 SPEAK` the widget MUST speak the answer aloud. Text-only after a microphone recording is a P0 bug.

1. NEVER remove the polite universal greeting:
   - EN: `Hello. I am the Head Engineer at ColdDirect. I'm glad you chose our company.`
   - FA: `درود، من سرپرست مهندسین در شرکت کولد دایرکت هستم و خوشحالم که ما را انتخاب کردید.`
   Never prepend the English greeting to a non-English answer. Selector label is `Auto`, not `Auto / خودکار`.
   Brand in Persian is `کولد دایرکت` (never `کل دایرکت`).
2. NEVER use street slang (`Alright mate`, `cheers`, `don't panic`).
3. NEVER use female voices or Urdu/Arabic fallback for Persian (`fa`). Male only: `fa_IR-ganji-medium` + `NormalizePersianForSpeech` (`ColdDirect` → `کولد دایرکت`), `en_GB-alan-medium`, Piper / Google-stream male for Tagalog and other languages.
4. NEVER break auto-play after microphone recording:
   - Stop every `MediaStreamTrack` and close the analyser `AudioContext` before playback.
   - Keep `window.__cdPlayCtx` (resumed on the SPEAK tap) and `window.__cdVoicePlayer` alive.
   - Diagnose JSON includes `audio_base64`.
   - Play first via `AudioBufferSourceNode` on `__cdPlayCtx` so silence-timer auto-stop never hits `NotAllowedError`.
   - Keep 3800ms silence after speech starts (do not restore 700ms cutoff).
