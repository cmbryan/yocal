#!/usr/bin/env python3
"""PROTOTYPE (throwaway): generate per-date Sunday-Vespers LIHC rules from the
research table (#7 findings, Typikon Ch V 'Sunday Vespers split' column)."""
import re, sys, yaml, subprocess
md = subprocess.check_output(["git","show","origin/research/typikon-menaia-structure:research/typikon-menaia-structure.md"],text=True)
tab = md.split("### 3a. Table")[1].split("### 3b.")[0]
MON = {m:i for i,m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(),1)}
rules, skipped = [], []
for line in tab.splitlines():
    c = [x.strip() for x in line.strip().strip("|").split("|")]
    if len(c) < 6 or not re.match(r"[A-Z][a-z]{2} \d", c[0]): continue
    date, commem, page, split = c[0], c[1], c[2], c[5]
    m = re.match(r"([A-Z][a-z]{2}) (\d+)$", date)
    if not m or ";" in split or not re.match(r"\d+R\+\d", split):
        skipped.append(f"{date}: {split}"); continue
    mmdd = f"{MON[m.group(1)]:02d}-{int(m.group(2)):02d}"
    nums = [int(x) for x in re.findall(r"(?<![\d(+])\+?(\d+)(?!R)", split.replace("(+1 repeat)",""))]
    res = int(re.match(r"(\d+)R", split).group(1))
    rest = [int(x) for x in re.findall(r"\+(\d+)", split.replace("(+1 repeat)",""))]
    pg = re.match(r"(\d+)", page).group(1)
    rules.append(dict(id=f"ves.lihc.ch5.{mmdd}", slot="vespers.lihc.stichera", tier=1,
        when=[dict(pred="sunday_eve"), dict(pred="menaion_date_is", args=[mmdd])],
        fill=dict(res=res, other=rest),
        source="typikon", locator=f"Ch V {date}, p.{pg}", status="explicit"))
yaml.safe_dump(rules, open("rules/vespers_lihc_ch5.yaml","w"), sort_keys=False)
print(len(rules), "rules;", len(skipped), "skipped", file=sys.stderr)
print("\n".join(skipped), file=sys.stderr)
