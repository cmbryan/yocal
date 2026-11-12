"""Hymn texts by hymn id (yocal_rules.hymns): saved once in the store, used for every date the Rules appoint the hymn.

Precedence (parish decision): parish > GOA DCS > ANCA. DCS and ANCA wording is shown flagged "parish translation pending".
  parish: data/parish_texts.yaml (our own translations, committed), then parish booklet texts (texts/parish.jsonl)
  dcs:    texts/dcs.jsonl keyed by AGES 'topic|field', found through yocal_rules.hymns.dcs_keys(id)
  anca:   texts/anca.jsonl keyed by hymn id
Files live in the sources store (store.py: the private yocal_sources submodule). Ingest (re-running only adds/updates):
    python -m yocal_service.texts ingest [CACHE_DIR]     # every cached DCS page + DCS corpus + parish booklets
    python -m yocal_service.texts get HYMN_ID
"""
from __future__ import annotations

import fnmatch
import glob
import json
import os
import re
import sys

import yaml

from yocal_rules import hymns

from . import booklet_readings, dcs_page, store

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PARISH = os.path.join(DATA, "parish_texts.yaml")
CORPUS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local", "dcs_corpus.json")
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "yocal_rules")
SOURCES = ("dcs", "anca", "parish")


class Texts:
    """All saved texts, in memory: {source: {key: {key, text, origin, seen}}}. `save()` writes changed sources back."""

    def __init__(self, root: str | None = None):
        self.root = root or store.root()
        self.rows = {s: {r["key"]: r for r in store.read_jsonl(self._file(s))} for s in SOURCES}
        self.dirty = set()

    def _file(self, source: str) -> str:
        return os.path.join(self.root, "texts", f"{source}.jsonl")

    def find(self, source: str, key: str) -> dict | None:
        rows = self.rows[source]
        if "*" not in key:
            return rows.get(key)
        hit = sorted(k for k in rows if fnmatch.fnmatchcase(k, key))
        return rows[hit[0]] if hit else None

    def save(self):
        for s in self.dirty:
            store.write_jsonl(self._file(s), list(self.rows[s].values()), "key")
        self.dirty.clear()


_LOADED: dict = {}


def load(root: str | None = None) -> Texts:
    """Shared in-memory copy, reloaded when a texts file changes on disk (e.g. after a git pull of the sources)."""
    root = root or store.root()
    sig = tuple(os.path.getmtime(f) if os.path.exists(f) else 0 for f in (os.path.join(root, "texts", f"{s}.jsonl") for s in SOURCES))
    if _LOADED.get(root, (None,))[0] != sig:
        _LOADED[root] = (sig, Texts(root))
    return _LOADED[root][1]


def parish_texts(path: str = PARISH) -> dict:
    if not os.path.exists(path):
        return {}
    return {k: v for k, v in ((yaml.safe_load(open(path, encoding="utf-8")) or {}).get("texts") or {}).items() if (v or {}).get("text")}


def _clean(text: str) -> str:
    """Drop the DCS metrical phrase markers (' * ', ' ⁄ ') from text shown on the stand."""
    return re.sub(r"\s*[*⁄]\s*", " ", text).strip()


def _split(text: str) -> list:
    return [_clean(p) for p in re.split(r"\n\s*\n", text) if p.strip()]


def _row(tx: Texts, source: str, key: str):
    return tx.find(source, key)


def _dcs(con: Texts, hid: str):
    for alt in hymns.dcs_keys(hid):
        parts, origin = [], None
        for i, part in enumerate(alt):
            keys = part if isinstance(part, list) else [part]
            rows = [_row(con, "dcs", k) for k in keys]
            if not all(rows):
                if i == 0:
                    parts = None
                break  # later parts (verse 2, 3) are optional
            parts.append(_clean(" ".join(r["text"] for r in rows)))
            origin = origin or rows[0]["origin"]
        if parts:
            return parts, origin
    return None


