"""Pre-upload HTML sanity check for Cold Direct (SEO-critical tags + merge-conflict markers).

Library: validate_html_file(path) -> list[str] of issues (empty = OK).
CLI:     python tools/html_preflight.py [paths...]   (default: every root *.html and */index.html)
"""
from __future__ import annotations

import os
import re
import sys

# Critical SEO tags and healthy HTML structure
REQUIRED_PATTERNS = {
    "DOCTYPE": re.compile(r"<!DOCTYPE\s+html>", re.IGNORECASE),
    "Title tag": re.compile(r"<title>\s*\S+.*?</title>", re.IGNORECASE | re.DOTALL),
    "Meta description": re.compile(
        r"<meta\s+[^>]*name=[\"\']description[\"\'][^>]*content=[\"\']\s*\S+[^>]*>",
        re.IGNORECASE,
    ),
    "Canonical link": re.compile(
        r"<link\s+[^>]*rel=[\"\']canonical[\"\'][^>]*href=[\"\']https://(www\.)?colddirect\.co\.uk[^\"\']*[\"\']",
        re.IGNORECASE,
    ),
    "Closing HTML tag": re.compile(r"</html>", re.IGNORECASE),
}

# Possible git/agent damage that must never reach the live site.
# NOTE: only the real conflict markers are enforced below; '=======' and 'undefined'
# legitimately appear in JS/CSS/text, so they are informational only.
FORBIDDEN_MARKERS = (
    "<<<<<<< HEAD",
    "=======",
    ">>>>>>>",
    "TODO: SEO",
    "undefined",
)


def validate_html_file(filepath: str) -> list[str]:
    """Check one HTML file before upload and return the list of issues."""
    issues: list[str] = []
    if not os.path.exists(filepath):
        return [f"Missing file: {filepath}"]

    # Search-engine verification files (googleXXXX.html) are tiny by design
    if re.match(r"google[0-9a-f]+\.html$", os.path.basename(filepath), re.IGNORECASE):
        return []

    if os.path.getsize(filepath) < 200:
        return [f"File suspiciously small or empty (<200 bytes): {filepath}"]

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:  # noqa: BLE001
        return [f"Cannot read {filepath}: {e}"]

    # 1. Required SEO tags (only full pages that have a <head>)
    if re.search(r"<head[\s>]", content, re.IGNORECASE):
        noindex = re.search(r"<meta\s+[^>]*name=[\"\']robots[\"\'][^>]*noindex", content, re.IGNORECASE)
        for name, pattern in REQUIRED_PATTERNS.items():
            if name == "Meta description" and noindex:
                continue  # noindex pages do not need a description
            if not pattern.search(content):
                issues.append(f"{filepath}: Missing or empty {name}")

    # 2. Unresolved git conflicts
    for marker in ("<<<<<<< HEAD", ">>>>>>>"):
        if marker in content:
            issues.append(f"{filepath}: Contains unresolved Git merge conflict marker ({marker})")

    return issues


def preflight_ok(local_path, remote_path: str = "") -> bool:
    """Used by deploy scripts: True if the file may be uploaded (non-HTML always passes).

    Set env CD_SKIP_PREFLIGHT=1 to override deliberately.
    """
    name = str(remote_path or local_path)
    if not name.lower().endswith(".html") or os.environ.get("CD_SKIP_PREFLIGHT") == "1":
        return True
    issues = validate_html_file(str(local_path))
    for i in issues:
        print("PREFLIGHT BLOCKED:", i)
    return not issues


def _default_targets(root: str) -> list[str]:
    out = []
    skip = {".git", ".github", ".cursor", ".vscode", "node_modules", "colddirect-public-html", "docs", "agent", "tools", "scripts"}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in skip]
        out += [os.path.join(dp, f) for f in fn if f.endswith(".html")]
    return out


if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    targets = sys.argv[1:] or _default_targets(root)
    problems = [i for t in targets for i in validate_html_file(t)]
    for p in problems:
        print("ISSUE:", p)
    print(f"html_preflight: {len(targets)} files checked, {len(problems)} issue(s)")
    raise SystemExit(1 if problems else 0)
