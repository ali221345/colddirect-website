# FIXED-LOG.md

| Date | File | Before -> After |
|---|---|---|
| 2026-09-13 | commercial-fridge-repair-north-london.html | 766 words, hasSeo=false -> 1250 words, seo-article added (~484w unique block, keyword x3) |
| 2026-09-13 | commercial-fridge-repair-london.html | 1269 words, hasSeo=false -> 1752 words, seo-article added (~483w unique block, keyword x3) |
| 2026-09-16 | commercial-chest-freezer-repair-london.html | 467 words, hasSeo=false -> 987 words, seo-article added (~520w unique block, keyword x3) |
| 2026-09-16 | blast-freezer-repair-london.html | 506 words, hasSeo=false -> 1006 words, seo-article added (~500w unique block, keyword x3) |
| 2026-09-17 | supermarket-freezer-repair-london.html | 579 words, hasSeo=false -> 1105 words, seo-article added (~519w unique block, keyword x3) |
| 2026-09-17 | williams-freezer-repair-london.html | 688 words, hasSeo=false -> 1214 words, seo-article added (~520w unique block, keyword x3) |
| 2026-09-18 | subzero-freezer-repair-london.html | 689 words, hasSeo=false -> 1212 words, seo-article added (~512w unique block, keyword x3) |
| 2026-09-18 | commercial-freezer-repair-north-london.html | 890 words, hasSeo=false -> 1416 words, seo-article added (~518w unique block, keyword x3) |
| 2026-09-19 | commercial-freezer-repair-london.html | 1275 words, hasSeo=false -> 1863 words, seo-article added (~513w unique block, keyword x4) |
| 2026-09-19 | freezer-room-repair-north-london.html | 697 words, hasSeo=false -> 1237 words, seo-article added (~521w unique block, keyword x4) |
| 2026-09-20 | supermarket-fridge-repair-london.html | 708 words, noindex,nofollow -> 1250 words, robots index,follow, seo-article added (GSC noindex-trap) |
| 2026-09-20 | commercial-dishwasher-repair-london.html | 166 words, hasSeo=false -> 818 words, seo-article + FAQ/Service schema (weak service page) |

Notes: 2026-09-20 max 2 service pages. Folder index.html copies kept in sync. Live noindex on /supermarket-fridge-repair-london/ fixed to index, follow. Repo air-conditioning-repair-london robots synced to index, follow (live already index; root files were still noindex). web.config now serves folder index.html first and rewrites about-us / contact / blog-cost slash+.html to the folder to stop IIS 301 loops. Homepage exact-match leak link: fridge repair london -> /fridge-repair-london/. Next weak service pages: multideck-fridge-repair-london.html, then undercounter-fridge-repair-london.html.
