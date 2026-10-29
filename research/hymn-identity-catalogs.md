# Hymn identity catalog sources (issue #13, map #5)

Researched 2026-10-29. Throwaway branch; never merged. No PDFs or hymn text committed. Only slot labels, record keys, licence statements and short identifiers quoted.

## Answer

Best source for machine-usable hymn identity: **AGES-Initiatives ALWB data on GitHub** (the same data that generates GOA Digital Chant Stand). It gives, per liturgical slot, a stable record key + tone/mode + model melody + (sometimes) author + English incipit, for Octoechos (8 tones x 7 days), 11 eothina, Menaion (371 day files), Triodion, Pentecostarion, heirmoi, commons. Same keys visible in DCS HTML (`data-key`). Licences mixed (CC0 / CC BY-NC-SA 4.0 / none). Key identifiers are enough for placeholder scheduling; text/incipit should be fetched at build time, not committed.

ANCA PDF labels and the Typikon give slot + cycle + tone only: enough to *check* a schedule, not an identity catalog.

## Sources assessed

| Source | Identity it gives | Machine-usable | Licence | Verdict |
|---|---|---|---|---|
| ALWB templates + libraries (GitHub, AGES-Initiatives) | slot key, mode, melody (model hymn), poet, incipit, borrowed-from refs | Yes: plain `key = value` `.ares` files, `.atem` templates | see Licences | Primary |
| GOA DCS HTML | same keys, as `data-key` attrs on rendered text; per service/date | Yes (static HTML, curl works) | site: all rights reserved, worship use; robots: `ai-train=no`, `use=reference` | Secondary; key extraction only |
| ANCA "Liturgy Variables" PDF | label per slot: "<TYPE> IN TONE <N>", tone/eothinon header, saint name | Semi: pdftotext works, labels uppercase | HTM copyright (see below) | Answer key only |
| Antiochian Typikon (local PDF) | role + cycle + tone ("for the Resurrection in the tone of the week"), counts, occasional incipits of doxastika | Prose only | copy-protected | Rule source, not catalog |
| OrthodoxWiki | prose/saint pages | no | GFDL + CC BY-SA 2.5 dual (OrthodoxWiki:Copyrights) | No hymn index found; skip |
| Ponomar (typiconman/ponomar) | tone-tagged troparion/kontakion in per-commemoration XML; ServiceRules.xml | XML | code GPL-3.0; texts: translator copyrights, unstated | Too sparse: 8 commemoration files in `languages/xml/Commemorations` (checked); alpha |
| anttro/ponomar-pwa, ryanmichael/oca-services, augyyyyy/typikon-coded, orthodox-liturgical-app | scraped JSON (OCA/HTM-derived) | JSON | no licence on most (GitHub API: none); nikolareljin/orthodox-calendar MIT (calendar only) | Avoid: unlicensed scrapes of copyrighted text. Not examined in depth |
| OCA oca.org/saints/troparia | per-day troparion/kontakion + tone | web only | OCA copyright | Not a catalog |
| Wirayudhaa/ocma-data | calendar only | JSON | unverified | Not hymns |

## ALWB / DCS detail

### Repos (AGES-Initiatives org, pushed Mar 2026)

- `ages-alwb-templates`: service templates (`.atem`), incl. `Books/Menaion/mNN/bk.me.mNN.dDD.atem` (per-day slot list), `Dated-Services/mNN/dDD/se.*.atem` (per-date service assembly, incl. `when-name-of-day-is Sunday use:` blocks), `Movable-Cycle/mcMaps`, `Blocks/Selectors`, `Typikon/`, `Books/Liturgical_Guide/GOA_20xx` (guide of incipits per slot, uses `Selector_Incipits`).
- `ages-alwb-library-en-us-dedes`: English (Fr Seraphim Dedes), `.ares` per record.
- `alwb-library-en-us-goadedes`: English layered for GOA (overrides/fills dedes).
- `ages-alwb-library-gr-gr-cog`: Greek (Church of Greece) texts; fullest slot/mode/poet coverage.
- `ages-alwb-library-en-us-goa`: GOA ceremonial/typikon constants. Others: `-en-us-oca`, `-holycross`, `-en-uk-ware` (UK, Mother Mary/Ware; not examined), `-andronache`, etc.

