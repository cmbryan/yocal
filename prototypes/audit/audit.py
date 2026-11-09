#!/usr/bin/env python3
"""PROTOTYPE (throwaway, wipe me): rule-coverage audit over the full ANCA range.

Question (wayfinder ticket "Prototype: run audit harness over full ANCA range"):
measure coverage = slot x observed context class -> Rule status (explicit/inferred/missing)
+ match rate vs ANCA key + unexplained diffs (candidate Rule errors).

Scope: every Sunday 2018-02-18..2026-11-22 (412) = Sat Great Vespers + Sun Matins + Sun Liturgy.
Keys: Matins/Liturgy from ../anca-compare/sun_keys.csv (+sun_matins_kontakion.csv); Vespers
VESP.pdf fetched to --cache (scratch). Rules here are Python stubs mirroring the already-decided
research (cited per rule); the YAML schema was validated in ../rule-spike and is not re-tested.
Only decided+encodable Rules are encoded; everything else is "missing (not encoded)" by design.

  python audit.py [--cache DIR]      -> audit.csv, summary on stdout
"""
import argparse, csv, datetime as dt, json, os, re, sqlite3, subprocess, urllib.request, urllib.error, urllib.parse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..")
DB = os.path.join(P, "../db/yocal/YOCal_Master.db")
WORDS = {w: i for i, w in enumerate("ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE TEN ELEVEN".split())}
LORD = {"01-01", "01-06", "02-02", "03-25", "08-06", "08-15", "09-08", "09-14", "11-21", "12-25"}  # fixed Major feasts

def pascha(y):
    a, b, c = y % 4, y % 7, y % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    m, dd = divmod(d + e + 114, 31)
    return dt.date(y, m, dd + 1) + dt.timedelta(days=13)

def pnum(s):
    m = re.search(r"\d+", s or "")
    return int(m.group()) if m else None

# ------------------------------------------------------------------ context class (observed from calendar)
def ctx_class(d, fa, desig=''):
    k = (d - pascha(d.year)).days
    sat = d - dt.timedelta(1)
    mm, ms = d.strftime("%m-%d"), sat.strftime("%m-%d")
    if k in (-7, 0, 49): return "movable_major_feast"
    if mm in LORD: return "major_feast_on_sunday"
    if ms in LORD: return "major_feast_eve_sat"
    if -70 <= k < -48: return "triodion"
    if -48 <= k < -7: return "lent"
    if 0 < k < 56: return "pentecostarion"
    if k == 56: return "all_saints"
    if (fa or "").strip(): return "fore_after_feast"
    if "after Pentecost" not in (desig or ""): return "named_sunday"   # Fathers, Forefathers, Sun before/after Elevation/Nativity/Theophany
    return "ordinary"

# ------------------------------------------------------------------ Vespers key
def month_name(d, long):
    return d.strftime("%B" if long else "%b")

def vesp_text(sat, cache, pages):
    fn = os.path.join(cache, f"{sat}-VESP.txt")
    if os.path.exists(fn): return open(fn).read() or None
    txt = None
    links = [l for l in pages.get(sat, {}).get("links", []) if l.endswith("VESP.pdf")]
    d = dt.date.fromisoformat(sat)
    local = os.path.join(P, "anca-compare/pdfs", f"{d.strftime('%b')} {d.day:02d} {d.year} VESP.pdf")
    data = None
    if os.path.exists(local): data = open(local, "rb").read()
    elif links:
        try: data = urllib.request.urlopen(urllib.request.Request("https://www.antiochian.org" + links[0], headers={"User-Agent": "yocal-spike"}), timeout=60).read()
        except Exception as e: data = None
    if data:
        tmp = fn + ".pdf"; open(tmp, "wb").write(data)
        txt = subprocess.run(["pdftotext", "-layout", tmp, "-"], capture_output=True, text=True).stdout; os.remove(tmp)
    open(fn, "w").write(txt or "")
    return txt

