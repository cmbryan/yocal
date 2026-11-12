"""Hymn identities for resolved slots: Rules + calendar facts -> the hymns a slot needs, by id (data/hymns.yaml).

The ids are what the text/music store is keyed by, so a hymn saved once serves every date the Rules appoint it.
Nothing here reads ANCA or the DCS; `dcs_keys` only names where a DCS page would hold the same hymn (for harvesting).
A slot the Rules have not yet given structured hymns for returns None (the service shows it as a gap).
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from functools import lru_cache

import yaml

from .calfacts import MAJOR_FIXED, MAJOR_MOVABLE
from .rules import DATA

MOVABLE_BASE = 71  # AGES Triodion/Pentecostarion day numbers: tr.d001 = Publican (-70), pe.d071 = Pascha (0)


@dataclass(frozen=True)
class Hymn:
    id: str
    label: str
    tone: int | None = None
    kind: str = ""  # apolytikion | kontakion | prokeimenon | alleluia | communion
    meta: dict = field(default_factory=dict, compare=False, hash=False)


@lru_cache(maxsize=1)
def table() -> dict:
    return yaml.safe_load(open(os.path.join(DATA, "hymns.yaml"), encoding="utf-8"))


# ------------------------------------------------------------------ calendar -> book locations
_FEAST_DATE = {v[0]: k for k, v in MAJOR_FIXED.items()}
_FEAST_P = {v[0]: k for k, v in MAJOR_MOVABLE.items()}


_PERIOD_DATE = {"entrance_theotokos": "11-21", "nativity_forerunner": "06-24", "peter_paul": "06-29", "beheading": "08-29",
                "procession_cross": "08-01", "conception": "12-09"}  # calfacts.FEAST_PERIODS keys that are not Major feast ids


def feast_base(name: str) -> str | None:
    """Major feast / feast-period id ('dormition', 'ascension', 'nativity_forerunner', ...) -> 'men/08-15' | 'mov/39'."""
    if name in _PERIOD_DATE:
        return f"men/{_PERIOD_DATE[name]}"
    if name in _FEAST_DATE:
        return f"men/{_FEAST_DATE[name]}"
    if name in _FEAST_P:
        return f"mov/{_FEAST_P[name]}"
    return None


FOREFEAST_DAY = {"nativity": "12-20", "theophany": "01-02", "presentation": "02-01", "annunciation": "03-24", "transfiguration": "08-05",
                 "dormition": "08-14", "nativity_theotokos": "09-07", "elevation": "09-13", "entrance_theotokos": "11-20"}


def forefeast_base(f: dict) -> str | None:
    """In a forefeast period: the Menaion day whose troparion/kontakion is the forefeast's (first day of the forefeast)."""
    fp = (f.get("feast_period") or "").split(":")
    return f"men/{FOREFEAST_DAY[fp[1]]}" if len(fp) == 2 and fp[0] == "forefeast" and fp[1] in FOREFEAST_DAY else None


def day_feast(f: dict) -> str | None:
    """The feast whose hymns the day takes: the Major feast itself, else the feast of a fore/after-feast period."""
    if f.get("major_feast"):
        return feast_base(f["major_feast"])
    fp = (f.get("feast_period") or "").split(":")
    return feast_base(fp[1]) if len(fp) == 2 else None


def saint_base(f: dict) -> str:
    return f"men/{f.get('menaion_key') or f['mmdd']}"


NAMED = [("Forefathers", "forefathers"), ("before the Nativity", "before_nativity"), ("fter the Nativity", "after_nativity"),
         ("before the Theophany", "before_theophany"), ("fter the Theophany", "after_theophany"), ("before the Elevation", "before_elevation"),
         ("fter the Elevation", "after_elevation"), ("Sunday of All Saints", "all_saints"), ("Fathers of the", "fathers")]


def named(f: dict) -> str | None:
    """Stable slug of a named Sunday (its own hymns), from the calendar designation; Sundays of the Fathers by council."""
    desig = f"{f.get('desig') or ''} {f.get('desig_g') or ''}"
    slug = next((s for sub, s in NAMED if sub in desig), None)
    if slug == "all_saints" and re.search(r"All Saints of \w", desig):
        return None  # regional All Saints Sundays take the tone's
    return (f.get("named_sunday") or slug) if slug == "fathers" else slug


