"""Hymn texts by hymn id (yocal_rules.hymns): saved once in the store, used for every date the Rules appoint the hymn.

Precedence (parish decision): parish > GOA DCS > ANCA. DCS and ANCA wording is shown flagged "parish translation pending".
  parish: data/parish_texts.yaml (our own translations, committed), then parish booklet texts (texts/parish.jsonl)
  dcs:    texts/dcs.jsonl keyed by AGES 'topic|field', found through yocal_rules.hymns.dcs_keys(id)
  anca:   texts/anca.jsonl keyed by hymn id
Files live in the sources store (store.py: the private yocal_sources submodule). Ingest (re-running only adds/updates):
    python -m yocal_service.texts ingest [CACHE_DIR]     # every cached DCS page + DCS corpus + parish booklets + ANCA READ files
    python -m yocal_service.texts get HYMN_ID
    python -m yocal_service.texts verify [REPORT.md]     # issue #64: is each id's text really that hymn? (cross-source, labels)
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

from . import anca_texts, booklet_readings, dcs_page, store

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
    """-> (parts, origin, [rows used]) via the id's DCS keys (override first, then pattern), or None."""
    for alt in hymns.dcs_keys(hid):
        parts, origin, used = [], None, []
        for i, part in enumerate(alt):
            keys = part if isinstance(part, list) else [part]
            rows = [_row(con, "dcs", k) for k in keys]
            if not all(rows):
                if i == 0:
                    parts = None
                break  # later parts (verse 2, 3) are optional
            parts.append(_clean(" ".join(r["text"] for r in rows)))
            origin = origin or rows[0]["origin"]
            used += rows
        if parts:
            return parts, origin, used
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
def put(tx: Texts, source: str, key: str, text: str, origin: str, seen: str, **meta):
    """Add, or replace when this copy is from a newer page (a corrected translation). Call tx.save() to write.
    meta (optional, for verification): label = the heading the source prints before the text; tone."""
    old = tx.rows[source].get(key)
    meta = {k: v for k, v in meta.items() if v not in (None, "")}
    if old and (old["seen"] > seen or (old["text"] == text and all(old.get(k) == v for k, v in meta.items()))):
        return
    tx.rows[source][key] = {"key": key, "text": text, "origin": origin, "seen": seen, **meta}
    tx.dirty.add(source)


_HYMN_FIELD = re.compile(r"\.(text|chapverse)$")


def ingest_dcs_page(con, html: str, date: str, origin: str) -> int:
    n, label = 0, ""
    for r in dcs_page.parse(html):
        if r["kind"] in ("designation", "heading"):
            label = r["text"]  # what the page calls the text(s) that follow ("Apolytikion of the Feast. Mode 4.")
        elif r["kind"] == "text" and _HYMN_FIELD.search(r["field"]) and not r["topic"].startswith(("actors", "rubrical", "pdf", "template", "client")):
            put(con, "dcs", f"{r['topic']}|{r['field']}", r["text"], origin, date, label=label)
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


def _facts(date):
    """Calendar facts for a date (only to find the Menaion date of a saint an ANCA heading names); None if unavailable."""
    from yocal_rules import calfacts
    try:
        return calfacts.load_facts(date, "liturgy")
    except (LookupError, FileNotFoundError):
        return None


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
    stats["anca"] = dict(anca_texts.ingest(con, put, cache, _facts))
    con.save()
    stats["stored"] = {s: len(r) for s, r in con.rows.items()}
    return stats


# ------------------------------------------------------------------ verify (issue #64): is each id's text really that hymn?
AGREE, CONFLICT = 0.45, 0.25  # word-overlap similarity between two translations of one hymn (harvest.sim)
_KINDS = {"apolytikion": "apolytikion|troparion|dismissal", "troparion": "apolytikion|troparion|dismissal", "kontakion": "kontakion",
          "hypakoe": "hypakoe", "prokeimenon": "prokeimenon|psalm", "alleluia": "alleluia|psalm", "communion": "communion|koinonikon|psalm",
          "megalynarion": "megalynarion|hymn to the theotokos", "eisodikon": "entrance|eisodikon"}
