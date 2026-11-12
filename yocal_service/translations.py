"""Parish translations of the seasonal hymns that the booklet lacks.

ANCA's Liturgy Variables supply the hymns for Pascha, Lent, feasts etc. Their wording is ANCA's translation, so each is looked up here
by key `<heading-slug>:<hash of the ANCA text>` in data/parish_translations.yaml. Found -> shown as the parish translation;
missing -> ANCA text is shown, flagged "parish translation pending". The file holds only our own translations (no ANCA text).

    python -m yocal_service.translations [FROM_YEAR [TO_YEAR]]   # list needed keys; add empty entries to the YAML
"""
from __future__ import annotations

import datetime as dt
import hashlib
import os
import re
import sys

import yaml

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "parish_translations.yaml")
HEADER = """# Parish translations of seasonal hymns (replace ANCA's wording). Fill `text`; blank line = new paragraph.
# Keys: <ANCA heading slug>:<hash of ANCA text>. `heading`/`dates` are hints only (where ANCA publishes it).
# `applies_to: [regex]` (optional) lets one entry also cover other headings whose slug matches (same hymn under another saint's name).
# Regenerate the list of needed keys with: python -m yocal_service.translations
"""


def slug(heading: str) -> str:
    h = re.sub(r"\([^)]*\)", "", heading)
    h = re.sub(r"\bIN TONE \w+\b", "", h, flags=re.I)
    return re.sub(r"[^a-z0-9]+", "-", h.lower()).strip("-")


def key(heading: str, body: list) -> str:
    norm = re.sub(r"\s+", " ", " ".join(body)).strip().lower()
    return f"{slug(heading)}:{hashlib.sha1(norm.encode()).hexdigest()[:8]}"


LOCAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local", "translations_harvested.yaml")  # git-ignored: text copied from third-party sources


def load_one(path: str = PATH) -> dict:
    if not os.path.exists(path):
        return {}
    return (yaml.safe_load(open(path, encoding="utf-8")) or {}).get("translations") or {}


def load(path: str = PATH) -> dict:
    """Our own translations (data/) override text copied from sheet-music sources (local/, git-ignored)."""
    out = {k: dict(v) for k, v in load_one(LOCAL).items()} if path == PATH else {}
    for k, v in load_one(path).items():
        if (v.get("text") or "").strip() or k not in out:
            out[k] = {**out.get(k, {}), **v}
    return out


def resolve(block: dict, role: str = "Choir", store: dict | None = None) -> tuple:
    """ANCA block {heading, body} -> (paragraphs, key, pending). Paragraph source is 'parish' or 'anca_pending'."""
    store = load() if store is None else store
    k = key(block["heading"], block["body"])
    ent = store.get(k) or {}
    txt = (ent.get("text") or "").strip()
    if not txt:  # an entry may cover other headings: `applies_to: [regex on the heading slug]` (same hymn, different ANCA heading/wording)
        sl = slug(block["heading"])
        ent = next((e for e in store.values() if (e.get("text") or "").strip() and any(re.search(rx, sl) for rx in e.get("applies_to") or [])), {})
        txt = (ent.get("text") or "").strip()
    if txt:
        src = {"dcs": "dcs_text"}.get(ent.get("provenance"), "parish")
        return [{"role": role, "text": p.strip(), "source": src, **({"credit": ent["source"]} if ent.get("source") else {})} for p in re.split(r"\n\s*\n", txt) if p.strip()], k, False
    return [{"role": role, "text": p, "source": "anca_pending"} for p in block["body"]], k, True


def scan(cfg_hymns: list, y0: int, y1: int) -> dict:
    """key -> {heading, dates} over every Sunday in the years, using the cached/fetched ANCA READ files."""
    from concurrent.futures import ThreadPoolExecutor
    from yocal_rules import anca
    from . import anca_read, music
    d = dt.date(y0, 1, 1)
    d += dt.timedelta(days=(6 - d.weekday()) % 7)
    days = []
    while d.year <= y1:
        days.append(d)
        d += dt.timedelta(weeks=1)

    def one(d):
        try:
            txt = anca.fetch(d, "READ", music.CACHE, False)
        except Exception:
            return d, []
        return d, anca_read.parse(txt) if txt else []

    out = {}
    with ThreadPoolExecutor(8) as ex:
        for d, blocks in ex.map(one, days):
            for c in cfg_hymns:
                if c.get("unless_anca") and anca_read.find(blocks, c["unless_anca"]):
                    continue
                for b in anca_read.find(blocks, c["anca"]):
                    if b["body"]:
                        e = out.setdefault(key(b["heading"], b["body"]), {"heading": re.sub(r"\s*\([^)]*\)", "", b["heading"]).strip(), "dates": []})
                        e["dates"].append(d.isoformat())
    return out


def main(argv=None):
    from . import template
    a = [int(x) for x in (argv if argv is not None else sys.argv[1:])]
    y0, y1 = (a + [a[0]])[:2] if a else (dt.date.today().year,) * 2
    need = scan(template.config()["seasonal_hymns"], y0, y1)
    store = load_one()
    for k, v in need.items():
        e = store.setdefault(k, {"heading": v["heading"], "text": None})
        e["heading"] = v["heading"]
        e["dates"] = sorted(set(e.get("dates") or []) | set(v["dates"]))
        e.setdefault("text", None)
    with open(PATH, "w", encoding="utf-8") as fh:
        fh.write(HEADER)
        yaml.safe_dump({"translations": store}, fh, allow_unicode=True, sort_keys=True, width=100, default_flow_style=False)
    merged = load()
    todo = [k for k, e in store.items() if not (merged.get(k, {}).get("text") or "").strip()]
    print(f"{len(store)} keys, {len(todo)} awaiting a parish translation -> {PATH}")
    for k in sorted(todo, key=lambda k: store[k]["dates"][0] if store[k].get("dates") else ""):
        print(f"  {k}  {store[k]['heading']}  ({', '.join(store[k].get('dates', [])[:3])})")


if __name__ == "__main__":
    main()
