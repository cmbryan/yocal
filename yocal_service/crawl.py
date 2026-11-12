"""One-off, rate-limited fill of the download cache (read-only fetches; each page/file fetched once, then cached).

    python -m yocal_service.crawl dcs [FROM [TO]]   # DCS Liturgy pages (li, li2) for every day not yet cached non-empty
    python -m yocal_service.crawl anca              # ANCA READ ('Liturgy Variables') file of every date in data/anca_pages.json

Then `python -m yocal_service.texts ingest` saves the texts into the sources store.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from yocal_rules import anca, dcs
from yocal_rules.rules import DATA

from .music import CACHE

DELAY = 1.0  # seconds between requests


def _cached(fn: str) -> bool:
    return os.path.exists(fn) and os.path.getsize(fn) > 0


def crawl_dcs(start: dt.date, end: dt.date, codes=("li", "li2")) -> dict:
    st = {"fetched": 0, "found": 0, "skipped": 0}
    d = start
    while d <= end:
        for code in codes:
            fn = os.path.join(CACHE, f"dcs-{d.isoformat()}-{code}.html")
            if _cached(fn):
                st["skipped"] += 1
                continue
            if os.path.exists(fn):
                os.remove(fn)  # an empty file = unavailable when last tried: retry once
            st["fetched"] += 1
            try:
                st["found"] += bool(dcs.fetch(d, code, CACHE))
            except Exception as e:  # network trouble: leave uncached, report
                print(f"dcs {d} {code}: {type(e).__name__}: {e}", file=sys.stderr)
            time.sleep(DELAY)
        d += dt.timedelta(days=1)
    return st


def _read_link(links: list) -> str | None:
    """The date's Liturgy Variables PDF: '... READ.pdf' or (older names) '... Variables ....pdf'; not the bilingual edition."""
    for want in ("READ", "Variables"):
        for l in links:
            n = urllib.parse.unquote(l)
            if n.lower().endswith(".pdf") and want in n and "Bilingual" not in n:
                return l
    return None


def crawl_anca() -> dict:
    idx = json.load(open(os.path.join(DATA, "anca_pages.json"), encoding="utf-8"))
    st = {"dates": 0, "fetched": 0, "found": 0, "skipped": 0}
    for day, ent in sorted(idx.items()):
        link = _read_link(ent.get("links", []))
        if not link:
            continue
        st["dates"] += 1
        fn = os.path.join(CACHE, f"anca-{day}-READ.txt")
        if _cached(fn):
            st["skipped"] += 1
            continue
        st["fetched"] += 1
        try:
            data = urllib.request.urlopen(urllib.request.Request(anca.BASE + link, headers=anca.UA), timeout=60).read()
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"anca {day}: {type(e).__name__}: {e}", file=sys.stderr)
            time.sleep(DELAY)
            continue
        txt = ""
        if data.startswith(b"%PDF"):
            pdf = fn + ".pdf"
            open(pdf, "wb").write(data)
            txt = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
            os.remove(pdf)
        open(fn, "w", encoding="utf-8").write(txt)
        st["found"] += bool(txt)
        time.sleep(DELAY)
    return st


def main(argv=None):
    a = argv if argv is not None else sys.argv[1:]
    if a[:1] == ["dcs"]:
        s = dt.date.fromisoformat(a[1]) if len(a) > 1 else dt.date.today() - dt.timedelta(days=14)
        e = dt.date.fromisoformat(a[2]) if len(a) > 2 else dt.date.today() + dt.timedelta(days=400)
        print(crawl_dcs(s, e))
    elif a[:1] == ["anca"]:
        print(crawl_anca())
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