_ALLKINDS = re.compile(r"\b(apolytikion|troparion|kontakion|hypakoe|prokeimenon|alleluia|communion|koinonikon|megalynarion|eisodikon)\b", re.I)
_PLAGAL = {"first": 5, "second": 6, "fourth": 8}


def mode_of(label: str):
    """'... Mode 4.' -> 4; 'Plagal of the First Mode' -> 5; 'Grave Mode' -> 7; else None."""
    m = re.search(r"\bPlagal (?:of the )?(First|Second|Fourth) Mode", label or "", re.I)
    if m:
        return _PLAGAL[m.group(1).lower()]
    if re.search(r"\bGrave Mode", label or "", re.I):
        return 7
    m = re.search(r"\bMode (\d)\b", label or "")
    return int(m.group(1)) if m else None


def needed_ids(start: str = "2026-11-15", end_year: int = 2100) -> dict:
    """Hymn id -> number of Sunday Liturgies (start .. end_year) whose Rules appoint it."""
    from collections import Counter
    import datetime as dt
    from yocal_rules import assemble
    need, d = Counter(), dt.date.fromisoformat(start)
    while d.year < end_year:
        r = assemble.build("liturgy", d)
        for s, _, x in r.slots:
            for h in hymns.for_slot(s, x, r.facts) or []:
                need[h.id] += 1
        d += dt.timedelta(weeks=1)
    return dict(need)


def _same_name(a: str, b: str) -> bool:
    """Two spellings name the same saint: a distinctive word in common (first 5 letters: Theodosios/Theodosius)."""
    from .anca_texts import STOP
    w = lambda s: {x[:5] for x in re.findall(r"[A-Z][A-Z'\-]{3,}", (s or "").upper()) if x not in STOP}
    return bool(w(a) & w(b))


def calendar_principal(mmdd: str):
    """Principal commemoration of a Menaion date (calendar DB, a non-leap year), '' if none."""
    import datetime as dt
    f = _facts(dt.date.fromisoformat(f"2027-{mmdd}")) if mmdd != "02-29" else None
    return (f or {}).get("principal_name") or ""


def verify(tx: Texts, need: dict, parish: dict | None = None, principal=calendar_principal) -> dict:
    """Per hymn id: texts from each source, pairwise similarity, DCS label kind/mode vs the id, duplicate DCS keys.
    status: agree | weak | conflict | single (one source: unverified) | none (no text)."""
    from .harvest import sim, toks
    parish = parish_texts() if parish is None else parish
    ids = sorted(set(need) | set(tx.rows["anca"]) | set(tx.rows["parish"]) | set(parish))
    out, by_key = {}, {}
    for hid in ids:
        srcs, notes = {}, []
        if hid in parish:
            srcs["parish"] = _split(parish[hid]["text"])
        elif hid in tx.rows["parish"]:
            srcs["parish"] = _split(tx.rows["parish"][hid]["text"])
        d = _dcs(tx, hid)
        if d:
            srcs["dcs"] = d[0]
            by_key.setdefault(d[2][0]["key"], []).append(hid)
            label = d[2][0].get("label", "")
            kind = re.sub(r"\d+$", "", hid.rsplit("/", 1)[-1])
            said = {w.lower() for w in _ALLKINDS.findall(label)}
            if said and kind in _KINDS and not re.search(_KINDS[kind], label, re.I):
                notes.append(f"DCS label names another kind: {label!r}")
            m = re.match(r"(?:oct|lit/sun)/t(\d)/", hid)
            want = int(m.group(1)) if m else None
            a = tx.rows["anca"].get(hid)
            want = want or (a or {}).get("tone")
            mode = mode_of(label)
            if want and mode and want != mode:
                notes.append(f"DCS label mode {mode} vs tone {want}: {label!r}")
            who = re.search(r"\bFor (?:St\.?|Sts\.?|Saint|the Holy|Holy)\s+(.+?)\.?$", label or "")
            mm = re.match(r"men/(\d\d-\d\d)/", hid)
            if who and mm and principal:
                p = principal(mm.group(1))
                if p and not _same_name(who.group(1), p):
                    notes.append(f"DCS label names {who.group(1)!r}, calendar principal is {p!r}")
        if hid in tx.rows["anca"]:
            srcs["anca"] = _split(tx.rows["anca"][hid]["text"])
        names = sorted(srcs)

        def score(a, b):  # whole text, or the best-matching part (short verses: refrain/verse translated differently)
            whole = sim(toks(" ".join(srcs[a])), toks(" ".join(srcs[b])))
            parts = [sim(toks(x), toks(y)) for x in srcs[a] for y in srcs[b]] if len(srcs[a]) > 1 or len(srcs[b]) > 1 else []
            return round(max([whole] + parts), 2)
        pairs = {f"{a}~{b}": score(a, b) for i, a in enumerate(names) for b in names[i + 1:]}
        lo = min(pairs.values()) if pairs else None
        status = ("none" if not srcs else "single" if not pairs else
                  "conflict" if lo < CONFLICT else "weak" if lo < AGREE else "agree")
        if notes and status in ("agree", "single"):
            status = "label"
        out[hid] = {"status": status, "uses": need.get(hid, 0), "sources": names, "sim": pairs, "notes": notes,
                    "dcs_key": d[2][0]["key"] if d else None, "text": {k: " / ".join(v)[:110] for k, v in srcs.items()},
                    "origin": (tx.rows["anca"].get(hid) or {}).get("origin")}
    dups = {k: v for k, v in by_key.items() if len(v) > 1}
    for k, v in dups.items():
        for hid in v:
            out[hid]["notes"].append(f"DCS key {k} also serves {[x for x in v if x != hid]}")
    return {"ids": out, "duplicate_keys": dups}


