#!/usr/bin/env python3
"""PROTOTYPE (throwaway, wipe me): rule-schema + harness spike.

Question: does the YAML Rule schema (slot-grain Rules, tiers, closed context
facts, provenance) + ANCA comparison harness hold up on real data?

Slice: ordinary Sundays (Sat Great Vespers, Sun Matins, Sun Liturgy), no
Triodion/Pentecostarion/Major feasts.

  python spike.py --from 2024-07-07 --to 2026-11-22 [--cache DIR] [--detail DATE]

ANCA PDFs are downloaded into --cache (scratch, never committed).
"""
import argparse, datetime as dt, glob, os, re, sqlite3, subprocess, sys, urllib.request, urllib.error
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "../../db/yocal/YOCal_Master.db")
WORDS = {w: i for i, w in enumerate("ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE TEN ELEVEN".split())}

# ------------------------------------------------------------------ rules
def load_rules():
    rules, errs = [], []
    for f in sorted(glob.glob(os.path.join(HERE, "rules/*.yaml"))):
        if f.endswith(("sources.yaml", "slots.yaml")):
            continue
        rules += yaml.safe_load(open(f))
    src = yaml.safe_load(open(os.path.join(HERE, "rules/sources.yaml")))
    slots = yaml.safe_load(open(os.path.join(HERE, "rules/slots.yaml")))
    ids = set()
    for r in rules:
        if r["id"] in ids: errs.append(f"dup id {r['id']}")
        ids.add(r["id"])
        if r["source"] not in src: errs.append(f"{r['id']}: unknown source")
        if r["slot"] not in slots: errs.append(f"{r['id']}: unknown slot")
        st = r["status"]
        if st == "explicit" and "evidence" in r: errs.append(f"{r['id']}: explicit with evidence")
        if st == "inferred" and "evidence" not in r: errs.append(f"{r['id']}: inferred w/o evidence")
        if st == "missing" and "ticket" not in r: errs.append(f"{r['id']}: missing w/o ticket")
    return rules, errs

# ------------------------------------------------------------------ calendar adapter (closed fact vocabulary)
def pnum(s):
    m = re.search(r"\d+", s or "")
    return int(m.group()) if m else None

def facts_for(db, date):
    d = dt.date.fromisoformat(date)
    r = db.execute("select * from yocal_main where date=?", (date,)).fetchone()
    cols = [c[0] for c in db.execute("select * from yocal_main limit 0").description]
    r = dict(zip(cols, r))
    def lect(code):
        x = db.execute("select lect_1,lect_2 from yocal_lections where code=?", (code,)).fetchone()
        return x or (None, None)
    if r["is_comm_apos"]: ep = lect(r["c_code"])[0]
    else: ep = lect(r["a_code"])[0]
    gp = lect(r["c_code"])[1] if r["is_comm_gosp"] else lect(r["g_code"])[1]
    return dict(
        date=date, mmdd=d.strftime("%m-%d"), weekday=d.strftime("%A"), year=d.year,
        tone=pnum(r["tone"]), eothinon=pnum(r["eothinon"]),
        epistle_owner="saint" if r["is_comm_apos"] else "sunday", gospel_owner="saint" if r["is_comm_gosp"] else "sunday",
        epistle_ref=ep, gospel_ref=gp,
        saint_in_calendar=bool((r["major_commem"] or "").strip()),
        desig=r["desig_a"],
    )

PREDS = {
    "sunday": lambda f, a: f["weekday"] == "Sunday",
    "sunday_eve": lambda f, a: f["weekday"] == "Sunday",     # liturgical-day unit: eve belongs to Sunday
    "menaion_date_is": lambda f, a: f["mmdd"] == a[0],
    "date_between": lambda f, a: a[0] <= f["mmdd"] <= a[1],
    "not_date_between": lambda f, a: not (a[0] <= f["mmdd"] <= a[1]),
    "saint_in_calendar": lambda f, a: f["saint_in_calendar"],
    "no_saint_in_calendar": lambda f, a: not f["saint_in_calendar"],
}

