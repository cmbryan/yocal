# Sunday Liturgy kontakion: windows and rules (issue #25)

Question: spike Rule `lit.kontakion.undisputed` uses window Sep 22 - Nov 8; ANCA key uses Entrance kontakion on Nov 8 (2020, 2026). Other ANCA windows unmodelled: July (O undisputed Intercessor t2), Transfiguration t7, Entrance t4, Preparation of Christmas t3. What are the correct windows, with sources?

Status labels: **explicit** = source states it; **inferred** = from ANCA key (evidence given); **missing** = no source, no key evidence.

## Answer

1. **Nov 8 is the first day of the Entrance kontakion, not the last day of the undisputed window.** Undisputed window ends **Nov 7 inclusive**. Violakis is unambiguous ("from 8 November", §40, pp. 32-33). Typikon is ambiguous ("between ... and November 8th" then "From November 8th", p. 35). Key: Nov 7 2021 undisputed, Nov 8 2020/2026 Entrance. Fix = explicit (Violakis) + corroborated by key.
2. **Source for Liturgy kontakion is the fixed "Kontakia chanted during the Divine Liturgy" schedule, which applies to Sundays too.** It is a date-window table (Typikon Ch I s6 V, pp. 35-37; Violakis §40, pp. 32-33). The Sunday "Octoechos kontakion" text (Typikon p. 28 s.X; Violakis §26, p. 21) is the **Matins** 6th-ode kontakion, not Liturgy. So no "Sunday exception": ANCA Sunday Liturgy follows the schedule on all sampled dates.
3. Spike rule `lit.kontakion.other` (missing) is replaced by the window table below. Only 3 small gaps remain (marked).

## Method

