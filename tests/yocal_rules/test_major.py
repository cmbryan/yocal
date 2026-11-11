"""Work package I: Major feasts on a weekday/Saturday and their eve Great Vespers (data/rules/major_feasts.yaml)."""
import datetime as dt
import os

import pytest

from yocal_rules import anca, assemble, calfacts, cli

needs_db = pytest.mark.skipif(not os.path.exists(calfacts.DEFAULT_DB), reason="calendar DB not built")


def slots(service, date):
    r = assemble.build(service, dt.date.fromisoformat(date))
    return r, {s: x for s, _, x in r.slots}


def test_major_feast_ids():
    assert calfacts.major_feast(dt.date(2026, 8, 6)) == ("transfiguration", "lord", False)
    assert calfacts.major_feast(dt.date(2026, 5, 21)) == ("ascension", "lord", True)  # Pascha 2026-04-12 + 39
    assert calfacts.major_feast(dt.date(2026, 5, 31))[0] == "pentecost"
    assert calfacts.major_feast(dt.date(2026, 8, 7))[0] == ""


@needs_db
def test_slice_weekday_vs_sunday_and_monday_orders():
    assert calfacts.load_facts(dt.date(2026, 8, 6), "matins")["in_slice"]
    assert calfacts.load_facts(dt.date(2026, 5, 20), "vespers")["in_slice"]                   # Ascension eve
    assert calfacts.load_facts(dt.date(2024, 9, 8), "matins")["slice_reasons"] == ["fixed Major feast on a Sunday"]
    assert not calfacts.load_facts(dt.date(2025, 1, 6), "matins")["in_slice"]                 # Theophany on a Monday
    assert not calfacts.load_facts(dt.date(2026, 3, 25), "matins")["in_slice"]                # Annunciation: not enabled


@needs_db
def test_feast_only_slots_and_order():
    r, s = slots("liturgy", "2026-08-06")
    ids = [x for x, _, _ in r.slots]
    assert ids[0] == "liturgy.antiphons" and ids.index("liturgy.trisagion") == ids.index("liturgy.kontakion") + 1
    _, sun = slots("liturgy", "2026-11-08")                                                     # ordinary Sunday: no feast-only slots
    assert "liturgy.antiphons" not in sun


@needs_db
def test_weekday_eve_vespers():
    _, v = slots("vespers", "2026-08-05")                                                      # Wednesday eve of the Transfiguration
    assert v["vespers.lihc.stichera"].fill["res"] == 0 and v["vespers.lihc.stichera"].fill["other"] == [6]
    assert (v["vespers.prokeimenon"].fill["kind"], v["vespers.prokeimenon"].fill["tone"]) == ("daily", 5)
    assert v["vespers.readings"].fill["count"] == 3 and v["vespers.litia"].fill["litia"] is True
    _, v = slots("vespers", "2026-01-05")                                                      # Theophany eve (Tuesday feast)
    assert v["vespers.readings"].fill["count"] == 13 and v["vespers.prokeimenon"].fill["kind"] == "none"
    assert v["vespers.readings"].rule["conflict"]["status"] == "open"
    _, v = slots("vespers", "2025-12-31")                                                      # Circumcision / St Basil
    assert v["vespers.lihc.stichera"].fill["other"] == [3, 3]


@needs_db
def test_liturgy_feast_parts():
    _, l = slots("liturgy", "2026-09-14")
    assert l["liturgy.trisagion"].fill["kind"] == "cross"
    assert (l["liturgy.dismissal_phrase"].fill["phrase"], l["liturgy.dismissal_phrase"].fill["clause"]) == ("resurrection", "cross")  # p.18
    _, l = slots("liturgy", "2026-01-01")
    assert l["liturgy.author"].fill["author"] == "Basil the Great" and l["liturgy.communion"].fill["kind"] == "praise_the_lord"
    _, l = slots("liturgy", "2025-12-25")
    assert l["liturgy.trisagion"].fill["kind"] == "baptized" and l["liturgy.epistle"].fill["ref"] == "Galatians 4:4-7"
    _, l = slots("liturgy", "2025-09-08")                                                      # Theotokos feast on a Monday
    assert l["liturgy.antiphons"].fill["refrain2"] == "saints" and l["liturgy.final_hymn"].fill["kind"] == "true_light"


def test_feast_parsers():
    txt = ("Great Vespers of August 06\n                For the Transfiguration (Nassar)\nVerse 6. If Thou.\nhymn\nVerse 5. x\nhymn\n"
           "Verse 4. x\nhymn\nVerse 3. x\nhymn\nVerse 2. x\nhymn\nVerse 1. x\nhymn\n  DOXASTICON FOR THE TRANSFIGURATION\n"
           " SATURDAY PROKEIMENON IN TONE SIX\n MONDAY PROKEIMENON IN TONE FOUR\nReader: The Reading from Exodus (24:12-18).\n"
           "Reader: The Reading from the First Epistle of St. Paul (9:19-27).\n")
    k = anca.parse_feast_vespers("x\nVerse 10. Bring my soul\nVerse 9. y\nVerse 8. y\nVerse 7. y\n" + txt)
    assert k["vespers.lihc.stichera"] == dict(res=0, other=[6], total=6)
    assert k["vespers.prokeimenon"]["kind"] == "daily" and k["vespers.readings"]["count"] == 1
    lit = ("THE SECOND ANTIPHON Refrain: Save us, O Son of God, Who art wondrous in the saints, who sing to Thee: Alleluia. "
           "THE ANTI-TRISAGION HYMN Before Thy Cross we bow down KOINONIKON (COMMUNION HYMN) OF THE FEAST I will take the cup of salvation "
           "Post-Communion Hymn: “We have seen the true light.” THE DISMISSAL Priest: May Christ our true God")
    k = anca.parse_feast_liturgy(lit)
    assert k["liturgy.antiphons"]["refrain2"] == "saints" and k["liturgy.trisagion"]["kind"] == "cross"
    assert k["liturgy.communion"]["kind"] == "cup_of_salvation" and k["liturgy.final_hymn"]["kind"] == "true_light"
    assert k["liturgy.dismissal_phrase"]["phrase"] == "plain"


