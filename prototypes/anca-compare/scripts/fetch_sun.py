"""Fetch plain ORTHROS.pdf + READ.pdf for every Sunday in anca-index (untracked, ../pdfs_sun). Polite: 3 workers, 0.5s sleep."""
import json, re, time, datetime, urllib.request, urllib.parse as up
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pdfs_sun"; OUT.mkdir(exist_ok=True)
snap = json.loads((ROOT / "pages_snapshot_full.json").read_text())
def pick(links, kind):
    L = [up.unquote(x) for x in links if x.lower().endswith(".pdf") and re.search(rf"{kind}\.pdf$", x, re.I)]
    L = [x for x in L if not re.search(r"bilingual|readers|\bTR\b|abbr", x, re.I)]
    L.sort(key=lambda x: (bool(re.search(r"FINAL", x)), x))
    return L[0] if L else None
jobs = []
for d, v in snap.items():
    if datetime.date.fromisoformat(d).weekday() != 6: continue
    for kind in ("ORTHROS", "READ"):
        fn = pick(v["links"], kind)
        if fn: jobs.append((d, kind, fn))
def go(j):
    d, kind, fn = j; dst = OUT / f"{d}-{kind}.pdf"
    if dst.exists(): return "skip"
    try:
        req = urllib.request.Request("https://www.antiochian.org" + up.quote(fn), headers={"User-Agent": "yocal-research/1.0"})
        dst.write_bytes(urllib.request.urlopen(req, timeout=60).read()); time.sleep(0.5); return "ok"
    except Exception as e: return f"fail {d} {kind} {fn} {e}"
with ThreadPoolExecutor(3) as ex:
    res = list(ex.map(go, jobs))
print(len(jobs), [r for r in res if r.startswith("fail")][:20], sum(r == "ok" for r in res))
