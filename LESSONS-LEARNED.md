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

This is a generic, named Hermes failure pattern — not specific to this skill or this
project. It appears to be stochastic (the model occasionally gets "stuck" generating
only internal reasoning for a final text response, unrelated to task content). The
`colddirect-overnight-seo-draft` skill was updated with this finding and a note to
keep the end-of-run report short, but that is a mitigation, not a guaranteed fix —
if it keeps recurring, this is arguably a Hermes-core issue (the auto-disable-
reasoning retry not working reliably) rather than something fixable at the skill/cron
level. Do not re-propose the file-size or toolset-count theories again; they are
conclusively ruled out by this evidence.

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
