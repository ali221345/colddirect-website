# ColdDirect SEO Keyword Map

**Date:** 2026-09-16  
**Model:** Repair / emergency callout (trade). Map keywords to **existing** pages first.

Status legend: `live` = page exists · `fix` = needs copy/meta · `new` = proposed · `blocked` = do not create yet

| Keyword cluster | Intent | Recommended page | Existing / new | Priority | Status |
|-----------------|--------|------------------|----------------|----------|--------|
| commercial fridge repair London | Transactional / local | commercial-fridge-repair-london.html | existing | P0 | live — keep improving |
| commercial freezer repair London | Transactional / local | commercial-freezer-repair-london.html | existing | P0 | live |
| commercial refrigeration repair North London | Local | index.html / commercial-fridge-repair-north-london.html | existing | P0 | live |
| emergency fridge repair London 24/7 | Transactional | emergency messaging on fridge + homepage | existing | P0 | live — strengthen above fold |
| cold room repair London | Transactional | cold-room-repair-london.html | existing | P0 | live |
| walk-in chiller / freezer repair | Transactional | walk-in-chiller-repair.html, walk-in-freezer-room-repair-london.html | existing | P1 | live |
| chiller repair London | Transactional | chiller-repair-london.html | existing | P1 | live (hero fixed) |
| air conditioning repair London commercial | Transactional | air-conditioning-repair-london.html | existing | **P0** | **was noindex — unblock** |
| supermarket fridge repair London | Transactional | supermarket-fridge-repair-london.html | existing | **P0** | **was noindex — unblock** |
| supermarket freezer repair London | Transactional | supermarket-freezer-repair-london.html | existing | P1 | live (image fixed) |
| Foster fridge repair London | Brand | foster-fridge-repair-london.html | existing | P1 | live |
| Williams fridge / freezer repair London | Brand | williams-*-london.html | existing | P1 | live |
| True / Gram / Polar / Adexa / Empire / Hoshizaki / Sub-Zero | Brand | matching *-london.html | existing | P1 | live / images WIP |
| Liebherr fridge repair London | Brand | liebherr-fridge-repair-london.html | **new → live** | P1 | **DONE** — page + nav + sitemap |
| ice cream machine repair London | Transactional | ice-cream-machine-repair-london.html | existing | P1 | live |
| ice machine / Hoshizaki repair | Transactional | ice-machine + hoshizaki pages | existing | P1 | live |
| wine cooler repair London | Transactional | wine-cooler-repair-london.html | existing | P1 | live |
| bottle cooler / display fridge repair | Transactional | bottle-cooler / display-fridge pages | existing | P1 | live — collapse non-London dups |
| blast chiller / blast freezer repair | Transactional | blast-*-london.html | existing | P2 | live |
| catering equipment repair London | Commercial | catering-repair-london.html | existing | P2 | live |
| commercial refrigeration servicing / PPM London | Commercial | — | new only if PPM sold | P2 | blocked until offer confirmed |
| commercial fridges for sale UK | Buy equipment | — | do **not** target | — | out of scope |
| multideck fridge buy / lease | Buy equipment | — | do **not** target | — | out of scope |
| why commercial freezer not freezing | Informational | blog posts | existing | P2 | live |
| commercial fridge vs domestic | Informational | guide | new | P2 | roadmap |
| F-Gas commercial fridge repair | Trust / commercial | about + service FAQs | fix | P1 | needs registration facts |

## Meta template rewrite (2026-09-16 P1)

Killed sitewide `"… in London from Cold Direct…"` title/description template.

**Pattern now:** `[Brand] Commercial [Type] Repair in London | Same-Day Callout - Cold Direct` (shortened to `| Cold Direct` when >70 chars).

| Scope | Count / status |
|-------|----------------|
| Pages rewritten | 61 money/service pages (+ 2 utility phrase cleanups) |
| Remaining template phrase | **0** |
| Example brand | `Foster Commercial Fridge Repair London \| Cold Direct` |
| Example service | `Commercial Fridge Repair London \| Same-Day Callout - Cold Direct` |
| Full list | `docs/_meta-schema-batch.json` → `changed_meta` |

## Schema unify (2026-09-16 P1)

| Before | After |
|--------|-------|
| LocalBusiness (~210) + HVACBusiness (2) | **ApplianceRepair only (212)** for org/provider nodes |
| Thin stubs (tel + London list) | Rich block: tel trio, priceRange ££, NAP, North London + 25 mile GeoCircle, openingHours 24/7 |
| Conflicting Store type | None |

Service + FAQPage nodes unchanged (not org types).

## Cannibalisation watchlist

| Pair | Action |
|------|--------|
| empire-fridge-repair.html ↔ empire-fridge-repair-london.html | **DONE** — IIS map 301 + canonical/noindex + removed from sitemap |
| bottle-cooler-repair.html ↔ bottle-cooler-repair-london.html | **DONE** — same |
| bottle-fridge-repair / commercial-bottle-cooler-repair | **DONE** → bottle-cooler-repair-london |
| display-fridge-repair.html ↔ display-fridge-repair-london.html | **DONE** — same |
| index.html ↔ / | Prefer `/` in sitemap |
| about.html ↔ about-us.html | Stub → about-us; drop stub from sitemap |

## People Also Ask / FAQ themes to cover on hubs

- How fast is emergency commercial fridge repair in London?
- Do you repair Foster / Williams / Polar?
- Is this domestic fridge repair? (**No — commercial only**)
- Are engineers F-Gas certified?
- What is the call-out / quote process?
- Do you cover Enfield / North London / 25 miles?

## 2026-10-09 — Generic fridge/freezer and services hub

| Keyword cluster | Search intent | Canonical target | Current action |
|---|---|---|---|
| fridge repair London | Commercial repair / local | `fridge-repair-london.html` | Keep this exact target; improve its unique search snippet and link from the services hub. Preserve the separate commercial-fridge page and homepage rather than repeating the phrase across every service page. |
| freezer repair London | Commercial repair / local | `freezer-repair-london.html` | Keep this exact target; improve its unique search snippet and link from the services hub. Preserve commercial-freezer and room pages for their narrower equipment intent. |
| commercial refrigeration services London | Service overview | `services.html` | Use a descriptive H1, concise summary and contextual links to existing repair pages. This URL was still “unknown to Google” in the 2026-10-09 bounded inspection although present in the 114-URL sitemap; monitor the next comparable inspection. |
| fridge service London / planned servicing / PPM | Commercial planned maintenance | No separate target confirmed | Keep blocked until the owner confirms ColdDirect sells planned visits or contracts. Do not add unsupported maintenance offers, prices or terms. |

The complete GSC keyword window currently available is 2026-09-07–2026-10-04, before recent service-page changes. Exact-query totals: fridge repair London 27 clicks / 187 impressions / avg position 14.37; freezer repair London 22 / 89 / 16.97. Most clicks were associated with the homepage or legacy combined URLs; do not claim a stable page-one ranking or attribute later results to recent changes. Reuse the saved complete report until its weekly refresh interval allows a new query.
