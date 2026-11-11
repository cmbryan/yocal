"""Work package H: Sundays (and their Saturday Great Vespers) in a fore-feast / after-feast / leavetaking period."""
import datetime as dt
import os

import pytest

from yocal_rules import anca, assemble, calfacts

pytestmark = pytest.mark.skipif(not os.path.exists(calfacts.DEFAULT_DB), reason="calendar DB not built")
CACHE = os.path.join(os.environ.get("CLAUDE_JOB_DIR", ""), "tmp", "cache")


def _res(service, d, slot):
    r = assemble.build(service, dt.date.fromisoformat(d))
    return next(x for s, _, x in r.slots if s == slot)


def test_feast_period_normalisation():
    fp = calfacts.feast_period
    assert fp("Afterfeast of The Dormition of the Mother of God") == ("afterfeast:dormition", "theotokos", False)
    assert fp("Forefeast of the Theophany") == ("forefeast:theophany", "lord", False)
    assert fp("Leavetaking of the Meeting of the Lord in the Temple")[0] == "leavetaking:presentation"
    assert fp("Afterfeast of the Entrance of the Lord to the Temple")[0] == "afterfeast:presentation"
    assert fp("Afterfeast of the Entrance of the Mother of God into the Temple")[0] == "afterfeast:entrance_theotokos"
    assert fp("Leavetaking of The Beheading of the Forerunner") == ("leavetaking:beheading", "saint", False)
    assert fp("", "Leavetaking of The Theophany") == ("leavetaking:theophany", "lord", True)  # DB puts Jan 14 / Aug 7 in major_commem
    assert fp("", "Saint Theodosius the Great") == ("", "", False)


def test_facts_and_slice():
    f = calfacts.load_facts(dt.date(2025, 8, 17), "matins")
    assert f["feast_period"] == "afterfeast:dormition" and not f["feast_period_saint"] and f["in_slice"]
    assert calfacts.load_facts(dt.date(2024, 1, 7), "matins")["feast_period_saint"]  # Synaxis of the Forerunner
    assert not calfacts.load_facts(dt.date(2022, 8, 7), "matins")["feast_period_saint"]  # period text in major_commem is not a saint
    f = calfacts.load_facts(dt.date(2026, 5, 24), "matins")  # Ascension afterfeast: Pentecostarion package (G), not this one
    assert f["feast_period"] == "afterfeast:ascension" and f["season"] == "pentecostarion"


def test_vespers_stichera_counts():
    cases = {  # Saturday -> (rule, res, other)
        "2025-08-16": ("fa.ves.lihc.afterfeast", 6, [4]),           # Sunday after the Dormition p.461
        "2024-01-06": ("fa.ves.lihc.afterfeast_saint", 4, [3, 3]),  # Jan 7 Synaxis p.179
        "2026-08-15": ("fa.ves.lihc.holy_napkin", 4, [3, 3]),       # Aug 16 p.460
        "2024-12-21": ("fa.ves.lihc.nativity", 4, [3, 3]),          # Sunday before the Nativity Dec 20-23 p.134
        "2023-06-24": ("fa.ves.lihc.forerunner_leavetaking", 6, [4]),  # Jun 24 on Saturday p.417
        "2026-08-29": ("fa.ves.lihc.beheading_leavetaking", 4, [3, 3]),  # Aug 29 on Saturday p.466
        "2025-09-20": ("ves.lihc.ch5.09-21", 4, [6]),               # Ch V per-date table wins over the period Rules
    }
    for sat, (rid, res, other) in cases.items():
        x = _res("vespers", sat, "vespers.lihc.stichera")
        assert (x.rule_id, x.fill["res"], x.fill["other"]) == (rid, res, other), sat


def test_great_prokeimenon_on_lords_feast_saturday():
    for sat in ("2024-01-06", "2022-08-06", "2024-09-14"):
        assert _res("vespers", sat, "vespers.prokeimenon").fill == {"kind": "great", "tone": 7}, sat
    assert _res("vespers", "2026-08-15", "vespers.prokeimenon").fill["kind"] == "lord_is_king"  # Dormition: not a feast of the Lord


