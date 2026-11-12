"""ANCA 'Liturgy Variables' (READ) texts -> hymn ids, from each block's own heading (never from our Rules).

The heading names the hymn ("KONTAKION OF ENTRANCE OF THE THEOTOKOS IN TONE FOUR"); the calendar DB is used only to find the
Menaion date of a saint the heading names (the file date's principal commemoration). Anything the heading does not name
unambiguously is skipped and counted, never guessed.
"""
from __future__ import annotations

import datetime as dt
import glob
import os
import re
import unicodedata
from collections import Counter

from . import anca_read

KIND = {"APOLYTIKION": "apolytikion", "KONTAKION": "kontakion", "KOINONIKON": "communion", "MEGALYNARION": "megalynarion",
        "EISODIKON": "eisodikon", "HYPAKOE": "hypakoe"}
TONES = {w: i for i, w in enumerate("ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT".split())}

# owner phrase (substring of the heading's "OF/FOR ..." part, normalised) -> id base. First match wins: specific before general.
MOVABLE = [("GREGORY PALAMAS", -35), ("JOHN CLIMACUS", -21), ("JOHN OF THE LADDER", -21), ("MARY OF EGYPT", -14), ("MID-PENTECOST", 24), ("THOMAS SUNDAY", 7), ("JOSEPH OF ARIMATH", 14), ("MYRRH", 14), ("PARALYTIC", 21), ("SAMARITAN", 28),
           ("BLIND", 35), ("ASCENSION", 39), ("FATHERS OF THE FIRST", 42), ("PENTECOST", 49), ("PASCHA", 0), ("PALM SUNDAY", -7),
           ("LAZARUS", -8), ("FORGIVENESS", -49), ("LAST JUDGMENT", -56), ("PRODIGAL", -63), ("PUBLICAN", -70),
           ("FIRST SUNDAY OF GREAT LENT", -42), ("SECOND SUNDAY OF GREAT LENT", -35), ("THIRD SUNDAY OF GREAT LENT", -28),
           ("FOURTH SUNDAY OF GREAT LENT", -21), ("FIFTH SUNDAY OF GREAT LENT", -14)]
NAMED = [(r"ALL SAINTS OF ANTIOCH", "all_saints_antioch"), (r"ALL SAINTS OF NORTH AMERICA", "all_saints_north_america"),
         (r"SUNDAY BEFORE (THE )?NATIVITY", "before_nativity"), (r"SUNDAY AFTER (THE )?NATIVITY", "after_nativity"), (r"FOREFATHERS", "forefathers"),
         (r"SUNDAY BEFORE (THE )?(THEOPHANY|EPIPHANY)", "before_theophany"), (r"SUNDAY AFTER (THE )?(THEOPHANY|EPIPHANY)", "after_theophany"),
         (r"SUNDAY BEFORE (THE )?(ELEVATION|EXALTATION)", "before_elevation"), (r"SUNDAY AFTER (THE )?(ELEVATION|EXALTATION)", "after_elevation")]
