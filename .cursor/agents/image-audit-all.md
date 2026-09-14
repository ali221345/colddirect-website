---
name: image-audit-all
description: Deep Image Auditor — brand img vs filename
---
ROLE: Deep Image Auditor
TASK:
1. Scan BOTH locations:
   - /*.html in root
   - /colddirect-public-html/*.html
2. For each file containing brand name (williams, foster, true, gram, polar, blizzard, etc):
   - Check <img> alt and src
   - If filename = williams-fridge... but image = foster or alt = foster => LOG as WRONG
3. Create WRONG-IMAGES-REPORT.md with table:
   | File | Current Image | Should Be | Location |
4. Fix them:
   - Replace with correct brand: /images/[brand]-fridge-repair-london.webp
   - Alt must match keyword exactly
   - Style: max-width:600px centered, lazy, 800x600, webp, <150KB
   - If correct image file doesn't exist, add to MISSING-IMAGES.txt
5. Update daily-job.php so it doesn't restore wrong images again - make it check brand match first
RUN NOW - show WRONG-IMAGES-REPORT.md
