# PROTOTYPE (throwaway, never merge): ANCA Sunday Matins + Liturgy comparison (issue #33)

Scripts: `scripts/fetch_sun.py` (plain `ORTHROS.pdf` + `READ.pdf` per Sunday via anca-index, 823 files, PDFs untracked), `scripts/parse_sun.py` (heading-based slot extraction -> `sun_keys.csv`), `scripts/compare_sun.py` (Rule predictions vs key; needs `db/yocal/YOCal_Master.db`). Run 2026-11-09; 412 Sundays 2018-02-18..2026-11-08.

## Results (412 Sundays)

| Slot / Rule | match | diff | other |
|---|---|---|---|
| matins.eothinon_gospel (DB cycle, #19) | 402 | 0 | 10 not in key |
| matins.ainoi tone = Sunday tone | 400 | 11 | 1 |
| matins.prokeimenon tone = Sunday tone | 342 | 18 | 52 not in key |
| liturgy.rite Basil/Chrysostom (#19) | 411 | 1 | |
| liturgy.kontakion fixed windows (#25) | 208 | 16 | 188 movable (Triodion/Pascha cycle) not modelled |
| liturgy.epistle ref vs DB | 283 | 6 | 65 saint's Epistle skipped |
| liturgy.gospel ref vs DB (notation-normalised) | 367 | 22 | |
| matins.kontakion (#27) | keyed 411/411: 234 resurrectional, 177 feast/Triodion/Pentecostarion | | |

## Every diff classified (0 unexplained Rule errors)

- **Rite**: 1 diff = 2018-03-25 Annunciation on Lent 5 (Chrysostom, per #19; yocal flag wrong, known).
- **Kontakion, 16 diffs = my predictor's omissions, all covered by #25 table**: All Saints Sun (P+56) x9 (window starts P+57), Jul 2 Robe, Jul 25 St Anna, Aug 31 Sash, Sep 7 forefeast, Sep 13 Dedication x2, Dec 9 Conception. Matches #25 key evidence.
- **Matins prokeimenon tone diffs 18**: 7 Theotokos-feast Sundays (Feb 2, Aug 15, Sep 8 area, Nov 20, Mar 25: tone 4 feast prokeimenon, per #24 rule "feast's if Theotokos feast"); 11 Pascha-cycle (Thomas, Palm, Pentecost) where yocal tone is null (Pascha-cycle tone gap, #19 says Thomas=1).
- **Ainoi tone diffs 11**: all Pascha-cycle, yocal tone null; key tones 1 (Thomas) / 4 (Palm, Pentecost). Calendar gap, not Rule gap.
- **Epistle diffs 6**: saint/feast readings not flagged in DB (2022-07-10, 2025-11-09, 2022-11-20 Entrance-forefeast), verse range (2022-07-03 5:1-10 vs 11; 2024-02-04), Luke-cycle pre-Triodion shift (2024-01-28/02-04: key Blind Man then Zacchaeus; DB one week earlier). NEW: the Zacchaeus/Blind-Man pre-Triodion Sunday assignment differs between yocal and ANCA in 2024; check Typikon.
- **Gospel diffs 22**: 18 notation/addenda only (DB appends `; Luke 8:8`, `; Matthew 22:14`, `,19:27-30` vs key `;`), 1 versification (2023-03-26 Mark 9:17-31 vs 9:16-30), 3 same as Epistle shifts.

## New observations for the audit

1. Liturgy READ file prints only variable slots; per-Liturgy slot set varies: antiphons (3 on Basil/feast days, 141 of 412), Eisodikon variant (Pascha 45, ordinary 30, feast, apodosis, Palm), Anti-Trisagion (11), megalynarion (St Basil's 44 + feast/Pascha-cycle), koinonikon (86; Lent/feast), apolytikia 1-4 (feast + patron prompt). These are slot-catalogue candidates; none is yet a Rule.
2. Liturgy prokeimenon / alleluia text is printed (verses visible in READ), so epistle-owner rule (#21/#22) can be tested against prokeimenon text, not just the Epistle ref.
3. Matins kathismata heading variants (Octoechos/Pentecostarion/Lenten tone N) and psalm 50 troparia type (plain 316, Lenten 75, festal 8, Palm 1) are keyed; Matins slots: 3-4 apolytikia/theotokia, exapostilarion count, doxasticon form.
4. Sunday Matins ORTHROS is the full-text key for Matins; Abbr unnecessary except older dates.

## Limits
Parsers are heading regexes; kontakion class prediction omits movable cycle; Matins kontakion not rule-predicted here (only keyed); saint-Epistle Sundays skipped; no hymn text compared.
