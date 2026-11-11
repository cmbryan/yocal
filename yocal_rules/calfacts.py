"""Calendar adapter: YOCal master DB (+ ALWB glory flags) -> closed context-fact dict for the Rules."""
from __future__ import annotations

import csv
import datetime as dt
import os
import re
import sqlite3
import unicodedata
from collections import defaultdict

from .rules import DATA

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB = os.path.join(REPO, "db", "yocal", "YOCal_Master.db")

# fixed Major feasts (+ Theotokos feasts); Sundays on these are outside the implemented slice
FIXED_MAJOR = {"01-01", "01-06", "02-02", "03-25", "08-06", "08-15", "09-08", "09-14", "11-21", "12-25"}


def pascha(y: int) -> dt.date:
    """Orthodox Pascha, Gregorian date (Julian computus + 13 days; valid 1900-2099)."""
    a, b, c = y % 4, y % 7, y % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    m, dd = divmod(d + e + 114, 31)
    return dt.date(y, m, dd + 1) + dt.timedelta(days=13)


def season(d: dt.date) -> str:
    k = (d - pascha(d.year)).days
    if -70 <= k < -48:
        return "triodion"
    if -48 <= k < 0:
        return "lent"
    if k == 0:
        return "pascha"
    if 0 < k <= 49:
        return "pentecostarion"
    return "ordinary"


# ---- ALWB glory flags (principal commemoration -> has Vespers Glory) --------------------------------
STOP = set("""saint saints st holy martyr martyrs hieromartyr hieromartyrs great venerable our father fathers among the of and in at on to with for from his her their
devout god bearing mother righteous apostle apostles prophet equal equal-to-the-apostles bishop archbishop patriarch metropolitan pope wonderworker wonderworkers
unmercenaries unmercenary confessor confessors new blessed repose translation relics synaxis commemoration memory finding icon city monk monks abbot abbess
ascetic ascetics those them him fool christ sake martyrdom of-the church mount holy-mountain athos elder younger first second third""".split())
SYN = [("theophany", "epiphany"), ("godbearer", "godbearing"), ("wonder worker", "wonderworker"), ("leave taking", "leavetaking"),
       ("translation", "transfer"), ("placing", "placement"), ("eleutherius", "eleftherios"), ("hilarion", "hilary")]


def _norm(s: str) -> set:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\([^)]*\)", " ", s).replace("-", " ")
    for a, b in SYN:
        s = s.replace(a, b)
    s = re.sub(r"god bear", "godbear", s)
    s = re.sub(r"(?<![a-z])eu", "ef", s).replace("th", "t").replace("ph", "f").replace("ks", "x")
    return {t[:5] for t in re.findall(r"[a-z]+", s) if t not in STOP and t[:5] not in STOP and len(t) > 2}