def _name(f: dict) -> str:
    return f.get("principal_name") or "the saint of the day"


_BOOK = {"oct": "Octoechos", "men": "Menaion", "mov": "Triodion/Pentecostarion", "lit": "Liturgy", "hor": "Horologion", "named": "Sunday"}


def label(hid: str, f: dict) -> str:
    """Readable default label for a hymn id ('men/05-21/apolytikion' -> 'Apolytikion — Menaion 05-21')."""
    parts = hid.split("/")
    kind = re.sub(r"(\d+)$", r" \1", parts[-1]).title()
    if parts[0] == "oct":
        return f"Resurrectional {kind} (Tone {parts[1][1:]})"
    where = parts[1]
    if parts[0] == "mov":
        p = int(where)
        where = "Pascha" if p == 0 else f"Pascha {p:+d} days"
    return f"{kind} — {_BOOK.get(parts[0], parts[0])} {where}"


# ------------------------------------------------------------------ slot -> hymns
def _explicit(fill: dict, f: dict) -> list | None:
    """A Rule may list its hymns: `hymns: [{id: 'men/{mmdd}/apolytikion', label: '...', tone: 4}]` ({fact} placeholders)."""
    if "hymns" not in fill:
        return None
    fx = {**f, "named": named(f) or f.get("named_sunday")}  # {named}: the named Sunday's slug (its own hymns)
    sub = lambda s: re.sub(r"{(\w+)}", lambda m: str(fx.get(m.group(1), m.group(0))), s) if isinstance(s, str) else s
    out = []
    for h in fill["hymns"]:
        h = h if isinstance(h, dict) else {"id": h}
        hid = sub(h["id"])
        kind = h.get("kind") or re.sub(r"\d+$", "", hid.rsplit("/", 1)[-1])
        out.append(Hymn(hid, sub(h.get("label") or label(hid, f)), h.get("tone"), kind))
    return out


def apolytikia(fill: dict, f: dict) -> list | None:
    if fill.get("parts"):
        return None  # free-text parts (proper days): the Rule needs `hymns:`
    out = []
    if fill.get("res_tone"):
        t = int(fill["res_tone"])
        out.append(Hymn(f"oct/t{t}/sun/apolytikion", f"Resurrectional Apolytikion (Tone {t})", t, "apolytikion"))
    if fill.get("feast"):
        if f.get("feast_period_saint"):
            out.append(Hymn(f"{saint_base(f)}/apolytikion", f"Apolytikion of {_name(f)}", None, "apolytikion"))
        fb = forefeast_base(f) or day_feast(f)
        if not fb:
            return None
        what = "forefeast" if forefeast_base(f) else "feast"
        out.append(Hymn(f"{fb}/apolytikion", f"Apolytikion of the {what} ({f.get('fore_after') or f.get('major_feast')})", None, "apolytikion"))
    elif fill.get("saint"):
        out.append(Hymn(f"{saint_base(f)}/apolytikion", f"Apolytikion of {_name(f)}", None, "apolytikion"))
    return out


def kontakion(fill: dict, f: dict) -> list | None:
    kind = fill.get("kind")
    hid = table()["kontakion"].get(kind)
    if not hid and kind == f.get("major_feast"):
        fb = day_feast(f)
        hid = f"{fb}/kontakion" if fb else None
    if not hid:
        return None
    tone = fill.get("tone")
    label = "Kontakion of the Theotokos (“O Protection of Christians”)" if kind == "ordinary_theotokos" else f"Kontakion ({kind.replace('_', ' ')})"
    return [Hymn(hid, label + (f" (Tone {tone})" if tone else ""), tone, "kontakion")]


def prokeimenon(fill: dict, f: dict) -> list | None:
    owner = fill.get("owner")
    if owner == "saint":
        return [Hymn(f"{saint_base(f)}/prokeimenon", f"Prokeimenon of {_name(f)}", None, "prokeimenon")]
    if owner == "feast":
        fb = day_feast(f)
        return [Hymn(f"{fb}/prokeimenon", "Prokeimenon of the feast", None, "prokeimenon")] if fb else None
    if owner == "sunday" and fill.get("proper"):
        ns = named(f)
        if not ns:
            return None
        return [Hymn(f"named/{ns}/prokeimenon", f"Prokeimenon ({f.get('desig_g') or f.get('desig')})", None, "prokeimenon")]
    if owner == "sunday" and f.get("tone") and not fill.get("parts"):
        t = int(f["tone"])
        return [Hymn(f"lit/sun/t{t}/prokeimenon", f"Prokeimenon (Tone {t})", t, "prokeimenon")]
    return None


