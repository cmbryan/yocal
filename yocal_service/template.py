"""Extract the Divine Liturgy text from the parish choir PDF into a section/block template.

The PDF mixes text with embedded notation; notation noise is filtered out. Output goes to a local,
git-ignored JSON (the PDF text is copyrighted and must not be committed).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

import yaml

HERE = os.path.dirname(__file__)
CONFIG = os.path.join(HERE, "data", "liturgy_sections.yaml")
LOCAL = os.path.join(HERE, "local")
TEMPLATE = os.path.join(LOCAL, "liturgy_template.json")

ROLE = re.compile(r"^(Priest|Deacon|Choir|Reader|People|All|Chanter|Cantor|Bishop|Verse|Refrain|Right Choir|Left Choir)(?:/\w+)?:\s*(.*)$")
LITURGY_START = re.compile(r"THE DIVINE LITURGY OF ST JOHN CHRYSOSTOM")
SCORE_TITLE = re.compile(r"(Mode \d|Mode pl|Plagal|Di=|Pa=|Vu=|Ga=|Ke=|Zo=|Soft Chromatic|Diatonic|Chromatic|Enharmonic|©|Copyright|Permission|Translation by|Translation ©|Melody|Text GOA|Used by permission|Musical text|Transcribed|transcribed|Byzantine chant|Arranged by|Fourth Mode|Tone \d+/|Intonation|Adagio|Andante|Largo|Version \d|BACK TO|START HERE|START WITH|RESUME HERE|Right Choir sings|Left Choir|Antiochian Village|Archdiocese of North America|Hieromonk|Greek Orthodox Archdiocese)")
MUSIC_GLYPH = re.compile(r"[œ˙ŒΛχµϕψ¶º•ˆ˜]|[#!\"$%&]{2,}|(\b[kjnfdeCDGEF]\b ?){3,}")
SYLLABLES = re.compile(r"\S+ - \S+ - |\w+ - \w+\s{2,}|\w+-\w+ - ")


def pdf_text(pdf: str) -> str:
    return subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout


def is_noise(line: str) -> bool:
    t = line.strip()
    if not t:
        return False  # blank lines are structure, kept
    if MUSIC_GLYPH.search(t) or SCORE_TITLE.search(t) or SYLLABLES.search(t):
        return True
    letters = sum(c.isalpha() for c in t)
    if letters < 0.6 * len(t.replace(" ", "")):
        return True
    if re.fullmatch(r"[A-G]( {2,}[A-G])*", t) or re.fullmatch(r"[A-Za-z]{1,2}", t):
        return True
    return False


def _indent(s: str) -> int:
    return len(s) - len(s.lstrip())


def anchor_lines(lines: list, sections: list) -> list:
    """-> [(section_cfg, line_index)] in order; each anchor searched after the previous one."""
    out, pos = [], 0
    for cfg in sections:
        rx = re.compile(cfg["start"])
        for i in range(pos, len(lines)):
            if rx.search(lines[i].strip()) and not is_noise(lines[i]):
                out.append((cfg, i))
                pos = i + 1
                break
        else:
            print(f"warning: anchor for {cfg['id']} not found ({cfg['start']})", file=sys.stderr)
    return out


def blocks_from(lines: list) -> list:
    """Cleaned lines -> blocks: line (role,text) | rubric | note."""
    blocks, cur, prev_kept = [], None, False

    def flush():
        nonlocal cur
        if cur:
            cur["text"] = re.sub(r"\s+(?:[A-Z]{3,}(?: [A-Z]{3,})+|After the Gospel Reading\.|The Prayer For The Departed\d?|The troparia for the Departed.*)$", "", re.sub(r"\s+", " ", cur["text"])).strip()
            if cur["text"] or cur.get("role"):
                blocks.append(cur)
        cur = None

    for raw in lines:
        mk = re.fullmatch(r"@@SLOT:(\w+)@@", raw.strip())
        if mk:
            flush()
            blocks.append({"t": "slot", "slot": mk.group(1)})
            prev_kept = False
            continue
        if is_noise(raw):
            prev_kept = False
            continue
        t = raw.strip()
        if not t:
            prev_kept = False
            flush()
            continue
        m = ROLE.match(t)
        if m:
            flush()
            cur = {"t": "line", "role": m.group(1), "text": m.group(2)}
            prev_kept = True
        elif prev_kept and cur and _indent(raw) >= 6 and cur["t"] == "line":
            cur["text"] += " " + t
        elif _indent(raw) < 6 or not prev_kept:
            if cur and cur["t"] == "rubric" and prev_kept and _indent(raw) < 6:
                cur["text"] += " " + t
            else:
                flush()
                cur = {"t": "rubric" if _indent(raw) < 6 else "note", "text": t}
                prev_kept = True
        else:
            if cur:
                cur["text"] += " " + t
    flush()
    return blocks


def _keep(b: dict) -> bool:
    """Drop score/lyric fragments that survived the line filter; keep real rubrics."""
    if b["t"] in ("line", "slot"):
        return True
    t = b["text"]
    words = t.split()
    if t.startswith("[") and len(words) >= 6:  # bracketed seasonal rubric (may contain " - " dashes)
        return True
    if b["t"] == "note" or len(words) < 4 or "Translation" in t or len(re.findall(r"[/;\"]", t)) > 1:
        return False
    if re.search(r"\w - \w|\w -\w|\w- \w| [A-Za-z] [A-Za-z] |[ΔΓκ]", t) or sum(len(w) == 1 and w.isalpha() and w not in "aIA" for w in words) > 1:
        return False
    return t[0].isupper() or t[0] in "[("


def clean_blocks(blocks: list) -> list:
    """Drop score fragments; an unlabelled prose paragraph (>= 8 words, sentence end) is kept as a role-less line."""
    out = []
    for b in blocks:
        if b["t"] == "note" and len(b["text"].split()) >= 8 and re.search(r"[.!?:;]$", b["text"]) and not re.search(r"\w - \w|[ΔΓκ]|[/;\"]", b["text"]):
            out.append({"t": "line", "role": "", "text": b["text"]})
        elif _keep(b):
            out.append(b)
    return out


def apply_spans(raw: list, spans: list, kept: dict | None = None) -> list:
    """Replace line ranges by @@SLOT:name@@ markers (spans are config-defined); `keep: true` spans store their text in `kept`."""
    for sp in spans or []:
        a_rx = re.compile(sp.get("after") or sp["start"])
        u_rx = re.compile(sp["until"])
        for i, ln in enumerate(raw):
            if a_rx.search(ln.strip()):
                begin = i + 1 if "after" in sp else i
                for j in range(begin, len(raw)):
                    if u_rx.search(raw[j].strip()) and j > i:
                        if kept is not None and sp.get("keep"):
                            kept[sp["slot"]] = re.sub(r"\s+", " ", " ".join(x.strip() for x in raw[begin:j])).strip()
                        raw = raw[:begin] + [f"@@SLOT:{sp['slot']}@@"] + raw[j:]
                        break
                else:
                    raw = raw[:begin] + [f"@@SLOT:{sp['slot']}@@"]
                break
    return raw


def _bracket_blocks(blocks: list, conds: list | None = None) -> list:
    """Bracketed rubrics '[ ... ]' (one or several blocks) -> a 'seasonal' block.
    `conds` (config `seasonal:`) supplies each one's `when` condition / `label` / `strip`; unmatched ones get none (shown collapsed)."""
    out, buf = [], None

    def emit(bs):
        first = bs[0].get("text", "")
        c = next((c for c in conds or [] if re.search(c["match"], first)), {})
        out.append({"t": "seasonal", "blocks": bs, "when": c.get("when"), "label": c.get("label", ""), "strip": c.get("strip", "")})

    for b in blocks:
        txt = b.get("text", "")
        if buf is None and txt.startswith("[") and b["t"] != "slot":
            if txt.count("[") > txt.count("]"):
                buf = [b]
            elif any(re.search(c["match"], txt) for c in conds or []):
                emit([b])
            else:
                out.append(b)  # ordinary bracketed phrase, not a seasonal block
            continue
        if buf is not None:
            buf.append(b)
            if txt.rstrip().endswith("]") and txt.count("]") >= txt.count("["):
                emit(buf)
                buf = None
            continue
        out.append(b)
    if buf:
        out += buf
    return out


