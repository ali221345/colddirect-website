"""Upload deny-list for Cold Direct deploy scripts (Plesk /httpdocs).

Never upload AI/editor folders, VCS/env folders, secrets or local junk.
Usage: `if should_skip_upload(remote_rel_path): return` before any STOR.
"""
from __future__ import annotations

from pathlib import PurePath

# Folders/files that must never be uploaded to the server
BLOCKED_PATHS = frozenset({
    # AI tools and editors
    ".cursor", ".pi", ".claude", ".codex", ".opencode", ".zed", ".vscode", ".idea",
    # git, virtualenvs, system
    ".git", ".github", "node_modules", "__pycache__", ".venv", "venv",
    # sensitive / local config
    ".env", ".env.local", ".gitignore", ".cursorrules", ".DS_Store", "Thumbs.db",
    # server-side secrets (auto-seo.key lives only on Plesk, uploaded by a dedicated one-off step)
    "App_Data", "app_data",
})

# Forbidden extensions (compiled python, logs, backups, key files)
BLOCKED_EXTENSIONS = frozenset({".pyc", ".pyo", ".log", ".bak", ".key"})


def should_skip_upload(relative_path: str) -> bool:
    """True if the path (file or folder, relative to site root) must be skipped."""
    parts = PurePath(str(relative_path).replace("\\", "/")).parts
    if not parts:
        return False
    if any(part in BLOCKED_PATHS for part in parts):
        return True
    return parts[-1].lower().endswith(tuple(BLOCKED_EXTENSIONS))


if __name__ == "__main__":
    cases = {
        "index.html": False, "js/cd-hover-card.js": False, ".htaccess": False,
        "fridge-repair-london/index.html": False,
        ".vscode/sftp.json": True, ".cursor/rules/x.mdc": True, ".git/config": True,
        "node_modules/a/b.js": True, "tools/__pycache__/x.pyc": True, "deploy.log": True,
        "App_Data/auto-seo.key": True, "app_data/x.txt": True, "secret.KEY": True, "auto-seo.key": True,
        "page.html.bak": True, ".env": True, "sub\\.github\\deploy.yml": True, "": False,
    }
    bad = [p for p, want in cases.items() if should_skip_upload(p) != want]
    print("deploy_guard self-test:", "OK" if not bad else "FAIL %s" % bad)
    raise SystemExit(1 if bad else 0)
