"""Derive per-date flags from Bp Basil's 'Ranking of Feasts according to the Typikon' (local, untracked text).

Output data/bpbasil_flags.csv keeps flags only (no descriptions):
  rank, implies_glory (Doxology/Polyeleos/Vigil rank or '2 Glories'), two_sets_of_3 ('A 3 + B 3 = 6 stichera').
Bp Basil is positive-only evidence for glory (never vetoes it), per #31/#34.
Usage: python -I -m yocal_rules.tools.build_bpbasil_flags BpBasil/Ranking_of_Feasts_according_to_the_Typikon.txt
"""
import csv
import os
import re
import sys

MON = "January February March April May June July August September October November December".split()
RANKS = ["POLYELEOS", "VIGIL", "DOXOLOGY", "SIMPLE", "LEAVETAKING", "FEAST OF THE MASTER", "FEAST OF THE MOTHER OF GOD"]


def parse(path):
    mon, last, phy, rows = None, None, False, []
    for line in open(path, encoding="utf-8").read().splitlines():
        s = re.sub(r"\[[^\]]*\]", "", line).strip()
        if s in MON:
            mon, phy = MON.index(s) + 1, False
            continue
        if s.lower().startswith("phyllada"):
            phy = True
            continue
        if phy:
            continue
        m = re.match(r"^(\d{1,2})\.\s+(.*)", s)
        if m and mon:
            last = [f"{mon:02d}-{int(m.group(1)):02d}", m.group(2)]
            rows.append(last)
        elif s and last and mon:
            last[1] += " | " + s
    out = []
    for key, txt in rows:
        t = txt.upper()
        rank = next((r for r in RANKS if t.startswith(r) or (" | " + r) in t), "OTHER")
        two_glories = "2 GLORIES" in t
        two_sets = bool(re.search(r"\b3 \+ [A-Z ]*?3 = 6 STICHERA", t))
        out.append(dict(date_key=key, rank=rank, implies_glory=int(rank in ("POLYELEOS", "VIGIL", "DOXOLOGY") or two_glories),
                        two_sets_of_3=int(two_sets)))
    return out


if __name__ == "__main__":
    rows = parse(sys.argv[1])
    dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "bpbasil_flags.csv")
    with open(dest, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "dates;", sum(r["implies_glory"] for r in rows), "imply glory;", sum(r["two_sets_of_3"] for r in rows), "two sets of 3")
