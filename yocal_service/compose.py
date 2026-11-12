"""Compose one service for a date: parish PDF template + rules-engine determinations + day texts + music."""
from __future__ import annotations

import datetime as dt
import os
import re
import sys

from . import anca_read, booklet_readings, dcs_tones, db, music, template, translations
from yocal_rules import anca as rules_anca, assemble, calfacts, render

from .harvest import sim as harvest_sim, toks as harvest_toks

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


def v_res_apolytikion(day: Day, f: dict, **_):
    t = day.dfirst(r"^oc\.m\d", r"Apolytikion\.text$")
    if t:
        return [_P("Choir", t, "dcs", f"Resurrectional Apolytikion (Tone {f['tone']})")]
    for b in day.ablocks("RESURRECTIONAL APOLYTIKION"):
        return [_P("Choir", b["body"][0], "anca", f"Resurrectional Apolytikion (Tone {f['tone']})")]
    return []


def v_apolytikia(day: Day, f: dict, **_):
    out = v_res_apolytikion(day, f)
    for b in day.ablocks(r"^APOLYTIKION (FOR|OF)"):
        out.append(_P("Choir", b["body"][0], "anca", _nice_heading(b["heading"])))
    if not out:  # no Octoechos/ANCA text (e.g. Sunday after the Nativity): the Menaion apolytikia the DCS page lists at the entrance
        on = False
        for r in day.dcs:
            if r["kind"] == "heading":
                on = r["text"].upper().startswith("ENTRANCE PRAYER")
            elif on and r["kind"] == "text" and re.search(r"Apolytikion\d*\.text$", r["field"]) and r["topic"].startswith("me."):
                m = re.match(r"me\.m(\d+)\.d(\w+)", r["topic"])
                out.append(_P("Choir", r["text"], "dcs", f"Apolytikion (Menaion {m.group(1)}/{m.group(2)})" if m else "Apolytikion"))
    return out


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


def v_kontakion(day: Day, f: dict, engine: dict, **_):
    for b in day.ablocks(r"^KONTAKION"):
        return [_P("Choir", b["body"][0], "anca", _nice_heading(b["heading"]))]
    t = day.dfirst(r"^me\.", r"Kontakion\d*\.text$")
    if t:
        return [_P("Choir", t, "dcs", "Kontakion")]
    fp = (f.get("feast_period") or "").split(":")  # fore/afterfeast: the feast's own kontakion, from the DCS page of the feast day
    mmdd = next((k for k, v in calfacts.MAJOR_FIXED.items() if len(fp) == 2 and v[0] == fp[1]), None)
    if mmdd:
        feast = dt.date(int(f["date"][:4]), int(mmdd[:2]), int(mmdd[3:]))
        for back in (0, 7, 14, 21):  # the feast-day page may omit it; the preceding Sundays (prefeast) carry the same kontakion
            for r in music.dcs_rows(feast - dt.timedelta(days=back), False):
                if r["kind"] == "text" and r["topic"].startswith("me.") and re.search(r"Kontakion\d*\.text$", r["field"]):
                    return [_P("Choir", r["text"], "dcs", f"Kontakion of the feast ({feast:%b} {feast.day})")]
    return []


def _epistle_parts(day: Day):
    for b in day.ablocks(r"^THE EPISTLE"):
        txt = " ".join(b["body"])
        m = re.search(r"(The reading (?:is )?from .*?\([\d:,\-– ]+\))\s*(.*)$", txt, re.I)
        if m:
            return txt[:m.start()].strip(), m.group(1).strip(), m.group(2).strip()
    return "", "", ""


def _booklet(x: dict, n: int, head: str) -> list:
    out = []
    for i, (role, text) in enumerate(x["lines"][:n]):
        p = {"role": role, "text": text, "source": "parish", "credit": f"parish booklet {x['booklet']}"}
        if i == 0:
            p["heading"] = head
        out.append(p)
    return out


def dcs_proper(day: Day, kind: str) -> dict:
    """The day's own prokeimenon/Alleluia verses on the DCS readings page (`psLI.mMM.dXX.<kind>.vK`, a saint or feast), {} if it uses the Sunday tone's."""
    out = {}
    for r in day.dcs2:
        m = r["kind"] == "text" and re.match(rf"^psLI\.m\d+\.d\w+\.{kind}\.v(\d)\.text$", r["field"])
        if m:
            out[f"v{m.group(1)}"] = r["text"].strip()
    return out


def _pk_paras(refrain: str, verse: str, source: str, head: str, credit: str = "") -> list:
    mk = lambda role, text, h=None: {"role": role, "text": text, "source": source, **({"heading": h} if h else {}), **({"credit": credit} if credit else {})}
    out = [_P("Deacon", "Let us attend!", "pdf"), mk("Reader", refrain, head), mk("Choir", refrain)]
    return out + ([mk("Reader", verse), mk("Choir", refrain)] if verse else [])


