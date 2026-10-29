# GOA Digital Chant Stand (DCS) as secondary answer key: access and format

Issue: cmbryan/yocal#10. Parent map: #5. Probed 2026-10-29 (site "today" = 2026-10-29).
Public repo: nothing downloaded is committed. Only URL patterns, key names, structure, counts and short citations (reading refs, hymn-identity keys). No service text quoted.

## TL;DR

- **Usable, high machine-parseability.** Plain static HTML over HTTPS, no auth, no JS needed, no frames needed (curl works). Frames/JS only for the music-score viewer. No JSON/API for service content.
- **Every text span carries a stable semantic key**: `<span class='kvp' data-key='<topic>_en_US_<provider>|<field>'>text</span>`. Document order = service order. Keys identify the Variable part and its source book/date (e.g. Octoechos mode+day, Menaion date, Eothinon n). This is much better than PDF scraping and gives an "inferred rule" trace (which date/mode a slot was drawn from).
- **Coverage: calendar year 2026 only** (Jan 1 - Dec 31 2026). 2025 and 2027 return 404; no Wayback snapshots found.
- **Gaps**: Triodion pre-Lent pages are empty shells (Jan 31 - Feb 22 2026: Sat Vespers, Sun Matins/Liturgy for Publican, Prodigal, Meatfare, Forgiveness). Vespers URL date = evening served, content = *next* liturgical day. No Dec 31 / Jan 1 eve Vespers across the year boundary. Sunday Liturgy page can omit the Sunday Epistle (use the "Readings for the Day" page).
- **Terms**: "for the purposes of worship only"; parish copying OK; no reproduction/sale/retrieval-system storage without GOA written permission; contributor copyrights (RSV, SAAS, NKJV, translators). Cite/compare for private checks; do not commit pages. No robots.txt (404). No API terms published.
- **Differences vs Antiochian**: GOA/Dedes translations and GOA parish-abridged structure (see Differences). Not verified against ANCA here (that is #-sibling ticket); items marked "check".

## 1. URL patterns

Host: `https://digitalchantstand.goarch.org/goa/dcs/` (alias host `https://dcs.goarch.org/goa/dcs/` serves same paths). Both HTTP/2, Apache, `cache-control: max-age=3600`, `last-modified` = site build time (pages for Oct-Nov 2026 built 2026-10-04; Mar pages 2026-03-08).

| Purpose | Pattern |
|---|---|
| Year index | `servicesindex.html` (lists 365 days of 2026, links to day indexes) |
| Day index | `indexes/YYYYMMDD.html` (lists every service for that date, per language, "Print"/"View") |
| Service, HTML | `h/s/YYYY/MM/DD/<code>/<lang>/index.html` |
| Service, print wrapper | `p/s/YYYY/MM/DD/<code>/<lang>/index.html` (JS redirect to `se.mMM.dDD.<code>.pdf`; PDF not fetched) |
| Label overrides | `indexmodifier.json` (date -> alt-commemoration index labels, 2021-2026; only content JSON on site, index labels only) |
| Scores (music, not text) | `https://digitalchantstand.goarch.org/media/m/<composer>/en/<book>/...pdf` (host root, NOT under `/goa/dcs/`); linked in HTML as `js/viewer/web/viewer.html?file=/media/m/...`. HEAD 200. Audio: `/media/a/...mp3`. Irrelevant for rules. |

`<lang>` = `en`, `gr`, `gr-en`. Use `en`.

**Service codes** (from all 365 day indexes; counts = days offered, 2026):

| code | label | days | note |
|---|---|---|---|
| `ve` | Vespers | 343 | all Sat+Sun have it (see "Vespers date shift") |
| `ma` | Matins (Orthros) | 359 | all Sat+Sun have it |
| `li` | Divine Liturgy | 327 | all Sun, Sat; weekdays only when served |
| `li2` | Liturgy Variables / Antiphons | 327 | subset of `li` content |
| `li3` | Liturgy Variables / Typika and Beatitudes | 302 | `li` page itself does not carry Typika/Beatitudes |
| `h91` | Readings for the Day | 364 | **both** Sunday-cycle and Menaion readings + Synaxarion; best readings source |
| `mo` | Midnight Office | 129 | |
| `ma2` / `ma3` | Matins Customizable / Unabridged | 92 / 81 | Sundays: `ma2` on 51 of 52 |
| `ve2` | Vespers Unabridged | 37 | |
| `ve4/5/6/9`, `ma4/5/6/9`, `li4/5/6/7`, `mo5` | additional/alternative commemoration/variables, hierarchical | 1-13 each | alternative saint when two commemorations compete; labels via `indexmodifier.json` |
| `vl`, `vl2` | Vesperal Liturgy (+Full) | 4 / 2 | Nativity/Theophany eves, Great Sat |
| `co7` | Vigil: Great Compline, Lity, End of Vespers | 1 (Dec 24) | only place a Litia appeared |
| `h1 h36 h9 co pl1 pl2 pl3 em em3 co1 co6 h13 gh h61 h92 ma1 ma8` | hours, Compline, Presanctified, Holy Week, Paschal, etc. | | out of scope |

Probe results: 2026-10-30 `li` 200 (259 KB); 2026-11-01 `li` 200 (276 KB); `or` code **404** (Orthros is `ma` in DCS); `vs` code **404** (Vespers is `ve`). Directory/month URLs (`h/s/2026/10/index.html`) 404; only `indexes/` and `servicesindex.html` enumerate.

Probed pages for the requested dates (all `en`, 200):
- Sat 2026-10-31 `ve` 163 KB, `ma` 149 KB, `li` 260 KB, `li2`, `li3`, `h91`.
- Sun 2026-11-01 `ma` 236 KB, `li` 276 KB, `li2` 75 KB, `li3` 69 KB, `h91` 19 KB, `ve` 142 KB, `ve9` (Hierarchical) 118 KB, `ma2`.

### Vespers date shift (important for harness)

`ve` on date D = Vespers **served the evening of D**, content keyed to **D+1** (`<title>` = `se.mMM.d(D+1).ve`; text "on Saturday, October 31, for November 1"). Examples: `2026/10/31/ve` = Great Vespers for Sunday Nov 1 (Octoechos mode 5 day 1 + Menaion Nov 1); `2026/11/01/ve` = Vespers for Nov 2. So "Saturday Great Vespers" = URL date Saturday. Feast eves follow the same rule (`2026/09/07/ve` = Nativity of Theotokos, `2026/09/13/ve` = Elevation). Year boundary: 2026-12-31 has **no** `ve` and 2025-12-31 does not exist, so Vespers for Jan 1 (Circumcision/Basil) is unavailable for 2026; Jan 1 2026's `ve` is for Jan 2. Dec 24 has `vl`/`co7` instead of `ve` (Vesperal Liturgy of Nativity eve).

## 2. Date coverage

- `servicesindex.html`: 2026-01-01 .. 2026-12-31 (365 days, all fetched OK).
- 2025 (e.g. 20250101, 20251231) and 2027 (20270101, 20270301, 20271231), 2024, 2028 day indexes: 404. Content pages for 2024/2025/2027 sample dates: 404. Wayback availability API: no snapshots for sampled 2024/2025 pages.
- `indexmodifier.json` has entries 2021-2026, so earlier years once existed; they are no longer online. Implication: DCS answer key only usable for **2026**, unless a later year is published (site seems to publish one calendar year at a time; when 2027 appears is unknown). Re-check periodically.
- Weekday availability (2026, of 52 each): Sat `ve` 51, `ma` 51, `li` 51; Sun `ve` 52, `ma` 52, `li` 52, `mo` 51, `ma2` 51.
- Missing `li` (38 days) = Lent weekdays + Holy Week etc. (not in scope). Missing `ma` 2026-04-06..11 (Holy Week).
- **Empty shells** (HTTP 200, 4308 bytes, table with one empty `<td>`, **no data-keys**): 2026-01-31 `ve`; 02-01 `ma`,`li`; 02-07 `ve`; 02-08 `ma`,`li`; 02-14 `ve`; 02-15 `ma`,`li`; 02-21 `ve`; 02-22 `ma`,`li`. = Triodion Sundays Publican (Feb 1), Prodigal (Feb 8), Meatfare (Feb 15), Cheesefare/Forgiveness (Feb 22) and their Sat Vespers. Checked all 155 Sat `ve` + Sun `ma`/`li` in 2026 by HEAD content-length (only these 12 are tiny); Soul Saturday Feb 14 `li`/`ma` and Lent Sundays from Mar 1 are full (e.g. Mar 1 `li` 266 KB). Cause unknown (pages stamped 2026-03-08). Weekday/other service codes were not size-checked, so shells may exist elsewhere. **Always size/key-check before comparing.**

## 3. Page structure

`<base href='../../../../../../../'/>` so relative links resolve to `/goa/dcs/`. Content = `<table id='biTable'>`; each row `<td class='rightCell'><p class='<style>'>...`.

- `<title data-timestamp=... data-commemoration='' data-language='EN'>` = `se.m<MM>.d<DD>.<code>` (service id, **liturgical day**; for `ve` this is D+1). Build timestamp is in `data-timestamp`.
- Text spans: `<span class='kvp' data-key='K'>text</span>`; placeholders `kvp dummy` (empty, ignore); `<span class='key' data-key=... hidden>` = version designation marker; visible source tag `<span class="versiondesignation">[SAAS]` / `[RSV]` / `[GOASD]` after verse/reading text.
- Speaker/role classes: `actor`, `dialog`, `adepr/ddepr` (deacon/priest), `aprhi/dprhi`, `rubric`, `mode`, `designation` (section title), `hymn`, `verse`, `reading`, `chapverse`.
- Key grammar: `<topic>_<lang>_<country>_<provider>|<field>`; provider = text source/translation (`goa`, `dedes` = Fr Seraphim Dedes, `goadedes`, `saas` = St Athanasius Academy Septuagint psalter, `rsv`, `cog`).
- Fixed text (prayers, litanies, `euLI.*` Liturgy of Chrysostom ordinary, `actors`, `rubrical`, `prayers`, `template`, `hi.hi01` Vespers ordinary, `ho.hoNN` hymn-book) vs **variable** topics (below). Page includes layout-only keys to skip.
- Layout is the **service order**, including rubric lines (`ru.*`), so slot order is directly extractable by walking keys in document order and filtering to variable topics.

### Variable-part key vocabulary (observed)

| Topic prefix | Meaning | Example (from probed pages) |
|---|---|---|
| `da.dN` | weekday (1 = Sunday) | `da.d1` |
| `oc.mM.dN` | Octoechos, mode M, day N | `oc.m5.d1` (Sat Vespers Nov 1: 6 resurrectional stichera, aposticha); `oc.m6.d1`, `oc.m8.d1` = theotokia from other modes |
| `me.mMM.dDD` | Menaion of month/day (can differ from the service date) | `me.m11.d01` saint; `me.m07.d01` = Jul 1 Cosmas & Damian texts reused for Nov 1; Nov 22 Sunday Liturgy uses `me.m11.d21` (Entrance afterfeast), Nov 22 saint only in `li6` |
| `eo.eNN` | Eothinon hymns (exapostilarion, doxasticon) | `eo.e11` |
| `le.go.eo.wNN` | Matins Eothinon Gospel | `le.go.eo.w11` (Jn 21:14-25) |
| `le.ep.mc.dNNN` / `le.go.mc.dNNN` | movable-cycle Epistle/Gospel by day index | index = days with **Pascha = d071**: Nov 1 = d274 (Gal 6:11-18, "Twenty-Second Sunday"); Palm Sun d064; Pentecost d120 |
| `le.go.lu.dNNN` | Luke-cycle Gospel by day | Nov 1 = d035 (Lk 16:19-31, "Fifth Sunday of Luke") |
| `le.ep.me.mMM.dDD`, `le.go.ge.<type>` | Menaion Epistle / generic saint-type Gospel (`unmercenary`, `apostle`) | Nov 1 saint: 1 Cor 12:27-13:8 + Mt 10:1,5-8 |
| `tr.dNNN`, `pe.dNNN` | Triodion / Pentecostarion day-indexed | `tr.d063/d064` on Palm Sunday; `pe.d120` Pentecost |
| `he.a.mM`, `he.h.mM`, `he.ga`, `he.k` | hymn library by *incipit id* + mode: apolytikia/automela (`he.a`), heirmoi/katavasia (`he.h`), general apolytikia (`he.ga`) | `heAU.TonSynanarchonLogon` = Tone 5 resurrectional apolytikion; `heAU.OlinApothemenoi` = Menaion sticheron melody |
| `liturgical.verses`, `menaion.verses`, `movable.verses` | psalm verses/prokeimena by cycle | `psLI.sunday.antiphon1.v1`, `psLI.m11.d01.prokeimenon.*`, `psVE.prokeimenon.saturday.*`, `psVE.stichologia.vNN`, `psVE.saturday.aposverse.vN` |
| `sy.mMM.dDD` | Synaxarion | in `ma` and `h91` |
| `ho.hoNN` | fixed hymnbook (Great Doxology, Evlogetaria, Trisagion hymns, Phos Hilaron `ho.ho10`) | `hoMA.ResEvlog1..6`, `hoMA.SunTroparion1` |

Hymn identity is by incipit key (`heAU.TonSynanarchonLogon`), with mode in the topic; good join key for the hymn-identity catalog work.

### Example slot orders (Variable parts only; from keys, no text)

- **Sat Great Vespers 2026-10-31** (for Sun Nov 1, saint = Unmercenaries, Tone 5): Intro Ps 103 -> Lord I Have Cried (6 Octoechos `oc.m5.d1` resurrectional + 4 Menaion incl. Glory from `me.m11.d01`/`me.m07.d01`; Both-now Theotokion `oc.m5.d1`) -> Phos Hilaron -> Prokeimenon Saturday (`psVE.prokeimenon.saturday`) -> Aposticha (4 Octoechos `oc.m5.d1`, Glory Menaion `me.m07.d01`, Both-now `oc.m6.d1`) -> Nunc Dimittis -> Apolytikion (Res Tone 5 `he.a.m5`, Glory saint `me.m11.d01`, Both-now `oc.m8.d1`). No Litia, no Artoklasia, no Kathisma/Psalm 1 text, no OT readings on this date (feast eve `2026/09/07/ve` does carry a Readings section).
- **Sun Matins 2026-11-01**: Res Apolytikion + saint's + Theotokion; Kathisma I and II (3 each, `oc.m5.d1`); Evlogetaria `hoMA.ResEvlog*`; Hypakoe; Anavathmoi (Octoechos antiphons 1-3); Eothinon 11 Gospel; post-Gospel idiomela; Magnificat (`he.h.m6` Tin Timioteran); Ode 9 katavasia; Exaposteilarion (Eothinon 11 + Menaion `me.m07.d01` + Theotokion); Lauds (4 Res `oc.m5.d1` + 2 Menaion `me.m11.d01` + 2 borrowed `me.m07.d01` Lity stichera; Glory `eo.e11`; Both-now `oc.m2.d1`); Great Doxology; Res troparion. **No Canon text**: only katavasias (`he.h.m4`) and the menaion canon's ode 6 hymns appear in `li3`. Oikos/Kontakion Resurrectional present (`oc.m5.d1`). Psalm 50/Polyeleos not variable.
- **Sun Divine Liturgy 2026-11-01** (`li` + `li2` + `li3`): Sunday antiphons (`psLI.sunday.antiphon1..3`) -> Entrance -> Res Apolytikion `he.a.m5`, saints' `me.m11.d01`, Kontakion (here fixed Theotokos "Protection of Christians" `hoTY.Key0408`; no resurrectional kontakion) -> Prokeimenon/Epistle/Gospel -> Communion hymn Sunday Ps 148 -> Dismissal inserts `meDA.insert1/2` (saint names). Typika/Beatitudes in `li3` (Octoechos `ocLI.Beatitudes1..3` + Theotokion, + Menaion Ode 6 canon for saints).
- **Weekday example 2026-10-30 `li`** (Friday): weekday antiphons; Menaion apolytikion; Epistle `le.ep.mc.d272`; Luke `le.go.lu.d040`; seasonal Kontakion keyed `me/m09/d14` (Cross).

## 4. Machine-parseability assessment

- **Good**: HTML is deterministic and server-generated (ALWB software, EPL-2.0). Keys are stable across pages. Parse with a few lines of Python (`re` or an HTML parser on `span.kvp[data-key]`); in-order key walk yields slot sequence. Day indexes give the service list and let `ve`/`ma`/`li` be addressed per date.
- **Quirks**:
  - Empty shells with HTTP 200 (check for zero `data-key` or size < ~10 KB). 404 for non-existent codes, with an Apache error HTML body.
  - Text spans often appear twice (a blank key span then the text span) and `dummy` spans carry nothing.
  - Non-English leakage: keys like `me.m11.d01_gr_GR_cog|meVE.MM.Stichera1123as78910` are hidden/dummy placeholders in English.
  - Choice points ("or" alternatives, e.g. weekday Antiphon 2 `ru.Or` variants) are inline, tagged by rubric key `ru.Or`; user-preference toggles exist in `ma2` (`website.preferences.titles`, `mc.*`).
  - Parish-localised keys (`client_en_US_goa|cl.*`, bishop/patron) are placeholders, not rules.
  - Commemoration title key `meDA.commemoration.first_short` is absent/blank on some pages (e.g. Nov 22 `li`) because the commemoration is from the previous date (`me.m11.d21`); `alt1.meDA...` appears on `li6`.
  - Text includes translator-source tags (GOASD, SAAS, RSV); the hymn texts are Fr Seraphim Dedes translations. Verse/psalm text is SAAS Septuagint; readings RSV.
- **Readings**: the `li` page may show only one set. Examples: 2026-11-01 `li` shows saint's Epistle + prokeimenon and Sunday Gospel only (Sunday Epistle Gal 6:11-18, `le.ep.mc.d274`, absent from `li`, present in `h91`); 2026-10-18 `li` (Ap. Luke on Sunday) shows saint's Epistle and Gospel only (Sunday Epistle Gal 1:11-19 only in `h91`); 2026-10-25 plain Sunday shows Sunday readings; 2026-11-08 (Archangels on Sunday) shows saint's Epistle + Sunday Gospel (`le.go.lu.d049`). So **use `h91` for the full reading set**, and treat `li` as "what GOA reads", not "what the day prescribes". This itself is a rule signal (GOA's epistle/gospel precedence when Sunday meets a saint) but inconsistent across cases; check against Antiochian rule.
- **Not machine-readable**: no JSON/XML/API for service content (only `indexmodifier.json` labels). Print PDFs exist but are redundant.

