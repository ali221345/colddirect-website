# ALL-IMAGES-FIXED

Date: 2026-09-13
Campaign: missing brand files + compress/delete heavy JPEGs (display-cabinets, pub-cellar, commercial-freezer, cold-room).

## Checklist (this campaign)

| Item | Status |
|---|---|
| Missing named brand/type files (the 8 from BRAND-CHECK-REPORT) | **0 missing** — files exist in `/images/` and `colddirect-public-html/images/` |
| Wrong-brand `src` (Williams with Foster, True with Polar, etc.) | **0** in live HTML. True page uses `/images/true-fridge-repair-london.webp` (Foster stand-in, named True — replace photo later) |
| Heavy JPEGs `display-cabinets.jpg`, `pub-cellar.jpg`, `commercial-freezer.jpg`, `cold-room.jpg` | **0 remain**. Both trees deleted after WebP + grep 0 |
| Those four replacements | All **under 150KB** (44-62 KB) |
| Brand JPEG fallbacks `/images/brands/*.jpg` | Kept on purpose |

## The four replacements

| Asset | After |
|---|---|
| `display-cabinets.webp` | 61.9 KB |
| `pub-cellar.webp` | 40.7 KB |
| `commercial-freezer-repair-london.webp` | 18.0 KB |
| `cold-room.webp` | **43.9 KB** (from 2.41 MB JPEG) |

## Verify

- Grep html/php/css/js/inc/asp for the four `.jpg` names: **0** (except `blog-cold-room.jpg`, a different file used only as blog og:image).
- `OLD-IMAGES-BACKUP.txt` has SHA256 for all deleted JPEGs.

## Folder totals (both image trees)

| | Bytes | MB |
|---|---|---|
| Before first JPEG delete | 48,784,198 | 46.53 |
| After cold-room pass | 29,418,576 | 28.06 |
| Saved | 19,365,622 | **18.47** |

## Not in this campaign (still over 150KB)

Duplicate/catalog copies remain (homepage/, brands/ webp aliases, ice-cream, fridge kitchen shots, wine-cooler, polar-fridge source, badge, engineer original). They were not the 2.4MB JPEGs. Compress later if PSI still flags them.

Examples: `commercial-fridge-north-london.webp` 310 KB, `homepage-hero-chiller.webp` 275 KB, `wine-cooler.webp` 179 KB, public-html freezer-room copies 328 KB.

## Air conditioning page (2026-09-13)

Wrong kitchen hero (`/images/catering-repair.webp` CSS background) removed from `air-conditioning-repair-london.html` (root + `colddirect-public-html`).

| | |
|---|---|
| File | `/images/air-conditioning-repair-london.webp` |
| Size | 69,144 bytes (67.5 KB), under 100KB |
| Encode | `cwebp -q 75 -resize 800 0` (800×600) |
| Copy | `/colddirect-public-html/images/air-conditioning-repair-london.webp` |
| Source | `/mnt/data/commercial_vrf_rooftop_units.webp` was not on this PC; used a generated commercial rooftop VRF photo, then compressed |
| Markup | Hero `<img>` + second inline `<img>` after paragraph 2 |
| Grep in that HTML | 0 hits for `display-cabinets`, `pub-cellar`, `commercial-freezer` as image paths |
| Phones | Three numbers still present (`tel:+442039524822`, `tel:08001123427`, `tel:+447983759320`) |
| Copy | Commercial-only wording unchanged |

## Urgent fix 2026-09-13e (AC + supermarket)

| Page | Change |
|---|---|
| Air con | CSS kitchen/catering background already gone; **single** hero `<img src="/images/air-conditioning-repair-london.webp?v=20260913e">`. File is rooftop VRF (not kitchen). **65.6 KB**. No `display-cabinets` / `commercial-freezer` in that HTML. |
| Supermarket | Removed full-bleed `dairy-cabinet-repair.webp` CSS hero (that was the stretch/blur). Hero is now `<img>` `max-width:800px; height:auto; object-fit:cover`. File **61.6 KB**. Second image `/images/supermarket-island-freezer.webp` **70.3 KB** after paragraph 2. |
| Both trees | Same three WebPs in `/images/` and `colddirect-public-html/images/` |

## image-deploy-agent run (`scripts/deploy_images.py`) cache `20260913f`

- Agent: `.cursor/agents/image-deploy-agent.md`
- Script: `scripts/deploy_images.py` (cwebp q75 resize 800, PIL fallback, optional FTPS)
- This machine had **no Python on PATH** (Windows Store stub only). Encode + HTML patch ran with the same cwebp command the script wraps.

| Dest | Size | Trees |
|---|---|---|
| `air-conditioning-repair-london.webp` | **64.7 KB** | `/images/` + `colddirect-public-html/images/` |
| `supermarket-fridge-repair-london.webp` | **59.0 KB** | both |
| `supermarket-island-freezer.webp` | **67.7 KB** | both |

HTML: air-con + supermarket (root + public-html) now use `?v=20260913f`, `background-image:none`, hero `max-width:800px`. Grep `display-cabinets` / `pub-cellar` on air-con = **0**.

FTP: skipped (`PLESK_FTP_HOST` / `PLESK_FTP_USER` / `PLESK_FTP_PASS` not set). Set those, install Python 3, then `python scripts/deploy_images.py` to upload to `/httpdocs/images/` then `/httpdocs/`.