def _alwb():
    d = defaultdict(list)
    with open(os.path.join(DATA, "menaion_commems.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d[r["date_key"]].append(r)
    return d


_ALWB = None
_BASIL = None


def _basil():
    global _BASIL
    if _BASIL is None:
        with open(os.path.join(DATA, "bpbasil_flags.csv"), encoding="utf-8") as f:
            _BASIL = {r["date_key"]: r for r in csv.DictReader(f)}
    return _BASIL


_LAUDS = None


def _alwb_lauds():
    """mm-dd -> number of Lauds stichera of the ALWB main commemoration block (data/alwb_lauds.csv; Greek data is partial)."""
    global _LAUDS
    if _LAUDS is None:
        with open(os.path.join(DATA, "alwb_lauds.csv"), encoding="utf-8") as f:
            _LAUDS = {r["date_key"]: int(r["lauds_count"]) for r in csv.DictReader(f) if r["role"] == "main"}
    return _LAUDS


def _overrides():
    p = os.path.join(DATA, "glory_overrides.yaml")
    import yaml
    return {o["mmdd"]: o for o in (yaml.safe_load(open(p, encoding="utf-8")) or [])} if os.path.exists(p) else {}


def principal_glory(key: str, major: str):
    """Principal-commemoration glory (#28/#31): cited override -> major_commem matched to ALWB -> ALWB main (inferred)
    -> missing; then Bp Basil rank as positive-only evidence (ALWB OR Bp Basil, never a veto).
    -> (has_glory True/False/None, source)."""
    global _ALWB
    _ALWB = _ALWB or _alwb()
    ov = _overrides().get(key)
    if ov:
        return bool(ov["glory"]), f"override: {ov['citation']}"
    blocks = _ALWB.get(key, [])
    main = next((b for b in blocks if b["role"] == "main"), None)
    alwb, src = None, ""
    if not blocks:
        src = "no ALWB day"
    elif major:
        mt, best = _norm(major), []
        for b in blocks:
            bt = _norm(b["name"])
            if bt and mt and len(bt & mt) >= 1 and len(bt & mt) / min(len(bt), len(mt)) >= 0.5:
                best.append((len(bt & mt) / min(len(bt), len(mt)), b))
        if not best:
            src = "major_commem unmatched in ALWB"
        else:
            best.sort(key=lambda x: -x[0])
            top = [b for s, b in best if s == best[0][0]]
            if len(top) > 1 and len({t["has_vespers_glory"] for t in top}) > 1:
                src = "ambiguous ALWB match"
            else:
                alwb, src = top[0]["has_vespers_glory"] == "1", f"ALWB {key} {top[0]['role']}"
    elif main:
        alwb, src = main["has_vespers_glory"] == "1", f"ALWB {key} main (inferred)"
    else:
        src = "no ALWB main"
    bb = _basil().get(key)
    basil = bool(bb and bb["implies_glory"] == "1")
    if alwb is True:
        return True, src + (" + Bp Basil rank agrees" if basil else "")
    if basil:
        return True, (src + "; " if src else "") + f"Bp Basil rank {bb['rank']}{' (2 Glories)' if bb['rank'] == 'SIMPLE' else ''} implies glory"
    return alwb, src


_CH5 = None


def _ch5_glory():
    """mm-dd -> saint-has-Glory implied by the Typikon Ch V per-date Sat-Vespers count (6R+4 yes, 7R+3 no)."""
    global _CH5
    if _CH5 is None:
        import yaml
        _CH5 = {}
        for r in yaml.safe_load(open(os.path.join(DATA, "rules", "vespers_lihc_ch5.yaml"), encoding="utf-8")):
            md = next(w["args"][0] for w in r["when"] if w["pred"] == "menaion_date_is")
            res, oth = r["fill"]["res"], r["fill"]["other"]
            if (res, oth) == (6, [4]):
                _CH5[md] = True
            elif (res, oth) == (7, [3]):
                _CH5[md] = False
    return _CH5


def _num(s):
    m = re.search(r"\d+", s or "")
    return int(m.group()) if m else None


_SLICES = None


def _slices():
    """data/slices.yaml: which seasons / fore-after-feasts / fixed Major feasts have Rules (see that file)."""
    global _SLICES
    if _SLICES is None:
        import yaml
        d = yaml.safe_load(open(os.path.join(DATA, "slices.yaml"), encoding="utf-8")) or {}
        _SLICES = {k: [str(x) for x in (d.get(k) or [])] for k in ("supported_seasons", "supported_fore_after", "supported_fixed_major", "supported_movable_major", "supported_major_eve_vespers")}
    return _SLICES


def named_sunday(ld: dt.date):
    """Sundays with their own Typikon section (Vespers 'Glory' for the Sunday's commemoration, saint apolytikion)."""
    if ld.weekday() != 6:
        return None
    m = ld.strftime("%m-%d")
    if "07-13" <= m <= "07-19":
        return "fathers_4th_council"       # Typikon p.432
    if "10-11" <= m <= "10-17":
        return "fathers_7th_council"       # Typikon p.93 (heading 'Oct 1-17'); window narrowed by ANCA practice
    if "12-11" <= m <= "12-17":
        return "forefathers"               # Typikon p.126
    if m in ("12-18", "12-19"):
        return "before_nativity_18_19"     # Typikon p.133
    if m == "12-24":
        return "before_nativity_24"        # Typikon p.136
    if "01-02" <= m <= "01-05":
        return "before_theophany"          # Typikon pp.167-169 (Sunday before Theophany, Jan 2-4 and Jan 5)
    if (ld - pascha(ld.year)).days == 56:
        return "all_saints"                # Typikon p.540
    return None


# fore/after-feast periods (work package H): DB fore_after substring -> (feast key, class); first match wins
FEAST_PERIODS = [
    ("Theophany", "theophany", "lord"), ("Presentation of the Lord", "presentation", "lord"),
    ("Meeting of the Lord", "presentation", "lord"), ("Entrance of the Lord", "presentation", "lord"),
    ("Annunciation", "annunciation", "theotokos"), ("Pascha", "pascha", "lord"), ("Ascension", "ascension", "lord"),
    ("Pentecost", "pentecost", "lord"), ("Nativity of the Forerunner", "nativity_forerunner", "saint"),
    ("Chief Apostles", "peter_paul", "saint"), ("Procession", "procession_cross", "minor"),
    ("Transfiguration", "transfiguration", "lord"), ("Dormition", "dormition", "theotokos"),
    ("Beheading", "beheading", "saint"), ("Nativity of the Mother of God", "nativity_theotokos", "theotokos"),
    ("Elevation", "elevation", "lord"), ("Entrance of the Mother of God", "entrance_theotokos", "theotokos"),
    ("Conception", "conception", "minor"), ("Nativity of Christ", "nativity", "lord")]


def feast_period(fore_after: str, major: str = ""):
    """Normalise the DB fore_after text (else a major_commem that is itself a period, e.g. 'Leavetaking of The Theophany'
    on Jan 14) -> ('afterfeast:dormition', 'theotokos', from_major) or ('', '', False)."""
    txt, from_major = fore_after, False
    if not txt and re.match(r"(Forefeast|Afterfeast|Leave-?taking) of", major or "", re.I):
        txt, from_major = major, True
    m = re.match(r"(Forefeast|Afterfeast|Leave-?taking) of", txt or "", re.I)
    if not m:
        return "", "", False
    kind = m.group(1).lower().replace("-", "")
    for sub, key, cls in FEAST_PERIODS:
        if sub.lower() in txt.lower():
            return f"{kind}:{key}", cls, from_major
    return f"{kind}:other", "", from_major


# Major feasts (GLOSSARY 'Major feast', work package I): normalised id and class. Fixed by mm-dd, movable by days from Pascha.
MAJOR_FIXED = {"12-25": ("nativity", "lord"), "01-01": ("circumcision", "lord"), "01-06": ("theophany", "lord"),
               "02-02": ("presentation", "lord"), "03-25": ("annunciation", "theotokos"), "08-06": ("transfiguration", "lord"),
               "08-15": ("dormition", "theotokos"), "09-08": ("nativity_theotokos", "theotokos"), "09-14": ("elevation", "lord"),
               "11-21": ("entrance", "theotokos")}
MAJOR_MOVABLE = {-7: ("palm_sunday", "lord"), 0: ("pascha", "lord"), 39: ("ascension", "lord"), 49: ("pentecost", "lord")}
# feasts whose services carry the feast-only slots (slots.yaml `only: major_feast_slots`); Palm Sunday, Pascha and Pentecost
# are Sunday-cycle days of the Triodion / Pentecostarion packages and keep the Sunday slot set
FEAST_SLOT_FEASTS = {v[0] for v in MAJOR_FIXED.values()} | {"ascension"}


def major_feast(ld: dt.date):
    """-> (id, class, movable) for a Major feast day, else ('', '', False). Leaves Sunday coincidence to the caller."""
    k = (ld - pascha(ld.year)).days
    if k in MAJOR_MOVABLE:
        return MAJOR_MOVABLE[k] + (True,)
    if ld.strftime("%m-%d") in MAJOR_FIXED:
        return MAJOR_FIXED[ld.strftime("%m-%d")] + (False,)
    return "", "", False


def liturgical_date(service: str, date: dt.date) -> dt.date:
    """Great Vespers on Saturday belongs to Sunday (liturgical-day unit)."""
    return date + dt.timedelta(days=1) if service == "vespers" else date


def load_facts(date: dt.date, service: str, db_path: str = DEFAULT_DB) -> dict:
    ld = liturgical_date(service, date)
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"calendar DB not found: {db_path} (build with db/build.sh)")
    con = sqlite3.connect(db_path)
    cur = con.execute("select * from yocal_main where date=?", (ld.isoformat(),))
    row = cur.fetchone()
    if row is None:
        raise LookupError(f"{ld} is not in the calendar DB")
    r = dict(zip([c[0] for c in cur.description], row))

    def lect(code):
        x = con.execute("select lect_1,lect_2 from yocal_lections where code=?", (code,)).fetchone()
        return x or (None, None)

    ep = lect(r["c_code"])[0] if r["is_comm_apos"] else lect(r["a_code"])[0]
    sunday_ep = lect(r["a_code"])[0]
    gp = lect(r["c_code"])[1] if r["is_comm_gosp"] else lect(r["g_code"])[1]
    major = (r["major_commem"] or "").strip()
    mmdd = ld.strftime("%m-%d")
    key = r["c_code"] if r["c_code"] and re.fullmatch(r"\d\d-\d\d", r["c_code"]) else mmdd
    glory, gsrc = principal_glory(key, major)
    if ld.weekday() == 6 and mmdd in _ch5_glory():
        indep = f"independent ALWB/Bp Basil view: {glory if glory is not None else 'none'}"
        glory, gsrc = _ch5_glory()[mmdd], f"Typikon Ch V per-date stichera count (6R+4 = Glory, Ch III p.48); {indep}"
    ssn = season(ld)
    sl = _slices()
    reasons = []
    mf, mf_cls, mf_mov = major_feast(ld)
    if ld.weekday() != 6 and not mf:
        reasons.append("not a Sunday")
    if mf_mov and ld.weekday() != 6 and mf not in sl["supported_movable_major"]:
        reasons.append(f"Major feast ({mf})")
    if mf in ("nativity", "theophany") and ld.weekday() == 0:  # Monday order (Typikon p.145, p.174): no Rules yet
        reasons.append(f"Major feast ({mf}) on a Monday")
    if ssn not in sl["supported_seasons"]:
        reasons.append(f"{ssn} season")
    eve_only = service == "vespers" and f"{mmdd}:{(ld - dt.timedelta(days=1)).strftime('%A')}" in sl["supported_major_eve_vespers"]  # eve Vespers only, per eve weekday
    if mmdd in FIXED_MAJOR and not eve_only and (mmdd + (":sunday" if ld.weekday() == 6 else "")) not in sl["supported_fixed_major"]:
        reasons.append("fixed Major feast" + (" on a Sunday" if ld.weekday() == 6 else ""))  # 'mm-dd' = weekday order, 'mm-dd:sunday' = Sunday order
    elif mmdd in FIXED_MAJOR and ld.weekday() == 6 and ssn != "ordinary":  # Sunday order Rules are written for the ordinary season only (Presentation on a Triodion Sunday: p.220)
        reasons.append(f"fixed Major feast on a Sunday of the {ssn} season")
    fa = (r["fore_after"] or "").strip()
    if fa and not any(x in fa for x in sl["supported_fore_after"]):
        reasons.append(f"fore/after-feast ({fa})")
    fp, fp_cls, fp_major = feast_period(fa, major)
    return dict(
        feast_period=fp, feast_period_class=fp_cls,
        # a principal commemoration with a Glory inside the period (the 'great saint' of Typikon p.12/p.16), not the period itself
        feast_period_saint=bool(fp and major and not fp_major and glory is True),
        date=ld.isoformat(), service_date=date.isoformat(), mmdd=mmdd, weekday=ld.strftime("%A"), year=ld.year,
        tone=_num(r["tone"]), eothinon=_num(r["eothinon"]), desig=r["desig_a"], desig_g=r["desig_g"],
        epistle_owner="saint" if r["is_comm_apos"] else "sunday",
        gospel_owner="saint" if r["is_comm_gosp"] else "sunday",
        epistle_ref=ep, sunday_epistle_ref=sunday_ep, gospel_ref=gp,
        all_saints_sunday="Sunday of All Saints" in f"{r['desig_a']} {r['desig_g']}",
        leavetaking=(_basil().get(mmdd, {}).get("rank") == "LEAVETAKING"),
        saint_in_calendar=bool(major), principal_name=major,
        saint_has_glory=glory, glory_source=gsrc,
        dismissal_saint=major or re.split(r"\)\.\s+(?=[A-Z])", (r["class_5"] or "").strip())[0].strip(" ."),
        named_sunday=named_sunday(ld),
        archangel_feast=bool(re.search(r"archangel|bodiless", major, re.I)),
        two_sets_of_3=_basil().get(mmdd, {}).get("two_sets_of_3") == "1",
        bb_rank=_basil().get(mmdd, {}).get("rank", ""),
        saint_lauds=_alwb_lauds().get(mmdd, 0),  # ALWB (Greek, partial) main-block Matins Lauds stichera count; 0 = none recorded
        other_commem=(r["class_5"] or "").strip(),
        uk_commem=(r["british"] or "").strip(),
        basil=bool((r["basil"] or "").strip()),
        # Annunciation on a Lent Sunday: Chrysostom (Typikon Lent 3 p.283; ANCA Lent 5 2018); the DB flag says Basil (#19)
        liturgy_author="Basil the Great" if (r["basil"] or "").strip() and not (ld.weekday() == 6 and mmdd == "03-25") else "John Chrysostom",
        pascha_days=(ld - pascha(ld.year)).days,
        fore_after=fa,  # DB fore_after text (forefeast/afterfeast/leavetaking), '' if none
        season=ssn, in_slice=not reasons, slice_reasons=reasons,
        # Major feast (work package I): id ('' if none), class lord|theotokos, movable flag; feast_slots gates the feast-only slots
        major_feast=mf, major_feast_class=mf_cls, major_feast_movable=mf_mov, major_feast_slots=mf in FEAST_SLOT_FEASTS, major_feast_sunday=mf in FEAST_SLOT_FEASTS and ld.weekday() == 6,
        # the feast's Matins Gospel (DB lection code m-<mm-dd>, m-<g_code> for movable feasts), '' if the DB has none
        feast_matins_gospel_ref=(lect(f"m-{mmdd}")[1] or lect(f"m-{r['g_code']}")[1] or "").strip() if mf else "",
        # the eve's own calendar row (Vespers is served on the eve): DB Liturgy-of-St-Basil flag (Vesperal Liturgy)
        eve_basil=bool(service == "vespers" and (con.execute("select basil from yocal_main where date=?", (date.isoformat(),)).fetchone() or [""])[0]),
    )

