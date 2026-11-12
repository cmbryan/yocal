"""Parse the text of an ANCA 'Divine Liturgy Variables' (READ) PDF into headed blocks."""
from __future__ import annotations

import re

FOOTER = re.compile(r"Liturgy Variables \d|^Portions of the Archdiocesan|Holy Transfiguration Monastery|^written authorization|^Pentecostarion, The Octoechos|^Transfiguration Monastery|may not be further reproduced", re.I)


def _is_heading(t: str) -> bool:
    letters = [c for c in t if c.isalpha()]
    return len(letters) >= 8 and all(c.isupper() for c in letters) and not t.startswith("•") and "**" not in t[:2]


def parse(text: str) -> list:
    """Like parse, but flushes the trailing paragraph of every block."""
    out, cur = [], None
    for raw in text.split("\n"):
        t = raw.strip()
        if FOOTER.search(t) or "Divine Liturgy Variables on" in t:
            continue
        base = re.sub(r"\([^)]*\)", "", t).strip()
        if base and _is_heading(base):
            if out and re.match(r"IN TONE \w+", base) and not out[-1]["body"] and not out[-1]["_p"]:  # heading wrapped onto a second line
                out[-1]["heading"] += " " + t
                cur = out[-1]
                continue
            cur = {"heading": t, "sub": [], "body": [], "_p": []}
            out.append(cur)
            continue
        if cur is None:
            continue
        if not t or t.startswith("•"):
            if cur["_p"]:
                cur["body"].append(" ".join(cur["_p"]))
                cur["_p"] = []
            if t.startswith("•"):
                cur = None
            continue
        if re.match(r"^(\(|\*\*)", t) and not cur["body"] and not cur["_p"]:
            cur["sub"].append(t)
        else:
            cur["_p"].append(t)
    for c in out:
        if c["_p"]:
            c["body"].append(" ".join(c["_p"]))
        c.pop("_p")
    return out


def find(blocks: list, heading_rx: str) -> list:
    rx = re.compile(heading_rx, re.I)
    return [b for b in blocks if rx.search(b["heading"])]
