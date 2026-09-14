# WRONG-IMAGES-REPORT.md

Deep Image Auditor — 2026-09-13  
Scanned root `*.html` and `colddirect-public-html/*.html` where the **filename** contains a brand (Williams, Foster, True, Gram, Polar, Blizzard, Adexa, Empire, Hoshizaki, Sub-Zero).

WRONG = `src` or `alt` names a **different** brand than the filename.

| File | Current Image | Should Be | Location |
|---|---|---|---|
| true-fridge-repair-london.html | `/images/polar-fridge-repair.webp` (Polar file, True alt) | `/images/true-fridge-repair-london.webp` | colddirect-public-html |
| foster-fridge-repair-london.html | *(no `<img>`)* | `/images/foster-fridge-repair-london.webp` | colddirect-public-html |

## Fixes applied

- **True:** Polar src replaced with `/images/true-fridge-repair-london.webp`, alt `True Fridge Repair London`, lazy, 800×600, max-width 600px centered. **Binary file is missing** — logged in `MISSING-IMAGES.txt`. Do not reuse Polar.
- **Foster:** Added `/images/foster-fridge-repair-london.webp` (copied from existing `foster-fridge-repair.webp`, ~34 KB). Alt `Foster Fridge Repair London`.

## Brand-matched (not WRONG)

These filenames match the image brand. They were **not** swapped to another make.

| File | Image | Location |
|---|---|---|
| williams-fridge-repair-london.html | `/images/williams-fridge.webp` | colddirect-public-html |
| williams-freezer-repair-london.html | williams.jpg / williams-freezer.webp | root + public-html |
| gram-fridge-repair-london.html | `/images/gram-fridge-repair.webp` | colddirect-public-html |
| polar-fridge-repair-london.html | polar.jpg / polar-fridge.webp | root + public-html |
| adexa-fridge-repair-london.html | adexa.jpg / adexa-fridge.webp | root + public-html |
| empire-fridge-repair-london.html | empire.jpg / empire-fridge.webp | root + public-html |
| subzero-fridge-repair-london.html | subzero / sub-zero fridge | root + public-html |
| subzero-freezer-repair-london.html | subzero-freezer.jpg | root + public-html |
| hoshizaki-ice-machine-repair-london.html | hoshizaki.jpg / hoshizaki-ice-machine.webp | root + public-html |

No Blizzard-named HTML pages found. No True/Foster HTML in repo **root**.

## daily-job.php

`colddirect-public-html/daily-job.php` now skips restore copies when the **source filename brand ≠ destination brand** (e.g. will not copy `polar-fridge.webp` onto a Williams target). Logs `SKIP_BRAND_MISMATCH`.
