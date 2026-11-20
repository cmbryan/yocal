#!/usr/bin/env python3
"""Find every indexed music setting of a hymn id across the public-domain books.

Sources:
  yocal_rules/data/sources/byzantine_pd.yaml   books in the repo root (TA1/TA2, PD2, HE1/HE2, AN)
  yocal_rules/data/sources/pergamos/*.yaml     Pergamos books in FETCHED/ (one file per book)

Usage:
  python scripts/hymn_sources.py men/12-25/apolytikion
  python scripts/hymn_sources.py 'oct/t3/sun/*'          # shell-style glob
  python scripts/hymn_sources.py --grep "Κύριε ἐλέησον"  # search titles/notes, mapped or not
  python scripts/hymn_sources.py lit/axion_estin --open 2   # open result [2] at its page
  python scripts/hymn_sources.py --write                 # regenerate hymn_sources.md (with page links)

In a terminal, "PDF n" and the path are hyperlinks (file://...#page=n; Ctrl-click). Browsers' PDF
viewers honour #page; desktop viewers via xdg-open usually don't, hence --open (evince/okular/zathura).
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "yocal_rules/data/sources"
FETCHED = ROOT / "FETCHED"
TONES = {1: "1", 2: "2", 3: "3", 4: "4", 5: "pl1", 6: "pl2", 7: "grave", 8: "pl4"}


def _pdf_page(layout: list[dict], page: int, part=None, vol=None) -> int | None:
    hit = None
    if layout:  # entries without part/vol belong to the first part/vol listed
        part = part if part is not None else layout[0].get("part")
        vol = vol if vol is not None else layout[0].get("vol")
    for seg in layout:
        if seg.get("part", part) != part or seg.get("vol", vol) != vol:
            continue
        if page >= seg.get("from", 1) and page <= seg.get("to", 10**6):
            hit = seg
    return None if hit is None else page // hit.get("div", 1) + hit["add"]


def _expand(hid: str, extra: dict) -> list[tuple[str, dict]]:
    """oct/t{t}/... -> 8 concrete ids; eothinon/{n}/... -> 11."""
    if "{t}" in hid:
        tones = extra.get("tones") or range(1, 9)
        return [(hid.replace("{t}", str(t)), {**extra, "tone": t}) for t in tones]
    if "{n}" in hid:
        return [(hid.replace("{n}", f"{n:02d}"), {**extra, "n": n}) for n in range(1, 12)]
    return [(hid, extra)]


def load() -> list[dict]:
    rows: list[dict] = []
    # 1. byzantine_pd.yaml (repo-root PDFs; single-page offsets)
    bp = yaml.safe_load((SRC / "byzantine_pd.yaml").read_text())
    books = bp["books"]
    for hid, locs in (bp.get("hymns") or {}).items():
        for loc in locs:
            b = books[loc["book"]]
            lay = [{"from": o["from"], "div": 1, "add": o["add"]} for o in b["offsets"]]
            for cid, x in _expand(hid, loc):
                page = (loc.get("pages") or [None])[0]
                if loc.get("section") and "tone" in x:
                    page = bp["an_tone_sections"][x["tone"]][loc["section"]]
                rows.append(dict(id=cid, book=loc["book"], year=b.get("year"), title=b["title"],
                                 file=ROOT / b["file"], page=page,
                                 pdf=_pdf_page(lay, page) if page else None,
                                 status=loc.get("status", ""), note=loc.get("note", ""),
                                 entry=loc.get("note", "")))
    # 2. Pergamos books
    for f in sorted((SRC / "pergamos").glob("*.yaml")):
        d = yaml.safe_load(f.read_text())
        for e in d.get("entries") or []:
            hids = e.get("hymn") or []
            hids = hids if isinstance(hids, list) else [hids]
            base = dict(book=d["key"], year=d.get("year"), title=d["title"],
                        file=FETCHED / d["file"], page=e.get("page"), status=e.get("status", ""),
                        note=e.get("note", ""), entry=e.get("title", ""), who=e.get("who", ""),
                        proposed=e.get("proposed", ""))
            pdf = _pdf_page(d.get("layout") or [], e["page"], e.get("part"), e.get("vol")) \
                if isinstance(e.get("page"), int) else None
            if not hids:
                rows.append(dict(base, id="", pdf=pdf))
            for hid in hids:
                for cid, _ in _expand(str(hid), e):
                    rows.append(dict(base, id=cid, pdf=pdf))
    return rows


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def _order(r: dict) -> tuple:
    m = re.search(r"\d{4}", str(r.get("year") or ""))
    return (int(m.group()) if m else 9999, r["book"], r.get("page") or 0 if isinstance(r.get("page"), int) else 0)


def _url(r: dict) -> str:
    return r["file"].resolve().as_uri() + (f"#page={r['pdf']}" if r.get("pdf") else "")


def _link(text: str, url: str, on: bool) -> str:
    """OSC 8 terminal hyperlink (Ctrl/Cmd-click in VS Code, GNOME Terminal, iTerm2, kitty, WezTerm...)."""
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\" if on else text


def fmt(r: dict, n: int, links: bool) -> str:
    who = f" — {r['who']}" if r.get("who") else ""
    pdf = f"PDF {r['pdf']}" if r.get("pdf") else "PDF ?"
    st = f" [{r['status']}]" if r.get("status") else ""
    note = f"\n      note: {r['note']}" if r.get("note") else ""
    rel = os.path.relpath(r["file"])
    missing = "" if r["file"].exists() else "  (file not present)"
    return (f"  [{n}] {r['book']:6} {r.get('year') or '':>4}  p.{r.get('page') or '?':<5} "
            f"{_link(pdf, _url(r), links):<9}{st}  {r['entry']}{who}\n"
            f"      {_link(rel, _url(r), links)}{missing}{note}")


def open_pdf(r: dict) -> None:
    """Open at the page: evince/okular/zathura take a page number; else xdg-open (first page)."""
    f, pg = str(r["file"]), r.get("pdf")
    for exe, args in (("evince", ["-i", str(pg)]), ("okular", ["-p", str(pg)]), ("zathura", ["-P", str(pg)])):
        if pg and shutil.which(exe):
            subprocess.Popen([exe, *args, f], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
    subprocess.Popen(["xdg-open", f], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def write_md(rows: list[dict]) -> Path:
    out = SRC / "hymn_sources.md"
    lines = ["# Hymn id → music settings (generated by scripts/hymn_sources.py --write; do not edit)", "",
             "PDF = page in the scan file (repo root for TA/PD2/HE/AN, `FETCHED/` for PG*).", ""]
    ids = sorted({r["id"] for r in rows if r["id"]})
    for hid in ids:
        lines.append(f"## `{hid}`")
        for r in sorted((r for r in rows if r["id"] == hid), key=_order):
            rel = os.path.relpath(r["file"], out.parent).replace(" ", "%20")
            pdf = f"[PDF {r['pdf']}]({rel}#page={r['pdf']})" if r.get("pdf") else f"[PDF]({rel})"
            lines.append(f"- **{r['book']}** ({r.get('year') or 'n.d.'}) p.{r.get('page') or '?'} → "
                         f"{pdf} · {r['entry']}"
                         + (f" — {r['who']}" if r.get("who") else "")
                         + (f" · _{r['status']}_" if r.get("status") else ""))
        lines.append("")
    out.write_text("\n".join(lines))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pattern", nargs="?", help="hymn id or glob")
    ap.add_argument("--grep", help="search entry titles/notes (accent-insensitive)")
    ap.add_argument("--write", action="store_true", help="regenerate hymn_sources.md")
    ap.add_argument("--open", type=int, metavar="N", help="open result [N] at its page in a PDF viewer")
    ap.add_argument("--no-links", action="store_true", help="plain text (no terminal hyperlinks)")
    a = ap.parse_args()
    rows = load()
    if a.write:
        print(f"wrote {write_md(rows)}")
    hits = []
    if a.pattern:
        hits = [r for r in rows if r["id"] and fnmatch.fnmatchcase(r["id"], a.pattern)]
    if a.grep:
        q = _fold(a.grep)
        hits = [r for r in rows if q in _fold(f"{r['entry']} {r['note']} {r.get('proposed', '')}")]
    links = sys.stdout.isatty() and not a.no_links
    ordered = [r for hid in sorted({r["id"] for r in hits})
               for r in sorted((r for r in hits if r["id"] == hid), key=_order)]
    last = None
    for n, r in enumerate(ordered, 1):
        if r["id"] != last:
            print(r["id"] or "(unmapped)")
            last = r["id"]
        print(fmt(r, n, links))
    if a.open:
        if not 1 <= a.open <= len(ordered):
            sys.exit(f"--open: choose 1..{len(ordered)}")
        open_pdf(ordered[a.open - 1])
    if (a.pattern or a.grep) and not hits:
        print("no settings indexed")


if __name__ == "__main__":
    main()
