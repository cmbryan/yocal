"""Emit CSV: date_key, role, lauds_count, lauds_glory, lauds_now from ALWB (Greek) Menaion day files. Counts/flags only, no text.
Usage: python3 -I extract_lauds.py <cog_menaion_dir> > ../../yocal_rules/data/alwb_lauds.csv
lauds_count = non-empty meMA.Lauds<N>.text; lauds_glory = non-empty meMA.LaudsGlory.text. Greek data is partial (most days empty)."""
import re,sys,csv
from pathlib import Path
LINE=re.compile(r'^((?:alt\d+\.)?)(\S+)\s*=\s*"(.*?)"\s*(?://.*)?$')
root=Path(sys.argv[1])
w=csv.writer(sys.stdout); w.writerow(['date_key','role','lauds_count','lauds_glory','lauds_now'])
for p in sorted(root.glob('m*/me.m*.ares')):
    m=re.match(r'me\.m(\d\d)\.d(\w\w)_',p.name); key=f'{m.group(1)}-{m.group(2)}'
    d={}
    for ln in p.read_text(encoding='utf-8').splitlines():
        x=LINE.match(ln)
        if x: d[(x.group(1).rstrip('.') or 'main',x.group(2))]=x.group(3).strip()
    for r in sorted({r for r,_ in d},key=lambda r:(r!='main',r)):
        n=sum(1 for (rr,k),v in d.items() if rr==r and re.fullmatch(r'meMA\.Lauds\d+\.text',k) and v)
        g=int(bool(d.get((r,'meMA.LaudsGlory.text'))))
        nw=int(bool(d.get((r,'meMA.LaudsTheotokion.text')) or d.get((r,'meMA.LaudsNow.text'))))
        w.writerow([key,r,n,g,nw])
