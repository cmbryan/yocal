# yocal_service: chant-stand web app

Full Divine Liturgy for a chosen Sunday: parish booklet text + `yocal_rules` determinations + day texts (ANCA, GOA DCS) + music, as a web page for the stand and a JSON API. Liturgy only for now; the service selector and `compose.SERVICES` are where Matins/Vespers plug in.

## Run
```
pip install -r requirements.txt            # flask, pyyaml, pypdf, beautifulsoup4
python -m yocal_service.build_template '/path/to/Matins & Liturgy.pdf'   # once; writes local/liturgy_template.json (git-ignored)
flask --app yocal_service.app run --host 0.0.0.0 -p 5055
```
Open `http://HOST:5055/`. Before Sunday press **⬇ Music** (or `POST /api/prefetch?date=YYYY-MM-DD[&all=1]`) so scores are cached and the stand works offline. Needs `pdftotext`/`pdftoppm` (poppler), the calendar DB, network for first fetch.

## API
- `GET /api/services`, `GET /api/sundays?n=12`
- `GET /api/service?date=YYYY-MM-DD&service=liturgy[&offline=1][&music=1]` -> sections/blocks/variable parts/music refs (422 + `nearest_sunday` if not a Sunday)
- `POST /api/prefetch?date=...[&all=1]` download scores into the cache
- `GET /api/music/<id>[/file|/pages|/page/N.png]` cached asset (lazy fetch)

## Design
- Template (`template.py`, `data/liturgy_sections.yaml`): PDF text -> sections/blocks; notation noise filtered. The YAML holds structure only (anchors, variable spans, music matchers). **The extracted text is not committed** (copyrighted; public repo).
- **Rules decide, sources only supply.** Variable parts: Rules (`yocal_rules`) -> hymn ids (`yocal_rules/hymns.py`, grammar in `yocal_rules/data/hymns.yaml`) -> saved text (`texts.py`). ANCA and the GOA DCS are never asked *which* hymn; a hymn whose text is not saved yet shows as a gap. Epistle/Gospel: calendar DB. Dismissal: parish template + Rules (`liturgy.dismissal`, `liturgy.dismissal_phrase`) + calendar names.
- Sources store (`store.py`): the private submodule `yocal_sources/` (override `YOCAL_SOURCES`). Plain files, saved once, shared by git: `texts/{dcs,anca,parish}.jsonl` (one text per line, sorted; DCS keyed by AGES `topic|field`, parish booklet/ANCA by hymn id) and `music/files/<sha256>.pdf|mp3` + `music/index.jsonl`. Copyrighted: never in this repo. After adding texts/music, commit in `yocal_sources/` and bump the submodule pointer here.
- Text precedence parish (`data/parish_texts.yaml`, our own, committed) > parish booklets > GOA DCS > ANCA; DCS and ANCA wording is flagged "parish translation pending". `python -m yocal_service.texts ingest` reads every cached DCS page (with the label DCS prints before each text), the DCS corpus, the booklets and every cached ANCA READ file (`anca_texts.py`: each block saved under the hymn id its *heading* names, never from our Rules; ambiguous headings skipped and counted); `... texts get HYMN_ID` shows one. Fill the download cache once with `python -m yocal_service.crawl dcs|anca` (rate-limited, ~1 req/s).
- Verification (issue #64): `python -m yocal_service.texts verify [REPORT.md]`: for every hymn id the Rules appoint (Sundays to 2099) plus every saved id, word-overlap similarity between sources (DCS/ANCA/parish), DCS label kind and mode vs the id, saint named by the DCS label vs the calendar's principal commemoration, DCS keys shared by several ids. Status agree / weak / conflict / label / single (one source, unverified) / none.
- Local cache `db/yocal/YOCal_Music.db` (`YOCAL_MUSIC_DB`): asset ids, per-date refs, rendered PNG pages only. Safe to delete; rebuilt from `music/index.jsonl`.
- Checking: `yocal_rules` compares each slot's hymn ids with the ids a DCS page prints (`dcs.hymn_ids`, `hymns.id_from_dcs`); differences are listed in the supplement (DCS diffs are non-blocking, review them).
- Still page-driven (transitional, to be replaced by Rules): the DCS text of sections the booklet prints as music only (`dcs_text`), and music (`music.py`, matched per date; `hymn_music` is the per-hymn table it moves to). `tests/yocal_service/test_service.py::test_rule_slots_do_not_depend_on_anca_or_dcs` guards the converted slots.

## Known gaps / guesses
Alleluia verses; prokeimenon music (none published); Litany of Fervent Supplication text (booklet gives music only); Sunday-only; saint's communion hymn; seasonal rubrics collapsed; the booklet is Tone 6/Nov 8 so Nov-8-specific text (Archangels) is replaced by rules/ANCA/DCS content. Only DCS 2026 is online.

## Seasonal rubrics
Bracketed rubrics in the booklet are conditional. `seasonal:` in `data/liturgy_sections.yaml` maps each (by opening text) to a `when` condition on calendar facts (`pascha_days`, `season`) (a deacon is always assumed). Applies -> inlined with a "Seasonal: ..." tag; not -> omitted; no mapping -> collapsed "Seasonal rubric". `/api/service` lists each decision under `seasonal`.
Silent priest prayers (`[Silently ...]`) are collapsed in the UI. The memorial section is excluded (`exclude: true`). Not yet covered: other-season variations absent from this booklet (see ANCA READ headings per season).

## Festal hymns (Rules -> booklet blocks replaced)
Antiphons, entrance hymn, trisagion and megalynarion are decided by Rules on every Sunday (`yocal_rules/data/rules/festal_hymns.yaml`; feast days in `major_feasts*.yaml`, `pascha.yaml`). `festal_hymns:` in `data/liturgy_sections.yaml` only says where they go (`drop` = booklet blocks replaced). A slot whose Rule gives the ordinary kind keeps the booklet. Festal antiphons: verses of the feast (store), 1st refrain the booklet's, 2nd the booklet's frame with the feast's phrase (`lit/refrain2/<feast>`), 3rd the troparion the Rule names; entrance hymn: festal verse + the booklet's ending with that phrase. `data/parish_translations.yaml` / `translations.py` (ANCA-heading keys) are obsolete; parish wording goes in `data/parish_texts.yaml` by hymn id. Liturgy of St Basil (calendar flag): banner + dismissal names Basil; the Cherubic Hymn does not change (Typikon, general rules IX: only Holy Thursday, Holy Saturday and the Presanctified differ).

## Communion hymn
Rules `yocal_rules/data/rules/communion.yaml` (Typikon Ch I s6 XI p.39) set `liturgy.communion.kind` for every Sunday; `hymns.yaml` maps the kind (or the feast/saint from the calendar) to a hymn id. ANCA no longer overrides it; the Aug 9 2026 Matthias disagreement stays a logged divergence for review.

## Alleluia and prokeimenon by tone
Alleluia and its verses use the **tone of the week**, not Tone 2: a decided **divergence from the Typikon** (Ch I s6 VIII p.38), recorded as Rule `lit.alleluia.day_tone` (source `parish`, tier 3) with `conflict` -> `lit.alleluia.t2` (kept as the shadowed Typikon alternative). Verses: parish booklet (previous years, `booklet_readings.py`) first, else the GOA DCS readings pages (`dcs_tones.py`, all eight tones, built from `li2` pages over the published window). Both text stores are in git-ignored `local/`.
Rebuild: `python -m yocal_service.booklet_readings <booklet PDFs>`; `python -m yocal_service.dcs_tones`.
