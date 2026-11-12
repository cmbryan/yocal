"""The sources store: downloaded texts and music, saved once, shared between machines as a private git repo.

Lives in the `yocal_sources` submodule (private: copyrighted content), or wherever YOCAL_SOURCES points. Plain files:
    texts/<source>.jsonl     one text per line {key, text, origin, seen}, sorted by key (source = dcs | anca | parish)
    music/files/<sha256>.<ext>   downloaded scores/recordings, named by content (never change once added)
    music/index.jsonl        one asset per line {url, file, sha256, source, title, label, form, mime, size, fetched_at, hymns}
Everything else (SQLite asset ids, rendered PNG pages) is a local cache rebuilt from these files.
"""
from __future__ import annotations

import json
import os
import threading

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "yocal_sources")
_LOCK = threading.Lock()


def root() -> str:
    return os.environ.get("YOCAL_SOURCES", ROOT)


def path(*parts: str) -> str:
    return os.path.join(root(), *parts)


def read_jsonl(p: str) -> list:
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def write_jsonl(p: str, rows: list, sort_key: str):
    """Rewrite atomically, sorted, one compact line per record (stable diffs)."""
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with _LOCK:
        with open(tmp, "w", encoding="utf-8") as fh:
            for r in sorted(rows, key=lambda r: r[sort_key]):
                fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
        os.replace(tmp, p)