_CFG = None


def config() -> dict:
    global _CFG
    if _CFG is None:
        _CFG = yaml.safe_load(open(CONFIG, encoding="utf-8"))
    return _CFG


def build(pdf: str, config: str = CONFIG) -> dict:
    cfg = yaml.safe_load(open(config, encoding="utf-8"))
    lines = pdf_text(pdf).split("\n")
    start = next(i for i, ln in enumerate(lines) if LITURGY_START.search(ln))
    lines = lines[start:]
    anchors = anchor_lines(lines, cfg["sections"])
    sections = []
    for k, (sc, i) in enumerate(anchors):
        end = anchors[k + 1][1] if k + 1 < len(anchors) else len(lines)
        raw = lines[i + 1:end] if not sc.get("keep_first") else lines[i:end]
        if sc["start"].startswith("^Deacon:") or sc["start"].startswith("^Priest:"):
            raw = lines[i:end]  # the anchor line is itself text
        if sc.get("replace"):
            blocks = [{"t": "slot", "slot": sc["replace"]}]
        else:
            kept = {}
            raw = apply_spans(raw, sc.get("spans"), kept)
            blocks = _bracket_blocks(clean_blocks(blocks_from(raw)), cfg.get("seasonal"))
            for b in blocks:
                if b["t"] == "slot" and b["slot"] in kept:
                    b["template"] = re.sub(r"^Priest:\s*", "", kept[b["slot"]])
        sections.append({"id": sc["id"], "title": sc["title"], "optional": bool(sc.get("optional")), "exclude": bool(sc.get("exclude")), "blocks": blocks,
                         "music": sc.get("music", []), "dcs_text": sc.get("dcs_text")})
    return {"source": os.path.basename(pdf), "service": "liturgy", "sections": sections}


def load() -> dict:
    if not os.path.exists(TEMPLATE):
        raise FileNotFoundError(f"{TEMPLATE} missing: run `python -m yocal_service.build_template <PDF>`")
    return json.load(open(TEMPLATE, encoding="utf-8"))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("usage: python -m yocal_service.build_template PDF [--out FILE]", file=sys.stderr)
        return 1
    out = argv[argv.index("--out") + 1] if "--out" in argv else TEMPLATE
    t = build(argv[0])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(t, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n = sum(len(s["blocks"]) for s in t["sections"])
    print(f"{out}: {len(t['sections'])} sections, {n} blocks")
    return 0
