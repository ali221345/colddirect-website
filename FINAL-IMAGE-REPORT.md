# FINAL-IMAGE-REPORT

Date: 2026-09-13
Scope: Delete unused heavy JPEGs after WebP swap. Brand fallbacks kept.

## Verify (before delete)

| Check | Result |
|---|---|
| `display-cabinets.webp` exists (root + public-html) | Yes |
| `pub-cellar.webp` exists (root + public-html) | Yes |
| `commercial-freezer-repair-london.webp` exists (root + public-html) | Yes |
| Grep `display-cabinets.jpg` in html/php/css/js/inc/asp | **0** |
| Grep `pub-cellar.jpg` in html/php/css/js/inc/asp | **0** |
| Grep `commercial-freezer.jpg` in html/php/css/js/inc/asp | **0** |
| `/images/brands/*.jpg` | Kept (not deleted) |

Backup list (sizes + SHA256): `OLD-IMAGES-BACKUP.txt`

## Deleted

| File | Size | Replacement |
|---|---|---|
| `/images/display-cabinets.jpg` | 2,574,752 (2.51 MB) | `/images/display-cabinets.webp` (61.9 KB) |
| `/images/pub-cellar.jpg` | 2,460,303 (2.40 MB) | `/images/pub-cellar.webp` (40.7 KB) |
| `/images/commercial-freezer.jpg` | 2,225,119 (2.17 MB) | `/images/commercial-freezer-repair-london.webp` (18.0 KB) |
| Same three under `/colddirect-public-html/images/` | same bytes | same WebPs |

Deleted this pass: **6 files**, **14,520,348 bytes** (~13.85 MB) across both image trees.

## Folder size before vs after

| Tree | Before delete | After delete | Saved |
|---|---|---|---|
| `/images/` | 17,995,629 (17.17 MB) | 10,735,455 (10.24 MB) | 7,260,174 (6.92 MB) |
| `/colddirect-public-html/images/` | 30,788,569 (29.36 MB) | 23,528,395 (22.44 MB) | 7,260,174 (6.92 MB) |
| Combined | 48,784,198 (46.53 MB) | 34,263,850 (32.67 MB) | 14,520,348 (13.85 MB) |

## Pages already on WebP (from BRAND-FIX-LOG)

- **54 HTML files** plus **2 PHP homepages** (`index.php` in root and `colddirect-public-html`)
- Brand pages now use named WebPs (Adexa, Empire, Hoshizaki, Polar, Williams, Sub-Zero, True stand-in)
- Type pages that used the three heavy JPGs now use WebP: commercial fridge (London + North), multideck, prep, blast-chiller, undercounter, commercial freezer (London + North + Tottenham), homepage, cellar, appliances, catering, display-cabinet North London, and related copies

## PageSpeed expected improvement

Not a live Lighthouse run. Estimate for pages whose first/hero image was one of the three JPGs:

| Metric | Before (2.1-2.5 MB JPEG) | After (18-62 KB WebP) |
|---|---|---|
| Image bytes on the wire | ~2,200-2,500 KB | ~18-62 KB (~97-99% less) |
| Download on Slow 4G (~1.6 Mbps) | ~11-13 s | ~0.1-0.4 s |
| LCP | Often 8-15 s+ if this was LCP | Often 2-6 s better; LCP image no longer the bottleneck |
| Mobile PageSpeed Insights | Heavy penalty on LCP + "properly size images" | Typical **+10 to +25** points on those URLs if nothing else is worse |

Homepage and commercial-fridge/multideck/prep/blast-chiller/undercounter/freezer pages should show the largest PSI lift.

## Pass 2 — cold-room.jpg (2026-09-13)

| | |
|---|---|
| Source | `/images/cold-room.jpg` 2,467,559 bytes (2.41 MB) |
| Encoder | `cwebp -q 75 -resize 800 0` |
| Output | `/images/cold-room.webp` **44,922 bytes (43.9 KB)** — under 150KB (slightly under 50-80KB aim) |
| Copy | `/colddirect-public-html/images/cold-room.webp` (same) |
| HTML/PHP | Replaced `cold-room.jpg` with `cold-room.webp` in **81 HTML pages** + `scripts/generate-areas.ps1` |
| Grep `/images/cold-room.jpg` or `images/cold-room.jpg` | **0** |
| Note | `blog-cold-room.jpg` in three blog og:image tags is a **different filename** — left as-is |

SHA256 of deleted JPEGs (both trees identical):

`34F1691DB05A11927C0EDD12CBBE2D9D086AAA99877B09BDD192576D84134690`

| Tree | After pass 1 | After pass 2 | Saved this pass |
|---|---|---|---|
| `/images/` | 10,735,455 (10.24 MB) | 8,312,818 (7.93 MB) | 2,422,637 (2.31 MB) |
| `/colddirect-public-html/images/` | 23,528,395 (22.44 MB) | 21,105,758 (20.13 MB) | 2,422,637 (2.31 MB) |
| Combined | 34,263,850 (32.67 MB) | 29,418,576 (28.06 MB) | **4,845,274 (4.62 MB)** |

Net vs original (before any heavy-JPEG delete): combined **48,784,198 → 29,418,576** saved **19,365,622 (~18.5 MB)**.

`/images/brands/*.jpg` still kept.

See `ALL-IMAGES-FIXED.md` for campaign checklist.
