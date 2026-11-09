# Why the Principal + Bp Basil glory prediction missed ANCA (8 dates)

Issue #34 (map #5). Paraphrased; no PDFs/long excerpts committed. Cites: "Typikon p.NN" = printed page (Antiochian Typikon, Khoury/Morris 2011); "Bp Basil" = Parish Typikon charts (dowama.org; Chart II, Ranking of Feasts); "ALWB" = AGES Menaion day files (GR `cog` flags, EN names); "ANCA" = AOCANA Saturday Vespers PDFs (answer key). Status tags: **EXPLICIT** / **INFERRED** / **MISSING**.

## 1. Answer

- The "8 + 3" are one set: 8 unique dates (the 3 ALWB-glory dates are inside the 8; the 4th ALWB-glory date is 2021-02-14). Split: 4 ALWB glory / ANCA 7R+3; 3 neither / ANCA 6R+4; Xenia.
- #32 per-commemoration (main/alt) rule changes nothing: every one of the 8 date keys has a single ALWB `main` block (no alt), so predictions are identical, 104/112 stands.
- No Typikon Ch.V entry exists for any of the 8 Sundays. Only Oct 26 (Saturday-feast case, pp.97-98) is relevant and it is a real Rule gap (2024-10-27).
- Classes: 1 Rule gap + ANCA variance (2024-10-27), 3 ANCA variance (2020-09-27, 2021-02-14, 2023-07-23), 1 wrong Principal (2022-07-10), 2 data gap / ANCA-only doxastikon (2022-08-28, 2024-01-21), 1 saint substitution (2021-01-24). No Bp Basil extraction error found.
- Residual ANCA variance is ~4/70 (6%) of ALWB-glory dates. No available feature separates them; log as Divergence class, not fix.

## 2. Table

Pred = Principal + Bp Basil (ALWB glory OR rank-implied). BpB = Bp Basil rank string for the Sunday's date (Chart II: plain Simple = 7+3; Simple with 2 doxastika = 6+4). ANCA doxastikon = saint's own "Glory" hymn present at LIHC in the key PDF.

