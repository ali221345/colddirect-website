# ColdDirect Voice AI — RULE 0 (permanent, never regress)

Owner 2026-10-25t: compact **Ask Your Fault** box sits in the top-left of the white header (`?v=20261025p`). Every spoken answer must end with the like/review closing. `vapi.start(id, assistantOverrides)` + system `add-message`. Highlight CTA on `speech-end`. Do not pass `model.messages` (that replaces the saved prompt).

1. Title `Ask Your Fault`. Badge `Lang: Auto`. SPEAK and LISTEN sit together in that compact box.
2. SPEAK opens a dropdown panel under the box with live transcript (RTL Persian / LTR English).
3. Highlight `👍 Like & Leave a 5-Star Review` → `/write-a-review/` when the assistant finishes (`speech-end`).
4. Assistant `e31c40c7-a45b-4dff-833c-320c54250743`. Public key in `App_Data/vapi-public.key` only.
