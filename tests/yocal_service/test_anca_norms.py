"""ANCA-following norms (parish decision 2026-11-12): saint hymn text by DCS self-label, different-hymn conflicts, communion commons."""
import datetime as dt
import os

import pytest

from yocal_rules import assemble, hymns
from yocal_service import anca_texts, texts

DB = os.path.exists("db/yocal/YOCal_Master.db")


@pytest.fixture
def tx(tmp_path, monkeypatch):
    monkeypatch.setenv("YOCAL_SOURCES", str(tmp_path / "sources"))
    t = texts.Texts(str(tmp_path / "sources"))
    texts.put(t, "dcs", "me.m01.d15|meVE.Apolytikion1.text", "From infancy you loved the Lord.", "GOA DCS 2027-01-15 li", "2027-01-15",
              label="Apolytikion. For St. John.")
    texts.put(t, "anca", "men/01-15/apolytikion", "The barren wilderness thou didst make fertile.", "ANCA 2023-01-15", "2023-01-15")
    texts.put(t, "dcs", "menaion.verses|psLI.m12.d09.prokeimenon.v1.text", "The righteous man shall be glad in the Lord.", "x", "2026-12-09")
    texts.put(t, "dcs", "menaion.verses|psLI.m12.d09.prokeimenon.v2.text", "Hear my voice, O God.", "x", "2026-12-09")
    texts.put(t, "anca", "men/12-09/prokeimenon", "God is wondrous in His saints.\n\nBless God in the congregations.", "ANCA 2018-12-09", "2018-12-09")
    texts.put(t, "dcs", "me.m12.d06|meVE.Apolytikion1.text", "A rule of faith are you, and an icon of gentleness.", "x", "2026-12-06")
    texts.put(t, "anca", "men/12-06/apolytikion", "Thy works of justice did reveal thee as a rule of faith, an icon of gentleness.", "y", "2025-12-06")
    return t


def test_dcs_copy_labelled_for_another_saint_is_not_used(tx):
    principal = lambda mmdd: {"01-15": "Saint Paul of Thebes"}.get(mmdd, "")
    assert texts.get(tx, "men/01-15/apolytikion", parish={}, principal=principal)["source"] == "anca"
    assert texts._dcs(tx, "men/01-15/apolytikion", principal) is None
    assert texts._dcs(tx, "men/01-15/apolytikion", lambda m: "John the Hut-dweller")  # label agrees: DCS copy usable
    assert texts.other_owner("men/01-15/apolytikion", "Apolytikion. For the Forefeast.", principal) is None  # names nobody


def test_different_hymn_follows_anca_same_hymn_keeps_dcs_wording(tx):
    t = texts.get(tx, "men/12-09/prokeimenon", parish={}, principal=None)
    assert t["source"] == "anca" and t["parts"][0] == "God is wondrous in His saints."
    assert texts.get(tx, "men/12-06/apolytikion", parish={}, principal=None)["source"] == "dcs"  # two translations of one hymn


def test_feb1_forefeast_kontakion_has_no_dcs_copy():
    assert hymns.dcs_keys("men/02-01/kontakion") == []


def test_common_communion_by_text():
    f = anca_texts.common_communion
    assert f("His sound hath gone forth into all the earth") == "lit/communion/common/apostle"
    assert f("Their sound hath gone forth into all the earth") == "lit/communion/common/apostles"
    assert f("In everlasting remembrance shall the righteous be") == "lit/communion/common/remembrance"
    assert f("He maketh his angels spirits") == "lit/communion/common/angels"
    assert f("Praise the Lord from the heavens") is None


@pytest.mark.skipif(not DB, reason="needs calendar DB")
@pytest.mark.parametrize("date,slot,rule,ids", [
    ("2025-11-30", "liturgy.communion", "lit.comm.saint.apostle", ["lit/communion/common/apostle"]),          # Andrew
    ("2025-06-29", "liturgy.communion", "lit.comm.saint.apostles", ["lit/communion/common/apostles"]),        # Peter and Paul
    ("2022-01-30", "liturgy.communion", "lit.comm.saint.apostles", ["lit/communion/common/apostles"]),        # Three Great Hierarchs (regex fix)
    ("2021-08-29", "liturgy.communion", "lit.comm.saint.forerunner", ["lit/communion/common/remembrance"]),   # Beheading
    ("2026-11-08", "liturgy.communion", "lit.comm.archangels", ["lit/communion/common/angels"]),
    ("2020-12-27", "liturgy.communion", "lit.comm.sunday", ["lit/communion/sunday"]),                         # Stephen: not in the Typikon list
    ("2018-11-11", "liturgy.prokeimenon", "lit.prokeimenon.menas_tone", ["lit/sun/t7/prokeimenon"]),
    ("2025-02-09", "liturgy.prokeimenon", "lit.prokeimenon.presentation_leavetaking", ["men/02-02/prokeimenon"]),
    ("2025-11-09", "liturgy.prokeimenon", "lit.prokeimenon.saint_by_anca", ["men/11-09/prokeimenon"]),
    ("2025-09-21", "liturgy.prokeimenon", "lit.prokeimenon.after_elevation_tone.2024", ["lit/sun/t6/prokeimenon"]),
    ("2021-09-19", "liturgy.prokeimenon", "lit.prokeimenon.named_sunday", ["named/after_elevation/prokeimenon"]),
])
def test_anca_norm_rules(date, slot, rule, ids):
    r = assemble.build("liturgy", dt.date.fromisoformat(date))
    x = dict((s, x) for s, _, x in r.slots)[slot]
    assert x.rule_id == rule and [h.id for h in hymns.for_slot(slot, x, r.facts)] == ids
