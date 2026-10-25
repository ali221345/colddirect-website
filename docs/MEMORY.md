# ColdDirect Voice AI — RULE 0 (permanent, never regress)

Owner 2026-10-25p restored the dark SPEAK/LISTEN bar above the homepage slider and service-page hero image (`?v=20261025i`). Do not put back the bottom-right floating Vapi launcher.

1. Title exactly `Ask Your Fault`. Badge exactly `Lang: Auto` (never `/ خودکار`, no Persian on the button).
2. SPEAK starts/ends the Vapi call. LISTEN starts the same assistant so the user can hear it. Assistant `e31c40c7-a45b-4dff-833c-320c54250743`.
3. Public API key is NOT in git. Serve it from `App_Data/vapi-public.key` via `/colddirect-vapi-config.aspx`. Never commit or print the key.
4. Place the bar in-flow immediately before `#home-slider` or the first hero image. Do not use a floating corner widget.
5. Vapi dashboard owns language matching, `کولد دایرکت`, greeting, like CTA, no slang, male voices.
