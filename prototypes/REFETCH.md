# Refetching sources for the prototypes

Source files are not committed (copyright / licence). Derived small files (CSV/JSON/YAML, scripts) are. Page cites in tickets assume the editions below.

## Typikon (Antiochian) — local `Typikon.pdf`
- Book of the Typikon, trans. Bp Demetri Khoury, ed. Fr John W. Morris, **Miami, October 2011**, 583 pages, copy-protected.
- Source: https://www.equip-orthodox.com/app/download/20479026/54-typikon-full.pdf (no licence stated; do not commit).
- Verify: `pdftotext -layout Typikon.pdf - | tr -s ' \f\n\t' '\n' | sha256sum` = `295c69ccb39b4c13714bb24c251227e943edf5f45904f747c532338b45d37def` (compare extracted text, not the PDF bytes).
- Printed page = PDF page - 3.
- Derived: `typikon-ch5/` (`extract.py` -> `ch5_vespers.csv`), `rule-spike/gen_ch5_rules.py`.

## ANCA service texts (answer key) — `anca-index/`, `anca-compare/`
- Public PDFs on antiochian.org: `liturgicday` page per date -> `servicetexts/<Mon DD YYYY> VESP.pdf`, `Abbr.pdf`, `READ.pdf`. Site publishes ~1 month ahead; older files may be withdrawn.
- Committed: `anca-index/pages.json` (date -> liturgicday id + file links; identical copies `anca-compare/pages_snapshot*.json` are not committed), `anca-compare/compare.csv`, `sun_matins_kontakion.csv` (`*.log` are gitignored).
- Rebuild: `anca-index/scripts/` (playwright; `scrape.py` -> `pages.json`, throttled, resumable; `build_index.py`, `render.py`). Then download files listed in `pages.json` into `anca-compare/pdfs*/`.
- NOT committed: `anca-index/raw/`, `anca-compare/pdfs*/`, `txt/`, `sun_keys.csv` (contains service text; regenerate from the PDFs).
- Material includes copyrighted Holy Transfiguration Monastery text; keep local.

## AGES ALWB Menaion — `alwb-menaion/`
- Pinned clones and extract command: see `alwb-menaion/README.md` (SHAs a3be51ac…, 3b8de5fe…). `data/` is gitignored. Committed: `menaion_commems.csv`.

## Bp Basil (Essey), Parish Typikon charts — `BpBasil/` (local, untracked)
- dowama.org: index http://www.dowama.org/node/31 (also http://www.dowama.org/content/typikon); files under http://www.dowama.org/sites/docs/: `typicon_ranking_letter.pdf`, `Descriptions of Ranks.pdf`, `Ranking_of_Feasts_according_to_the_Typikon.pdf`, `RankingListOfFeastsAndCommemorations.pdf`, `Chart1.pdf`, `Chart2.pdf`, `Chart3.pdf`. URLs from the #11 research; not re-tested at time of writing.
- Committed: `bpbasil-rank/extract.py`, `ranks.csv` (flags only, no descriptions).

## Violakis, Typikon of the Great Church (1888) — `Violakis/` (local, untracked)
- Aristotle University of Thessaloniki: https://digital.lib.auth.gr/record/125938. **Manual browser download only** (HTTP 403 to scripts). CC BY-NC-ND: do not commit scans, OCR or translation. Full provenance in `Violakis/SOURCE.txt`.
- Files `001.pdf`-`005.pdf` (514 pages) SHA-256:
  - 001 `9b62a478…cecea8`, 002 `4c8b4826…d524`, 003 `7c8cceae…30aa`, 004 `a6147043…becd`, 005 `1de25bb5…5545`
- OCR regenerable: tesseract 5, `-l grc`, 200 dpi. `translation.md` / `greek.md` / `NOTES.md` are hand/agent work with no remote copy: back up outside git.

## Not reproducible from sources
- Violakis translation and notes (above); the research notes live on pushed `research/*` branches (throwaway, never merged).
- Hand-written rules in `rule-spike/rules/` are committed.
