# Pascha plan (work package P)

Headline: Typikon Ch VI-VII gives an explicit order for every modelled Pascha service; ANCA verifies one sample per service (2026; Agape also 2020, 2024). Encode all four, enable by service in `slices.yaml` `supported_pascha`, all Rules single-sample or Typikon-explicit.

## (a) What the engine can model
Slots exist for Vespers, Matins, Liturgy only. Modelled: Holy Saturday Vesperal Liturgy (Vespers part, service `vespers` on Saturday: the eve of Pascha), Paschal Matins (Orthros), Paschal Liturgy, Agape Vespers (new service `agape`, Sunday evening). NOT modelled (not added): Midnight Office, Rush procession/Resurrection Service (the Vigil outline's first two parts; recorded in Matins Rule parts only), Paschal Hours/Office, Compline, Bright Week services (Mon-Sat, no calendar slice: `not a Sunday`), the Liturgy part of the Holy Saturday Vesperal Liturgy (Epistle Rom 6:3-11, Gospel Mt 28:1-20, cherubic/communion substitutes).

Calendar facts: `calfacts.season` = `pascha` for Pascha day only (not in `supported_seasons`); `MAJOR_MOVABLE[0]` = pascha; Bright Week = season `pentecostarion`, weekdays; Bright Saturday eve Vespers = Thomas Sunday (already in slice). Pascha (Gregorian 4 Apr-8 May) never meets Annunciation (25 Mar). St George (23 Apr) in Holy Week or on Pascha is transferred by the DB to Bright Monday (row `Transferred from April 23rd`; 2021, 2024, 2027): it enters Agape Vespers (Typikon Ch V p.325), new fact `bright_monday_george`. Other Menaion saints are not sung on Pascha (ANCA Liturgy and Agape dismissals name none).

## (b) ANCA coverage (antiochian.org service texts)
| Year | Pascha | Holy Sat VDL | Orthros (Vigil) | Paschal Hours | Liturgy | Agape |
|---|---|---|---|---|---|---|
| 2018, 2019, 2021, 2022, 2023 | 04-08, 04-28, 05-02, 04-24, 04-16 | none | none | none | none | none |
| 2020 | 04-19 | none | none | none | none | readers' `11C-Agape-Readers-VESP` |
| 2024 | 05-05 | none | none | none | none | `11A-Agape-VESP` (St George); bilingual |
| 2025 | 04-20 | none | none | none | none | none (only readers' `9A-Paschal TYPIKA`: Epistle/Gospel text, no new key) |
| 2026 | 04-12 | `Holy-Sat-Vesperal-Lit-NEW` (26 pp, with baptisms) | `8-Paschal VIGIL` (outline of rubrics incl. Midnight Office) | none | `9-Paschal-READ` | `11B-Agape-VESP` |
Fetched (polite, curl, 2 s delay, into the cache dirs, not the repo): the 2026 VDL, VIGIL, Agape; 2024 and 2020 Agape; 2026 READ was already cached. 8 further name probes (9A-READ, 8A-VIGIL, 11D-Agape ...) all 404. No Paschal Hours text exists in any year.

## (c) Typikon pages (printed)
Ch VI Holy Saturday Vesperal Liturgy pp.516-517 (15 readings: editor's note p.517); Ch VII Pascha: Midnight Office/Rush procession p.518, Matins pp.518-520, Liturgy pp.520-522, Agape Vespers pp.522-523, Paschal Office p.523, note 319-322; Ch V Apr 23 George moved to Bright Monday p.325; Ch I s2 p.13 (Holy Saturday prokeimenon), s6 VIII p.38 (Alleluia).

## (d) Existing `missing` Rules and tickets Pascha touched
`pent.pascha.ves.*` (3 Rules, ticket "Holy Saturday Vesperal Liturgy out of scope (G)"): replaced by `pascha.ves.*`. `sunday_general.yaml` matins/liturgy kontakion fallbacks (ticket #27): Pascha now covered by `pent.pascha.mat.kontakion` and `lit.kontakion.pascha_cycle` (fallbacks stay for Palm Sunday). Earlier Pascha Matins/Liturgy Rules (Typikon, single ANCA sample) moved into `pascha.yaml`; `pent.coincidence.*` tickets are Pentecostarion Sundays, untouched. Decisions #39/#42/#43 applied: Holy Saturday 8 hymns = 4R + 4 (misreading of ~10).

## (e) Priority (by what ANCA can verify) and status
1. Paschal Liturgy: ANCA 2026 READ, 13/13 comparable slots match (new feast slots: antiphons, eisodikon, trisagion, megalynarion, communion, final hymn, Pascha prokeimenon). Done.
2. Agape Vespers: ANCA 2020, 2024, 2026, 6/6 each. Done, plain and St George orders.
3. Paschal Matins: ANCA 2026 Vigil outline, 4/4 comparable (eothinon, kontakion, katavasia, praises); kathismata/prokeimenon/apolytikia are Typikon-explicit "none" (outline silent). Done.
4. Holy Saturday Vesperal Liturgy, Vespers part: ANCA 2026 VDL, 3/3 (stichera 4R+4, Arise O God, 15 readings). Done; Liturgy part not started.
Not started: Midnight Office, Paschal Hours/Office, Compline (no slots, no ANCA text); Bright Week; Holy Saturday Liturgy part; Pascha on Apr 23 (George on Pascha: DB transfer assumed, no sample). Conflicts logged: see `conflict` fields in `pascha.yaml` (George Agape Res tone 4 vs 2, `open`; Holy Saturday Glory/Now wording, `open`; count `misreading` per #42).
