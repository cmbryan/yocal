# yocal_rules

Generates the **Variable parts** of Saturday Great Vespers, Sunday Matins and Sunday Divine Liturgy (placeholder hymn references, readings, tones) by evaluating cited **Rules** against the YOCal calendar, then reviews the result against the ANCA service texts and the GOA Digital Chant Stand (DCS). No hymn text is produced.

## Requirements
- Python 3.10+, `PyYAML`, `pytest` (tests). `pdftotext` (poppler-utils) on PATH for ANCA PDFs.
- Built calendar DB `db/yocal/YOCal_Master.db` (git-ignored; build with `db/*.py`, see `db/0_yocal_scripts_explained.txt`).
- Network only for the comparison step (ANCA, DCS over https). Use `--no-compare` or `--offline` otherwise.
- `pip install pyyaml pytest` (requirements.txt/requirements_dev.txt are updated where missing).

Run from the repo root.

## Usage
```
python -m yocal_rules 2026-10-31 vespers      # Saturday (the evening before the Sunday)
python -m yocal_rules 2026-11-01 matins
python -m yocal_rules 2026-11-01 liturgy --print
python -m yocal_rules weekend 2026-10-31      # all three + combined file; DATE = Saturday or any day Mon-Sun of that weekend
```
Options: `--out DIR` (default `build/service`), `--db`, `--cache DIR`, `--offline`, `--no-compare`, `--no-dcs`, `--no-anca`, `--strip-uk`, `--print`, `--fail-on-diff` (exit 2 on an unexplained ANCA diff). A summary line goes to stderr, file paths to stdout.
Mon-Fri dates in `weekend` resolve to the coming Saturday; a Sunday resolves to the day before.