## 5. Terms of use

From `about.html` (paraphrased): translation, rubrics, Greek and English texts are for purposes of worship only, subject to change without notice at GOA's discretion, all rights reserved. Materials remain property of contributing translators. Parishes may copy as needed for worship; may not be reprinted, reproduced, transmitted, stored in a retrieval system or translated for sale without GOA written permission. Third-party copyrights: RSV (NCC), SAAS Septuagint (St Athanasius Academy), NKJV, audio by Pres. Stacey Dorrance by permission, many named contributors (Dedes, Cook, Houpos, Duvall, Ware, Roumas, Barrett, Boyer, Carroll, Andronache, HC, MLGS, OCA). Software ALWB is EPL-2.0 (the software, not the content). No explicit robots.txt (404) and no published API/crawl policy. Contact on site: `dcsinfo@goarch.org`.

Implication for this public repo: do not commit pages or text. Our use (private rule checking, keys, counts, citations) is compatible with a conservative reading; any harness that stores DCS text must keep it local/untracked. Crawling was light (about 365 index GETs + ~50 content GETs + ~155 HEADs, polite pacing, parallelism <= 6 on HEAD).

## 6. Where DCS differs from Antiochian practice (candidate "acceptable" classes)

Observed in DCS (facts); Antiochian side needs confirming against ANCA/Typikon (flagged **check**):

