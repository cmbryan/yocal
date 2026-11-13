"""Compose one service for a date: parish PDF template + Rules -> hymn ids -> saved texts (texts.py) + music.

The Rules alone decide which hymn goes where (yocal_rules.hymns). ANCA/DCS pages are only text/music sources (saved once,
by hymn id) and answer keys. Festal antiphons / entrance hymn / trisagion / megalynarion: Rules too (festal_hymns).
Not yet converted (still read from the date's ANCA/DCS page): dcs_text, music.
"""
from __future__ import annotations

import datetime as dt
import re

from . import anca_read, db, music, template, texts
from yocal_rules import anca as rules_anca, assemble, calfacts, hymns, render

SERVICES = {"liturgy": "Divine Liturgy"}


# ------------------------------------------------------------------ day texts
class Day:
    """Texts for the date from ANCA (Liturgy Variables) and the DCS; every lookup says where it came from."""

    def __init__(self, date: dt.date, offline: bool):
        self.date = date
        txt = rules_anca.fetch(date, "READ", music.CACHE, offline)
        self.anca = anca_read.parse(txt) if txt else []
        self.dcs = music.dcs_rows(date, offline)
        self.dcs2 = music.dcs_rows(date, offline, "li2")  # readings half: prokeimenon / Alleluia verses (a Menaion proper when the day has one)

    def dtexts(self, topic_rx: str, field_rx: str) -> list:
        return [r["text"] for r in self.dcs if r["kind"] == "text" and re.search(topic_rx, r["topic"]) and re.search(field_rx, r["field"])]

    def dfirst(self, topic_rx: str, field_rx: str):
        t = self.dtexts(topic_rx, field_rx)
        return t[0] if t else None

    def ablocks(self, heading_rx: str) -> list:
        return anca_read.find(self.anca, heading_rx)


def _P(role, text, source, heading=None):
    return {"role": role, "text": text, "source": source, **({"heading": heading} if heading else {})}


_NT = {"Acts": "the Acts of the Apostles", "Romans": "the Epistle of St Paul to the Romans", "Galatians": "the Epistle of St Paul to the Galatians",
       "Ephesians": "the Epistle of St Paul to the Ephesians", "Philippians": "the Epistle of St Paul to the Philippians",
       "Colossians": "the Epistle of St Paul to the Colossians", "Titus": "the Epistle of St Paul to Titus", "Philemon": "the Epistle of St Paul to Philemon",
       "Hebrews": "the Epistle of St Paul to the Hebrews", "James": "the Epistle of St James", "Jude": "the Epistle of St Jude",
       "1 Corinthians": "the First Epistle of St Paul to the Corinthians", "2 Corinthians": "the Second Epistle of St Paul to the Corinthians",
       "1 Thessalonians": "the First Epistle of St Paul to the Thessalonians", "2 Thessalonians": "the Second Epistle of St Paul to the Thessalonians",
       "1 Timothy": "the First Epistle of St Paul to Timothy", "2 Timothy": "the Second Epistle of St Paul to Timothy",
       "1 Peter": "the First Epistle of St Peter", "2 Peter": "the Second Epistle of St Peter",
       "1 John": "the First Epistle of St John", "2 John": "the Second Epistle of St John", "3 John": "the Third Epistle of St John"}
_GOSPEL = {"Matthew": "St Matthew", "Mark": "St Mark", "Luke": "St Luke", "John": "St John"}


def _ref(ref: str) -> tuple:
    """'1 Corinthians 4:5-8' -> ('1 Corinthians', '4:5–8')"""
    m = re.match(r"^(.*?)\s+(\d[\d:,\-–; .]*\S*)$", (ref or "").strip())
    return (m.group(1), m.group(2).replace("-", "–")) if m else (ref or "", "")


def _db_text(html: str) -> list:
    """yocal_lections text (HTML) -> paragraphs, without the leading '<em>reference</em><br>'."""
    t = re.sub(r"^\s*<em>.*?</em>\s*(<br\s*/?>)?", "", html or "", flags=re.S)
    out = []
    for p in re.split(r"(?:<br\s*/?>\s*){2,}", t):
        p = re.sub(r"\s+", " ", re.sub(r"<[^>]+>|%", " ", re.sub(r"<br\s*/?>", " ", p))).strip()
        if p:
            out.append(p)
    return out


