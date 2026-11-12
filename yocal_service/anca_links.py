"""ANCA service-text PDFs: extract the embedded music hyperlinks with the visible label and the line they sit on."""
from __future__ import annotations

import datetime as dt
import io
import os
import re
import subprocess
import tempfile
import urllib.request

import pypdf

from yocal_rules import anca

MUSIC_HOST = "antiochianprodsa.blob.core.windows.net/musiclibrary"


def fetch_pdf(date: dt.date, kind: str) -> bytes | None:
    for url in anca.candidate_urls(date, kind):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers=anca.UA), timeout=40).read()
        except Exception:
            continue
        if data.startswith(b"%PDF"):
            return data
    return None


def _words(pdf: bytes):
    """pdftotext -bbox -> {page: [(x0, y0, x1, y1, word)]}"""
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "a.pdf")
        open(p, "wb").write(pdf)
        out = subprocess.run(["pdftotext", "-bbox", p, "-"], capture_output=True, text=True).stdout
    pages = {}
    for i, pg in enumerate(out.split("<page ")[1:], 1):
        pages[i] = [(float(a), float(b), float(c), float(d_), w) for a, b, c, d_, w in
                    re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)', pg)]
    return pages


def links(pdf: bytes) -> list:
    """-> [{url, page, label, context}] in document order. context = text of the line the link sits on (before the link)."""
    reader = pypdf.PdfReader(io.BytesIO(pdf))
    words = _words(pdf)
    out = []
    for pno, page in enumerate(reader.pages, 1):
        h = float(page.mediabox.height)
        for a in page.get("/Annots") or []:
            a = a.get_object()
            if a.get("/Subtype") != "/Link":
                continue
            url = (a.get("/A") or {}).get("/URI")
            if not url or MUSIC_HOST not in url:
                continue
            x0, y0, x1, y1 = (float(v) for v in a["/Rect"])
            top, bot = h - y1, h - y0  # PDF y is bottom-up; bbox is top-down
            inside = [w for w in words.get(pno, []) if w[0] >= x0 - 2 and w[2] <= x1 + 2 and w[1] >= top - 3 and w[3] <= bot + 3]
            line = sorted([w for w in words.get(pno, []) if w[1] >= top - 3 and w[3] <= bot + 3 and w[2] <= x0 + 2], key=lambda w: w[0])
            out.append({"url": url, "page": pno, "label": " ".join(w[4] for w in sorted(inside, key=lambda w: w[0])),
                        "context": " ".join(w[4] for w in line)})
    return out