def anca_prokeimenon(day: Day, f: dict) -> list:
    """ANCA decides which prokeimenon (the one it prints in the Epistle block, labelled with whose it is). Wording: the parish booklet's or the
    DCS's text of the same hymn when one matches ANCA's (similar wording), else ANCA's own text flagged as pending a parish translation."""
    pre, _, _ = _epistle_parts(day)
    if not pre:
        return []
    parts = re.split(r"(?<=[.!?])\s+", pre.strip(), maxsplit=1)
    a_ref, a_verse = parts[0], parts[1] if len(parts) > 1 else ""
    label = next((re.sub(r"^\(|\)$", "", x.strip()) for b in day.ablocks(r"^THE EPISTLE") for x in b["sub"][:1]), "")
    owner = re.sub(r"^For\s+", "", label)
    head = f"Prokeimenon (Tone {f.get('tone')})" if (not owner or "after Pentecost" in owner) else f"Prokeimenon (of {owner[:1].lower() + owner[1:] if owner.startswith('The ') else owner})"
    t = harvest_toks(a_ref)
    cands = []  # (similarity, rank, paragraphs); parish wording ranks before DCS
    for it in booklet_readings.load():
        x = it.get("prokeimenon")
        if x and len(x["lines"]) >= 3:
            cands.append((harvest_sim(t, harvest_toks(x["lines"][0][1])), 0, _pk_paras(x["lines"][0][1], x["lines"][2][1], "parish", head, f"parish booklet {it['booklet']}")))
    for tone_v in [dcs_tones.get(f.get("tone")).get("prokeimenon") or {}, dcs_proper(day, "prokeimenon")]:
        if tone_v.get("v1"):
            cands.append((harvest_sim(t, harvest_toks(tone_v["v1"])), 1, _pk_paras(tone_v["v1"], tone_v.get("v2", ""), "dcs", head)))
    ok = [c for c in cands if c[0] >= 0.5]
    if ok:
        return max(ok, key=lambda c: (round(c[0], 1), -c[1], c[0]))[2]
    return _pk_paras(a_ref, a_verse, "anca_pending", head)


def v_prokeimenon(day: Day, f: dict, **_):
    av = anca_prokeimenon(day, f)
    if av:
        return av
    bk = booklet_readings.select("prokeimenon", f)
    if bk and bk.get("occasion"):  # the parish's own text for the same feast (Forefathers, Sunday before the Nativity)
        return [_P("Deacon", "Let us attend!", "pdf")] + _booklet(bk, 4, f"Prokeimenon (Tone {bk['tone']})")
    pr = dcs_proper(day, "prokeimenon")
    if pr.get("v1"):  # saint/feast prokeimenon (the DCS page uses it when the epistle is the saint's, and on the feast Sundays)
        a = {"role": "Reader", "text": pr["v1"], "source": "dcs", "heading": "Prokeimenon (of the saint/feast)"}
        return [_P("Deacon", "Let us attend!", "pdf"), a, _P("Choir", pr["v1"], "dcs"),
                *([_P("Reader", pr["v2"], "dcs"), _P("Choir", pr["v1"], "dcs")] if pr.get("v2") else [])]
    if bk:  # the Sunday tone's, parish wording
        return [_P("Deacon", "Let us attend!", "pdf")] + _booklet(bk, 4, f"Prokeimenon (Tone {bk['tone']})")
    refrain = day.dfirst(r"^liturgical\.verses", r"sunday\.m\d\.prokeimenon\.v1\.text") or ""
    verse = day.dfirst(r"^liturgical\.verses", r"sunday\.m\d\.prokeimenon\.v2\.text") or ""
    src = "dcs"
    if not refrain:
        pre, _, _ = _epistle_parts(day)
        parts = re.split(r"(?<=[.!?])\s+", pre, maxsplit=1)
        if pre:
            refrain, verse, src = parts[0], parts[1] if len(parts) > 1 else "", "anca"
    if not refrain:
        pv = dcs_tones.get(f.get("tone")).get("prokeimenon") or {}
        if pv.get("v1"):  # the tone's Sunday prokeimenon from the DCS readings pages
            refrain, verse, src = pv["v1"], pv.get("v2", ""), "dcs"
    if not refrain:
        return []
    return [_P("Deacon", "Let us attend!", "pdf"), _P("Reader", refrain, src, f"Prokeimenon (Tone {f['tone']})"), _P("Choir", refrain, src),
            _P("Reader", verse, src), _P("Choir", refrain, src)] if verse else [_P("Reader", refrain, src, f"Prokeimenon (Tone {f['tone']})"), _P("Choir", refrain, src)]


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