def get(con: Texts, hid: str, parish: dict | None = None) -> dict | None:
    """-> {parts: [str], source, pending, credit} or None (not saved yet: a visible gap, never a per-date fallback)."""
    parish = parish_texts() if parish is None else parish
    if hid in parish:
        e = parish[hid]
        return {"parts": _split(e["text"]), "source": "parish", "pending": False, "credit": e.get("credit", "parish translation")}
    r = _row(con, "parish", hid)
    if r:
        return {"parts": _split(r["text"]), "source": "parish", "pending": False, "credit": r["origin"]}
    d = _dcs(con, hid)
    if d:
        return {"parts": d[0], "source": "dcs", "pending": True, "credit": d[1]}
    r = _row(con, "anca", hid)
    if r:
        return {"parts": _split(r["text"]), "source": "anca", "pending": True, "credit": r["origin"]}
    return None


# ------------------------------------------------------------------ ingest
def put(tx: Texts, source: str, key: str, text: str, origin: str, seen: str):
    """Add, or replace when this copy is from a newer page (a corrected translation). Call tx.save() to write."""
    old = tx.rows[source].get(key)
    if old and (old["seen"] > seen or old["text"] == text):
        return
    tx.rows[source][key] = {"key": key, "text": text, "origin": origin, "seen": seen}
    tx.dirty.add(source)


_HYMN_FIELD = re.compile(r"\.(text|chapverse)$")


def ingest_dcs_page(con, html: str, date: str, origin: str) -> int:
    n = 0
    for r in dcs_page.parse(html):
        if r["kind"] == "text" and _HYMN_FIELD.search(r["field"]) and not r["topic"].startswith(("actors", "rubrical", "pdf", "template", "client")):
            put(con, "dcs", f"{r['topic']}|{r['field']}", r["text"], origin, date)
            n += 1
    return n


def ingest_booklets(con) -> int:
    """Parish booklet prokeimena/Alleluia verses -> hymn ids (ordinary items: the booklet's Sunday tone; Forefathers: named Sunday)."""
    n = 0
    for it in booklet_readings.load():
        for kind in ("prokeimenon", "alleluia"):
            x = it.get(kind)
            if not x or not x.get("lines"):
                continue
            readers = [t for role, t in x["lines"] if role == "Reader"]
            if kind == "alleluia":
                parts = readers
                hid = f"lit/sun/t{x['tone']}/alleluia" if x["tone"] == it["sunday_tone"] else None
            else:
                parts = readers[:2]
                hid = ("named/forefathers/prokeimenon" if "Forefathers" in x["title"]
                       else f"lit/sun/t{x['tone']}/prokeimenon" if x["tone"] == it["sunday_tone"] else None)
            if hid and parts:
                put(con, "parish", hid, "\n\n".join(parts), f"parish booklet {it['booklet']}", it.get("date") or "")
                n += 1
    return n


def ingest(cache: str = CACHE, root: str | None = None) -> dict:
    con = Texts(root)
    stats = {"dcs_pages": 0, "dcs_texts": 0, "booklet": 0}
    for fn in sorted(glob.glob(os.path.join(cache, "dcs-*.html"))):
        m = re.search(r"dcs-(\d{4}-\d\d-\d\d)-(\w+)\.html$", fn)
        html = open(fn, encoding="utf-8").read()
        if not m or not html:
            continue
        stats["dcs_pages"] += 1
        stats["dcs_texts"] += ingest_dcs_page(con, html, m.group(1), f"GOA DCS {m.group(1)} {m.group(2)}")
    if os.path.exists(CORPUS):
        for r in json.load(open(CORPUS, encoding="utf-8")):
            if _HYMN_FIELD.search(r["field"]):
                put(con, "dcs", f"{r['topic']}|{r['field']}", r["text"], f"GOA DCS {r['date']} li", r["date"])
                stats["dcs_texts"] += 1
    stats["booklet"] = ingest_booklets(con)
    con.save()
    stats["stored"] = {s: len(r) for s, r in con.rows.items()}
    return stats


def main(argv=None):
    a = argv if argv is not None else sys.argv[1:]
    if a[:1] == ["ingest"]:
        print(ingest(*(a[1:2] or [CACHE])))
    elif a[:1] == ["get"] and len(a) > 1:
        print(json.dumps(get(load(), a[1]), ensure_ascii=False, indent=1))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
