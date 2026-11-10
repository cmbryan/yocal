# ALWB Menaion day files (untracked prototype data)

Local copy of AGES Liturgical Workbench `Books-Collections/Menaion` for the principal-commemoration prototype (#30, #26, #13). Do not commit `data/` (text).

## Source (fetched 2026-11-09, shallow clones into `data/`)
- Greek (flags): https://github.com/AGES-Initiatives/ages-alwb-library-gr-gr-cog @ a3be51ac70a10c9c803d2276f0f8711bb90e8718 (2026-03-15). Licence: none stated (all rights reserved by default). Use flags only.
- English (names): https://github.com/AGES-Initiatives/ages-alwb-library-en-us-dedes @ 3b8de5fefbfee135141948c9f39fb9e2c0072c88 (2026-03-15). CC BY-NC-SA 4.0 (c) Fr. Seraphim Dedes.
- Path in each repo: `net.ages.liturgical.workbench.library_*/Books-Collections/Menaion/mMM/me.mMM.dDD_*.ares`.

## Refetch
    cd data
    git clone --depth 1 https://github.com/AGES-Initiatives/ages-alwb-library-gr-gr-cog.git
    git clone --depth 1 https://github.com/AGES-Initiatives/ages-alwb-library-en-us-dedes.git

## Extract
    cd data && python3 -I ../extract.py ages-alwb-library-gr-gr-cog/net*/Books-Collections/Menaion \
      ages-alwb-library-en-us-dedes/*/Books-Collections/Menaion > ../menaion_commems.csv

Columns: date_key (MM-DD, or MM-HF/AC/BC/FF for 5 movable-Sunday files), role (main|alt1|alt2|alt3), name (English, else Greek), has_vespers_glory (Greek `meVE.SticGlory.text` non-empty), glory_en (same in English; subset of Greek), name_lang.

## Format notes
- `key = "value"` lines; `alt1.`/`alt2.`/`alt3.` prefix = alternate commemoration block, none = main.
- Names: English `meDA.commemoration.first_short` / `.full` (prefix "Memory of "); Greek `first_name` mostly empty. Use English glory only as cross-check (Greek is fuller).
- Rank (`meHO.rank`) empty everywhere.