FIXED = [("PREPARATION OF CHRIST", "12-20"), ("THEOTOKOS' NATIVITY", "09-07"), ("FOREFEAST OF THE NATIVITY OF THE THEOTOKOS", "09-07"),
         ("FOREFEAST OF THE NATIVITY", "12-20"), ("FOREFEAST OF THE NATIVITY OF CHRIST", "12-20"), ("FOREFEAST OF CHRIST", "12-20"),
         ("FOREFEAST OF THEOPHANY", "01-02"), ("FOREFEAST OF THE THEOPHANY", "01-02"), ("FOREFEAST OF THE ENTRANCE", "11-20"),
         ("FOREFEAST OF THE NATIVITY OF THE THEOTOKOS", "09-07"), ("FOREFEAST OF THE DORMITION", "08-14"),
         ("FOREFEAST OF THE TRANSFIGURATION", "08-05"), ("FOREFEAST OF THE ELEVATION", "09-13"), ("FOREFEAST OF THE MEETING", "02-01"),
         ("FOREFEAST OF THE PRESENTATION", "02-01"), ("FOREFEAST OF THE ANNUNCIATION", "03-24"),
         ("NATIVITY OF THE THEOTOKOS", "09-08"), ("NATIVITY OF JOHN", "06-24"), ("NATIVITY OF THE FORERUNNER", "06-24"),
         ("NATIVITY OF CHRIST", "12-25"), ("ENTRANCE OF THE THEOTOKOS", "11-21"), ("ENTRANCE OF THE MOST HOLY THEOTOKOS", "11-21"),
         ("CIRCUMCISION", "01-01"), ("THEOPHANY", "01-06"), ("MEETING OF", "02-02"), ("PRESENTATION OF CHRIST", "02-02"),
         ("PRESENTATION OF OUR LORD", "02-02"), ("ANNUNCIATION", "03-25"), ("TRANSFIGURATION", "08-06"), ("DORMITION", "08-15"),
         ("ELEVATION", "09-14"), ("EXALTATION", "09-14"), ("PLACING OF THE ROBE", "07-02"), ("PLACING OF THE SASH", "08-31"),
         ("PLACING OF THE BELT", "08-31"), ("PROPHET ELIAS", "07-20"), ("PROPHET ELIJAH", "07-20"), ("ARCHANGEL", "11-08"),
         ("THREE HIERARCHS", "01-30"), ("SYNAXIS OF JOHN THE BAPTIST", "01-07"), ("SYNAXIS OF THE FORERUNNER", "01-07"),
         ("BEHEADING", "08-29"), ("PETER AND PAUL", "06-29"), ("CONSTANTINE AND HELEN", "05-21"), ("HOLY CROSS", "09-14"),
         ("PRESENTATION", "02-02")]
COMMON = {"APOSTLE": "apostle", "APOSTLES": "apostle", "HIERARCH": "hierarch", "HIERARCHS": "hierarch", "MARTYR": "martyr",
          "MARTYRS": "martyr", "THEOTOKOS": "theotokos", "RIGHTEOUS": "righteous"}  # koinonikon "FOR THE APOSTLE": a common hymn
STOP = set(("SAINT ST ST. SS SS. STS HOLY GREAT GREATMARTYR GREAT-MARTYR MARTYR MARTYRS APOSTLE APOSTLES EVANGELIST FATHER FATHERS AMONG "
            "SAINTS BISHOP ARCHBISHOP WONDERWORKER VENERABLE RIGHTEOUS GLORIOUS PROPHET CONFESSOR MOTHER HIEROMARTYR OUR THE AND OF "
            "FOR WITH ALL HIS HER THEIR EQUAL-TO-THE-APOSTLES PATRIARCH NEW").split())
SUNDAY_PLAIN = re.compile(r"SUNDAY (AFTER PENTECOST|OF (LUKE|MATTHEW))")  # the tone's prokeimenon


def _norm(s: str) -> str:
    s = re.sub(r"\([^)]*\)", " ", s.upper()).replace("’", "'").replace("ST.", "ST ")
    return re.sub(r"\s+", " ", s).strip(" .")


def _tone(h: str):
    m = re.search(r"IN TONE (\w+)", h)
    return TONES.get(m.group(1)) if m else None


def saint_date(owner: str, facts: dict) -> tuple:
    """Owner phrase naming a saint -> (menaion date, None) when it names the file date's principal commemoration; else (None, reason)."""
    toks = {t for t in re.findall(r"[A-Z][A-Z'\-]{3,}", owner) if t not in STOP}
    if not toks:
        return None, "saint: no distinctive name"
    words = lambda s: set(re.findall(r"[A-Z][A-Z'\-]{3,}", _norm(unicodedata.normalize("NFKD", s or "").replace("Œ", "OE").replace("œ", "oe"))))
    same = lambda a, b: any(x[:5] == y[:5] for x in a for y in b)  # spelling variants: Theodosios/Theodosius, Paraskeva/Parasceva
    if same(toks, words(facts.get("principal_name"))):
        return facts.get("menaion_key") or facts["mmdd"], None
    if same(toks, words(facts.get("other_commem"))):
        return None, "saint: not the principal commemoration (numbering unknown)"
    return None, "saint: not in the calendar for the date"


