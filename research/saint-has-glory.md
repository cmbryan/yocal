# Menaion class / doxastikon data: `saint_has_glory`

Issue #26 (map #5). Paraphrased; no PDFs/long excerpts committed. Cites: "Typikon p.NN" = printed page (Antiochian Typikon, Khoury/Morris 2011); "Violakis p.N" = printed page, Typikon of the Great Church 1888 (local scan + transcription, not committed); "ALWB" = AGES Liturgical Workbench Menaion day files (GR `cog` library; slot keys only).

Status tags: **EXPLICIT** (source states it), **INFERRED** (from key/data), **MISSING**.

## 1. Answer

- The Rule is EXPLICIT: Sunday Great Vespers LIHC split is 7 Res + 3 saint if the saint has no doxastikon ("Glory"), 6 Res + 4 saint if it has one (Typikon p.12 stichera list, p.48 Sunday order; Violakis p.7 Protheoria, p.50 Sunday Vespers).
- The input is MISSING from yocal. `Menaion.class` / `major_commem` do not predict it (sec. 3).
- Best available per-date source: ALWB Menaion day files: is `meVE.SticGlory.text` non-empty for the day's lead commemoration. INFERRED proxy, 83/89 (93%) agreement with the ANCA key on 6R+4 vs 7R+3 Sundays 2019-2026 (sec. 4).
- Expose as a tri-state boolean per commemoration (true / false / unknown) with source tag, plus override table. Sec. 5.

## 2. What the Typikon says depends on a doxastikon

All EXPLICIT. "Doxastikon" = proper "Glory..." hymn of the saint at a given slot.

| Slot | Effect of saint having / lacking doxastikon | Cite |
|---|---|---|
| Sun Great Vespers, LIHC stichera | has: 6 Res + 4 saint (Glory = saint, Now = Theotokion). lacks: 7 Res + 3 saint, "Glory.. Now.." Theotokion of tone | Typikon p.12, p.48; Violakis p.7, p.50 |
| LIHC exceptions (list of great saints) | 4 Res + 6 saint: Archangels, Nativity of Forerunner, Peter & Paul, John Evangelist (Sep 26), Three Hierarchs (not in Triodion), Fathers of 4th/7th Councils, Demetrius, Nicholas. Not conditional on glory | Typikon p.12 |
| First Glory (LIHC) | no special Glory: Glory..Now = Theotokion of tone. Great-martyr on Lord/Theotokos Sunday: Glory = saint, Now = tone | Typikon p.13 |
| Aposticha Glory | saint on Sunday: Glory = saint, Now = Resurrection in tone of Glory; with no special Glory, theotokion of tone | Typikon p.14 |
| Vespers/Matins/Liturgy troparion | saint with no LIHC Glory: its troparion is NOT sung on Sunday; only Resurrection troparion + theotokion. With Glory on Sunday after Lord feast: saint troparion at Glory | Typikon p.16 |
| Dismissal | saint named only "if it has a Doxastikon" | Typikon p.17 |
| Daily (non-Sunday) Vespers | 6 stichera w/o Glory: 3 Octoechos + 3 saint; saint's Saturday-eve troparia change if no Glory | Typikon p.42-43; Violakis p.41-42 |
| Matins praises | separate fact: "if saint has stichera for the praises" (not the same as Vespers Glory) | Typikon p.51 (Sunday Matins order); p.30-31 feast cases |

Conclusion: one boolean is not enough. At least three per-commemoration facts: `vespers_glory` (LIHC SticGlory), `aposticha_glory`, `has_lauds` (praises stichera; ALWB `meMA.Lauds1..4`, `LaudsGlory`). #26 only needs `vespers_glory`; the other two come free from the same ALWB read and will gate Matins praises (38 missing cells in the spike) and Vespers aposticha.

## 3. What yocal has: not predictive

- `Menaion.class` (YOCal.db only, **not in master**; `class_5` is an unrelated name collision): `1` x4, `2` x5, `3` x34, `4` x29, `5` x1, `K` x4, `V` x1, `X` x13, blank x275 (of 366). Undocumented scale; K/V/X used only for fast logic (`db/6_fast_codes.py`). See gap analysis #12.
- Spike key data (`prototypes/rule-spike`, ANCA `Abbr.pdf`, 106 post-Pentecost Sundays 2019-2026; I re-parsed vespers LIHC split and joined on date):

| yocal `Menaion.class` | 6R+4 | 7R+3 | 4R+3+3 | 4R+6 |
|---|---|---|---|---|
| blank | 34 | 29 | 9 | 0 |
| 3 | 7 | 0 | 4 | 3 |
| 4 | 12 | 0 | 0 | 0 |
| K | 4 | 0 | 0 | 0 |
| X | 3 | 0 | 1 | 0 |

