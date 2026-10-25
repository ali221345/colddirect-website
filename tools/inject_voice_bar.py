"""Idempotently add the homepage voice widget script to every public HTML page.

Does not touch <title>, <h1>, meta descriptions, canonicals, JSON-LD, or V4 blocks.
Usage: python tools/inject_voice_bar.py [--check]
"""
import os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {
    ".git", ".github", ".cursor", ".vscode", "node_modules", "docs", "agent",
    "tools", "scripts", "logs", "App_Data", "images", "css", "js", "assets",
}
SKIP_PREFIX = ("_backup", "gsc-analysis", "AUDIT-", "audit-")
SCRIPT = '<script src="/assets/js/colddirect-voice-bar.js?v=20261025aa" defer></script>'
MARKER = "<!-- CD-VOICE-BAR-V1 -->"
BLOCK = MARKER + "\n" + SCRIPT + "\n"
HAS_SCRIPT = re.compile(r"colddirect-voice-bar\.js\?v=[^\"'\s>]+", re.I)
BUMP_V = re.compile(r'(src="/assets/js/colddirect-voice-bar\.js)\?v=[^"\']+"', re.I)
BODY = re.compile(r"</body\s*>", re.I)
HOVER = re.compile(r'(<script[^>]+cd-hover-card\.js[^>]*></script>)', re.I)
V4 = re.compile(r"<!--\s*AUTO-SEO-V4-2026\s*-->")
SEO = re.compile(
    r"<title\b|<h1\b|<meta\s+[^>]*(name|property)=[\"'](description|og:title|og:description|twitter:title|twitter:description)[\"']|<link\s+[^>]*rel=[\"']canonical[\"']|application/ld\+json|AUTO-SEO-V4-",
    re.I,
)


def targets():
    out = []
    for dp, dn, fn in os.walk(ROOT):
        rel = Path(dp).relative_to(ROOT).as_posix()
        top = rel.split("/", 1)[0] if rel != "." else ""
        if top in SKIP_DIRS:
            dn[:] = []
            continue
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if not f.endswith(".html"):
                continue
            if f.startswith(SKIP_PREFIX):
                continue
            out.append(Path(dp) / f)
    return sorted(out)


def inject(text):
    bumped = BUMP_V.sub(r'\1?v=20261025aa"', text, count=1)
    changed = bumped != text
    text = bumped
    if HAS_SCRIPT.search(text):
        # Keep the existing script; only tidy a leftover homepage-only comment.
        tidy = re.sub(r"<!--\s*CD-VOICE-BAR-V1 homepage-only test\s*-->\s*", MARKER + "\n", text, count=1)
        return tidy, changed or tidy != text
    if not BODY.search(text) or "<html" not in text.lower():
        return text, False
    if HOVER.search(text):
        new = HOVER.sub(r"\1\n" + BLOCK.rstrip() + "\n", text, count=1)
    elif V4.search(text):
        new = V4.sub(BLOCK + "<!-- AUTO-SEO-V4-2026 -->", text, count=1)
    else:
        new = BODY.sub(BLOCK + "</body>", text, count=1)
    return new, new != text


def seo_changed(old, new):
    def keys(s):
        return SEO.findall(s)
    return keys(old) != keys(new)


def main():
    check = "--check" in sys.argv
    changed = missing = 0
    for path in targets():
        raw = path.read_bytes()
        bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig")
        new, did = inject(text)
        if not HAS_SCRIPT.search(new) and BODY.search(text) and "<html" in text.lower():
            print("NO SCRIPT", path.relative_to(ROOT))
            missing += 1
            continue
        if not did:
            continue
        if seo_changed(text, new):
            print("SEO GUARD FIRED", path.relative_to(ROOT))
            sys.exit(2)
        changed += 1
        if check:
            continue
        data = new.encode("utf-8")
        if bom:
            data = b"\xef\xbb\xbf" + data
        path.write_bytes(data)
        print("injected", path.relative_to(ROOT))
    print(f"{'would change' if check else 'changed'} {changed} files; missing {missing}")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
