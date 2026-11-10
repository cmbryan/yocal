"""Parse Bp Basil 'Rankings of Feasts and Commemorations According to the Menaion' (local text) -> per-date rank + two-glories flag.
Source: Bp Basil (Essey), Parish Typikon, Ranking of Feasts (dowama.org). Local copy untracked. Output keeps rank labels/flags only (no verbatim descriptions)."""
import re, csv, sys
from pathlib import Path
SRC = Path(__file__).resolve().parents[2] / "BpBasil/Ranking_of_Feasts_according_to_the_Typikon.txt"
MON = "January February March April May June July August September October November December".split()
mon = None; rows = []; last = None; phy = False
for line in SRC.read_text().splitlines():
    s = re.sub(r"\[[^\]]*\]", "", line).strip()  # drop footnote markers like April[iii]
    if s in MON: mon = MON.index(s) + 1; phy = False; continue
    if s.lower().startswith("phyllada"): phy = True; continue  # optional local vigils, not the base rank
    if phy: continue
    m = re.match(r"^(\d{1,2})\.\s+(.*)", s)
    if m and mon:
        day, rest = int(m.group(1)), m.group(2)
        last = [f"{mon:02d}-{day:02d}", rest]; rows.append(last); continue
    if s and last and mon:  # continuation / 'or' alternative lines
        last[1] += " | " + s
out = []
for key, txt in rows:
    t = txt.upper()
    if t.startswith("PHYLLADA") : continue
    rank = next((r for r in ["POLYELEOS", "VIGIL", "DOXOLOGY", "SIMPLE", "LEAVETAKING", "FEAST OF THE MASTER", "FEAST OF THE MOTHER OF GOD", "FEAST OF THE", "FOREFEAST", "AFTERFEAST", "PREFEAST", "POSTFEAST"] if t.startswith(r) or (" | " + r) in t), "OTHER")
    two_glories = "2 GLORIES" in t
    out.append(dict(date_key=key, rank=rank, two_glories=int(two_glories), has_or=int("|" in txt), count=(re.search(r"=\s*(\d+) STICHERA", t) or [None, ""])[1], raw_len=len(txt)))
with open(Path(__file__).parent / "ranks.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
import collections
print(len(out), "dates;", collections.Counter(r["rank"] for r in out))