def parse_vesp(t):
    k = {}
    m = re.search(r"O LORD,? I HAVE CRIED.*?\n(.*?)(?=\n\s*[A-Z’' ,.]*THEOTOKION|GLADSOME|\n\s*ENTRANCE)", t, re.S)
    if m:
        sec = m.group(1); cur = None; res = oth = 0
        for ln in sec.splitlines():
            s = ln.strip()
            if re.match(r"^For .*(Tone|tone)", s): cur = "R" if "Resurrection" in s else "O"
            elif re.match(r"^Verse \d+\.", s):
                if cur == "R": res += 1
                else: oth += 1
        glory = bool(re.search(r"^\s*Glory to the Father", sec, re.M))
        k["vespers.lihc"] = dict(res=res, other=oth, glory=glory)
    h = re.search(r"\n\s*([A-Z’' ,.()-]*PROKEIMENON[A-Z’' ,.()-]*)\n", t)
    if h:
        H = h.group(1).strip(); k["vespers.prokeimenon"] = dict(kind="lord_is_king" if "SATURDAY" in H else "other:" + H[:40], tone=None)
    a = re.search(r"\n\s*(APOSTICHA[A-Z’' ,.()-]*)\n", t)
    if a: k["vespers.aposticha"] = dict(kind="resurrectional" if "RESURRECTION" in a.group(1) else "other:" + a.group(1).strip()[:40])
    return k

# ------------------------------------------------------------------ Rules (stubs mirroring decided research)
BASIL_FIXED_SUN = {"01-01", "12-24", "01-05"}   # Jan 1; Nativity/Theophany eve falling on Sunday (#19, Typikon)

def rule_eval(f, vglory):
    """-> {slot: (rule_id, status, source, expected)}. status explicit|inferred|missing. expected None if missing."""
    r = {}
    cls, tone, k = f["cls"], f["tone"], f["k"]
    feastish = cls in ("movable_major_feast", "major_feast_on_sunday", "major_feast_eve_sat")
    # vespers.prokeimenon: Sat eve = "Lord is King" (Typikon p.13; #23). Feast eves not covered.
    r["vespers.prokeimenon"] = ("ves.prok.sat", "explicit", "typikon p.13/#23", dict(kind="lord_is_king")) if not feastish else ("ves.prok.feast", "missing", "", None)
    # vespers.aposticha: Resurrection frame on Sunday eve (Typikon Ch I); feast replaces.
    r["vespers.aposticha"] = ("ves.apost.res", "explicit", "typikon Ch I/III", dict(kind="resurrectional")) if cls in ("ordinary", "named_sunday", "fore_after_feast", "lent", "triodion") else ("ves.apost.other", "missing", "", None)
    # vespers.lihc: split via glory model (#28/#31/#32), ordinary only; Triodion/Lent/Pasch tables (#8) not encoded
    if cls in ("ordinary", "named_sunday") and f["pred"]:   # glory model validated only in-scope (#31/#32); fore/after not validated -> missing
        r["vespers.lihc"] = ("ves.lihc.principal_glory", "inferred" if "inferred" in f["pred_src"] or "alwb" in f["pred_src"] else "explicit", f["pred_src"], dict(split=f["pred"]))
    else:
        r["vespers.lihc"] = ("ves.lihc.none", "missing", "", None)
    # matins.eothinon / prokeimenon tone / kathismata tone from calendar (Typikon Ch I s5; #19 verified)
    ok = tone is not None and not feastish
    r["matins.eothinon"] = ("mat.eothinon", "explicit", "typikon p.29 fn21/#19", dict(n=f["eothinon"])) if ok and f["eothinon"] else ("mat.eothinon.none", "missing", "", None)
    r["matins.prokeimenon"] = ("mat.prok", "explicit", "typikon p.25", dict(tone=tone)) if ok else ("mat.prok.none", "missing", "", None)
    # matins.kontakion (#27): default resurrectional on ordinary Sundays w/o Theotokos/feast override. Only ordinary encoded.
    r["matins.kontakion"] = ("mat.kon.res", "explicit", "typikon pp.27-28/#27", dict(resurrectional=True)) if cls in ("ordinary", "named_sunday") else ("mat.kon.none", "missing", "(#27 rules not encoded)", None)
    # liturgy.rite (#19): Basil on Lent Suns 1-5 (k=-42..-14), Jan 1, Nativity/Theophany eve on Sunday; else Chrysostom.
    if cls == "movable_major_feast" and k in (-7, 49): rite = ("lit.rite", "missing", "", None)
    elif cls == "movable_major_feast": rite = ("lit.rite.pascha", "missing", "Pascha: Chrysostom (not stated in encoded rule)", None)
    else:
        basil = (-42 <= k <= -14 and f["weekday_sun"]) or f["mmdd"] == "01-01"   # Sunday eves of Nativity/Theophany: ANCA = Chrysostom (3/3), removed
        rite = ("lit.rite.basil_list", "explicit", "typikon/#19", dict(rite="basil" if basil else "chrys"))
    r["liturgy.rite"] = rite
    # liturgy.kontakion window (#25): ordinary_theotokos Sep22-Nov7 only encoded
    if cls in ("ordinary", "named_sunday", "fore_after_feast") and "09-22" <= f["mmdd"] <= "11-07":
        r["liturgy.kontakion"] = ("lit.kon.undisputed", "explicit", "typikon pp.35-37/#25", dict(kind="ordinary"))
    else: r["liturgy.kontakion"] = ("lit.kon.other", "missing", "(windows beyond Sep22-Nov7 not encoded)", None)
    # liturgy epistle/gospel refs from calendar lectionary (Typikon p.37 defers to lectionary)
    r["liturgy.epistle"] = ("lit.epistle.cal", "explicit", "typikon p.37/calendar", dict(ref=f["epistle_ref"])) if f["epistle_ref"] else ("lit.epistle.none", "missing", "", None)
    r["liturgy.gospel"] = ("lit.gospel.cal", "explicit", "typikon p.37/calendar", dict(ref=f["gospel_ref"])) if f["gospel_ref"] else ("lit.gospel.none", "missing", "", None)
    return r

