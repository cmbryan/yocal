# PROTOTYPE (throwaway, never merge): Rule schema + ANCA harness spike

Question: does the YAML Rule schema (slot-grain Rules, specificity tiers, closed context facts,
provenance status) plus an ANCA comparison harness hold up on real data?

Run: `python spike.py --from 2019-06-30 --to 2026-11-22 [--cache DIR] [--detail YYYY-MM-DD]`
(needs PyYAML, `pdftotext`, `db/yocal/YOCal_Master.db`; ANCA PDFs fetched to `--cache`, never committed).
`gen_ch5_rules.py` generates 59 per-date Sat-Vespers LIHC Rules from the Typikon Ch V research table
(needs `origin/research/typikon-menaia-structure`).

Slice: ordinary post-Pentecost Sundays (Sat Great Vespers, Sunday Matins, Sunday Liturgy); 106 Sundays 2019-2026.
11 slots, 13 hand rules + 59 generated; ANCA key = `Abbr.pdf` (Vespers/Matins) + `READ.pdf` (Liturgy).

## Results (run 2026-11-06)

Schema/harness held: 72 rules loaded, 0 schema errors, 0 tier ties, 106/106 dates keyed, zero redesign needed.
Every cell resolves to explicit / inferred / missing and compares to the key.

| Slot | explicit/inferred match | diff | missing (no usable Rule) | not in key |
|---|---|---|---|---|
| vespers.prokeimenon | 106 | 0 | | |
| matins.eothinon, matins.kathismata | 106 / 102 | 0 | | 4 |
| matins.praises | 68 | 0 | 38 | |
| matins.prokeimenon | 6 | 0 | | 100 (older Abbr omit it; use ORTHROS file) |
| vespers.lihc.stichera | 30 | 1 | **75 (71%)** | |
| liturgy.kontakion | 45 | 2 | **59 (56%)** | |
| liturgy.epistle / gospel | 102 / 100 | 4 / 4 | | 2 |
| liturgy.prokeimenon (inferred) | 103 | 3 | | |
| liturgy.alleluia | | | | 106 (key prints no verses) |

## Findings

1. **Biggest gap is a calendar fact, not a Rule.** 71% of Sat-Vespers LIHC cells have no Rule because
   `saint_has_glory` cannot be derived from yocal (`major_commem` non-empty does not predict it:
   key splits on those dates are 6R+4 x35, 7R+3 x29, 4R+3+3 x10, regardless). Needs Menaion class data (as #12 said).
   The 7R+3 vs 6R+4 rule is explicit in the Typikon; only the input is missing.
2. **Typikon Ch V per-date table works as top-tier Rules** (generated, 59 rules): 30/31 keyed dates match.
   One diff: Sep 24 2023 (Typikon 6R+4, ANCA 4R+3+3).
3. **Kontakion seasonal windows**: Typikon window Sep 22-Nov 8 only. Key shows more windows needing Rules:
   July Sundays "O undisputed Intercessor" t2 (19 of 28), Transfiguration t7 (Aug), Entrance t4 and
   Preparation of Christmas t3 (late Nov/Dec). **Nov 8 diff x2 (2020, 2026): ANCA uses Entrance kontakion**, so the
   window end in the Typikon rule is probably wrong (or a boundary meaning). Evidence-backed candidate Rule error.
4. **Calendar vs key readings**: saint's Epistle not flagged in calendar (Nektarios 2025-11-09; 2022-07-10),
   one reverse (2021-07-04), a verse-range difference (Romans 5:1-10 vs 5:1-11, 2022-07-03). Ref notation
   differs (`12:16-21,8:8` vs `12:16-21`; `,` vs `;`): needs a ref normaliser and Divergence-log class.
5. **Key owner marker is unreliable**: apostle-feast Epistles print no "(For ...)" subtitle, so Epistle owner must
   be checked via the reference, not the subtitle.
6. **Prokeimenon follows Epistle owner (inferred)**: 103 matches, but the key shows the owner only via the Epistle,
   so this check is circular; only the prokeimenon *text* could verify it.
7. **Key source per slot**: Abbr (Vespers/Matins counts) is not enough for Matins prokeimenon on older dates;
   harness must pick Abbr vs ORTHROS per slot. Parser needs wording tolerance (stichera/troparia, case).
8. Spike limits: slice only (no Triodion/Pentecostarion/feasts), 11 slots, no hymn refs, no UK strip run,
   coarse slice windows, parser is regex on text-PDFs.
