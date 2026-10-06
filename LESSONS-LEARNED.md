# Cold Direct — Lessons Learned Ledger

Operational mistakes and their fixes, across ALL work on this site (cron automation,
scripts, SEO content, infrastructure) — not just SEO page edits (those go in
`seo_fixes.md` / `seo_fixes_archive.md`). Read this before starting any new piece of
work on the site. Append a new dated entry whenever a real mistake is found and fixed,
whether by the agent or a cron job. Never delete entries — if something is superseded,
add a new entry noting it, don't remove the old one.

## 2026-09-23 — OG/Twitter tag script corrupted 28 real files (caught before commit)

**What happened:** An early version of a script that adds Open Graph/Twitter Card meta
tags computed the insertion offset relative to the extracted `<head>` substring, then
applied that offset directly against the full document string. Since `<head>` is not at
offset 0 of the real document, every insertion landed dozens of characters too early —
mid-attribute-value — corrupting the `og:description` tag and leaving trailing text
dangling outside any tag.

**How it was caught:** Tested in an isolated temp copy before running against real
files on a correctness check, not by looking at the diff by eye.

**Fix:** Always add `head_offset = head_match.start()` and apply it to any position
found via a regex/search run against the `head` substring before using that position to
slice the full `html` string. Verified afterward with `json.loads()`/HTML-parser
validation, not just "the script exited 0".

**Rule going forward:** Any script that searches within an extracted substring of a
larger document and then writes back into the full document must explicit carry and
apply the substring's offset. Test on an isolated copy BEFORE running on real site
files, every time — not just for this bug class, as a standing practice.

## 2026-09-27 — protected-pages.json fingerprint false-positive after legitimate title change

**What happened:** The SEO Draft/Publish pipeline legitimately changed a page's
`<title>` to the site's "Emergency Same Day" convention. `protected-pages.json`'s
`expected_title` field was never updated to match, so the next night's Protect Pages
Check reported a FAIL ("fingerprint mismatch") and refused to auto-restore, even though
the page content was correct and intentional.

**Recurred:** 2026-10-01, same pattern on a different page (`fridge-repair-london`)
after its own legitimate title change on 2026-09-28.

**Fix both times:** Verified the "failing" file was actually fine (byte size well over
minimum, `must_contain` string present, title matches a real recent commit) before
touching anything, then updated `expected_title` in `protected-pages.json` to match.

**Rule going forward:** Any job that changes a protected page's title/content MUST
update its `protected-pages.json` entry in the SAME commit. The SEO Publish skill
should check `protected-pages.json` for an entry matching any file it just edited and
update `expected_title`/`min_bytes` if those changed — this has now happened twice and
is a predictable recurring gap, not a one-off.

## 2026-09-29 to present — SEO Draft cron job truncates most nights (UNRESOLVED)

**What happened:** `ColdDirect Overnight SEO Draft` started failing with
`RuntimeError: Response remained truncated after 4 continuation attempts` on 2026-09-29
and has failed on most nights since (9/29, 9/30, 10/1, 10/2 all failed; a few nights in
between succeeded). Two theories were tested and BOTH DISPROVEN with real evidence:

1. **Theory: `seo_fixes.md` grew too large** (8KB → 36.7KB over a week), leaving no
   output budget to also write 800-1200 words of new content. Fixed by archiving old
   entries to `seo_fixes_archive.md`, dropping the file to 15.5KB, and adding a
   self-check to the skill. **Disproven**: the very next run, using the already-shrunk
   15.5KB file, truncated again with an identical error.
2. **Theory: `enabled_toolsets: null` on this job loaded every tool in the system into
   the schema on every call** (unlike the working jobs, which are scoped to
   `["terminal"]`), bloating the prompt. Restricted to `["terminal"]`. **Disproven**:
   the next scheduled run still truncated.

**Also ruled out by direct evidence:**
- Context window exhaustion — claude-sonnet-5 has a 1M token window; even all files the
  skill scans combined (~41KB) are negligible against that.
- Runtime correlation — successful runs took just as long (10-14 min) as failed ones,
  so it isn't simply "doing more work in one run."

**ROOT CAUSE CONFIRMED 2026-10-02** via direct log evidence (`agent.log`, grep for
`cron_a9da04730c00_*` + `API call #`). This is NOT a file-size, tool-count, or
context-window problem — those are all genuinely fine (sonnet-5 has a 1M token context
window and a 128K output cap; even a 26-call run only reaches ~112K input tokens).

