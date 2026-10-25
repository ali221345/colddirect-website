# ColdDirect Voice AI — RULE 0 (permanent, never regress)

Owner 2026-10-25ai: Same ElevenLabs agent. If public token 404s, the widget mints a conversation token via `/colddirect-elevenlabs-token.aspx` + `App_Data/elevenlabs.key`. Script `?v=20261025ai`.

Owner 2026-10-25ah: Production voice is ElevenLabs Conversational AI agent `agent_2901m5th5arfe9amcec9ef2p42q` via `@elevenlabs/client` `Conversation.startSession({ agentId, connectionType: 'webrtc' })`. SPEAK opens the existing diagnostic modal and starts the live session immediately. Live user/agent transcript (RTL for Persian/Arabic; clickable `tel:` for `0203 952 4822` and `07983 759320`). Keep the green Like & 5-Star Review CTA. Do not bring back MediaRecorder, PHP vault, OpenAI TTS, or Vapi. Script `?v=20261025ah`.

Owner 2026-10-25ag: No OpenAI TTS. Persian audio is Azure/Edge `fa-IR-FaridNeural` only. LLM writes 2 technical sentences; wrapper adds one greeting + one close. No live SpeechRecognition in Auto (show Recording…). Diagnose = one Gemini call then neural TTS. Script `?v=20261025ag`.

Owner 2026-10-25af: Universal multilingual JSON `{target_language_code, display_text, spoken_text}` via `gpt-4o-mini` `json_object`. Every language MUST greet as Senior Engineer, answer in 2–3 sentences, then close with `0203 952 4822` / `07983 759320` and the green Like & 5-Star Review request. “Translate to X” wins. Persian TTS is FaridNeural / Edge / Piper only — never OpenAI onyx. Script `?v=20261025af`.

Owner 2026-10-25ae: Do NOT let the LLM invent Persian opening/phones/closing. LLM outputs 2 technical sentences only. Display wrap and vocalized TTS wrap are hardcoded (`دُرود بر شُما…کُلد دایرِکت…صِفر دِویست و سه…`). Persian audio = FaridNeural then onyx; never append English audio. Script `?v=20261025ae`.

Owner 2026-10-25ad: Live widget is custom record-stop-reply, not Vapi. Persian MUST open `درود، من سرپرست مهندسین در شرکت کولد دایرکت هستم و خوشحالم که ما را انتخاب کردید.` (audio pronounces `کُلد دایرِکت`) and close by asking for the green Like & 5-Star Review button. Phones in audio: mobile `صفر هفت نه هشت سه، هفت پنج نه، سه دو صفر` / office `صفر دو صفر سه، نه پنج دو، چهار هشت دو دو` / free `صفر هشتصد، یک یک دو، سه چهار دو هفت`. Script `?v=20261025aa`.

Owner 2026-10-25ac: Persian display vs TTS split (`?v=20261025z`). On-screen transcript keeps `کولد دایرکت` and `07983 759320` / `0203 952 4822` / `0800 112 3427`. TTS audio input uses `کُلد دایرِکت` and the spoken Persian number-word groups. `NormalizePersianForSpeech` must never reverse the phonetic brand and must never run `NumFa` on leftover phone digits.

Owner 2026-10-25ab: No Vapi WebRTC. Instant MediaRecorder: SPEAK starts in <100ms, second tap is STOP & SEND, mic tracks fully stopped before playback (`?v=20261025y`). Play via `__cdPlayCtx` AudioBufferSourceNode then HTML5 `<audio playsinline>`. Vault diagnose returns `audio_base64`. Pulse Like CTA when the answer finishes. Never auto-stop on silence.

1. Title `Ask Your Fault`. Badge `Lang: Auto`. SPEAK and LISTEN sit together in that compact box.
2. SPEAK opens a dropdown panel under the box with live transcript (RTL Persian / LTR English).
3. Highlight `👍 Like & Leave a 5-Star Review` → `/write-a-review/` when the assistant finishes (`speech-end`).
4. Assistant `e31c40c7-a45b-4dff-833c-320c54250743`. Public key in `App_Data/vapi-public.key` only.
