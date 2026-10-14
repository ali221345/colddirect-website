# Priority keyword research and prepared changes — 14 October 2026

Status: prepared on `ai/priority-keyword-research-20261014`, based on main `313351a42168874922f0d9a081239a63939f12a4`. Not deployed. Top-three organic visibility is a goal, not a guaranteed outcome. Maps visibility is a separate measurement.

## Continuity and evidence

Reviewed project memory, lessons, SEO history, change log, current pages, open PRs and private-review progress. Existing freezer consolidation PR #51 remains the implementation path for that page; do not duplicate it. The private Sites preview remains unchanged. The earlier nightly note saying freezer images were not deployed is superseded by merged PR #56 and its successful deployment; that change is already complete.

Performance source: `seo-audit/daily-report-2026-10-14.md`, reporting 7–13 October. This is a stored report, not a fresh authenticated Search Console query. Its small samples do not establish a stable rank, trend or cause. Private analytics are not reproduced in this new public document. Before judging results, obtain matched 28-day UK Web query/page data, including device and the landing URL. Preserve existing homepage and legacy URL traffic while assessing page overlap.

Direct HTTP checks on all three slash URLs returned 200, one H1, a matching self-canonical and no HTML meta noindex. This does not prove Google indexing or a chosen Google canonical; HTTP X-Robots-Tag, Google URL Inspection and alias redirects were not audited in this pass. Search results included bare, slash and ASP variants; that is a reason to investigate, not proof of harmful competition between pages.

## Keyword ownership and hero copy

| Primary query | Existing target | Role |
|---|---|---|
| commercial fridge repair London | /commercial-fridge-repair-london/ | Highest business-intent priority: cabinet diagnosis, equipment, brands, quote process and emergency availability. |
| fridge repair London | /fridge-repair-london/ | Broad entry point, explicitly commercial-only; guide eligible customers to the detailed service. |
| freezer repair London | /freezer-repair-london/ | Commercial frozen-storage cabinets; retain separate commercial-freezer and freezer-room destinations. Continue PR #51. |

Keep the existing titles and H1s for this first pass: each already describes its primary query. Avoid changing all three repeatedly or adding new keyword-only pages.

**Commercial-fridge hero, prepared in source:** “Commercial fridge repair in London for restaurants, shops and catering kitchens. We repair upright fridges, prep counters, under-counter cabinets and display units. Call with your postcode, make and fault to check emergency availability.” Existing phone buttons are retained. The benefit list qualifies the two-to-four-hour aim by postcode and engineer availability and names established trade brands.

**Fridge hero, proposed only:** “Fridge repair in London for commercial kitchens, shops and hospitality businesses. Tell us your postcode, fridge make and current fault to check call-out availability. We repair commercial equipment only.” Retain the contextual link to the commercial-fridge page and existing phone buttons. Do not claim domestic coverage to chase broader searches.

**Freezer hero, proposed only after PR #51 review:** “Freezer repair in London for restaurants, pubs, shops and catering kitchens. We diagnose commercial cabinets that are warming, icing up or showing temperature alarms. Call with your postcode, make and fault to check emergency availability.” Retain the existing commercial-only notice and contact actions. These are editorial proposals, not added services or guarantees.

Supporting phrases belong naturally in the relevant equipment/fault sections: emergency commercial fridge repair, commercial fridge not cooling, upright fridge repair, prep counter repair, display fridge repair, commercial freezer not freezing, freezer temperature alarm. They are intent suggestions, not verified search-volume estimates. Preserve existing dedicated equipment pages and avoid repeating every phrase in every heading.

## Competitor research

Sources were retrieved on 14 October 2026; crawler freshness varies. This is a search sample, not a London-localised rank tracker or proof of current top-three positions. Competitor claims are their own, not independently verified facts.

