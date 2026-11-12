import datetime as dt
import os

import pytest

from yocal_rules import hymns
from yocal_rules.rules import Resolution

F = {"mmdd": "11-15", "menaion_key": "11-15", "tone": 7, "principal_name": "St X", "weekday": "Sunday", "desig": "24th after Pentecost",
     "desig_g": "8th of Luke", "major_feast": "", "feast_period": "", "named_sunday": None, "liturgy_author": "John Chrysostom", "dismissal_saint": "St X"}


def R(slot, fill, status="explicit"):
    return Resolution(slot, status, {"id": "r"}, fill)


def ids(slot, fill, **facts):
    return [h.id for h in hymns.for_slot(slot, R(slot, fill), {**F, **facts}) or []]


def test_ordinary_sunday_ids():
    assert ids("liturgy.apolytikia", {"res_tone": 7, "saint": True}) == ["oct/t7/sun/apolytikion", "men/11-15/apolytikion"]
    assert ids("liturgy.apolytikia", {"res_tone": 7, "saint": True}, menaion_key="11-14") == ["oct/t7/sun/apolytikion", "men/11-14/apolytikion"]  # transferred saint
    assert ids("liturgy.kontakion", {"kind": "ordinary_theotokos", "tone": 2}) == ["hor/kontakion/protection"]
    assert ids("liturgy.prokeimenon", {"owner": "sunday", "proper": False}) == ["lit/sun/t7/prokeimenon"]
    assert ids("liturgy.prokeimenon", {"owner": "saint"}) == ["men/11-15/prokeimenon"]
    assert ids("liturgy.prokeimenon", {"owner": "sunday", "proper": True}, desig="Sunday of the Holy Forefathers") == ["named/forefathers/prokeimenon"]
    assert ids("liturgy.apolytikia", {"res_tone": 8, "saint": True, "feast": True}, feast_period="afterfeast:entrance_theotokos")[1] == "men/11-21/apolytikion"
    assert ids("liturgy.alleluia", {"tone": 7}) == ["lit/sun/t7/alleluia"]
    assert ids("liturgy.communion", {"kind": "praise_the_lord"}) == ["lit/communion/sunday"]


def test_feast_ids_follow_calendar():
    assert ids("liturgy.communion", {"kind": "feast"}, major_feast="ascension") == ["mov/39/communion"]
    assert ids("liturgy.communion", {"kind": "feast"}, feast_period="afterfeast:dormition") == ["men/08-15/communion"]
    assert ids("liturgy.kontakion", {"kind": "dormition", "tone": 2}) == ["men/08-15/kontakion"]
    assert ids("liturgy.apolytikia", {"res_tone": 2, "saint": True, "feast": True}, feast_period="afterfeast:dormition", fore_after="Afterfeast of the Dormition") == \
        ["oct/t2/sun/apolytikion", "men/08-15/apolytikion"]


def test_forefeast_takes_forefeast_troparion_and_named_sunday_its_own():
    assert ids("liturgy.apolytikia", {"res_tone": 4, "saint": True, "feast": True}, feast_period="forefeast:nativity")[1] == "men/12-20/apolytikion"
    assert ids("liturgy.apolytikia", {"res_tone": 3, "hymns": ["oct/t{tone}/sun/apolytikion", "named/{named}/apolytikion"]},
               tone=3, desig="Sunday of the Holy Forefathers") == ["oct/t3/sun/apolytikion", "named/forefathers/apolytikion"]


def test_explicit_hymns_on_rule_and_missing():
    fill = {"hymns": [{"id": "mov/{pascha_days}/apolytikion", "label": "Apolytikion of Thomas Sunday", "tone": 7}]}
    assert ids("liturgy.apolytikia", fill, pascha_days=7) == ["mov/7/apolytikion"]
    assert hymns.for_slot("liturgy.kontakion", R("liturgy.kontakion", {}, "missing"), F) is None
    assert hymns.for_slot("liturgy.apolytikia", R("liturgy.apolytikia", {"parts": ["free text"], "res_tone": None}), F) is None