def v_epistle_intro(day: Day, f: dict, **_):
    """Epistle and Gospel text always come from the yocal database (yocal_lections), never from DCS/ANCA."""
    book, loc = _ref(f.get("epistle_ref"))
    if not book:
        return []
    return [_P("Reader", f"The reading is from {_NT.get(book, book)}! [{loc}]", "yocal")]


def v_epistle(day: Day, f: dict, **_):
    return [_P("Reader", p, "yocal") for p in _db_text(f.get("epistle_text"))]


def v_gospel_intro(day: Day, f: dict, **_):
    book, loc = _ref(f.get("gospel_ref"))
    if not book:
        return []
    n = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", f.get("explanatory_notes") or "")).strip()  # DB explanatory note on the reading (rubric)
    note = [_P("", n, "yocal")] if n else []
    return note + [_P("Deacon", f"The reading is from the Holy Gospel according to {_GOSPEL.get(book, book)}. [{loc}]", "yocal")]


def v_gospel(day: Day, f: dict, **_):
    return [_P("Deacon", p, "yocal") for p in _db_text(f.get("gospel_text"))]



# ------------------------------------------------------------------ hymns: Rules -> hymn ids -> saved texts (never "what ANCA/DCS print today")
SRC = {"parish": "parish", "dcs": "dcs_pending", "anca": "anca_pending"}
ALLELUIA = "Alleluia! Alleluia! Alleluia!"


def hymn_paras(h: hymns.Hymn, t: dict | None, role: str = "Choir") -> list:
    """One hymn's paragraphs from its saved text t (texts.get); a visible gap when the text is not saved yet."""
    if not t:
        return [{"role": "", "text": f"{h.label}: text not saved yet", "source": "gap", "heading": h.label, "hymn": h.id}]
    src = SRC[t["source"]]
    mk = lambda r, text, head=None: {"role": r, "text": text, "source": src, "credit": t["credit"], "hymn": h.id, **({"heading": head} if head else {})}
    ps = t["parts"]
    if h.kind == "prokeimenon":
        out = [_P("Deacon", "Let us attend!", "pdf"), mk("Reader", ps[0], h.label), mk("Choir", ps[0])]
        return out + ([mk("Reader", ps[1]), mk("Choir", ps[0])] if len(ps) > 1 else [])
    if h.kind == "alleluia":
        out = [mk("Choir", ALLELUIA, h.label)]
        for v in ps:
            out += [mk("Reader", v), mk("Choir", ALLELUIA)]
        return out
    if h.kind == "communion":
        return [mk("Choir", " ".join(ps).rstrip(".") + ". Alleluia, alleluia, alleluia.", h.label)]
    return [mk(role, p, h.label if i == 0 else None) for i, p in enumerate(ps)]


def slot_paras(ctx: dict, slot: str, pick=None) -> list:
    """Paragraphs for the hymns the Rules give a rules-engine slot; a gap paragraph if the Rule names no hymns yet."""
    hs = ctx["hymns"].get(slot)
    if hs is None:
        return []
    hs = pick(hs) if pick else hs
    out = []
    for h in hs:
        t = texts.get(ctx["con"], h.id, ctx["parish"])
        if t and t["pending"] and all(p["key"] != h.id for p in ctx["pending"]):
            ctx["pending"].append({"section": slot, "key": h.id, "heading": h.label, "source": t["source"]})
        out += hymn_paras(h, t)
    return out


def v_res_apolytikion(day, f, ctx, **_):
    """Sung with the 3rd antiphon: the resurrectional apolytikion of the Rules' apolytikia."""
    return slot_paras(ctx, "liturgy.apolytikia", lambda hs: [h for h in hs if h.id.startswith("oct/")][:1])


def v_apolytikia(day, f, ctx, **_):
    return slot_paras(ctx, "liturgy.apolytikia")


def v_kontakion(day, f, ctx, **_):
    return slot_paras(ctx, "liturgy.kontakion")


def v_prokeimenon(day, f, ctx, **_):
    return slot_paras(ctx, "liturgy.prokeimenon")