def alleluia(fill: dict, f: dict) -> list | None:
    t = fill.get("tone")
    return [Hymn(f"lit/sun/t{int(t)}/alleluia", f"The Alleluia (Tone {t})", int(t), "alleluia")] if t else None


def communion(fill: dict, f: dict) -> list | None:
    kind = fill.get("kind")
    hid = table()["communion"].get(kind)
    if kind == "feast":
        fb = day_feast(f)
        hid = f"{fb}/communion" if fb else None
    elif kind == "saint":
        hid = f"{saint_base(f)}/communion"
    if not hid:
        return None
    label = "Communion Hymn (Sunday)" if kind == "praise_the_lord" else f"Communion Hymn ({kind.replace('_', ' ')})"
    return [Hymn(hid, label, None, "communion")]


SLOTS = {"liturgy.apolytikia": apolytikia, "liturgy.kontakion": kontakion, "liturgy.prokeimenon": prokeimenon,
         "liturgy.alleluia": alleluia, "liturgy.communion": communion}


def for_slot(slot: str, res, f: dict) -> list | None:
    """Resolution of `slot` -> [Hymn] in order; None when the Rule gives no structured hymns (or the slot is missing)."""
    if res is None or res.status == "missing":
        return None
    ex = _explicit(res.fill, f)
    if ex is not None:
        return ex
    fn = SLOTS.get(slot)
    return fn(res.fill, f) if fn else None


# ------------------------------------------------------------------ dismissal (rules + calendar, no hymn text)
PHRASES = {"resurrection": "he who rose from the dead"}  # Typikon Ch I s4 p.17-18; other characteristic phrases: to be entered


def dismissal(dis, phrase, f: dict) -> dict:
    """liturgy.dismissal + liturgy.dismissal_phrase resolutions -> {phrase, phrase_known, author, saints}."""
    pf = (phrase.fill if phrase and phrase.status != "missing" else {}) or {}
    df = (dis.fill if dis and dis.status != "missing" else {}) or {}
    p = pf.get("phrase") or ("resurrection" if f.get("weekday") == "Sunday" else None)
    saints = None
    if df.get("saint_named"):
        na = df.get("named_as", "")
        saints = (f.get("desig_g") or f.get("desig")) if na.startswith("the Sunday") else (f.get("dismissal_saint") or f.get("principal_name"))
    return {"phrase_kind": p, "phrase": PHRASES.get(p), "clause": pf.get("clause"),
            "author": df.get("author") or f.get("liturgy_author"), "saints": saints or None}