def owner_base(owner: str, facts_fn) -> tuple:
    """Owner phrase -> (id base like 'men/11-21' | 'mov/7' | 'named/forefathers', None) or (None, reason)."""
    if re.search(r"\b(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|DAY BEFORE|DAY AFTER)\b", owner) and "LAZARUS" not in owner:
        return None, "weekday proper (not a Sunday/feast hymn id)"
    for sub, p in MOVABLE:
        if sub in owner and not (sub == "PENTECOST" and "SUNDAY AFTER" in owner):
            return f"mov/{p}", None
    if owner.strip() == "ALL SAINTS":
        return "mov/56", None
    for rx, slug in NAMED:
        if re.search(rx, owner):
            return f"named/{slug}", None
    for sub, mmdd in FIXED:
        if sub in owner:
            return f"men/{mmdd}", None
    facts = facts_fn()
    if facts is None:
        return None, "saint: date not in the calendar DB"
    if "FATHERS" in owner:  # which Sunday of the Fathers: by the file's own date (season/month), not by our Rules
        if 0 < facts["pascha_days"] < 50:
            return "mov/42", None
        fc = {"07": "fathers_4th_council", "10": "fathers_7th_council"}.get(facts["mmdd"][:2])
        return (f"named/{fc}", None) if fc else (None, "fathers: which council not named")
    if re.fullmatch(r"(THE )?(FEAST|LEAVE-TAKING( OF THE FEAST)?)", owner):  # "of the feast": the feast the calendar has on that date
        from yocal_rules.hymns import day_feast
        fb = day_feast(facts)
        return (fb, None) if fb else (None, "feast: no feast in the calendar for the date")
    d, why = saint_date(owner, facts)
    return (f"men/{d}", None) if d else (None, why)


_HEAD = re.compile(r"^(?:THE )?(?:(PASCHAL|RESURRECTIONAL|ORDINARY) )?(APOLYTIKION|KONTAKION|KOINONIKON|MEGALYNARION|EISODIKON|HYPAKOE)"
                   r"(?: \(COMMUNION HYMN\))?(?: (?:OF|FOR) (.*?))?(?: IN TONE \w+)?$")


def heading_id(heading: str, sub: list, facts_fn, file_tone=None) -> tuple:
    """One READ block -> (hymn id, None) or (None, reason it is skipped)."""
    raw = heading.upper()
    h = _norm(re.sub(r"\(COMMUNION HYMN\)", "", raw))
    h = re.sub(r"\b(CHANT|CHORAL)\b", "", h).strip()
    if h.startswith(("ST BASIL LITURGY MEGALYNARION",)):
        return "lit/basil/megalynarion", None
    if h == "THE EPISTLE" or h.startswith("THE EPISTLE"):
        return _prokeimenon(sub, facts_fn, file_tone)
    m = _HEAD.match(h)
    if not m:
        return None, "not a hymn heading"
    adj, kind_w, owner = m.group(1), m.group(2), (m.group(3) or "").strip()
    kind, tone = KIND[kind_w], _tone(h)
    if adj == "RESURRECTIONAL" and kind == "apolytikion" and tone:
        return f"oct/t{tone}/sun/apolytikion", None
    if adj == "ORDINARY" and kind == "kontakion":
        return ("hor/kontakion/protection", None) if tone == 2 else (None, "ordinary kontakion not in tone 2")
    if adj == "PASCHAL" and kind == "apolytikion":
        return "mov/0/troparion", None
    if kind == "kontakion" and "SUNDAYS IN GREAT LENT" in owner:
        return "men/03-25/kontakion", None  # the Lenten Sunday kontakion: "To thee, the Champion Leader"
    if not owner:
        return None, f"{kind}: no owner named"
    if kind == "communion" and owner.replace("THE ", "") in COMMON:
        return f"lit/communion/common/{COMMON[owner.replace('THE ', '')]}", None
    if "ORDINARY SUNDAYS" in owner or "ORDINARY WEEKDAYS" in owner:
        return None, f"{kind}: ordinary (fixed text)"
    base, why = owner_base(owner, facts_fn)
    if not base:
        return None, f"{kind}: {why}"
    if base == "mov/0" and kind == "apolytikion":
        kind = "troparion"
    return f"{base}/{kind}", None


