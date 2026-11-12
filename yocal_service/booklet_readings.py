"""Prokeimena and Alleluia verses from the parish choir booklets (previous years' full services).

Text is third-party/parish copyright: it is extracted into git-ignored local/booklet_readings.json, with the booklet named as the source.
A booklet's Sunday tone is in its file name ('... TONE 7.pdf'). Selection for a date (see `select`):
  * ordinary: the item whose tone equals the Sunday's tone (and the booklet's own Sunday tone), so saint/feast items are skipped;
  * occasion: items whose tone differs from the booklet's Sunday tone are kept as occasion items (Forefathers, Sunday before the Nativity).

    python -m yocal_service.booklet_readings PDF [PDF ...]
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

LOCAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local")
PATH = os.path.join(LOCAL, "booklet_readings.json")
ROLE = re.compile(r"^(Reader|Choir|Deacon|Priest):\s*(.*)$")


def _lines(pdf: str) -> list:
    return subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout.split("\n")


def _section(lines: list, start_rx: str, stop_rx: str) -> tuple:
    """-> (heading, [(role, text)]) for the LAST heading matching start_rx (the Liturgy, after the Hours/Matins), up to stop_rx."""
    idx = [i for i, l in enumerate(lines) if re.match(start_rx, l.strip())]
    if not idx:
        return None, []
    i = idx[-1]
    head, out = lines[i].strip(), []
    for l in lines[i + 1:]:
        t = l.strip()
        if re.search(stop_rx, t):
            break
        m = ROLE.match(t)
        if m:
            out.append([m.group(1), m.group(2)])
        elif t and out and not re.search(r"[œ˙&]|^\W*$", t) and len(l) - len(l.lstrip()) >= 4 and not t.startswith(("The reader", "Soft", "Mode ", "Alleluia before")):
            out[-1][1] += " " + t
    return head, [(r, re.sub(r"\s*The Gospel\s*$", "", re.sub(r"\s+", " ", x)).strip()) for r, x in out]  # a wrapped page heading can trail the last line


def extract(pdf: str) -> dict:
    base = os.path.basename(pdf)
    m = re.match(r"(\d\d)(\d\d)(\d\d) .*TONE (\d)", base)
    lines = _lines(pdf)
    out = {"booklet": base, "date": f"20{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None, "sunday_tone": int(m.group(4)) if m else None}
    h, p = _section(lines, r"^(The )?Prokeimenon\b.*", r"^Deacon: Wisdom|^The Epistle")
    if p:
        tone = re.search(r"Tone (\d)", h)
        out["prokeimenon"] = {"title": h, "tone": int(tone.group(1)) if tone else None, "lines": [list(x) for x in p if x[0] in ("Reader", "Choir")]}
    h, p = _section(lines, r"^The Alleluia\b.*", r"^Priest:|^Deacon:")
    if p:
        tone = re.search(r"Tone (\d)", h)
        out["alleluia"] = {"title": h, "tone": int(tone.group(1)) if tone else out["sunday_tone"], "lines": [list(x) for x in p if x[0] in ("Reader", "Choir")]}
    return out


def build(pdfs: list):
    items = [extract(p) for p in pdfs]
    os.makedirs(LOCAL, exist_ok=True)
    json.dump(items, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for i in items:
        print(i["date"], "tone", i["sunday_tone"], "| prokeimenon:", (i.get("prokeimenon") or {}).get("title"), "| alleluia:", (i.get("alleluia") or {}).get("title"))
    print("->", PATH)


def load() -> list:
    return json.load(open(PATH, encoding="utf-8")) if os.path.exists(PATH) else []


def select(kind: str, f: dict) -> dict | None:
    """Booklet item for `kind` ('prokeimenon'|'alleluia') on the date described by facts f, or None."""
    desig = f"{f.get('desig','')} {f.get('desig_g','')}"
    occasion = "Forefathers" if "Forefathers" in desig else "Before the Nativity" if "before the nativity" in desig.lower() else None
    for it in load():
        x = it.get(kind)
        if not x or not x["lines"]:
            continue
        ordinary = x["tone"] == it["sunday_tone"]
        title = x["title"]
        if occasion and not ordinary and (("Forefathers" in title and kind == "prokeimenon") or kind == "alleluia" and it["date"].endswith("12-21") and occasion == "Before the Nativity"):
            return {**x, "booklet": it["booklet"], "date": it["date"], "occasion": True}
        if occasion == "Forefathers" and kind == "prokeimenon" and "Forefathers" in title:
            return {**x, "booklet": it["booklet"], "date": it["date"], "occasion": True}
        if not occasion and ordinary and x["tone"] == f.get("tone") and "Forefathers" not in title and not (kind == "alleluia" and f.get("tone") != x["tone"]):
            return {**x, "booklet": it["booklet"], "date": it["date"]}
    return None


if __name__ == "__main__":
    build(sys.argv[1:]) if len(sys.argv) > 1 else print(__doc__)