def resolve(fill, f):
    out = {}
    for k, v in fill.items():
        out[k] = f[v[1:]] if isinstance(v, str) and v.startswith("$") else v
    return out

def evaluate(rules, f):
    """-> {slot: (winner_rule, output) | ('ERROR', msg)}; lowest tier number wins; tie = build error."""
    by = defaultdict(list)
    for r in rules:
        if all(PREDS[w["pred"]](f, w.get("args", [])) for w in r["when"]):
            by[r["slot"]].append(r)
    res = {}
    for slot, rs in by.items():
        best = min(r["tier"] for r in rs)
        top = [r for r in rs if r["tier"] == best]
        if len(top) > 1:
            res[slot] = ("ERROR", "tie: " + ",".join(r["id"] for r in top))
        else:
            res[slot] = (top[0], resolve(top[0]["fill"], f))
    return res

# ------------------------------------------------------------------ ANCA fetch + parse
def month_variants(d):
    m = d.strftime("%b")
    v = [m]
    if m == "Sep": v.append("Sept")
    if m in ("Jun", "Jul", "Mar", "Apr"): v.insert(0, d.strftime("%B"))
    return v

def fetch(date, kind, cache):
    d = dt.date.fromisoformat(date)
    fn = os.path.join(cache, f"{date}-{kind}.txt")
    if os.path.exists(fn): return open(fn).read() or None
    if kind == "VESP": d_file = d - dt.timedelta(days=1)   # Saturday eve file is keyed by Saturday
    else: d_file = d
    txt = None
    for mv in month_variants(d_file):
        name = f"{mv} {d_file.day:02d} {d_file.year} {kind}.pdf"
        url = "https://www.antiochian.org/servicetexts/" + urllib.request.quote(name)
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "yocal-spike"}), timeout=30).read()
        except urllib.error.HTTPError:
            continue
        p = fn + ".pdf"
        open(p, "wb").write(data)
        txt = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True).stdout
        os.remove(p)
        break
    open(fn, "w").write(txt or "")
    return txt

def tone_of(s):
    m = re.search(r"TONE\s+(\w+)", s, re.I)
    if not m: return None
    w = m.group(1).upper()
    return WORDS.get(w) or (int(w) if w.isdigit() else None)

def blocks_with_verses(span):
    """split a rubric span into blocks by 'For ... in Tone' headings; count 'Verse N.' lines per block."""
    out, cur = [], None
    for ln in span.splitlines():
        s = ln.strip()
        if re.match(r"^For .*(Tone|tone)", s) and not s.startswith("Verse"):
            cur = [s, 0]; out.append(cur)
        elif re.match(r"^Verse \d+\.", s) and cur is not None:
            cur[1] += 1
    return out

def span_between(txt, start_re, end_re):
    m = re.search(start_re, txt)
    if not m: return ""
    rest = txt[m.start():]
    e = re.search(end_re, rest[10:])
    return rest[: e.start() + 10] if e else rest

