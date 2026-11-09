# Major feast rules: slot lists, coincidence, displacement of Sunday frame

Issue #36 (map #5). Paraphrased; short quotes only; no PDFs/long excerpts committed. Throwaway branch, not for merge.

## 0. Conventions

- "p.NN" = printed footer page, Antiochian Typikon (Khoury/Morris 2011). Typikon's own TOC runs ~2-3 low (see #7, #8). "Ch.I p.NN" = general rules; Ch.V dates = Menaia; Ch.VI/VII = Triodion/Pentecostarion; "Gloss." = Ch. XI Glossary pp.575-577.
- Status: **E** explicit, **I** inferred (from ANCA or pattern, flagged), **M** missing (Typikon silent/defers to Menaion/Triodion books), **Q** internal conflict or typo.
- "N stichera" at "Lord I have cried" = count of verse-slots; the Glory/Now line is **extra** in the Typikon wording ("10 stichera, Glory, Now") and in ANCA (verses 10..1, then a separate Doxasticon). Encode `(res, feast1, feast2, glory_owner, now_owner)`, not a bare total.
- ANCA = AOCANA `servicetexts` PDFs via `prototypes/anca-index/pages.json` (#29); plain `VESP.pdf` (Saturday eve) and `Abbr.pdf` (Sunday rubrics). Checked by counting verse-slots per heading (my parse, not the harness).
- "Vespers" for a Sunday feast = Saturday-evening Great Vespers (liturgical-day unit, #15.4). For a **Saturday** feast, the Saturday-evening Vespers is the next Sunday's (afterfeast-Sunday rule), and the feast's own Vespers is Friday's.
- R = Resurrection (tone of week).

## 1. Answer

1. All 12 in-scope feasts + Palm/Ascension/Pentecost/Pascha have explicit Typikon slot lists for the **Sunday** case, except Transfiguration (pointer "follow Menaion", p.449) and Elevation (Sunday only; weekday not stated, p.75).
2. **Weekday/Saturday** feast Vespers: explicit full order only for Nativity Theotokos (p.64), Nativity of Christ (Tue-Sat p.138-141), Epiphany (p.170-172), Dormition (p.455). All others = "follow the Menaion" (+ listed changes): **missing** (Menaion book content, #7 gap 1).
3. Which feasts displace the Sunday frame (no R stichera): Nativity, Theophany, Transfiguration, Elevation, Palm, Thomas (not in scope), Pentecost (Ch.I p.12), plus Pascha (own cycle). Everything else keeps R beside the feast (sec. 3).
4. **Typikon vs ANCA conflicts found (Vespers LIHC):** Presentation on Sunday (Typikon 6R+4 p.218; ANCA 4R+6, 2/2 samples) and Annunciation on Lent 5 Sunday (Typikon 6R+4 p.304; ANCA 4R+6, 1 sample). Also Holy Saturday Vespers (Typikon 8 = 4R+4 p.516; ANCA 10, apparently 6R+4) and Annunciation-on-Sat-of-Lent-4 Glory owner (Typikon: Gabriel p.289; ANCA: Annunciation). Treat as candidate Rule errors per map rule (unexplained ANCA mismatch = blocking) or logged divergences; needs user decision (sec. 7).
5. ANCA key is **absent** for every Sunday where a feast drops R and in the date range: Theophany 2019-01-06, Nativity 2022-12-25, Transfiguration 2023-08-06, Cross 2025-09-14 (liturgicday pages have no `servicetexts` links; HTML checked in `prototypes/anca-index/raw`). So the Res-omission rules are explicit-only, unchecked.

## 2. Slot lists and counts per feast (Typikon)

LIHC = "Lord I have cried" stichera. Apost = aposticha. Trop = troparia at Vespers. Matins/Liturgy only where they differ from Sunday template.

### 2.1 Sunday coincidence (feast on Sunday; Vespers = Sat eve)

| Feast | LIHC (Glory / Now) | Apost | Trop | Matins/Liturgy deltas | Status, cite |
|---|---|---|---|---|---|
| Nativity Theotokos Sep 8 | 4R + 6 feast (G,N feast); readings | R + G/N feast | R 1x, feast 2x | polyeleos; evlogetaria **not** sung; feast prokeimenon + Gospel then "In that we have beheld"; 2 exaposteilaria feast + R; praises 4R+4; Epistle/Gospel of Sunday before Cross | E p.66-68 |
| Elevation Sep 14 | 3 stichera x2 = 6, G/N Cross; **no R**; readings | Cross stichera + G/N | Cross | Res omitted; evlogetaria not sung; 6 troparia per ode; procession | E p.75-77; Ch.I p.11-12 |
| Entry Nov 21 | 4R + 6 (G,N feast); readings | R + G/N feast | R 1x, feast 2x | as Sep 8 (feast Gospel + R); katavasia 1st Nativity | E p.113-114 |
| Nativity Dec 25 | Sat eve: 6 idiomela, G/N feast; entrance with Gospel; OT readings (Gen 1:1-13, Is 9:6-7 with troparia) + Epistle + Gospel; **no R**, no kathisma | feast | feast 3x | feast only; praises 4 | E p.143-145; Ch.I p.11-12 |
| Circumcision/Basil Jan 1 | 4R + 3 Circ (2 + first repeated) + 3 Basil; G Basil, N R theotokion | R + G Basil + N Circ | R, Basil, Circ | Basil Liturgy; polyeleos **with** evlogetaria (differs from Theotokos pattern, Q); praises 4R+4 (ANCA) | E p.165-166 |
| Theophany Jan 6 | Sat eve: feast only, no R (Great Vespers); Fri Royal Hours + Fri Vespers; Sun Basil + blessing of waters | feast | feast | no R | E p.173-174 |
| Presentation Feb 2 (pre-Triodion) | **6R + 4** Presentation, G feast; readings | R + G/N feast | R 1x, feast 2x | evlogetaria not sung (p.219) | E p.218-219 (**ANCA 4R+6, conflict**) |
| Presentation on Triodion Sun | 4R + 2 Triodion; G Triodion, N feast; Meatfare: 4R + 3 Triodion | R, G Triodion, N feast | R 1x, feast 2x | Gospel of Sunday | E p.220 (sum 6 not 10, Q: typo) |
| Annunciation Mar 25 on Lent 3 Sun | Sat eve: 3R + 3 Cross + 4 Annun; G Cross, N Annun; readings | R + G Cross | R, Cross, Annun | Cross Sunday frame kept | E p.280-282 |
| Annunciation on Lent 4 Sun | 4R + 6 Annun; G/N Annun; readings | R + G/N Annun | R 1x, Annun 2x | | E p.290-291 |
| Annunciation on Lent 5 Sun | **6R + 4** Annun; G/N Annun; readings | R + G/N | R 1x, Annun 2x | | E p.304-305 (**ANCA 4R+6, conflict**) |
| Annunciation on Palm Sun / Lazarus Sat | feast takes precedence (p.309); Palm Sun: feast + Lazarus mixed (4 Lazarus, 3 forefeast on Fri Presanctified) | | | | E p.307-311 |
| Annunciation on Pascha / Bright Mon | Pascha: Glory from Pentecostarion, Now feast (Ch.I p.13); Bright Mon Sunday eve: 4R tone 2 + 4 Annun, G tone 2 | | | | E Ch.I p.13; p.322 |
| Transfiguration Aug 6 | "follow the Menaion", **nothing for R**; omit "Blessed is the man"; troparion 3x; Great Prokeimenon "Our God is in heaven" any day (p.450) | | feast | no "In that we have beheld"; canons without verses; 9th ode of both | E p.449-450; Vespers slot list **M** (Menaion) |
| Dormition Aug 15 | 4R + 3 prosomia x2 = 6; G/N Dormition; readings | R + G/N | R, Dormition | evlogetaria not sung (p.458) | E p.457-458 |
| Palm Sunday (Pascha-7) | 10 = 5 stichera tone 6, each twice; G/N repeat 1st; entrance; OT readings; Triodion aposticha | Triodion | Lazarus 2x, "buried with thee" 1x | no R stichera; evlogetaria **not** sung; no "In that we have beheld"; no exaposteilaria; Chrysostom; Res service omitted (Ch.I p.11-12) | E p.504-506; Vespers day **Q** (day unstated) |
| Pascha | Holy Sat Vespers + Basil: 8 = 4R tone 1 + 4 idiomela; G/N "Moses"; entrance with Gospel; 15 OT readings; special prokeimenon; Matins Paschal canon tone 1; Chrysostom; Agape Vespers (6 = Res tone 2 + G tone 2) | | | | E p.516-523; practice variant fn 312 p.514 |
| Ascension (Thu) | Wed: 10 = 5 Ascension tone 6 each x2; G/N tone 6; entrance; OT readings | idiomela tone 2 + G/N tone 6 | Ascension 3x | | E p.535-536 |
| Pentecost (Sun) | Sat eve: 10 = 3 tone 1 (+1st repeated = 4) + 5 tone 2 (+1st repeated = 6); G/N doxastikon tone 8; prokeimenon + 3 OT readings; **no R** | Pentecost tone 6 + G/N tone 8 | Pentecost 3x | evlogetaria not sung (ANCA Abbr agrees); Kneeling Vespers (Sun eve) 8 stichera: text says 3 "repeating each for a total of 8" (Q, arithmetic) | E p.538-540 |

Forefeast on Sunday (Vespers 6R+4 forefeast, G forefeast, N R): Sep 7 p.63; Nov 20 p.110; Aug 5 p.448; Aug 14 p.453; Feb 1 4R+3+3 Tryphon p.216-217; Sep 13 4R+3 Consecration+3 forefeast p.73; Dec 20-24 Sunday-before-Nativity p.133-138 (6R+4 Forefathers Dec 18-19; Dec 24: **no R**, 8 stichera = 3 Forefathers + repeat 1st, + 4 forefeast; p.136, Ch.I p.12). All E.

Afterfeast Sunday (Sat-eve Vespers): Nativity Theotokos 6R+4 p.70; Cross 6R+4 p.79; Entry 6R+4 p.114; Nativity of Christ Dec 26 4R+3+3 p.152; Dec 31 leavetaking Sunday 3R+4 Nativity+3 Sunday-after p.161; Theophany Jan 7 4R+3+3 Forerunner p.177-179; Presentation Sunday after p.223-225; Transfiguration 6R+4 p.450; Dormition 6R+4 p.461 (Napkin Aug 16 on Sunday 4R+3+3 p.460). Leavetaking on Sunday: Nativity Theotokos 4R+6 p.71; Transfiguration 4R+6 p.452; Dormition 4R+6 p.463. All E. Ch.I p.13 says leavetaking of a Theotokos feast takes G/N of feast only; Ch.V Sep 12 gives N = R theotokion (p.71, Q).

### 2.2 Weekday and Saturday coincidence (feast on Mon-Sat; Vespers = eve)

| Feast | Eve Vespers | Status, cite |
|---|---|---|
| Nativity Theotokos | 6 feast stichera; G/N repeat 1st; daily prokeimenon; readings; Apost 3 idiomela + G/N; troparion 3x | E p.64-65 |
| Elevation | none stated for weekday/Saturday (single order headed Sunday) | **M** p.75 |
| Entry | "Menaion" + changes (polyeleos, Nativity katavasia, 9th ode both) | **M** (Vespers) p.111 |
| Nativity of Christ Tue-Sat | Royal Hours Dec 24 morning (p.138-139); Great Vespers + Basil Liturgy: 4 idiomela, first and second repeated = 6; G/N; entrance with Gospel; 8 Menaion readings w/ 2 troparia (fn 80 p.140); Basil | E p.138-141 |
| Nativity Monday | Sat eve: Forefathers, 8 stichera (nothing for R, p.146); Sun Matins/Liturgy Sunday-before-Nativity; **Sun eve = Sunday-order Nativity Vespers**; Mon Basil | E p.145-148 |
| Circumcision | "Menaion" with dismissal phrase; midnight litia Basil | **M** (Vespers) p.164 |
| Theophany Tue-Sat | Jan 5 Royal Hours + Vespers (readings 3; Menaion has 13, fn p.170) + Basil + Great Blessing | E p.170-172 |
| Theophany Monday | Sat eve = Sunday-before-Epiphany 7R+3 (p.174-175); Sun eve feast Vespers only (p.176) | E p.174-176 |
| Presentation | "Menaion" + changes (polyeleos, 9th ode) | **M** p.218 |
| Annunciation | per-Lenten-weekday grid: e.g. Tue-Thu wk 4-6 eve 10 = 7 Triodion + 3 forefeast; Sat wk 3/4 eves 6 = 3 Triodion + 3 forefeast | E p.277-324 (grid; Menaion/Triodion text behind) |
| Transfiguration | "Menaion"; Great Prokeimenon "Our God is in heaven" on the evening any day | **M** + E p.450 |
| Dormition | 6 prosomia x2; G/N; entrance; readings; Apost 3 idiomela + G/N; troparion 3x | E p.455 |
| Ascension | Wed only (always Thursday) | E p.535-536 |
| Fore/leavetaking weekday (Ch.II) | Daily Vespers: 3 forefeast/leavetaking + 3 saint, G saint, N forefeast; entrance only on leavetaking of Lord/Theotokos feasts; forefeast troparion not sung | E Ch.II p.42-43 |
| Leavetaking weekday | feast service minus readings, litia, polyeleos, Matins Gospel; daily Epistle/Gospel | E Sep 12 p.71; Sep 21 p.83; Dec 31 p.161; Aug 13 p.452; Aug 23 p.463 |

### 2.3 Saturday feast: effect on Sat-eve (Sunday-after) Vespers

Sat feast means the Saturday-evening Vespers is the Sunday-after-feast service, not the feast Vespers. Typikon gives these (E): Cross 6R+4 p.79; Transfiguration 6R+4 p.450; Dormition Sunday Aug 16 4R+3+3 p.460 and Aug 17-22 6R+4 p.461; Entry 6R+4 p.114; Nativity Dec 26 4R+3+3 p.152; Theophany Jan 7 4R+3+3 p.179; Nativity Theotokos Sunday after 6R+4 p.70; Presentation Sunday after p.223. Ch.I p.11 says Nativity/Theophany **on Saturday** lose the first kathisma but "the hymns for the Resurrection are said and take precedence" (**Q**, contradicts p.174 for the eve of a Sunday Theophany). Gaps: Annunciation, Circumcision, Presentation, Elevation, Sep 8 on Saturday have no stated Sat-eve rule beyond the afterfeast-Sunday patterns (I).

## 3. Which feasts displace the Sunday Octoechos frame

| Class | Feasts | Evidence | Status |
|---|---|---|---|
| **Full** (no R stichera; Octoechos Sunday not sung) | Pascha cycle: Pascha, Palm, Thomas (to leavetaking of Thomas week, fn 290 p.503); Nativity of Christ; Theophany; Transfiguration; Elevation; Pentecost; Sunday-before-Nativity on Dec 24 | Ch.I p.12 (list), Ch.I p.11 (Palm/Thomas/Cross: kathisma recited, Res service omitted), p.75, p.143, p.173-174, p.449, p.504, p.538 | E |
| **Combined** (R kept, feast shares LIHC) | Nativity Theotokos 4R+6, Entry 4R+6, Dormition 4R+6, Presentation (6R+4 Typikon; ANCA 4R+6), Circumcision 4R+3+3, Annunciation Lent 4 (4R+6)/Lent 5 (6R+4 vs ANCA 4R+6)/Lent 3 (3R+3 Cross+4) | per-date orders above | E per date; the **class rule** (which feasts keep R) is not stated generally (I, Ch.V P3/P5 in #7); #15's `class` 1 = drops R matches the 4 Ch.I-listed Lord feasts only if Elevation/Transfiguration/Nativity/Theophany are class 1 (propagate and check) |
| **Frame kept, Triodion/Pentecostarion overlay** | Triodion Sundays, Myrrhbearers-Blind Man (7+3 or 4+3+3), Fathers Sunday after Ascension (3R+3 Ascension+4 Fathers p.536-538), All Saints (6R+4 p.540) | #8 | E |
| Not a Sunday | Ascension (Thursday), Pentecost leavetaking | | n/a |

Octoechos resume point: Lazarus Sat to Thomas leavetaking = no Octoechos (fn 290 p.503); Myrrhbearers (tone 2) resumes. Thomas leavetaking weekday: "Saturday" (Ch.I p.39 per #8), no slot list (M).

## 4. Fore-feast, afterfeast, leavetaking dates

The Typikon has **no feast table**. Dates come from Ch.V headings, Ch.XI Gloss. ("forefeast: 5 days Nativity, 4 Epiphany, others 1", p.575; katavasia schedule pp.576-577) and Ch.II p.42-43. Ascension/Pentecost leavetaking appear only in saint-coincidence notes (not slot lists).

| Feast | Forefeast | Afterfeast | Leavetaking | Cite |
|---|---|---|---|---|
| Nativity Theotokos Sep 8 | Sep 7 | Sep 9-11 | Sep 12 | p.63, p.71 |
| Elevation Sep 14 | Sep 13 | Sep 15-20 | Sep 21 | p.73, p.83; Gloss. |
| Entry Nov 21 | Nov 20 | Nov 22-24 | Nov 25 | p.110, p.116 |
| Nativity Dec 25 | Dec 20-24 (5 days; Dec 24 = paramon) | Dec 26-30 | Dec 31 | Gloss.; p.131, p.161 |
| Circumcision Jan 1 | none (Basil) | none | none | p.164; Jan 2-5 = Epiphany forefeast |
| Theophany Jan 6 | Jan 2-5 (4 days; Jan 5 paramon) | Jan 7-13 | Jan 14 (Sunday-case shifts with Triodion, p.190) | Gloss.; p.167-168, p.190 |
| Presentation Feb 2 | Feb 1 | Feb 3-8 | Feb 9 baseline; Triodion-dependent branches (Fri before Meatfare, Cheesefare Fri, etc.) | p.216-217, p.226-228 fn 143 |
| Annunciation Mar 25 | Mar 24 | Mar 26 (Gabriel) | Lent-grid dependent (e.g. Sat of wk 3, p.278; Fri eve of Lazarus Sat p.307; wk 4-6 weekdays p.283+) | p.277-324 |
| Transfiguration Aug 6 | Aug 5 | Aug 7-12 | Aug 13 | p.448, p.452 |
| Dormition Aug 15 | Aug 14 | Aug 16-22 | Aug 23 | p.453, p.463 |
| Palm Sunday | none | none (Holy Week) | none | |
| Pascha | none | Bright Week | Wed before Ascension (Pascha+38) | p.534-535; Gloss. |
| Ascension (Pascha+39) | none (Wed eve is Vespers of feast; Pascha leavetaking same Wed) | Fri-Wed | Friday (Pascha+47), per saint-coincidence notes only | p.382, p.395 |
| Pentecost (Pascha+49) | none | week of Pentecost | day **not stated** (Pascha+55 Saturday I) | p.401 note only |

## 5. ANCA check (key samples)

26 Saturday-eve `VESP.pdf` + 5 Sunday `Abbr.pdf` fetched (in scratchpad only). Verse counts per heading.

| Case | Date (Sat eve) | ANCA | Typikon | Result |
|---|---|---|---|---|
| Nat Theotokos on Sun | 2019-09-07, 2024-09-07 | 4R+6; Sat prokeimenon t6; readings; Apost R + Dox; trop R, feast x2 | 4R+6 p.66 | match |
| Entry on Sun | 2021-11-20 | 4R + 3 + 3 (two melodies), Dox Entry | 4R+6 p.113 | match |
| Dormition on Sun | 2021-08-14 | 4R+6; Dox Dormition | 4R+6 p.457 | match |
| Circumcision on Sun | 2022-12-31 | 4R+3 Circ+3 Basil; Dox Basil; theotokion R; trop R, Basil, Circ | p.165 | match |
| Presentation on Sun | 2020-02-01, 2025-02-01 | **4R+6**, Dox Presentation | **6R+4** p.218 | **MISMATCH** (2/2) |
| Annunciation Lent 5 Sun | 2018-03-24 | **4R+6**, Dox Annun, readings | **6R+4** p.304 | **MISMATCH** (1) |
| Palm Sun | 2020-04-11, 2026-04-04 | 10 Palm stichera; Dox; Sat prokeimenon t6; Apost Palm; trop Lazarus x2 + Palm | p.504 | match |
| Pentecost | 2020-06-06, 2026-05-30 | 4 (t1) + 6 (t2); Dox t8; Sat prokeimenon; 3 OT readings (2026); Apost t6; trop | p.538 | match |
| Pentecost Matins | 2026-05-31 Abbr | no evlogetaria (polyeleos), no "In that we have beheld", praises **4** stichera | praises "3 repeated" p.539 | partial (Q) |
| Palm Matins | 2026-04-05 Abbr | no evlogetaria, no "In that...", exaposteilaria "Holy is the Lord" | p.505 | match |
| Holy Sat Vespers | 2026-04-11 | 10 slots, 6R+4 Harrowing (heading layout ambiguous [?]) | 8 = 4R+4 p.516 | **probable mismatch** |
| Matins evlogetaria | 2019-09-08, 2020-02-02, 2021-08-15 Abbr | evlogetaria (tone 5) sung | not sung p.67, p.219, p.458 | mismatch (3/3); Circumcision (sung) matches p.165 |
| Praises | same 4 Abbr | 4R+4 feast | p.67-68 etc. | match |
| Sat Cross | 2019-09-14, 2024-09-14 | 6R+4 afterfeast; G Cross; Great Prokeimenon t7 | p.79 + Ch.I p.13 | match |
| Sat Transfiguration | 2022-08-06 | 6R+4; Great Prokeimenon t7 | p.450 | match |
| Sat Entry | 2020-11-21, 2026-11-21 | 6R+4 | p.114 | match |
| Sat Dormition | 2020-08-15, 2026-08-15 | 4R+3 Napkin+3 Dormition (heading order varies by year) | p.460 | match |
| Sat Nativity | 2021-12-25 | 4R+3 Nativity+3 Sunday-after; G Sunday-after, N Synaxis; Great Prokeimenon t7 | 4R+3+3 p.152 (N differs) | match counts; N differs |
| Sat Theophany | 2024-01-06 | 4R+3 Theophany+3 Synaxis; G Synaxis, N Theophany | p.179 | match |
| Sat Presentation | 2019-02-02 | 6R+4 afterfeast | p.223 | match |
| Sat Annunciation (wk 4) | 2023-03-25 | 4R+3+3; **G Annunciation** | 4R+3+3, **G Gabriel** p.289 | counts match; Glory owner differs; p.289 prints "9 stichera" (Q) |

Prokeimenon: Saturday t6 on every Sunday-feast eve above (Ch.I p.13 default); Great Prokeimenon t7 when a Lord feast falls on the Saturday (Cross, Transfiguration, Nativity, Theophany) but ANCA used the Saturday t6 for Annunciation on Saturday (Typikon p.11 treats Annunciation as a Lord feast too; I).

**No key:** Nativity Sunday (2022-12-25), Theophany Sunday (2019-01-06), Transfiguration Sunday (2023-08-06), Cross Sunday (2025-09-14), Pascha (index has files for 2020, 2024-2026 only; only Holy Sat 2026 checked), all weekday feast Vespers, Ascension Wed, Thomas/Fathers Sunday (not run). Sat 2019-01-05 and 2025-09-13 have only daily Orthros/Read (paramon/forefeast), no Great Vespers.

## 6. Missing / gaps

1. Menaion content for weekday/Saturday feast Vespers: Entry, Circumcision, Presentation, Transfiguration, Elevation, Annunciation outside the Lent grid (M).
2. Elevation: no weekday/Saturday order; Transfiguration Sunday Sat-eve has no slot list (M).
3. Palm Sunday Vespers day unstated (Q); Palm praises count unstated (M).
4. Ascension leavetaking and Pentecost leavetaking: dates only by inference; no slot lists; Ascension forefeast none (M).
5. General class rule for "feast keeps R" absent (I); Presentation counts conflict (E vs ANCA).
6. Litia/artoklasia/vigil structure for feasts: Ch.IV p.54 lists vigil dates (Sep 8, 14, 26; Nov 21; Dec 25; Jan 6, 17; Feb 2; Mar 25; May 8; Jun 24, 29; Aug 6, 15, 29; Ascension; patron). Circumcision and Pentecost not in vigil list (E).
7. Ch.I p.11 vs Ch.V p.174 on Saturday Nativity/Theophany (Q). Typos: Sep 12 N slot, p.220 count, p.289 "9", Kneeling Vespers "8".
8. ANCA absent where R is dropped on Sunday (4 dates); no ANCA for weekday Vespers (not indexed, #29 index is Sat/Sun only).

## 7. Recommendations

- Encode Sunday-feast Vespers as a per-feast table (res, feast1, feast2, glory_owner, now_owner) using sec. 2.1; do not derive from `class`. Lord-feast `drops_res` list from Ch.I p.12 is E; use it as the single displacement predicate (7 feasts + Dec-24 Sunday + Pascha cycle fn 290 range).
- Conflicts need a user call: Presentation Sunday and Annunciation Lent 5 follow Typikon (6R+4) or ANCA (4R+6)? ANCA is the check key, so unexplained mismatch blocks (map). Suggest log both on the Rule `conflicts` (#15.7) and prefer ANCA for the generator while ANCA is the answer key, since Presentation 2/2.
- Matins evlogetaria mismatch (3 Theotokos/Lord-on-Sunday cases) needs the same call; Matins is a separate slot group, not Vespers.
- Weekday/Saturday feast Vespers beyond sec. 2.2 needs Menaion data (ALWB Menaion day files, #26 workflow) rather than Typikon.
- File tickets: Ascension/Pentecost leavetaking dates (add Pascha+47/+55 as I), and ANCA fetch for Sunday-Res-drop feasts (Nativity, Theophany, Cross, Transfiguration) from other years or DCS (#10).
