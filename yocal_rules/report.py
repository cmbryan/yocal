"""Explanatory supplement / build report: Rules, provenance, sources, and explicit comparison with ANCA and DCS."""
from __future__ import annotations

import datetime as dt

from .render import TITLES

SYM = {"match": "✔ match", "diff": "✘ DIFF", "not_in_key": "— not in key", "key_only": "! key only (no Rule)",
       "no_key": "— no key", "n/a": "—"}


def _attrs(d):
    if not d:
        return "—"
    return ", ".join(f"{k}={v}" for k, v in d.items() if k != "saint_labels") + (
        f" [{'; '.join(d['saint_labels'])}]" if d.get("saint_labels") else "")


def _fill(res):
    return _attrs(res.fill) if res.status != "missing" else "—"


def _cite(res):
    r = res.rule
    if not r:
        return "no Rule matches"
    s = f"{r['source']} {r['locator']}"
    if r["status"] == "inferred":
        s += f" — evidence: {r['evidence']}"
    if r["status"] == "missing":
        s += f" — ticket {r['ticket']}"
    if r.get("conflict"):
        s += f" — ⚠ Source conflict ({r['conflict']['status']}): {r['conflict']['note']}"
    return s


def gate(r):
    blocking = [(s, c) for src in r.comparisons.values() for s, c in src.items() if c.blocking]
    return blocking


def supplement(r) -> str:
    f = r.facts
    anca, dcs = r.comparisons.get("anca", {}), r.comparisons.get("dcs", {})
    ld = f["date"]
    L = [f"# Supplement: {TITLES[r.service]}, {r.service_date:%A %-d %B %Y}", "",
         f"Liturgical day {ld}. Companion to the service document; explains how each Variable part was chosen and how it compares with the Answer keys.", ""]
    blocking = gate(r)
    cnt = lambda src, st: sum(1 for c in src.values() if c.state == st)
    L.append("## Summary")
    L.append(f"- Gate: **{'BLOCKED — ' + str(len(blocking)) + ' unexplained ANCA diff(s)' if blocking else 'no blocking diffs'}** "
             f"(blocking = ANCA diff on an explicit/inferred Rule with no Divergence-log entry)")
    L.append(f"- Slots: {len(r.slots)}; explicit {sum(1 for *_, x in r.slots if x.status == 'explicit')}, "
             f"inferred {sum(1 for *_, x in r.slots if x.status == 'inferred')}, missing {sum(1 for *_, x in r.slots if x.status == 'missing')}")
    for name, src in (("ANCA", anca), ("DCS", dcs)):
        if name.lower() in r.comparisons:
            L.append(f"- {name}: {cnt(src, 'match')} match, {cnt(src, 'diff')} differ, {cnt(src, 'not_in_key')} not in key, "
                     f"{cnt(src, 'key_only')} key-only, {cnt(src, 'no_key') + cnt(src, 'n/a')} no key/n.a.")
    g = f["glory_source"]
    if f["saint_has_glory"] is None:
        L.append(f"- Caution: saint-has-Glory could not be derived ({g}); dependent Rules are missing.")
    elif g.startswith("Typikon Ch V"):
        L.append("- Caution: saint-has-Glory was inferred from the Typikon Ch V per-date stichera count, so a stichera-count match with a key on this date is partly circular; apolytikia/dismissal matches remain an independent check.")
    else:
        L.append(f"- Caution: saint-has-Glory comes from ALWB flags only ({g}), which the earlier spike found unreliable; treat matches and diffs on glory-dependent slots (stichera count, saint apolytikion, dismissal) accordingly.")
    if not f["in_slice"]:
        L.append(f"- Outside implemented Rules: {'; '.join(f['slice_reasons'])}. Date-dependent Rules are withheld, so those slots are missing.")
    L.append("")

    L.append("## Attention")
    n = 0
    for slot, meta, res in r.slots:
        notes = []
        for name, src in (("ANCA", anca), ("DCS", dcs)):
            c = src.get(slot)
            if c and c.state == "diff":
                notes.append(f"{name} {c.cls}: {'; '.join(c.details)}")
            if c and c.state == "key_only":
                notes.append(f"{name} has {_attrs(c.key)} but there is no Rule")
        if res.status == "missing":
            notes.append(f"no Rule resolved ({_cite(res)})")
        if res.status == "inferred":
            notes.append("inferred Rule (not stated in a Source)")
        if res.rule and res.rule.get("conflict"):
            notes.append(f"open Source conflict with {', '.join('`'+x+'`' for x in res.rule['conflict']['with'])}")
        for x in notes:
            L.append(f"- `{slot}`: {x}")
            n += 1
    if not n:
        L.append("- none")
    L.append("")

    L.append("## Slot detail")
    L.append("| Slot | Chosen | Rule · status | Source / locator | ANCA | DCS |")
    L.append("|---|---|---|---|---|---|")
    for slot, meta, res in r.slots:
        def cell(src):
            c = src.get(slot)
            if c is None:
                return "not compared"
            v = SYM[c.state] + (f" ({_attrs(c.key)})" if c.key and c.state in ("match", "diff", "key_only") else "")
            if c.state == "diff":
                v += f" [{c.cls}]: {'; '.join(c.details)}"
            return v
        rule = f"`{res.rule_id}` · {res.status} · tier {res.rule['tier']}" if res.rule else "none · missing"
        if res.shadowed:
            rule += f" (shadows {', '.join('`'+x+'`' for x in res.shadowed)})"
        L.append(f"| `{slot}` | {_fill(res)} | {rule} | {_cite(res)} | {cell(anca)} | {cell(dcs)} |")
    L.append("")

    L.append("## Calendar facts used")
    for k in ("date", "tone", "eothinon", "desig", "desig_g", "principal_name", "saint_has_glory", "glory_source",
              "epistle_owner", "epistle_ref", "gospel_ref", "season", "in_slice"):
        L.append(f"- {k}: {f[k]}")
    L.append("")

    L.append("## Comparison sources")
    for name in ("anca", "dcs"):
        if name not in r.comparisons:
            L.append(f"- {name.upper()}: not requested")
            continue
        ki = r.key_info[name]
        L.append(f"- {name.upper()}: {'; '.join(ki['used']) if ki['used'] else 'no key found'}" + (f" ({'; '.join(ki['notes'])})" if ki["notes"] else ""))
    L.append("- UK: comparison uses Rules that ignore UK-origin commemorations, so UK additions (e.g. in the dismissal) never count as differences.")
    L.append("- ANCA `liturgy.prokeimenon` is checked only via the Epistle owner printed in the key (circular); `liturgy.alleluia` is not printed by ANCA.")
    L.append("")
    L.append("Source authority: Typikon > ANCA > DCS > other Typika. Notation: `ours` = generated, ANCA/DCS = key value.")
    return "\n".join(L) + "\n"


def summary_line(r) -> str:
    b = len(gate(r))
    parts = []
    for name, src in r.comparisons.items():
        m = sum(1 for c in src.values() if c.state == "match")
        d = sum(1 for c in src.values() if c.state == "diff")
        parts.append(f"{name.upper()} {m} match/{d} diff")
    miss = sum(1 for *_, x in r.slots if x.status == "missing")
    return f"{len(r.slots)} slots, {miss} missing; " + "".join(x + "; " for x in parts) + f"{'BLOCKED: ' + str(b) if b else 'no blocking diffs'}"