def report(res: dict) -> str:
    from collections import Counter
    ids = res["ids"]
    used = {h: r for h, r in ids.items() if r["uses"]}
    c = Counter(r["status"] for r in used.values())
    tot = sum(r["uses"] for r in used.values()) or 1
    L = [f"# Hymn text verification (issue #64)", "",
         f"Hymn ids appointed by the Rules (Sunday Liturgies to 2099): {len(used)}; by status: " + ", ".join(f"{k} {n}" for k, n in c.most_common()),
         f"Uses with a saved text: {100 * sum(r['uses'] for r in used.values() if r['status'] != 'none') / tot:.0f}%; "
         f"with 2+ agreeing sources: {100 * sum(r['uses'] for r in used.values() if r['status'] == 'agree') / tot:.0f}%",
         f"Ids with text not (yet) appointed by any Rule: {len(ids) - len(used)}", ""]
    for st in ("conflict", "label", "weak"):
        rows = sorted(((h, r) for h, r in ids.items() if r["status"] == st), key=lambda x: -x[1]["uses"])
        if rows:
            L += [f"## {st} ({len(rows)})", ""]
            for h, r in rows:
                L.append(f"- `{h}` uses {r['uses']} sim {r['sim']} key {r['dcs_key']}" + (f" anca: {r['origin']}" if r.get("origin") else "")
                         + (f" — {'; '.join(r['notes'])}" if r["notes"] else ""))
                for k, v in r["text"].items():
                    L.append(f"  - {k}: {v}")
            L.append("")
    if res["duplicate_keys"]:
        L += ["## ids sharing one DCS key", ""] + [f"- {k}: {v}" for k, v in res["duplicate_keys"].items()] + [""]
    miss = sorted(((h, r) for h, r in used.items() if r["status"] == "none"), key=lambda x: -x[1]["uses"])
    L += [f"## no text ({len(miss)})", "", ", ".join(f"`{h}` ({r['uses']})" for h, r in miss), ""]
    return "\n".join(L)


def main(argv=None):
    a = argv if argv is not None else sys.argv[1:]
    if a[:1] == ["ingest"]:
        print(ingest(*(a[1:2] or [CACHE])))
    elif a[:1] == ["verify"]:
        rep = report(verify(load(), needed_ids()))
        print(rep)
        if len(a) > 1:
            open(a[1], "w", encoding="utf-8").write(rep)
    elif a[:1] == ["get"] and len(a) > 1:
        print(json.dumps(get(load(), a[1]), ensure_ascii=False, indent=1))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