@needs_db
@pytest.mark.parametrize("date,service,must", [
    ("2025-12-25", "liturgy", ["As many as have been baptized", "Galatians 4:4-7", "Matthew 2:1-12", "Liturgy of St. John Chrysostom"]),
    ("2026-01-05", "vespers", ["13 Old Testament readings", "Apolytikion of Theophany"]),
    ("2026-08-06", "matins", ["Luke 9:28-36", "Katavasia of the Holy Cross", "4 stichera of the feast"]),
    ("2026-08-15", "liturgy", ["Philippians 2:5-11", "wondrous in the saints", "I will take the cup of salvation"]),
    ("2026-05-21", "liturgy", ["Acts 1:1-12", "Luke 24:36-53", "Kontakion of the Ascension", "ascended from us into heaven"]),
])
def test_documents(tmp_path, date, service, must):
    assert cli.main([date, service, "--no-compare", "--out", str(tmp_path)]) == 0
    doc = (tmp_path / f"{date}-{service}.md").read_text()
    unverified = date in ("2025-12-25", "2026-01-05")  # Nativity / Theophany: Rules exist but disabled in slices.yaml (no ANCA check)
    assert ("Incomplete" in doc) == unverified
    assert "- [to be determined]" not in doc and "Typikon" not in doc and "{'" not in doc
    for m in must:
        assert m in doc, m


@needs_db
@pytest.mark.parametrize("date,tone,prok_rule", [("2019-03-24", 8, "mf.ves.ann.prokeimenon.sun"), ("2026-03-24", 1, "mf.ves.ann.prokeimenon.tue")])
def test_annunciation_eve_vespers_follow_anca(date, tone, prok_rule):
    r, v = slots("vespers", date)                                                              # Sunday eve (Mon feast, 2019) / Tuesday eve (Wed feast, 2026)
    assert calfacts.load_facts(dt.date.fromisoformat(date), "vespers")["in_slice"]
    assert v["vespers.lihc.stichera"].fill["res"] == 0 and v["vespers.lihc.stichera"].fill["other"] == [6]
    assert (v["vespers.prokeimenon"].fill["kind"], v["vespers.prokeimenon"].fill["tone"]) == ("daily", tone)
    assert v["vespers.prokeimenon"].rule["id"] == prok_rule
    assert v["vespers.readings"].fill["count"] == 3 and v["vespers.litia"].fill["litia"] is True
    assert v["vespers.aposticha"].fill["owner"] == "feast" and v["vespers.apolytikia"].fill["saint"] is True
    assert not any(x.rule["status"] == "missing" for x in v.values())


@needs_db
def test_annunciation_eve_typikon_reading_logged_as_conflict():
    _, v = slots("vespers", "2026-03-24")
    for slot in ("vespers.lihc.stichera", "vespers.prokeimenon"):
        c = v[slot].rule["conflict"]
        assert c["status"] == "open" and "p.283" in c["with"][0] and "p.286" in c["with"][0] and "Menaion" in c["note"]
    assert v["vespers.litia"].rule["conflict"]["with"] == ["mf.ves.litia"]
    assert all(v[s].rule["source"] == "anca" and v[s].rule["status"] == "inferred" for s in v)


@needs_db
def test_annunciation_eve_other_cases_stay_incomplete():
    f = lambda d, s: calfacts.load_facts(dt.date.fromisoformat(d), s)
    assert not f("2025-03-24", "vespers")["in_slice"]                                          # Monday eve (Tue feast): no ANCA text
    assert not f("2022-03-24", "vespers")["in_slice"]                                          # Wednesday eve
    assert not f("2018-03-24", "vespers")["in_slice"]                                          # Saturday eve of a Sunday feast
    assert not f("2026-03-25", "matins")["in_slice"] and not f("2026-03-25", "liturgy")["in_slice"]  # feast day itself stays disabled


@needs_db
def test_annunciation_eve_document(tmp_path):
    assert cli.main(["2026-03-24", "vespers", "--no-compare", "--out", str(tmp_path)]) == 0
    doc = (tmp_path / "2026-03-24-vespers.md").read_text()
    assert "Incomplete" not in doc and "All Variable parts determined" in doc and "Annunciation" in doc
    assert cli.main(["2025-03-24", "vespers", "--no-compare", "--out", str(tmp_path)]) == 0
    assert "Incomplete" in (tmp_path / "2025-03-24-vespers.md").read_text()
