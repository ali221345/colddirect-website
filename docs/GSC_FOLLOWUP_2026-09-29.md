# GSC Follow-up Checklist — September 29, 2026

Run this on **September 29, 2026** (7 days after the fixes were deployed).

## How to run

```bash
cd C:\Users\khora\Documents\colddirect-website
python gsc_report.py
```

This pulls the last 28 days from GSC and writes `gsc_report.csv` and `gsc_followup.md`.

## Baseline (Sep 22, 2026)

These are the numbers **before** the fixes were deployed. Compare the new report against these:

### Homepage

| Metric | Baseline (Sep 22) | Target |
|---|---|---|
| Impressions | 5,426 | Should stay or grow |
| CTR | 4.1% | Target: 6%+ (new title "Commercial Fridge & Freezer Repair London") |
| Position | 32.5 | Should improve if CTR improves |
| Clicks | 222 | Target: 300+ |

### "fridge repair london" query

| Metric | Baseline (Sep 22) | Target |
|---|---|---|
| Impressions | 197 | Should stay or grow |
| Position | 19.5 | Target: under 15 (now that /fridge-repair-london/ is 301 not 404) |
| CTR | 13.7% | Should improve if dedicated page ranks |
| Clicks | 27 | Target: 40+ |

**Key check:** Are the impressions now landing on `/fridge-repair-london/` instead of the homepage? The GSC report's check2 section should show `/fridge-repair-london/` getting impressions, not just the homepage.

### "freezer repair london" query

| Metric | Baseline (Sep 22) | Target |
|---|---|---|
| Impressions | 95 | Should stay or grow |
| Position | 27 | Target: under 20 |
| Clicks | 15 | Target: 20+ |

**Key check:** Google chose a different canonical for `/freezer-repair-london/` (without slash). The 301 redirect should fix this on recrawl. Check if Google has picked up the correct canonical.

### "ice cream machine repair" query

| Metric | Baseline (Sep 22) | Target |
|---|---|---|
| Impressions | 67 | Should stay or grow |
| Position | 9.0 | Target: under 7 |
| CTR | 11.9% | Should improve |
| Clicks | 8 | Target: 15+ |

**Key check:** The old URL `/ice-cream-maker-repairs-london` was 404ing with 710 impressions. It now 301s to `/ice-cream-machine-repair-london/`. Check if Google has indexed the new URL.

### "commercial fridge repair london" query

| Metric | Baseline (Sep 22) | Target |
|---|---|---|
| CTR | 24.0% | Already improving (was 21.4%) |
| Position | 11.4 | Target: under 10 |
| Clicks | 37 | Target: 50+ |

### Blog: "different-types-of-ice" page

| Metric | Baseline (Sep 22) | Target |
|---|---|---|
| Impressions | 7,237 | Should stay (this is your highest-impression page) |
| CTR | 0.19% | Target: 2%+ (new title "Which Ice Machine Makes the Right Ice?") |
| Clicks | 14 | Target: 100+ (even 2% CTR = 144 clicks) |
| Position | 5.7 | Already good — position is not the problem, title CTR is |

### "cold room repair london" query (the winner — don't break it)

| Metric | Baseline (Sep 22) | Target |
|---|---|---|
| Position | 2.92 | Should stay 2-3 |
| CTR | 59.5% | Should stay above 55% |
| Clicks | 100 | Should stay or grow |

**Do NOT** change anything on the `/cold-room-repairs-london` page. It is your best performer.

### "commercial freezer repair london" query

| Metric | Baseline (Sep 22) | Target |
|---|---|---|
| Position | 4.8 | Should stay under 6 |
| CTR | 77% | Should stay above 60% |
| Clicks | 10 | Should stay or grow |

### New blog articles (should be indexed by Sep 29)

| URL | Baseline | Target |
|---|---|---|
| `/blog/prevent-commercial-fridge-breakdown/` | Unknown to Google | Should be "Submitted and indexed" |
| `/blog/commercial-freezer-temperature-guide/` | Unknown to Google | Should be "Submitted and indexed" |

Check by running:
```bash
python tools/request_indexing.py
```
And looking for "inspect Submitted and indexed" in the output.

## What to do with the results

1. **If CTR improved** but position didn't: give it another 2 weeks. CTR drives position — Google tests the new title in SERP and if more people click, it ranks higher.

2. **If impressions dropped** on the blog/different-types-of-ice page: the new title might have changed the query match. Check if the page is still ranking for "types of ice" or "ice machine" queries.

3. **If position improved on "fridge repair london"**: the 301 redirect worked. If not, check Google's URL Inspection for `/fridge-repair-london/` — it may still show the old canonical.

4. **If the ice-cream page impressions dropped**: this is expected. The old URL `/ice-cream-maker-repairs-london` (710 impr) is now a 301. Those impressions should transfer to `/ice-cream-machine-repair-london/` once Google recrawls.

5. **If nothing changed**: Google may not have recrawled yet. Run `python tools/request_indexing.py` again to resubmit the sitemap. Check the Indexing API is enabled at https://console.developers.google.com/apis/api/indexing.googleapis.com/overview?project=237190212015

## After the GSC report

Update `gsc_followup.md` and `gsc_report.csv` in git:
```bash
git add gsc_followup.md gsc_report.csv
git commit -m "GSC follow-up Sep 29 — compare against Sep 22 baseline"
git push origin main
```
