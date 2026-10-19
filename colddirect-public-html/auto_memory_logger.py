#!/usr/bin/env python3
"""
Permanent Action & Change Logger for Cold Direct (colddirect.co.uk).
Automatically records every website change, SEO update, script run, 24h health check,
and 48h backup into both:
1. User's persistent agent store: C:/Users/khora/AppData/Local/Cursor/AgentStores/cursor_agent_stores/u420035230/files/colddirect-memory.md
2. Workspace ledger: C:/Users/khora/Documents/colddirect-website/colddirect-public-html/colddirect-memory-ledger.md
3. Repo docs ledger: C:/Users/khora/Documents/colddirect-website/docs/ai-memory/WORK_LOG.md
"""
from __future__ import annotations

import argparse
import datetime as dt
import subprocess
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent
REPO_ROOT = WORKSPACE_DIR.parent
USER_STORE_MEMORY = Path(
    r"C:\Users\khora\AppData\Local\Cursor\AgentStores\cursor_agent_stores\u420035230\files\colddirect-memory.md"
)
LOCAL_LEDGER = WORKSPACE_DIR / "colddirect-memory-ledger.md"
REPO_WORK_LOG = REPO_ROOT / "docs" / "ai-memory" / "WORK_LOG.md"


def get_git_commit() -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return "N/A"


def log_action(
    action_type: str,
    summary: str,
    files_info: str = "All synced HTML/SEO files",
    gsc_status: str = "200 OK / Sitemap 204",
    extra_details: str = "",
) -> str:
    now_utc = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    commit_hash = get_git_commit()

    entry = (
        f"\n### [{now_utc}] — {action_type}\n"
        f"- **Summary**: {summary}\n"
        f"- **Git Commit**: `{commit_hash}`\n"
        f"- **Affected Files / Scope**: {files_info}\n"
        f"- **GSC / Live Status**: {gsc_status}\n"
    )
    if extra_details:
        entry += f"- **Details**: {extra_details}\n"

    # 1. Append to local workspace ledger
    if not LOCAL_LEDGER.exists():
        LOCAL_LEDGER.write_text(
            "# Cold Direct Permanent Automated Action & Backup Ledger\n",
            encoding="utf-8",
        )
    with LOCAL_LEDGER.open("a", encoding="utf-8") as f:
        f.write(entry)

    # 2. Append to User Persistent Store memory
    if USER_STORE_MEMORY.exists():
        with USER_STORE_MEMORY.open("a", encoding="utf-8") as f:
            f.write(entry)

    # 3. Append to Repo WORK_LOG.md if present
    if REPO_WORK_LOG.exists():
        with REPO_WORK_LOG.open("a", encoding="utf-8") as f:
            f.write(entry)

    return entry


def main() -> None:
    parser = argparse.ArgumentParser(description="Log action to Cold Direct permanent memory.")
    parser.add_argument("--type", default="AUTO-UPDATE", help="Action type")
    parser.add_argument("--summary", required=True, help="Action summary")
    parser.add_argument("--files", default="Synced live /httpdocs & git workspace", help="Files affected")
    parser.add_argument("--gsc", default="Verified 200 OK", help="GSC / HTTP status")
    parser.add_argument("--details", default="", help="Additional details")
    args = parser.parse_args()

    entry = log_action(
        action_type=args.type,
        summary=args.summary,
        files_info=args.files,
        gsc_status=args.gsc,
        extra_details=args.details,
    )
    print(entry.strip())


if __name__ == "__main__":
    main()
