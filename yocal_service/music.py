"""Find, cache and serve the music for a service.

Sources, in preference order: ANCA service-text links (antiochian.org PDFs), then the GOA Digital Chant
Stand (DCS). Every asset keeps the URL it came from; content is fetched into SQLite (lazily or by `prefetch`).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import tempfile
import urllib.parse
import urllib.request

from . import anca_links, dcs_page, db, store
from yocal_rules import dcs as rules_dcs

UA = {"User-Agent": "yocal-service/0.1"}
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "yocal_rules")
MAX_PREFETCH = 4  # content fetched eagerly per music item; the rest on first view


def _humanize(url: str) -> str:
    name = urllib.parse.unquote(url.rsplit("/", 1)[-1])
    name = re.sub(r"\.(pdf|mp3)$", "", name, flags=re.I)
    return re.sub(r"[_\-]+", " ", name).strip()


# ---------------------------------------------------------------- candidates
def anca_candidates(date: dt.date, kinds=("READ",), offline: bool = False) -> list:
    """[{url, title, label, context, source:'anca', form}] from the date's ANCA PDFs (links cached as JSON)."""
    out = []
    for kind in kinds:
        fn = os.path.join(CACHE, f"anca-links-{date.isoformat()}-{kind}.json")
        if os.path.exists(fn):
            links = json.load(open(fn, encoding="utf-8"))
        elif offline:
            links = []
        else:
            pdf = anca_links.fetch_pdf(date, kind)
            links = anca_links.links(pdf) if pdf else []
            os.makedirs(CACHE, exist_ok=True)
            json.dump(links, open(fn, "w", encoding="utf-8"))
        for l in links:
            title = (l["context"] or l["label"] or _humanize(l["url"])).strip()
            out.append({"source": "anca", "url": l["url"], "title": title, "label": l["label"] or _humanize(l["url"]),
                        "context": l["context"], "form": "audio" if l["url"].endswith(".mp3") else "score"})
    return out


def dcs_rows(date: dt.date, offline: bool = False, code: str = "li") -> list:
    page = rules_dcs.fetch(date, code, CACHE, offline)
    return dcs_page.parse(page) if page else []


def dcs_candidates(rows: list) -> list:
    out, seen = [], set()
    for r in rows:
        if r["kind"] != "media":
            continue
        for a in r["assets"]:
            if a["url"] in seen:
                continue
            seen.add(a["url"])
            out.append({"source": "dcs", "url": a["url"], "title": r["title"], "label": a["label"] or "DCS", "form": a["form"], "context": r["section"]})
    return out


def _rank(c: dict) -> tuple:
    thy = 0 if "thyateira" in c["url"] or "Thyateira" in c["label"] else 1
    return (0 if c["source"] == "anca" else 1, {"score": 0, "western": 1, "byzantine": 2, "audio": 3}.get(c["form"], 4), thy)


def match(cfg: dict, anca: list, dcs: list) -> list:
    """Candidates for one template music entry {key,title,dcs?,anca?}: ANCA first, then DCS."""
    found = []
    if cfg.get("anca"):
        rx = re.compile(cfg["anca"], re.I)
        found += [c for c in anca if rx.search(c["context"] + " " + c["label"] + " " + c["url"].rsplit("/", 1)[-1])]
    if cfg.get("dcs"):
        rx = re.compile(cfg["dcs"])
        found += [c for c in dcs if rx.search(c["url"].rsplit("/", 1)[-1])]
    return sorted(found, key=_rank)


# ---------------------------------------------------------------- persistence
def upsert_asset(con, c: dict, title: str) -> int:
    con.execute("INSERT INTO music_asset(url, source, title, label, form) VALUES(?,?,?,?,?) "
                "ON CONFLICT(url) DO UPDATE SET label=excluded.label, form=excluded.form", (c["url"], c["source"], title, c["label"], c["form"]))
    return con.execute("SELECT id FROM music_asset WHERE url=?", (c["url"],)).fetchone()["id"]


def record(con, service: str, date: dt.date, slot_key: str, title: str, cands: list) -> list:
    """Persist candidates + refs; -> [asset rows as dicts]."""
    con.execute("DELETE FROM music_ref WHERE service=? AND date=? AND slot_key=?", (service, date.isoformat(), slot_key))
    out = []
    for rank, c in enumerate(cands):
        aid = upsert_asset(con, c, title)
        con.execute("INSERT OR REPLACE INTO music_ref VALUES(?,?,?,?,?,?)", (service, date.isoformat(), slot_key, title, aid, rank))
        out.append(asset_info(con, aid))
    con.commit()
    return out


_EXT = {"application/pdf": ".pdf", "audio/mpeg": ".mp3"}
INDEX = ("music", "index.jsonl")


def file_path(sha: str | None, mime: str | None) -> str | None:
    """Where an asset's bytes live in the sources store (named by content hash)."""
    return store.path("music", "files", sha + _EXT.get(mime or "", ".bin")) if sha else None


def content(con, aid: int) -> tuple:
    """-> (bytes | None, mime) from the sources store."""
    r = con.execute("SELECT sha256, mime FROM music_asset WHERE id=?", (aid,)).fetchone()
    fp = file_path(r["sha256"], r["mime"]) if r else None
    return (open(fp, "rb").read(), r["mime"]) if fp and os.path.exists(fp) else (None, r["mime"] if r else None)


def _index_put(row: dict):
    p = store.path(*INDEX)
    rows = {r["url"]: r for r in store.read_jsonl(p)}
    rows[row["url"]] = {**rows.get(row["url"], {}), **row}
    store.write_jsonl(p, list(rows.values()), "url")


