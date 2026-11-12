"""Compose one service for a date: parish PDF template + Rules -> hymn ids -> saved texts (texts.py) + music.

The Rules alone decide which hymn goes where (yocal_rules.hymns). ANCA/DCS pages are only text/music sources (saved once,
by hymn id) and answer keys. Not yet converted (still read from the date's ANCA/DCS page): seasonal_hymns, dcs_text, music.
"""
from __future__ import annotations

import datetime as dt
import re

from . import anca_read, db, music, template, texts, translations
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


def _tone_of(h: str) -> str:
    m = re.search(r"TONE (\w+)", h, re.I)
    return m.group(1).title() if m else ""


def _nice_heading(h: str) -> str:
    """'KONTAKION OF ENTRANCE OF THE THEOTOKOS IN TONE FOUR' -> 'Kontakion of Entrance of the Theotokos in Tone Four'."""
    h = re.sub(r"\s*\([^)]*\)", "", h).strip().title()
    h = re.sub(r"\b(Of|The|In|For|And)\b", lambda m: m.group(1).lower(), h).replace("Ss.", "SS.").replace("Ss ", "SS. ")
    return h[:1].upper() + h[1:]



def dcs_antiphon(day: Day, n: int) -> list:
    """Festal antiphon n from the DCS page (verses that belong to a Menaion date, `psLI.mMM.dDD.antiphonN`), with their refrains; [] if none."""
    name = {1: "FIRST", 2: "SECOND", 3: "THIRD"}[n]
    out, on, refr = [], False, []
    festal = False

    def flush():
        if refr:
            out.append(_P("Choir", "Refrain: " + " ".join(refr), "dcs"))
            refr.clear()
    for r in day.dcs:
        if r["kind"] == "heading":
            on = r["text"].upper().startswith(f"PRAYER OF {name} ANTIPHON")
            continue
        if not on or r["kind"] != "text":
            continue
        if re.search(rf"\.m\d+\.d\w+\.antiphon{n}\.v\d+\.text$", r["field"]):
            flush()
            festal = True
            out.append(_P("Choir", "Verse: " + r["text"], "dcs"))
        elif re.search(rf"hoLI\.Antiphon{n}\d?\.text$|^pr\.antiphon{n}\.", r["field"]):
            refr.append(r["text"])
        elif n == 3 and re.search(r"Apolytikion\d*\.text$", r["field"]) and r["topic"].startswith("me."):
            flush()
            out.append(_P("Choir", r["text"], "dcs", "Apolytikion"))
    flush()
    return out if festal else []



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
    return [_P("Deacon", f"The reading is from the Holy Gospel according to {_GOSPEL.get(book, book)}. [{loc}]", "yocal")]


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


# ------------------------------------------------------------------ seasonal hymns (ANCA headings -> replace booklet blocks)
def _bmatch(b: dict, m: dict) -> bool:
    return all(re.search(rx, str(b.get(k) if k != "slot" else b.get("slot") or "") or "") for k, rx in m.items())


def seasonal_hymns(day: Day, sec_id: str, blocks: list, cfgs: list, store: dict, pending: list) -> list:
    for c in cfgs:
        if c["section"] != sec_id or (c.get("unless_anca") and day.ablocks(c["unless_anca"])):
            continue
        found = [b for b in day.ablocks(c["anca"]) if b["body"]]
        if not found and c.get("dcs_antiphon"):  # no ANCA heading (or file): festal antiphon verses on the DCS page
            paras = dcs_antiphon(day, c["dcs_antiphon"])
            if paras:
                new = {"t": "variable", "slot": f"{sec_id}_seasonal", "caption": ["Festal antiphon from the GOA Digital Chant Stand (no ANCA text for this date)"], "paragraphs": paras, "missing": False}
                out, idx = [], None
                for b in blocks:
                    if any(_bmatch(b, m) for m in c.get("drop", [])):
                        idx = len(out) if idx is None else idx
                        continue
                    out.append(b)
                blocks = out[:len(out) if idx is None else idx] + [new] + out[len(out) if idx is None else idx:]
            continue
        if not found:
            continue
        paras, heads = [], []
        for h in found:
            ps, k, pend = translations.resolve(h, store=store)
            for p in ps:
                p.setdefault("heading", None)
            ps[0]["heading"] = _nice_heading(h["heading"])
            paras += ps
            heads.append(_nice_heading(h["heading"]))
            if pend:
                pending.append({"section": sec_id, "key": k, "heading": heads[-1]})
        new = {"t": "variable", "slot": f"{sec_id}_seasonal", "caption": ["Seasonal replacement from ANCA's Liturgy Variables for this date"], "paragraphs": paras, "missing": False}
        out, idx = [], None
        for b in blocks:
            if any(_bmatch(b, m) for m in c.get("drop", [])):
                if idx is None:
                    idx = len(out)
                continue
            out.append(b)
        if idx is None and c.get("after"):
            idx = next((i + 1 for i, b in enumerate(out) if _bmatch(b, c["after"])), len(out))
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
    store = translations.load()
    hymn_cfgs = template.config().get("seasonal_hymns", [])
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
        blocks = seasonal_hymns(day, sec["id"], blocks, hymn_cfgs, store, pending)
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
