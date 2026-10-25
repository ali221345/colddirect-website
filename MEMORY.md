# ColdDirect Voice AI — RULE 0 (permanent, never regress)

See `docs/MEMORY.md` for the full lock.

After `🎤 SPEAK` the widget MUST speak the answer aloud. Keep the Head Engineer greeting. No slang. Male voices only (Ganji fa, Alan en; never Urdu/Arabic for Persian). Stop mic tracks + close the analyser context before play. Unlock `__cdPlayCtx` + `__cdVoicePlayer` on the SPEAK tap. Diagnose JSON includes `audio_base64`. Play via `AudioBufferSourceNode` first. Keep 3800ms silence.