### Key scheme (verified on Nov 1 2026 DCS pages + repo)

`<record>_<lang>_<lib>|<slot>`, e.g.

- `oc.m5.d1 | ocVE.Stichera1..7, ocVE.SticTheotokion, ocVE.Aposticha1..4, ocVE.AposTheotokion, ocVE.Apolytikion` — Octoechos mode 5, day 1 (d1 = Sunday, d6 = Friday, confirmed from `da.d1`/`da.d6` labels). Matins: `ocMA.Kathisma11..23, Hypakoe, Antiphon11..33, Kontakion, Oikos, Lauds1..8, ApolTheotokion`; Liturgy: `ocLI.Beatitudes1..6`. 306 slot records per mode-day file (incl. canon odes).
- `me.m11.d01 | meVE.Stichera01..03, SticGlory, SticTheotokion, Aposticha1..3, AposGlory, Apolytikion1, meMA.Kontakion1/Oikos1, Exaposteilarion1, Lauds1..4, LaudsGlory, meLI.Kontakion1, Megalynarion` plus canon odes.
- `eo.e11 | eo.Exaposteilarion, eo.Doxasticon`; Gospel `le.go.eo.w11`.
- `he.a.m5 | heAU.TonSynanarchonLogon` = automelon (model hymn) keyed by transliterated Greek incipit + `.greekname`, `.name`, `.melody`, `.incipit`, `.mode`. `he.h.m4 | heHE.*` heirmoi; `he.ga | heGA.OiMartyresSouKyrie` = commons (e.g. apolytikion "for the martyrs", mode 4).
- Prokeimena: `psLI.sunday.m1..m8.prokeimenon`, `psLI.weekday.d2..d7.prokeimenon`, commons (`angels, apostles, hierarchs, martyrs, monastics`), Menaion `psLI.m11.d01.prokeimenon`.
- Readings: `le.ep.me.m11.d01` (Menaion epistle), `le.go.lu.d035` (Luke cycle index).
- Triodion `tr.d001..d071`, Pentecostarion `pe.d071..` (Pascha = d071 in the movable-cycle map `mc.map.li.atem`).
- Per-slot metadata fields: `.mode`, `.melody`, `.greekmelody`, `.incipit`, `.poet` (author; catalog `Constants/poets_*.ares`), `.text`. Borrowing is explicit: e.g. `me.m11.d01.meVE.Stichera02.incipit = me.m07.d01...Stichera02.incipit` (Nov 1 reuses Jul 1 Cosmas and Damian stichera) = natural identity graph for "same hymn reused".

### Verified example (Sat Oct 31 2026 Vespers, DCS)

Keys: `oc.m5.d1|ocVE.Stichera1..6`, `me.m11.d01_gr_GR_cog|meVE.MM...` (Menaion block), `me.m07.d01|meVE.Stichera02/03/SticGlory`, `oc.m5.d1|ocVE.SticTheotokion`, `oc.m6.d1|ocVE.AposTheotokion`, `he.a.m5|heAU.TonSynanarchonLogon` (apolytikion), `oc.m8.d1|ocVE.ApolTheotokionVM`. Typikon Nov 1 (p.100) independently calls for "Now" aposticha theotokion "in tone 6" and troparia theotokion "in tone 8": matches. So DCS keys are usable to cross-check Typikon-derived rules.

### Coverage (computed from repos)

Menaion day files per lib: 371. Slots with content (text/incipit) in Greek `cog`: Stichera01 365, Apolytikion1 137, Kontakion1 263, SticGlory 216, Lauds1 116, Exaposteilarion1 245. English: `dedes` Apolytikion1 123, `goadedes` 56 (overlay). `poet` filled on 118 of 216 Glory slots; rarely elsewhere. Octoechos 57 files (8x7 + weekdays), eothina 11, Triodion 60 files, Pentecostarion 57 files. `meHO.rank`/`number` (feast rank fields) exist but are empty in 1114 of 1114 records checked: no usable rank data here.

### DCS access

