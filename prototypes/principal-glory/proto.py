"""Dry run (ALWB side only): Principal commemoration -> principal_glory -> predicted 6R+4 / 7R+3 for each Sunday.
Order: (1) override [none yet] -> (2) non-blank yocal major_commem matched to an ALWB block -> (3) ALWB main (inferred) -> (4) missing.
No ANCA comparison here (blocked on #29)."""
import csv, re, sqlite3, unicodedata, collections, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "db/yocal/YOCal_Master.db"
ALWB = ROOT / "prototypes/alwb-menaion/menaion_commems.csv"
Y0, Y1 = int(sys.argv[1]) if len(sys.argv) > 1 else 2019, int(sys.argv[2]) if len(sys.argv) > 2 else 2026

STOP = set("""saint saints st holy martyr martyrs hieromartyr hieromartyrs great venerable our father fathers among the of and in at on to with for from his her their
devout god bearing mother righteous apostle apostles prophet equal equal-to-the-apostles bishop archbishop patriarch metropolitan pope wonderworker wonderworkers
unmercenaries unmercenary confessor confessors new blessed repose translation relics synaxis commemoration memory finding icon city monk monks abbot abbess
ascetic ascetics those them him fool christ sake martyrdom of-the church mount holy-mountain athos elder younger first second third""".split())

SYN = [("theophany", "epiphany"), ("godbearer", "godbearing"), ("wonder worker", "wonderworker"), ("leave taking", "leavetaking"),
       ("translation", "transfer"), ("placing", "placement"), ("eleutherius", "eleftherios"), ("hilarion", "hilary")]

def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\([^)]*\)", " ", s)
    s = s.replace("-", " ")
    for a, b in SYN: s = s.replace(a, b)
    s = re.sub(r"god bear", "godbear", s)
    s = re.sub(r"(?<![a-z])eu", "ef", s).replace("th", "t").replace("ph", "f").replace("ks", "x")
    toks = re.findall(r"[a-z]+", s)
    return {t[:5] for t in toks if t not in STOP and t[:5] not in STOP and len(t) > 2}

alwb = collections.defaultdict(list)
for r in csv.DictReader(open(ALWB, encoding="utf-8")):
    alwb[r["date_key"]].append(r)

def match(major, blocks):
    mt = norm(major)
    best = []
    for b in blocks:
        bt = norm(b["name"])
        if not bt or not mt: continue
        inter = len(bt & mt)
        score = inter / min(len(bt), len(mt))  # containment: shorter name must be >= half covered
        if inter >= 1 and score >= 0.5: best.append((score, b))
    if not best: return None, "no-match"
    best.sort(key=lambda x: -x[0])
    top = [b for s, b in best if s == best[0][0]]
    if len(top) > 1 and len({t["has_vespers_glory"] for t in top}) > 1: return None, "ambiguous"
    return top[0], "ok"

# EXPLICIT 4R+6 (Antiochian Typikon): p.12 list (Archangels, Nativity of the Baptist, Peter & Paul, John the Evangelist, Three Hierarchs [not on a Triodion Sunday],
# Demetrius, Nicholas) + Ch.V Aug 29 (p.464, Beheading on Sunday). Fathers of 4th/7th Councils (p.12) are calendar windows, out of scope here (named-sunday).
# "Archangels" -> Nov 8 only (ANCA 2020-09-06 Archangel Michael at Colossae was 6R+4). Verified by hand; Ch.V extractor in ../typikon-ch5 is unreliable, not used.
FOUR_R_SIX = {"06-24": "Typikon p.12", "06-29": "Typikon p.12", "09-26": "Typikon p.12", "10-26": "Typikon p.12", "12-06": "Typikon p.12",
              "11-08": "Typikon p.12 (Archangels)", "01-30": "Typikon p.12 (Three Hierarchs)", "08-29": "Typikon Ch.V p.464"}