# ------------------------------------------------------------------ comparison
def nref(s):
    s = (s or "").replace("–", "-").replace("—", "-").lower()
    s = re.sub(r"\b(romans|corinthians|cor|galatians|ephesians|philippians|colossians|thessalonians|timothy|titus|hebrews|james|peter|john|acts|matthew|mark|luke|jude|philemon|revelation|\d?\s*[a-z]+\.?)\b(?=\s*\d)", "", s)
    return re.sub(r"[\s.]", "", s).replace(";", ",")

def refs(s):
    """list of (chapter:verse) range tokens of the first book-passage only (drops '; Matthew 22:14', ',8:8' tails)"""
    s = re.sub(r"(?:\d\s+)?[A-Za-z]+\.?\s*(?=\d+:)", "", (s or "").split(";")[0].replace("–", "-"))
    first = re.match(r"\s*(\d+):(\d+)\w*\s*-\s*(?:(\d+):)?(\d+)", s)
    return [(first.group(1) + ":" + first.group(2),)] if first else [(s.strip(),)]

def compare(slot, exp, key):
    if key is None: return "not_in_key", ""
    if slot == "vespers.lihc":
        tot = key["res"] + key["other"]
        res, oth = key["res"], key["other"]
        pred = exp["split"]
        obs = f"{res}R+{oth}" if oth else f"{res}R+0"
        # collapse key to coarse split: 6R+4 / 7R+3 / 4R+6 / 4R+3+3 etc: compare R count and total
        m = re.match(r"(\d+)R\+(\d+)", pred); pr = int(m.group(1))
        return ("match", "") if (res == pr) else ("diff", f"rule {pred} / key {res}R+{oth}")
    if slot in ("vespers.prokeimenon", "vespers.aposticha"):
        return ("match", "") if key["kind"] == exp["kind"] else ("diff", f"rule {exp['kind']} / key {key['kind']}")
    if slot in ("liturgy.epistle", "liturgy.gospel"):
        a, b = refs(exp["ref"]), refs(key["ref"])
        if a == b: return "match", ""
        if a and b and a[0] == b[0] and a[-1][1] == b[-1][1] or (a and b and a[0] == b[0]): return "match", "notation: " + f"rule {exp['ref']} / key {key['ref']}"
        return "diff", f"rule {exp['ref']} / key {key['ref']}"
    for a, v in exp.items():
        if key.get(a) != v: return "diff", f"{a}: rule {v} / key {key.get(a)}"
    return "match", ""

