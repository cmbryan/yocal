"""Issue #88: vespers.litia -> Lity hymns of the feast + the fixed Artoklasia hymns (hymns.litia). No network."""
import datetime as dt
import os

import pytest

from yocal_rules import assemble, calfacts, hymns

needs_db = pytest.mark.skipif(not os.path.exists(calfacts.DEFAULT_DB), reason="calendar DB not built")
ARTOKLASIA = ["lit/vespers/theotoke_parthene", "lit/vespers/artoklasia_ps33"]


def litia(date):
    r = assemble.build("vespers", dt.date.fromisoformat(date))
    res = {s: x for s, _, x in r.slots}["vespers.litia"]
    return res, hymns.for_slot("vespers.litia", res, r.facts)


@needs_db
def test_entrance_eve_lity_hymns_then_artoklasia():
    res, hs = litia("2026-11-20")                                    # Friday eve of the Entrance (parish booklet 2026-11-20)
    assert res.fill["litia"] is True
    assert [h.id for h in hs] == ["men/11-21/lity1", "men/11-21/lity2", "men/11-21/lity3", "men/11-21/doxastikonlity"] + ARTOKLASIA
    rich = hs[-1]
    assert rich.meta == {"priest": 1, "choir": 2} and rich.kind == "artoklasia"


@needs_db
def test_feast_with_separate_glory_and_now_and_count_not_located():
    _, hs = litia("2026-08-05")                                      # Transfiguration eve: idiomela count not in hymns.yaml `lity:`
    assert [h.id for h in hs] == ["men/08-06/lity", "men/08-06/doxastikonlity", "men/08-06/doxastikonlitynow"] + ARTOKLASIA
    _, asc = litia("2026-05-20")                                     # Ascension (movable): base from the calendar
    assert asc[0].id == "mov/39/lity" and asc[1].id == "mov/39/doxastikonlity"


@needs_db
def test_eve_without_lity_has_no_lity_hymns():
    res, hs = litia("2025-12-24")                                    # Nativity on a weekday: Lity at the Midnight Service (mf.nat.ves.litia)
    assert res.fill["litia"] is False and hs == []


def test_lity_dcs_keys():
    assert hymns.dcs_keys("men/01-06/doxastikonlity") == [["me.m01.d06|meVE.LityGlory.text"], ["me.m01.d06|meVE.LityBoth.text"]]
    assert hymns.dcs_keys("men/01-06/doxastikonlitynow") == [["me.m01.d06|meVE.LityBoth.text"]]
    assert hymns.dcs_keys("lit/vespers/theotoke_parthene") == [["ho.ho10|hoVE.LentApolytikion1.text"]]
    assert hymns.dcs_keys("lit/vespers/artoklasia_ps33") == [["liturgical.verses|psVE.breadhymn.v1.text"]]
    assert hymns.id_from_dcs("liturgical.verses", "psVE.breadhymn.v1.text") == "lit/vespers/artoklasia_ps33"


def test_litia_without_feast_is_a_gap():
    assert hymns.litia({"litia": True}, {}) is None                  # no feast base: no ids (gap), never guessed
    assert hymns.litia({"litia": False}, {}) == []
