"""Nativity (Dec 25) and Theophany (Jan 6) on a Monday: Typikon p.145-148 / p.174-176 (data/rules/major_feasts_nat_thy_monday.yaml
plus the Rules of major_feasts.yaml widened with feast_not_sunday). No ANCA text exists, so slices.yaml keeps both Mondays disabled:
documents carry the 'Incomplete' banner, and the Rules are checked here without the slice gate (Rules do not read in_slice)."""
import datetime as dt
import os

import pytest

from yocal_rules import assemble, calfacts, cli
from yocal_rules.rules import load_catalogue

needs_db = pytest.mark.skipif(not os.path.exists(calfacts.DEFAULT_DB), reason="calendar DB not built")

NAT = "2023-12-25"   # Monday; eve = Sunday 2023-12-24
THY = "2025-01-06"   # Monday; eve = Sunday 2025-01-05


def _eve(date):
    return (dt.date.fromisoformat(date) - dt.timedelta(days=1)).isoformat()


def slots(service, date):
    r = assemble.build(service, dt.date.fromisoformat(date))
    return r, {s: x for s, _, x in r.slots}


def _all(date):
    out = {}
    for svc, d in (("vespers", _eve(date)), ("matins", date), ("liturgy", date)):
        out[svc] = slots(svc, d)
    return out


def test_mondays_not_in_slices_yaml():
    sl = calfacts._slices()
    for key in ("supported_fixed_major", "supported_major_eve_vespers"):
        bad = [x for x in sl[key] if x.startswith(("12-25", "01-06"))]
        assert not bad, (key, bad)


@needs_db
@pytest.mark.parametrize("date,feast", [("2017-12-25", "nativity"), ("2023-12-25", "nativity"), ("2028-12-25", "nativity"),
                                         ("2025-01-06", "theophany"), ("2031-01-06", "theophany")])
def test_monday_cases_resolve_everything_but_missing(date, feast):
    for svc, (r, s) in _all(date).items():
        f = r.facts
        assert f["major_feast"] == feast and f["weekday"] == "Monday" and not f["in_slice"], svc
        assert any("on a Monday" in x for x in f["slice_reasons"])
        missing = sorted(k for k, x in s.items() if x.status == "missing")
        want = ["vespers.prokeimenon"] if (svc == "vespers" and feast == "nativity") else []
        assert missing == want, (svc, missing)
        for k, x in s.items():
            assert x.rule is not None and x.rule["source"] in ("typikon", "anca"), k
            if x.status == "missing":
                assert x.rule["ticket"]


@needs_db
def test_nativity_eve_is_sunday_great_vespers_without_vesperal_liturgy():
    r, v = slots("vespers", _eve(NAT))
    assert r.facts["weekday"] == "Monday" and dt.date.fromisoformat(_eve(NAT)).weekday() == 6
    assert (v["vespers.lihc.stichera"].fill["res"], v["vespers.lihc.stichera"].fill["other"]) == (0, [6])
    assert v["vespers.lihc.stichera"].rule_id == "mf.nat.ves.lihc" and v["vespers.lihc.stichera"].status == "explicit"   # widened, p.143
    assert v["vespers.readings"].fill["count"] == 2 and v["vespers.readings"].rule_id == "mf.nat.mon.ves.readings"
    assert v["vespers.readings"].rule["conflict"]["status"] == "open"                                                  # Menaion's 8, as the weekday Rule
    assert v["vespers.aposticha"].fill["owner"] == "feast"                                                              # Tue-Sat has none (Vesperal Liturgy)
    assert v["vespers.litia"].fill["litia"] is False and v["vespers.apolytikia"].status == "explicit"
    pk = v["vespers.prokeimenon"]
    assert pk.status == "missing" and "p.144" in pk.rule["ticket"]
    _, tue = slots("vespers", "2024-12-24")                                                                             # Wednesday feast: eve Tuesday, Vesperal Liturgy
    assert tue["vespers.aposticha"].fill["owner"] == "none" and tue["vespers.readings"].rule_id == "mf.nat.ves.readings"


@needs_db
def test_theophany_eve_widened_anca_rules_and_typikon_monday_rules():
    r, v = slots("vespers", _eve(THY))
    assert v["vespers.lihc.stichera"].rule_id == "mf.thy.ves.lihc" and v["vespers.prokeimenon"].fill["kind"] == "none"
    rd = v["vespers.readings"]
    assert rd.fill["count"] == 13 and rd.status == "inferred"
    assert any("p.176" in w for w in rd.rule["conflict"]["with"]) and rd.rule["conflict"]["status"] == "open"          # Typikon Monday list logged
    assert v["vespers.litia"].rule_id == "mf.thy.mon.ves.litia" and v["vespers.litia"].status == "inferred"
    assert v["vespers.litia"].rule["conflict"]["with"][0] == "mf.thy.ves.litia"                                         # references, not duplicated
    assert v["vespers.aposticha"].status == "explicit" and "p.176" in v["vespers.aposticha"].rule["locator"]
    assert v["vespers.apolytikia"].rule_id == "mf.thy.mon.ves.apolytikia" and v["vespers.apolytikia"].status == "explicit"