def key_for(sk, mk, vk, slot):
    if slot.startswith("vespers"): return vk.get(slot)
    if sk is None: return None
    if slot == "matins.eothinon": return dict(n=pnum(sk["M_eothinon"])) if sk["M_eothinon"] else None
    if slot == "matins.prokeimenon": return dict(tone=pnum(sk["M_prok_tone"])) if sk["M_prok_tone"] else None
    if slot == "matins.kontakion": return dict(resurrectional=(mk["resurrectional"] == "True")) if mk else None
    if slot == "liturgy.rite": return dict(rite=sk["L_rite"]) if sk["L_rite"] else None
    if slot == "liturgy.kontakion":
        h = sk["L_kontakion"].upper()
        return dict(kind="ordinary" if "ORDINARY" in h else "other:" + h[:30]) if h else None
    if slot == "liturgy.epistle": return dict(ref=sk["L_epistle_ref"]) if sk["L_epistle_ref"] else None
    if slot == "liturgy.gospel": return dict(ref=sk["L_gospel_ref"]) if sk["L_gospel_ref"] else None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cache", default="/tmp/yocal-audit-cache"); args = ap.parse_args()
    os.makedirs(args.cache, exist_ok=True)
    sun = {r["date"]: r for r in csv.DictReader(open(os.path.join(P, "anca-compare/sun_keys.csv")))}
    mkon = {r["date"]: r for r in csv.DictReader(open(os.path.join(P, "anca-compare/sun_matins_kontakion.csv")))}
    glory = {r["date"]: r for r in csv.DictReader(open(os.path.join(P, "principal-glory/out.csv")))}
    pages = json.load(open(os.path.join(P, "anca-index/pages.json")))
    db = sqlite3.connect(DB); cols = [c[0] for c in db.execute("select * from yocal_main limit 0").description]
    dates = sorted(sun)
    sats = {d: (dt.date.fromisoformat(d) - dt.timedelta(1)).isoformat() for d in dates}
    with ThreadPoolExecutor(6) as ex: texts = dict(zip(dates, ex.map(lambda d: vesp_text(sats[d], args.cache, pages), dates)))
    rows = []; sc = Counter()
    for d in dates:
        dd = dt.date.fromisoformat(d)
        cal = dict(zip(cols, db.execute("select * from yocal_main where date=?", (d,)).fetchone()))
        cls = ctx_class(dd, cal["fore_after"], cal["desig_a"])
        g = glory.get(d, {})
        pred = g.get("predicted", "") if g.get("season") in ("ordinary", "named-sunday") and cls in ("ordinary", "fore_after_feast") else ""
        def lect(code, i):
            x = db.execute("select lect_1,lect_2 from yocal_lections where code=?", (code,)).fetchone(); return x[i] if x else None
        ep = lect(cal["c_code"], 0) if cal["is_comm_apos"] else lect(cal["a_code"], 0)
        gp = lect(cal["c_code"], 1) if cal["is_comm_gosp"] else lect(cal["g_code"], 1)
        f = dict(cls=cls, tone=pnum(cal["tone"]), eothinon=pnum(cal["eothinon"]), k=(dd - pascha(dd.year)).days, mmdd=d[5:], weekday_sun=True,
                 pred=pred, pred_src=g.get("src", ""), epistle_ref=ep, gospel_ref=gp)
        rules = rule_eval(f, None)
        vk = parse_vesp(texts[d]) if texts[d] else {}
        for slot, (rid, st, src, exp) in rules.items():
            key = key_for(sun[d], mkon.get(d), vk, slot)
            if st == "missing": res, det = ("not_in_key" if key is None else "no_rule"), ""
            else: res, det = compare(slot, exp, key)
            rows.append(dict(date=d, cls=cls, slot=slot, rule=rid, status=st, source=src, result=res, detail=det, key=json.dumps(key) if key else ""))
    with open(os.path.join(HERE, "audit.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("Sundays:", len(dates), " cells:", len(rows), " vespers key present:", sum(1 for d in dates if texts[d]))
    print("class counts:", Counter(r["cls"] for r in rows if r["slot"] == "liturgy.rite"))
    tab = defaultdict(Counter)
    for r in rows: tab[r["slot"]][(r["status"], r["result"])] += 1
    print("\n== slot x (rule status, result)")
    for s in sorted(tab): print(f"{s:22s}", "  ".join(f"{a}/{b}={n}" for (a, b), n in sorted(tab[s].items())))
    tab2 = defaultdict(Counter)
    for r in rows: tab2[r["cls"]][(r["status"] != "missing", r["result"])] += 1
    print("\n== class x (rule encoded?, result)")
    for c in sorted(tab2): print(f"{c:22s}", "  ".join(f"{'rule' if a else 'norule'}/{b}={n}" for (a, b), n in sorted(tab2[c].items())))
    cov = sum(1 for r in rows if r["status"] != "missing" and r["result"] in ("match", "diff")); tot = sum(1 for r in rows if r["result"] != "not_in_key")
    mt = sum(1 for r in rows if r["result"] == "match")
    print(f"\ncoverage (cells with a Rule and a key / cells with a key): {cov}/{tot} = {100*cov/tot:.0f}%; match {mt}/{cov}")
    print("\n== diffs by slot x class")
    dd_ = Counter((r["slot"], r["cls"]) for r in rows if r["result"] == "diff")
    for k, v in sorted(dd_.items()): print(" ", k, v)

if __name__ == "__main__":
    main()