## Outputs (in `--out`)
- `YYYY-MM-DD-<service>.md`: the **service document**. What the service needs only: Variable parts, no rules or provenance. Ends with a footer naming slots marked `[to be determined]`. `weekend` also writes `YYYY-MM-DD-weekend.md` (Saturday's date): the three documents concatenated under one heading.
- `YYYY-MM-DD-<service>-supplement.md`: the **supplement**, for the reviewer.
  - *Summary*: gate (BLOCKED = ANCA diff on an explicit/inferred Rule with no Divergence-log entry), slot counts by status, match/diff counts per source, cautions about the saint-has-Glory fact.
  - *Attention*: only what needs a look: diffs, key-only slots, missing Rules, inferred Rules, open Source conflicts.
  - *Slot detail*: per slot the chosen value, Rule id/status/tier (and any shadowed Rules), source + locator, ANCA and DCS verdicts.
  - *Calendar facts used*: the context facts the Rules saw.
  - *Comparison sources*: which ANCA/DCS files were used or why none.
  - Source conflicts: shown in Attention and in the Source/locator column (marked "Source conflict") where a Rule carries `conflict`.

## ANCA / DCS fetching
ANCA file names come from the committed `data/anca_pages.json`; PDFs are downloaded from antiochian.org, converted with `pdftotext -layout`, and cached. DCS pages (`dcs.goarch.org`) are read for hymn keys only. Default cache `~/.cache/yocal_rules` (override `--cache`). `--offline` uses cached files only (missing key = "no key"). Nothing downloaded is committed.

## Slice and out-of-scope behaviour
- Out of scope (exit 1, error message): other days or services, unless the date is a fixed Major feast.
- **In slice** = ordinary-season Sunday with no fixed Major feast and no fore/after-feast. Outside the slice (Triodion/Pentecostarion seasons, Major feasts, fore/after-feasts) the document is still produced, headed **Incomplete** with the reasons, and slots whose Rules are not yet written show `[to be determined]` (status `missing` in the supplement). Tone, readings and names from the calendar are still shown.
- `slices.yaml` `supported_fixed_major`: `mm-dd` enables a fixed Major feast on a weekday/Saturday; `mm-dd:sunday` enables its Sunday order (`data/rules/major_feasts_sunday.yaml`, ordinary season only): 09-08, 02-02, 11-21, 08-15, each verified against cached ANCA texts. `mm-dd:Weekday` (feast-day weekday) enables that feast's Matins/Liturgy only on that weekday (never its eve Vespers): `03-25:Monday` (ANCA 2019), `03-25:Wednesday` (ANCA 2026). `mm-dd:sunday@N` enables the Sunday order on the Sunday N days from Pascha, eve Vespers included: `03-25:sunday@-14` (Annunciation on Lent 5, ANCA 2018; `major_feasts_annunciation_lent5.yaml`). `01-01:sunday` enables Circumcision/St Basil on a Sunday (`major_feasts_jan1_sunday.yaml`; Typikon p.165-166, ANCA 2022-12-31 Vespers and 2023-01-01 only, so single-sample: Source conflicts open; Liturgy prokeimenon `missing`). Nativity and Theophany on a **Monday** have Typikon-only Rules (p.145-148, p.174-176; `major_feasts_nat_thy_monday.yaml` plus Tue-Sat Rules widened with `feast_not_sunday`) but stay disabled (no ANCA text): Incomplete; `tests/yocal_rules/test_major_monday.py` runs the Rules without the slice gate (Rules never read `in_slice`). Transfiguration, Elevation (ANCA publishes no Sunday text: 2023-08-06/2025-09-14 liturgicday pages list none; cache files are 0 bytes), Nativity, Theophany, Presentation on a Triodion Sunday, and Annunciation on other Sundays stay Incomplete on a Sunday. A Sunday feast adds the `matins.evlogetaria` slot.
- `slices.yaml` `supported_major_eve_vespers` (`mm-dd:Weekday` of the eve) enables only the eve Great Vespers of a fixed Major feast, leaving that feast's Matins/Liturgy Incomplete (Annunciation: Sunday and Tuesday eves, ANCA 2019/2026; Mon/Wed/Thu/Fri eves have no ANCA text).

## Divergence log
`data/divergence.yaml` (all `data/divergence*.yaml` are read): accepted, class-scoped differences between our output and an answer key. A diff matching no entry is *unexplained*, and for ANCA on an explicit/inferred Rule it blocks the gate. Entry:
```yaml
- slot: liturgy.dismissal        # or a list of slots
  source: anca                   # anca | dcs
  scope: {mmdd: ["07-14"]}       # context facts (any fact in the supplement's facts list, plus `service`); list = any of
  ours: {saint_named: true}      # optional: our attrs (subset match)
  theirs: {saint_named: false}   # optional: key attrs; a list = alternatives
  class: anca_generic_sunday_not_named
  reason: "why, with evidence"
```
Never log UK-origin differences (UK is excluded by construction). Never justify a Glory override by ANCA alone (`data/glory_overrides.yaml` needs an independent citation).

## Adding a Rule
Add to a new or existing `data/rules/*.yaml` (all files globbed except `slots.yaml`/`sources.yaml`, which are catalogues):
```yaml
- {id: mat.kathismata.res, slot: matins.kathismata, tier: 4, when: [{pred: sunday}],
   fill: {tone: "$tone"}, source: typikon, locator: "Ch I s5 p.21-22", status: explicit}
```
- `slot`: must exist in `slots.yaml` (append new slots there). `when`: predicates from the closed vocabulary `PREDS` in `rules.py` (AND-ed; `args` optional). `fill`: values for the slot attrs; `$name` takes a calendar fact.
- `tier`: specificity; lowest wins; a tie among matching Rules is a build error. Losing Rules are listed as *shadowed*.
- `source`: key in `sources.yaml` (typikon, anca, dcs, violakis, bpbasil). Authority: Typikon > ANCA > DCS > other. `locator`: printed page/section only, no long quotes.
- `status`: `explicit` (a Source states it; no `evidence`), `inferred` (needs `evidence`), `missing` (needs `ticket`; renders `[to be determined]`).
- `conflict` (optional): `{with: [rule ids or Typikon locators], status: open|accepted|misreading, note: "..."}`. Used where ANCA shows a well-evidenced pattern the default Rule follows and the Typikon reading is kept as a shadowed Rule; shown in the supplement as a Source conflict (user decision pending).
- New predicates/facts: add to `rules.py` / `calfacts.py`.

## Data files (`data/`)
- `menaion_commems.csv`: from `prototypes/alwb-menaion` (ALWB Menaion names/glory flags).
- `bpbasil_flags.csv`: built from the local Bp Basil ranking text: `python -I -m yocal_rules.tools.build_bpbasil_flags BpBasil/Ranking_of_Feasts_according_to_the_Typikon.txt` (flags only; Bp Basil is positive-only evidence for Glory).
- `anca_pages.json`: ANCA file index, from `prototypes/anca-index/pages.json`.
- `dcs_map.yaml`: keys-only DCS hymn key to hymn identity map. `glory_overrides.yaml`: cited glory overrides. `divergence.yaml`: see above.
- Typikon page numbers: printed page = PDF page - 3.

## Tests and sweep
```
PYTHONPATH=. python3 -m pytest tests/yocal_rules -q     # DB-dependent tests skip if the DB is absent
```
CLI weekend tests: `tests/yocal_rules/test_cli_weekend.py` (no network). Regression sweep over many dates against cached ANCA files: loop `python -m yocal_rules DATE SERVICE --offline --fail-on-diff --out /tmp/x` over Saturdays/Sundays and count exit-code 2 (unexplained diffs). Prototype harness: `prototypes/rule-spike/`.