# ------------------------------------------------------------------ id -> DCS keys (harvest/lookup only)
def dcs_keys(hid: str) -> list:
    """Hymn id -> candidate DCS key lists: [[part, ...], ...] (alternatives, each the hymn's parts in order; a part may be a list to join)."""
    alts = []
    over = table().get("dcs", {}).get(hid)
    if over:
        alts.append(over)
    m = re.fullmatch(r"oct/t(\d)/sun/(apolytikion|kontakion)", hid)
    if m:
        alts.append([f"oc.m{m.group(1)}.d1|oc{'VE' if m.group(2) == 'apolytikion' else 'MA'}.{m.group(2).title()}.text"])
    m = re.fullmatch(r"men/(\d\d)-(\d\d)/([a-z]+)(\d*)", hid)
    if m:
        mm, dd, k, n = m.groups()
        if k in ("apolytikion", "kontakion"):
            alts.append([f"me.m{mm}.d{dd}|me*.{k.title()}{n or 1}.text"])
        elif k in ("prokeimenon", "alleluia"):
            alts.append([f"menaion.verses|psLI.m{mm}.d{dd}.{k}.v{i}.text" for i in (1, 2, 3)])
        elif k == "communion":
            alts.append([f"menaion.verses|psLI.m{mm}.d{dd}.communion.v1.text"])
    m = re.fullmatch(r"mov/(-?\d+)/([a-z]+)(\d*)", hid)
    if m:
        p, k, num = int(m.group(1)), m.group(2), m.group(3)
        b, n = ("tr" if p < 0 else "pe"), p + MOVABLE_BASE
        if k in ("apolytikion", "kontakion", "troparion", "hypakoe"):
            alts.append([f"{b}.d{n:03d}|{b}*.{k.title()}{num or 1}.text"])
            if not num:
                alts.append([f"{b}.d{n:03d}|{b}*.{k.title()}.text"])
        elif k == "communion":
            alts += [[f"movable.verses|psLI.{b}.d{n:03d}.communion.v1.text"], [f"{b}.d{n:03d}|{b}LI.CommunionHymn.text"]]
        elif k in ("prokeimenon", "alleluia"):
            alts.append([f"movable.verses|psLI.{b}.d{n:03d}.{k}.v{i}.text" for i in (1, 2, 3)])
    m = re.fullmatch(r"lit/sun/t(\d)/(prokeimenon|alleluia)", hid)
    if m:
        alts.append([f"liturgical.verses|psLI.sunday.m{m.group(1)}.{m.group(2)}.v{i}.text" for i in (1, 2, 3)])
    return alts


# ------------------------------------------------------------------ DCS key -> hymn id (answer key: which hymns a DCS page prints)
def _overrides() -> dict:
    """Override keys -> id (first key of a multi-key part names the hymn; its other keys -> '' = skip)."""
    out = {}
    for hid, parts in (table().get("dcs") or {}).items():
        keys = [k for p in parts for k in (p if isinstance(p, list) else [p])]
        out[keys[0]] = hid
        for k in keys[1:]:
            out.setdefault(k, "")
    return out


def id_from_dcs(topic: str, field_: str) -> str | None:
    """AGES/DCS key -> our hymn id, or None for keys that are not a variable hymn ('' = part of a hymn already named)."""
    key = f"{topic}|{field_}"
    if key in (table().get("dcs_ignore") or []):
        return None
    for k, hid in _overrides().items():
        if re.fullmatch(re.escape(k).replace(r"\*", ".*"), key):
            return hid
    num = lambda n: "" if n in ("", "1") else n
    m = re.fullmatch(r"oc\.m(\d)\.d1\|oc\w+\.(Apolytikion|Kontakion)\.text", key)
    if m:
        return f"oct/t{m.group(1)}/sun/{m.group(2).lower()}"
    m = re.fullmatch(r"me\.m(\d\d)\.d(\d\d)\|me\w+\.(Apolytikion|Kontakion)(\d+)\.text", key)
    if m:
        return f"men/{m.group(1)}-{m.group(2)}/{m.group(3).lower()}{num(m.group(4))}"
    m = re.fullmatch(r"(tr|pe)\.d(\d{3})\|\w+\.(Apolytikion|Kontakion|Troparion|Hypakoe)(\d*)\.text", key)
    if m:
        return f"mov/{int(m.group(2)) - MOVABLE_BASE}/{m.group(3).lower()}{num(m.group(4))}"
    m = re.fullmatch(r"(tr|pe)\.d(\d{3})\|\w+LI\.CommunionHymn\.text", key)
    if m:
        return f"mov/{int(m.group(2)) - MOVABLE_BASE}/communion"
    m = re.fullmatch(r"liturgical\.verses\|psLI\.sunday\.m(\d)\.(prokeimenon|alleluia)\.v1\.text", key)
    if m:
        return f"lit/sun/t{m.group(1)}/{m.group(2)}"
    m = re.fullmatch(r"menaion\.verses\|psLI\.m(\d\d)\.d(\d\d)\.(prokeimenon|alleluia|communion)\.v1\.text", key)
    if m:
        return f"men/{m.group(1)}-{m.group(2)}/{m.group(3)}"
    m = re.fullmatch(r"movable\.verses\|psLI\.(tr|pe)\.d(\d{3})\.(prokeimenon|alleluia|communion)\.v1\.text", key)
    if m:
        return f"mov/{int(m.group(2)) - MOVABLE_BASE}/{m.group(3)}"
    return None