| Source | Observed pattern | Practical ColdDirect application |
|---|---|---|
| [Commercial Fridge Repair / Be Cool](https://commercialfridgerepair.co.uk/) | Equipment categories, quote form, visit steps and visible credentials. | Explain what to send when calling and how diagnosis leads to a quote; use only verifiable credentials. |
| [Fix My Fridge](https://www.fixmyfridge.co.uk/) | Clear emergency phone action, equipment list and published call-out/guarantee terms. | Make existing contact actions easy to find. Publish prices or warranty terms only after owner confirmation. |
| [Bear commercial fridge service](https://bearbuildingservices.com/services/commercial-fridge-repair-london/) | Dedicated commercial repair landing page and business-focused service information. | Strengthen the existing commercial page rather than building another competing London page. |
| [Domex fridge repairs](https://www.domex-uk.co.uk/appliance-repairs/fridge-repairs/) and [AA freezer repairs](https://aaservice.co.uk/service-freezer) | Broad appliance repair results also appear for the generic queries. | Broad fridge/freezer searches have mixed intent; make commercial eligibility clear before the visitor calls. |

## Prepared implementation

Four maintained commercial-fridge HTML copies have the same bounded changes:

- Clearer equipment-led hero and qualified emergency availability.
- Removed the conflicting 60–90-minute statement in favour of the page's existing two-to-four-hour aim with availability qualification.
- Five existing links to cold-room area pages now accurately say “cold room repair”; destinations are unchanged.
- Replaced the editorial phrase “for the shorter search” with a customer-facing explanation and made one conditional household sentence explicitly commercial-only.
- Removed the hidden historical analytics comment from these upload payloads. No new analytics, secrets or customer information are added.

Titles, H1s, descriptions, canonicals, JSON-LD, images, phone numbers, all link destinations, booking scripts and routes are unchanged. Existing F-Gas statements elsewhere are not independently verified by this research; no new certification or warranty claim is introduced.

## Next work, ordered

1. Review and approve this bounded commercial-fridge patch, then verify deployment and served content. No main merge is authorised by this research request.
2. Review and continue PR #51 for freezer repetition. On the fridge page, remove visible internal design text (“Brand blue…”); do not duplicate prior intent/link fixes. Investigate the pre-existing protected-page mismatch before its release.
3. Inspect the three query-to-page splits and Google-selected canonicals before considering consolidation or redirects. Do not blindly remove the homepage, legacy ASP URLs or established pages.
4. Build evidence-based trust: real job examples with permission, real equipment photographs, confirmed qualifications and clear pricing terms. AI illustrations must not be represented as completed customer jobs.
5. Review the existing Google Business Profile for correct category, actual hours, services and genuine reviews. No profile edit, review solicitation or external message was sent in this pass.
6. Measure matched 28-day periods after recrawl: exact-query impressions, clicks, CTR and average position, plus qualified calls/enquiries where tracking exists. Report organic and Maps results separately. Do not attribute small weekly changes to a single edit or rewrite titles daily.

## Validation and limits

JSON-LD validation: 425 files, no parse errors or duplicate organisation nodes. Patch whitespace check passed. All four commercial-fridge copies remain identical. Focused preservation checks cover metadata, H1, schema, link destinations, images, scripts and protected-page requirements. No mobile visual QA, booking submission, Core Web Vitals measurement, new GSC authentication, Maps rank audit or ranking gain is claimed. No live site or private-preview update was made.

## Lessons and official guidance

Check open PRs before implementing keyword improvements; PR #51 already addresses freezer duplication. Broad appliance keywords do not justify advertising domestic repairs. Inconsistent response promises and misleading link labels can harm customer understanding even when keyword placement is already present.

Google recommends useful, original, accurate content rather than writing to an arbitrary word count or changing dates for apparent freshness: [people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content). Use descriptive titles without repetitive keyword stuffing: [title links](https://developers.google.com/search/docs/appearance/title-link). Investigate aliases with consistent signals: [canonical guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls). Local visibility also depends on relevance, distance and prominence: [Business Profile guidance](https://support.google.com/business/answer/7091?hl=en).

## خلاصه فارسی

سه عبارت درخواست‌شده اولویت هستند؛ عبارت commercial fridge repair London بیشترین تطابق را با خدمات تجاری سایت دارد. عنوان‌های اصلی از قبل کلمات هدف را دارند. اصلاح محدود متن بالای صفحه تجاری، هماهنگ‌کردن زمان پاسخ و دقیق‌کردن نام پنج لینک آماده شده است. کار فریزر در PR #51 ادامه دارد و تکرار نشده است. هیچ‌کدام از تغییرات این بررسی منتشر نشده‌اند. هدف سه رتبه اول است، اما نتیجه قابل تضمین نیست؛ ارزیابی باید با داده تاریخ‌دار و بازه‌های قابل‌مقایسه انجام شود.
