# Major-feast Typikon vs ANCA conflicts: tiebreak

Issue #42 (map #5; decision #39; findings #36). Paraphrased; no PDFs/long excerpts. Throwaway branch, not for merge.

## 0. Conventions

- "p.NN" = printed footer page, Antiochian Typikon (Khoury/Morris 2011). "Vio. §N p.P" = Violakis 1888, Protheoria section N, printed page P (local scan + translation, untracked). "BpB" = `BpBasil/` charts. "ALWB" = local AGES data (`prototypes/alwb-menaion/`, GOA text, Greek+English). ANCA = AOCANA `servicetexts` PDFs (filenames from `prototypes/anca-index/pages.json`).
- R = Resurrection stichera; LIHC = "Lord, I have cried".
- Verdict set (#39): **Typikon holds** / **ANCA holds** / **misreading** (not a true conflict).
- Proposed #39 status: ANCA holds -> Rule follows ANCA, Typikon reading logged as dissent, `accepted`; misreading -> `misreading`.

## 1. Summary

| # | Conflict | Verdict | Rule |
|---|---|---|---|
| 1 | Presentation on Sunday, Vespers LIHC | **ANCA holds** | 4R+6, Glory/Now feast |
| 2 | Annunciation on Lent 5 Sunday, Vespers LIHC | **ANCA holds** | 4R+6, Glory/Now feast |
| 3 | Sat of Lent wk 4 (Annunciation leavetaking) Vespers Glory | **misreading** | Glory = Annunciation Doxastikon; Now = R Theotokion |
| 4 | Holy Saturday Vespers count | **misreading** | 8 = 4R+4 (verses 10,9 empty) |
| 5 | Pentecost praises | **misreading** (Typikon wording loose) | 4 slots = 3 distinct + 1st repeated |

## 2. Per conflict

### 2.1 Presentation on Sunday (pre-Triodion): Typikon 6R+4 vs ANCA 4R+6

- Typikon p.218: LIHC 10 = 6R + 4 Presentation, Glory feast (Now via aposticha line "Glory, Now" feast). Count is self-consistent (no typo evidence).
- ANCA: Feb 01 2020 and Feb 01 2025 VESP: verses 10-7 R (4), verses 6-1 Presentation (3 distinct, each repeated = 6 slots), then Glory feast. 4R+6, 2/2.
- Typikon own pattern for Sunday on Theotokos feasts: 4R+6 (Nativity Theotokos pp.66-68, Entry p.113, Dormition p.457). Same Typikon p.219 gives Matins praises 4R+4 for the Presentation, the Theotokos-feast pattern (p.292 Annunciation same).
- Violakis: Sunday + Theotokos feast on principal day = 4R + 6 feast (Vio. §7 pp.6-7). Meeting is grouped with Theotokos feasts (Vio. §8 p.7-8: Doxastikon rules; §31 p.25: praises 4R+4; §42 p.35: readings) and is absent from the R-omission list (§7 p.7). Violakis does not name the Meeting in the §7 count sentence itself: reading is by grouping (inferred).
- BpB: Meeting classed with 2nd-class Theotokos feasts but flagged as sharing Master-feast traits, defers to the Typikon of the Great Church for specifics (Descriptions of Ranks n.7, n.10); Chart II 2nd class Sunday = 4R+6. Supporting only.
- Triodion-Sunday variants (Typikon p.220: 4R+2 Triodion, Meatfare 4R+3, sum 6 not 10) are a separate Typikon typo already noted in #36; not re-tiebroken.
- Verdict: **ANCA holds**. Typikon p.218 is the outlier against Typikon pp.66/113/457/219 and Violakis. Evidence tier: explicit (ANCA x2, Violakis by grouping, Typikon pattern).

### 2.2 Annunciation on Lent 5 Sunday: Typikon 6R+4 vs ANCA 4R+6

- Typikon p.305 (section starts p.304): Sat-evening LIHC 10 = 6R + 4 Annunciation. The same page introduces the Sat evening/Sunday order as "the order for the 4th Sunday", but the 4th-Sunday order (p.291) is 4R + 6 Annunciation. Typikon contradicts itself; the 6R+4 line is a likely slip (also differs from Lent 3, p.280-282, which has its own Cross-Sunday frame).
- ANCA: Mar 24 2018 VESP (Great Vespers of the Annunciation, Lent 5 Sunday eve): verses 10-7 R, verses 6-1 Annunciation (3 distinct, each repeated = 6 slots), Glory Annunciation tone 6. 4R+6; 1/1 sample (only year in range, 2018).
- Violakis: 4R+6 principal day (Vio. §7); Matins praises 4R+4 on Lent 4/5 (§31 p.25).
- Verdict: **ANCA holds**. Treat p.305 6R+4 as Typikon error (internal contradiction with p.291 and the p.305 lead-in).
- Note: issue cited p.304; the Vespers count is printed on p.305.

### 2.3 Sat of Lent wk 4, Vespers Glory owner: Typikon "Gabriel" vs ANCA "Annunciation"

- Typikon p.289 (feast on Saturday of Lent 4; leavetaking Saturday evening): LIHC "9" stichera = 4R + 3 Annunciation + 3 Gabriel; Glory Archangel, Now R. "9" is a misprint (4+3+3=10). Matins praises for Gabriel (p.290).
- ANCA Mar 25 2023 VESP ("Leave-taking of the Annunciation"): verses 10-7 R, 6-4 Annunciation, 3-1 Gabriel (10 slots), Glory = Doxastikon of the Annunciation tone 6 ("From heaven the archangel Gabriel was sent"), Both now = R Theotokion tone 8; aposticha Glory = Annunciation doxastikon tone 8.
- Menaion check (ALWB, GOA): Mar 26 Vespers has 3 Gabriel stichera and **no Doxastikon of its own**: its SticGlory field points to the Mar 25 Doxastikon. So "Glory for the Archangel" in Typikon is the Menaion's Mar 26 Glory = same text ANCA prints, labelled Annunciation.
- Violakis (Vio. §8 p.7): on Apodoses, Glory = hymn of the feast or saint, Both now = Theotokion: consistent either way.
- Verdict: **misreading** (labelling). No count or text difference. Rule: Glory = Mar 25 Doxastikon (via Mar 26 pointer), Now = R Theotokion. Encode Glory ref as "Mar 26 Menaion Glory", resolving to the Annunciation text. Typikon "9" = typo for 10.
- Caveat: single ANCA sample (2023; 2017 outside range). ALWB is Greek-derived GOA data, not Antiochian.

### 2.4 Holy Saturday Vespers: Typikon 8 (4R+4) vs ANCA ~10

- Typikon p.516: LIHC "8 stichera": 4R tone 1 + 4 idiomela of Great Saturday; then Glory/Now line ("The great Moses...").
- ANCA (only keyed year 2026; file Holy-Sat-Vesperal-Lit-NEW.pdf): verse slots numbered 10 to 1 but verses 10 and 9 carry **no hymn** (printed as bare verses); verses 8-5 R tone 1 (4 hymns); verses 4-1 Harrowing of Hades tone 8 (3 distinct texts, verse 3 repeats verse 4, so 4 slots). Total hymns 8 = 4R+4. Glory = Doxastikon Holy Saturday ("Moses"), Both now = R Theotokion tone 1.
- Menaion/Triodion check (ALWB Triodion d071 = Holy Sat): 4 R + 3 "Today Hades" idiomela (4th by repeat); Glory (Moses, tone 6) + Theotokion tone 1 for Now. Matches ANCA.
- Typikon p.516 "Glory... Now and ever... The great Moses" is one rubric; the printed form attaches Moses to both, ANCA/ALWB give Moses to Glory and R Theotokion to Now. Minor, noted.
- Verdict: **misreading** (~10 came from verse numbering). Counts agree: 8. Rule 4R+4.
- Caveat: one ANCA year; other years' Holy Sat files absent from index (no `servicetexts` links).

### 2.5 Pentecost praises: Typikon "3 repeated" vs ANCA 4

- Typikon p.539: praises "3 stichera for Pentecost repeating each in tone 4", then Glory/Now "O Heavenly King".
- ANCA Pentecost ORTHROS (2020 Readers file and 2026 file) and 2026 Abbr: 4 verses; verse 1 text A, verse 2 repeats A ("repeat above"), verse 3 text B, verse 4 text C. So 3 distinct stichera, first repeated = 4 slots; Abbr cites HTM Pentecostarion pp.245-246 for the 4 stichera. Glory/Now = O Heavenly King, tone 6 (matches p.539).
- Typikon wording is loose: Vespers LIHC same page (p.538) says "3 in tone 1 repeating the 1st to make a total of 4", i.e. the "repeat the first" form; Kneeling Vespers (p.539) "3 stichera from the praises... repeating each for a total of 8" cannot be 3 x 2 = 6, but is 4 x 2 = 8, which implies a 4-slot base. Literal "repeating each" (3x2=6) fits neither ANCA nor Kneeling Vespers.
- ALWB (GOA) Pentecost d120 lists 3 Lauds stichera + media key `Lauds123as123`: 3 distinct; does not say whether first is repeated. Non-evidence.
- Violakis Protheoria does not cover Pentecost praises counts (not found).
- Verdict: **misreading**: Typikon wording elliptical; 3 distinct + first repeated = 4 slots, consistent with the Typikon's own Vespers and Kneeling Vespers arithmetic. Rule 4 slots. Residual: no independent Typikon (Greek/Slavonic) print checked for this line; ANCA/HTM is the Pentecostarion reference.

## 3. Rule changes for #39 / encoding

- Presentation Sunday and Annunciation Lent 5 Sunday: set Rule to 4R+6 (feast Glory/Now); log Typikon p.218 / p.305 as Source conflict, `accepted` (reason: Typikon outlier; ANCA + Violakis + Typikon pattern).
- Lent 4 Sat Glory: no Rule conflict; encode Mar 26 Glory as pointer to Mar 25 Doxastikon; fix typo "9"->10.
- Holy Sat: keep 4R+4; model verses 10,9 as hymn-less.
- Pentecost praises: 4 slots (A,A,B,C); record Typikon "repeating each" as loose wording.

## 4. Gaps

- Only 1 ANCA sample each for Annunciation Lent 5 (2018), Lent-4 Sat (2023), Holy Sat (2026); two for Presentation (2020, 2025), Pentecost 2 files (2020, 2026).
- Slavonic Menaion/Triodion (orthlib.info) and Greek Typikon print of the Menaion rubrics not checked; Violakis Meeting-on-Sunday count is by grouping not an explicit sentence.
- Typikon p.305 and p.218 contradictions suggest a general check of other 6R+4 / 4R+6 Typikon Sunday counts (Ch.V pp.66-457) against the 4R+6 Theotokos pattern.
