"""Partial ANCA comparison: Saturday Great Vespers (VESP.pdf) 'Lord I Have Cried' split vs principal-glory prediction.
Reads a snapshot of anca-index/pages.json; downloads only needed PDFs to ../pdfs (untracked); never touches anca-index/."""
import csv, json, re, subprocess, sys, time, datetime, urllib.request, urllib.parse as up
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PROTO = ROOT.parent / "principal-glory/out.csv"
snap = json.loads((ROOT / "pages_snapshot.json").read_text())

def fetch(fn):
    dst = ROOT / "pdfs" / Path(fn).name
    if not dst.exists():
        url = "https://www.antiochian.org" + up.quote(fn)
        req = urllib.request.Request(url, headers={"User-Agent": "yocal-research/1.0"})
        dst.write_bytes(urllib.request.urlopen(req, timeout=60).read()); time.sleep(1.0)
    return dst

def split_of(pdf):
    txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
    m = re.search(r"I HAVE CRIED", txt, re.I)
    e = re.search(r"THE HOLY ENTRANCE|HYMN OF ENTRANCE|GLADSOME LIGHT", txt[m.end():] if m else "", re.I)
    if not m or not e: return None
    sec = txt[m.end(): m.end() + e.start()]
    kind, R, S, dox = None, 0, 0, []
    for line in sec.splitlines():
        if re.match(r"^\w+ \d+, \d{4}\s+Great Vespers", line.strip()): continue
        h = re.match(r"^\s{8,}(\S.*)$", line)
        if h and re.search(r"\bTone\b|DOXASTICON|THEOTOKION", h.group(1), re.I) and not re.match(r"\s*Verse", line):
            t = h.group(1)
            if re.search(r"DOXASTICON", t, re.I): dox.append("R" if re.search(r"RESURRECTION", t, re.I) else "S"); kind = None; continue
            if re.search(r"THEOTOKION", t, re.I): kind = None; continue
            kind = "R" if re.search(r"Resurrection", t) else "S"; continue
        if re.match(r"^\s*Verse \d+\.", line) and kind:
            R += kind == "R"; S += kind == "S"
    return R, S, dox

pred = [r for r in csv.DictReader(open(PROTO, encoding="utf-8")) if r["scope"] == "in"]
RANK = {r["date_key"]: r for r in csv.DictReader(open(ROOT.parent / "bpbasil-rank/ranks.csv"))}
FOUR_SIX = {"06-24", "06-29", "09-26", "10-26", "12-06", "11-08", "01-30", "08-29"}
def bpb(key):  # Bp Basil Chart II: Simple 7+3 (6+4 with two doxastika); Doxology, Polyeleos, Vigil 6+4; 4+6 footnote list
    if key in FOUR_SIX: return "4R+6"
    r = RANK.get(key)
    if not r: return ""
    if r["rank"] == "SIMPLE": return "6R+4" if r["two_glories"] == "1" else "7R+3"
    if r["rank"] in ("DOXOLOGY", "POLYELEOS", "VIGIL"): return "6R+4"
    return ""
rows, tally = [], {"match": 0, "diff": 0, "no_key": 0, "parse_fail": 0, "blank_pred": 0}
for r in pred:
    sat = (datetime.date.fromisoformat(r["date"]) - datetime.timedelta(days=1)).isoformat()
    L = [up.unquote(x) for x in snap.get(sat, {}).get("links", []) if x.lower().endswith(".pdf") and "vesp" in x.lower()]
    L.sort(key=lambda x: (bool(re.search(r"readers|bilingual|\bTR\b", x, re.I)), x))  # prefer plain Great Vespers file
    obs, st = "", ""
    if not L: st = "no_key"
    else:
        try: res = split_of(fetch(L[0]))
        except Exception as ex: res, st = None, "parse_fail"
        if res is None and not st: st = "parse_fail"
        elif res:
            R, S, dox = res; obs = f"{R}R+{S}"
            if not r["predicted"]: st = "blank_pred"
            else: st = "match" if obs == r["predicted"].replace("R+", "R+") else "diff"
    tally[st] += 1
    rows.append(dict(date=r["date"], sat=sat, pred=r["predicted"], bpb=bpb(r["key"]), bpb_rank=(RANK.get(r["key"]) or {}).get("rank", ""), obs=obs, status=st, src=r["src"], principal=r["principal"][:50], note=r["note"], file=(L[0] if L else "")))
with open(ROOT / "compare.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(tally)
