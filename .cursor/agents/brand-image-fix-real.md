---
name: brand-image-fix-real
description: Create missing brand images, compress heavy generics, update HTML src
---
ROLE: Fix Real Image Problems
TASK 1 - Create missing brand images (8 files):
For each missing in root:
- images/brands/adexa.jpg -> COPY /colddirect-public-html/images/adexa-fridge.webp to /images/adexa-fridge-repair-london.webp AND /images/brands/adexa.jpg + also root copy
- images/brands/empire.jpg -> copy empire-fridge.webp
- images/brands/hoshizaki.jpg -> copy hoshizaki-ice-machine.webp to hoshizaki-ice-machine-repair-london.webp AND brands/hoshizaki.jpg
- images/brands/polar.jpg -> copy /colddirect-public-html/images/polar-fridge.webp to /images/polar-fridge-repair-london.webp AND brands/polar.jpg
- images/brands/williams.jpg -> copy williams-fridge.webp to williams-fridge-repair-london.webp AND brands/williams.jpg + williams-freezer-repair-london.webp
- images/brands/subzero-fridge.jpg + subzero-freezer.jpg -> copy sub-zero-fridge.webp to both names
- /images/true-fridge-repair-london.webp -> copy foster-fridge-repair-london.webp to true name (35KB) - temp professional
All: cwebp -q 75 -resize 800 0, webp, <150KB, copy to both /images/ and /colddirect-public-html/images/
TASK 2 - Compress heavy generic images (the 2.5MB killers):
- /images/display-cabinets.jpg (2514KB) -> compress to /images/display-cabinets.webp 800px q75 <150KB, then update all HTML that use it (commercial-fridge, multideck, prep, blast-chiller, north-london etc) to use webp version
- /images/pub-cellar.jpg (2402KB) -> compress to pub-cellar.webp 800px <150KB
- /images/commercial-freezer.jpg (2173KB) -> compress to commercial-freezer-repair-london.webp 800px <150KB
- /images/bottle-cooler.webp (244KB) -> check, if >150KB compress
TASK 3 - Update HTML src to point to new correct webp files
OUTPUT: BRAND-FIX-LOG.md with before/after sizes
RUN NOW
