"""Pre-upload HTML sanity check for Cold Direct (SEO-critical tags + merge-conflict markers).

Library: validate_html_file(path) -> list[str] of issues (empty = OK).
CLI:     python tools/html_preflight.py [paths...] [--strict] [--write-baseline]
         (default: every root *.html; known legacy issues in html_preflight_baseline.txt do not fail)
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


import json  # noqa: E402

# All JSON-LD blocks on a page
JSON_LD_PATTERN = re.compile(
    r"<script\s+[^>]*type=[\"\']application/ld\+json[\"\'][^>]*>(.*?)</script>",
    re.IGNORECASE | re.DOTALL,
)

# Allowed schema types for core service pages
VALID_BUSINESS_TYPES = {
    "LocalBusiness",
    "HVACBusiness",
    "HomeAndConstructionBusiness",
    "ProfessionalService",
    "Service",
}

# Money pages (+ homepage) that must carry the official phone and a business schema
CORE_SLUGS = {
    "fridge-repair-london", "freezer-repair-london", "commercial-fridge-repair-london",
    "commercial-freezer-repair-london", "cold-room-repair-london", "catering-repair-london",
    "commercial-appliances-repair-london", "air-conditioning-repair-london",
    "cellar-cooler-repair-london",
}
_ROOT_DIRS = {"colddirect-website", "colddirect-public-html", "httpdocs"}


def is_core_page(path: str) -> bool:
    """True for the 9 money pages (<slug>.html or <slug>/index.html) and the homepage."""
    parts = [p for p in str(path).replace("\\", "/").split("/") if p and p != "."]
    if not parts:
        return False
    name = parts[-1]
    if name == "index.html":
        parent = parts[-2] if len(parts) > 1 else ""
        return parent in CORE_SLUGS or parent == "" or parent in _ROOT_DIRS
    return name.endswith(".html") and name[:-5] in CORE_SLUGS


def validate_core_page_schema_and_contact(filepath: str, content: str) -> list[str]:
    """Check JSON-LD schema and phone number on core revenue (money) pages."""
    issues: list[str] = []

    # 1. Official phone present (spaces/dashes and +44 prefix tolerated)
    normalized_digits = re.sub(r"[\s\-]", "", content)
    if "07983759320" not in normalized_digits and "447983759320" not in normalized_digits:
        issues.append(f"{filepath}: Missing official contact phone number (07983 759320)")

    # 2. Extract JSON-LD and verify syntax
    matches = JSON_LD_PATTERN.findall(content)
    if not matches:
        issues.append(f"{filepath}: Missing <script type='application/ld+json'> schema block")
        return issues

    has_valid_business_schema = False
    for idx, raw_json in enumerate(matches, 1):
        try:
            data = json.loads(raw_json.strip())
        except json.JSONDecodeError as e:
            issues.append(f"{filepath}: Malformed JSON-LD in block #{idx} ({e.msg} at line {e.lineno})")
            continue

        # single object, list, or @graph
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get("@graph", [data])
        else:
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            schema_type = item.get("@type", "")
            types = {schema_type} if isinstance(schema_type, str) else {x for x in schema_type if isinstance(x, str)}
            if types & VALID_BUSINESS_TYPES:
                has_valid_business_schema = True

    if not has_valid_business_schema:
        issues.append(f"{filepath}: JSON-LD present but missing LocalBusiness/HVACBusiness/Service @type")

    return issues


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

    # 3. Core money pages: official phone + business schema
    if is_core_page(filepath):
        issues += validate_core_page_schema_and_contact(filepath, content)

    return issues


def preflight_ok(local_path, remote_path: str = "") -> bool:
    """Used by deploy scripts: True if the file may be uploaded (non-HTML always passes).

    Set env CD_SKIP_PREFLIGHT=1 to override deliberately.
    """
    name = str(remote_path or local_path)
    if not name.lower().endswith(".html") or os.environ.get("CD_SKIP_PREFLIGHT") == "1":
        return True
    issues = validate_html_file(str(local_path))
    if remote_path and is_core_page(remote_path) and not is_core_page(str(local_path)):
        issues += validate_core_page_schema_and_contact(str(local_path), open(str(local_path), encoding="utf-8").read())
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


BASELINE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "html_preflight_baseline.txt")


def _load_baseline() -> set[str]:
    """Known, accepted legacy issues ('<relative/path>: <message>' per line). Empty if file missing."""
    if not os.path.exists(BASELINE_FILE):
        return set()
    with open(BASELINE_FILE, encoding="utf-8") as fh:
        return {ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")}


def _normalise(issue: str, target: str, root: str) -> str:
    rel = os.path.relpath(os.path.abspath(target), root).replace("\\", "/")
    return issue.replace(target, rel)


if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv          # ignore the baseline, report everything
    write_baseline = "--write-baseline" in sys.argv
    targets = args or _default_targets(root)
    found = [_normalise(i, t, root) for t in targets for i in validate_html_file(t)]
    if write_baseline:
        with open(BASELINE_FILE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("# Accepted legacy preflight issues. Remove a line once the page is fixed.\n")
            fh.write("\n".join(sorted(set(found))) + "\n")
        print(f"baseline written: {len(set(found))} entries")
        raise SystemExit(0)
    baseline = set() if strict else _load_baseline()
    new = [i for i in found if i not in baseline]
    known = [i for i in found if i in baseline]
    for i in known:
        print("KNOWN (baseline):", i)
    for i in new:
        print("ISSUE:", i)
    if not args:  # stale entries only meaningful on a full scan
        for i in sorted(baseline - set(found)):
            print("FIXED (remove from baseline):", i)
    print(f"html_preflight: {len(targets)} files checked, {len(new)} new issue(s), {len(known)} known")
    raise SystemExit(1 if new else 0)