def v_alleluia(day, f, ctx, **_):
    """Tone of the week (parish practice; Typikon Tone 2 is the shadowed Rule lit.alleluia.t2)."""
    return slot_paras(ctx, "liturgy.alleluia")


def v_communion_hymn(day, f, ctx, **_):
    return slot_paras(ctx, "liturgy.communion")


_YEARS = re.compile(r"\s*\((?:\d[^)]*|[^)]*\b(?:c\.|C)\b[^)]*)\)")  # '(299)', '(4th C)', '(c. 1000)'


_TITLES = "Holy|Righteous|Venerable|Great|Blessed|Glorious|Hiero-?martyrs?|Great-?martyrs?|Martyrs?|Confessors?|Apostles?|Prophets?|Monk-?martyrs?"


def dismissal_names(name: str) -> str:
    """Calendar commemoration -> dismissal wording: dates dropped, 'Holy Martyr X' -> 'the holy martyr X'."""
    n = _YEARS.sub("", name or "").strip(" .")
    m = re.match(rf"^((?:{_TITLES})(?:\s+(?:and\s+)?(?:{_TITLES}))*)\b(.*)$", n)
    return f"the {m.group(1).lower()}{m.group(2)}" if m else n


def v_dismissal(day, f, ctx, template_text: str = "", **_):
    """Parish template with the Rules' characteristic phrase, Liturgy author and saint(s) of the day (calendar)."""
    d = ctx["dismissal"]
    txt = template_text
    if not txt:
        return []
    phrase = d["phrase"] or f"[characteristic phrase: {d['phrase_kind'] or 'to be determined'}]"
    txt = re.sub(r"May \[insert the appointed characteristic phrase\]", f"May {phrase}", txt)
    if d["saints"]:
        txt = re.sub(r"of N\., \[the saint\(s\) of the day\] whose memory we celebrate", f"of {dismissal_names(d['saints'])}, whose memory we celebrate", txt)
    else:
        txt = re.sub(r"of N\., \[the saint\(s\) of the day\] whose memory we celebrate and ", "and ", txt)
    saint = ("Basil the Great, archbishop of Cæsarea, whose Liturgy we have celebrated;" if d["author"] == "Basil the Great"
             else "John Chrysostom, archbishop of Constantinople, whose Liturgy we have celebrated;")
    txt = re.sub(r"John Chrysostom, archbishop of Constantinople; or Basil the Great,.*?we have celebrated;", saint, txt)
    out = [_P("Priest", txt, "pdf+rules")]
    if d["clause"]:
        out.append(_P("", f"Also name the feast in the {d['clause']} clause (Rule liturgy.dismissal_phrase).", "gap"))
    return out


RESOLVERS = {
    "res_apolytikion": v_res_apolytikion, "apolytikia": v_apolytikia, "kontakion": v_kontakion, "prokeimenon": v_prokeimenon,
    "epistle_intro": v_epistle_intro, "epistle": v_epistle, "alleluia": v_alleluia, "gospel_intro": v_gospel_intro, "gospel": v_gospel,
    "communion_hymn": v_communion_hymn, "dismissal": v_dismissal,
}
# which rules-engine slot explains each variable slot (for the caption)
ENGINE_SLOT = {"res_apolytikion": "liturgy.apolytikia", "apolytikia": "liturgy.apolytikia", "kontakion": "liturgy.kontakion",
               "prokeimenon": "liturgy.prokeimenon", "epistle_intro": "liturgy.epistle", "epistle": "liturgy.epistle",
               "alleluia": "liturgy.alleluia", "gospel_intro": "liturgy.gospel", "gospel": "liturgy.gospel",
               "dismissal": "liturgy.dismissal", "communion_hymn": "liturgy.communion"}


# ------------------------------------------------------------------ music
def attach_music(con, date, day: Day, sec_cfg: list, service: str, fetch: bool) -> list:
    anc = music.anca_candidates(date, offline=not fetch) if fetch else music.anca_candidates(date, offline=True)
    dcs = music.dcs_candidates(day.dcs)
    items = []
    for cfg in sec_cfg:
        cands = music.match(cfg, anc, dcs)
        assets = music.record(con, service, date, cfg["key"], cfg["title"], cands) if cands else music.previous_refs(con, service, cfg["key"])
        for a in assets[: music.MAX_PREFETCH if fetch else 0]:
            if not a["cached"] and not a["error"]:
                music.fetch_asset(con, a["id"])
        items.append({"key": cfg["key"], "title": cfg["title"], "assets": [music.asset_info(con, a["id"]) for a in assets]})
    return items


