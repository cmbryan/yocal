"""Rule loading, validation and evaluation (slot-grain Rules, specificity tiers, closed context facts).

Lowest tier number wins; an equal-tier tie among matching Rules is a build error. A slot with no matching
Rule resolves to `missing` (never dropped).
"""
from __future__ import annotations

import fnmatch
import glob
import os
from dataclasses import dataclass, field

import yaml

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
NON_RULE_FILES = ("sources.yaml", "slots.yaml")
STATUSES = ("explicit", "inferred", "missing")
_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# closed vocabulary of context-fact predicates
PREDS = {
    "sunday": lambda f, a: f["weekday"] == "Sunday",
    "sunday_eve": lambda f, a: f["weekday"] == "Sunday",  # liturgical-day unit: the Saturday eve belongs to Sunday
    "in_slice": lambda f, a: f["in_slice"],
    "menaion_date_is": lambda f, a: f["mmdd"] == a[0],
    "date_between": lambda f, a: a[0] <= f["mmdd"] <= a[1],
    "not_date_between": lambda f, a: not (a[0] <= f["mmdd"] <= a[1]),
    "saint_in_calendar": lambda f, a: f["saint_in_calendar"],
    "no_saint_in_calendar": lambda f, a: not f["saint_in_calendar"],
    "saint_has_glory": lambda f, a: f["saint_has_glory"] is True,
    "saint_no_glory": lambda f, a: f["saint_has_glory"] is False,
    "glory_unknown": lambda f, a: f["saint_has_glory"] is None,
    "desig_contains": lambda f, a: any(x in f"{f['desig']} {f['desig_g']}" for x in a),
    "archangel_feast": lambda f, a: f["archangel_feast"],
    # ANCA reads the Sunday's own Epistle/prokeimenon (not the saint's) on these Sundays
    "anca_sunday_epistle": lambda f, a: f["all_saints_sunday"] or f["season"] == "triodion" or f["leavetaking"],
    "named_sunday_is": lambda f, a: f["named_sunday"] in a,
    "two_sets_of_3": lambda f, a: f["two_sets_of_3"],
    "bb_rank_in": lambda f, a: f["bb_rank"] in a,          # Bp Basil rank of the Menaion date (POLYELEOS, DOXOLOGY, VIGIL, ...)
    "bb_rank_not_in": lambda f, a: f["bb_rank"] not in a,
    "saint_lauds": lambda f, a: f["saint_lauds"] > 0,      # ALWB records Lauds stichera for the date's main commemoration
    "no_saint_lauds": lambda f, a: f["saint_lauds"] == 0,
    "leavetaking": lambda f, a: f["leavetaking"],
    "basil": lambda f, a: f["basil"],
    "not_basil": lambda f, a: not f["basil"],
    "date_in": lambda f, a: f["mmdd"] in a,
    "year_at_least": lambda f, a: f["year"] >= a[0],
    "pascha_days_between": lambda f, a: a[0] <= f["pascha_days"] <= a[1],  # days since this calendar year's Pascha (Jan-Feb dates are negative)
    # a Menaion commemoration or fore/after-feast shares the day (DB major_commem or fore_after set)
    "menaion_coincidence": lambda f, a: f["saint_in_calendar"] or bool(f.get("fore_after")),
    # fore/after-feast periods (data/rules/fore_after.yaml): feast_period is 'kind:feast', e.g. 'afterfeast:dormition'; args are fnmatch patterns
    "feast_period_in": lambda f, a: any(fnmatch.fnmatchcase(f["feast_period"], p) for p in a),
    "fore_after_contains": lambda f, a: any(x.lower() in f["fore_after"].lower() for x in a),
    "season_is": lambda f, a: f["season"] in a,
    "feast_period_saint": lambda f, a: f["feast_period_saint"],
    "no_feast_period_saint": lambda f, a: not f["feast_period_saint"],
    "not_date_in": lambda f, a: f["mmdd"] not in a,  # Pentecostarion: dates with their own Ch V coincidence order
    "epistle_owner_is": lambda f, a: f["epistle_owner"] in a,
    # Major feasts (data/rules/major_feasts.yaml): normalised id (calfacts.MAJOR_FIXED / MAJOR_MOVABLE), class, weekday coincidence
    "major_feast_is": lambda f, a: f.get("major_feast", "") in a,
    "major_feast_class_is": lambda f, a: f.get("major_feast_class", "") in a,
    # Mon-Sat (Vespers: the eve of it) under the weekday order; Nativity/Theophany on a Monday have their own order (Typikon p.145, p.174)
    "feast_on_weekday": lambda f, a: bool(f.get("major_feast")) and f["weekday"] != "Sunday"
                                     and not (f["major_feast"] in ("nativity", "theophany") and f["weekday"] == "Monday"),
    "feast_on_sunday": lambda f, a: bool(f.get("major_feast")) and f["weekday"] == "Sunday",
    # Sunday order of a fixed Major feast (data/rules/major_feasts_sunday.yaml): feast id in args, ordinary season (Presentation on a Triodion Sunday has its own order, p.220)
    "sunday_feast_order": lambda f, a: f["weekday"] == "Sunday" and f.get("major_feast", "") in a and f["season"] == "ordinary",
    "weekday_in": lambda f, a: f["weekday"] in a,  # weekday of the liturgical day (Vespers: the day after the eve)
    "eve_weekday_in": lambda f, a: _WEEK[(_WEEK.index(f["weekday"]) - 1) % 7] in a,  # weekday of the eve (the day before)
    "eve_basil": lambda f, a: f.get("eve_basil", False),  # the eve's DB row has the Liturgy of St Basil (Vesperal Liturgy)
}


