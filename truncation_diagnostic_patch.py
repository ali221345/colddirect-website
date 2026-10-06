"""
Diagnostic monkey-patch for the SEO Draft truncation bug. Wraps
agent.turn_truncation._continue_text to log the ACTUAL finish_reason, content
presence, and response id on every truncation attempt to a plain file
(bypassing the gated _vprint/diagnostic system entirely), so we can see what
Hermes's own internals saw at the exact failure moment instead of inferring
from agent.log gaps.

Usage: imported by a tiny bootstrap script that then runs the cron job's own
agent turn directly (not through the scheduler), so this patch is active for
the run.
"""
import functools
from datetime import datetime
from pathlib import Path

LOG_PATH = Path(r"C:\Users\khora\Documents\colddirect-website\truncation_debug.log")


def log(msg: str) -> None:
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} {msg}\n")


def install_patch():
    from agent import turn_truncation

    original = turn_truncation._continue_text

    @functools.wraps(original)
    def patched(st, _retry, assistant_message):
        content = getattr(assistant_message, "content", None)
        reasoning = getattr(assistant_message, "reasoning", None)
        tool_calls = getattr(assistant_message, "tool_calls", None)
        response_id = getattr(st.response, "id", None)
        content_preview = content[:200] if content else None
        log(
            f"_continue_text called: attempt={st.length_continue_retries + 1} "
            f"finish_reason={st.finish_reason!r} "
            f"content_len={len(content) if content else 0} "
            f"content_repr={content_preview!r} "
            f"reasoning_len={len(reasoning) if reasoning else 0} "
            f"has_tool_calls={bool(tool_calls)} "
            f"response_id={response_id} "
            f"is_stub={st.is_stub} "
            f"window_filled={st.window_filled}"
        )
        result = original(st, _retry, assistant_message)
        log(f"_continue_text returned: action={result.action}")
        return result

    turn_truncation._continue_text = patched
    log("=== Patch installed ===")


if __name__ == "__main__":
    install_patch()
    print("Patch installed, log at", LOG_PATH)
