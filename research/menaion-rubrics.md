# Menaion rubrics for glory and sticheron counts (#40)

Question: do published Menaia print per-day Vespers sticheron counts and Glory placement? Can that upgrade 6R+4 / 7R+3 and Principal-commemoration glory (#28, #31, #34) from inferred to explicit? Paraphrase only; no text committed.

## Verdict

- **Glory presence per commemoration: explicit, printed in the Menaion.** Slavonic Menaion prints, per date, the eve Vespers "Lord, I have cried" section with a saint-specific Glory idiomelon or only "Glory, Both now, Theotokion". This is the same fact as ALWB `meVE.SticGlory`, but from an independent primary print. It resolves 3 of the #34 misses.
- **Sunday split rule: already explicit** (Violakis §7 pp.6-7, Typikon p.12/48 per #26). Keyed on whether the saint is "celebrated"/has a doxastikon; Menaion Glory is the input. No Menaion prints the Sunday merge itself.
- **Counts "on 6" are printed only sometimes** (Nov 1: "stichera of the saints on 6"); other days give tone + similar melody and the count is by listing. Not a reliable count source; the 4R+6 flag (#32) is not in any Menaion.
- Per-day rubrics online that state counts + Glory source (azbyka) apply Russian practice, so they cannot answer Antiochian Sunday cases.

## Sources checked

| Source | Result |
|---|---|
| orthlib.info Daily Menaion (Slavonic; per-day PDFs `Menaia/Rjadovaja-Minea/<MM-Month>/<mon><DD>.pdf`; cert expired, needs `curl -k`) | Reprint of Kiev Menaion, Sretensky Monastery, Pravilo very, 1997 (title page). Prints counts sometimes, tone, Glory idiomelon explicitly. Usable via text layer (legacy Slavonic font, partly mapped). Best primary source here. |
| azbyka.ru "Bogosluzhebnye ukazaniya" (`?date=YYYY-MM-DD`, civil date, Julian-calendar days) | Per-date rubric: stichera count/split, Glory source, Now. Cites Typikon + Kiev Minea 1893 + Rozanov. Russian practice; weekday split for Sunday-merge differs (below). Secondary. |
| st-sergius.org Oktoechos PDF (English) | Rubric: Great Vespers 7+3, or 4+6 if Menaion service is polyeleos rank; Glory from Menaion "if appointed". Confirms the general rule; site served 403 to some fetches. Not per date. |
| CCEL "General Menaion" (English, anon.) | Common services only (hierarchs, prophets): stichera sets printed with Glory per set. Not per date. |
| orthodox-europe.org (Diocese of Sourozh/Western Europe) | No Menaion texts; Liturgics section has handbook, clergy downloads, British Saints project (planned). Not a source. |
| Metropolitan Cantor Institute (MCI) | Stichera page and Daily Vespers pdf exist (Byzantine Catholic); not fetched in full; secondary forum description only. Not a source for per-date counts. |
| Greek Menaion (print), Online Menaion | Not reachable/not checked. |
| Local: Violakis `translation.md` §7-8 (pp.6-8); Bp Basil `Descriptions of Ranks.txt` | Explicit Sunday rule text (below). |

## Explicit rule text (paraphrase)

- Violakis §7 (pp.6-7): on afterfeast Sundays and for commemorations of celebrated saints, 6 resurrection + 4 saint; when a celebrated saint also falls on an afterfeast Sunday/apodosis, 4 + 3 feast + 3 saint; a listed set of great saints get 4 + 6; if the saint falling on Sunday has no doxastikon, 7 + 3.
- Violakis §8 (pp.7-8) and §13: for a saint on Sunday, Glory is the saint's hymn and Both now the first Theotokion of the tone; if the saint has no doxastikon, the Theotokion of the tone covers Glory/Both now.
- Bp Basil Descriptions of Ranks: Polyeleos/Vigil rank = 6 or 8 Menaion stichera, Glory = commemoration's own doxastikon from the Menaion; Simple rank with two doxastika (LIHC + aposticha): six saint stichera, none from Parakletike (note 32).

Net: the split is explicit as a function of "has a doxastikon at Lord I have cried", which the Menaion print supplies. Wording "celebrated saint" is not defined, so the 7+3 / 6+4 line is still derived from doxastikon presence, not rank.

## Sample dates vs ANCA key (`prototypes/anca-compare/compare.csv`, `prototypes/principal-glory/out.csv`)

Slavonic Menaion eve Vespers (Menaion date D = Saturday eve of Sunday D). "pred" = #31 prototype.

| Menaion date | Saint | Menaion Vespers | ANCA obs | pred (ALWB) | Outcome |
|---|---|---|---|---|---|
| Nov 1 | Cosmas and Damian | stichera "on 6", Glory printed | 6R+4 (2020-10-31, 2026-10-31) | 7R+3 | Fixes miss; ALWB data gap |
| Oct 27 | Nestor | no saint Glory (Glory/Both now Theotokion) | 7R+3 (2024-10-26) | 6R+4 | Fixes miss |
| Jan 24 | Xenia of Rome | octoechos 3 + saint 3, no saint Glory | 6R+4 (2021-01-23) | 7R+3 | Menaion agrees with ALWB/our 7+3; ANCA diverges (matches #34 Xenia note) |
| Nov 10 | Apostles Olympas et al. | no saint Glory | 4R+6 (2019, 2024) | 7R+3 | Not explained: 4R+6 is ANCA/Bp Basil "two sets of 3" convention (#32), not Menaion |
| Jul 27 | Panteleimon | Glory printed | 6R+4 (2025-07-26 match) | 6R+4 | Control agrees |

Azbyka cross-check (Russian rubric, Sunday): Nestor 7+3 with Glory/Now = dogmatikon (Nov 9 2025); Olympas 7+3, Glory/Now dogmatikon (Nov 23 2025). Weekday: Cosmas "6, Glory saint's" (Nov 14 2025); Panteleimon "8, Glory saint's" (Aug 9 2025). So Russian practice on a Sunday gives the dogmatikon at Glory even where the Menaion has a saint Glory-type hymn on weekdays; Antiochian/Greek (Violakis §8) uses the saint's. Do not use azbyka for Glory on Sundays.

Not checked: other #34 misses (Oct 26 Sat-rule gap, 07-10 Joseph of Damascus override, 2 ALWB gaps beyond Nov 1/Oct 27) pending text-layer parsing of the full set.

## Recommendation

1. Add Slavonic Menaion Glory flag as a second independent evidence column for `saint_has_glory` (tri-state: Menaion print vs ALWB; disagreement logged). Keep ALWB as primary build input (structured, English names); use Menaion print to fill/override on disagreement, cite "Kiev Menaion (orthlib.info), <date> eve Vespers".
2. Keep 4R+6 (two saints) as Inferred (#32); no Menaion states it.
3. Do not treat azbyka as Glory evidence for Sundays (Russian dogmatikon convention).
4. Optional follow-up: scripted extraction (`pdftotext` of 366 `.pdf`s, regex on "Slava" within the LIHC section before "stichovne") to compare all dates to ALWB; font mapping is partial, expect manual review.
