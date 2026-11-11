"""ANCA service-text answer key: locate (committed filename index), fetch (cached), parse to slot attributes.

Downloaded PDFs/text stay in the cache directory and are never committed.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request

from .rules import DATA

BASE = "https://www.antiochian.org"
WORDS = {w: i for i, w in enumerate("ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE TEN ELEVEN".split())}
UA = {"User-Agent": "yocal-rules/0.1"}
_INDEX = None


def _index():
    global _INDEX
    if _INDEX is None:
        _INDEX = json.load(open(os.path.join(DATA, "anca_pages.json"), encoding="utf-8"))
    return _INDEX


_FEAST_INDEX = None


def _feast_index():
    """data/anca_feast_files.json: weekday Major-feast texts with undated filenames (work package I)."""
    global _FEAST_INDEX
    if _FEAST_INDEX is None:
        p = os.path.join(DATA, "anca_feast_files.json")
        _FEAST_INDEX = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
    return _FEAST_INDEX


def candidate_urls(date: dt.date, kind: str):
    """kind: VESP | Abbr | ORTHROS | READ. Index first (covers non-date filenames), then constructed names."""
    ent = _index().get(date.isoformat())
    urls = []
    named = _feast_index().get(date.isoformat(), {}).get("named", {}).get(kind)  # undated/odd names mapped to a pseudo-kind (VIGIL, VDL)
    if named:
        return [BASE + named]
    for link in (ent or {}).get("links", []) + _feast_index().get(date.isoformat(), {}).get("links", []):
        name = urllib.parse.unquote(link)
        if name.endswith((f" {kind}.pdf", f"-{kind}.pdf")) and "Bilingual" not in name:  # '-': e.g. '7-Palm-Sunday-READ.pdf'
            urls.append(BASE + link)
    if not urls:
        months = [date.strftime("%b")] + (["Sept"] if date.month == 9 else []) + ([date.strftime("%B")] if date.month in (3, 4, 6, 7) else [])
        urls = [f"{BASE}/servicetexts/{urllib.parse.quote(f'{m} {date.day:02d} {date.year} {kind}.pdf')}" for m in months]
    return urls


def fetch(date: dt.date, kind: str, cache: str, offline: bool = False) -> str | None:
    """-> extracted text, or None if no such file (a `no key`, non-blocking)."""
    os.makedirs(cache, exist_ok=True)
    fn = os.path.join(cache, f"anca-{date.isoformat()}-{kind}.txt")
    if os.path.exists(fn):
        return open(fn, encoding="utf-8").read() or None
    if offline:
        return None
    txt = None
    for url in candidate_urls(date, kind):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
        except urllib.error.HTTPError:
            continue
        if not data.startswith(b"%PDF"):
            continue
        pdf = fn + ".pdf"
        open(pdf, "wb").write(data)
        txt = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
        os.remove(pdf)
        break
    open(fn, "w", encoding="utf-8").write(txt or "")
    return txt


# ------------------------------------------------------------------ parsing
ORD = {w: i for i, w in enumerate("ZEROTH FIRST SECOND THIRD FOURTH FIFTH SIXTH SEVENTH EIGHTH NINTH TENTH ELEVENTH".split())}


def _word(w):
    w = w.upper()
    if w in WORDS:
        return WORDS[w]
    return ORD[w] if w in ORD else (int(w) if w.isdigit() else None)


def _span(txt, start_re, end_re):
    m = re.search(start_re, txt)
    if not m:
        return ""
    rest = txt[m.start():]
    e = re.search(end_re, rest[10:])
    return rest[: e.start() + 10] if e else rest


def _blocks(span):
    out, cur = [], None
    for ln in span.splitlines():
        s = ln.strip()
        if re.match(r"^For .*(Tone|tone)", s):
            cur = [s, 0]
            out.append(cur)
        elif re.match(r"^Verse \d+\.", s) and cur is not None:
            cur[1] += 1
    return out


def _flat(s):
    return re.sub(r"\s+", " ", s)


def parse_apolytikia(span: str):
    f = _flat(span)
    res = re.search(r"RESURRECTIONAL APOLYTIKION IN TONE (\w+)", f)
    saints = [(re.sub(r"\s+", " ", n).strip(), _word(t))
              for n, t in re.findall(r"(?<![A-Z])APOLYTIKION (?:OF|FOR) ([A-Z][A-Z0-9 .,’'“”‘’&()-]*?) IN TONE (\w+)", f)
              if not n.startswith("THE RESURRECTION")]
    if not res and not saints:
        return None
    return dict(res_tone=_word(res.group(1)) if res else None, saint=bool(saints),
                saint_labels=[f"{n} (tone {t})" for n, t in saints])


def split_abbr(txt):
    ves, _, mat = txt.partition("Orthros on Sunday")
    if not mat:  # 'Festal Orthros on Palm Sunday Morning' (Palm Sunday Abbr 2026)
        ves, _, mat = txt.partition("Orthros on Palm Sunday")
    return (ves, mat) if mat else (txt, "")


def parse_vespers(txt):
    k = {}
    sp = _span(txt, r"3\.\)\s+We chant .O Lord, I Have Cried", r"\n\s*4\.\)")
    n = re.search(r"with (\w+) (?:stichera|troparia)", sp)
    if n:
        bl = _blocks(sp)
        res = sum(c for h, c in bl if "Resurrection" in h)
        oth = [c for h, c in bl if "Resurrection" not in h and c]
        total = _word(n.group(1))
        if res == 0 and total and sum(oth) < total:  # Resurrection block printed without a 'For ...' header
            head = sp.split("Verse ", 1)[0]  # unheaded first block cited only from the Pentecostarion (Thomas Sunday): proper, not Resurrection
            if "Pentecostarion" in head and not re.search(r"Vesp\.|Octoechos", head):
                oth = [total - sum(oth)] + oth
            else:
                res = total - sum(oth)
        k["vespers.lihc.stichera"] = dict(res=res, other=oth, total=total)
    pk = re.search(r"[Pp]rokeimenon\s+[“\"]([^”\"]+)[”\"]\s+in Tone (\d)", txt)
    if pk:
        k["vespers.prokeimenon"] = dict(kind="lord_is_king" if "Lord is King" in pk.group(1) else pk.group(1)[:30], tone=int(pk.group(2)))
    elif re.search(r"SATURDAY PROKEIMENON IN TONE (\w+)", txt):
        k["vespers.prokeimenon"] = dict(kind="lord_is_king", tone=_word(re.search(r"SATURDAY PROKEIMENON IN TONE (\w+)", txt).group(1)))
    elif re.search(r"GREAT PROKEIMENON IN TONE (\w+)", txt):  # Saturday that is Nativity / Theophany (Typikon p.12-13)
        k["vespers.prokeimenon"] = dict(kind="great", tone=_word(re.search(r"GREAT PROKEIMENON IN TONE (\w+)", txt).group(1)))
    ap =parse_apolytikia(_span(txt, r"7\.\)\s+We then say the Prayer of St\. Simeon", r"\n\s*8\.\)") or "")
    if ap:
        k["vespers.apolytikia"] = ap
    return k


def parse_matins(mat):
    k = {}
    m = re.search(r"(?:[Kk]athismata hymns|Poetic Kathismata) are from the Octoechos for Tone (\d)", mat)
    if m:
        k["matins.kathismata"] = dict(tone=int(m.group(1)))
    m = re.search(r"\n\s*([A-Z ,.’'()-]*PROKEIMENON[A-Z ]*IN TONE \w+)", mat)
    if m:
        h = m.group(1)
        t = re.search(r"TONE (\w+)", h)
        k["matins.prokeimenon"] = dict(kind="resurrectional" if ("RESURRECTION" in h) else "other", tone=_word(t.group(1)) if t else None)
    m = re.search(r"The (\w+) Eothinon Gospel", mat, re.I)
    if m and _word(m.group(1)) is not None:
        k["matins.eothinon_gospel"] = dict(number=_word(m.group(1)))
    ap = parse_apolytikia(_span(mat, r"\n\s*5\.\)\s+After the Great Litany", r"\n\s*6\.\)") or "")
    if ap:
        k["matins.apolytikia"] = ap
    sp = _span(mat, r"We chant .The Praises", r"\n\s*22\.\)")
    n = re.search(r"with (\w+) (?:stichera|troparia)", sp)
    if n:
        k["matins.praises"] = dict(total=_word(n.group(1)), **parse_praises(sp))
    kk = parse_matins_kontakion(mat)
    if kk:
        k["matins.kontakion"] = kk
    return k


def parse_praises(sp: str):
    """Printed Praises structure: res = stichera under 'For the Resurrection...' headings, other = counts of the other
    headed blocks in print order (feast/saint/Triodion/Paschal; each 'Verse N.' line carries one sticheron), glory =
    'eothinon' | 'other' (heading above the 'Glory' line). Empty dict if the text prints no verses."""
    res, other, cur, head = 0, [], None, None
    glory = None
    for ln in sp.split("\n"):
        s = re.sub(r"^\(Tone \w+\)\s+(?=Verse \d)", "", ln.strip())  # '(Tone Two) Verse 6.' (Prodigal Son praises)
        if not s or s.startswith("(") or re.match(r"\w+ \d\d, 20\d\d\b", s) or "Rubrics" in s[:60]:
            continue
        if re.match(r"Verse \d", s):
            if cur == "res":
                res += 1
            elif cur == "other":
                other[-1] += 1
        elif re.match(r"Glory to the Father", s):
            glory = "eothinon" if head and "EOTHINON" in head.upper() else "other"
            cur = None
        elif ln.startswith("  ") and not s.startswith("Choir") and len(s) < 120 and (
                s.upper().startswith(("FOR ", "THE ")) or re.match(r"(For|The) ", s)):
            head = s
            if re.match(r"(?i)for the resurrection|resurrection", s) and "DOXASTICON" not in s.upper():
                cur = "res"
            elif "DOXASTICON" in s.upper() or "THEOTOKION" in s.upper():
                cur = None
            else:
                cur = "other"
                other.append(0)
    if not res and not other:
        return {}
    d = dict(res=res, other=other)
    if glory:
        d["glory"] = glory
    return d


def parse_matins_kontakion(mat):
    """Kontakion headings printed in the Matins text: resurrectional only -> kind=resurrectional; any other only
    -> kind=feast (resurrectional displaced/not printed); both (ANCA 2026 pairs) -> kind=both. `labels` is informational."""
    f = _flat(mat)
    res = re.search(r"(\w+) TONE RESURRECTIONAL KONTAKION AND OIKOS|RESURRECTIONAL KONTAKION[A-Z ]* IN TONE (\w+)", f)
    other = [(m.group(1) or m.group(2)).strip() for m in re.finditer(
        r"(?<![A-Z])KONTAKION (?:AND|&) OIKOS FOR ([A-Z][A-Z .,&’'-]*?) \(Plain Reading\)|(?<![A-Z])KONTAKION (?:FOR|OF) ([A-Z][A-Z .,&’'-]*?) \(Plain Reading\)", f)]
    if not res and not other:
        return None
    kind = "both" if res and other else "resurrectional" if res else "feast"
    d = dict(kind=kind, labels=other)
    if res and not other:
        d["tone"] = _word(next(g for g in res.groups() if g))
    return d


def _dismissal_names_saint(f: str) -> bool:
    """True if the dismissal names a commemoration after Joachim and Anna ('; of X' or '; and of X', then 'whose memory').
    The generic 'all the saints of all ages' wording is not a named saint, unless it adds 'especially ...'
    (the Sunday of All Saints of Antioch names its own feast)."""
    m = re.search(r"Joachim and Anna;(?: and)?(?: of)? (.{3,300}?) whose memory", f)
    if not m:
        return False
    g = m.group(1).lower()
    if g.startswith("all the saints") and "all ages" not in g:  # '; and of all the saints:' (no named saint)
        return False
    return not (g.startswith("all the saints of all ages") and "especially" not in g)


_LIT_KONTAKION_KINDS = [  # heading keyword -> kind label (as used by the data/rules/kontakion.yaml fills); order matters
    ("ORDINARY", "ordinary_theotokos"), ("RESURRECTIONAL", "resurrectional"), ("SUNDAYS IN GREAT LENT", "lent_sunday"),
    ("FOREFEAST OF THEOPHANY", "forefeast_theophany"), ("FOREFEAST OF THE PRESENTATION", "forefeast_presentation"),
    ("FOREFEAST OF THEOTOKOS", "forefeast_nativity_theotokos"), ("FOREFEAST OF THE DORMITION", "forefeast_dormition"),
    ("FOREFEAST OF ENTRANCE", "forefeast_entrance"), ("FOREFEAST OF THE ANNUNCIATION", "forefeast_annunciation"), ("PASCHA", "pascha"), ("ASCENSION", "ascension"), ("ALL SAINTS", "all_saints"),
    ("PENTECOST", "pentecost"), ("PRESENTATION", "presentation"), ("TRANSFIGURATION", "transfiguration"), ("ENTRANCE", "entrance"),
    ("PREPARATION OF CHRIST", "nativity_preparation"), ("NATIVITY OF THE THEOTOKOS", "nativity_theotokos"),
    ("NATIVITY OF CHRIST", "nativity"), ("THEOPHANY", "theophany"), ("CIRCUMCISION", "circumcision"), ("DORMITION", "dormition"),
    ("ELEVATION", "holy_cross"), ("INDICTION", "indiction"), ("HOLY RESURRECTION CHURCH", "dedication_resurrection_church"),
    ("SASH", "placing_of_sash"), ("ROBE", "placing_of_robe"), ("LAST JUDGMENT", "last_judgment"), ("FORGIVENESS", "forgiveness"),
    ("PRODIGAL", "prodigal_son"), ("PHARISEE", "pharisee_publican"), ("PALM SUNDAY", "palm_sunday"),
    ("ANNUNCIATION", "annunciation"), ("ANNUNICATION", "annunciation")]  # ANCA misspells it (Mar 25 2026)


def _liturgy_kontakion_kind(heading: str) -> str:
    h = _flat(heading).upper()
    return next((v for kw, v in _LIT_KONTAKION_KINDS if kw in h), "other:" + h[:30])


def parse_dismissal_phrase(f: str):
    """Great Dismissal opening (Typikon p.17-18): phrase = resurrection ('May He Who rose ...') | feast_and_resurrection
    ('May He Who <feast phrase> ..., and rose ...') | feast (no 'rose'); clause = the feast ANCA names inside the
    Theotokos / Cross / Forerunner clause ('—whose Dormition we now celebrate—'), else none. Labels only, no text."""
    m = re.search(r"THE DISMISSAL\s*(?:Priest:\s*)?(May [Hh]e [Ww]ho .{0,600}?)Christ our true God(.{0,1500}?)Joachim and Anna", f)
    if not m:
        return None
    op, seg = m.group(1), m.group(2)
    phrase = "resurrection" if re.match(r"May [Hh]e [Ww]ho rose", op) else "feast_and_resurrection" if "rose" in op else "feast"
    clause = ("theotokos" if re.search(r"holy Mother\s*—", seg) else "cross" if re.search(r"[Cc]ross\s*—", seg)
              else "forerunner" if re.search(r"Baptist John\s*—", seg) else "none")
    return dict(phrase=phrase, clause=clause)


def parse_liturgy(txt):
    k = {}
    f = _flat(txt)
    ap = parse_apolytikia(_span(txt, r"little entrance, chant the resurrectional apolytikion", r"Now sing the apolytikion of the patron") or txt)
    if ap:
        k["liturgy.apolytikia"] = ap
    m = re.search(r"(?:(?:ORDINARY|RESURRECTIONAL) |THE )?KONTAKION[A-Z ,.’'()&-]*?(?: IN TONE (\w+))?[ \t]*(?:\(CHANT\)|\(AND|\n)", txt)
    if m:
        k["liturgy.kontakion"] = dict(kind=_liturgy_kontakion_kind(m.group(0)), tone=_word(m.group(1)) if m.group(1) else None)
    ep = re.search(r"THE EPISTLE[ \t]*\n?\s*\(For ([^)]+)\)", txt)
    owner = None
    if ep:
        owner = "sunday" if re.search(r"Sunday|Week|Holy Fathers|Holy Forefathers", ep.group(1)) else "saint"
    k["liturgy.epistle"] = dict(owner=owner)
    m = (re.search(r"Epistle[^\n]*\((\d+:\d+[-–\d:,; ]*)\)", txt) or re.search(r"Epistle of [^(]*\((\d+:\d+[-–\d:,; ]*)\)", f)
         or re.search(r"Reading from (?:the )?Acts of the (?:Holy )?Apostles\.?\s*\((\d+:\d+[-–\d:,; ]*)\)", f, re.I))
    if m:
        k["liturgy.epistle"]["ref"] = m.group(1)
    m2 = re.search(r"Holy Gospel according to St\.? \w+\.?\s*\((\d+:\d+[-–\d:,; ]*)\)", txt)
    if m2:
        k["liturgy.gospel"] = dict(ref=m2.group(1).strip())
    if owner:  # circular: the key shows the prokeimenon owner only through the Epistle subtitle
        k["liturgy.prokeimenon"] = dict(owner=owner)
    a = re.search(r"of our father among the saints, ([A-Z][A-Za-z ]+?)(?:,| archbishop)", f)
    if "Priest: May he who rose" in f or "THE DISMISSAL" in f:
        k["liturgy.dismissal"] = dict(author="Basil the Great" if a and "Basil" in a.group(1) else "John Chrysostom" if a else None,
                                      saint_named=_dismissal_names_saint(f))
    ph = parse_dismissal_phrase(f)
    if ph:
        k["liturgy.dismissal_phrase"] = ph
    if a:  # the READ dismissal names the Liturgy's author ('... of our father among the saints, John Chrysostom / Basil the Great')
        k["liturgy.author"] = dict(author="Basil the Great" if "Basil" in a.group(1) else "John Chrysostom")
    return k


# ------------------------------------------------------------------ Major-feast documents (work package I)
# Full-text festal files ('Great Vespers of August 06', 'Festal Orthros on ...', 'Divine Liturgy Variables on ...'):
# headings differ from the Sunday Abbr template, so these parsers read the festal layout and only emit what it prints.
_DAYS = "SUNDAY MONDAY TUESDAY WEDNESDAY THURSDAY FRIDAY SATURDAY".split()


def _lihc_blocks(span):
    """'Lord, I have cried' in a full text: blocks open at a centred 'For the X' heading (hymn-less verses before the first
    heading are psalm verses only); each 'Verse N.' line after a heading carries one sticheron (repeats included)."""
    res, other, cur = 0, [], None
    for ln in span.splitlines():
        s = ln.strip()
        if re.match(r"\s{3,}For (the|St\.?|Saint|Holy) ", ln) and len(s) < 110:
            cur = "res" if "Resurrection" in s else "other"
            if cur == "other":
                other.append(0)
        elif re.match(r"Verse \d+\.", ln) and cur:
            if cur == "res":
                res += 1
            else:
                other[-1] += 1
    return res, other


def _owner(h):
    return "saint" if re.search(r"\bST\.|\bSAINT\b", h) else "resurrection" if "RESURRECTION" in h else "feast"  # Sunday feast: Resurrection stichera, Glory/Now of the feast


def parse_feast_vespers(txt):
    k = {}
    m10 = re.search(r"\nVerse 10\.", txt)  # a block heading may stand just above Verse 10 (Ascension: 5 stichera each twice)
    sp = _span(txt[max(m10.start() - 300, 0):] if m10 else "", r"\n", r"DOXASTICON|O GLADSOME LIGHT|\n\s*Glory to the Father")
    if sp:
        res, oth = _lihc_blocks(sp)
        if res or oth:
            k["vespers.lihc.stichera"] = dict(res=res, other=oth, total=res + sum(oth))
    days = re.findall(r"\b(%s) PROKEIMENON IN TONE (\w+)" % "|".join(_DAYS), txt)
    great = re.search(r"GREAT PROKEIMENON IN TONE (\w+)", txt)
    if great:
        k["vespers.prokeimenon"] = dict(kind="great", tone=_word(great.group(1)))
    elif re.search(r"No daily prokeimenon is sung", txt):  # Theophany / Nativity eve: the readings follow at once
        k["vespers.prokeimenon"] = dict(kind="none", tone=None)
    elif len(days) > 1:  # year-generic text prints every evening's prokeimenon: 'the prokeimenon of the day'
        k["vespers.prokeimenon"] = dict(kind="daily", tone=None)
    elif days:
        k["vespers.prokeimenon"] = dict(kind="lord_is_king", tone=_word(days[0][1])) if days[0][0] == "SATURDAY" else \
            dict(kind="daily", tone=_word(days[0][1]))
    n = len(re.findall(r"Reader:\s+The [Rr]eading from (?!the [\w ]*Epistle)", txt))  # Old Testament readings only
    if n:
        k["vespers.readings"] = dict(count=n)
    if re.search(r"Litia and Artoklasia", txt):
        k["vespers.litia"] = dict(litia=True)
    m = re.search(r"APOSTICHA FOR ([A-Z][A-Z .’'-]+)", txt)
    if m:
        k["vespers.aposticha"] = dict(owner=_owner(m.group(1)), label=m.group(1).strip())
    tail = txt[max(txt.rfind("TRISAGION PRAYERS"), 0):]
    ap = parse_apolytikia(tail.split("THE DISMISSAL")[0])
    if ap:
        k["vespers.apolytikia"] = ap
    return k


def _katavasia(h):
    h = h.upper()
    return ("cross" if "CROSS" in h else "nativity" if re.search(r"CHRIST’?'?S NATIVITY|NATIVITY OF CHRIST", h)
            else "theophany" if "THEOPHANY" in h else "feast")


def parse_feast_matins(txt):
    k = {}
    sp = _span(txt, r"[Gg]od is the Lord", r"KATHISMATA|THE LITTLE LITANY|FESTAL ANABATHMOI")
    ap = parse_apolytikia(sp)
    if ap:
        k["matins.apolytikia"] = ap
    m = re.search(r"ORTHROS GOSPEL.{0,600}?Gospel according to (?:Saint|St\.?) \w+\.?\s*\((\d+:[-–\d:,; ]+)\)", txt, re.S | re.I)
    if m:
        k["matins.eothinon_gospel"] = dict(ref=m.group(1).strip())  # the feast's Matins Gospel (no eothinon)
    if re.search(r"EVLOGETARIA", txt):  # Sunday feast of the Theotokos class: resurrectional evlogetaria printed (the Typikon omits them)
        k["matins.evlogetaria"] = dict(kind="resurrectional")
    m = re.search(r"\n\s*(?:THE )?KATAVASIA[E]?:? (?:OF )?(?:THE )?([A-Z’' ]+?)(?: IN TONE| \(|\n)", txt)
    if m:
        k["matins.katavasia"] = dict(of=_katavasia(m.group(1)), label=m.group(1).strip())
    sp = _span(txt, r"AINOI \(PRAISES\)", r"DOXASTICON|GREAT DOXOLOGY|\n\s*Glory to the Father")
    if sp:
        total = len(re.findall(r"(?m)^\s*Verse \d+\.", sp))
        if total:
            k["matins.praises"] = dict(total=total, **parse_praises(sp))
    return k


def parse_feast_liturgy(txt):
    k = {}
    f = _flat(txt)
    m = re.search(r"SECOND ANTIPHON.{0,400}?Refrain: (?:Save us, )?O Son of God, (?:[Ww]ho )?(.{0,80}?)(?:, who sing|Alleluia)", f)
    if m:
        r2 = m.group(1).lower()
        k["liturgy.antiphons"] = dict(refrain2="resurrection" if re.search(r"rose|risen", r2) else "saints" if "wondrous in" in r2 else "feast")
    m = re.search(r"EISODIKON \(ENTRANCE HYMN\) (?:OF|FOR) ([A-Z ’']+)", txt)
    if m:
        k["liturgy.eisodikon"] = dict(kind="sunday" if "SUNDAY" in m.group(1) else "weekday" if "ORDINARY" in m.group(1) else "feast")
    if "liturgy.eisodikon" not in k and re.search(r"Eisodikon \(Entrance Hymn\) is “O come, let us worship[^”]{0,40}[Rr]isen from the dead", f):
        k["liturgy.eisodikon"] = dict(kind="sunday")  # 'as on ordinary Sundays' (Jan 1 on a Sunday)
    tri = re.search(r"ANTI-?TRISAGION.{0,200}", f)
    k["liturgy.trisagion"] = dict(kind="cross" if tri and "Cross" in tri.group(0) else "baptized" if tri else "trisagion")
    if re.search(r"BASIL LITURGY MEGALYNARION|In thee rejoiceth|All creation rejoiceth", f):
        k["liturgy.megalynarion"] = dict(kind="in_thee_rejoiceth")
    elif re.search(r"MEGALYNARION (?:OF|FOR) ", f):
        k["liturgy.megalynarion"] = dict(kind="feast")
    m = re.search(r"KOINONIKON \(COMMUNION HYMN\)(.{0,250})", f)
    if m:
        t = m.group(1)
        k["liturgy.communion"] = dict(kind="praise_the_lord" if re.search(r"Praise (?:ye )?the Lord from the heavens", t)
                                      else "cup_of_salvation" if "cup of salvation" in t
                                      else "chosen_zion" if re.search(r"(?:chosen|elected) (?:Zion|Sion)", t) else "feast")
    if re.search(r"[Ii]nstead of singing “?We have seen the true light,?”?,? sing the [Aa]polytikion", f):
        k["liturgy.final_hymn"] = dict(kind="feast_troparion")
    elif re.search(r"Instead of “We have seen the true light,?” sing “Christ is [Rr]isen”", f):  # Pascha
        k["liturgy.final_hymn"] = dict(kind="christ_is_risen")
    elif re.search(r"Post-Communion Hymn: “?We have seen the true light", f):
        k["liturgy.final_hymn"] = dict(kind="true_light")
    if re.search(r"THE DISMISSAL\s*(?:Priest:\s*)?May Christ our true God", f):  # weekday Great Dismissal without a phrase
        k["liturgy.dismissal_phrase"] = dict(phrase="plain", clause="none")
    m = re.search(r"(Do NOT|Now) sing the apolytikion of the patron", f)
    if m:
        k["liturgy.patron"] = dict(patron=m.group(1) == "Now")
    return k


# ------------------------------------------------------------------ Pascha (data/rules/pascha.yaml)
def parse_holy_saturday(txt):
    """ANCA 'Vesperal Divine Liturgy of St Basil' on Holy Saturday (Vespers part only): Lord-I-have-cried blocks, the
    anti-alleluarion that replaces the daily prokeimenon, the count of Old Testament readings."""
    k = {}
    sp = _span(txt, r"“O LORD I HAVE CRIED” IN TONE", r"DOXASTICON FOR")
    res, oth = _lihc_blocks(sp)
    if res or oth:
        k["vespers.lihc.stichera"] = dict(res=res, other=oth, total=res + sum(oth))
    m = re.search(r"ANTI-ALLELUARION IN TONE (\w+)", txt)
    if m and re.search(r"Daily Prokeimenon is not sung", txt):
        k["vespers.prokeimenon"] = dict(kind="arise_o_god", tone=_word(m.group(1)))
    n = len(re.findall(r"Reader:\s+The reading from (?!the Epistle)", txt, re.I))
    if n:
        k["vespers.readings"] = dict(count=n)
    return k


def parse_agape(txt):
    """ANCA 'Paschal Agape Great Vespers' (Sunday evening of Pascha), with or without a Great Martyr George section."""
    k = {}
    f = _flat(re.sub(r"Agape Vespers\s+Great Vespers \d+\s+(?:with St\. George|Agape Vespers)", " ", txt))  # running page headers split sentences
    res, oth = _lihc_blocks(_span(txt, r"“O LORD I HAVE CRIED” IN TONE", r"DOXASTICON FOR"))
    if res or oth:
        k["agape.lihc.stichera"] = dict(res=res, other=oth, total=res + sum(oth))
    m = re.search(r"GREAT PROKEIMENON IN TONE (\w+)", txt)
    if m:
        k["agape.prokeimenon"] = dict(kind="great", tone=_word(m.group(1)))
    m = re.search(r"Holy Gospel according to Saint John \((\d+:\d+[-–\d:]*)\)", f)
    if m:
        k["agape.gospel"] = dict(ref=m.group(1))
    if "PASCHAL STICHERA IN TONE" in txt:
        tail = txt[txt.index("APOSTICHON"):] if "APOSTICHON" in txt else txt
        k["agape.aposticha"] = dict(kind="paschal", glory="saint" if re.search(r"DOXASTICON FOR ST\.", tail) else "pascha")
    k["agape.apolytikia"] = dict(saint=bool(re.search(r"APOLYTIKION OF ST\.", txt)))
    if "THE DISMISSAL" in txt:
        k["agape.dismissal"] = dict(saint_named=_dismissal_names_saint(f))
    return k


def parse_paschal_vigil(txt):
    """ANCA 'Outline of Rubrics for Great and All-Holy Pascha' (Midnight Office, Resurrection Service, Paschal Orthros): Orthros slots only."""
    k = {}
    m = re.search(r"\((\d+)(?:st|nd|rd|th) Eothinon Gospel\)", txt)
    if m:
        k["matins.eothinon_gospel"] = dict(number=int(m.group(1)))
    if re.search(r"To be read:\s+Kontakion: “Though Thou, O deathless one", txt):
        k["matins.kontakion"] = dict(kind="feast")  # the kontakion, oikos and synaxarion of Pascha replace the resurrectional kontakion
    if re.search(r"Katavasia \(repeat the Irmos\)", txt):
        k["matins.katavasia"] = dict(of="feast")
    sp = _span(txt, r"\n\s*8\.\s+Praises", r"\n\s*9\.\s")
    r = re.search(r"(\d+) stichera for the Resurrection", sp)
    o = re.search(r"(\d+) Pascha Stichera", sp)
    if r and o:
        k["matins.praises"] = dict(total=int(r.group(1)) + int(o.group(1)), res=int(r.group(1)), other=[int(o.group(1))],
                                   glory="other" if "Doxasticon" in sp else None)
    return k


def _feast_day(service, date):
    from .calfacts import major_feast  # lazy: calfacts is the calendar side
    return major_feast(date + dt.timedelta(days=1) if service == "vespers" else date)[0]


def _FEAST_SLOT_FEASTS():
    from .calfacts import FEAST_SLOT_FEASTS
    return FEAST_SLOT_FEASTS


def key_for(service: str, date: dt.date, cache: str, offline: bool = False):
    """-> (key dict slot->attrs, [source labels], [notes]). Empty key => `no key`."""
    notes, used = [], []
    from .calfacts import pascha as _pascha  # lazy (calendar side)
    ld = date + dt.timedelta(days=1) if service == "vespers" else date
    if ld == _pascha(ld.year) and service != "liturgy":  # Pascha day: Holy Saturday Vesperal Liturgy (eve), Paschal Vigil outline, Agape Vespers
        kind = {"vespers": "VDL", "matins": "VIGIL", "agape": "VESP"}[service]
        t = fetch(date, kind, cache, offline)
        if not t:
            return {}, used, [f"no ANCA {kind} file for this date"]
        used.append(f"{kind} {date:%b %d %Y}")
        return {"vespers": parse_holy_saturday, "matins": parse_paschal_vigil, "agape": parse_agape}[service](t), used, notes
    if service == "liturgy":
        t = fetch(date, "READ", cache, offline)
        if not t:
            return {}, used, ["no ANCA READ file for this date"]
        used.append(f"READ {date:%b %d %Y}")
        k = parse_liturgy(t)
        if _feast_day(service, date):  # festal Liturgy parts (feast-only slots)
            fk = parse_feast_liturgy(t)
            pat = fk.pop("liturgy.patron", None)
            if pat and "liturgy.apolytikia" in k:  # 'Do NOT sing the apolytikion of the patron saint' on Lord's/Theotokos feasts
                k["liturgy.apolytikia"]["patron"] = pat["patron"]
            k.update({s: v for s, v in fk.items() if s not in k})
            if _feast_day(service, date) in _FEAST_SLOT_FEASTS():  # '(For the Transfiguration)': the feast's own reading
                for s in ("liturgy.epistle", "liturgy.prokeimenon"):
                    if k.get(s, {}).get("owner") == "saint":
                        k[s]["owner"] = "feast"
        return k, used, notes
    sunday = date + dt.timedelta(days=1) if service == "vespers" else date  # Abbr is keyed by the Sunday
    ab = fetch(sunday, "Abbr", cache, offline)
    full = fetch(date, "VESP" if service == "vespers" else "ORTHROS", cache, offline)
    ves, mat = split_abbr(ab) if ab else ("", "")
    parse = (lambda t: parse_vespers(t)) if service == "vespers" else (lambda t: parse_matins(t))
    key = {}
    if ab:
        used.append(f"Abbr {sunday:%b %d %Y}")
        key.update(parse(ves if service == "vespers" else mat))
    if full:
        extra = parse(full)
        added = {s: v for s, v in extra.items() if s not in key}
        if added:
            used.append(f"{'VESP' if service == 'vespers' else 'ORTHROS'} {date:%b %d %Y}")
        key.update(added)
        if "matins.kontakion" in extra and service == "matins":  # the full ORTHROS text is authoritative over the Abbr template (2025-03-23)
            key["matins.kontakion"] = extra["matins.kontakion"]
        if _feast_day(service, date):  # festal full text: festal layout wins where the Abbr is silent (prokeimenon: always)
            fk = parse_feast_vespers(full) if service == "vespers" else parse_feast_matins(full)
            key.update({s: v for s, v in fk.items() if s not in key or (s == "vespers.prokeimenon" and not ab)})
    if not key:
        notes.append("no ANCA file for this date")
    return key, used, notes
