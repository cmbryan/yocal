"""Assemble one Service: facts -> Rules -> resolved slots -> comparison against the Answer keys."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

from . import anca, calfacts, compare as cmp, dcs
from .rules import apply_db, evaluate, load_catalogue

SERVICES = ("vespers", "matins", "liturgy", "agape")  # agape = Agape Vespers, Sunday evening of Pascha only


class OutOfScope(Exception):
    pass


@dataclass
class Result:
    service: str
    service_date: dt.date
    facts: dict
    slots: list  # ordered [(slot_id, meta, Resolution)]
    comparisons: dict = field(default_factory=dict)  # source -> {slot: Cmp}
    key_info: dict = field(default_factory=dict)  # source -> dict(used=[], notes=[], present=bool)
    catalogue: tuple = ()


def check_scope(service: str, date: dt.date):
    if service not in SERVICES:
        raise OutOfScope(f"unknown service {service!r}; choose from {', '.join(SERVICES)}")
    ld = calfacts.liturgical_date(service, date)
    if service == "agape":
        if date != calfacts.pascha(date.year):
            raise OutOfScope(f"{date} agape: Agape Vespers is served on Pascha Sunday only ({calfacts.pascha(date.year)} in {date.year})")
        return
    eve_of_feast = ld.strftime("%m-%d") in calfacts.FIXED_MAJOR or bool(calfacts.major_feast(ld)[0])  # feast day itself (Vespers: the feast the eve precedes)
    if service == "vespers":
        ok = date.weekday() == 5 or eve_of_feast
    else:
        ok = date.weekday() == 6 or eve_of_feast
    if not ok:
        raise OutOfScope(f"{date} {service}: only Saturday Great Vespers, Sunday Matins/Liturgy and Major feasts are in scope")


def build(service: str, date: dt.date, db_path: str = calfacts.DEFAULT_DB, strip_uk: bool = False) -> Result:
    check_scope(service, date)
    rules, sources, slots = load_catalogue()
    facts = calfacts.load_facts(date, service, db_path)
    if strip_uk:
        facts["uk_commem"] = ""
    ids = [s for s, m in slots.items() if m["service"] == service and (not m.get("only") or facts.get(m["only"]))]  # `only`: fact gating feast-only slots
    for s in [s for s in ids if slots[s].get("after")]:  # `after`: document position ('^' = first)
        ids.remove(s)
        a = slots[s]["after"]
        if a not in ids and a != "^":
            a = slots[s].get("after_or", a)  # anchor slot absent (feast-only): fall back
        ids.insert(0 if a == "^" else ids.index(a) + 1 if a in ids else len(ids), s)
    res = evaluate(rules, facts, ids)
    apply_db(res, facts, slots)
    ordered = [(s, slots[s], res[s]) for s in ids]
    return Result(service, date, facts, ordered, catalogue=(rules, sources, slots))


def compare_keys(r: Result, cache: str, offline: bool = False, dcs_on: bool = True, anca_on: bool = True):
    log = cmp.load_divergence()
    srcs = []
    if anca_on:
        srcs.append(("anca", anca.key_for))
    if dcs_on and r.service != "agape":  # DCS has no Agape Vespers page
        srcs.append(("dcs", dcs.key_for))
    for name, fn in srcs:
        try:
            key, used, notes = fn(r.service, r.service_date, cache, offline)
        except Exception as e:  # network / parse trouble must not kill the build: report as no key
            key, used, notes = {}, [], [f"{name.upper()} lookup failed: {type(e).__name__}: {e}"]
        r.key_info[name] = dict(used=used, notes=notes, present=bool(key), key=key)
        r.comparisons[name] = {s: cmp.compare(res, key, name, r.facts, r.service, log) for s, _, res in r.slots}
    return r
