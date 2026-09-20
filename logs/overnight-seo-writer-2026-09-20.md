# Overnight SEO Writer log

**Night:** 19–20 Sep 2026 (London)  
**Ran:** ~2:08 AM London (commit `e199ac8` at 2026-09-20 01:08:57 UTC)  
**Repo:** ali221345/colddirect-website  
**Branch:** `cursor/colddirect-seo-strategy-1d50`  
**Status:** Ran successfully. **Not on `main`.** No matching open pull request found. **Not FTP-deployed.**

Sources: commit `e199ac8`, `logs/overnight-seo-404.log` (crawl 2026-09-20T01:03:10Z), `FIXED-LOG.md` and `seo_fixes.md` from that commit.

| Metric | Value |
|---|---|
| Service pages written | 2 |
| Sitemap URLs crawled | 109 |
| Sitemap 301 loops | 3 |
| Live noindex traps | 1 |

---

## Pages written (2-page cap)

| When (London) | Page | Before → after | Class |
|---|---|---|---|
| ~2:09 AM | supermarket-fridge-repair-london.html | 708 words, `noindex,nofollow` → 1250 words, `index,follow` | GSC noindex trap |
| ~2:09 AM | commercial-dishwasher-repair-london.html | 166 words, no seo-article → 818 words + FAQ/Service schema | Weak service page |

Folder `index.html` copies were kept in sync. Header, hero, CTA and footer otherwise unchanged.

Commit message: `SEO: Add supermarket fridge repair London - GSC noindex-trap - tags: supermarket fridge, dishwasher - borough London`

---

## Classification used

| URL | Class | Action |
|---|---|---|
| /cold-room-repair-london/ | Winner | Left title/H1 alone (29 clicks, pos 5.4) |
| /fridge-repair-london/ | Leak | Homepage exact-match link only; H1 locked until 28 Sep |
| /commercial-fridge-repair-london/ | Opportunity | Already expanded — not rewritten |
| /supermarket-fridge-repair-london/ | Noindex trap | Live IIS had `noindex,nofollow` — unblocked in repo |
| /air-conditioning-repair-london/ | Repo drift | Live already index; root + folder were still noindex |
| /commercial-dishwasher-repair-london/ | Weak | Second page of the night (166 words) |

GSC live API was unavailable in the agent (no `gsc-key.json` / `GSC_CREDENTIALS_JSON`). Keyword choice used `seo-audit/daily-report-2026-09-19.md` (window 12–18 Sep 2026).

---

## Live sitemap crawl

109 URLs from https://www.colddirect.co.uk/sitemap.xml. Failures are IIS 301 loops (slash ↔ `.html`), not missing pages.

| URL | Desktop | Mobile | Issue |
|---|---|---|---|
| /blog/commercial-fridge-repair-cost-london/ | 301 | 301 | Slash → `.html` → slash (then homepage) |
| /contact/ | 301 | 301 | Slash → `.html` → slash |
| /about-us/ | 301 | 301 | Slash → `.html` → slash |

Loop detail (HEAD, no follow):

- `/about-us/` → 301 `/about-us.html` ; `/about-us.html` → 301 `/about-us/`
- `/contact/` → 301 `/contact.html` ; `/contact.html` → 301 `/contact/`
- `/blog/commercial-fridge-repair-cost-london/` → 301 `.html` ; `.html` → 301 `/`

Live site is Microsoft-IIS / PleskWin, not WordPress + nginx.

---

## Repo fixes (pending FTP)

- `web.config` now serves folder `index.html` first and rewrites about-us, contact, and the blog-cost path (slash and `.html`) with `stopProcessing="true"` to break the IIS loop. WordPress/nginx rules were skipped.
- Money-page robots: supermarket fridge set to `index, follow`.
- Air-conditioning root HTML + folder synced to `index, follow` so a future FTP cannot re-noindex a live page.
- Homepage gained exact-match anchors: `fridge repair london` → `/fridge-repair-london/`, plus supermarket fridge and commercial dishwasher.

---

## Queue after this night

Next weak service pages recorded in the commit notes:

1. `multideck-fridge-repair-london.html`
2. `undercounter-fridge-repair-london.html`

## Other jobs (not this writer)

GitHub seo-bot `daily seo 2026-09-20` ran at 05:09 UTC (6:09 AM London) on `main` (`15cd0f2`). That is a sitemap/report job, not the Overnight SEO Writer.

Writer work remains only on `cursor/colddirect-seo-strategy-1d50` until merged and FTP-deployed.