1. **Texts**: Fr Seraphim Dedes/GOA translations; psalms SAAS; readings RSV. Wording will never match ANCA; compare by Variable-part identity (key/incipit/mode/date), not text. Acceptable class: translation/wording.
2. **Abridged parish format**: no Canon texts at Sunday Matins (only katavasias and Ode 9; Ode 6 hymns in `li3`), no Litia/Artoklasia in `ve` (only Dec 24 vigil), no OT readings at the plain Sat Vespers probed, Kathisma/psalter fixed text omitted. Acceptable class: GOA omission; check whether ANCA lists the omitted items as Variable parts.
3. **Stichera split**: Sat Vespers Nov 1 is 6 Octoechos + 4 Menaion (counting Glory). Wichita chart (other research branch) gives other splits by rank (e.g. 7+3 simple Sunday). **check**.
4. **Sunday Kontakion** in Liturgy appears to be the fixed Theotokos kontakion in some Sundays (`hoTY.Key0408`) rather than the mode's resurrectional/Menaion kontakion; seasonal Cross kontakion on weekdays (`me/m09/d14`). **check** vs ANCA.
5. **Readings precedence** on Sunday + saint (section 4) varies; use `h91`.
6. **Triodion pre-Lent absent** (empty shells): no DCS answer for 4 Triodion Sundays; ANCA only.
7. **Single year** (2026) and **no Dec 31 Vespers**: no cross-year feast eves.
8. **Greek tradition**: Greek-style Menaion cross-date borrowing (`me.m07.d01` for Nov 1), "Entrance afterfeast" on Nov 22 Sunday, Greek calendar saints (e.g. Nov 22 alt commemoration St Iakovos of Hosios David, Hierarch/new martyrs like Hermeningeld, New Hieromartyr Iakovos). Antiochian/UK saints will not appear: UK divergence log handles British saints; Greek-only saints are acceptable DCS differences.
9. **Dismissal/inserts and hierarchical/alt services** (`ve9`, `li6`, `li7`): ignore for comparison; treat `ve`/`ma`/`li` + `h91` as canonical.
10. **Octoechos**: cycle Tone computed by DCS (`oc.m5.d1` Nov 1; Tone 5 Res apolytikion `TonSynanarchonLogon`, Eothinon 11): matches standard Octoechos/Eothinon cycle; treat as a strong check on Tone/Eothinon for any date.

