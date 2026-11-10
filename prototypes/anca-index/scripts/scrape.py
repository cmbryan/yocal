"""Resolve each Sunday (+ eve Saturday) in range to liturgicday id, render page, extract servicetexts links.
Writes pages.json (date -> id, links). Resumable; raw DOM cached in raw/. Throttled."""
import json, re, sys
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import unquote
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent))
import render

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "pages.json"
START, END = date(2018, 2, 17), date(2026, 12, 6)
ANCHOR = (date(2026, 11, 1), 4724)

def parse_date(h):
    m = re.search(r"([A-Z]+)\s+(\d+),\s*(\d{4})", h.upper())
    return datetime.strptime(f"{m[1]} {m[2]} {m[3]}", "%B %d %Y").date() if m else None

def links(html):
    seen = []
    for m in re.finditer(r'href="([^"]*?/servicetexts/[^"]+)"', html):
        u = m[1].replace("&amp;", "&")
        if u not in seen: seen.append(u)
    return seen

def main():
    pages = json.loads(OUT.read_text()) if OUT.exists() else {}
    pages = {k: v for k, v in pages.items() if v["id"] is not None}
    idmap = {}  # id -> date
    for k, v in pages.items(): idmap[v["id"]] = date.fromisoformat(k)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome"); page = b.new_page()
        def get(i):
            html = render.fetch(page, i)
            d = parse_date(render.heading(html))
            if d: idmap[i] = d
            return d, html
        def resolve(target):
            # seed from raw cache headings
            for f in render.RAW.glob("*.html"):
                if int(f.stem) not in idmap:
                    dd = parse_date(render.heading(f.read_text()))
                    if dd: idmap[int(f.stem)] = dd
            if not idmap: idmap[ANCHOR[1]] = ANCHOR[0]
            bi, bd = min(idmap.items(), key=lambda kv: abs((kv[1] - target).days))
            i = bi + (target - bd).days
            for _ in range(8):
                d = idmap.get(i) or get(i)[0]
                if d == target: return i
                if d is None:
                    # hole in ids: find a dated id above, then step back by day difference
                    k = 2
                    while k <= 64:
                        j = i + k
                        dj = idmap.get(j) or get(j)[0]
                        if dj:
                            i = j - (dj - target).days
                            break
                        k *= 2
                    else:
                        return None
                    continue
                i += (target - d).days
            return None
        d = START + timedelta(days=(6 - START.weekday() - 0) % 7)  # first Sunday
        sundays = []
        while d <= END: sundays.append(d); d += timedelta(days=7)
        for sun in sundays:
            for day in (sun - timedelta(days=1), sun):
                k = day.isoformat()
                if k in pages: continue
                i = resolve(day)
                if i is None:
                    pages[k] = {"id": None, "links": []}; print(k, "UNRESOLVED id", flush=True)
                else:
                    _, html = get(i)
                    pages[k] = {"id": i, "links": links(html)}
                    print(k, i, len(pages[k]["links"]), flush=True)
                OUT.write_text(json.dumps(pages, indent=0))
        b.close()
main()