# ------------------------------------------------------------------ festal hymns (Rules -> replace booklet blocks)
def _bmatch(b: dict, m: dict) -> bool:
    return all(re.search(rx, str(b.get(k) if k != "slot" else b.get("slot") or "") or "") for k, rx in m.items())


_RISEN = "risen from the dead"


def _text(ctx: dict, hid: str, slot: str, label: str):
    """Saved text of a hymn id (texts.get), recording a pending translation; None if not saved."""
    t = texts.get(ctx["con"], hid, ctx["parish"])
    if t and t["pending"] and all(p["key"] != hid for p in ctx["pending"]):
        ctx["pending"].append({"section": slot, "key": hid, "heading": label, "source": t["source"]})
    return t


def _src(t: dict) -> dict:
    return {"source": SRC[t["source"]], "credit": t["credit"]}


def _swap_phrase(booklet: str, phrase: str) -> str | None:
    """Booklet refrain/ending with 'risen from the dead' replaced by the feast's phrase ('who sat on a donkey's colt.').
    A phrase that is a whole refrain ('Save us, O good Comforter.') replaces the booklet's 'Save us, O Son of God, …' head."""
    if _RISEN not in booklet:
        return None
    head, tail = booklet.split(_RISEN, 1)
    phrase = phrase.strip().rstrip(".")
    if phrase.lower().startswith("save us"):
        return phrase + tail
    return head + phrase + tail


def _refrain_para(ctx: dict, booklet: str, rid: str | None, slot: str) -> dict:
    """Refrain paragraph: the booklet's when rid is None, else the booklet's frame with the phrase saved under rid."""
    if not rid:
        return {"role": "Refrain", "text": booklet, "source": "pdf"}
    t = _text(ctx, rid, slot, "Refrain of the feast")
    txt = _swap_phrase(booklet, " ".join(t["parts"])) if t else None
    if not txt:
        return {"role": "Refrain", "text": f"Refrain of the feast: text not saved yet ({rid})", "source": "gap", "hymn": rid}
    return {"role": "Refrain", "text": txt, "hymn": rid, **_src(t)}


def antiphon_paras(ctx: dict, h: hymns.Hymn, booklet_refrain: str) -> list:
    """Festal antiphon: each verse of the feast followed by its refrain (1: booklet; 2: booklet frame + feast phrase; 3: a troparion)."""
    n, rid = h.meta["n"], h.meta.get("refrain")
    slot = "liturgy.antiphons"
    t = _text(ctx, h.id, slot, h.label)
    if not t:
        return [{"role": "", "text": f"{h.label}: verses not saved yet", "source": "gap", "heading": h.label, "hymn": h.id}]
    if n == 3:
        rt = _text(ctx, rid, slot, "Refrain (troparion)") if rid else None
        refr = ({"role": "Refrain", "text": rt["parts"][0], "hymn": rid, **_src(rt)} if rt else
                {"role": "Refrain", "text": f"Refrain: troparion not saved yet ({rid})", "source": "gap", "hymn": rid})
    else:
        refr = _refrain_para(ctx, booklet_refrain, rid, slot)
    out = []
    for i, v in enumerate(t["parts"]):
        out += [{"role": "Verse", "text": v, "hymn": h.id, **_src(t), **({"heading": h.label} if i == 0 else {})}, dict(refr)]
    if n == 1:
        out += [{"role": "Verse", "text": "Glory... Now...", "source": "pdf"}, dict(refr)]
    return out


