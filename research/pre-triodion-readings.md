# Pre-Triodion Sunday readings and saint/feast Epistle flags (issue #35)

Question: why do yocal and ANCA differ on 2024-01-28 / 2024-02-04, 2022-11-20, 2022-07-10, 2025-11-09? Labels: **explicit** (source states), **inferred** (key/DB evidence), **missing**.

## Verdicts

| Date | yocal | ANCA | Verdict |
|---|---|---|---|
| 2024-01-28 | E32 + L15 (Zacchaeus) | E31 1Tim 1:15-17 + L14 (Blind Man, Lk 18:35-43) | **Rule gap** (sources silent for 5 Sundays) + ANCA internally inconsistent; yocal = coherent inference, not wrong per source |
| 2024-02-04 | E15 + M15 (Mt 22:35-46) | E32 + L15 (Zacchaeus) | same |
| 2022-11-20 | Sunday E23/L9 | Entrance readings (Heb 9:1-7, Lk 10:38-42; 11:27-28), "Transfer of the Entrance" | **ANCA variance** (feast transferred to Sunday); yocal + Typikon + Violakis agree |
| 2022-07-10 | Sunday E4/M4 | Joseph of Damascus 2Tim 2:1-10 + Mt 8:5-13 | **Rule/data gap**; ANCA variance (Antiochian saint) |
| 2025-11-09 | Sunday E22 (Gal 6:11-18) | Nektarios Eph 5:8-19 + Lk 8:41-56 | **Rule/data gap**; yocal flag is_sun_apos blank |

## 1. 2024-01-28 / 02-04 (pre-Triodion Sundays)

