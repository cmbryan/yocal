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
- Variable parts (`compose.py`): rules engine gives the caption/determination; text from GOA DCS, else ANCA Liturgy Variables (each paragraph tagged with its source). Dismissal = parish text with ANCA's phrase/saints substituted.
- Music (`music.py`, `db.py`): ANCA PDF hyperlinks (read from the PDF annotations) first, then every DCS score for the hymn (all composers, Byzantine + Western). SQLite `db/yocal/YOCal_Music.db` (override `YOCAL_MUSIC_DB`) keeps URL, source, label, bytes, sha256, fetch time and rendered PNG pages; `music_ref` records which assets served which slot/date. Dates with no DCS page reuse the last stored refs for fixed hymns.

## Known gaps / guesses
Alleluia verses; prokeimenon music (none published); Litany of Fervent Supplication text (booklet gives music only); Sunday-only; saint's communion hymn; seasonal rubrics collapsed; the booklet is Tone 6/Nov 8 so Nov-8-specific text (Archangels) is replaced by rules/ANCA/DCS content. Only DCS 2026 is online.

## Seasonal rubrics
Bracketed rubrics in the booklet are conditional. `seasonal:` in `data/liturgy_sections.yaml` maps each (by opening text) to a `when` condition on calendar facts (`pascha_days`, `season`) (a deacon is always assumed). Applies -> inlined with a "Seasonal: ..." tag; not -> omitted; no mapping -> collapsed "Seasonal rubric". `/api/service` lists each decision under `seasonal`.
Silent priest prayers (`[Silently ...]`) are collapsed in the UI. The memorial section is excluded (`exclude: true`). Not yet covered: other-season variations absent from this booklet (see ANCA READ headings per season).

## Seasonal hymns (ANCA -> parish translation)
`seasonal_hymns:` in `data/liturgy_sections.yaml`: when ANCA's Liturgy Variables for the date has a matching heading (antiphons, Eisodikon, Paschal/feast apolytikia/kontakia, Anti-Trisagion, Megalynarion, Koinonikon), it replaces the booklet blocks listed in `drop`. Text: `data/parish_translations.yaml` (our own translations, key = heading slug + hash of the ANCA text) -> badge "parish translation"; absent -> ANCA wording with badge "parish translation pending" and listed in `translations_pending`. `python -m yocal_service.translations 2026` lists/creates the keys needed. Liturgy of St Basil (calendar flag): banner + dismissal names Basil; the Cherubic Hymn does not change (Typikon, general rules IX: only Holy Thursday, Holy Saturday and the Presanctified differ).

## Communion hymn
Rules `yocal_rules/data/rules/communion.yaml` (Typikon Ch I s6 XI p.39) set `liturgy.communion.kind` for every Sunday. `praise_the_lord` -> Sunday hymn (DCS text); any other kind -> ANCA's Koinonikon heading (parish translation or pending). If the ANCA file exists but has no Koinonikon heading, the Sunday hymn is shown (ANCA wins; Rule/ANCA conflict on Aug 9 2026 Matthias is in the divergence log).

## Alleluia and prokeimenon by tone
Alleluia and its verses use the **tone of the week**, not Tone 2: a decided **divergence from the Typikon** (Ch I s6 VIII p.38), recorded as Rule `lit.alleluia.day_tone` (source `parish`, tier 3) with `conflict` -> `lit.alleluia.t2` (kept as the shadowed Typikon alternative). Verses: parish booklet (previous years, `booklet_readings.py`) first, else the GOA DCS readings pages (`dcs_tones.py`, all eight tones, built from `li2` pages over the published window). Both text stores are in git-ignored `local/`.
Rebuild: `python -m yocal_service.booklet_readings <booklet PDFs>`; `python -m yocal_service.dcs_tones`.