def _prokeimenon(sub: list, facts_fn, file_tone) -> tuple:
    """The Epistle block's subtitle names whose prokeimenon it prints: '(For the 24th Sunday after Pentecost)', '(For St. X)'."""
    owner = _norm(" ".join(sub).replace("(", " ").replace(")", " ").replace("*", " ")).removeprefix("FOR ").removeprefix("THE ").strip()
    if not owner:
        return None, "prokeimenon: owner not printed"
    if SUNDAY_PLAIN.search(owner) and "GREAT LENT" not in owner:
        return (f"lit/sun/t{file_tone}/prokeimenon", None) if file_tone else (None, "prokeimenon: tone unknown")
    base, why = owner_base(owner, facts_fn)
    return (f"{base}/prokeimenon", None) if base else (None, f"prokeimenon: {why}")


def prokeimenon_parts(body: list) -> list:
    """Epistle block text before 'The Reading ...' -> [refrain, verse]."""
    pre = re.split(r"\bThe Reading\b", " ".join(body), maxsplit=1, flags=re.I)[0].strip()
    parts = re.split(r"(?<=[.!?])\s+", pre, maxsplit=1)
    return [p.strip() for p in parts if p.strip()]


def hymn_text(hid: str, body: list) -> str:
    keep = [p for p in body if not p.startswith(("**", "Priest:", "Deacon:")) and "Copyright" not in p]
    if hid.endswith("/communion"):  # the Alleluia is added when shown
        keep = [re.sub(r"(\s*Alleluia[.!,]?)+\s*$", "", p, flags=re.I).strip() for p in keep]
    return "\n\n".join(p for p in keep if p)


def ingest(tx, put, cache: str, facts_for) -> Counter:
    """Every cached READ file -> tx (source 'anca', key = hymn id). facts_for(date) -> calendar facts or None."""
    st = Counter()
    for fn in sorted(glob.glob(os.path.join(cache, "anca-*-READ.txt"))):
        txt = open(fn, encoding="utf-8").read()
        m = re.search(r"anca-(\d{4}-\d\d-\d\d)-READ", fn)
        if not txt or not m:
            continue
        day = m.group(1)
        st["files"] += 1
        blocks = anca_read.parse(txt)
        cache_f = {}
        facts_fn = lambda: cache_f.setdefault("f", facts_for(dt.date.fromisoformat(day)))
        res = [b for b in blocks if re.match(r"RESURRECTIONAL APOLYTIKION", b["heading"].upper())]
        file_tone = _tone(_norm(res[0]["heading"])) if res else None
        for b in blocks:
            hid, why = heading_id(b["heading"], b["sub"], facts_fn, file_tone)
            if not hid:
                if why != "not a hymn heading":
                    st[f"skip: {why}"] += 1
                continue
            text = "\n\n".join(prokeimenon_parts(b["body"])) if hid.endswith("/prokeimenon") else hymn_text(hid, b["body"])
            if not text:
                st["skip: empty body"] += 1
                continue
            put(tx, "anca", hid, text, f"ANCA Liturgy Variables {day}", day, label=re.sub(r"\s+", " ", b["heading"]).strip(),
                tone=_tone(_norm(b["heading"])))
            st["stored"] += 1
    return st
