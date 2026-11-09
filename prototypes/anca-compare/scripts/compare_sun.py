"""PROTOTYPE (throwaway): Sunday Matins/Liturgy Rule predictions vs ANCA keys (sun_keys.csv from parse_sun.py)."""
import csv, re, sqlite3, collections, datetime as dt
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
db = sqlite3.connect(ROOT.parent.parent / "db/yocal/YOCal_Master.db"); db.row_factory = sqlite3.Row
keys = list(csv.DictReader(open(ROOT / "sun_keys.csv", encoding="utf-8")))
def num(s):
    m = re.search(r"\d+", s or ""); return int(m.group()) if m else None
def lect(code):
    x = db.execute("select lect_1,lect_2 from yocal_lections where code=?", (code,)).fetchone(); return x or (None, None)
def norm(s): return re.sub(r"[\s]", "", (s or "").replace("–", "-")).lower()
def verses(s):  # set of chapter:verse tokens, notation-insensitive (a/b parts dropped, ;/, equal)
    s = re.sub(r"[a-z]\b", "", (s or "").replace("–", "-").lower()); out = set(); ch = None
    for part in re.split(r"[;,]", re.sub(r"[a-z]+\s*(?=\d)", "", s)):
        part = part.strip()
        if not part: continue
        m = re.match(r"(\d+):(\d+)(?:-(?:(\d+):)?(\d+))?$", part)
        if m:
            ch = int(m.group(1)); a = int(m.group(2)); c2 = int(m.group(3) or ch); b = int(m.group(4) or a)
            out |= {(ch, v) for v in range(a, b + 1)} if c2 == ch else {(ch, a)}
        elif re.match(r"\d+(?:-\d+)?$", part) and ch:
            a, _, b = part.partition("-"); out |= {(ch, v) for v in range(int(a), int(b or a) + 1)}
    return out
def same(a, b): return verses(a) == verses(b) or norm(a) == norm(b)

# ---- Liturgy kontakion fixed-window table (#25), ordinary-time windows only. returns class or None (movable/unmodelled)
def kon_pred(d, desig):
    mm = d.strftime("%m-%d")
    if "after Pentecost" in desig or not re.search(r"Pascha|Pentecost|Lent|Triodion|Publican|Prodigal|Forgiveness|Meatfare|Sunday of|Fathers|Thomas|Myrrh|Paralytic|Samaritan|Blind|Ascension|Mid", desig):
        pass
    elif "after Pentecost" not in desig:
        return None
    if mm == "09-01": return "indiction"
    if "08-24" <= mm <= "09-12": return "nativity_theotokos"
    if mm == "09-13": return "dedication"
    if "09-14" <= mm <= "09-21": return "cross"
    if "09-22" <= mm <= "11-07": return "undisputed"
    if "11-08" <= mm <= "11-24": return "entrance"
    if "11-26" <= mm <= "12-24": return "preparation"
    if "12-25" <= mm <= "12-31": return "nativity"
    if "07-27" <= mm <= "08-13": return "transfiguration"
    if "08-15" <= mm <= "08-23": return "dormition"
    if "01-01" <= mm <= "01-14": return "theophany_cycle"
    if "06-01" <= mm <= "07-26": return "undisputed"
    return None
def kon_obs(h):
    h = h.upper()
    for k, pat in [("undisputed", r"ORDINARY"), ("entrance", r"ENTRANCE|PRESENTATION OF THE THEOTOKOS"), ("preparation", r"PREPARATION|NATIVITY OF (OUR LORD|CHRIST)? ?.*FOREFEAST"), ("transfiguration", r"TRANSFIGURATION"),
                   ("nativity_theotokos", r"NATIVITY OF THE THEOTOKOS|BIRTH"), ("cross", r"CROSS|EXALTATION"), ("dormition", r"DORMITION"), ("nativity", r"NATIVITY"), ("indiction", r"INDICTION|NEW YEAR"), ("dedication", r"DEDICATION"),
                   ("theophany_cycle", r"THEOPHANY|CIRCUMCISION|EPIPHANY")]:
        if re.search(pat, h): return k
    return "other:" + h[:40]

tally = collections.defaultdict(collections.Counter); diffs = collections.defaultdict(list)
def rec(slot, d, status, det=""):
    tally[slot][status] += 1
    if status == "diff": diffs[slot].append((d, det))
for k in keys:
    d = dt.date.fromisoformat(k["date"])
    r = db.execute("select * from yocal_main where date=?", (k["date"],)).fetchone()
    if not r: continue
    tone, eoth, desig = num(r["tone"]), num(r["eothinon"]), r["desig_a"] or ""
    # ---------------- Matins
    if k.get("M_eothinon"):
        rec("matins.eothinon_gospel", k["date"], "match" if int(k["M_eothinon"]) == eoth else "diff", f"key {k['M_eothinon']} db {eoth}")
    else: rec("matins.eothinon_gospel", k["date"], "not_in_key")
    for slot, col in [("matins.prokeimenon.tone", "M_prok_tone"), ("matins.ainoi.tone", "M_ainoi_tone")]:
        if k.get(col): rec(slot, k["date"], "match" if int(k[col]) == tone else "diff", f"key {k[col]} db {tone} [{desig}]")
        else: rec(slot, k["date"], "not_in_key")
    # ---------------- Liturgy
    basil_pred = bool(re.search(r"(1st|2nd|3rd|4th|5th) of Great Lent", desig)) and not re.search(r"Annunciation", desig) or k["date"][5:] == "01-01"
    if k.get("L_rite"):
        obs_b = k["L_rite"] == "basil"
        rec("liturgy.rite", k["date"], "match" if obs_b == basil_pred else "diff", f"pred basil={basil_pred} key {k['L_rite']} [{desig}]")
    if r["is_comm_apos"] == 0 and k.get("L_epistle_ref"):
        ep = lect(r["a_code"])[0] or ""
        ref = ep.split()[-1] if ep else ""
        rec("liturgy.epistle.ref", k["date"], "match" if same(ref, k["L_epistle_ref"]) else "diff", f"db {ep} key {k['L_epistle_ref']}")
    elif k.get("L_epistle_ref"): rec("liturgy.epistle.ref", k["date"], "saint_epistle_skipped")
    if k.get("L_gospel_ref") and not r["is_comm_gosp"]:
        gp = lect(r["g_code"])[1] or ""; ref = gp.split()[-1] if gp else ""
        rec("liturgy.gospel.ref", k["date"], "match" if same(ref, k["L_gospel_ref"]) or verses(k["L_gospel_ref"]) <= verses(ref) else "diff", f"db {gp} key {k['L_gospel_ref']}")
    kp = kon_pred(d, desig)
    if kp is None: rec("liturgy.kontakion", k["date"], "movable_unmodelled", f"{desig} :: {k['L_kontakion']}")
    elif k.get("L_kontakion"):
        ko = kon_obs(k["L_kontakion"]); rec("liturgy.kontakion", k["date"], "match" if ko == kp else "diff", f"pred {kp} key {ko} ({k['L_kontakion'][:50]}) [{desig}]")
    else: rec("liturgy.kontakion", k["date"], "not_in_key")
print(f"{len(keys)} Sundays with READ key")
for s in sorted(tally): print(f"{s:28s}", dict(tally[s]))
for s in sorted(diffs):
    print(f"\n== {s} diffs ({len(diffs[s])})"); [print("  ", *x) for x in diffs[s][:25]]
