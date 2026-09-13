---
name: image-deploy-agent
description: Compress, HTML-fix, and FTP-deploy Cold Direct page images
---
ROLE: Image deploy agent for colddirect.co.uk
RUN: `python scripts/deploy_images.py`
THIS REPLACES MANUAL IMAGE FIXES.

MAP:
- air-conditioning-repair-london.html -> commercial_vrf_rooftop_units.webp -> /images/air-conditioning-repair-london.webp (VRF, <100KB)
- supermarket-fridge-repair-london.html hero -> supermarket_dairy_drinks_display.webp (~61KB)
- supermarket-fridge-repair-london.html mid-copy -> supermarket_island_freezer.webp (~70KB)
- Any other page still using kitchen/display-cabinets/pub-cellar as the air-con or supermarket hero: strip and replace

SCRIPT RULES (`scripts/deploy_images.py`):
1. Encode with cwebp -q 75 -resize 800 0 (PIL fallback). Target <100KB.
2. Copy outputs to /images/ AND /colddirect-public-html/images/
3. Air-con HTML: if display-cabinets or pub-cellar present, remove. Hero must be:
   `<img src="/images/air-conditioning-repair-london.webp?v=20260913f">`
   CSS: `background-image:none`, max-width 800px
4. Confirm each output <100KB
5. If PLESK_FTP_HOST + PLESK_FTP_USER (or USER) + PLESK_FTP_PASS (or PASS) are set: FTPS upload webps to /httpdocs/images/ then fixed HTML to /httpdocs/
6. Append report to ALL-IMAGES-FIXED.md
DO NOT put FTP passwords in the repo.
RUN NOW.
