#!/usr/bin/env python3
"""Regression test: html_preflight must block dummy phone / example contact details and accept the real ones."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import html_preflight as hp  # noqa: E402

BAD = [
    '<a href="tel:02071234567" class="cta">CALL NOW: 0207 123 4567</a>',
    "<p>Call 020 1234567 today</p>",
    "<p>Call 1234567</p>",
    "<p>Call 020 123456</p>",
    '<a href="tel:+442000000000">x</a>',
    "<p>Phone 07700 909999</p>",
    '<a href="mailto:test@example.com">mail</a>',
    '<a href="https://example.com/x">x</a>',
]
GOOD = [
    '<a href="tel:+447983759320">Mobile 07983 759320</a> <a href="tel:08001123427">0800 112 3427</a>',
    '<a href="tel:+442039524822">0203 952 4822</a> <a href="mailto:info@colddirect.co.uk">info@colddirect.co.uk</a>',
    "<style>.a{color:#000000;width:1234567px}</style><script>var n=1234567;</script><p>Prices from \u00a3199</p>",
]

fails = 0
for s in BAD:
    if not hp.find_dummy_contact_issues("t.html", s):
        print("NOT BLOCKED:", s)
        fails += 1
for s in GOOD:
    r = hp.find_dummy_contact_issues("t.html", s)
    if r:
        print("FALSE POSITIVE:", s, r)
        fails += 1

# --- site-wide unique <title>/<h1> rule ---
import tempfile  # noqa: E402

PAGE = ('<!DOCTYPE html><html><head><title>{t}</title><link rel="canonical" href="https://www.colddirect.co.uk/{c}/">'
        '{extra}</head><body><h1>{h}</h1></body></html>')
with tempfile.TemporaryDirectory() as d:
    def mk(name, t, c, h, extra=""):
        p = Path(d) / name
        p.write_text(PAGE.format(t=t, c=c, h=h, extra=extra), encoding="utf-8")
        return str(p)

    dup = [mk("a.html", "Same Title", "a", "H A"), mk("b.html", "Same Title", "b", "H B")]
    if not hp.duplicate_title_h1_issues(dup):
        print("NOT BLOCKED: duplicate title across two pages")
        fails += 1
    duph = [mk("c.html", "T C", "c", "Same H"), mk("d.html", "T D", "d", "Same H")]
    if not hp.duplicate_title_h1_issues(duph):
        print("NOT BLOCKED: duplicate h1 across two pages")
        fails += 1
    ok = [mk("e.html", "Title E", "e", "H E"), mk("e2.html", "Title E", "e", "H E"),  # .html + /index.html copy of one page
          mk("f.html", "Title E", "f", "H F", '<meta name="robots" content="noindex">')]  # noindex ignored
    if hp.duplicate_title_h1_issues(ok):
        print("FALSE POSITIVE: copies / noindex page flagged")
        fails += 1

print("preflight dummy-contact rule:", "OK" if not fails else f"{fails} FAILURE(S)")
sys.exit(1 if fails else 0)