- Typikon: `pdftotext -layout Typikon.pdf`; page = printed page (footer "Back to Table of Contents N" ends page N).
- Violakis 1888: local scan, user's translation `Violakis/translation.md` §40 (pp. 32-33), §26 (p. 21). Transcribed-as-printed; fix #3 below is not an emendation.
- Key: ANCA `<date> READ.pdf` ("Liturgy Variables") for every Sunday 2019-01-06 .. 2026-11-22 (412 dates, 28 not found by date filename; see #9). Kontakion heading parsed from each. Throwaway script, not committed. Window rule coded from this note and diffed against the key.
- Result: **356 Sundays compared in ordinary time + Triodion/Pentecostarion/Nativity cycle, 0 diffs for the windows below** once the Nov 8 fix and the 3 inferences below are applied. Without the Nov 8 fix: exactly 2 diffs (2020-11-08, 2026-11-08). Key paraphrased only; no key text committed.

## Window table (Sunday Liturgy kontakion, ordered by calendar)

Fixed dates assume the Menaion cycle: leavetaking (apodosis) = Typikon/Violakis feast-end days (Cross Sep 21; Entrance Nov 25; Theophany Jan 14; Presentation Feb 9; Transfiguration Aug 13; Dormition Aug 23; Nativity Theotokos Sep 12; Nativity Dec 31). Leavetaking dates are not restated in the kontakion section; taken from the Typikon feast tables (explicit elsewhere in Ch. V). Not re-verified here.

| Window | Kontakion (tone) | Source | Status | Key evidence (Sundays hit) |
|---|---|---|---|---|
| Sep 1 | Indiction (4) | Typikon p. 35; Violakis §40 | explicit | 2019, 2024: match |
| Aug 24 - Sep 12 (Dormition leave to Nativity-Theotokos leave); Sep 7 forefeast "Today the Virgin and Theotokos Mary" | Nativity of Theotokos (4) / forefeast (3) | Typikon p. 37; Violakis §40 | explicit | 17 Nativity, 1 forefeast: match |
| Sep 13 | Dedication / Holy Resurrection Church (4) | Typikon p. 35; Violakis §40 | explicit | 2020, 2026: match |
| Sep 14 - Sep 21 | Exaltation of the Cross (4) | Typikon p. 35; Violakis §40 | explicit | 6: match |
| **Sep 22 - Nov 7** | O undisputed Intercessor, "ordinary" (2) | Typikon p. 35 + Violakis §40 | explicit (end date fixed per above) | 40 distinct dates Sep 22..Nov 7: match; Nov 7 2021 undisputed |
| **Nov 8 - Nov 24** (leave of Entrance is Nov 25) | Entrance (4) "The all-pure Temple" | Typikon p. 35 ("From November 8th to the leavetaking"); Violakis §40 | explicit | 20: match incl. Nov 8 2020/2026 |
| Nov 20 (forefeast) | Forefeast of Entrance (4) "Today the whole world" | Typikon p. 35; Violakis §40 | explicit | 2022-11-20: match |
| Nov 26 - Dec 24 | Preparation of Christ's Nativity (3) "Today the Virgin cometh" | Typikon p. 36 says until **forefeast** of Nativity; Violakis §40 says until the **eve** | explicit (Nov 26 - Dec 19); **Dec 20-24 inferred** | 29 Sundays Nov 26..Dec 24 match, 5 of them Dec 20-24 (2019, 2020, 2023, 2024, 2025) |
| Dec 9 | St Anna (2) | Typikon p. 36 | explicit | none sampled (no Sunday Dec 9 2019-2026) |
| Dec 25 - Dec 31 | Nativity (3) | Typikon p. 36 | explicit | match |
| Jan 1 / Jan 2-5 / Jan 6-14 | Circumcision / Forefeast Theophany / Theophany (4) | Typikon p. 36 | explicit | match |
| Jan 15 - Feb 9 (Feb 1 forefeast) | Presentation (1) / forefeast (4) | Typikon p. 36 | explicit | match, incl. Publican Sun 2020-02-09, 2025-02-09 and Prodigal Sun 2026-02-08 (see below) |
| Triodion Sunday, date after Feb 9 | Triodion kontakion | Typikon p. 36 + fn 27 ("if leavetaking ... celebrated") | explicit; boundary Feb 9 itself still Presentation is **inferred** (key: Feb 9 2020, 2025; Feb 1/8 2026 all Presentation) | 3 inferred-boundary dates |
| Feb 10 - day before Publican | O undisputed (2) | none (Typikon silent) | **inferred** | 2019-02-10, 2021-02-14, 2024-02-11/18: all undisputed |
| Lent Sun 1-5 | "To thee the Champion Leader" (8) | Typikon p. 36 | explicit | all 5th-Sun diffs below |
| Lent 5th Sunday, **if Annunciation before Akathist Saturday** (derived: Pascha-15 days later than Mar 25 Gregorian) | O undisputed Intercessor (2) instead | Typikon p. 36; Violakis §40 fn/p. 33 | explicit | 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026: 8/8 undisputed |
| Pascha .. Pentecostarion | Pascha (8); Ascension (6) P+39..P+46 (hits 8/8 on P+42); Pentecost (8) P+49..; All Saints (8) P+56 | Typikon p. 36; Violakis §40 | explicit; see Typikon error below | match (coarse) |
| **P+57 (after All Saints) - Jul 26** | O undisputed Intercessor (2) | Typikon p. 36 ("from beginning of Fast of Apostles to July 27"); Violakis: "thereafter [after All Saints] until 27 July" | explicit | 29 distinct dates Jun 14..Jul 26: match |
| Jul 2 | "A garment of incorruption" (Robe) (2) | Typikon p. 36 ("2nd and 25th of July ... kontakion of the day"); Violakis §40 | explicit | 2023-07-02: match |
| Jul 25 | St Anna / Forebears of Christ (2) | same | explicit | 2021-07-25: match |
| **Jul 27 - Aug 13** | Transfiguration (7) | Typikon p. 36; Violakis §40 | explicit | 19: match (earliest Jul 27, latest Aug 13) |
| Aug 1 on Sunday | Transfiguration (7) (not Cross, which is the non-Sunday rule) | Typikon p. 36; Violakis §40 | explicit | no Sunday Aug 1 sampled 2019-2026 |
| Aug 14 forefeast / Aug 15 - Aug 23 | Forefeast Dormition (4) / Dormition (2) | Typikon p. 36-37; Violakis §40 | explicit | match (1 / 11) |
| Aug 31 | Placing of the Belt/Sash (2) | Typikon p. 37 | explicit | 2025-08-31: match |

"Today the Virgin cometh" etc. incipits are paraphrase pointers only.

## Why the old spike rule failed

`lit.kontakion.undisputed` fires Sep 22 - Nov 8 on Sundays and reads "silent outside". Real behaviour: that window is only one of ~20 windows; June/July (undisputed, 29 dates), Transfiguration, Entrance, Preparation, plus Theotokos/Cross/Triodion windows are explicit in the same table. Nov 8 error cause: Typikon p. 35 uses "between X and Nov 8" and "from Nov 8", so Nov 8 belongs to both readings. Violakis resolves.

## Source discrepancies and errors

- **Typikon p. 36 Pentecostarion bullet is garbled**: "From Wednesday of Mid Pentecost and its leavetaking, we chant 'When thou didst fulfill the dispensation for our sake'". That incipit is the Ascension kontakion; Mid-Pentecost's own is "At the mid-point of the feast". Violakis §40 (p. 32-33) correct: Mid-Pentecost Wed to its leave, then from Ascension to its leave "Having fulfilled the dispensation". Key matches Violakis (Ascension kontakion on Sunday P+42, 8/8). Use Violakis.
- **Dec 20-24**: Typikon "until forefeast of the Nativity" would leave Dec 20-24 unspecified; Violakis "until the eve". Key confirms Preparation to Dec 24 (inferred, 5 dates).
- **Violakis start of July window**: "thereafter [after All Saints] until 27 July"; Typikon "from the beginning of the Apostles' Fast". Differ only on days between All Saints and Monday after (none are Sundays). No effect.
- **Typikon Jul 2 ("2nd and 25th of July")** = Violakis ("On 2 July ... Robe", "25 July ... Dormition of St Anne"). Fine.
- **Typikon fn 33 (p. 46)**: some chant O undisputed Intercessor on every day; irrelevant for Sundays but note for weekday scope.

## Missing / open

1. **Feb 10 - Publican**: no source. Inferred undisputed (4 dates).
2. **Triodion boundary Feb 9**: footnote 27 text ("if the leavetaking ... has been celebrated") implies Feb 9 itself still Presentation; confirmed by 3 key dates, but sources only imply it.
3. **Dec 20-24**: inferred from Violakis + key (see above).
4. **Nov 25** (Entrance leave) on Sunday not sampled; **Dec 9, Aug 1, Aug 31, Sep 1, Sep 13 Sunday** rarely sampled. Rule from sources only.
5. **Saints' feasts on Sunday (Typikon p. 28 s.X: Forerunner Jun 24, SS Peter & Paul Jun 29, John Sep 26, Andrew Nov 30, 3 Hierarchs, Archangels Nov 8, Demetrius Oct 26, Nicholas Dec 6)**: this list governs the **Matins** 6th-ode kontakion (feast's kontakion and oikos, resurrectional moved to ode 3). For Liturgy the key shows the seasonal kontakion: Archangels Nov 8 (2020, 2026) Entrance; Oct 26 2025 Demetrius, Jun 29 2025, Nov 30 2025 Andrew = undisputed/Preparation. Inferred: **no Liturgy override for saints' Sundays**. Typikon p. 28 text ("On a feast of a saint ... kontakion 'O undisputed Intercessor' ... unless Sunday after Triodion") applies to weekday Liturgy.
6. **Matins** Sunday kontakion (resurrectional Octoechos vs feast) is separate Rule (Typikon p. 28 s.X; Violakis §26) and was not checked against the key here (ANCA Abbr/ORTHROS).
7. Pentecostarion/Triodion Sundays only coarse-checked (family match, not exact Sunday names).

## Recommended Rule shape

One `liturgy.kontakion` Rule family: ordered date-window table (above) with context facts `leavetaking_of(feast)` or fixed month-day pairs, plus movable cases (Triodion Sundays, Lent 5 + Annunciation test, Pascha cycle). Fixed windows as `date_between` with **inclusive ends and Entrance start Nov 8**. Provenance: explicit for windows citing Typikon pp. 35-37 + Violakis §40; inferred for Feb 10, Feb 9 boundary, Dec 20-24.

## Sources

- Antiochian Typikon (Khoury/Morris, 2011), Ch I s6 V "The Kontakia chanted during the Divine Liturgy", pp. 35-37; s.X "The Kontakion and Oikos" p. 28; fn 27 p. 36; fn 33 p. 46.
- Violakis, Typikon of the Great Church of Christ (1888), §40 pp. 32-33 (Liturgy kontakia), §26 p. 21 (Matins), footnote on Triodion kontakion p. 33; local scan, CC BY-NC-ND, via user's translation.
- ANCA / AOCANA Liturgy Variables `READ.pdf`, 2019-2026 Sundays (answer key; not committed).
- `prototypes/rule-spike/README.md` finding 3 and `rules/sunday_general.yaml` (branch `prototype/rule-spike`).