def _tone_para(role: str, text: str, tone, what: str, heading: str | None = None) -> dict:
    p = _P(role, text, "dcs", heading)
    p["credit"] = dcs_tones.get(tone).get("source", "")
    return p


def v_alleluia(day: Day, f: dict, engine: dict | None = None, **_):
    """Alleluia and verses in the tone of the week (parish practice; the Typikon says Tone 2: a logged divergence, Rule lit.alleluia.day_tone)."""
    bk = booklet_readings.select("alleluia", f)
    if bk:
        return _booklet(bk, 5, f"The Alleluia (Tone {bk['tone']})")
    tone = f.get("tone")
    v = dcs_tones.get(tone).get("alleluia") or {}
    if v.get("v1"):
        a = "Alleluia! Alleluia! Alleluia!"
        return [_tone_para("Choir", a, tone, "alleluia", f"The Alleluia (Tone {tone})"), _tone_para("Reader", v["v1"], tone, "alleluia"), _tone_para("Choir", a, tone, "alleluia"),
                *([_tone_para("Reader", v["v2"], tone, "alleluia"), _tone_para("Choir", a, tone, "alleluia")] if v.get("v2") else [])]
    return [_P("", f"The Alleluia (Tone {tone})", "engine", "The Alleluia"), _P("Choir", "Alleluia! Alleluia! Alleluia!", "pdf"),
            _P("", "Verses of the day: not available from any source yet", "gap")]


def v_communion_hymn(day: Day, f: dict, engine: dict | None = None, **_):
    """Sunday hymn only when the rules say 'praise_the_lord' (Typikon Ch I s6 XI p.39); any other kind comes from ANCA's Koinonikon (seasonal_hymns)."""
    kind = ((engine or {}).get("liturgy.communion") or {}).get("fill", {}).get("kind")
    anca_silent = bool(day.anca) and not day.ablocks(r"^KOINONIKON")  # ANCA lists a heading only when it is not the Sunday hymn (project default: follow ANCA)
    if kind not in (None, "praise_the_lord") and not anca_silent:
        return []
    v = day.dfirst(r"^liturgical\.verses", r"sunday\.communion\.v1\.text")
    txt = (v or "Praise the Lord from the heavens, praise him in the highest.").rstrip(".") + ". Alleluia, alleluia, alleluia."
    return [_P("Choir", txt, "dcs" if v else "inferred", "Communion hymn (Sunday)")]


def v_dismissal(day: Day, f: dict, template_text: str = "", **_):
    """Parish template text with the day's phrase and saint(s) substituted; ANCA's dismissal supplies both."""
    txt = template_text
    anca_txt = ""
    for b in day.ablocks(r"^THE (GREAT )?DISMISSAL"):
        anca_txt = b["body"][0] if b["body"] else ""
    if not txt:
        return [_P("Priest", anca_txt, "anca")] if anca_txt else []
    phrase = (re.match(r"Priest:\s*May (.*?), Christ our true God", anca_txt) or [None, "he who rose from the dead"])[1]
    saints = (re.search(r"Joachim and Anna;\s*(?:of )?(.*?),?\s*whose memory we celebrate", anca_txt) or [None, None])[1]
    txt = re.sub(r"May \[insert the appointed characteristic phrase\]", f"May {phrase}", txt)
    if saints:
        txt = re.sub(r"of N\., \[the saint\(s\) of the day\] whose memory we celebrate", f"of {saints}, whose memory we celebrate", txt)
    else:
        txt = re.sub(r"of N\., \[the saint\(s\) of the day\]", f"of {f.get('principal_name') or 'the saint of the day'}", txt)
    saint = ("Basil the Great, archbishop of Cæsarea, whose Liturgy we have celebrated;" if f.get("liturgy_author") == "Basil the Great"
             else "John Chrysostom, archbishop of Constantinople, whose Liturgy we have celebrated;")
    txt = re.sub(r"John Chrysostom, archbishop of Constantinople; or Basil the Great,.*?we have celebrated;", saint, txt)
    return [_P("Priest", txt, "pdf+anca")]


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
            paras = fn(day, f, engine=engine, template_text=b.get("template", "")) if fn else []
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
        "engine": engine, "sections": sections, "seasonal": seasonal, "translations_pending": pending, "liturgy_author": f.get("liturgy_author"),
        "notes": ([f"Liturgy of St. {f['liturgy_author']}: the booklet text is St. John Chrysostom's. The priest's prayers differ; the Cherubic Hymn and the rest of the choir text are unchanged (Typikon, general rules IX)."] if f.get("liturgy_author") == "Basil the Great" else []),
        "sources": {"template": "Parish choir booklet (PDF)", "variable_text": "ANCA Liturgy Variables, GOA Digital Chant Stand", "music": "ANCA service-text links, GOA Digital Chant Stand"},
    }
