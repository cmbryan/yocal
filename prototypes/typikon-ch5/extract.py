"""Extract per-date Sunday Great Vespers 'Lord I have cried' stichera counts from Typikon Ch.V (pdftotext -layout text, passed as argv[1]).
Output CSV: date_key, page, orders (e.g. '4R+6'); counts only, paraphrase-free. Source: Antiochian Typikon 2011, Ch.V."""
import re, sys, csv
from pathlib import Path
MON = "JANUARY FEBRUARY MARCH APRIL MAY JUNE JULY AUGUST SEPTEMBER OCTOBER NOVEMBER DECEMBER".split()
lines = open(sys.argv[1], encoding="utf-8").read().splitlines()
hdr = re.compile(r"^\s+(%s) (\d{1,2})\s*$" % "|".join(MON))
page = re.compile(r"Back to Table of Contents\s+(\d+)")
heads = [(i, f"{MON.index(m.group(1))+1:02d}-{int(m.group(2)):02d}") for i, l in enumerate(lines) if (m := hdr.match(l))]
out = []
for n, (i, key) in enumerate(heads):
    j = heads[n+1][0] if n+1 < len(heads) else len(lines)
    sec = lines[i:j]
    pg = next((int(m.group(1)) for l in sec for m in [page.search(l)] if m), "")
    # find Sunday-specific block(s): any 'O Lord, I have cried' ... 'we chant N stichera' followed by 'k for ...' lines
    orders = []
    for k, l in enumerate(sec):
        if re.search(r"O Lord,? I have cried", l, re.I) and re.search(r"we chant,? (\d+) stichera", l):
            tot = int(re.search(r"we chant,? (\d+) stichera", l).group(1)); parts = []
            for l2 in sec[k+1:k+8]:
                m2 = re.match(r"^\s*(\d+) (?:for|from|of)\b(.*)", l2)
                if m2: parts.append((int(m2.group(1)), "R" if re.search(r"Resurrection", m2.group(2)) else "S"))
                elif l2.strip() == "" and parts: break
                elif parts and not re.match(r"^\s*(\d+|“Glory)", l2): break
            if parts: orders.append("+".join(f"{n_}{t}" for n_, t in parts))
    # context: does the section talk about a Sunday?
    sun = any(re.search(r"falls on (a )?Sunday|If .* Sunday", l) for l in sec)
    if orders: out.append((key, pg, "|".join(dict.fromkeys(orders)), "sunday-text" if sun else ""))
with open(Path(__file__).parent / "ch5_vespers.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["date_key", "page", "orders", "sunday"]); w.writerows(out)
print(len(heads), "date headings;", len(out), "with stichera orders")
