# PROTOTYPE (throwaway, never merge): rule-coverage audit over the full ANCA range

Question: measured coverage + unexplained diffs of the Rule set vs the ANCA key over all Sundays (Sat Great Vespers, Sun Matins, Sun Liturgy), incl. Triodion/Lent/Pentecostarion/Major-feast weekends.

Run: `python audit.py --cache DIR` -> `audit.csv` (date x slot: class, rule, status, result, detail, key). Needs `pdftotext`, `db/yocal/YOCal_Master.db`, local `../anca-compare` (Matins/Liturgy keys), `../principal-glory/out.csv`, `../anca-index/pages.json`. Rules are Python stubs mirroring decided tickets (YAML schema validated in `../rule-spike`). Only decided + encodable Rules are encoded; the rest count as *missing (not encoded)*.

Range 2018-02-18..2026-11-22: 412 Sundays, 10 slots, 4120 cells; 400 Sat Vespers keys (12 absent/non-standard files).

## Result (run 2026-11-09)

Keyed cells 3715; Rule encoded for 2794 (75%); match 2700 (96.6% of encoded); diff 94.

| context class | Sundays | keyed cells | with Rule | match | diff |
|---|---|---|---|---|---|
| ordinary (post-Pentecost) | 160 | 1530 | 91% | 1343 | 55 |
| named Sunday (Fathers, Forefathers, pre/post feast Sundays) | 31 | 272 | 81% | 192 | 30 |
| fore/after-feast | 64 | 583 | 67% | 388 | 5 |
| lent | 42 | 389 | 68% | 265 | 0 |
| triodion | 32 | 290 | 66% | 193 | 1 |
| pentecostarion | 53 | 397 | 54% | 216 | 0 |
| all saints | 9 | 82 | 60% | 49 | 1 |
| Major feast: eve Sat | 11 | 95 | 32% | 30 | 1 |
| Major feast: on Sunday | 7 | 60 | 35% | 20 | 1 |
| Major feast: movable (Palm, Pascha, Pentecost) | 3 | 17 | 23% | 4 | 0 |

Per slot: missing Rules (no_rule): liturgy.kontakion 354/412 (only Sep22-Nov7 window encoded), matins.kontakion 220 (only default resurrectional), vespers.lihc 261 (glory model only ordinary/named), vespers.aposticha 24, vespers.prokeimenon 12, matins.eothinon 21, matins.prokeimenon 26 (feast Sundays, no tone).
Slots at ~100% match once encoded: vespers.prokeimenon 265/265, vespers.aposticha 265/265, matins.eothinon 381/381, matins.prokeimenon 333/334, liturgy.rite 408/409, liturgy.gospel 403/409, liturgy.epistle 341/354.

## The 94 diffs, triaged (none new blocking except two)

- matins.kontakion x43 (ordinary 15, named 28): ANCA non-resurrectional kontakion = Theotokos/feast/saint override rules of #27, not encoded here. Gap, not error.
- vespers.lihc x30 (ordinary/named): 4R+6 / 4R+3+3 / 6R+4 variance and glory misses; #31/#32/#34 (4R+6 flag not wired into this run; 92/122 = 75% vs 93% in-scope-only in #31, because named Sundays + 4R+6 included).
- epistle x13: saint's-Epistle ownership (Acts 11:19-30 Barnabas x5, Nektarios, Joseph) and Zacchaeus/Blind-Man order: #35 known.
- gospel x6: pre-Triodion order (3, #35), 2022-11-20 ANCA transfer (#35), 2023-03-26 range 9:17-31 vs 9:16-30, 2024-01-14 Sun after Theophany range.
- matins.prokeimenon x1: 2022-11-20 (#35 transfer).
- **liturgy.rite x1 (2018-03-25): Annunciation on Lent Sunday -> ANCA Chrysostom; Basil-on-Lent-Sundays Rule needs an Annunciation exception. Candidate Rule gap.**
- **Stub error found and fixed during run: "Basil on Sunday eve of Nativity/Theophany" (3/3 ANCA = Chrysostom on the Sunday; vesperal Basil is a separate service).** #19 wording ("etc.") was ambiguous; Rule must say Sunday morning Liturgy is Chrysostom.

## Findings

1. Parse/compare artefacts were the largest "diff" source until fixed: epistle/gospel ref notation (calendar lists alt verses `12:16-21,8:8`), numbered-book names, Vespers heading variants (`O LORD I HAVE CRIED` w/o comma), 12 absent VESP files. Harness needs a ref normaliser + Divergence-log class `ref-notation`.
2. Context classes overlap (Annunciation eve on a Lent Sunday): single-label class broke the Basil Rule. Rules need multi-label context facts (season x feast-day flag).
3. Glory/LIHC model is not valid in fore/after-feast scope (11/54 match); kept as missing, not inferred.
4. Coverage cliff: Major-feast weekends 23-35% and Pentecostarion 54% -> these are where rule research (#36) + gap decisions (#38) must land before the generation script.
5. Pentecostarion Vespers aposticha/prokeimenon are seasonal (Thomas Sunday etc.), absent from the Ordinary frame; key for older Pascha-cycle Vespers often has no prokeimenon.
6. `not_in_key` is large for Vespers prokeimenon (126): ANCA VESP files omit/relabel the heading; harness should treat as a parser gap per slot, not a Rule signal.