def test_dcs_keys():
    assert hymns.dcs_keys("oct/t4/sun/apolytikion") == [["oc.m4.d1|ocVE.Apolytikion.text"]]
    assert hymns.dcs_keys("mov/0/kontakion")[0] == ["pe.d071|pe*.Kontakion1.text"]
    assert hymns.dcs_keys("men/01-01/apolytikion2") == [["me.m01.d01|me*.Apolytikion2.text"]]
    assert hymns.dcs_keys("mov/-70/kontakion")[0] == ["tr.d001|trMA.Kontakion0.text"]  # override first, then pattern
    assert hymns.dcs_keys("lit/sun/t2/prokeimenon")[0][:2] == ["liturgical.verses|psLI.sunday.m2.prokeimenon.v1.text", "liturgical.verses|psLI.sunday.m2.prokeimenon.v2.text"]


def test_dismissal_rules():
    d = hymns.dismissal(R("liturgy.dismissal", {"author": "John Chrysostom", "saint_named": True}), None, F)
    assert d["phrase"] == "he who rose from the dead" and d["saints"] == "St X"
    d = hymns.dismissal(R("liturgy.dismissal", {"author": "x", "saint_named": True, "named_as": "the Sunday's own commemoration"}), None, {**F, "desig_g": "Forefathers"})
    assert d["saints"] == "Forefathers"
    assert hymns.dismissal(R("liturgy.dismissal", {"author": "x", "saint_named": False}), None, F)["saints"] is None


@pytest.mark.skipif(not os.path.exists("db/yocal/YOCal_Master.db"), reason="needs calendar DB")
def test_sundays_to_2099_resolve_without_error():
    """Every Sunday Liturgy to 2099 builds; ordinary-season Sundays get hymn ids for every hymn slot."""
    from yocal_rules import assemble
    d, bad = dt.date(2026, 11, 15), []
    while d.year < 2100:
        r = assemble.build("liturgy", d)
        if r.facts["in_slice"] and r.facts["season"] == "ordinary":
            for s, _, x in r.slots:
                if s in hymns.SLOTS and hymns.for_slot(s, x, r.facts) is None:
                    bad.append((d.isoformat(), s, x.rule_id))
        d += dt.timedelta(weeks=1)
    assert not bad, bad[:20]


def test_id_from_dcs_roundtrip():
    f = hymns.id_from_dcs
    assert f("oc.m4.d1", "ocVE.Apolytikion.text") == "oct/t4/sun/apolytikion"
    assert f("me.m11.d21", "meMA.Kontakion1.text") == "men/11-21/kontakion"
    assert f("me.m01.d01", "meVE.Apolytikion2.text") == "men/01-01/apolytikion2"
    assert f("pe.d071", "peMA.Troparion.text") == "mov/0/troparion"
    assert f("tr.d063", "trVE.Apolytikion1.text") == "mov/-8/apolytikion"
    assert f("ho.ho07", "hoTY.Key0408.text") == "hor/kontakion/protection"
    assert f("tr.d056", "trMA.Kontakion11.text") == "men/03-25/kontakion" and f("tr.d056", "trMA.Kontakion12.text") == ""
    assert f("tr.d069", "trLI.CommunionHymn.text") is None  # pre-communion hymn at every Liturgy
    assert f("liturgical.verses", "psLI.sunday.m7.prokeimenon.v1.text") == "lit/sun/t7/prokeimenon"
    for hid in ["oct/t4/sun/apolytikion", "men/11-21/kontakion", "mov/49/communion", "lit/sun/t2/alleluia"]:  # pattern keys map back
        k = hymns.dcs_keys(hid)[-1][0].replace("*", "XX").split("|")
        assert f(*k) == hid, (hid, k)
