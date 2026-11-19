#!/usr/bin/env python3
"""One-shot consolidation: fold unique content from the retired
/blog/why-commercial-freezer-icing-up/ into the survivor
/blog/commercial-freezer-ice-buildup-causes/, refresh dateModified to
2026-11-19, then sync the 3 byte-identical copies (root .html + both mirrors).
"""
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "blog" / "commercial-freezer-ice-buildup-causes" / "index.html"
COPIES = [
    ROOT / "blog" / "commercial-freezer-ice-buildup-causes.html",
    ROOT / "colddirect-public-html" / "blog" / "commercial-freezer-ice-buildup-causes" / "index.html",
    ROOT / "colddirect-public-html" / "blog" / "commercial-freezer-ice-buildup-causes.html",
]

text = SRC.read_text(encoding="utf-8")
edits = []

def rep(old, new, label):
    global text
    if old not in text:
        print(f"MISS: {label}")
        sys.exit(1)
    if text.count(old) != 1:
        print(f"NOT-UNIQUE ({text.count(old)}): {label}")
        sys.exit(1)
    text = text.replace(old, new)
    edits.append(label)

# 1) Visible <time> dateModified
rep(
    '<p class="byline">Published 5 Sep 2025 · 8 min read</p>',
    '<p class="byline">Published 5 Sep 2025 · Updated <time datetime="2026-11-19">19 Nov 2026</time> · 8 min read</p>',
    "byline time/dateModified",
)

# 2) BlogPosting schema with dateModified
rep(
    '</script>\n<script type="application/ld+json" data-cd-schema="top-right-welcome-audio">',
    '''</script>
<script type="application/ld+json" data-cd-schema="blogposting">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "@id": "https://www.colddirect.co.uk/blog/commercial-freezer-ice-buildup-causes/#article",
  "headline": "Why Is My Commercial Freezer Icing Up? 5 Causes & Fixes",
  "description": "Commercial freezer icing up? Learn 5 common causes of ice buildup in commercial freezers & when to defrost vs call an engineer in London.",
  "datePublished": "2025-09-05",
  "dateModified": "2026-11-19",
  "inLanguage": "en-GB",
  "mainEntityOfPage": "https://www.colddirect.co.uk/blog/commercial-freezer-ice-buildup-causes/",
  "author": {"@id": "https://www.colddirect.co.uk/#business"},
  "publisher": {"@id": "https://www.colddirect.co.uk/#business"}
}
</script>
<script type="application/ld+json" data-cd-schema="top-right-welcome-audio">''',
    "BlogPosting schema dateModified 2026-11-19",
)

# 3) Door seal section: door-frame heater + magnetic strip checks
rep(
    "Close a piece of paper in the door. If it slides out with no grip, the gasket has lost tension.</p>",
    "Close a piece of paper in the door. If it slides out with no grip, the gasket has lost tension. "
    "Two less obvious checks sit next to the seal. A failed door-frame (perimeter) heater leaves a wet stripe "
    "around the frame that freezes into a wedge, so the door stops sealing even with a healthy gasket. On "
    "magnetic gaskets the strip inside the rubber wears first on doors that are slammed through service; if "
    "the magnet no longer pulls evenly along its length, fit the correct replacement profile rather than "
    "taping or gluing the old one.</p>",
    "door-frame heater + magnetic gasket checks",
)

# 4) Blocked drain: failed drain heater sends water back to the fan
rep(
    "If the drain heater (where fitted) has failed, the plug will form again on the next cycle.</p>",
    "If the drain heater (where fitted) has failed, the plug will form again on the next cycle. A dead drain "
    "heater also sends melt water back towards the fan instead of out of the cabinet; the giveaway is ice "
    "growing from the bottom of the liner upwards, often with ice chips thrown onto product.</p>",
    "drain heater failure symptoms",
)

# 5) Faulty defrost heater: klixon/probe, timer, power-cut controller, error code
rep(
    "An engineer will test heater resistance and look at the controller\u2019s defrost history. This is not a "
    "\u201cturn it off overnight\u201d fix if the same ice returns the next afternoon.</p>",
    "An engineer will test heater resistance and look at the controller\u2019s defrost history. This is not a "
    "\u201cturn it off overnight\u201d fix if the same ice returns the next afternoon. The defrost circuit has "
    "several failure points and they are tested in order: heater element resistance, the defrost timer or "
    "controller channel, the termination klixon (defrost termination thermostat) or evaporator probe that ends "
    "the cycle once the coil is warm, and the drain heater that keeps melt water moving. A controller that "
    "silently skips defrost after a power cut makes the fault look like \u201cit iced up overnight\u201d. "
    "Photograph any error code on the controller before resetting it \u2014 that code can halve the diagnosis "
    "time.</p>",
    "defrost heater/klixon/probe detail",
)

# 6) Refrigerant leak stripe + natural links to the three money pages
rep(
    "<p>For a booked diagnosis on uprights and rooms, see ",
    "<p>Ice that forms in a stripe on one patch of the coil while the rest of the cabinet warms points to a "
    "refrigerant leak rather than a defrost fault. Topping up refrigerant without a proper leak test is "
    "illegal without F-Gas certification and the ice simply returns, so that pattern goes straight to an "
    "engineer.</p>\n      <p>For a booked diagnosis on uprights and rooms, see ",
    "refrigerant leak stripe paragraph",
)
rep(
    '<a href="/freezer-repair-london/" data-cd-popover="Commercial Freezer Repair London">freezer repair London</a> or <a href="/commercial-freezer-repair-north-london/" data-cd-popover="Commercial Freezer Repair London">commercial freezer repair north london</a>.',
    '<a href="/commercial-freezer-repair-london/" data-cd-popover="Commercial Freezer Repair London">commercial freezer repair London</a>, <a href="/freezer-repair-london/" data-cd-popover="Commercial Freezer Repair London">freezer repair London</a> or our <a href="/commercial-freezer-repair-north-london/" data-cd-popover="Commercial Freezer Repair London">North London freezer engineers</a>.',
    "natural links: commercial-freezer-repair-london + freezer-repair-london",
)
rep(
    "Walk-in rooms with ice on the evaporator need a trade visit; the refrigerant circuit and heaters are not DIY.",
    "Walk-in rooms with ice on the evaporator need a trade visit \u2014 see <a href=\"/cold-room-repair-london/\" "
    "data-cd-popover=\"Walk-In Cold Room Engineers London\">cold room repair London</a>; the refrigerant circuit "
    "and heaters are not DIY.",
    "natural link: cold-room-repair-london",
)

SRC.write_text(text, encoding="utf-8")
for dst in COPIES:
    shutil.copyfile(SRC, dst)
print("Applied edits:")
for e in edits:
    print(" -", e)
print("Synced", len(COPIES), "copies.")
