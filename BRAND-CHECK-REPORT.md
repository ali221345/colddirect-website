# BRAND-CHECK-REPORT.md

Brand Image Auditor - CHECK ONLY. No files were deleted, replaced, or compressed.

Scan: root `*.html` and `colddirect-public-html/*.html` only. First `<img>` per file.

No HTML files matched blizzard, kenwood, samsung, beko, electrolux, leibherr/liebherr.

## Summary

- Total files scanned (matching brand/type in filename): **38**
- Files with NO image: **0**
- Files with WRONG brand image: **0**
- Files with correct image (has img, brand in src matches filename or src has no other brand): **38**

WRONG brand means the image `src` names a brand that is not in the HTML filename (example: True page using Polar). None of the 38 files do that.

First-image type/generic mismatches (not counted as WRONG brand): blast-chiller, multideck, prep-fridge, and commercial-fridge pages use `display-cabinets.jpg`; undercounter uses `pub-cellar.jpg`; display-fridge pages use `bottle-cooler.webp`. Root commercial-freezer pages use `commercial-freezer.jpg` instead of the named webp. Several root brand pages point at missing `images/brands/*.jpg`. True page `src` is `/images/true-fridge-repair-london.webp` (correct name, file missing on disk).

### Missing image files (src set, not found on disk)

- `images/brands/subzero-freezer.jpg`
- `/images/true-fridge-repair-london.webp`
- `images/brands/adexa.jpg`
- `images/brands/empire.jpg`
- `images/brands/hoshizaki.jpg`
- `images/brands/polar.jpg`
- `images/brands/subzero-fridge.jpg`
- `images/brands/williams.jpg`

WRONG = image `src` names a brand that is not in the HTML filename (e.g. True page using Polar). Type pages using a specific other-brand filename are also marked WRONG.