def eisodikon_paras(ctx: dict, h: hymns.Hymn, booklet: str) -> list:
    """Festal entrance verse(s) + the booklet's ending ('O Son of God risen from the dead, save us …'), phrase of the feast if any."""
    slot = "liturgy.eisodikon"
    t = _text(ctx, h.id, slot, h.label)
    ending = booklet.split(". ", 1)[1] if ". " in booklet else booklet
    if h.meta.get("refrain"):
        p = _refrain_para(ctx, ending, h.meta["refrain"], slot)
        if p["source"] == "gap":
            return [{"role": "Choir", "text": f"{h.label}: ending of the feast not saved yet", "source": "gap", "heading": h.label, "hymn": h.id}]
        ending = p["text"]
    if not t:
        return [{"role": "Choir", "text": f"{h.label}: verse not saved yet", "source": "gap", "heading": h.label, "hymn": h.id}]
    return [{"role": "Choir", "text": " ".join(t["parts"]) + " " + ending, "heading": h.label, "hymn": h.id, **_src(t)}]


def festal_hymns(ctx: dict, sec_id: str, blocks: list, cfgs: list, captions: dict) -> list:
    """Replace booklet blocks by the festal hymns the Rules appoint (liturgy_sections.yaml `festal_hymns` says where).
    A slot whose hymns are [] (the booklet's ordinary text) or None (no structured hymns) leaves the booklet as it is."""
    for c in cfgs:
        if c["section"] != sec_id:
            continue
        hs = ctx["hymns"].get(c["slot"]) or []
        if c.get("n"):
            hs = [h for h in hs if h.meta.get("n") == c["n"]]
        if not hs:
            continue
        dropped = [b for b in blocks if any(_bmatch(b, m) for m in c.get("drop", []))]
        if c["slot"] == "liturgy.antiphons":
            refr = next((b["text"] for b in dropped if b.get("role") == "Refrain"), "")
            paras = antiphon_paras(ctx, hs[0], refr)
        elif c["slot"] == "liturgy.eisodikon":
            paras = eisodikon_paras(ctx, hs[0], next((b["text"] for b in dropped if b.get("role") == "Choir"), ""))
        else:
            paras = slot_paras(ctx, c["slot"])
        new = {"t": "variable", "slot": f"{sec_id}_festal", "caption": captions.get(c["slot"], []), "paragraphs": paras,
               "missing": not paras or all(p["source"] == "gap" for p in paras)}
        out, idx = [], None
        for b in blocks:
            if b in dropped:
                idx = len(out) if idx is None else idx
                continue
            out.append(b)
        idx = len(out) if idx is None else idx
        ins = ([{"t": "line", **c["lead"]}] if c.get("lead") else []) + [new]
        blocks = out[:idx] + ins + out[idx:]
    return blocks


# ------------------------------------------------------------------ compose
def _match(cond, v) -> bool:
    if isinstance(cond, list) and len(cond) == 2 and all(isinstance(x, (int, float)) for x in cond):
        return v is not None and cond[0] <= v <= cond[1]
    return v in cond if isinstance(cond, list) else v == cond


def applies(when, ctx: dict) -> bool:
    """`when`: list of alternatives (OR); each a dict fact -> [lo,hi] | list of values | value (AND); `[{}]` = always."""
    return any(all(_match(c, ctx.get(k)) for k, c in alt.items()) for alt in when)


def inline_seasonal(b: dict) -> list:
    """Seasonal block -> plain blocks: outer brackets and any leading condition phrase removed, tagged with its label."""
    bs = [dict(x) for x in b["blocks"]]
    bs[0]["text"] = re.sub(b.get("strip") or r"^\[", "", bs[0]["text"]).strip()
    bs[-1]["text"] = re.sub(r"\]\s*$", "", bs[-1]["text"]).strip()
    if bs[0]["t"] == "line" and not bs[0]["text"]:
        bs = bs[1:]
    for x in bs:
        x["seasonal"] = b.get("label") or "seasonal"
    return bs


