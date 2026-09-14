# BRAND-FIX-LOG

Fix Real Image Problems - created missing brand files, compressed heavy generics, updated HTML src. No unrelated files deleted.

Encoder: cwebp -q 75 (lower if still over 150KB) -resize 800 0

## Before / after sizes

| Output | Source (before) | After | Quality | Under 150KB |
|---|---|---|---|---|
| `/images/adexa-fridge-repair-london.webp` | 132.3 KB | 4.1 KB | 75 | Yes |
| `/images/empire-fridge-repair-london.webp` | 137.7 KB | 5.4 KB | 75 | Yes |
| `/images/hoshizaki-ice-machine-repair-london.webp` | 29.3 KB | 25.3 KB | 75 | Yes |
| `/images/polar-fridge-repair-london.webp` | 154.2 KB | 11.5 KB | 75 | Yes |
| `/images/williams-fridge-repair-london.webp` | 124.3 KB | 5.9 KB | 75 | Yes |
| `/images/williams-freezer-repair-london.webp` | 124.3 KB | 5.9 KB | 75 | Yes |
| `/images/subzero-fridge-repair-london.webp` | 146.8 KB | 5.1 KB | 75 | Yes |
| `/images/subzero-freezer-repair-london.webp` | 146.8 KB | 5.1 KB | 75 | Yes |
| `/images/true-fridge-repair-london.webp` | 34.2 KB | 30.7 KB | 75 | Yes |
| `/images/display-cabinets.webp` | 2,514.4 KB | 61.9 KB | 75 | Yes |
| `/images/pub-cellar.webp` | 2,402.6 KB | 40.7 KB | 75 | Yes |
| `/images/commercial-freezer-repair-london.webp` | 2,173.0 KB | 18.0 KB | 75 | Yes |
| `/images/bottle-cooler.webp` | 244.5 KB | 28.1 KB | 75 | Yes |

## JPEG brand fallbacks (also copied to both image trees)

| File | Size |
|---|---|
| `/images/brands/adexa.jpg` | 19.5 KB |
| `/images/brands/empire.jpg` | 22.6 KB |
| `/images/brands/hoshizaki.jpg` | 47.2 KB |
| `/images/brands/polar.jpg` | 28.2 KB |
| `/images/brands/williams.jpg` | 19.3 KB |
| `/images/brands/subzero-fridge.jpg` | 21.8 KB |
| `/images/brands/subzero-freezer.jpg` | 21.8 KB |

## HTML files updated

- `adexa-fridge-repair-london.html`
- `appliances-repair-london.html`
- `blast-chiller-repair-london.html`
- `bottle-cooler-repair-london.html`
- `catering-repair-london.html`
- `cellar-cooler-repair-london.html`
- `colddirect-public-html/adexa-fridge-repair-london.html`
- `colddirect-public-html/appliances-repair-london.html`
- `colddirect-public-html/blast-chiller-repair-london.html`
- `colddirect-public-html/catering-repair-london.html`
- `colddirect-public-html/cellar-cooler-repair-london.html`
- `colddirect-public-html/commercial-appliances-repair-london.html`
- `colddirect-public-html/commercial-freezer-repair-london.html`
- `colddirect-public-html/commercial-freezer-repair-north-london.html`
- `colddirect-public-html/commercial-freezer-repair-tottenham.html`
- `colddirect-public-html/commercial-fridge-repair-london.html`
- `colddirect-public-html/commercial-fridge-repair-north-london.html`
- `colddirect-public-html/display-cabinet-repair-north-london.html`
- `colddirect-public-html/empire-fridge-repair.html`
- `colddirect-public-html/empire-fridge-repair-london.html`
- `colddirect-public-html/freezer-repair-london.html`
- `colddirect-public-html/freezer-room-repair-north-london.html`
- `colddirect-public-html/hoshizaki-ice-machine-repair-london.html`
- `colddirect-public-html/image-preview.html`
- `colddirect-public-html/index.html`
- `colddirect-public-html/multideck-fridge-repair-london.html`
- `colddirect-public-html/polar-fridge-repair-london.html`
- `colddirect-public-html/prep-fridge-repair-london.html`
- `colddirect-public-html/subzero-freezer-repair-london.html`
- `colddirect-public-html/subzero-fridge-repair-london.html`
- `colddirect-public-html/supermarket-freezer-repair-london.html`
- `colddirect-public-html/undercounter-fridge-repair-london.html`
- `colddirect-public-html/williams-freezer-repair-london.html`
- `colddirect-public-html/williams-fridge-repair-london.html`
- `commercial-appliances-repair-london.html`
- `commercial-freezer-repair-london.html`
- `commercial-freezer-repair-north-london.html`
- `commercial-fridge-repair-london.html`
- `commercial-fridge-repair-north-london.html`
- `display-cabinet-repair-north-london.html`
- `empire-fridge-repair-london.html`
- `freezer-repair-london.html`
- `freezer-room-repair-north-london.html`
- `hoshizaki-ice-machine-repair-london.html`
- `index.html`
- `multideck-fridge-repair-london.html`
- `polar-fridge-repair-london.html`
- `prep-fridge-repair-london.html`
- `preview-colddirect-homepage.html`
- `subzero-freezer-repair-london.html`
- `subzero-fridge-repair-london.html`
- `supermarket-freezer-repair-london.html`
- `undercounter-fridge-repair-london.html`
- `williams-freezer-repair-london.html`

Also updated `index.php` and `colddirect-public-html/index.php` (same display-cabinets / pub-cellar srcs as the homepage HTML).

Total HTML files touched: **54** (+ 2 PHP homepages)

Note: `true-fridge-repair-london.webp` is a temporary professional stand-in from Foster (same 800px encode). Replace with a True cabinet photo when available.
