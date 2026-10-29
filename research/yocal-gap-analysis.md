# yocal calendar gap analysis against rule inputs

Issue #12 (map #5). Research branch, throwaway, never merged. Planning only.

## Verdict

- Calendar core (Pascha, tone, eothinon, Nth-after-Pentecost, Matthew/Luke/John slots, Triodion/Pentecostarion Sunday names, Basil days) is **correct** in every sample checked. No blocking ANCA mismatch.
- yocal is a **lectionary + commemoration-text calendar**, not a service-rule input. It has no feast rank in the master DB, no structured fore/after/leavetaking, no Sunday-vs-feast precedence, no Sat-eve concept, no hymn data.
- Typikon already holds the explicit per-feast "if on Sunday" orders (e.g. Nov 1, pp.99-101). Those are the Rule source; yocal only supplies *which* day/feast/tone, and a few reading-precedence flags.
- 5 calendar doubts, all low/medium impact (see Doubts). None blocks Rules design.

## Sources and method

| Source | Use |
|---|---|
| `db/*.py`, `db/*.csv`, `db/0_yocal_scripts_explained.txt`, `db/build.sh` | what is computed, how |
| `db/yocal/YOCal.db`, `YOCal_Master.db` (main checkout; gitignored `*.db`, built by `db/build.sh`, 2000-2099, files dated Aug 11) | actual values, read-only sqlite3 |
| `api-php/lib.php`, `api/api.py` | what is exposed |
| ANCA key 2026-11-01 (given in issue) | answer key (only sample available; antiochian.org is a JS SPA whose service-text API needs a credential, not used) |
| GOA Digital Chant Stand (DCS) Matins pages, all 2026 Sundays | answer key; DCS has only 2026 (2020-2025, 2027 are 404) |
| OCA daily readings, Sundays 2025-2030 | secondary cross-check of tone/eothinon (Slavic; not authority) |
| Antiochian Typikon (local PDF, `pdftotext -layout`), cited by printed page (footer number) | rule authority; paraphrased only |
| Independent recompute (Meeus Pascha + cycle arithmetic), all Sundays 2001-2099 | internal consistency |

## What yocal provides

`yocal_main` (master DB, one row per date 2000-2099, 24 cols):
`date, day_name, day_num, ord, month, year, fast, tone, eothinon, desig_a, desig_g, major_commem, fore_after, basil, class_5, british, a_code, g_code, c_code, x_code, is_comm_apos, is_comm_gosp, hymn_key, explanatory_notes`.
Source tables in `YOCal.db`: `Menaion` (366 fixed-date rows: `major, class, fore_after, class_5, british, apostle, gospel, is_sun_*, is_wkdy_*`), `A_Lections`/`G_Lections`/`X_Lections`, `Pascha`, `Year_YYYY`, plus `Hymns` (3 placeholder rows) and `Menaion_Hymns` (3 rows, one date 06-11). No repo script builds those two hymn tables.

APIs (`api-php/lib.php::get_date_data`, `api/api.py::_get_date`, duplicated logic) expose: day_name, ord, month, year, fast, tone, eothinon, `liturgy` (Basil / "" / Chrysostom, derived), desig, commem, fore_after, global_saints (`class_5`), british_saints, lections {basic, commem, liturgy primary}. Not exposed: Menaion `class`, codes, tone-of-week on festal Sundays.

## Gap table

Legend: **Y** available as needed, **P** partial/ambiguous, **N** absent.