- All 29 7R+3 cells are class-blank, but so are 34 6R+4 cells. Blank-class dates have a lead saint in ANCA (and ALWB) whose rank yocal never recorded, because `major_commem` is only filled for "major" dates. Classes 4/K never occur with 7R+3, so a class>=4 date implies glory (INFERRED, 19/19), but that decides only the minority.
- 4R+3+3 and 4R+6 are decided by Lord/Theotokos context and the p.12 great-saint list, not by glory. Class 3 is mixed because some class-3 saints are on the p.12 list (Archangels, Demetrius, Nicholas, John) and others not (Andrew, Sabbas, Chrysostom: 6R+4).
- Typikon Ch. V (per-date orders) states the split for ~59 Sunday dates (generated rules, spike) but 7R+3 appears only for Jan 5 (p.168); Ch. V largely says "follow the Menaion" for Sat/weekday, so it supplies no glory flag for ordinary saints (typikon-menaia-structure, #7).

## 4. Candidate source: ALWB Menaion day files (INFERRED, validated)

- AGES ALWB `Books-Collections/Menaion/mMM/me.mMM.dDD_*.ares`; slot `meVE.SticGlory.text`. Alternate commemorations on same date appear as `alt1.`, `alt2.` blocks. Day record also has `meHO.rank` (empty everywhere checked, #13) so rank is unavailable; glory presence is.
- GR `cog` library: SticGlory filled on 216 of 371 day files (#13). English `dedes`/`goadedes` too sparse (goadedes 97 of 269 filled; dedes agrees ~64%): use Greek for the flag, keys only (licence decision #16: no text stored).
- Validation vs ANCA key (6R+4 -> glory expected; 7R+3 -> none; 89 Sundays; main commemoration only):

| ALWB cog `SticGlory` | 6R+4 | 7R+3 |
|---|---|---|
| present | 57 | 3 |
| absent | 3 | 26 |

  93% agreement (83/89). The 6 misses:
  - Nov 9 2025 Nektarios; Jul 12 2026 (alt block has glory): ANCA picks a modern/alt commemoration, not ALWB's main -> need explicit lead-commemoration choice per date (ALWB `alt1/alt2` carry glory).
  - Jul 10 2022: ALWB lacks glory for 45 Martyrs of Nicopolis; ANCA has 6R+4. Possible Slavic/ANCA hymnography beyond Greek base.
  - Sep 27 2020, Jul 23 2023, Oct 27 2024: ALWB has a glory, ANCA used 7R+3 (Callistratus, Phocas, Nestor). Antiochian practice, or ANCA omits Glory. Unexplained. Note Typikon p.97 Oct 26-27 entry covers Demetrius/Sat order.
- "Alt-aware" variant (glory in main OR any alt) is no better (84/89): picking the lead commemoration is a separate Rule input.
- Key bias: only post-Pentecost Sundays; Feb-Jun/Dec-Jan feasts untested; ANCA is not Typikon authority, only the check.

## 5. Needed data and how the calendar exposes it

Explicit / inferred / missing per item:

| Item | Status | Source |
|---|---|---|
| Rule "has glory -> 6+4, else 7+3" | EXPLICIT | Typikon p.12, p.48 |
| Great-saint 4R+6 list | EXPLICIT | Typikon p.12 |
| Lord/Theotokos-context 4R+3+3 / aposticha / troparion effects | EXPLICIT | Typikon p.12-16 |
| Per-date `vespers_glory` for lead saint | INFERRED (ALWB cog, 93%) | ALWB Menaion; key-validate |
| Per-date `aposticha_glory`, `has_lauds` | INFERRED (ALWB, unvalidated) | ALWB `AposGlory`, `Lauds*` |
| Lead-commemoration choice when ALWB has alts / ANCA differs | MISSING | ANCA key observed; no source states it |
| British/UK-only saints | MISSING (assume unknown, not false) | `Menaion.british`; UK divergence log |
| Authoritative per-saint Menaion (printed HTM Menaia) | MISSING (not supplied; Typikon fn 41 p.62 names them) | - |
| Violakis | no per-saint glory data (only the rule, p.7, p.50) | - |

Proposed calendar shape:

1. New table `Menaion_Commem(date_key, seq, role[main|alt], name, vespers_glory, aposticha_glory, has_lauds, src, note)`. Tri-state values: 1 / 0 / NULL (unknown). Built by a `db/` script reading ALWB (boolean only). Keeps `Menaion` untouched.
2. Master `yocal_main`: add `saint_has_glory` (lead commemoration's `vespers_glory`), `glory_src` (`alwb|override|typikon`), propagate `Menaion.class` as `menaion_class` (already ask in #12/#15). Expose both in `api-php/lib.php::get_date_data` and `api/api.py::_get_date` (duplicated logic; change both).
3. `overrides` CSV (`db/glory_overrides.csv`: date_key, lead name, vespers_glory, evidence) for ANCA/Antiochian lead-commemoration differences (Nektarios Nov 9, Jul 12) and 7R+3 cases ALWB mislabels. Rule engine reads override first, then ALWB flag, then unknown.
4. Rule predicate `saint_has_glory` (closed context fact, #14): returns true/false/unknown; rules resolve unknown to `missing`, never default. Derived per-date; for Sunday only the Saturday-eve cell of the next date is used.
5. Not predictors: `major_commem` non-empty, `Menaion.class`. Do not use them as proxies, except Typikon p.12 list for 4R+6.

## 6. Open / follow-up

- Validate `vespers_glory` flag beyond post-Pentecost Sundays (Dec-Jan, Feb, Apr-Jun feasts) against ANCA `Abbr.pdf` once full-range harness (#20) exists.
- Adjudicate 3 ALWB-glory / ANCA-7R+3 cases (Sep 27, Jul 23, Oct 27): ANCA anomaly vs Antiochian practice. Possible check against Bp Basil Parish Typikon Charts (#11).
- How does the generator pick the lead commemoration when several saints? (ALWB alt vs ANCA vs yocal `major_commem`) -> needs a Rule or decision.
- UK-only saints: glory unknown, treat per divergence-log policy.
- Matins praises: confirm `has_lauds` predicts 4R+4 vs 8R with ANCA.