| Sunday | Principal (ALWB main) | Pred | ANCA | BpB | Evidence | Class |
|---|---|---|---|---|---|---|
| 2020-09-27 | Callistratus | 6R+4 | 7R+3 | Simple, no 2 Glories | ALWB GR glory=1 (EN=0). ANCA 2020 3 stichera, no doxastikon; ANCA 2026 same key (Sat Sep 26, 6R+4) includes Callistratus doxastikon. Typikon Sep 26 (pp.90-91) = John Theologian, "Saturday: Menaion order", nothing for Sep 27 | ANCA variance (year-variant, known mixed key) |
| 2021-02-14 | Auxentius | 6R+4 | 7R+3 | Simple, "Venerable 3 stichera" | ALWB GR+EN glory=1. ANCA: 3 stichera, no doxastikon. Single observation. No Typikon entry | ANCA variance |
| 2023-07-23 | Phocas (Sinope) | 6R+4 | 7R+3 | Simple (Parakletike 3 + Hieromartyr 3) | ALWB GR+EN glory=1. ANCA: 3 stichera, no doxastikon (Sat Jul 22 = Mary Magdalene, no Typikon entry). Single observation | ANCA variance |
| 2024-10-27 | Nestor | 6R+4 | 7R+3 | Simple (Leavetaking 3 + Martyr 3) | Oct 26 on a Saturday: Typikon Ch.V pp.97-98 gives explicit order: 6 Res + 4 Nestor, Glory = Demetrius (Sunday vespers part). ANCA 2019 (also Sat Oct 26) followed it: Demetrios afterfeast + doxastikon, 6R+4. ANCA 2024 dropped Demetrios, Nestor only, 7R+3. Our 6R+4 matched Typikon only by coincidence (Nestor ALWB glory) | Rule gap (Saturday-feast combo unmodelled) + ANCA variance (2024 deviates from Typikon) |
| 2022-07-10 | 45 Martyrs Nikopolis (no glory) | 7R+3 | 6R+4 | Simple for 45 Martyrs; Joseph of Damascus listed only under Bp Basil "Phyllada" (local) as Polyeleos | ANCA Sat Jul 9 principal = Joseph of Damascus, with doxastikon at LIHC + aposticha. Typikon Ch.V (p.429 fn 232, editor's note) says Joseph of Damascus is celebrated Jul 10. ALWB has no Joseph block | Wrong Principal (ALWB lacks Antiochian saint) -> override, cited Typikon fn 232 + Bp Basil Phyllada |
| 2022-08-28 | Moses the Ethiopian (no glory) | 7R+3 | 6R+4 | Simple (Parakletike 3 + Venerable 3) | ANCA has Moses doxastikon at LIHC and aposticha; ALWB GR and EN lack it; no Typikon entry; Bp Basil shows no 2 Glories | Data gap in ALWB (Greek-only source); ANCA-only evidence, cannot justify override |
| 2024-01-21 | Maximus Confessor (no glory) | 7R+3 | 6R+4 | Simple (Confessor 3 + Martyr 3) | ANCA has Maximus doxastika (LIHC + aposticha); ALWB lacks; Bp Basil none; no Typikon entry (Sat Jan 20 Euthymius Ch.V is Sunday-only) | Data gap in ALWB; ANCA-only |
| 2021-01-24 | Xenia of Rome (no glory) | 7R+3 | 6R+4 | Simple (Parakletike 3 + Venerable 3) | ANCA sings Xenia of St Petersburg (own stichera + doxastikon at LIHC and aposticha). yocal/ALWB = Xenia of Rome | ANCA variance / saint substitution; Divergence log (already logged in #31) |

## 3. Cross-checks

- **Bp Basil does not veto ALWB glory.** Chart II footnote: a Simple saint with two doxastika (LIHC + aposticha) on Sunday is 6+4; plain Simple is 7+3. Test over the 112 dates: ALWB glory with Bp Basil plain Simple (7R+3): ANCA 6R+4 in 17, 7R+3 in 4 (the four misses). Using Bp Basil Simple as a veto would fix 4 and break 17. ANCA follows Typikon p.12/p.48 (a doxastikon => 6+4), not Bp Basil's two-doxastika wording. INFERRED from key.
- **No discriminating ALWB feature.** For ALWB-glory dates, EN flag 1: 32 glory / 3 none; EN flag 0: 34 glory / 1 none; alt block present or not makes no difference. ALWB aposticha glory is not in the data (no `meAP` glory keys), so the Bp Basil two-doxastika test cannot be run on ALWB.
- **Same-key year variance.** 09-27 (2020 7R+3, 2026 6R+4), 10-27 (2019 6R+4, 2024 7R+3) are the mixed keys from #31; 02-14 and 07-23 have one observation each. Doxastikon exists in the ANCA corpus for Callistratus (2026) and Demetrios; compilers sometimes omit it.
- **Bp Basil extraction (`ranks.csv`).** The 07-10 row is SIMPLE because the extractor skips the "Phyllada" section (Joseph of Damascus, Polyeleos, and Kirykos/Julitta Jul 15, Doxology). Intentional (optional local vigils), and a candidate independent cite for the Joseph override. No other extraction error found for the 8 keys.
- **Typikon Ch.V.** Searched for all 8 saints and for the Saturday dates (Sep 26, Feb 13, Jul 9/22, Aug 27, Jan 20/23, Oct 26). Only Sep 26 (pp.90-91, John Theologian: 4R+6 on Sunday, "Menaion order" on Saturday), Oct 26 (pp.97-98), Jan 20 (p.199, Sunday case only) and the Jul 10 note exist. None states glory for the 8 saints.

## 4. Conclusion

Principal-order logic is sound: only one miss is a wrong Principal (Joseph of Damascus), and one is a missing Rule (Saturday-feast combination, Oct 26). The rest are irreducible with available sources: ANCA omits/adds a doxastikon relative to the Greek Menaion (4 omit, 3 add). ~93% is close to the ceiling for an inferred Rule.

## 5. Recommended changes

1. Override (cited, #28 step 1): 07-10 Principal = Joseph of Damascus, glory true, cite Typikon p.429 fn 232 + Bp Basil Phyllada (Polyeleos). Review other Phyllada dates (Jul 15 Kirykos/Julitta, etc.) as override candidates.
2. Rule: Saturday-feast combination for Oct 26 (explicit, Typikon pp.97-98): Sunday vespers 6R+4, Glory = Demetrius. Add to the explicit-list tier above ALWB glory. Check Sep 26 and other Ch.V entries with a "Saturday" branch for similar rules (Sep 26 Saturday = Menaion order, no Sunday-vespers effect found). Harness: ANCA 2024 deviation from the explicit Rule = non-blocking, Divergence log (ANCA 2019 follows it).
3. Divergence log class "ANCA omits/adds Menaion doxastikon vs Greek Menaion" for 2020-09-27, 2021-02-14, 2023-07-23 (omit) and 2022-08-28, 2024-01-21 (add). Non-blocking, per-date-key variant audit (as #32).
4. Do not use Bp Basil Simple as a negative glory signal (17 vs 4). Keep "Bp Basil adds evidence only".
5. Keep Xenia in the Divergence log (Rome vs St Petersburg).
6. Data follow-up (optional): ALWB aposticha glory is absent; if needed for Matins/aposticha Rules, source from another library.

Data: `prototypes/principal-glory/out.csv`, `prototypes/anca-compare/compare.csv`, `prototypes/alwb-menaion/menaion_commems.csv`, `prototypes/bpbasil-rank/ranks.csv` (untracked).
