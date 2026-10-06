"""
Runs the colddirect-overnight-seo-draft skill prompt through a real AIAgent turn,
with the truncation diagnostic patch installed, so we can see exactly what
Hermes's turn loop observes on each truncation retry attempt.

This bypasses the cron scheduler (which has its own harness) but exercises the
SAME underlying agent/turn_truncation.py code path that the cron job does.
"""
import sys
sys.path.insert(0, r"C:\Users\khora\AppData\Local\hermes\hermes-agent")

from truncation_diagnostic_patch import install_patch, log

install_patch()

from run_agent import AIAgent

SKILL_PROMPT = open(
    r"C:\Users\khora\AppData\Local\hermes\skills\colddirect-overnight-seo-draft\SKILL.md",
    encoding="utf-8",
).read()

USER_PROMPT = (
    f'[IMPORTANT: The user has invoked the "colddirect-overnight-seo-draft" skill, '
    f"indicating they want you to follow its instructions. The full skill content is "
    f"loaded below.]\n\n---\n{SKILL_PROMPT}\n---\n\n"
    "Run the Cold Direct overnight SEO draft pass at "
    r"C:\Users\khora\Documents\colddirect-website"
    ", following the colddirect-overnight-seo-draft skill exactly. Ground every keyword "
    "decision in today's real gsc_report.csv. Apply the full on-page checklist to EXACTLY "
    "1 page this run. Append a '## DRAFT PENDING PUBLISH' block to seo_fixes.md for that "
    "page. Do NOT commit, push, rebuild the sitemap, run internal_linking.js, or call the "
    "GSC API. CRITICAL: your final chat response must be ONLY the fixed sentence "
    '"Draft complete — see seo_fixes.md for the DRAFT PENDING PUBLISH entry."'
)

log(f"Starting diagnostic run, prompt length={len(USER_PROMPT)}")

agent = AIAgent(
    model="anthropic/claude-sonnet-5",
    provider="nous",
    platform="cli",
    enabled_toolsets=["terminal"],
    reasoning_config={"enabled": False},
    skip_memory=True,
    skip_context_files=True,
    cwd=r"C:\Users\khora\Documents\colddirect-website",
)

try:
    result = agent.run_conversation(USER_PROMPT)
    log(f"run_conversation returned: completed={result.get('completed')} "
        f"failed={result.get('failed')} error={result.get('error')!r} "
        f"final_response_len={len(result.get('final_response') or '')}")
    print("DONE")
    print("completed:", result.get("completed"))
    print("failed:", result.get("failed"))
    print("error:", result.get("error"))
    print("final_response:", (result.get("final_response") or "")[:500])
except Exception as e:
    log(f"EXCEPTION: {type(e).__name__}: {e}")
    print("EXCEPTION:", type(e).__name__, e)
finally:
    try:
        agent.close()
    except Exception:
        pass
