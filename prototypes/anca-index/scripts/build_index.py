"""pages.json -> index.csv/index.json (date,service,filename,url,http_status). HEAD-checks PDFs (throttled, cached in headcache.json).
Dates: Saturdays (eve) and Sundays in range. Kind from filename suffix."""
import csv, json, re, sys, time, urllib.request
from pathlib import Path
from urllib.parse import unquote
ROOT = Path(__file__).resolve().parent.parent
pages = json.loads((ROOT / "pages.json").read_text())
cache_f = ROOT / "headcache.json"
cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}

def kind(fn):
    f = fn.lower()
    bil = "bilingual" in f
    if re.search(r"vesp", f): k = "VESP"
    elif re.search(r"orthros|matins", f): k = "ORTHROS"
    elif re.search(r"abbr", f): k = "ABBR"
    elif re.search(r"read|variables|liturgy", f): k = "READ"
    else: k = "OTHER"
    return ("BIL-" if bil else "") + k

def head(url):
    if url in cache: return cache[url]
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "yocal-research/1.0"})
    try: s = urllib.request.urlopen(req, timeout=30).status
    except urllib.error.HTTPError as e: s = e.code
    except Exception as e: s = f"ERR:{type(e).__name__}"
    cache[url] = s; time.sleep(0.4)
    if len(cache) % 50 == 0: cache_f.write_text(json.dumps(cache))
    return s

rows = []
for d, v in sorted(pages.items()):
    seen = set()
    for u in v["links"]:
        if not u.lower().endswith(".pdf"): continue
        fn = unquote(u.rsplit("/", 1)[1])
        if fn in seen: continue
        seen.add(fn)
        rows.append({"date": d, "liturgicday_id": v["id"], "kind": kind(fn), "filename": fn, "url": u, "http_status": head(u)})
cache_f.write_text(json.dumps(cache))
with open(ROOT / "index.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
(ROOT / "index.json").write_text(json.dumps(rows, indent=1))
print(len(rows), "rows")