`https://digitalchantstand.goarch.org/goa/dcs/h/s/YYYY/MM/DD/<svc>/en/index.html` is server-rendered, no JS needed. Verified 200: `li` (Liturgy), `ve` (Vespers), `ma`, `ma2`; `or` is 404 (Matins code is `ma`). Not exhaustively probed (see #10).

## ANCA PDF slot labels (answer key)

Samples fetched (not committed): Oct 4, 18, 25, Nov 1, Sep 27, Feb 15 2026. 404 for Sep 8, Dec 25, Jan 1, Apr 12 and for any non-`READ` suffix tried (see #9). Observed label forms:

- `RESURRECTIONAL APOLYTIKION IN TONE <N> (KAZAN) (CROW[-MP3])`; Feb 15 variant has no melody tags.
- `APOLYTIKION OF SS. <names> IN TONE <N>`; `APOLYTIKION FOR THE MARTYRS IN TONE FOUR` (commons phrased as "for the <class>"); `ORDINARY KONTAKION IN TONE TWO (CHANT) (CHORAL)`; Triodion `KONTAKION FOR SUNDAY OF LAST JUDGMENT IN TONE ONE`; `KOINONIKON (COMMUNION HYMN) FOR ST. <X> IN TONE EIGHT`.
- Header: `Tone N / Eothinon M` + Sunday name + saints list.
- Prokeimenon/alleluia, eisodikon not labelled with tone (prokeimenon only identified by text, epistle by "(For <saint>)").
- Only Liturgy; no Vespers/Matins `READ` file found by URL pattern.

Gives: type, tone, which saint/feast. Lacks: key, author, incipit-as-id, melody for non-resurrectional hymns, Matins/Vespers slots. Mapping label to ALWB key needs manual alignment (e.g. "FOR THE MARTYRS IN TONE FOUR" = `he.ga|heGA.OiMartyresSouKyrie`, mode 4: matches by tone and class, name differs).

PDF footer states HTM-copyrighted Menaion/Horologion/Pentecostarion/Octoechos/Psalter text, used with permission, single personal copy only. Document metadata: author P. Samore.

## Typikon (local `typikon.txt`)

Nov 1 (pp.99-100 per map; text lines ~5085-5165) and Jul 1 (~22479-22530): hymns identified only as role + cycle + tone ("6 for the Resurrection in the tone of the week", "theotokion in tone 8"), plus doxastikon incipits on some (e.g. "Unending is the grace..."). ~800 `Glory…` lines, ~128 with an incipit. No hymn catalog, no authors, no model melodies. Note Typikon wording differs from DCS slot counts: Typikon Nov 1 Vespers wants 4 Menaion stichera + Glory; DCS Oct 31 shows 3 + Glory. Divergence to log (ALWB follows GOA/Greek Menaion; Typikon follows Arabic/Antiochian books).

## Licences (explicit)

| Item | Licence | Evidence |
|---|---|---|
| ALWB software | EPL-2.0 | DCS About page; alwb-jars |
| `ages-alwb-templates`, `-library-en-us-dedes`, `-library-en-us-goa`, `-system` | CC BY-NC-SA 4.0 ("(c) Fr. Seraphim Dedes" / "(c) Greek Orthodox Archdiocese of America") | `LICENSE` in each repo; GitHub shows "Other" |
| `alwb-library-en-us-goadedes` | CC0 1.0 | `LICENSE.md`; GitHub API `CC0-1.0` |
| `ages-alwb-library-gr-gr-cog` | **none stated** (no LICENSE; GitHub API empty) => all rights reserved by default | repo listing |
| DCS website text | "for worship only... may be copied by parish... not for sale w/o GOA permission"; Bible: RSV/NKJV/SAAS copyrighted | DCS About + page credits |
| DCS robots (dcs.goarch.org) | `Content-Signal: search=yes, ai-train=no, use=reference` | robots.txt |
| ANCA PDFs | HTM copyright; single personal printed copy | PDF footer |
| Antiochian Typikon | copy-protected, no open licence | per map notes |
| OrthodoxWiki | GFDL + CC BY-SA 2.5 | OrthodoxWiki:Copyrights |
| Ponomar code | GPL-3.0 | repo LICENSE |

**Conflict to resolve:** `goadedes` repo asserts CC0 while the DCS site asserts all rights reserved over the same translations. Treat CC0 as owner-asserted but verify with GOA/AGES before relying on it. Everything else: BY-NC-SA requires attribution + NonCommercial + ShareAlike for derivatives: do not vendor into this public repo without a decision; clearly "identifiers only" (keys, tone numbers) is the low-risk path.

## Recommendation for #16 (identity scheme)

1. Identity tuple: `(cycle, tone-or-day key, service, slot, index)`, taking ALWB keys as-is (`oc.m5.d1:ocVE.Stichera1`, `me.m11.d01:meVE.Apolytikion1`, `he.ga:heGA.OiMartyresSouKyrie`, `psLI.sunday.m5.prokeimenon`, `eo.e11:eo.Doxasticon`). Treat as external foreign keys; keep reference-resolution (borrowed-from) as a field.
2. Repo stores keys only; text/incipit/author fetched at build time from upstream clones (cached outside repo). Placeholder shows slot label + tone + key.
3. Typikon-style role phrasing ("the tone of the week", "theotokion in tone 8") maps directly to `(oc, tone, d1, slot)`; saint hymns map via `me.mNN.dDD`; commons via `he.ga`. Rules layer (#14) therefore only needs to emit `(source-cycle, tone/day, slot)` selectors.
4. Use ANCA labels as test oracle: parse `<TYPE> IN TONE <N>` and compare type + tone (not text).

## Gaps

- Antiochian-specific choices (counts, tones of theotokia, saints/UK saints) not in ALWB; Menaion data is GOA/Greek tradition. Expect divergences (Nov 1 stichera count).
- UK saints: no key source. ALWB has no British saints data (not verified exhaustively); `ages-alwb-library-en-uk-ware` is Mother Mary/Ware Festal Menaion/Triodion (not inspected).
- Saint's apolytikion exists for only ~137 of 366 Menaion days in Greek; others fall to commons (`heGA`) by class: needs a day-to-class map (not provided; ANCA/DCS show the choice only per date).
- Keys are positional, not semantic hymn ids: same hymn appearing in several slots has different keys (borrow refs help only inside ALWB). Some keys reuse unrelated records (e.g. Sunday communion hymn is keyed `tr.d069|trLI.CommunionHymn`).
- Octoechos Sunday Vespers/Matins stichera in `dedes` are partly empty (stub incipit "..."); `goadedes` fills them. English coverage = union of both; Greek `cog` full but unlicensed.
- No feast rank data (`meHO.rank` empty); #12/#15 still needs another source.
- Eothinon identity fine (`eo.e01..e11`); Luke/John gospel indices (`le.go.lu.d035`) require mapping from the yocal calendar's cycle logic: not verified.
- ANCA: Liturgy only, no Vespers/Matins variables found; prokeimenon/alleluia unlabelled.
- Only ALWB `main` snapshots examined; repos "automatically exported from code.google.com" so history/provenance of content licences uncertain.

## Side finding (for rule tickets #14/#9/#15)

`ages-alwb-templates` is effectively an executable encoding of GOA service-assembly rules: `Dated-Services/*/se.*.li.atem` has `when-name-of-day-is Sunday use:` composition (e.g. Sunday Liturgy = Enarxis, antiphons, entrance, resurrectional apolytikion by mode of week, then Menaion apolytikion, kontakion by season, Menaion epistle, daily gospel), `Blocks/Selectors/*` (FestalApolytikion, Kontakion, Eisodikon, Prokeimenon, Megalynarion, ...), `Movable-Cycle/mcMaps`. Useful as a third-party reference/cross-check (GOA practice, BY-NC-SA), distinct from the Antiochian rules. Not analysed beyond samples.

## Sources

- https://github.com/AGES-Initiatives (repos listed above; `gh api orgs/AGES-Initiatives/repos` for licences)
- https://digitalchantstand.goarch.org/goa/dcs/about.html ; https://digitalchantstand.goarch.org/goa/dcs/h/s/2026/11/01/li/en/index.html (also `/ma/`, `/2026/10/31/ve/`, `/2026/10/30/li/`)
- https://dcs.goarch.org/robots.txt
- https://www.antiochian.org/servicetexts/Nov%2001%202026%20READ.pdf (+ Oct 4/18/25, Sep 27, Feb 15 2026)
- Antiochian Typikon (Khoury/Morris 2011), local text
- https://orthodoxwiki.org/OrthodoxWiki:Copyrights
- https://github.com/typiconman/ponomar
