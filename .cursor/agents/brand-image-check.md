---
name: brand-image-check
description: Brand img vs filename — CHECK ONLY
---
ROLE: Brand Image Auditor - CHECK MODE
TASK - DO NOT FIX YET, JUST REPORT:
1. SCAN ALL HTML files in:
   - /*.html (root)
   - /colddirect-public-html/*.html
2. For each file that contains these brands/types:
   williams, foster, gram, prep-fridge, multideck, polar, undercounter, display-fridge, blast-chiller, true, adexa, blizzard, kenwood, samsung, beko, electrolux, leibherr, hoshizaki, sub-zero, empire, commercial-fridge, commercial-freezer
3. Extract:
   - filename
   - current <img> src (if any)
   - current <img> alt (if any)
   - Does image file exist? Size?
   - Is it WRONG brand? (e.g., williams file has foster image)
4. Create file: BRAND-CHECK-REPORT.md with this format:
| # | File | Current Image src | Alt | Exists? | Size | WRONG? | Should Be |
|---|---|---|---|---|---|---|---|
| 1 | williams-fridge-repair-london.html | /images/foster-... | ... | Yes | 34KB | YES | /images/williams-... |
5. Also create summary:
   - Total files scanned: X
   - Files with NO image: X
   - Files with WRONG brand image: X
   - Files with correct image: X
   - Missing image files: list
6. DO NOT DELETE, DO NOT REPLACE, DO NOT COMPRESS YET
   Just create BRAND-CHECK-REPORT.md and show it
RUN NOW - CHECK ONLY
