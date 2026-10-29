# Litourgia app as black-box answer key (issue #18, map #5)

Researched 2026-10-29. Public info only: store listings, developer site, privacy policy, reviews. App NOT downloaded, run, unpacked or intercepted. Short paraphrase only; no app content.

## Verdict

**Weak candidate as systematic answer key. Usable at most as manual human spot-check oracle; ask developers before anything more.**

Why:
- Arabic only. ANCA key is English. No English/French version (users ask for it, 2024-2026 reviews).
- No licence / terms of use found. Only a 3-sentence privacy policy.
- No public web version, API or docs. Mobile only (iOS/Android).
- Reviews + changelog indicate server-fed, online-dependent content, so batch/offline runs not guaranteed and date range unknown.
- Output granularity (slot labels, hymn identities) unverifiable without running it; cannot confirm from public info.
- Beirut Archdiocese (Arabic, Patriarchate of Antioch) tradition, not ANCA/UK English usage: expect systematic differences in text/hymn selection, not only "UK divergence".
- Active again: Play "Updated" Jul 31 2026; an Aug 2 2026 review thanks "whoever is updating the app". Content likely current for 2026; earlier years' coverage unknown.

## Developer and licence

- Seller on both stores: "Schools of the Greek Orthodox Archdiocese of Beirut" ([App Store](https://apps.apple.com/us/app/litourgia/id948623110), [Google Play `lb.org.quartos.litourgia`](https://play.google.com/store/apps/details?id=lb.org.quartos.litourgia)).
- Developer page: "developed by the Orthodox Archbishopric of Beirut for the benefit of the Church children" ([quartos.org.lb/Litourgia](https://quartos.org.lb/Litourgia)). Older page footer: Copyright 2015 ([Wayback 2026-02-19](http://web.archive.org/web/20260219092315/http://www.quartos.org.lb/iTypikon/litourgia.php)).
- Free, no IAP mentioned; App Store privacy label "no data collected"; Play data safety same.
- **Terms/licence: none found.** Both stores link privacy policy `http://www.quartos.org.lb/terms.html` ([Wayback 2025-12-24](http://web.archive.org/web/20251224185952/http://www.quartos.org.lb/terms.html)). Paraphrase: purpose is helping believers follow liturgical texts; texts come from Church liturgical books, "property of the Church", freely readable; no personal data, cookies or spyware. No licence for reuse, scraping or derived outputs. Live URL now 404s (site rebuilt as SPA), so the store-linked policy is dead; only the archive copy exists.
- Implication: no explicit permission to automate or redistribute output. Treat as all-rights-reserved by default; manual personal lookups fine, bulk capture not.

## Platforms, versions, availability

- iOS: v4.1 "Aug 2" (year not shown; 4.0 "May 20"); earlier dated releases 2015-2020 (v1.0.2 2015-01-15 ... 3.0.3 2020-09-04). Needs iOS 12.2+; listed "Designed for iPad", runs on Apple Silicon Mac and Vision Pro (not verified by Apple). 54.2 MB. Arabic ([App Store](https://apps.apple.com/us/app/litourgia/id948623110)).
- Android: Play 4.7 stars / ~276-290 reviews, 10K+ downloads, "Updated Jul 31 2026", PEGI 3, Books & Reference ([Play](https://play.google.com/store/apps/details?id=lb.org.quartos.litourgia&hl=en_GB)). Third-party mirrors list v2.14/2.15 (stale; not relied on).
- No web version, web app, API or docs found. Developer page links only the two stores ([quartos.org.lb/Litourgia](https://quartos.org.lb/Litourgia)).
- Emulator feasibility: Android emulator with Play Store (or iOS app on Apple Silicon Mac) would run a normal consumer install; fine for personal use but no automation hooks. In-app date selection: **not documented publicly; unverified**. Reverse-engineering/automation out of bounds (issue #18).
- Related public site feature: [quartos.org.lb/Calendar](https://quartos.org.lb/Calendar) offers a monthly Orthodox calendar archive for 2025-2026 (not opened/parsed; likely calendar/saints only, Arabic). Possible secondary check for fasts/saints, not hymns.

## What it claims to output

Per developer/store text: composes daily Vespers, Matins and Divine Liturgy "according to the Typikon of the Antiochian Orthodox Church", New Julian calendar; audience mode (clergy / chanters / ordinary faithful) pre-selectable in settings; daily saint/feast icon, daily readings, various prayers; search over weekly bulletin "Annashra" archive ([quartos.org.lb/Litourgia](https://quartos.org.lb/Litourgia)). Reviews mention a chanter view with hymns.

Not publicly documented: slot labels, hymn identities (title/incipit vs full text), reading citations vs full text, how Sat Vespers / Sunday Matins / Liturgy variables are sectioned, feast/Sunday coincidence handling. All need a human to open the app. Slot-by-slot comparability to ANCA "Liturgy Variables" unknown; expected partial at best (Arabic, different book editions, Byzantine terminology).

Version-history hints (App Store): 1.3.0 (2015-07-31) "enabled the 2016 liturgical year" -> suggests per-year data enabling at that time; 2.0.3 (2016-09-15) "Webservices interaction" -> server component. Current year range unknown.

## Reliability (reviews, paraphrased)

Google Play (4-5 stars only: 184x5, 92x4; none 1-3) and App Store LB/KW (21 ratings, 4.5):
- 2017-06 (Arabic): only "various prayers" and bulletin search readable; bulletin, daily readings, meditation and Mass/prayers would not load; asks if support stopped. => content was server-dependent and broke in the past.
- 2017-09: text sometimes unreadable, esp. hymn.
- 2019-12: asks for update/support.
- 2016-01 / 2016-05: requests to add Vespers, small Compline, other services => early coverage limited; now claims the three main services.
- 2019-09: wants doxa + eothinon doxastikon pairing in chanter view (variable-part slot incomplete at the time).
- 2024-07: asks for offline download => needs internet.
- 2024-09, 2024-12: crash on a mail/chanter icon (Galaxy A20); Android compat bugs.
- iOS 2022: some pages unreadable, reversed text direction; 2023: won't open after update.
- 2026-08-02: reviewer says app is "so good now" after updates.
- Net: **no review explicitly reports "missing hymns/readings" for current versions**; "missing content" signal is 2017 loading failures and 2022 unreadable pages. Coverage for arbitrary dates untested publicly.

## Contact route

- App support: litourgia@quartos.org.lb (Play listing, old developer page).
- Archdiocese: metbey@quartos.org.lb; phone +961 1 200 612 / 200 613 / 217 612 (Mon-Fri 8-16, Beirut); Facebook facebook.com/metbei ([Contact Us](https://quartos.org.lb/Contact-Us)).
- Suggested ask (Arabic/English): permission to compare outputs for a bounded set of dates for a non-commercial UK research tool; any export or date-range limits; which Typikon edition; licence statement. Do not claim endorsement.

## Feasibility summary for the harness

| Question | Finding |
|---|---|
| Arbitrary dates | Unknown; date picker undocumented; data range possibly server/year-gated |
| Offline | Probably no (reviews) |
| Automation | None offered; scraping/RE out of bounds, no licence |
| Language | Arabic only; ANCA key English -> needs mapping layer |
| Slot comparability | Unverified; likely partial |
| Tradition | Beirut Antiochian Arabic, not ANCA/UK |
| Use | Manual spot-check of a handful of dates (tone/eothinon/readings), after permission |

## Open items / uncertainty

- App Store 4.1/4.0 year inferred as 2026 from Play date + review (not stated).
- Calendar archive and Annashra not examined.
- No in-app behaviour verified first-hand (by design).

## Sources

- https://apps.apple.com/us/app/litourgia/id948623110 (also /ca/, /lb/ storefronts)
- https://play.google.com/store/apps/details?id=lb.org.quartos.litourgia (listing, reviews, support links)
- https://quartos.org.lb/Litourgia ; /Contact-Us ; /Calendar
- http://web.archive.org/web/20260219092315/http://www.quartos.org.lb/iTypikon/litourgia.php
- http://web.archive.org/web/20251224185952/http://www.quartos.org.lb/terms.html
