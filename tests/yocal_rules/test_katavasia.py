"""Sunday Matins katavasia by the Typikon schedule (data/rules/matins_katavasia.yaml, Gloss. p.576-577)."""
import datetime as dt
import os

import pytest

from yocal_rules import assemble, hymns

needs_db = pytest.mark.skipif(not os.path.exists("db/yocal/YOCal_Master.db"), reason="needs calendar DB")


def kat(date):
    r = assemble.build("matins", dt.date.fromisoformat(date))
    for s, _, x in r.slots:
        if s == "matins.katavasia":
            return [h.id for h in hymns.for_slot(s, x, r.facts)]
    return None


@needs_db
@pytest.mark.parametrize("date,expect", [
    ("2026-11-22", ["kat/nativity1"]),             # Entrance afterfeast: first katavasia of the Nativity from Nov 21
    ("2026-11-15", ["kat/presentation_theotokos"]),  # Nov 8-20
    ("2026-10-25", ["kat/theotokos"]),             # Sep 22 - Nov 7
    ("2026-09-13", ["kat/cross"]),                 # Sep 1-21
    ("2026-08-23", ["kat/dormition"]),             # Aug 15-23
])
def test_sunday_katavasia_follows_schedule(date, expect):
    assert kat(date) == expect


@needs_db
def test_feast_day_keeps_its_own_katavasia_rule():
    r = assemble.build("matins", dt.date(2026, 11, 21))
    m = {s: x for s, _, x in r.slots}
    assert m["matins.katavasia"].rule["id"] == "mf.mat.katavasia.nativity"  # feast Rule (tier -10) wins; no hymn ids (parts only)


@needs_db
def test_entrance_eve_vespers_lists_readings():
    r = assemble.build("vespers", dt.date(2026, 11, 20))
    m = {s: x for s, _, x in r.slots}
    assert m["vespers.readings"].fill["parts"] == ["Exodus 40:1-5, 8-9, 14, 28-29", "3 Kingdoms 8:1, 3-7, 9-11", "Ezekiel 43:27-44:4"]


@needs_db
def test_sunday_hypakoe_and_canon():
    r = assemble.build("matins", dt.date(2026, 11, 22))
    m = {s: x for s, _, x in r.slots}
    assert [h.id for h in hymns.for_slot("matins.hypakoe", m["matins.hypakoe"], r.facts)] == ["oct/t8/sun/hypakoe"]
    assert m["matins.canon"].rule["id"] == "mat.canon.katavasiae_only" and hymns.for_slot("matins.canon", m["matins.canon"], r.facts) == []