@needs_db
@pytest.mark.parametrize("date", [NAT, THY])
def test_monday_liturgy_is_basil_and_feast_parts_widened(date):
    _, l = slots("liturgy", date)
    assert l["liturgy.author"].fill["author"] == "Basil the Great" and l["liturgy.author"].status == "explicit"
    assert l["liturgy.dismissal"].fill["author"] == "Basil the Great"
    assert l["liturgy.trisagion"].fill["kind"] == "baptized" and l["liturgy.final_hymn"].fill["kind"] == "feast_troparion"
    assert l["liturgy.epistle"].fill["ref"] and l["liturgy.gospel"].fill["ref"]
    assert l["liturgy.antiphons"].fill["refrain2"] == "feast" and l["liturgy.dismissal_phrase"].fill["phrase"] == "feast"
    for k in ("liturgy.antiphons", "liturgy.communion", "liturgy.epistle"):
        assert "Monday" in l[k].rule["locator"], k


@needs_db
def test_monday_matins_widened_locators_name_monday_pages():
    for date, pages in ((NAT, "p.144-145"), (THY, "p.176")):
        _, m = slots("matins", date)
        assert m["matins.praises"].status == "explicit" and pages in m["matins.praises"].rule["locator"]
        assert m["matins.eothinon_gospel"].fill["ref"]
    _, m = slots("matins", NAT)
    assert (m["matins.praises"].fill["total"], m["matins.praises"].fill["other"]) == (4, [4])
    _, m = slots("matins", THY)
    assert (m["matins.praises"].fill["total"], m["matins.praises"].fill["other"]) == (6, [6])


@needs_db
def test_tuesday_to_saturday_orders_unchanged():
    _, l = slots("liturgy", "2025-12-25")                                                                              # Thursday
    assert l["liturgy.author"].rule_id == "mf.nat.lit.author" and l["liturgy.author"].fill["author"] == "John Chrysostom"
    _, v = slots("vespers", "2026-01-05")                                                                              # Theophany Tuesday: Monday eve
    assert v["vespers.litia"].rule_id == "mf.thy.ves.litia" and v["vespers.aposticha"].rule_id == "mf.thy.ves.aposticha"


@needs_db
@pytest.mark.parametrize("date,named", [("2023-12-23", "before_nativity_24"), ("2023-12-24", "before_nativity_24"),
                                         ("2025-01-04", "before_theophany"), ("2025-01-05", "before_theophany")])
def test_sunday_before_stays_in_slice(date, named):
    for svc in (("vespers",) if dt.date.fromisoformat(date).weekday() == 5 else ("matins", "liturgy")):
        r, s = slots(svc, date)
        assert r.facts["in_slice"] and r.facts["named_sunday"] == named
        assert not any(x.status == "missing" for x in s.values())


def test_conflict_references_exist():
    rules, _, _ = load_catalogue()
    ids = {r["id"] for r in rules}
    for r in rules:
        for w in r.get("conflict", {}).get("with", []):
            if w.startswith("mf."):
                assert w in ids, (r["id"], w)


@needs_db
@pytest.mark.parametrize("date,svc,must", [
    (_eve(NAT), "vespers", ["Aposticha of the Nativity", "Genesis 1:1-13"]),
    (NAT, "matins", ["Matthew 1:18-25", "4 stichera of the Nativity"]),
    (NAT, "liturgy", ["As many as have been baptized", "Galatians 4:4-7", "Liturgy of St. Basil the Great"]),
    (_eve(THY), "vespers", ["13 Old Testament readings", "when John saw Thee"]),
    (THY, "matins", ["Mark 1:9-11", "6 stichera of Theophany"]),
    (THY, "liturgy", ["Matthew 3:13-17", "Titus 2:11-14", "Liturgy of St. Basil the Great"]),
])
def test_monday_documents_incomplete_banner(tmp_path, date, svc, must):
    assert cli.main([date, svc, "--no-compare", "--out", str(tmp_path)]) == 0
    doc = (tmp_path / f"{date}-{svc}.md").read_text()
    assert "Incomplete" in doc and "on a Monday" in doc
    assert doc.count("- [to be determined]") == (1 if (svc == "vespers" and date == _eve(NAT)) else 0)
    for m in must:
        assert m in doc, m
