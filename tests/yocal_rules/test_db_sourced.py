"""DB-sourced slots: the YOCal DB decides readings, eothinon and Liturgy author by construction (never a Rule)."""
import datetime as dt
import os
import sqlite3

import pytest

from yocal_rules import assemble, calfacts
from yocal_rules.rules import RuleError, apply_db, load_catalogue, validate

needs_db = pytest.mark.skipif(not os.path.exists(calfacts.DEFAULT_DB), reason="calendar DB not built")


def test_no_rule_fills_a_db_attribute():
    rules, sources, slots = load_catalogue()  # load_catalogue validates
    db_slots = {s: m["db"] for s, m in slots.items() if m.get("db")}
    assert {"liturgy.epistle", "liturgy.gospel", "matins.eothinon_gospel", "liturgy.author", "agape.gospel"} <= set(db_slots)
    for r in rules:
        for a, v in r.get("fill", {}).items():
            if a in db_slots.get(r["slot"], {}) and v is not None:
                assert a == "owner" and v not in ("sunday", "saint"), (r["id"], a)


def test_validate_rejects_rule_that_fills_db_attribute():
    rules, sources, slots = load_catalogue()
    bad = dict(id="x", slot="liturgy.epistle", tier=0, when=[], fill={"ref": "Acts 1:1"}, source="typikon", locator="l", status="explicit")
    assert any("DB-sourced" in e for e in validate(rules + [bad], sources, slots))


@needs_db
def test_sunday_slots_equal_db_values_2024_2026():
    con = sqlite3.connect(calfacts.DEFAULT_DB)
    d = dt.date(2024, 1, 7)
    n = 0
    while d.year <= 2026:
        f = calfacts.load_facts(d, "liturgy")
        if f["in_slice"] and not f["major_feast"]:
            got = {s: x for s, _, x in assemble.build("liturgy", d).slots}
            assert got["liturgy.epistle"].fill["ref"] == f["epistle_ref"], d
            assert got["liturgy.gospel"].fill["ref"] == f["gospel_ref"], d
            assert got["liturgy.author"].fill["author"] == ("Basil the Great" if f["basil"] else "John Chrysostom"), d
            assert got["liturgy.epistle"].rule_id == "db.liturgy.epistle" or got["liturgy.epistle"].fill["owner"] in ("sunday", "saint", "feast"), d
            m = assemble.build("matins", d)
            e = {s: x for s, _, x in m.slots}["matins.eothinon_gospel"]
            assert e.fill.get("number") == f["eothinon"] or e.fill.get("ref") == f["feast_matins_gospel_ref"], d
            n += 1
        d += dt.timedelta(days=7)
    assert n > 50


@needs_db
def test_annunciation_lent_sunday_author_follows_db():
    d = dt.date(2018, 3, 25)  # DB basil flag; Typikon/ANCA say Chrysostom (logged divergence)
    f = calfacts.load_facts(d, "liturgy")
    assert f["liturgy_author"] == "Basil the Great"


@needs_db
def test_matins_gospel_of_the_feast_from_db_lection():
    for d, ref in [(dt.date(2026, 4, 5), "Matthew 21:1-11,15-17"), (dt.date(2026, 5, 31), "John 20:19-23"), (dt.date(2026, 4, 12), "Mark 16:1-8")]:
        e = {s: x for s, _, x in assemble.build("matins", d).slots}["matins.eothinon_gospel"]
        assert e.fill["ref"] == ref and e.fill["number"] is None, d


@needs_db
def test_agape_gospel_and_pascha_from_db():
    assert calfacts.pascha(2026) == dt.date(2026, 4, 12)
    a = {s: x for s, _, x in assemble.build("agape", dt.date(2026, 4, 12)).slots}["agape.gospel"]
    assert a.fill["ref"].startswith("John 20:19")


def test_apply_db_gives_missing_slot_a_db_resolution():
    from yocal_rules.rules import Resolution
    res = {"liturgy.gospel": Resolution("liturgy.gospel", "missing", None)}
    apply_db(res, {"gospel_ref": "Luke 1:1"}, {"liturgy.gospel": {"db": {"ref": "gospel_ref"}}})
    r = res["liturgy.gospel"]
    assert r.status == "explicit" and r.rule_id == "db.liturgy.gospel" and r.fill == {"ref": "Luke 1:1"}
