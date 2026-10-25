# ColdDirect Voice AI — RULE 0 (permanent, never regress)

Owner 2026-10-25ac: Persian display vs TTS split (`?v=20261025z`). On-screen transcript keeps `کولد دایرکت` and `07983 759320` / `0203 952 4822` / `0800 112 3427`. TTS audio input uses `کُلد دایرِکت` and the spoken Persian number-word groups. `NormalizePersianForSpeech` must never reverse the phonetic brand and must never run `NumFa` on leftover phone digits.

Owner 2026-10-25ab: No Vapi WebRTC. Instant MediaRecorder: SPEAK starts in <100ms, second tap is STOP & SEND, mic tracks fully stopped before playback (`?v=20261025y`). Play via `__cdPlayCtx` AudioBufferSourceNode then HTML5 `<audio playsinline>`. Vault diagnose returns `audio_base64`. Pulse Like CTA when the answer finishes. Never auto-stop on silence.

1. Title `Ask Your Fault`. Badge `Lang: Auto`. SPEAK and LISTEN sit together in that compact box.
2. SPEAK opens a dropdown panel under the box with live transcript (RTL Persian / LTR English).
3. Highlight `👍 Like & Leave a 5-Star Review` → `/write-a-review/` when the assistant finishes (`speech-end`).
4. Assistant `e31c40c7-a45b-4dff-833c-320c54250743`. Public key in `App_Data/vapi-public.key` only.
