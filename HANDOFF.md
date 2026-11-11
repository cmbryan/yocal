# Handoff: build the service-assembly Rules engine

Map (spec): https://github.com/cmbryan/yocal/issues/5 (closed, design-complete). Read it first, then zoom ticket links for detail. Vocabulary: `GLOSSARY.md`. Source/refetch: `prototypes/REFETCH.md`.

## Goal
Generate a review of Saturday Great Vespers, Sunday Matins, Sunday Liturgy and Major feasts (+ preceding Vespers) for Antiochian UK: output lists Variable parts (placeholder hymn refs) chosen by cited Rules. Check against ANCA answer key; unexplained ANCA diff on an explicit/inferred Rule = blocking.

## Start here
- `prototypes/rule-spike/`: YAML Rule schema (slot-grain, specificity tiers, closed context facts, provenance explicit/inferred/missing), `spike.py` harness (needs PyYAML, `pdftotext`, `db/yocal/YOCal_Master.db`, ANCA PDFs fetched to `--cache`). README has results (72 rules, 0 schema errors, 106/106 Sundays keyed). Throwaway: port, don't import.
- Data: `prototypes/anca-index/pages.json` (ANCA filenames), `alwb-menaion/menaion_commems.csv` (glory flags/names), `bpbasil-rank/ranks.csv`, `typikon-ch5/ch5_vespers.csv`, `principal-glory/out.csv`.
- Existing calendar: `db/yocal/YOCal_Master.db`, built by `db/*.py`; APIs `api/`, `api-php/`.
- Local-only (not in git): `Typikon.pdf` (Oct 2011; printed page = PDF page - 3), `Violakis/`, `BpBasil/`, ANCA PDFs. Never commit PDFs or long verbatim text; cite page/section.

## Key decisions (zoom tickets for detail)
- Rules: #14 representation/provenance; UK diff by stripped-vs-full run, not logged.
- Precedence: #15 behavioural classes from `Menaion.class`; liturgical-day unit; Major feast derived.
- Hymns: #16 Slot vs Hymn reference; keys-only ALWB map, no text fetch.
- Output: #17 review-by-exception + per-slot drill-down; `not in key` class.
- Audit/harness: #20; Source conflicts on the Rule (#39, #42, #43), Divergence log class-scoped.
- Principal/second commemoration + glory: #28, #31, #32, #34, #40. Kontakion: #25, #27. Basil/tone/eothinon: #19. Prokeimenon: #21-#24.
- Source authority: Typikon > ANCA > DCS > other; Violakis transcribed as printed, Bp Basil = evidence below Typikon/ANCA.

## Build order (vertical slices; ANCA key is the test oracle)
1. Port Rule loader/schema, context-fact vocabulary, slot catalogue, ref normaliser, tolerant Vespers parser; tests (`/tdd`). Prove on Nov 1 2026 Liturgy (#17).
2. Calendar columns: feast class propagation, fore/after-feast, Sunday-feast precedence, Major-feast flag, 2 glory columns on `Menaion`, ALWB name-match overrides (~30).
3. Wire decided Rules: Matins kontakion (#27), 4R+3+3 flag (#32), kontakion windows beyond Sep 22-Nov 7 (#25), Annunciation-on-Lent-Sunday Basil exception (#19).
4. Encode Typikon-vs-ANCA verdicts (#39/#42/#43) as Source conflicts; multi-label context facts (#37).
5. Rerun audit after each slice; track match rate (baseline: 75% of keyed cells encoded, 96.6% match; Major-feast weekends 23-35%).

## Known gaps (ship as missing/inferred, flagged)
Pentecostarion text, alleluia verses, weekday-feast Vespers Menaion content, Typikon p.11 vs p.174, some Triodion ANCA Vespers. Optional follow-up: #44 (Ascension/Pentecost leavetaking dates). Open conflicts needing more samples: Dormition leavetaking Sunday, Myrrhbearers St John, Jan 5 / 12 Apostles Glory (#43).

## Constraints
Planning of rules is done; no hymn text, chant, weekday services, non-English, or mobile/web app in scope. Public repo.

## Status and known limits (`yocal_rules/`, see its README)
- Package built: `python -m yocal_rules DATE vespers|matins|liturgy` and `python -m yocal_rules weekend DATE` (Sat Vespers + Sun Matins + Sun Liturgy + combined `build/service/YYYY-MM-DD-weekend.md`). Each service writes a service document (no provenance) and a supplement (gate, attention, slot detail, calendar facts, sources, Source conflicts).
- Rules in `data/rules/*.yaml` (tier, closed predicates, explicit/inferred/missing, optional `conflict`); Divergence log `data/divergence.yaml`; ANCA/DCS fetched over https and cached (`~/.cache/yocal_rules`, `--offline`).
- Slice: ordinary-season Sundays without Major feast or fore/after-feast. Outside it the document is marked Incomplete and unwritten slots read `[to be determined]` (Triodion, Pentecostarion, Major feasts and their Vespers, fore/after-feasts).
- Known gaps: Matins kontakion (#27), praises with a saint, kontakion windows (#25), alleluia verses, Pentecostarion text; saint-has-Glory from ALWB/Bp Basil is partly unreliable (Typikon Ch V count used on Sundays).
- Open Source conflicts (Typikon vs ANCA) are shadowed Rules with `conflict` notes; ANCA-pattern default is used pending a user decision.
- A few ANCA diffs remain unexplained or logged as class divergences (Dec 7 Glory, generic Fathers/All Saints dismissal, 4R+6 year variance).
- Tests: `PYTHONPATH=. python3 -m pytest tests/yocal_rules -q`. DB must be built; comparisons need network or a warm cache.

