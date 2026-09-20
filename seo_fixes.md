# SEO fixes 2026-09-20

GSC live API: UNAVAILABLE in this agent (no `gsc-key.json`, no `GSC_CREDENTIALS_JSON`, Windows path `C:\Users\khora\gsc-oauth.json` not present). Keyword choice used last GSC dump `seo-audit/daily-report-2026-09-19.md` (window 2026-09-12 to 2026-09-18) plus a live IIS robots crawl.

GSC URL Inspection Live Test: not run (no Search Console credentials). Robots/canonical changes are in repo + folder `index.html` for IIS. Recheck live after FTP deploy.

## Classification

| URL | Class | GSC / live reason |
|---|---|---|
| /cold-room-repair-london/ | WINNER | 29 clicks, pos 5.4, 58% CTR — title/H1 left alone |
| /fridge-repair-london/ | LEAK / OPPORTUNITY | 10 clicks, pos 13.9, 33% CTR; homepage now has exact-match anchor. H1 locked until 2026-09-28 so page body not rewritten |
| /commercial-fridge-repair-london/ | OPPORTUNITY (already expanded) | 14 clicks, pos 15.2, 35% CTR — not rewritten today |
| /supermarket-fridge-repair-london/ | NOINDEX TRAP | LIVE IIS returned `<meta name="robots" content="noindex, nofollow">` on 2026-09-20 |
| /air-conditioning-repair-london/ | NOINDEX TRAP (repo drift) | LIVE already `index, follow`; root `.html` + folder still said `noindex, nofollow` and would re-break on FTP |
| /commercial-dishwasher-repair-london/ | WEAK (166 words) | Not in GSC priority list; next service page after noindex trap |

## Before / after titles

| File | Before | After |
|---|---|---|
| supermarket-fridge-repair-london.html | Supermarket Fridge Repair London \| Cold Direct - North London Commercial Only 24/7 | Emergency Same Day Supermarket Fridge Repair \| ColdDirect |
| commercial-dishwasher-repair-london.html | Commercial Dishwasher Repair London \| Trade Kitchens \| Cold Direct | Emergency Same Day Dishwasher Repair London \| ColdDirect |
| air-conditioning-repair-london.html | (title unchanged) | robots only: noindex,nofollow → index, follow |
| index.html | (H1 unchanged) | added exact-match links: fridge repair london, supermarket fridge repair london, commercial dishwasher repair london |

## Robots

- MONEY /supermarket-fridge-repair-london/ and sibling `.html`: `index, follow` (was live noindex).
- MONEY /air-conditioning-repair-london/ `.html` + `/air-conditioning-repair-london/index.html`: `index, follow`.
- No X-Robots-Tag added to web.config.

## 404 / trailing slash

Live IIS 301 loop (slash → `.html` → slash) on:

- /about-us/
- /contact/
- /blog/commercial-fridge-repair-cost-london/

`web.config` now rewrites those paths (and any folder that has `index.html`) to the folder file with `stopProcessing="true"`. WordPress `index.php` catch-all was **not** added — live is static HTML on IIS, not WordPress. ASP extensionless rules kept.

## Internal links

See `scripts/internal_linking.js`. Homepage leak link uses trailing slash `/fridge-repair-london/` with exact-match anchor `fridge repair london`.