def test_apolytikia_praises_dismissal():
    for svc, d in (("vespers", "2025-08-16"), ("matins", "2025-08-17"), ("liturgy", "2025-08-17")):
        x = _res(svc, d, f"{svc}.apolytikia")
        assert x.fill["saint"] is True and x.fill["feast"] is True, svc
    assert _res("matins", "2025-08-17", "matins.praises").fill == {"total": 8, "res": 4, "other": [4], "glory": "eothinon"}
    assert _res("matins", "2026-08-30", "matins.praises").fill["res"] == 8  # Beheading leavetaking: all Resurrection (p.466)
    assert _res("liturgy", "2025-08-17", "liturgy.dismissal").fill["saint_named"] is False  # p.17: no Doxastikon for the saint
    assert _res("liturgy", "2026-01-11", "liturgy.dismissal").fill["saint_named"] is True   # great saint (Theodosius)
    assert _res("liturgy", "2025-12-21", "liturgy.dismissal").rule_id == "fa.lit.dismissal.nativity_sunday"
    assert _res("liturgy", "2024-01-07", "liturgy.dismissal").fill["saint_named"] is False  # Forerunner clause


def test_dismissal_phrase():
    assert _res("liturgy", "2025-01-12", "liturgy.dismissal_phrase").fill == {"phrase": "feast_and_resurrection", "clause": "none"}
    assert _res("liturgy", "2024-09-15", "liturgy.dismissal_phrase").fill == {"phrase": "resurrection", "clause": "cross"}
    assert _res("liturgy", "2025-08-17", "liturgy.dismissal_phrase").fill == {"phrase": "resurrection", "clause": "theotokos"}
    assert _res("liturgy", "2026-01-04", "liturgy.dismissal_phrase").fill == {"phrase": "resurrection", "clause": "none"}
    assert _res("liturgy", "2022-07-03", "liturgy.dismissal_phrase").fill["phrase"] == "resurrection"  # ordinary Sunday default


def test_parse_dismissal_phrase():
    f = ("THE DISMISSAL Priest: May He Who was transfigured in glory before His holy disciples, and rose from the dead, Christ our true God, "
         "through the intercessions of His all-immaculate holy Mother; by the might of the Cross; of Joachim and Anna, and of all the saints")
    assert anca.parse_dismissal_phrase(f) == {"phrase": "feast_and_resurrection", "clause": "none"}
    f = ("THE DISMISSAL Priest: May He Who rose from the dead, Christ our true God, through the intercessions of His holy Mother—whose "
         "Dormition we now celebrate—by the might of the Cross; of Joachim and Anna")
    assert anca.parse_dismissal_phrase(f) == {"phrase": "resurrection", "clause": "theotokos"}


def test_out_of_season_untouched():
    assert not _res("matins", "2026-05-24", "matins.praises").rule_id.startswith("fa.")  # Ascension afterfeast


@pytest.mark.skipif(not os.path.isdir(CACHE), reason="ANCA cache not available")
def test_anca_sweep_period_sundays():
    """Every cached 2022-26 period Sunday in an enabled category: no unexplained ANCA diff."""
    import sqlite3
    con = sqlite3.connect(calfacts.DEFAULT_DB)
    days = [r[0] for r in con.execute("select date from yocal_main where fore_after!='' and strftime('%w',date)='0' "
                                      "and date between '2022-01-01' and '2026-11-08'")]
    bad = []
    for d in map(dt.date.fromisoformat, days):
        for svc, sd in (("vespers", d - dt.timedelta(days=1)), ("matins", d), ("liturgy", d)):
            r = assemble.build(svc, sd)
            if not r.facts["in_slice"]:
                break
            assemble.compare_keys(r, CACHE, offline=True, dcs_on=False)
            bad += [(str(d), s, c.details) for s, c in r.comparisons["anca"].items() if c.blocking]
    assert not bad, bad