**Sources (explicit).** Typikon pp. 191-192 ("Epistle and Gospel readings for the Sundays which follow Epiphany"): table by number of Sundays between Epiphany and Triodion, **1-4 cases only**. Violakis Menaion, 14 Jan "Notes on Apostle and Gospel" A-D + note, printed pp. 162-163 (scan 002-100/101): same four cases, same as Typikon.
- 1 Sunday: E32 + L15 (Zacchaeus). 2: E29/L12 (Ten Lepers), E32/L15. 3: E29/L12, E32/L15, E17/M17 (Canaanite). 4: E29/L12, E31 + **13th Luke** (Rich Young Ruler), E32/L15, E17/M17.
- Note (both): late Pascha, weekdays run out of Gospels -> after Luke complete, count the remaining Matthew weeks before Exaltation Sunday; same for Epistles. Violakis adds nothing on >4 Sundays or on re-reading Luke 14 (its note E concerns Hypapante katavasias).
- Violakis 4-case prints Epistle of **32nd** for both 2nd and 3rd Sundays (p. 163); Typikon says 31st for the 2nd. Transcribed as printed; likely misprint [?]. Both give "13th" Luke, not 14th.
- Typikon p. 192 count excludes the "Sunday after Theophany"; 2024: Jan 7 = Forerunner Synaxis (saint's Epistle/Gospel, Typikon p. 37), SunAT = Jan 14 (fn 130, p. 191), then Jan 21, 28, Feb 4, 11, 18 = **5 Sundays** to Publican (Feb 25). Neither source covers 5 or 6 Sundays: **missing**.

**yocal (db/4_paschalion_cycle.py lines 60-88, 369-405).** Lists for 1-6 Sundays. 4 and 5 have two variants: "a" (includes E31/L14 Blind Man) or "b" (omits it), chosen by whether L14Sun already fell in Dec (Dec 1 is Fri/Sat/Sun). 2024: Dec 3 2023 was L14 (ANCA agrees) -> "5b": L12, Zacchaeus, M15, M16, M17. Rule L14-once is yocal's own; not in either source. Also L14 (18:35-43) not L13 in the 31st slot: ANCA-conformant, differs from the sources' "13th".

**ANCA key** (2018-2026 Sundays, READ.pdf): 2024 = "5a": L12, **L14**, Zacchaeus, M16, M17 -- L14 re-read after Dec 3 2023.
Cross-check of all years 2019-2026: L14 omitted in 2019 (4 Sundays, L14 Dec 2 2018) = yocal 4b, ANCA matches; included 2021, 2022 (L14 unread in Dec) = 4a/5a. Only 2024 combines L14-used + 5 Sundays. 2020/2023/2025/2026 (2-3 Sundays) no L14 either way. L13 (Rich Ruler) read late Nov every year in yocal, so the sources' "13th Luke" in the 4-case would always be a repeat -- consistent with both ANCA and yocal replacing it with L14 or Matthew when read.

**Conclusion.** yocal is not provably wrong: Typikon/Violakis do not address 5 Sundays; yocal's "skip L14 if read in Dec" matches ANCA 2019 but not ANCA 2024. ANCA 2024 either has a different rule for >=5 Sundays (always E31/L14, i.e. "5a" unconditionally) or an ad hoc choice. Evidence is one data point. **Missing rule**, not DB bug.

**Recommended.** (a) Log as Divergence "pre-Triodion 5-Sunday case (2024)": yocal 5b vs ANCA 5a; DB 2019-2031 shows 2024 as the only >=5-Sunday year with L14 already read in Dec, so no further ANCA sample exists yet. (b) For Rule encoding: keep Typikon 1-3 explicit, 4 explicit but with L14/Matthew substitution (inferred, ANCA 2019/2022), 5-6 inferred from yocal lists. (c) Optional DB change: switch 5b to 5a to match ANCA (one-line list change at db/4_paschalion_cycle.py:84), only if the user prefers ANCA over the "no repeat" principle. Ask OLG/Fr John Morris to settle.

## 2. 2022-11-20 (forefeast of Entrance on a Sunday)

- Typikon Nov 20, pp. 109-111 (order if forefeast falls on Sunday): at Liturgy "The Epistle and the Gospel for the Sunday" (p. 111). Violakis Menaion Nov 20, printed p. 102 (scan 002-040): "Apostle and Gospel of the Sunday". **Explicit; both agree with yocal** (E23 Eph 2:4-10, L9 Lk 12:16-21).
- Violakis §42 (pp. 34-35) list of Theotokos feasts with changed readings on Sunday (Nativity, Meeting, Annunciation, Dormition) does not include the Entrance; the Typikon p. 37 list likewise.
- ANCA 2022-11-20 READ is headed "Transfer of the Entrance of the Theotokos" (apolytikion, kontakion, megalynarion, Eisodikon of the feast; Heb 9:1-7 + Lk 10:38-42; 11:27-28). That is a transfer of the Nov 21 (Monday) feast to the Sunday: US pastoral practice, no Typikon basis found. Kontakion window already explained in #25 (Forefeast kontakion in Typikon p. 35 would differ from ANCA's Entrance kontakion on this date too).
- **Verdict: ANCA variance.** yocal correct per sources; UK has no transfer assumption. Log as Divergence (class: ANCA weekday-feast-to-Sunday transfers; check other ANCA "Transfer of ..." headings in the key).

## 3. Saint-Epistle flags (2022-07-10, 2025-11-09)

- Rule explicit: Typikon p. 37 s.VII: on Sunday, "Epistle for the saint and Gospel for the Sunday if a feast of a **great saint**" falls on Sunday; always both for Forerunner feasts, Peter & Paul, the Twelve, Evangelists, three Holy-Fathers Sundays, Three Hierarchs (pre-Triodion). Violakis §42 (p. 34): same ("celebrated saint"; same exception list). Neither defines "great saint"/"celebrated" except via rank (Typikon general rules p. 28, Ch. V).
- yocal: is_sun_apos is a per-commemoration flag in `db/menaion.csv`. 11-09 Nektarios: class 4, Eph 5:8-19 + Mt 4:25-5:12, **is_sun_apos blank** (weekday only) -> yocal reads Sunday Epistle. 07-10: no major commemoration, no readings (Joseph of Damascus is only in the minor list).
- Typikon: no Nov 9 entry; Jul 10 appears only as editor note fn 232 (p. 429, "We celebrate the Feast of St. Joseph of Damascus on July 10"), no order. Bp Basil (local `BpBasil/`): both are plain SIMPLE/6-stichera in the Menaion ranking (ranks.csv 07-10, 11-09), but his Parish Typikon phyllada list adds "POLYELEOS for Hieromartyr Joseph of Damascus" and "VIGIL for St Nektarios" (Ranking of Feasts according to the Typikon, Phyllada section).
- ANCA reads the saint's Epistle for both (2022-07-10 2Tim 2:1-10; 2025-11-09 Eph 5:8-19). Pattern: Antiochian-added saints promoted to polyeleos/vigil level -> saint's Epistle on Sunday.
- **Verdict: Rule gap** (no source defines "great saint" for readings; Antiochian promotions are outside Typikon) with **data gap** in yocal (Joseph has no readings; Nektarios flag off). ANCA reading is inferred from Bp Basil rank (POLYELEOS/VIGIL = "great saint"), single key observation each.
- **Recommended.** Rule: Sunday saint's-Epistle = per-commemoration flag, default from Bp Basil Phyllada/rank >= polyeleos plus Typikon p. 37 list (explicit). Add overrides Jul 10 (Joseph, 2Tim 2:1-10, needs Menaion readings row) and Nov 9 (Nektarios, set is_sun_apos = 1) as Antiochian divergence from UK-DB; flag inferred. Spot-check other keyed Sundays with saint headings (ANCA epistle label "For St X").

## Method / sources

- Typikon (Khoury/Morris 2011) `pdftotext -layout`, printed page = footer "Back to Table of Contents N" (the page ends at that line). pp. 37, 109-111, 191-192, 429.
- Violakis 1888 local scan (CC BY-NC-ND), Menaion section pages checked at image level; Greek read as printed, uncertain items flagged [?]. Cited pages = printed page numbers (Menaion 102 = 002-040; 162-163 = 002-100/101; Protheoria §42 pp. 34-35 via `Violakis/translation.md`).
- yocal DB: `db/yocal/YOCal_Master.db` (`yocal_main`, `yocal_lections`), `db/4_paschalion_cycle.py`, `db/menaion.csv`.
- ANCA key: `prototypes/anca-compare/sun_keys.csv` + `pdfs_sun/*-READ.pdf` (untracked, not committed; paraphrased).
- Bp Basil: `BpBasil/` text + `prototypes/bpbasil-rank/ranks.csv`.