The actual mechanism is Hermes's own documented `_continue_text()` thinking-only-
truncation path (`agent/turn_truncation.py` ~L241-260, comment: "Thinking-only
truncation: continuing with thinking ON re-burns the budget"): on some nights, when
the model goes to write its FINAL end-of-run text response after a long chain of tool
calls (18-26+ calls that complete fine), it generates reasoning/thinking tokens but
ZERO visible output text, hits the length limit, and even after Hermes auto-disables
reasoning on the retry, still fails to produce visible text within 4 continuation
attempts. Confirmed in `agent.log` for the 2026-09-29 failure: 24 tool-calling API
calls completed normally, then the job died ~45s after the last tool call — i.e. on
the final text-only summary response, not during any content-writing step. A
diagnostic subagent investigating this exact bug independently hit the identical
failure itself, and Hermes's own error copy named the mechanism precisely: "the model
hit its output-token limit ... its reasoning consumed the entire budget each time."

**CORRECTION 2026-10-05: the 2026-10-02 "confirmed root cause" above was WRONG.**
The mitigation applied that day (`reasoning_effort: none`, which was verified to
correctly send `thinking: {"type": "disabled"}` to the Anthropic API per
`agent/anthropic_adapter.py` — the config plumbing genuinely worked) did NOT fix the
bug. The job failed again on 2026-10-05 with the identical error, reasoning fully
disabled. So reasoning-token exhaustion was never the real cause either — it was a
plausible-sounding theory based on Hermes's own error copy, but the error message
("the model hit its output-token limit... its reasoning consumed the entire budget")
is a GENERIC message that same code path prints for the thinking-exhaustion case
specifically, and it was wrongly assumed to be diagnostic rather than just the
label for whichever sub-case triggered the generic 4-retry-then-fail logic in
`_continue_text()`. Lesson: a subagent (or anyone) hitting the "same" error itself
while investigating is suggestive, not proof of mechanism — Hermes's own cron jobs
and ad-hoc investigation sessions can all hit the same generic truncation path for
DIFFERENT underlying reasons.

**What is still true and re-confirmed on 2026-10-05:** the crash happens at the exact
same moment every single time — immediately after the model's last tool call,
specifically when it tries to compose its free-form final text summary. `agent.log`
on 2026-10-05 shows the last successful tool-calling API call completing normally,
then the job dying ~30-45s later with NO further logged API call in between —
consistent with 4 silent continuation-retry attempts (Hermes's own diagnostic
`_vprint` lines for those retries are not written to `agent.log` at INFO level, which
is why the retry content itself couldn't be inspected directly).

**Fix applied 2026-10-05 (structural, not another parameter tweak):** removed the
free-form final summary step entirely. The `colddirect-overnight-seo-draft` skill and
its cron prompt were both changed so the model writes its full report into the
structured `## DRAFT PENDING PUBLISH` block in `seo_fixes.md` (via a tool call — tool
calls have never failed in any logged run) and its actual final chat response is
required to be ONLY a fixed one-line sentence, not a composed summary. This removes
the specific step that was crashing every time, regardless of what the underlying
mechanism in Hermes turns out to be. Verify this actually works on the next scheduled
run (21:30) before declaring it fixed — given two prior "fixed" claims were wrong,
do not report this as resolved until a real successful run confirms it.

Do not re-propose file-size, toolset-count, or reasoning-effort theories again; all
three are conclusively disproven by direct evidence as of 2026-10-05.

**2026-10-06 21:30 scheduled run — fix from 2026-10-05 DISPROVEN.** The
`colddirect-overnight-seo-draft` job failed again with the identical
`RuntimeError: Response remained truncated after 4 continuation attempts` error,
despite the free-form-final-summary removal applied the day before. Per `agent.log`:
last successful tool-calling API call (#17) completed at 21:41:23, job died 42s later
at 21:42:05 with the same "4 continuation attempts" message and no further logged API
call in between — the exact same signature as every prior occurrence. Crucially, this
run never got far enough to reach a final-summary step at all (it crashed mid-research,
while diffing root-vs-folder index.html files on API call #16-17, well before any
`seo_fixes.md` DRAFT block was written). This proves the crash is NOT tied to the
free-form final-summary step specifically — that theory is now disproven alongside the
file-size/toolset-count/reasoning-effort theories. The crash appears to be a
continuation/truncation bug in the underlying Hermes conversation loop that can trigger
on ANY sufficiently long tool-calling turn in this job, not a property of which step is
last. No fix is proposed here — only recording that the 2026-10-05 fix did not hold,
per Ali's standing instruction to never declare a theory confirmed without a verified
successful run. Next step: needs fresh investigation into the continuation-retry
mechanism itself (the `_continue_text()` 4-retry-then-fail path), not another
structural workaround to the draft job's own prompt/skill.

## 2026-09-24 — Redirect-loop risk on `/services/` discovered, not yet fixed

**What happened:** While adding schema.org structured data, found that `/services/`
returns a live HTTP 301 redirect to the homepage on IIS/Plesk — meaning
`services.html` in the repo is never actually served to visitors or crawlers. Schema
was added to the file anyway (harmless if routing is ever fixed) but currently reaches
nobody.

**Why not fixed immediately:** `web.config` has no explicit rule for `/services/` at
all, so the redirect must come from either a generic catch-all rule or a Plesk-panel
level setting outside the repo. Given this site's history of IIS redirect loops (see
`iis-webconfig-redirect-debug` skill), changing `web.config` blind without a full
investigation risks creating a new loop. Flagged, not touched.

**Status: open, needs a dedicated investigation pass** using the
`iis-webconfig-redirect-debug` skill's verification method (curl -sI without following
redirects, check for a loop) before attempting any fix.
