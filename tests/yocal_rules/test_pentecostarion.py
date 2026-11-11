"""Work package G: Pentecostarion Sundays (data/rules/pentecostarion.yaml)."""
import datetime as dt
import os

import pytest

from yocal_rules import anca, assemble, calfacts, cli, compare

needs_db = pytest.mark.skipif(not os.path.exists(calfacts.DEFAULT_DB), reason="calendar DB not built")


def slots(service, date):
    r = assemble.build(service, date)
    return r, {s: x for s, _, x in r.slots}


@needs_db
def test_pentecostarion_sundays_are_in_slice_pascha_is_not():
    assert calfacts.load_facts(dt.date(2026, 4, 19), "matins")["in_slice"]          # Thomas
    assert calfacts.load_facts(dt.date(2026, 5, 24), "matins")["in_slice"]          # Holy Fathers (afterfeast of the Ascension)
    assert not calfacts.load_facts(dt.date(2026, 4, 12), "matins")["in_slice"]      # Pascha stays out of the slice


@needs_db
def test_thomas_sunday_no_resurrection_material():
    _, v = slots("vespers", dt.date(2026, 4, 18))
    assert v["vespers.lihc.stichera"].fill["res"] == 0 and v["vespers.lihc.stichera"].fill["other"] == [10]
    assert v["vespers.apolytikia"].fill["res_tone"] is None
    _, m = slots("matins", dt.date(2026, 4, 19))
    assert m["matins.prokeimenon"].fill["kind"] == "other"
    assert m["matins.praises"].fill["total"] == 6 and m["matins.praises"].rule_id == "pent.mat.praises.thomas"
    assert "pent.mat.praises.thomas.anca4" in m["matins.praises"].shadowed


@needs_db
def test_samaritan_and_fathers_counts():
    _, v = slots("vespers", dt.date(2026, 5, 9))
    assert v["vespers.lihc.stichera"].fill["res"] == 4 and v["vespers.lihc.stichera"].fill["other"] == [3, 3]
    _, v = slots("vespers", dt.date(2026, 5, 23))
    assert v["vespers.lihc.stichera"].fill["res"] == 3 and v["vespers.lihc.stichera"].fill["other"] == [3, 4]
    _, l = slots("liturgy", dt.date(2026, 5, 24))
    assert l["liturgy.dismissal_phrase"].fill == {"phrase": "feast_and_resurrection", "clause": "none"}


@needs_db
def test_coincidence_orders_and_withheld_dates():
    _, v = slots("vespers", dt.date(2023, 4, 22))  # St George on Thomas Sunday (Ch V p.328)
    assert v["vespers.lihc.stichera"].fill["other"] == [6, 4]
    _, m = slots("matins", dt.date(2023, 4, 23))
    assert m["matins.kathismata"].status == "missing"
    # Ss Constantine and Helen on the Samaritan Woman (2028-05-21? use any year where 05-21 is pascha+28): withheld
    y = next(y for y in range(2001, 2100) if calfacts.pascha(y) + dt.timedelta(days=28) == dt.date(y, 5, 21))
    _, m = slots("matins", dt.date(y, 5, 21))
    assert m["matins.apolytikia"].status == "missing" and m["matins.praises"].status == "missing"


@needs_db
def test_pascha_matins_and_holy_saturday_vespers():
    _, m = slots("matins", dt.date(2026, 4, 12))
    assert m["matins.eothinon_gospel"].fill["number"] == 2
    assert m["matins.kontakion"].fill["kind"] == "feast"
    _, v = slots("vespers", dt.date(2026, 4, 11))
    assert all(x.status == "missing" for x in v.values())


def test_thomas_unheaded_stichera_parse_as_proper():
    txt = ("3.) We chant “O Lord, I Have Cried” in Tone 1 with ten stichera:\n(Nassar 940; Kazan Pentecostarion I, 107)\n"
           + "".join(f"Verse {n}. x\n" for n in range(10, 0, -1)) + "\n4.) next\n")
    assert anca.parse_vespers(txt)["vespers.lihc.stichera"] == {"res": 0, "other": [10], "total": 10}


def test_acts_of_the_holy_apostles_ref():
    k = anca.parse_liturgy("THE EPISTLE\n The Reading from the Acts of the Holy Apostles. (6:1-7)\n")
    assert k["liturgy.epistle"]["ref"] == "6:1-7"


@needs_db
@pytest.mark.parametrize("date,service", [("2026-04-19", "liturgy"), ("2026-05-10", "matins"), ("2026-05-09", "vespers"),
                                          ("2026-05-31", "liturgy"), ("2026-05-31", "matins")])
def test_documents(tmp_path, date, service):
    assert cli.main([date, service, "--no-compare", "--out", str(tmp_path)]) == 0
    doc = (tmp_path / f"{date}-{service}.md").read_text()
    assert "Incomplete" not in doc and "None" not in doc and "Typikon" not in doc
    if date == "2026-05-31" and service == "liturgy":
        assert "Acts 2:1-11" in doc and "Apolytikion of Pentecost" in doc and "[to be determined]" not in doc
    if service == "matins" and date == "2026-05-10":
        assert "Mid-Pentecost" in doc or "Samaritan" in doc


@needs_db
def test_divergence_log_explains_thomas_praises():
    r = assemble.build("matins", dt.date(2026, 4, 19))
    res = {s: x for s, _, x in r.slots}["matins.praises"]
    c = compare.compare(res, {"matins.praises": {"total": 4, "res": 0}}, "anca", r.facts, "matins", compare.load_divergence())
    assert c.cls == "divergence:anca_counts_without_repetition"
