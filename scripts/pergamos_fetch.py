#!/usr/bin/env python3
"""Download printed music books from Pergamos (University of Athens, Psachos
collection) and stitch each book's page images into one PDF.

Pergamos offers no PDF/zip for these items; page images are public via its API:
  POST /public-api/search  (PsachosBookPage children, sorted by pageNumber)
  GET  /public-api/files/uoadl/<webFile.id>/payload

Scans are CC BY-NC-ND 4.0: keep output private (not in this public repo).

Usage:
  python scripts/pergamos_fetch.py --list                 # list books
  python scripts/pergamos_fetch.py                        # all books
  python scripts/pergamos_fetch.py 168180 168182          # selected ids
  python scripts/pergamos_fetch.py --out DIR              # default: ./pergamos
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import time
import urllib.request
from pathlib import Path

import img2pdf
from PIL import Image, ImageDraw

BASE = "https://pergamos.lib.uoa.gr/public-api"
STORE = "uoadl"
PAGE_SIZE = 200
DELAY = 0.2  # seconds between image requests


def _request(url: str, body: dict | None = None, retries: int = 4) -> bytes:
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Accept": "application/json", "User-Agent": "pergamos-fetch/1.0"}
    if data:
        headers["Content-Type"] = "application/json"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            if attempt == retries - 1:
                raise
            wait = 2 ** attempt
            print(f"  retry in {wait}s: {e}", file=sys.stderr)
            time.sleep(wait)
    raise AssertionError


def search(model: str, filters: list[dict]) -> list[dict]:
    items, start = [], 0
    while True:
        body = {
            "start": start, "count": PAGE_SIZE, "models": [model], "fields": [],
            "strict": False,
            "query": {"filters": {"and": [{"eq": {"published": True}}, *filters]},
                      "sorting": ["pageNumber:asc"] if model.endswith("Page") else []},
        }
        res = json.loads(_request(f"{BASE}/search", body))
        items += res["items"]
        start += PAGE_SIZE
        if start >= res["total"]:
            return items


def el(value) -> str:
    if isinstance(value, list):
        for x in value:
            if isinstance(x, dict) and x.get("key") == "el":
                return str(x["value"])
        return str(value[0].get("value", "")) if value and isinstance(value[0], dict) else ""
    return str(value or "")


def list_books() -> list[dict]:
    return search("PsachosBook", [])


def book_name(book: dict) -> str:
    title = re.sub(r'[\\/:*?"<>|]+', " ", el(book.get("title"))).strip()
    year = el(book.get("creationYearText")).replace("/", "-").strip()
    name = f"{book['id']} {title[:90].rstrip()}"
    return f"{name} ({year})" if year else name


def _readable_or_placeholder(path: Path, book_id: str, n: int) -> Path:
    """Some Pergamos files are corrupt at source (checksum matches, not a JPEG).
    Substitute a labelled blank page so image numbering stays aligned."""
    try:
        with Image.open(path) as im:
            im.verify()
        return path
    except Exception:  # noqa: BLE001
        print(f"  WARNING: book {book_id} image {n} is corrupt at source; placeholder inserted",
              file=sys.stderr)
        ph = path.with_name(f"{path.stem}.placeholder.png")
        im = Image.new("L", (1536, 1024), 255)
        ImageDraw.Draw(im).text((40, 40), f"Pergamos {book_id}: image {n} corrupt at source", fill=0)
        im.save(ph)
        return ph


def fetch_book(book: dict, out: Path) -> Path:
    name = book_name(book)
    pdf = out / f"{name}.pdf"
    if pdf.exists():
        print(f"skip (exists): {pdf.name}")
        return pdf
    pages = search("PsachosBookPage", [{"eq": {"parents": f"{STORE}:{book['id']}"}},
                                       {"exists": "webFile"}])
    pages.sort(key=lambda p: (p.get("pageNumber") or 0))
    cache = out / ".cache" / book["id"]
    cache.mkdir(parents=True, exist_ok=True)
    print(f"{name}: {len(pages)} images")
    files = []
    for i, p in enumerate(pages, 1):
        wf = p["webFile"]
        dest = cache / f"{i:04d}.jpg"
        want = wf.get("checksum")
        if not (dest.exists() and (not want or hashlib.sha1(dest.read_bytes()).hexdigest() == want)):
            blob = _request(f"{BASE}/files/{wf.get('storeName', STORE)}/{wf['id']}/payload")
            if want and hashlib.sha1(blob).hexdigest() != want:
                raise RuntimeError(f"checksum mismatch: book {book['id']} page {i}")
            dest.write_bytes(blob)
            time.sleep(DELAY)
        files.append(dest)
        print(f"\r  {i}/{len(pages)}", end="", flush=True)
    print()
    files = [_readable_or_placeholder(f, book["id"], i) for i, f in enumerate(files, 1)]
    tmp = pdf.with_suffix(".pdf.part")
    tmp.write_bytes(img2pdf.convert([str(f) for f in files]))  # lossless JPEG embed
    tmp.rename(pdf)
    shutil.rmtree(cache)
    print(f"  -> {pdf}")
    return pdf


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*", help="book ids (uoadl:NNN or NNN); default all")
    ap.add_argument("--out", type=Path, default=Path("pergamos"))
    ap.add_argument("--list", action="store_true", help="list books and exit")
    args = ap.parse_args()

    books = list_books()
    if args.list:
        for b in books:
            print(book_name(b))
        return
    if args.ids:
        want = {i.split(":")[-1] for i in args.ids}
        books = [b for b in books if b["id"] in want]
        missing = want - {b["id"] for b in books}
        if missing:
            sys.exit(f"unknown ids: {', '.join(sorted(missing))}")
    args.out.mkdir(parents=True, exist_ok=True)
    failed = []
    for b in books:
        try:
            fetch_book(b, args.out)
        except Exception as e:  # noqa: BLE001
            print(f"\nFAILED {b['id']}: {e}", file=sys.stderr)
            failed.append(b["id"])
    if failed:
        sys.exit(f"failed: {' '.join(failed)} (rerun to resume)")


if __name__ == "__main__":
    main()