| # | File | Current Image src | Alt | Exists? | Size | WRONG? | Should Be | Location |
|---|---|---|---|---|---|---|---|---|
| 1 | adexa-fridge-repair-london.html | `/images/adexa-fridge.webp` | Adexa stainless commercial fridge product shot, +4C display, studio white bac... | Yes | 132.3KB | No | `/images/adexa-fridge-repair-london.webp` | colddirect-public-html |
| 2 | blast-chiller-repair-london.html | `/images/display-cabinets.jpg` | Commercial blast chiller in a London catering kitchen | Yes | 2,514.4KB | No | `/images/blast-chiller-repair-london.webp` | colddirect-public-html |
| 3 | commercial-freezer-repair-london.html | `/images/commercial-freezer-repair-london.webp` | Walk-in freezer room at -20C with two refrigeration engineers | Yes | 328.3KB | No | `/images/commercial-freezer-repair-london.webp` | colddirect-public-html |
| 4 | commercial-freezer-repair-north-london.html | `/images/commercial-freezer.jpg` | Commercial freezer repair North London on an upright trade freezer | Yes | 2,173.0KB | No | `/images/commercial-freezer-repair-london.webp` | colddirect-public-html |
| 5 | commercial-freezer-repair-tottenham.html | `/images/commercial-freezer.jpg` | Commercial freezer repair Tottenham | Yes | 2,173.0KB | No | `/images/commercial-freezer-repair-london.webp` | colddirect-public-html |
| 6 | commercial-fridge-repair-london.html | `/images/display-cabinets.jpg` | Commercial fridge repair london on a glass-door catering fridge | Yes | 2,514.4KB | No | `/images/commercial-fridge-repair-london.webp` | colddirect-public-html |
| 7 | commercial-fridge-repair-north-london.html | `images/display-cabinets.jpg` | Commercial fridge cabinets used in shops and kitchens | Yes | 2,514.4KB | No | `/images/commercial-fridge-repair-london.webp` | colddirect-public-html |
| 8 | display-fridge-repair.html | `/images/bottle-cooler.webp` | Commercial glass-door display fridge at +4C with water and soft drinks | Yes | 244.5KB | No | `/images/display-fridge-repair-london.webp` | colddirect-public-html |
| 9 | display-fridge-repair-london.html | `/images/bottle-cooler.webp` | Commercial glass-door display fridge at +4C with water and soft drinks | Yes | 244.5KB | No | `/images/display-fridge-repair-london.webp` | colddirect-public-html |
| 10 | empire-fridge-repair.html | `/images/empire-fridge.webp` | Empire commercial fridge product shot, +3C display, studio white background | Yes | 137.7KB | No | `/images/empire-fridge-repair-london.webp` | colddirect-public-html |
| 11 | empire-fridge-repair-london.html | `/images/empire-fridge.webp` | Empire commercial fridge product shot, +3C display, studio white background | Yes | 137.7KB | No | `/images/empire-fridge-repair-london.webp` | colddirect-public-html |
| 12 | foster-fridge-repair-london.html | `/images/foster-fridge-repair-london.webp` | Foster Fridge Repair London | Yes | 34.2KB | No | `/images/foster-fridge-repair-london.webp` | colddirect-public-html |
| 13 | gram-fridge-repair-london.html | `/images/gram-fridge-repair.webp` | Gram fridge repair London | Yes | 27.3KB | No | `/images/gram-fridge-repair-london.webp` | colddirect-public-html |
| 14 | hoshizaki-ice-machine-repair-london.html | `/images/hoshizaki-ice-machine.webp` | Hoshizaki commercial ice machine repair London — stainless ice bin full of cubes | Yes | 29.3KB | No | `/images/hoshizaki-ice-machine-repair-london.webp` | colddirect-public-html |
| 15 | multideck-fridge-repair-london.html | `/images/display-cabinets.jpg` | Commercial multideck fridge in a London shop | Yes | 2,514.4KB | No | `/images/multideck-fridge-repair-london.webp` | colddirect-public-html |
| 16 | polar-fridge-repair-london.html | `/images/polar-fridge.webp` | Polar commercial fridge product shot, +3C display, studio white background | Yes | 154.2KB | No | `/images/polar-fridge-repair-london.webp` | colddirect-public-html |
| 17 | prep-fridge-repair-london.html | `/images/display-cabinets.jpg` | Commercial prep fridge on a London restaurant line | Yes | 2,514.4KB | No | `/images/prep-fridge-repair-london.webp` | colddirect-public-html |
| 18 | subzero-freezer-repair-london.html | `images/brands/subzero-freezer.jpg` | Sub-Zero freezer repair - commercial freezer repair london | No | - | No | `/images/subzero-freezer-repair-london.webp` | colddirect-public-html |
| 19 | subzero-fridge-repair-london.html | `/images/sub-zero-fridge.webp` | Sub-Zero refrigerator product shot, +3C display, studio white background | Yes | 146.8KB | No | `/images/subzero-fridge-repair-london.webp` | colddirect-public-html |
| 20 | true-fridge-repair-london.html | `/images/true-fridge-repair-london.webp` | True Fridge Repair London | No | - | No | `/images/true-fridge-repair-london.webp` | colddirect-public-html |
| 21 | undercounter-fridge-repair-london.html | `/images/pub-cellar.jpg` | Commercial undercounter fridge in a London kitchen | Yes | 2,402.6KB | No | `/images/undercounter-fridge-repair-london.webp` | colddirect-public-html |
| 22 | williams-freezer-repair-london.html | `/images/homepage/williams-freezer.webp` | Williams Jade commercial cabinet product shot, studio white background | Yes | 124.3KB | No | `/images/williams-freezer-repair-london.webp` | colddirect-public-html |
| 23 | williams-fridge-repair-london.html | `/images/williams-fridge.webp` | Williams Jade commercial fridge product shot, +3C display, studio white backg... | Yes | 124.3KB | No | `/images/williams-fridge-repair-london.webp` | colddirect-public-html |
| 24 | adexa-fridge-repair-london.html | `images/brands/adexa.jpg` | Adexa fridge repair | No | - | No | `/images/adexa-fridge-repair-london.webp` | root |
| 25 | blast-chiller-repair-london.html | `/images/display-cabinets.jpg` | Commercial blast chiller in a London catering kitchen | Yes | 2,514.4KB | No | `/images/blast-chiller-repair-london.webp` | root |
| 26 | commercial-freezer-repair-london.html | `/images/commercial-freezer.jpg` | Commercial freezer repair london on an upright trade freezer | Yes | 2,173.0KB | No | `/images/commercial-freezer-repair-london.webp` | root |
| 27 | commercial-freezer-repair-north-london.html | `/images/commercial-freezer.jpg` | Commercial freezer repair North London on an upright trade freezer | Yes | 2,173.0KB | No | `/images/commercial-freezer-repair-london.webp` | root |
| 28 | commercial-fridge-repair-london.html | `/images/display-cabinets.jpg` | Commercial fridge repair london on a glass-door catering fridge | Yes | 2,514.4KB | No | `/images/commercial-fridge-repair-london.webp` | root |
| 29 | commercial-fridge-repair-north-london.html | `images/display-cabinets.jpg` | Commercial fridge cabinets used in shops and kitchens | Yes | 2,514.4KB | No | `/images/commercial-fridge-repair-london.webp` | root |
| 30 | empire-fridge-repair-london.html | `images/brands/empire.jpg` | Empire fridge repair | No | - | No | `/images/empire-fridge-repair-london.webp` | root |
| 31 | hoshizaki-ice-machine-repair-london.html | `images/brands/hoshizaki.jpg` | Hoshizaki ice machine repair | No | - | No | `/images/hoshizaki-ice-machine-repair-london.webp` | root |
| 32 | multideck-fridge-repair-london.html | `/images/display-cabinets.jpg` | Commercial multideck fridge in a London shop | Yes | 2,514.4KB | No | `/images/multideck-fridge-repair-london.webp` | root |
| 33 | polar-fridge-repair-london.html | `images/brands/polar.jpg` | Polar fridge repair | No | - | No | `/images/polar-fridge-repair-london.webp` | root |
| 34 | prep-fridge-repair-london.html | `/images/display-cabinets.jpg` | Commercial prep fridge on a London restaurant line | Yes | 2,514.4KB | No | `/images/prep-fridge-repair-london.webp` | root |
| 35 | subzero-freezer-repair-london.html | `images/brands/subzero-freezer.jpg` | Sub-Zero freezer repair - commercial freezer repair london | No | - | No | `/images/subzero-freezer-repair-london.webp` | root |
| 36 | subzero-fridge-repair-london.html | `images/brands/subzero-fridge.jpg` | Sub-Zero fridge repair | No | - | No | `/images/subzero-fridge-repair-london.webp` | root |
| 37 | undercounter-fridge-repair-london.html | `/images/pub-cellar.jpg` | Commercial undercounter fridge in a London kitchen | Yes | 2,402.6KB | No | `/images/undercounter-fridge-repair-london.webp` | root |
| 38 | williams-freezer-repair-london.html | `images/brands/williams.jpg` | Williams freezer repair - commercial freezer repair london | No | - | No | `/images/williams-freezer-repair-london.webp` | root |
