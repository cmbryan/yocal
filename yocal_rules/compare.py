"""Slot-by-slot comparison of resolved Rules against an Answer key (ANCA, DCS keys-only).

States: match | diff | not_in_key (Rule resolved, key silent on the slot) | key_only (key has it, Rule missing)
        | no_key (no file/page for the date) | n/a (Rule missing and key silent).
Diff classes: ANCA diff on explicit/inferred Rule with no Divergence-log entry = `unexplained` (blocking);
DCS diff = `unreviewed DCS diff` (non-blocking) unless logged.
"""
from __future__ import annotations

import glob
import os
from dataclasses import dataclass, field

import yaml

from . import hymns
from .refs import norm_ref
from .rules import DATA


@dataclass
class Cmp:
    source: str  # anca | dcs
    state: str
    key: dict | None = None
    details: list = field(default_factory=list)
    cls: str = ""  # '', unexplained, unreviewed, or Divergence-log class
    entry: dict | None = None

    @property
    def blocking(self):
        return self.source == "anca" and self.cls == "unexplained"


def load_divergence(data_dir: str = DATA):
    """All data/divergence*.yaml files (one file per area keeps edits separate)."""
    out = []
    for p in sorted(glob.glob(os.path.join(data_dir, "divergence*.yaml"))):
        out += yaml.safe_load(open(p, encoding="utf-8")) or []
    return out


def _val_eq(attr, ours, theirs):
    if attr == "ref":
        return norm_ref(ours) == norm_ref(theirs)
    if attr == "other":  # structure of the non-resurrectional blocks is not reliably printed: compare totals
        return sum(ours) == sum(theirs)
    return ours == theirs


def _subset_eq(spec: dict, actual: dict) -> bool:
    return all(k in actual and _val_eq(k, v, actual[k]) for k, v in spec.items())


def _find_entry(log, slot, source, facts, service, ours, theirs):
    """Class-scoped Divergence-log entry: scope = context facts (date, mmdd, service or any fact), plus optional
    `ours` / `theirs` (dict or list of alternatives) the two sides are expected to show."""
    ctx = {**facts, "service": service}
    for e in log:
        slots = e["slot"] if isinstance(e["slot"], list) else [e["slot"]]
        if slot not in slots or e["source"] != source:
            continue
        if not all(ctx.get(k) in v if isinstance(v, list) else ctx.get(k) == v for k, v in e.get("scope", {}).items()):
            continue
        if "ours" in e and not _subset_eq(e["ours"], ours):
            continue
        if "theirs" in e:
            alts = e["theirs"] if isinstance(e["theirs"], list) else [e["theirs"]]
            if not any(_subset_eq(a, theirs) for a in alts):
                continue
        return e
    return None


def compare(res, key: dict | None, source: str, facts, service, log):
    """res: rules.Resolution; key: slot->attrs dict for the date ({} or None => no key)."""
    if not key:
        return Cmp(source, "no_key")
    kv = key.get(res.slot)
    if res.status == "missing":
        return Cmp(source, "key_only" if kv else "n/a", kv)
    if kv is None:
        return Cmp(source, "not_in_key")
    diffs, compared = [], 0
    for a, v in res.fill.items():
        if a == "hymns" or v in (None, "?") or a not in kv or kv[a] is None:
            continue
        compared += 1
        if not _val_eq(a, v, kv[a]):
            diffs.append(f"{a}: ours {v} / {source.upper()} {kv[a]}")
    ours_h = [h.id for h in (hymns.for_slot(res.slot, res, facts) or [])]
    if kv.get("hymns") and ours_h:  # the hymns themselves (DCS keys name them): ids, order ignored
        compared += 1
        if set(ours_h) != set(kv["hymns"]):
            diffs.append(f"hymns: ours {ours_h} / {source.upper()} {kv['hymns']}")
    if not compared:
        return Cmp(source, "not_in_key", kv)
    if not diffs:
        return Cmp(source, "match", kv)
    c = Cmp(source, "diff", kv, diffs)
    c.entry = _find_entry(log, res.slot, source, facts, service, res.fill, kv)
    c.cls = f"divergence:{c.entry['class']}" if c.entry else ("unexplained" if source == "anca" else "unreviewed")
    return c