def sync_index(con) -> int:
    """Teach the local cache every asset already saved in the sources store (a fresh machine, or after a git pull)."""
    n = 0
    for r in store.read_jsonl(store.path(*INDEX)):
        con.execute("INSERT INTO music_asset(url, source, title, label, form, mime, sha256, size, fetched_at) VALUES(?,?,?,?,?,?,?,?,?) "
                    "ON CONFLICT(url) DO UPDATE SET mime=excluded.mime, sha256=excluded.sha256, size=excluded.size, fetched_at=excluded.fetched_at, error=NULL",
                    (r["url"], r["source"], r.get("title", ""), r.get("label", ""), r.get("form", ""), r.get("mime"), r["sha256"], r.get("size"), r.get("fetched_at")))
        n += 1
    con.commit()
    return n


def export_db_blobs(con) -> int:
    """One-off migration: asset bytes kept in SQLite -> files + index in the sources store; the blob column is then cleared."""
    n = 0
    for r in con.execute("SELECT id, url, source, title, label, form, mime, sha256, size, fetched_at, content FROM music_asset WHERE content IS NOT NULL").fetchall():
        _save(r["url"], r["content"], r["mime"], dict(r), r["fetched_at"])
        con.execute("UPDATE music_asset SET content=NULL WHERE id=?", (r["id"],))
        n += 1
    con.commit()
    con.execute("VACUUM")
    return n


def _save(url: str, data: bytes, mime: str, meta: dict, when: str) -> str:
    sha = hashlib.sha256(data).hexdigest()
    fp = file_path(sha, mime)
    if not os.path.exists(fp):
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        open(fp, "wb").write(data)
    _index_put({"url": url, "file": os.path.basename(fp), "sha256": sha, "mime": mime, "size": len(data), "fetched_at": when,
                "source": meta["source"], "title": meta.get("title", ""), "label": meta.get("label", ""), "form": meta.get("form", "")})
    return sha


def asset_info(con, aid: int) -> dict:
    r = con.execute("SELECT id, url, source, title, label, form, mime, size, fetched_at, error, sha256 FROM music_asset WHERE id=?", (aid,)).fetchone()
    d = dict(r)
    fp = file_path(d.pop("sha256"), d["mime"])
    d["cached"] = bool(fp and os.path.exists(fp))
    d["pages"] = con.execute("SELECT COUNT(*) FROM music_page WHERE asset_id=?", (aid,)).fetchone()[0]
    return d


def previous_refs(con, service: str, slot_key: str) -> list:
    """Most recent stored refs for a slot (fixed hymns when the DCS has no page for the date)."""
    row = con.execute("SELECT date FROM music_ref WHERE service=? AND slot_key=? ORDER BY date DESC LIMIT 1", (service, slot_key)).fetchone()
    if not row:
        return []
    ids = [r[0] for r in con.execute("SELECT asset_id FROM music_ref WHERE service=? AND slot_key=? AND date=? ORDER BY rank", (service, slot_key, row[0]))]
    return [asset_info(con, i) for i in ids]


# ---------------------------------------------------------------- fetching
def fetch_asset(con, aid: int, force: bool = False) -> dict:
    """Download an asset into the DB (no-op if cached). -> asset_info."""
    row = con.execute("SELECT url, source, title, label, form FROM music_asset WHERE id=?", (aid,)).fetchone()
    if row is None:
        raise KeyError(aid)
    if asset_info(con, aid)["cached"] and not force:
        return asset_info(con, aid)
    try:
        req = urllib.request.Request(row["url"], headers=UA)
        with urllib.request.urlopen(req, timeout=60) as resp:
            data, mime = resp.read(), resp.headers.get_content_type()
        if data.startswith(b"%PDF"):
            mime = "application/pdf"
        elif row["url"].endswith(".mp3"):
            mime = "audio/mpeg"
        when = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        sha = _save(row["url"], data, mime, dict(row), when)  # saved once in the sources store
        con.execute("UPDATE music_asset SET mime=?, sha256=?, size=?, fetched_at=?, error=NULL WHERE id=?", (mime, sha, len(data), when, aid))
    except Exception as e:
        con.execute("UPDATE music_asset SET error=? WHERE id=?", (f"{type(e).__name__}: {e}", aid))
    con.commit()
    return asset_info(con, aid)


def page_png(con, aid: int, page: int) -> bytes | None:
    """PNG of one page of a cached PDF asset (rendered once, then stored)."""
    r = con.execute("SELECT png FROM music_page WHERE asset_id=? AND page=?", (aid, page)).fetchone()
    if r:
        return r[0]
    fetch_asset(con, aid)
    data, mime = content(con, aid)
    if not data or mime != "application/pdf":
        return None
    with tempfile.TemporaryDirectory() as d:
        pdf = os.path.join(d, "a.pdf")
        open(pdf, "wb").write(data)
        subprocess.run(["pdftoppm", "-r", "130", "-png", pdf, os.path.join(d, "p")], check=False, capture_output=True)
        files = sorted(f for f in os.listdir(d) if f.startswith("p") and f.endswith(".png"))
        for i, f in enumerate(files, 1):
            con.execute("INSERT OR REPLACE INTO music_page VALUES(?,?,?)", (aid, i, open(os.path.join(d, f), "rb").read()))
    con.commit()
    r = con.execute("SELECT png FROM music_page WHERE asset_id=? AND page=?", (aid, page)).fetchone()
    return r[0] if r else None
