# ColdDirect Voice AI — RULE 0 (permanent, never regress)

Owner 2026-10-25z: Call `vapi.start(ASSISTANT_ID)` with no `assistantOverrides` (`?v=20261025w`). Never auto `vapi.stop()` on speech-end/timer — only END / ✕. Ignore non-fatal daily-js warnings; log real Vapi errors to console. Mobile Welcome LEFT, Ask Your Fault RIGHT. Never overlay phones, email, logo, or Menu. Do not pass `model.messages` or partial `model` in start overrides.

1. Title `Ask Your Fault`. Badge `Lang: Auto`. SPEAK and LISTEN sit together in that compact box.
2. SPEAK opens a dropdown panel under the box with live transcript (RTL Persian / LTR English).
3. Highlight `👍 Like & Leave a 5-Star Review` → `/write-a-review/` when the assistant finishes (`speech-end`).
4. Assistant `e31c40c7-a45b-4dff-833c-320c54250743`. Public key in `App_Data/vapi-public.key` only.