def pascha(y):  # Orthodox Pascha, Gregorian date (Julian computus + 13d, valid 1900-2099)
    import datetime
    a, b, c = y % 4, y % 7, y % 19
    d = (19 * c + 15) % 30
    e = (2 * a + 4 * b - d + 34) % 7
    m, dd = divmod(d + e + 114, 31)
    return datetime.date(y, m, dd + 1) + datetime.timedelta(days=13)
import datetime
LORD = {"01-01", "01-06", "02-02", "03-25", "08-06", "08-15", "09-08", "09-14", "11-21", "12-25"}  # fixed Major feasts (+Theotokos)

def season(date):
    d = datetime.date.fromisoformat(date); P = pascha(d.year); k = (d - P).days
    if -70 <= k < -48: return "triodion"
    if -48 <= k < 0: return "lent"
    if k == 0: return "pascha"
    if 0 < k <= 49: return "pentecostarion"
    return "ordinary"

con = sqlite3.connect(DB)
rows = con.execute("""select date, tone, fast, major_commem, c_code, fore_after from yocal_main
  where day_name='Sunday' and cast(substr(date,1,4) as int) between ? and ? order by date""", (Y0, Y1)).fetchall()
out, stats = [], collections.Counter()
for date, tone, fast, major, ckey, fa in rows:
    key = ckey if ckey and re.fullmatch(r"\d\d-\d\d", ckey) else date[5:]
    blocks = alwb.get(key, [])
    main = next((b for b in blocks if b["role"] == "main"), None)
    major = (major or "").strip()
    src = principal = ""; glory = ""; note = ""
    if not blocks:
        src, note = "missing", "no-alwb-day"
    elif major:
        m, why = match(major, blocks)
        if m:
            src, principal, glory = "major_commem->alwb:" + m["role"], m["name"], m["has_vespers_glory"]
            if main and m is not main and m["has_vespers_glory"] != main["has_vespers_glory"]: note = "differs-from-alwb-main"
        else:
            src, note = "unmatched", why  # Q4: blank, listed for review
    elif main:
        src, principal, glory = "alwb-main(inferred)", main["name"], main["has_vespers_glory"]
        if any(b["role"] != "main" and b["has_vespers_glory"] != glory for b in blocks): note = "alt-glory-differs"
    else:
        src = "missing"
    ssn = season(date); feast = "feast" if key in LORD else ""
    dd = datetime.date.fromisoformat(date); md = (dd.month, dd.day); P = pascha(dd.year)
    named = ((dd - P).days == 56 or (7, 13) <= md <= (7, 19) or (10, 11) <= md <= (10, 17) or (12, 11) <= md <= (12, 24)
             or (12, 26) <= md or md <= (1, 13) or (9, 11) <= md <= (9, 13) or (9, 15) <= md <= (9, 21))  # INFERRED calendar windows of Sundays with their own commemorations
    if named and ssn == "ordinary" and not feast: ssn = "named-sunday"
    scope = "in" if (ssn == "ordinary" and not feast and not (fa or "").strip()) else ("fore/after" if ssn == "ordinary" and not feast else (feast or ssn))
    pred = {"1": "6R+4", "0": "7R+3"}.get(glory, "")
    if key in FOUR_R_SIX and ssn != "triodion":
        pred = "4R+6"; src = "explicit:" + FOUR_R_SIX[key]  # explicit rule beats glory flag
    stats[src.split(":")[0]] += 1; stats["scope:" + scope] += 1
    if scope == "in": stats["in-scope " + src.split(":")[0]] += 1
    if note: stats["note:" + note] += 1
    out.append(dict(date=date, key=key, tone=tone, fast=fast, season=ssn, scope=scope, major_commem=major, principal=principal, src=src, glory=glory, predicted=pred, note=note))

with open(Path(__file__).parent / "out.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print("Sundays", len(out), Y0, Y1)
for k, v in sorted(stats.items()): print(f"  {k}: {v}")
print("predicted:", collections.Counter(r["predicted"] or "blank" for r in out))