def parse_abbr(txt):
    k = {}
    ves, _, mat = txt.partition("Orthros on Sunday")
    if not mat:
        ves, mat = txt, ""
    # vespers LIHC
    sp = span_between(ves, r"3\.\)\s+We chant .O Lord, I Have Cried", r"\n\s*4\.\)")
    n = re.search(r"with (\w+) (?:stichera|troparia)", sp)
    bl = blocks_with_verses(sp)
    if n:
        res = sum(c for h, c in bl if "Resurrection" in h)
        oth = [c for h, c in bl if "Resurrection" not in h and c]
        k["vespers.lihc.stichera"] = dict(res=res, other=oth, total=WORDS.get(n.group(1).upper()))
    pk = re.search(r"[Pp]rokeimenon\s+[“\"]([^”\"]+)[”\"]\s+in Tone (\d)", ves)
    if pk:
        k["vespers.prokeimenon"] = dict(kind="lord_is_king" if "Lord is King" in pk.group(1) else pk.group(1)[:30], tone=int(pk.group(2)))
    # matins
    m = re.search(r"(?:[Kk]athismata hymns|Poetic Kathismata) are from the Octoechos for Tone (\d)", mat)
    if m: k["matins.kathismata"] = dict(tone=int(m.group(1)))
    m = re.search(r"\n\s*([A-Z ,.’'()-]*PROKEIMENON[A-Z ]*IN TONE \w+)", mat)
    if m:
        h = m.group(1)
        k["matins.prokeimenon"] = dict(kind="resurrectional" if "RESURRECTIONAL" in h else "other", tone=tone_of(h))
    m = re.search(r"The (\w+) Eothinon Gospel", mat, re.I)
    if m:
        w = m.group(1).upper(); k["matins.eothinon_gospel"] = dict(number=WORDS.get(w) or None)
    sp = span_between(mat, r"We chant .The Praises", r"\n\s*22\.\)")
    n = re.search(r"with (\w+) (?:stichera|troparia)", sp)
    if n:
        bl = blocks_with_verses(sp)
        # praises: stichera not 'Verse'-labelled consistently; count Res vs other via headings
        k["matins.praises"] = dict(total=WORDS.get(n.group(1).upper()), res=None)
    return k

def parse_read(txt):
    k = {}
    heads = re.findall(r"^\s*([A-Z][A-Z .,’'()*-]{10,}IN TONE \w+)", txt, re.M)
    m = re.search(r"ORDINARY KONTAKION IN TONE (\w+)|RESURRECTIONAL KONTAKION IN TONE (\w+)|KONTAKION[A-Z ,.’'-]* IN TONE (\w+)", txt)
    if m:
        kind = "ordinary_theotokos" if "ORDINARY" in m.group(0) else ("resurrectional" if "RESURRECTIONAL" in m.group(0) else "other:" + m.group(0)[:30])
        k["liturgy.kontakion"] = dict(kind=kind, tone=WORDS.get(next(g for g in m.groups() if g).upper()))
    ep = re.search(r"THE EPISTLE\s*\n\s*\(For ([^)]+)\)", txt)
    own = None   # key marks owner only via a '(For ...)' subtitle; absent => unknown (apostle feasts print none)
    if ep: own = "sunday" if re.search(r"Sunday|Week", ep.group(1)) else "saint"
    k["liturgy.epistle"] = dict(owner=own)
    m = re.search(r"Epistle[^\n]*\((\d+:\d+[-–\d:,; ]*)\)", txt)
    if m: k["liturgy.epistle"]["ref"] = m.group(1)
    m = re.search(r"THE GOSPEL[^\n]*\n(?:[^\n]*\n){0,3}?[^\n]*\((\d+:\d+[-–\d:,; ]*)\)", txt)
    m2 = re.search(r"Holy Gospel according to St\.? \w+\.?\s*\((\d+:\d+[-–\d:,; ]*)\)", txt)
    if m2: k["liturgy.gospel"] = dict(ref=m2.group(1).strip())
    k["liturgy.prokeimenon"] = dict(owner=k["liturgy.epistle"]["owner"])   # circular: see report
    return k

# ------------------------------------------------------------------ compare
def norm_ref(s):
    return re.sub(r"\s+", "", (s or "").replace("–", "-")).lower()

