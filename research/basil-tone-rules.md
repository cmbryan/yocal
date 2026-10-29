# Basil vs Chrysostom assignment; tone/eothinon cycle rules

Issue #19 (map #5). Research branch, throwaway, never merged. Accessed 2026-10-29.
Public repo: nothing copied. Paraphrase + short cites only. No PDFs committed.

Cite forms: "AT p.NNN" = Antiochian Typikon (Khoury/Morris 2011), page = number of the "Back to Table of Contents NN" footer that closes the page (as #6/#8). "ANCA yyyy-mm-dd READ/Abbr" = antiochian.org `servicetexts` PDF. Tags: **E** explicit, **I** inferred, **G** gap, **Q** quirk.

## TL;DR

1. **Basil days (Antiochian), 10/yr**: Lent Sundays 1-5, Holy Thu, Holy Sat, Jan 1, eve of Nativity, eve of Theophany; Nativity/Theophany eve rule shifts to the feast day when feast is Sun or Mon. Palm Sunday, Lazarus Sat = Chrysostom. **Lent 2 and 5 = Basil: settled** (ANCA key 2018-2026 all years; Typikon Mar 9 section p.267; Patriarchate of Antioch; GOA Holy Cross book).
2. **yocal `basil` flag matches** all of the above in every date checked, with **one divergence**: Annunciation on a Lent Sunday (Mar 25 on Lent 1-5; 15 dates 2000-2099) is flagged Basil; Typikon (Lent 3, p.283) and ANCA 2018-03-25 (Lent 5) say **Chrysostom**.
3. **Tone/eothinon formulas verified**: eothinon ((N-1) mod 11)+1, tone ((N-2) mod 8)+1, N = Sundays after Pentecost (All Saints N=1 -> T8/E1). 0 mismatches vs yocal DB, all of 2000-2099 (5,642 post-Pentecost checks; 2,775 pre-Lent-5 checks with N carried from previous Pentecost across the New Year and Triodion). ANCA headers 2018-2026 agree.
4. **Pascha-cycle eothinon**: ANCA = Typikon = GOA DCS = yocal: Thomas E1, Myrrh E4, Paralytic E5, Samaritan E7, Blind E8, Fathers E10 (tones 1*, 2, 3, 4, 5, 6). OCA E3/E4 for Myrrh/Paralytic is the Slavic outlier: **do not use**. ANCA/Typikon settle it.
5. **Thomas tone**: Antiochian = tone 1 for the Octoechos part (ANCA Abbr 2026-04-19: LIHC "in Tone 1", polyeleos tone 1, 1st eothinon). Pentecost: no Octoechos; notional week-tone 7 by cycle arithmetic (I).

## 1. Basil vs Chrysostom

### 1.1 Rule as Antiochian sources state it

| Day | Liturgy | Source / status |
|---|---|---|
| Lent Sun 1 (Orthodoxy) | Basil | AT p.488 **E**; ANCA 2018-2026 READ title "St. Basil the Great" **E** |
| Lent Sun 2 | Basil | AT Ch.VI p.490 says only "rest of the service for the Sunday" (**G**); AT Mar 9 section p.267 lists Lent 1-5 together "rest of the Liturgy of St. Basil" **E (indirect)**; ANCA 2018-2026 (all 9 yrs) **E**; Antioch Patriarchate list names it **E**; GOA Holy Cross Basil book has a proper "Second Sunday of Lent" section |
| Lent Sun 3 (Cross) | Basil | AT p.493 **E**; ANCA all yrs **E** |
| Lent Sun 4 | Basil | AT p.495 **E**; ANCA all yrs **E** |
| Lent Sun 5 | Basil | AT Ch.VI p.502 gives only the kontakion (**G**); AT Mar 9 p.267 (Lent 1-5) **E (indirect)**; AT Mar 25 when Mar 26 = Lent 5, p.303: "rest of the Liturgy of St. Basil, incl. Typika" **E**; AT Mar 25 forefeast on Lent 5/6 Sunday p.294 "Liturgy of St. Basil" **E**; ANCA 2019-2026 all yrs **E** |
| Lazarus Sat | Chrysostom | AT p.503-504 **E**; ANCA 2026 `3-Laz-Sat-READ.pdf` title Chrysostom **E** |
| Palm Sunday | Chrysostom | AT p.505-506 **E**. ANCA Palm Liturgy variables not located (only VESP/LITART files seen); parish source says Basil excludes Palm Sunday |
| Holy Thursday | Basil | AT p.509 **E** (AT p.320 fn 207 notes the 1685 Typikon prescribes Basil if Annunciation falls on Holy Thu) |
| Holy Saturday | Basil | AT p.517 **E** (Vespers+Basil, the Pascha-eve service; p.320 same) |
| Jan 1 (Circumcision/Basil) | Basil, any weekday incl. Sunday | AT p.164 (Sat/weekday), p.166 (Sunday) **E**; ANCA 2023-01-01 (Sunday) title Basil **E** |
| Eve of Nativity (Dec 24) | Basil (Royal Hours + Vespers + Liturgy) when Dec 24 is Mon-Fri | AT p.140 **E** (feast on Tue-Sat) |
| Nativity on Sunday | Basil on Sunday Dec 25; Sat Dec 24 Liturgy Chrysostom ("as usual") | AT p.143 and p.145 **E**; ANCA 2022-12-24 (Sat) Chrysostom **E** |
| Nativity on Monday | Basil on Mon Dec 25; Sun Dec 24 = Sunday-before-Nativity Liturgy (Chrysostom); Sunday evening Great Vespers of Nativity (no Liturgy) | AT p.148 **E**; ANCA 2023-12-24 Chrysostom **E** |
| Eve of Theophany (Jan 5) Mon-Fri | Basil | AT p.170 **E** |
| Theophany on Sunday | Basil on Sunday; Sat Jan 5 Liturgy Chrysostom then Water blessing | AT p.174 **E**; ANCA 2019-01-05 (Sat) Chrysostom **E** |
| Theophany on Monday | Basil on Monday; Sun Jan 5 Liturgy Chrysostom (Sunday before Theophany) | AT p.176 **E**; ANCA 2020-01-05, 2025-01-05 Chrysostom **E** |
| Annunciation on Lent Sun 3 | **Chrysostom** | AT p.283 "rest of the Liturgy of St. John Chrysostom" **E** |
| Annunciation on Lent Sun 5 | **Chrysostom** | ANCA 2018-03-25 READ title Chrysostom **E** (AT silent on author, p.306 **G**) |
| Annunciation on Lent Sun 4 | Chrysostom (inferred) | AT p.292 gives Liturgy with no author; stray heading "The Divine Liturgy of St. Basil the Great" at p.290 sits between sections, attaches to nothing (**Q**). **I**: follow Lent 3/5 |
| Annunciation on Lent Sun 1, 2 | not covered | AT has no order for these (**G**); can occur (e.g. 2035, 2040, 2046). **I**: Chrysostom by analogy |
| All other Sundays, feasts | Chrysostom | default; AT Ch.I names no Basil days (#6) |

Count: Lent 1-5 (5) + Holy Thu + Holy Sat + Jan 1 + 2 eves/feasts = 10. Matches Antiochian Archdiocese intro text ("ten times a year", per search snippet; page `ww1.antiochian.org/introduction-divine-liturgy` unreachable now, not read directly).

### 1.2 Evidence for Lent 2 and 5 (the open question)

- **ANCA answer key** (primary for this project): `<Mon DD YYYY> READ.pdf` header "Divine Liturgy of St. Basil the Great" for every Lent 1-5 Sunday 2018-2026 except 2018-03-25 (Lent 5 = Annunciation, Chrysostom). 44 of 45 Lent Sundays Basil; Lent 2 = 9/9, Lent 5 = 8/9 (+1 Annunciation).
- **Typikon Mar 9 section** (AT pp.264-267): the "If the feast falls on the 1st, 2nd, 3rd, 4th or 5th Sunday of Great Lent" order ends "The rest of the Divine Liturgy of St. Basil the Great" (p.267) with 1st/3rd Sundays on proper antiphons and the others on Typika. Same section prints a Communion hymn list for 1,2,4,5 vs 3. Reads as a statement for all five. This is the only place the Typikon names Basil for Lent 2/5; I flag it as **E (indirect)**.
- AT Feb 10 (Lent 1, p.242) and Feb 24 (Lent 1, p.254) name Basil; Feb 24 on Lent 2 and 3 (pp.255-256) name no author (**G**, not contradicting).
- **GOA/Greek**: Holy Cross Orthodox Press Basil book (Brookline) preface: Basil "normally celebrated ten times": Jan 1, five Lent Sundays, eves of Christmas/Theophany "and on the former feasts when they occur on Sunday or Monday", Holy Thu, Holy Sat; has proper sections for Lent 2 and 5. Greek Orthodox Patriarchate of Antioch page (antiochpatriarchate.org "…celebrated ten times a year") lists Lent 1,2,3,4,5 individually.
- **Antiochian parish**: St Michael Antiochian (Beaumont TX) pages "What is / When is the Liturgy of St. Basil used?": five Lent Sundays (not Palm), Holy Thu, Holy Sat, eves of Nativity/Theophany (shifted to the feast day if Sun/Mon), Jan 1. Secondary.
- Wichita Parish Typikon Charts I-III + Ranking docs (dowama.org): read; **no statement on Basil vs Chrysostom** (only Jan 1 listed as a feast). Not a source for this rule.
- OCA reflection (Kostoff): Basil on the five Lent Sundays, Holy Thu/Sat, Nativity, Theophany, Jan 1. Secondary.

### 1.3 Decision proposal (rules)

```
basil_days =
  Lent Sundays 1..5            (except when Annunciation falls on that Sunday: then Chrysostom)
  Holy Thursday, Holy Saturday
  Jan 1                         (any weekday)
  Dec 24 / Jan 5 if Mon-Fri     (eve: Royal Hours + Vespers + Liturgy)
  Dec 25 / Jan 6 if Sun or Mon  (feast day itself)
```
Equivalently: Nativity/Theophany eve Liturgy is Basil iff the feast day itself is Tue-Sat; feast day is Basil iff Sun/Mon. Exactly one of the two Basil, never both.

### 1.4 yocal check (`db/4_paschalion_cycle.py` ~l.718-748; DB `YOCal_Master.db`)

- Flags Basil: `G1Sun..G5Sun`, `G7Thu`, `G7Sat`, Jan 1, Dec 24/Jan 5 on Mon-Fri, Dec 25/Jan 6 on Sun/Mon. Spot-checked against ANCA/AT: 2022-12-24 (Sat) no, 12-25 (Sun) yes; 2023-12-24 (Sun) no, 12-25 (Mon) yes; 2019-01-05 no / 01-06 yes; 2020-01-05 no / 01-06 yes; 2023-01-01 yes; 2025-12-24 (Wed) yes. All consistent.
- Basil count per ANCA/DB: `G2Sun` 88 and `G3Sun` 95 over 100 yrs vs 93 for G1/G4/G5: counts differ because Annunciation/other overlaps? Not investigated beyond the Annunciation list below (**G**).
- **Divergence**: every Sunday G1-G5 is Basil even when Mar 25 falls on it. Dates 2000-2099: 2001 (G4), 2007 (G5), 2012 (G4), 2018 (G5), 2029 (G5), 2035 (G2), 2040 (G1), 2046 (G2), 2057 (G2), 2063 (G3), 2068 (G2), 2074 (G3), 2085 (G4), 2091 (G5), 2096 (G4). Only 2018 is checkable vs ANCA (Chrysostom). Fix: suppress Basil when Mar 25 is on a Lent Sunday (I for G1, G2, G4; E for G3 per AT p.283, G5 per ANCA).
- Published years 2018-2026: ANCA agrees with yocal on all Lent Sundays except 2018-03-25.

## 2. Tone and eothinon assignment

### 2.1 Sources

- AT Glossary p.580 ("Tone"): 8-tone cycle begins with Tone 1 on the 2nd Sunday after Pentecost. AT never defines the rotation otherwise (#6). Eothinon: 11 Gospels, no rotation stated (AT Glossary p.576, Ch.I p.29).
- Pentecostarion (AT Ch.VII) fixes the Pascha-cycle values explicitly: Thomas "tone 1" stichera + 1st eothinon (p.526); Myrrhbearers E4 (p.528, but "Glory" cites E2: **Q**); Paralytic E5 (p.529); Samaritan E7 (p.532); Blind man E8 (p.533); Fathers E10 (p.537); Pentecost own Gospel (p.540); All Saints E1, tone 8 (pp.540-541). Octoechos suspended Lazarus Sat -> leavetaking of Thomas Sunday (fn 290 p.503).
- ANCA headers "Tone N / Eothinon M" (READ/Orthros files 2018-2026) as key.

### 2.2 Formulas (tested)

Let N = number of Sundays after Pentecost (All Saints N=1; Pentecost itself N=0).

- eothinon(N) = ((N-1) mod 11) + 1  (All Saints E1, N=12 -> E1 again)
- tone(N) = ((N-2) mod 8) + 1  (N=1 -> 8; N=2 -> 1; N=3 -> 2)
- Same formula **continues unbroken** through New Year, Triodion (Publican etc.) up to Lent 5 (N carried from the previous Pentecost, not restarted at Jan 1 or at Triodion start).
- **Reset at Pascha**: Palm, Pascha, Thomas, Pentecost are outside the carried cycle. From Myrrhbearers the fixed 8-/11- sequence applies:

| Sunday | Tone | Eothinon |
|---|---|---|
| Lent 5 | carried N formula | carried N formula |
| Palm, Pascha | none (Octoechos suspended, AT fn 290) | none (festal) |
| Thomas | 1 (stichera/polyeleos per ANCA Abbr 2026-04-19) | 1 |
| Myrrhbearers | 2 | 4 |
| Paralytic | 3 | 5 |
| Samaritan | 4 | 7 |
| Blind man | 5 | 8 |
| Fathers (6th Sun after Pascha) | 6 | 10 |
| Pentecost | no Res; notional 7 (I) | none (own Gospel) |
| All Saints (N=1) | 8 | 1 |

Because the cycle restarts at Myrrhbearers (tone 2) and again at All Saints, the Lent-5 week-tone/eothinon vary by year; they are NOT predictable from the Pascha cycle (seen in key: Lent 5 = T5/E2, T8/E8, T1/E9, T4/E1).

### 2.3 Test results

- `db/7_tone_eoth.py` logic = the formulas above (8-cycle seeded T2 at Pascha+14 of previous year; 11-cycle seeded E1 at All Saints). Logic reviewed, not changed.
- Query of `YOCal_Master.db` 2000-2099 (read-only):
  - Post-Pentecost Sundays: 5,642 tone+eothinon values compared to formula, **0 mismatches**. Festal overrides (tone "of the feast") only on 08-06, 09-14, 12-25; eothinon "of the feast" also 02-02, 03-25, 08-15, 09-08, 11-21 (Theotokos/Lord feasts).
  - Pre-Lent-5 Sundays with N carried from previous Pentecost: 2,775 values, **0 mismatches**.
  - Pascha-cycle table identical in all 100 yrs: Thomas E1, +14 T2/E4, +21 T3/E5, +28 T4/E7, +35 T5/E8, +42 T6/E10, +56 T8/E1, +63 T1/E2.
- ANCA 2018-2026 (9 yrs): Myrrh T2/E4, Paralytic T3/E5, Samaritan T4/E7, Blind T5/E8, Fathers T6/E10, All Saints T8/E1 every year; Publican..Cheesefare and Lent 1-5 headers consistent with formula (e.g. 2026: Publican T1/E1 ... Cheesefare T4/E4, Lent 1 T5/E5, Lent 5 T1/E9). Header on Thomas file absent; slots read in Tone 1/E1 (ANCA Abbr 2026-04-19).
- Not independent for the Pascha-cycle: yocal's sequence 1,4,5,7,8,10 equals the Typikon's and ANCA's. OCA (E3/E4 for Myrrh/Paralytic) differs and is Slavic; GOA DCS 2026 = Typikon. So #12 doubt "GOA E4/E5 vs OCA E3/E4" is resolved for Antiochian: **E4/E5**.

### 2.4 Festal Sundays (Lord/Theotokos feast on a Sunday)

- Formula still gives a numeric "week tone" (e.g. 2025-09-14: N=14 -> T5; 2028-08-06: N=9 -> T8, matches OCA per #12). yocal stores "Tone of the feast". Cycle after the feast is unaffected (checked: 0 mismatches including those Sundays).
- Whether the Octoechos tone is **used** that day is a precedence question (Res service omitted for Nativity, Theophany, Transfiguration, Cross: AT Ch.I p.11-12); the week-tone number only matters for Saturday-eve/next-day hymn selection and the Theotokos-feast-on-Sunday cases, where AT p.25 fn 18 keeps the eothinon Gospel. **I**: encode numeric week-tone always (computed) plus a `res_service` boolean.
- Theotokos feasts on Sunday: yocal sets "Eothinon of the feast" (but tone stays numeric). AT p.25 fn 18 says NA Antiochian chants the eothinon Gospel as well. Not resolved vs ANCA here (**G**; no such Sunday in 2018-2026 sample). Examples: 2027-08-15 Dormition.
- Pentecost: AT says no Res; tone 7 only notional (**I**). Thomas: tone 1/E1 **E** (above).

## 3. Open / flagged

1. **I**: Annunciation on Lent 1, 2, 4 -> Chrysostom (AT silent/ambiguous; only Lent 3 and ANCA-Lent 5 explicit). Ask ANCA/OLG@antiochian.org if wanted; next occurrence 2029-03-25 (Lent 5), 2035 (Lent 2).
2. **Q**: AT p.290 orphan heading "Liturgy of St. Basil" before the Lent 4 Annunciation order; could mean Basil there. ANCA has no Lent 4 case in 2018-2026.
3. **G**: Lent 2/5 Basil in Ch.VI is implicit; only Mar 9 (p.267) and Mar 25 (pp.294, 303) wording supports it. ANCA settles it.
4. **G**: ANCA Basil-day files for eves/feasts (Dec 24 2025, Jan 5 2026, Holy Thu/Sat, Palm, Nativity/Theophany on Sun/Mon) are non-date-keyed (see #9); only the adjacent Chrysostom days were checked. Basil for those relies on AT + parish/Patriarchate sources.
5. **G**: Counts G2Sun 88 / G3Sun 95 / G1,4,5 93 of 100 Basil-flagged in DB are unexplained (other Sundays with overlap?); not investigated.
6. **Q**: Myrrhbearers Matins Gospel E4 vs praises "Glory" E2 (AT p.528); ANCA header says E4.
7. **G**: ww1.antiochian.org Archdiocese "ten times a year" intro page not fetched (host down); relied on search snippet + Patriarchate of Antioch page.

## 4. Sources

- Antiochian Typikon (local PDF, `pdftotext`), pages as cited.
- ANCA `servicetexts` (blob `antiochianprodsa.blob.core.windows.net/servicetexts/<Mon DD YYYY> READ.pdf`, `Abbr.pdf`), 2018-2026 Lent 1-5, Pascha cycle, All Saints, Dec 24 2022/2023, Jan 5 2019/2020/2025, Jan 1 2023, Mar 25 2018, `3-Laz-Sat-READ.pdf`, `4 Nativity Read JOHN.pdf`. Downloaded to scratch only.
- Greek Orthodox Patriarchate of Antioch: https://antiochpatriarchate.org/en/page/the-divine-liturgy-of-st-basil-is-celebrated-ten-times-a-year/1375/
- Holy Cross Orthodox Press, Divine Liturgy of St Basil (PDF, preface): https://holycrosspgh.org/wp-content/uploads/2024/06/Divine-Liturgy-of-Saint-Basil-the-Great.pdf
- St Michael Antiochian parish: https://stmichaeltx.org/orthodox-101/worship-services/when-is-the-liturgy-of-st-basil-used/ and /what-is-the-liturgy-of-st-basil/
- OCA reflection: https://www.oca.org/reflections/fr.-steven-kostoff/on-the-liturgy-of-saint-basil-the-great
- Wichita Parish Typikon Charts/Ranking: http://www.dowama.org/node/31 (read, no Basil rule)
- yocal: `db/7_tone_eoth.py`, `db/4_paschalion_cycle.py`, `YOCal_Master.db` (main checkout), prior branches #6, #8, #9, #10, #11, #12.