| Rule input | Status | What yocal has (where) | Gap |
|---|---|---|---|
| Tone of week, ordinary Sundays | Y | `tone` "Tone 1..8" (`7_tone_eoth.py`) | none; verified |
| Tone of week, Palm / Pascha / Thomas / Pentecost | P | literal "Tone of the feast" | No numeric. OCA lists Thomas T1, Pentecost T7. DCS Thomas Matins has Pentecostarion proper + Octoechos "mode of the week" 1. Rule needs explicit decision (Typikon p.11, p.33: Resurrection service omitted on Palm/Thomas) |
| Tone, Sunday that is Nativity/Theophany/Transfiguration/Elevation | P | "Tone of the feast" (hardcoded 4 date_keys) | Underlying week-tone dropped (OCA shows e.g. 2025-09-14 T5, 2028-08-06 T8; cycle continues correctly after). Consistent with Typikon p.11 (Resurrection hymns omitted) so likely intentional, but Saturday-eve / following-week rules may need the number |
| Eothinon 1-11 | Y | `eothinon` | verified vs DCS 2026 (46 Sundays) |
| Eothinon on Pascha, Palm, Pentecost, 9 feasts on Sunday | P | "Eothinon of the feast" | Typikon p.25 fn.18: NA Antiochian chants eothinon Gospel *and* feast Gospel on Theotokos feasts on Sunday; DB says "of the feast". Check vs ANCA. DCS Pascha shows Eothinon 7 (DB: of the feast) |
| Eothinon Thomas..Fathers (E1,4,5,7,8,10) | P | fixed seq in `7_tone_eoth.py` | matches DCS 2026; OCA differs for Myrrhbearers (E3) and Paralytic (E4). Typikon gives no numbers. Source = GOA, not ANCA: confirm with ANCA |
| Matthew / Luke / John cycle slot | Y | `desig_g`, `g_code` (`L5Sun`, `M12Sun`, `J2Sun`) | "Nth of Luke" is a **lectionary slot**, not a week count (see below) |
| Nth Sunday after Pentecost | Y | `desig_a`, `a_code` (`E22Sun`) | verified (2026: 17th=Sep 27; 2027 OCA numbering) |
| Fathers of 4th / 7th councils, Forefathers, Sun before/after Nativity/Theophany/Cross | Y | `desig_*`, codes `F4EC F7EC SFF SunBN SunAN SunBT SunAT SunBX SunAX` | Fathers of 6 councils (OCA 2027-07-18) not distinguished; Sunday desig lost (NULL) on Lord-feast Sundays |
| Triodion Sunday names (Publican..Palm) | Y | `desig_a` | verified 2026, 2027 dates |
| Triodion/Lent Saturdays | P | Lazarus Sat, Holy Sat, 1st Sat (Kollyva), "Soul Sabbath" on Meatfare Sat and Pentecost eve only | Lent Sat 2-4 not marked; Typikon text search found "Saturday of Souls" only for Meatfare and Pentecost eve; confirm vs ANCA |
| Pascha-relative movables (Palm, Pascha, Mid-Pentecost, Ascension, Pentecost) | Y | `desig_a`, `fore_after`; Pascha+38 Leavetaking of Pascha, Ascension afterfeast +40..46, leavetaking +47, Pentecost afterfeast +50..54, leavetaking +55 (`5_menaion_cycle.py:414-421`) | no Pascha afterfeast/Bright Week structure beyond day names; no leavetaking of Mid-Pentecost |
| Fasts | Y | `fast` free text; `season` only in Year tables, not master | text only; fast codes (f1..) in `6_fast_codes.py` not in master |
| Readings (Apostle/Gospel/extra) and Menaion-vs-Sunday reading precedence | Y | `a_code g_code c_code x_code is_comm_apos is_comm_gosp`; `lect_*` in `yocal_lections` | lectionary only. 1 deviation from Typikon (see Doubts) |
| Commemorations | Y (free text) | `major_commem` (1 per day), `class_5` (list of lesser saints, free text), `british` | text; no structure, no ordering; `class_5` is a name collision with Menaion `class`=5 |
| Feast rank / class | P | `Menaion.class` only in `YOCal.db`, **not in master**: `1`(4: Cross, Nativity, Theophany, Transfig) `2`(5: Presentation, Annunciation, Dormition, Nativity Theotokos, Entrance) `3`(34 great saints incl. Circumcision, Peter&Paul) `4`(29) `5`(1) `K`(4) `V`(1) `X`(13), 275 blank | No documented scale; K/V/X unexplained (used only for fast logic, `6_fast_codes.py:334-377`). Does not map to Typikon categories (Lord / Theotokos / great saint / polyeleos). Movable Major feasts (Palm, Asc, Pent) have no class. Circumcision = class 3, needs special-case |
| Twelve Great Feasts + Major feast flag | P | derivable: class 1+2 (9 fixed) + 3 movables by `desig_a` | no explicit flag; Circumcision not in 1/2 |
| Forefeast / afterfeast / leavetaking | P | `fore_after` free text, 69 fixed keys + Pascha-cycle (`5_menaion_cycle.py`) | one string per day, not structured (feast id, day n, role). Labels inconsistent ("of The Theophany" vs "of the Theophany"; Feb 3 "Entrance of the Lord"). Leavetaking of Theophany stored in `major_commem` (Jan 14), not `fore_after`. Only one slot/day. Meeting leavetaking shortened when Prodigal Son close (handled, `:388-410`) |
| Menaion vs Octoechos precedence (service level) | N | only `is_comm_*` (reading) and festal tone/eothinon | all stichera/canon/troparia combination rules are absent; Typikon has them per feast ("if on Sunday", e.g. Nov 1 pp.99-101: 6 resurrection + 4 saint stichera at Vespers etc.) |
| Sat-eve identification | N | Saturday row has own desig (e.g. "Saturday before the Theophany", Soul Sabbath) | no link Saturday->Sunday; derive Sunday = date+1; Saturday-Great-Vespers needs Sunday's tone + feast |
| Basil/Chrysostom day flag | Y | `basil` ("Liturgy of St Basil"); API `liturgy` | rule matches Typikon list; API field mixes 3 states, and `liturgy_allowed()` name is inverted (true = *no* liturgy). See below |
| Hymn / variable-part data | N | placeholders only | out of scope by map |
| UK divergences | Y | `british` free text, class_5 transfer notes | log needed (map) |