def compare(slot, exp, key):
    """-> (state, details). state in match | diff | not_in_key"""
    if key is None: return "not_in_key", ""
    diffs = []
    for a, v in exp.items():
        if v in ("?", None): continue
        kv = key.get(a)
        if kv is None: continue
        if slot in ("liturgy.gospel", "liturgy.epistle") and a == "ref":
            if norm_ref(v.split(" ",1)[-1].split()[-1]) != norm_ref(kv): diffs.append(f"{a}: rule {v} / key {kv}")
        elif slot == "liturgy.gospel":
            if norm_ref(v.split(" ",1)[-1].split()[-1]) != norm_ref(kv): diffs.append(f"{a}: rule {v} / key {kv}")
        elif a == "other":
            if sum(v) != sum(kv): diffs.append(f"{a}: rule {v} / key {kv}")
        elif v != kv:
            diffs.append(f"{a}: rule {v} / key {kv}")
    return ("diff", "; ".join(diffs)) if diffs else ("match", "")

# ------------------------------------------------------------------ main
def sundays(a, b):
    d = dt.date.fromisoformat(a)
    d += dt.timedelta(days=(6 - d.weekday()) % 7)
    while d <= dt.date.fromisoformat(b):
        yield d.isoformat(); d += dt.timedelta(days=7)

IN_SLICE = [("07-01", "08-04"), ("09-22", "11-19"), ("11-26", "12-10")]   # coarse: no Major feast windows / Triodion / Pentecostarion
def in_slice(mmdd): return any(a <= mmdd <= b for a, b in IN_SLICE)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="a", default="2024-07-07"); ap.add_argument("--to", dest="b", default="2026-11-22")
    ap.add_argument("--cache", default="/tmp/yocal-spike-cache"); ap.add_argument("--detail")
    args = ap.parse_args(); os.makedirs(args.cache, exist_ok=True)
    rules, errs = load_rules()
    print(f"rules loaded: {len(rules)}; schema errors: {len(errs)}"); [print("  ERR", e) for e in errs]
    db = sqlite3.connect(DB)
    dates = [d for d in sundays(args.a, args.b) if in_slice(d[5:])]
    # pascha-relative exclusion: Sundays before Pentecost+1 are not in the 'post-Pentecost' slice
    dates = [d for d in dates if "after Pentecost" in (facts_for(db, d)["desig"] or "")]
    print(f"slice Sundays: {len(dates)}")
    with ThreadPoolExecutor(6) as ex:
        keys = dict(zip(dates, ex.map(lambda d: (fetch(d, "Abbr", args.cache), fetch(d, "READ", args.cache)), dates)))
    cell = Counter(); diffs = []; ties = []; nokey = []; grid = defaultdict(Counter)
    for d in dates:
        f = facts_for(db, d); out = evaluate(rules, f)
        ab, rd = keys[d]
        if not ab or not rd: nokey.append(d); continue
        key = {**parse_abbr(ab), **parse_read(rd)}
        for slot, v in out.items():
            if v[0] == "ERROR": ties.append((d, slot, v[1])); continue
            r, exp = v
            st, det = compare(slot, exp, key.get(slot)) if r["status"] != "missing" else ("n/a", "")
            if st == "diff": diffs.append((d, slot, r["id"], r["status"], det))
            cell[(slot, r["status"], st)] += 1
            grid[slot][(r["status"], st)] += 1
    print(f"dates with ANCA key (Abbr+READ): {len(dates)-len(nokey)}; no key: {len(nokey)} {nokey[:6]}")
    print(f"\n== coverage grid: slot x (rule status, vs ANCA) ==")
    for slot in sorted(grid):
        print(f"{slot:28s} " + "  ".join(f"{s}/{c}={n}" for (s, c), n in sorted(grid[slot].items())))
    print(f"\n== tier ties (build errors): {len(ties)}"); [print(" ", t) for t in ties[:5]]
    print(f"\n== UNEXPLAINED DIFFS: {len(diffs)}")
    for x in diffs[:40]: print(" ", *x)
    if args.detail:
        f = facts_for(db, args.detail); print("\n", f)
        for slot, v in evaluate(rules, f).items(): print(slot, v if v[0] == "ERROR" else (v[0]["id"], v[0]["status"], v[1]))

if __name__ == "__main__":
    main()