class RuleError(Exception):
    pass


@dataclass
class Resolution:
    slot: str
    status: str  # explicit | inferred | missing
    rule: dict | None
    fill: dict = field(default_factory=dict)
    shadowed: list = field(default_factory=list)  # ids of lower-priority matching Rules
    note: str = ""

    @property
    def rule_id(self):
        return self.rule["id"] if self.rule else None


def load_catalogue(data_dir: str = DATA):
    rdir = os.path.join(data_dir, "rules")
    sources = yaml.safe_load(open(os.path.join(rdir, "sources.yaml"), encoding="utf-8"))
    slots = yaml.safe_load(open(os.path.join(rdir, "slots.yaml"), encoding="utf-8"))
    rules = []
    for f in sorted(glob.glob(os.path.join(rdir, "*.yaml"))):
        if os.path.basename(f) in NON_RULE_FILES:
            continue
        rules += yaml.safe_load(open(f, encoding="utf-8"))
    errs = validate(rules, sources, slots)
    if errs:
        raise RuleError("; ".join(errs))
    return rules, sources, slots


def validate(rules, sources, slots):
    errs, ids = [], set()
    for r in rules:
        rid = r.get("id", "?")
        if rid in ids:
            errs.append(f"dup id {rid}")
        ids.add(rid)
        if r["source"] not in sources:
            errs.append(f"{rid}: unknown source {r['source']}")
        if r["slot"] not in slots:
            errs.append(f"{rid}: unknown slot {r['slot']}")
        for w in r.get("when", []):
            if w["pred"] not in PREDS:
                errs.append(f"{rid}: unknown predicate {w['pred']}")
        st = r["status"]
        if st not in STATUSES:
            errs.append(f"{rid}: bad status {st}")
        if st == "explicit" and "evidence" in r:
            errs.append(f"{rid}: explicit with evidence")
        if st == "inferred" and "evidence" not in r:
            errs.append(f"{rid}: inferred without evidence")
        if st == "missing" and "ticket" not in r:
            errs.append(f"{rid}: missing without ticket")
    return errs


def _resolve(fill, facts):
    return {k: (facts[v[1:]] if isinstance(v, str) and v.startswith("$") else v) for k, v in fill.items()}


def evaluate(rules, facts, slot_ids):
    """-> {slot: Resolution} for every requested slot."""
    by = {s: [] for s in slot_ids}
    for r in rules:
        if r["slot"] in by and all(PREDS[w["pred"]](facts, w.get("args", [])) for w in r.get("when", [])):
            by[r["slot"]].append(r)
    out = {}
    for slot, rs in by.items():
        if not rs:
            out[slot] = Resolution(slot, "missing", None, note="no Rule matches this context")
            continue
        best = min(r["tier"] for r in rs)
        top = [r for r in rs if r["tier"] == best]
        if len(top) > 1:
            raise RuleError(f"tier tie on {slot}: {', '.join(r['id'] for r in top)}")
        w = top[0]
        out[slot] = Resolution(slot, w["status"], w, _resolve(w["fill"], facts),
                               [r["id"] for r in rs if r is not w])
    return out
