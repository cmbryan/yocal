"""Festal Liturgy hymns on Sundays (data/rules/festal_hymns.yaml): antiphons, entrance hymn, trisagion, megalynarion -> hymn ids."""
import datetime as dt
import os

import pytest

from yocal_rules import assemble, hymns

needs_db = pytest.mark.skipif(not os.path.exists("db/yocal/YOCal_Master.db"), reason="needs calendar DB")
SLOTS = ("liturgy.antiphons", "liturgy.eisodikon", "liturgy.trisagion", "liturgy.megalynarion")


def ids(date):
    r = assemble.build("liturgy", dt.date.fromisoformat(date))
    out = {}
    for s, _, x in r.slots:
        if s in SLOTS:
            hs = hymns.for_slot(s, x, r.facts)
            out[s.split(".")[1]] = None if hs is None else [h.id for h in hs]
    return out


@needs_db
@pytest.mark.parametrize("date,expect", [
    ("2026-11-15", {"antiphons": [], "eisodikon": [], "trisagion": [], "megalynarion": []}),                     # ordinary Sunday: booklet
    ("2026-11-22", {"antiphons": ["men/11-21/antiphon1", "men/11-21/antiphon2", "men/11-21/antiphon3"], "eisodikon": [], "megalynarion": []}),
    ("2023-08-13", {"eisodikon": ["men/08-06/eisodikon"], "megalynarion": ["men/08-06/megalynarion"]}),          # Lord's leavetaking
    ("2026-03-15", {"antiphons": ["mov/-28/antiphon1", "mov/-28/antiphon2", "mov/-28/antiphon3"], "trisagion": ["lit/trisagion/cross"],
                    "megalynarion": ["lit/megalynarion/basil"]}),                                                 # Lent 3
    ("2026-04-19", {"antiphons": ["mov/0/antiphon1", "mov/0/antiphon2", "mov/0/antiphon3"], "eisodikon": ["mov/0/eisodikon"],
                    "trisagion": [], "megalynarion": ["mov/7/megalynarion"]}),                                    # Thomas Sunday
    ("2026-05-03", {"megalynarion": ["mov/0/megalynarion"]}),                                                     # Paralytic
    ("2026-05-24", {"antiphons": ["mov/39/antiphon1", "mov/39/antiphon2", "mov/39/antiphon3"], "megalynarion": []}),  # Ascension afterfeast
    ("2026-05-31", {"eisodikon": ["mov/49/eisodikon"], "trisagion": ["lit/trisagion/baptized"], "megalynarion": ["mov/49/megalynarion"]}),
    ("2026-04-05", {"eisodikon": ["mov/-7/eisodikon"], "megalynarion": ["mov/-7/megalynarion"]}),                 # Palm Sunday
])
def test_sunday_festal_hymns(date, expect):
    got = ids(date)
    for k, v in expect.items():
        assert got[k] == v, (date, k, got[k])


@needs_db
def test_refrains():
    r = assemble.build("liturgy", dt.date(2026, 8, 9))  # Transfiguration afterfeast: 2nd refrain of the feast, 3rd its troparion
    hs = hymns.for_slot("liturgy.antiphons", {s: x for s, _, x in r.slots}["liturgy.antiphons"], r.facts)
    assert hs[1].meta["refrain"] == "lit/refrain2/transfiguration" and hs[2].meta["refrain"] == "men/08-06/apolytikion"
    r = assemble.build("liturgy", dt.date(2026, 11, 22))  # Theotokos afterfeast: booklet 'risen from the dead'
    hs = hymns.for_slot("liturgy.antiphons", {s: x for s, _, x in r.slots}["liturgy.antiphons"], r.facts)
    assert hs[1].meta["refrain"] is None
    r = assemble.build("liturgy", dt.date(2026, 4, 12))   # Pascha: 3rd refrain "Christ is risen"
    hs = hymns.for_slot("liturgy.antiphons", {s: x for s, _, x in r.slots}["liturgy.antiphons"], r.facts)
    assert hs[2].meta["refrain"] == "mov/0/troparion"


def test_festal_dcs_keys_roundtrip():
    f = hymns.id_from_dcs
    assert f("menaion.verses", "psLI.m11.d21.antiphon3.v1.text") == "men/11-21/antiphon3"
    assert f("menaion.verses", "psLI.m11.d21.antiphon3.v2.text") is None  # only the first verse names the hymn
    assert f("movable.verses", "psLI.pe.d071.entrance.v1.text") == "mov/0/eisodikon"
    assert f("liturgical.verses", "psLI.trisagionbaptized.text") == "lit/trisagion/baptized"
    assert f("pe.d071", "peMA.Ode9C1MKa.text") == "mov/0/megalynarion" and f("he.h.m1", "heHE.FotizouFotizou.text") == ""
    assert hymns.dcs_keys("lit/refrain2/presentation") == [["prayers|pr.antiphon2.meeting.text"]]
    assert hymns.dcs_keys("mov/-28/antiphon2")[0][0] == "movable.verses|psLI.tr.d043.antiphon2.v1.text"