def compose(date: dt.date, service: str = "liturgy", db_path: str | None = None, offline: bool = False, fetch_music: bool = True) -> dict:
    if service not in SERVICES:
        raise ValueError(f"service {service!r} not supported yet; available: {', '.join(SERVICES)}")
    if date.weekday() != 6:
        raise assemble.OutOfScope(f"{date}: the Liturgy builder currently covers Sundays")
    tpl = template.load()
    result = assemble.build(service, date, calfacts.DEFAULT_DB)
    f = result.facts
    engine = {s: {"label": m["label"], "status": x.status, "lines": render.describe(s, x, f), "fill": x.fill, "rule": (x.rule or {}).get("id")} for s, m, x in result.slots}
    day = Day(date, offline)
    con = db.connect(db_path)
    ctx = dict(f)
    seasonal, pending = [], []
    res = {s: x for s, _, x in result.slots}
    hctx = {"con": texts.load(), "parish": texts.parish_texts(), "pending": pending,
            "hymns": {s: hymns.for_slot(s, x, f) for s, x in res.items()},
            "dismissal": hymns.dismissal(res.get("liturgy.dismissal"), res.get("liturgy.dismissal_phrase"), f)}
    hymn_cfgs = template.config().get("festal_hymns", [])
    captions = {s: [c.lstrip("- ").strip() for c in e["lines"]] for s, e in engine.items()}
    sections = []
    for sec in tpl["sections"]:
        if sec.get("exclude"):
            continue
        blocks = []
        for b in sec["blocks"]:
            if b["t"] == "seasonal" and b.get("when"):
                ok = applies(b["when"], ctx)
                seasonal.append({"section": sec["id"], "label": b.get("label", ""), "applied": ok})
                if ok:
                    blocks.extend(inline_seasonal(b))
                continue
            if b["t"] != "slot":
                blocks.append(b)
                continue
            fn = RESOLVERS.get(b["slot"])
            paras = fn(day, f, ctx=hctx, engine=engine, template_text=b.get("template", "")) if fn else []
            cap = [c.lstrip("- ").strip() for c in engine.get(ENGINE_SLOT.get(b["slot"], ""), {}).get("lines", [])]
            blocks.append({"t": "variable", "slot": b["slot"], "caption": cap, "paragraphs": paras, "missing": not paras})
        blocks = festal_hymns(hctx, sec["id"], blocks, hymn_cfgs, captions)
        if sec.get("dcs_text") and sum(b["t"] == "line" for b in blocks) < 3:
            rx = re.compile(sec["dcs_text"], re.I)
            grab, on = [], False
            for r in day.dcs:
                if r["kind"] == "heading":
                    on = bool(rx.search(r["text"]))
                elif on and r["kind"] == "text" and r["field"].endswith(".text") and not r["topic"].startswith(("actors", "rubrical")):
                    grab.append(_P("", r["text"], "dcs"))
            if grab:
                blocks.append({"t": "variable", "slot": f"{sec['id']}_text", "caption": ["Text from the GOA Digital Chant Stand (the parish booklet gives this part as music only)"], "paragraphs": grab, "missing": False})
        sections.append({"id": sec["id"], "title": sec["title"], "optional": sec["optional"], "blocks": blocks,
                         "music": attach_music(con, date, day, sec["music"], service, fetch_music) if sec["music"] else []})
    names = render._items(f["other_commem"]) if f["other_commem"] else []
    return {
        "service": service, "service_title": SERVICES[service], "date": date.isoformat(), "weekday": date.strftime("%A"),
        "heading": f"{f['desig']}" + (f" · Tone {f['tone']}" if f["tone"] else "") + (f" · Eothinon {f['eothinon']}" if f["eothinon"] else ""),
        "gospel_designation": f.get("desig_g") or "", "principal": f.get("principal_name") or "", "commemorations": names, "uk_commemorations": f.get("uk_commem") or "",
        "tone": f["tone"], "template_source": tpl["source"], "complete": bool(f["in_slice"]), "incomplete_reasons": f.get("slice_reasons") or [],
        "engine": engine, "sections": sections, "seasonal": seasonal, "translations_pending": pending,
        "hymns": {s: [{"id": h.id, "label": h.label} for h in hs] for s, hs in hctx["hymns"].items() if hs}, "liturgy_author": f.get("liturgy_author"),
        "notes": ([f"Liturgy of St. {f['liturgy_author']}: the booklet text is St. John Chrysostom's. The priest's prayers differ; the Cherubic Hymn and the rest of the choir text are unchanged (Typikon, general rules IX)."] if f.get("liturgy_author") == "Basil the Great" else []),
        "sources": {"template": "Parish choir booklet (PDF)", "variable_text": "Rules -> hymn ids -> saved texts (parish, else GOA DCS / ANCA wording pending a parish translation)", "music": "ANCA service-text links, GOA Digital Chant Stand"},
    }
