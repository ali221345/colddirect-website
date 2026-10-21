#!/usr/bin/env python3
"""Repo-wide phone / contact consistency sweep.

1. Dummy / placeholder contact patterns in every .html (root + colddirect-public-html mirror):
   '123 4567', '1234567', '123456', runs of 0000 / 9999 inside phone-like numbers, example.com/.org/.net.
2. Every tel: link must be one of the three official numbers.
3. Every area page (see area_pages_audit.area_slugs) must show the official mobile 07983 759320
   (visible + tel:+447983759320) and info@colddirect.co.uk (visible + mailto:).

--fix  injects an idempotent contact block (marker CD-AREA-CONTACT-V1) into area pages lacking them
       (all 4 copies kept identical). --check exits 1 on any remaining problem.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import area_pages_audit as ap  # noqa: E402

ROOT = ap.ROOT
OFFICIAL_TEL = {"+447983759320", "08001123427", "+442039524822"}
MOBILE_TXT = "07983 759320"
EMAIL = "info@colddirect.co.uk"
MARK = "<!-- CD-AREA-CONTACT-V1 -->"
END = "<!-- /CD-AREA-CONTACT-V1 -->"

DUMMY = re.compile(
    r"(?:\b0\d{2,4}[\s-]?123[\s-]?4567\b|123[\s-]?4567|\b1234567\b|\b0\d{2,4}[\s-]?123456\b|"
    r"\+?\d[\d\s-]{4,}(?:0000|9999)\b|\b[\w.+-]+@(?:[\w-]+\.)?example\.(?:com|org|net)\b|"
    r"https?://(?:www\.)?example\.(?:com|org|net)|\bexample\.(?:com|org|net)\b)", re.I)
TEL = re.compile(r'href="tel:([^"]+)"', re.I)
# unofficial / legacy forms -> official ones (applied by --fix to every html file)
REPLACE = (
    ("tel:+442080502374", "tel:+442039524822"),
    ("020 8050 2374", "0203 952 4822"),
    ("02080502374", "02039524822"),
    ("tel:07983759320", "tel:+447983759320"),
    ("tel:02039524822", "tel:+442039524822"),
)
LEGACY_TEXT = re.compile(r"020\s?8050\s?2374|\+?44\s?20\s?8050\s?2374")

SKIP_DIRS = {"node_modules", ".git", "tools", "docs", "agent", "logs", "App_Data", ".github"}


def html_files():
    for base in (ROOT, ROOT / "colddirect-public-html"):
        for p in base.rglob("*.html"):
            rel = p.relative_to(ROOT).parts
            if rel[0] in SKIP_DIRS or (base == ROOT and rel[0] == "colddirect-public-html"):
                continue
            yield p


def scan():
    problems = []
    for p in html_files():
        t = p.read_text(encoding="utf-8", errors="replace")
        for m in DUMMY.finditer(t):
            problems.append((p, f"dummy contact pattern: {m.group(0)!r}"))
        for m in LEGACY_TEXT.finditer(t):
            problems.append((p, f"legacy/unofficial number text: {m.group(0)!r}"))
        for m in TEL.finditer(t):
            num = re.sub(r"[\s().-]", "", m.group(1))
            if num not in OFFICIAL_TEL:
                problems.append((p, f"non-official tel: {m.group(1)!r}"))
    return problems


def contact_block():
    return (f'{MARK}<section class="section"><div class="wrap"><p class="cd-contact-line">'
            f'<strong>Call Cold Direct 24/7:</strong> '
            f'<a href="tel:+447983759320">Mobile {MOBILE_TXT}</a> &middot; '
            f'<a href="tel:08001123427">Freephone 0800 112 3427</a> &middot; '
            f'<a href="tel:+442039524822">London office 0203 952 4822</a> &middot; '
            f'<a href="mailto:{EMAIL}">{EMAIL}</a></p></div></section>{END}\n')


def has_contacts(t):
    return (MOBILE_TXT in t and "tel:+447983759320" in t and EMAIL in t and "mailto:" + EMAIL in t)


def main():
    fix = "--fix" in sys.argv
    check = "--check" in sys.argv
    bad = 0
    if fix:
        n = 0
        for p in html_files():
            raw = p.read_bytes().decode("utf-8", errors="replace")
            new = raw
            for a, b in REPLACE:
                new = new.replace(a, b)
            if new != raw:
                p.write_bytes(new.encode("utf-8"))
                n += 1
        print(f"number normalisation: {n} file(s) rewritten")
    for p, msg in scan():
        print(f"BAD   {p.relative_to(ROOT)}: {msg}")
        bad += 1

    areas = ap.area_slugs()
    missing = []
    for slug in areas:
        src = ap.copies(slug)["root .html"]
        if not src.exists():
            src = ap.copies(slug)["root /index.html"]
        t = src.read_text(encoding="utf-8")
        if not has_contacts(t):
            missing.append(slug)
    print(f"area pages: {len(areas)} | missing mobile/email: {len(missing)}")
    for slug in missing:
        print(f"  lacks contact details: {slug}")
        if fix:
            for name, p in ap.copies(slug).items():
                if not p.exists():
                    continue
                raw = p.read_bytes().decode("utf-8")
                if MARK in raw:
                    continue
                crlf = "\r\n" in raw
                t = raw.replace("\r\n", "\n")
                block = contact_block()
                for pat in (r'<section class="cta-band"', r"<!-- CD-9-MONEY-KEYWORD-SILO-V47 -->", r"<footer\b",
                            r"<!-- AUTO-SEO-V4-2026 -->", r"</body>"):
                    m = re.search(pat, t, re.I)
                    if m:
                        t = t[: m.start()] + block + t[m.start():]
                        break
                else:
                    raise SystemExit(f"no insertion point: {p}")
                if crlf:
                    t = t.replace("\n", "\r\n")
                p.write_bytes(t.encode("utf-8"))
        else:
            bad += 1
    return 1 if (check and bad) else 0


if __name__ == "__main__":
    sys.exit(main())
