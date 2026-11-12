"""Fill pending seasonal-hymn translations from sheet-music publishers' own text (GOA Digital Chant Stand pages), keeping the source.

1. `corpus`: every DCS Liturgy page in its published window -> paragraphs (date, heading, topic, text) in local/dcs_corpus.json.
2. `match`: each pending ANCA hymn paragraph -> the DCS paragraph with the most similar wording (archaisms normalised); accepted only
   above a threshold; the result goes to local/translations_harvested.yaml (git-ignored: third-party text) with the source noted.

    python -m yocal_service.harvest corpus [DAYS]
    python -m yocal_service.harvest match [THRESHOLD]
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import yaml

from . import anca_read, dcs_page, music, translations as tr

LOCAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local")
CORPUS = os.path.join(LOCAL, "dcs_corpus.json")
OUT = os.path.join(LOCAL, "translations_harvested.yaml")
ARCH = {"thou": "you", "thee": "you", "ye": "you", "thy": "your", "thine": "your", "hath": "has", "doth": "does", "art": "are", "hast": "have",
        "dost": "do", "shalt": "shall", "wilt": "will", "unto": "to", "saith": "says", "o": ""}
STOP = set("the a an and of to in on for is are was be by with as at from that this it his her their our your my i we you he she they who whom which".split())


def toks(t: str) -> set:
    w = [ARCH.get(x, x) for x in re.findall(r"[a-z']+", t.lower())]
    return {re.sub(r"(s|ed|ing)$", "", x) for x in w if x and x not in STOP and len(x) > 1}


def sim(a: set, b: set) -> float:
    return 2 * len(a & b) / (len(a) + len(b)) if a and b else 0.0


def corpus(days: int = 400, workers: int = 8):
    from yocal_rules import dcs as rules_dcs
    start = dt.date.today()
    dates = [start + dt.timedelta(days=i) for i in range(days)]

    def one(d):
        try:
            h = rules_dcs.fetch(d, "li", music.CACHE, False)
        except Exception:
            return d, None
        return d, h

    out = []
    with ThreadPoolExecutor(workers) as ex:
        for d, html in ex.map(one, dates):
            if not html:
                continue
            for r in dcs_page.parse(html):
                if r["kind"] == "text" and r["field"].endswith(".text") and not r["topic"].startswith(("actors", "rubrical", "miscellanea", "template")):
                    out.append({"date": d.isoformat(), "topic": r["topic"], "field": r["field"], "text": r["text"]})
    os.makedirs(LOCAL, exist_ok=True)
    json.dump(out, open(CORPUS, "w", encoding="utf-8"))
    print(f"{len(out)} paragraphs from {len({o['date'] for o in out})} dates -> {CORPUS}")


def _anca_body(key: str, dates: list) -> list | None:
    from yocal_rules import anca
    for d in dates:
        t = anca.fetch(dt.date.fromisoformat(d), "READ", music.CACHE, True)
        for b in anca_read.parse(t or ""):
            if tr.key(b["heading"], b["body"]) == key:
                return b["body"]
    return None


def _window(body: list, corp: list, threshold: float):
    """Whole-hymn match for a multi-verse body: the run of consecutive DCS rows (one date) whose combined wording best fits it."""
    t = toks(re.sub(r"\b(Refrain|Verse):", " ", " ".join(body)))
    if not t:
        return None
    seeds = sorted(range(len(corp)), key=lambda i: -len(t & corp[i]["_t"]))[:40]
    best, bs = None, 0.0
    for i in seeds:
        for a in range(max(0, i - 7), i + 1):
            u = set()
            for b in range(a, min(len(corp), i + 8)):
                if corp[b]["date"] != corp[i]["date"]:
                    break
                u |= corp[b]["_t"]
                sc = sim(t, u)
                if sc > bs and 0.8 <= len(u) / len(t) <= 1.25 and b >= i:
                    best, bs = (a, b), sc
    if best and bs >= threshold:
        a, b = best
        return [c["text"].strip() for c in corp[a:b + 1] if c["text"].strip()], [f"{corp[a]['date']} {corp[a]['topic']}"], round(bs, 2)
    return None


def match(threshold: float = 0.5):
    corp = json.load(open(CORPUS, encoding="utf-8"))
    for c in corp:
        c["_t"] = toks(c["text"])
    corp = [c for c in corp if not c["topic"].startswith("prayers")]  # priest's prayers/doxologies are not hymns
    store = tr.load()
    res = yaml.safe_load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else None
    res = (res or {}).get("translations", {})
    done = 0
    for key, e in sorted(store.items()):
        if (e.get("text") or "").strip() or key in res:
            continue
        body = _anca_body(key, e.get("dates") or [])
        if not body:
            continue
        paras, srcs, scores = [], [], []
        for p in body:
            p2 = re.sub(r"^(Refrain|Verse):\s*", "", p)
            t = toks(p2)
            best = max(corp, key=lambda c: sim(t, c["_t"]))
            s = sim(t, best["_t"])
            if not 0.75 <= len(best["_t"]) / max(len(t), 1) <= 1.4:  # a fragment (one verse of several) or a longer passage: not the same piece
                s = min(s, 0.0)
            scores.append(round(s, 2))
            if s < threshold:
                paras = None
                break
            txt = best["text"].strip()
            i = corp.index(best)
            while txt.endswith("…") and i + 1 < len(corp) and corp[i + 1]["date"] == best["date"] and corp[i + 1]["text"].lstrip().startswith("…"):
                i += 1  # DCS splits a hymn across rows ("…tombs…" / "…He has granted life")
                txt = txt.rstrip("…").rstrip() + " " + corp[i]["text"].strip().lstrip("…")
            paras.append(txt)
            srcs.append(f"{best['date']} {best['topic']}")
        if not paras and len(body) > 0:
            w = _window(body, corp, threshold)
            if w:
                paras, srcs, scores = w[0], w[1], [w[2]]
        if not paras:
            print(f"  no match  {key}  scores {scores}")
            continue
        res[key] = {"heading": e["heading"], "text": "\n\n".join(paras), "provenance": "dcs",
                    "source": "GOA Digital Chant Stand, Divine Liturgy page, " + "; ".join(sorted(set(srcs))), "match": scores}
        done += 1
    os.makedirs(LOCAL, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("# Harvested from sheet-music publishers' text (third-party; git-ignored). `source` = where each text came from; `match` = wording similarity to ANCA's.\n")
        yaml.safe_dump({"translations": res}, fh, allow_unicode=True, sort_keys=True, width=100)
    print(f"{done} new, {len(res)} total -> {OUT}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["corpus"]:
        corpus(int(a[1]) if len(a) > 1 else 400)
    elif a[:1] == ["match"]:
        match(float(a[1]) if len(a) > 1 else 0.5)
    else:
        print(__doc__)