### Basil flag (checked)
Set in `4_paschalion_cycle.py` end: Lent Sundays 1-5 (`G1Sun..G5Sun`), Holy Thu, Holy Sat, Jan 1 (any weekday), Nativity/Theophany Eve if Mon-Fri, Nativity/Theophany if Sun or Mon. Checked: 2022-12-25 (Sun) Y, 2025-01-06 (Mon) Y, 2022-12-24 (Sat) N, 2026/2027 lists, Annunciation on Lent Sundays (2029, 2035, 2040) Y. Consistent with the Typikon Lenten-Sunday order (Mar 9 section, ~p.267: rest of the Liturgy is St. Basil's).

### "Nth of Luke" is a slot label
Luke 1 starts Monday after Sunday after Elevation. Sundays are then assigned from three fixed series chosen by the date of Sunday-after-Elevation (`4_paschalion_cycle.py` series_1..3): L4 sits on Oct 11-17 (also Fathers of 7th Council), L5 on Oct 30-Nov 5, L13/L14/L10/L11 reordered in Nov-Dec. So 2026-10-11=4th, 10-18=3rd, 10-25=6th, 11-01=5th of Luke. 11-01 = 5th matches ANCA key. Rules must key on `g_code`, never compute "Sunday n after the Cross".

## Sample verification

### 2026-11-01 vs ANCA key: all match
`tone` Tone 5, `eothinon` Eothinon 11, `desig_a` 22nd after Pentecost, `desig_g` 5th of Luke, `major_commem` Cosmas and Damian of Asia Minor, `c_code` 11-01, `is_comm_apos`=1, `is_comm_gosp`=0. DCS 2026-11-01: Mode pl.1 (=T5), Eothinon 11. Typikon pp.99-101 (Nov 1 on Sunday): saints' Epistle with Sunday Gospel, matches the two `is_comm_*` flags. UK divergence: `british` lists 7 Welsh/British saints (not in ANCA); `class_5` has extra saints (Theodota, James of Prodromou...). Record in divergence log.

### Tone / eothinon, all Sundays checked
| Check | Coverage | Result |
|---|---|---|
| DCS Matins 2026 | 52 Sundays; 39 tone + 46 eothinon comparable (4 pre-Lent pages are empty stubs, Palm/Pentecost festal) | 0 mismatches except Pascha eothinon (DCS reads E7, DB "of the feast") |
| OCA 2025-2030 | ~210 Sundays tone, ~200 eothinon | 0 mismatches except: Thomas (OCA T1), Pentecost (OCA T7), Lord feast on Sunday (OCA keeps week-tone), Myrrhbearers/Paralytic eothinon (OCA E3/E4 vs DB/DCS E4/E5) |
| Own recompute, 2001-2099 (5,165 Sundays) + Pascha 2000-2099 | all | 0 mismatches (Meeus Pascha equals `Pascha` table all 100 years). Only tests internal consistency |

### Pascha-centred spot checks
- 2026: Pascha Apr 12; Lent 5 Mar 29 (T1 E9); Palm Apr 5; Thomas Apr 19 (E1); Myrrh Apr 26 T2 E4; Paralytic T3 E5; Samaritan T4 E7; Blind T5 E8; Fathers May 24 T6 E10; Leavetaking of Pascha Wed May 20; Ascension Thu May 21; afterfeast May 22-28; leavetaking Fri May 29; Soul Sabbath May 30; Pentecost May 31; leavetaking Sat Jun 6; All Saints Jun 7 T8 E1; 2026 Luke 1 Sep 27 = 17th after Pentecost. All consistent with DCS/OCA.
- 2027: Pascha May 2 (OCA agrees), Palm Apr 25, Thomas May 9 (E1), Ascension Jun 10, Pentecost Jun 20, All Saints Jun 27 (T8). George/Mark/John transfers behave (George moved to Bright Monday May 3; Mark on Palm Sunday reduced to class 5; John on Bright Sat unmoved).
- Triodion Sundays 2026 (Feb 1-Apr 5) and 2027 (Feb 21-Apr 25) names/tones correct (OCA 2027, OCA+DCS partial 2026).
- Great feast on Sunday: Dormition 2027-08-15 (T7, eothinon of feast, both readings feast), Entrance 2027-11-21, Presentation 2025-02-02 (T7) and on Publican Sunday 2031-02-02 (feast Epistle, Sunday Gospel, matches Typikon p.37), Annunciation on Lent Sundays 2029/2035/2040 (Basil; both feast readings), Nativity 2022-12-25 and 2033-12-25, Theophany 2030-01-06, Transfiguration 2023-08-06 and 2028-08-06, Elevation 2025-09-14. No Sunday collisions exist in 2026 (DCS cannot confirm any); verified vs Typikon logic and OCA tone only.

## Doubts (ranked)

1. **Annunciation on 3rd Sunday of Lent**: DB sets both feast readings (`is_comm_apos`=1, `is_comm_gosp`=1) (2063, 2074; none before 2060). Typikon p.37: Epistle of Sunday, Gospel of Annunciation. Low impact (outside published years). 
2. **Thomas / Pentecost tone and eothinon of Theotokos feasts on Sunday**: "of the feast" strings vs OCA/DCS numeric. Needs ANCA to settle which the answer key uses.
3. **Myrrhbearers/Paralytic eothinon (E4/E5)**: matches DCS (GOA), not OCA (E3/E4). ANCA unchecked.
4. **Data hygiene**: Leavetaking of Theophany in `major_commem`; Feb 3 afterfeast label differs; Sunday `desig` NULL on 4 Lord-feast Sundays.
5. **API**: `liturgy_allowed()` returns True when there is *no* liturgy; Basil only via `basil` column; logic duplicated in PHP and Python.
6. Not a bug: Typikon p.190 moves Theophany leavetaking off a Sunday to Sat Jan 13 only if Triodion has begun; with Pascha >= Apr 4 (Gregorian) this never happens, DB ok.

## Missing from yocal, needed by Rules (ticket candidates)

1. Rank taxonomy that maps to Typikon categories; export `class` to master; document K/V/X.
2. Structured feast-cycle table (feast id, role forefeast/afterfeast/leavetaking, day n, leavetaking date incl. movable overlaps).
3. Sunday/feast coincidence matrix (Sunday vs Lord / Theotokos / great saint / Triodion / Pentecostarion): source = Typikon per-feast "if on Sunday" orders (e.g. pp.11-13, 25-26, 33, 37, 39, 99-101). Not in yocal at all.
4. Numeric week-tone on festal Sundays + Thomas/Pentecost; decision record.
5. Sat-eve mapping and per-service day model (Great Vespers = Saturday evening, uses Sunday row).
6. Major-feast flag including Circumcision and 3 movables; Soul Saturdays 2-4 of Lent decision.
7. ANCA comparison for the 5 doubts above (need ANCA service-text access; only the 2026-11-01 key was available here).

## Not verified

- ANCA key beyond 2026-11-01; DCS years other than 2026; DCS Feb 2026 pre-Lent Matins pages are empty stubs.
- Sat-eve Great Vespers content (DCS/ANCA vesper pages not located).
- Typikon read only for the passages cited; no full audit of its Sunday-coincidence tables.
- Worktree has no built DBs; all queries used main checkout `db/yocal/*.db` (not rebuilt here; assumed built from current scripts).
