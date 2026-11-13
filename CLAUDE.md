# yocal

## Rules decide, sources supply
Services are built from our Rules alone (`yocal_rules/`): Rules -> hymn ids (`yocal_rules/hymns.py`) -> saved text/music. ANCA and the GOA Digital Chant Stand (DCS) are text/music sources and answer keys, never the decider of which hymn is sung. A text not yet saved shows as a gap. Details: `yocal_rules/README.md`, `yocal_service/README.md`.

## YOCal DB is authoritative
Anything `db/yocal/YOCal_Master.db` encodes (readings and which lection is used, Liturgy author `basil`, tone, eothinon, designations, fore/after-feasts, commemorations, notes) is consumed as-is: Rules and `calfacts.py` never override, re-derive or ignore it. If it is wrong, fix the scripts/data that build it (`db/`), not the Rules. ANCA disagreeing with the DB is a Divergence-log entry.

## `yocal_sources/` submodule (private, copyrighted)
Downloaded texts and music, saved once and shared between machines: private repo `cmbryan/yocal_sources`, checked out at `yocal_sources/` (`store.py`; override with `YOCAL_SOURCES`). Third-party copyright: that content lives only in the submodule; this repo is public.

- Fresh clone: `git submodule update --init`. `db/yocal/YOCal_Music.db` is a local cache rebuilt from `yocal_sources/music/index.jsonl`.
- Anything that saves texts or music (`python -m yocal_service.texts ingest`, music fetch/prefetch) writes into `yocal_sources/`. Publishing is two commits, in order:
  1. inside `yocal_sources/`: commit, then `git push` (the main repo must never point at an unpushed commit);
  2. in the main repo: commit the updated `yocal_sources` pointer (alone or with the code change that produced it).
- Tests write only to a temp store: set `YOCAL_SOURCES` to a tmp dir (see the autouse fixture in `tests/yocal_service/test_service.py`).
- Keep `texts/*.jsonl` and `music/index.jsonl` sorted one-record-per-line through `store.write_jsonl` (stable diffs); music files are named by sha256 and never rewritten.