## 7. Recommended use as secondary answer key

1. Source of truth for slot-by-slot checks: per target date, fetch `ve` (URL date = Saturday for Sunday), `ma`, `li`, `li2`, `li3`, `h91`; skip if size < 10 KB or no `data-key`.
2. Normalise each Variable part to a tuple `(service, slot, source-topic, id)` from the key (`oc.m5.d1`, `me.m11.d01`, `eo.e11`, `le.ep.mc.d274`, `he.a.m5|TonSynanarchonLogon`). Compare tuples (Octoechos mode/day, Menaion date, Eothinon number, reading refs) with our encoded Rule output; ignore text.
3. Strong checks: Tone, Eothinon number, Luke/John Gospel index, Epistle cycle day index, Menaion date used (incl. borrowed dates), Octoechos source for each stichera group, ordering of slots.
4. Weak checks (log, non-blocking): counts of stichera, omitted items, Kontakion choice, reading precedence.
5. Cache locally (untracked) once; build is static (hourly cache). Re-poll for 2027 publication. Respect terms; contact `dcsinfo@goarch.org` if bulk/ongoing use or redistribution is planned.

## 8. Access problems (explicit)

- First guess codes `vs`/`or` 404: DCS codes are `ve`/`ma`. Day index is the only discovery mechanism.
- Vespers date shift (D vs D+1) is easy to get wrong (title `se.m11.d01.ve` under `2026/10/31`).
- Empty-shell pages return HTTP 200, not 404 (Jan 31 - Feb 22 2026 Triodion).
- Only 2026 online; 2025/2027 404; no archive copies found.
- Score PDFs are at host-root `/media/...`, not `/goa/dcs/media/...` (404 there); irrelevant for text.
- No network blocks or auth walls. No Chrome/Playwright MCP needed: curl sufficient since content is server-rendered; frames are only the score viewer.
- Not verified: Antiochian-side comparison (ANCA) and DCS behaviour on major feasts other than Nativity of Theotokos / Elevation Vespers probes; Pascha-cycle and Great Feast Matins/Liturgy structure not walked.

## Reproduce (no content stored)

```
H=https://digitalchantstand.goarch.org/goa/dcs
curl -s $H/servicesindex.html                      # year index
curl -s $H/indexes/20261031.html                   # per-day service list
curl -s $H/h/s/2026/10/31/ve/en/index.html         # Vespers (for Nov 1)
curl -s $H/h/s/2026/11/01/ma/en/index.html         # Matins
curl -s $H/h/s/2026/11/01/li/en/index.html         # Liturgy; +li2, li3, h91
# parse: re.findall(r"<span class='kvp[^']*' data-key='([^']*)'>(.*?)</span>", html, re.S)
```
