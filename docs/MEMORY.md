# ColdDirect Voice AI — RULE 0 (permanent, never regress)

Owner 2026-10-25o replaced the custom top bar with the Vapi **Ask Your Fault** widget (`?v=20261025g`). Do not restore the old SPEAK/LISTEN top bar.

1. Widget title is exactly `Ask Your Fault`. Language badge is exactly `Lang: Auto` (never `/ خودکار`).
2. Browser SDK: `@vapi-ai/web` + assistant `e31c40c7-a45b-4dff-833c-320c54250743`.
3. Public API key is NOT in git. Serve it from `App_Data/vapi-public.key` via `/colddirect-vapi-config.aspx` (or `window.CD_VAPI_PUBLIC_KEY`). Never commit or print the key. Never put a private/server Vapi key in browser JS.
4. Do not apply the widget's `body { background }` styles to the whole site. Scope CSS to `.vapi-widget`.
5. Do not add `html.cd-voice-on` top padding. The launcher is bottom-right.
6. Vapi assistant prompt (in the Vapi dashboard, not this repo) still owns language matching, `کولد دایرکت`, the Head Engineer greeting, and the like CTA. No slang. Male voices only.
