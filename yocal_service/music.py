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

from . import anca_links, dcs_page, db
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


def asset_info(con, aid: int) -> dict:
    r = con.execute("SELECT id, url, source, title, label, form, mime, size, fetched_at, error, content IS NOT NULL AS cached FROM music_asset WHERE id=?", (aid,)).fetchone()
    d = dict(r)
    d["cached"] = bool(d["cached"])
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
    row = con.execute("SELECT url, content IS NOT NULL AS cached FROM music_asset WHERE id=?", (aid,)).fetchone()
    if row is None:
        raise KeyError(aid)
    if row["cached"] and not force:
        return asset_info(con, aid)
    try:
        req = urllib.request.Request(row["url"], headers=UA)
        with urllib.request.urlopen(req, timeout=60) as resp:
            data, mime = resp.read(), resp.headers.get_content_type()
        if data.startswith(b"%PDF"):
            mime = "application/pdf"
        elif row["url"].endswith(".mp3"):
            mime = "audio/mpeg"
        con.execute("UPDATE music_asset SET content=?, mime=?, sha256=?, size=?, fetched_at=?, error=NULL WHERE id=?",
                    (data, mime, hashlib.sha256(data).hexdigest(), len(data), dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), aid))
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
    row = con.execute("SELECT content, mime FROM music_asset WHERE id=?", (aid,)).fetchone()
    if not row or not row["content"] or row["mime"] != "application/pdf":
        return None
    with tempfile.TemporaryDirectory() as d:
        pdf = os.path.join(d, "a.pdf")
        open(pdf, "wb").write(row["content"])
        subprocess.run(["pdftoppm", "-r", "130", "-png", pdf, os.path.join(d, "p")], check=False, capture_output=True)
        files = sorted(f for f in os.listdir(d) if f.startswith("p") and f.endswith(".png"))
        for i, f in enumerate(files, 1):
            con.execute("INSERT OR REPLACE INTO music_page VALUES(?,?,?)", (aid, i, open(os.path.join(d, f), "rb").read()))
    con.commit()
    r = con.execute("SELECT png FROM music_page WHERE asset_id=? AND page=?", (aid, page)).fetchone()
    return r[0] if r else None
