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
print("preflight dummy-contact rule:", "OK" if not fails else f"{fails} FAILURE(S)")
sys.exit(1 if fails else 0)
