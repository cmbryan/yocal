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
    assert calfacts.load_facts(dt.date(2024, 9, 8), "matins")["in_slice"]                     # Sunday order enabled (major_feasts_sunday.yaml)
    assert calfacts.load_facts(dt.date(2023, 8, 6), "matins")["slice_reasons"] == ["fixed Major feast on a Sunday"]  # Transfiguration on Sunday: no ANCA text
    assert not calfacts.load_facts(dt.date(2025, 1, 6), "matins")["in_slice"]                 # Theophany on a Monday
    assert calfacts.load_facts(dt.date(2026, 3, 25), "matins")["in_slice"]                    # Annunciation on a Wednesday: enabled (ANCA 2026)
    assert not calfacts.load_facts(dt.date(2025, 3, 25), "matins")["in_slice"]                # ... on a Tuesday: no ANCA text


@needs_db
def test_feast_only_slots_and_order():
    r, s = slots("liturgy", "2026-08-06")
    ids = [x for x, _, _ in r.slots]
    assert ids[0] == "liturgy.antiphons" and ids.index("liturgy.trisagion") == ids.index("liturgy.kontakion") + 1
    _, sun = slots("liturgy", "2026-11-08")                     # ordinary Sunday: festal-hymn slots resolve to the booklet's ordinary texts
    assert sun["liturgy.antiphons"].fill == {"kind": "ordinary"} and sun["liturgy.megalynarion"].fill == {"kind": "axion"}
    assert "liturgy.final_hymn" not in sun


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
    assert not f("2021-03-24", "vespers")["in_slice"]                                          # Wednesday eve (Thu feast)
    assert not f("2022-03-24", "vespers")["in_slice"]                                          # Thursday eve (Fri feast)
    assert not f("2023-03-24", "vespers")["in_slice"]                                          # Friday eve (Sat feast): ANCA has only a Presanctified Liturgy
    assert f("2020-03-24", "vespers")["in_slice"] and f("2026-03-24", "vespers")["in_slice"]  # Tuesday eves
    # the feast-day weekday key enables Matins/Liturgy only, never the eve Vespers of that weekday
    assert not f("2019-03-25", "vespers")["in_slice"] and not f("2026-03-25", "vespers")["in_slice"]  # Mon/Wed evening = the eve of Tuesday/Thursday


@needs_db
@pytest.mark.parametrize("date", ["2019-03-25", "2026-03-25"])
def test_annunciation_feast_day_matins_liturgy_enabled(date):                                    # Monday (ANCA 2019), Wednesday (ANCA 2026)
    for svc in ("matins", "liturgy"):
        r, s = slots(svc, date)
        assert r.facts["in_slice"] and r.facts["major_feast"] == "annunciation"
        assert not any(x.status == "missing" for x in s.values())
    _, m = slots("matins", date)
    assert m["matins.praises"].fill["other"] == [4] and m["matins.katavasia"].rule["id"] == "mf.mat.katavasia.annunciation"
    _, l = slots("liturgy", date)
    assert l["liturgy.communion"].fill["kind"] == "chosen_zion" and l["liturgy.kontakion"].fill["kind"] == "annunciation"
    assert l["liturgy.epistle"].fill["ref"] == "Hebrews 2:11-18" and l["liturgy.gospel"].fill["ref"] == "Luke 1:24-38"


@needs_db
@pytest.mark.parametrize("date", ["2021-03-25", "2022-03-25", "2023-03-25", "2025-03-25"])
def test_annunciation_feast_day_other_weekdays_stay_incomplete(date):                             # Thu, Fri, Sat, Tue: no ANCA Orthros/Liturgy text
    for svc in ("matins", "liturgy"):
        assert not calfacts.load_facts(dt.date.fromisoformat(date), svc)["in_slice"]


@needs_db
def test_annunciation_eve_document(tmp_path):
    assert cli.main(["2026-03-24", "vespers", "--no-compare", "--out", str(tmp_path)]) == 0
    doc = (tmp_path / "2026-03-24-vespers.md").read_text()
    assert "Incomplete" not in doc and "All Variable parts determined" in doc and "Annunciation" in doc
    assert cli.main(["2025-03-24", "vespers", "--no-compare", "--out", str(tmp_path)]) == 0
    assert "Incomplete" in (tmp_path / "2025-03-24-vespers.md").read_text()


# ---- Sunday occurrence of a fixed Major feast (data/rules/major_feasts_sunday.yaml) ----
SUNDAY_FEASTS = [("2024-09-08", "nativity_theotokos", 2), ("2019-09-08", "nativity_theotokos", 3), ("2025-02-02", "presentation", 7),
                 ("2020-02-02", "presentation", 8), ("2021-11-21", "entrance", 5), ("2021-08-15", "dormition", 7)]


def _eve(date):
    return (dt.date.fromisoformat(date) - dt.timedelta(days=1)).isoformat()


@needs_db
@pytest.mark.parametrize("date,feast,tone", SUNDAY_FEASTS)
def test_sunday_feast_in_slice_and_complete(date, feast, tone):
    for svc, d in (("vespers", _eve(date)), ("matins", date), ("liturgy", date)):
        r, s = slots(svc, d)
        assert r.facts["in_slice"] and r.facts["major_feast"] == feast and r.facts["weekday"] == "Sunday"
        assert not any(x.status == "missing" for x in s.values()), (svc, [k for k, x in s.items() if x.status == "missing"])
    _, v = slots("vespers", _eve(date))
    assert (v["vespers.lihc.stichera"].fill["res"], v["vespers.lihc.stichera"].fill["other"]) == (4, [6])
    assert v["vespers.apolytikia"].fill["res_tone"] == tone and v["vespers.apolytikia"].fill["saint"] is True
    assert (v["vespers.prokeimenon"].fill["kind"], v["vespers.prokeimenon"].fill["tone"]) == ("lord_is_king", 6)   # Saturday evening
    assert v["vespers.readings"].fill["count"] == 3 and v["vespers.aposticha"].fill["owner"] == "resurrection"
    _, m = slots("matins", date)
    assert (m["matins.prokeimenon"].fill["kind"], m["matins.prokeimenon"].fill["tone"]) == ("other", 4)           # the feast's, not the resurrectional
    assert m["matins.praises"].fill["total"] == 8 and m["matins.praises"].fill["res"] == 4 and m["matins.praises"].fill["other"] == [4]
    assert m["matins.kathismata"].fill["tone"] == tone and m["matins.evlogetaria"].fill["kind"] == "resurrectional"
    assert m["matins.eothinon_gospel"].fill["ref"]                                                                 # the feast's Matins Gospel


@needs_db
def test_theotokos_feast_sunday_liturgy_parts():
    _, l = slots("liturgy", "2024-09-08")                                                                         # Nativity of the Theotokos
    assert l["liturgy.antiphons"].fill["refrain2"] == "resurrection" and l["liturgy.eisodikon"].fill["kind"] == "sunday"
    assert l["liturgy.epistle"].fill["owner"] == "sunday" and l["liturgy.epistle"].fill["ref"] == "Galatians 6:11-18"  # p.68: Sunday before the Elevation
    assert l["liturgy.gospel"].fill["ref"] == "John 3:13-17"
    assert (l["liturgy.dismissal_phrase"].fill["phrase"], l["liturgy.dismissal_phrase"].fill["clause"]) == ("resurrection", "theotokos")
    assert l["liturgy.communion"].fill["kind"] == "cup_of_salvation" and l["liturgy.final_hymn"].fill["kind"] == "true_light"
    assert l["liturgy.apolytikia"].fill["patron"] is False
    _, l = slots("liturgy", "2021-11-21")                                                                         # Entrance: the feast's own readings
    assert l["liturgy.epistle"].fill["owner"] == "feast" and l["liturgy.epistle"].fill["ref"] == "Hebrews 9:1-7"
    _, l = slots("liturgy", "2025-02-02")                                                                         # Presentation: Lord's-feast phrase and entrance hymn
    assert l["liturgy.antiphons"].fill["refrain2"] == "feast" and l["liturgy.eisodikon"].fill["kind"] == "feast"
    assert l["liturgy.dismissal_phrase"].fill["phrase"] == "feast_and_resurrection"
    assert l["liturgy.kontakion"].fill["kind"] == "presentation"


@needs_db
@pytest.mark.parametrize("date", ["2020-02-02", "2025-02-02"])
def test_presentation_sunday_vespers_4r6_conflict_accepted(date):
    _, v = slots("vespers", _eve(date))
    r = v["vespers.lihc.stichera"].rule
    assert r["id"] == "mf.sun.ves.lihc.presentation" and r["source"] == "anca" and r["status"] == "inferred"
    assert r["conflict"]["status"] == "accepted" and "p.218" in r["conflict"]["with"][0]
    for d in ("2024-09-08", "2021-11-21", "2021-08-15"):                                                          # Theotokos class: Typikon's own 4R+6, no conflict
        _, v = slots("vespers", _eve(d))
        assert v["vespers.lihc.stichera"].rule["source"] == "typikon" and "conflict" not in v["vespers.lihc.stichera"].rule


@needs_db
@pytest.mark.parametrize("date", [d for d, _, _ in SUNDAY_FEASTS])
def test_theotokos_feast_sunday_evlogetaria_conflict_accepted(date):
    _, m = slots("matins", date)
    r = m["matins.evlogetaria"].rule
    assert r["source"] == "anca" and r["conflict"]["status"] == "accepted" and "not chanted" in r["conflict"]["with"][0]
    assert "parish practice" in r["conflict"]["note"]
    _, l = slots("matins", "2026-11-08")                                                                          # ordinary Sunday: no evlogetaria slot
    assert "matins.evlogetaria" not in l


@needs_db
def test_sunday_feast_vespers_litia_conflict_accepted_like_weekday():
    _, v = slots("vespers", "2024-09-07")
    c = v["vespers.litia"].rule["conflict"]
    assert c["status"] == "accepted" and "mf.ves.litia" in c["with"]


@needs_db
@pytest.mark.parametrize("date,svc", [("2024-09-08", "matins"), ("2025-02-02", "matins")])
def test_sunday_feast_matins_prokeimenon_not_resurrectional(date, svc):
    _, m = slots(svc, date)
    assert m["matins.prokeimenon"].rule["id"] == "mf.sun.mat.prokeimenon" and m["matins.prokeimenon"].fill["kind"] == "other"


@needs_db
def test_sunday_feast_orders_not_enabled_stay_incomplete():
    f = lambda d, s: calfacts.load_facts(dt.date.fromisoformat(d), s)
    assert f("2023-08-06", "liturgy")["slice_reasons"] == ["fixed Major feast on a Sunday"]                      # Transfiguration: no ANCA text
    assert f("2025-09-14", "matins")["slice_reasons"] == ["fixed Major feast on a Sunday"]                       # Elevation: no ANCA text
    r = f("2031-02-02", "matins")                                                                                 # Presentation on a Triodion Sunday (Typikon p.220 alt. order)
    assert not r["in_slice"] and "fixed Major feast on a Sunday of the triodion season" in r["slice_reasons"]
    _, m = slots("matins", "2031-02-02")
    assert m["matins.prokeimenon"].rule["id"] != "mf.sun.mat.prokeimenon"


def test_sunday_feast_parsers():
    assert anca._owner("THE RESURRECTION IN TONE TWO") == "resurrection" and anca._owner("ST. BASIL") == "saint" and anca._owner("THE ANNUNCIATION") == "feast"
    k = anca.parse_feast_matins("\n   EVLOGETARIA (BENEDICTIONS) IN TONE FIVE (KAZAN)\nBlessed art Thou, O Lord\n")
    assert k["matins.evlogetaria"] == dict(kind="resurrectional")
    k = anca.parse_feast_liturgy("THE EISODIKON (ENTRANCE HYMN) OF ORDINARY SUNDAYS Come, let us worship")
    assert k["liturgy.eisodikon"]["kind"] == "sunday"


@needs_db
@pytest.mark.parametrize("date,service,must,absent", [
    ("2024-09-08", "matins", ["Evlogetaria", "Prokeimenon of the feast — Menaion 09-08, Tone 4", "Luke 1:39-49,56", "4 of the Resurrection"], ["Resurrectional prokeimenon"]),
    ("2025-02-02", "matins", ["Evlogetaria", "Prokeimenon of the feast — Menaion 02-02, Tone 4", "Luke 2:25-32"], ["Resurrectional prokeimenon"]),
    ("2024-09-07", "vespers", ["4 stichera of the Resurrection — Octoechos Tone 2", "6 stichera of the feast", "Apolytikion of the feast (twice)"], ["Incomplete"]),
    ("2025-02-01", "vespers", ["6 stichera of the Presentation", "3 Old Testament readings"], ["Incomplete"]),
    ("2025-02-02", "liturgy", ["Hebrews 7:7-17 — for the feast", "Luke 2:22-40", "I will take the cup of salvation"], ["Incomplete"]),
    ("2021-08-15", "liturgy", ["Philippians 2:5-11 — for the feast", "Who art risen from the dead", "Dormition"], ["Incomplete"]),
])
def test_sunday_feast_documents(tmp_path, date, service, must, absent):
    assert cli.main([date, service, "--no-compare", "--out", str(tmp_path)]) == 0
    doc = (tmp_path / f"{date}-{service}.md").read_text()
    assert "- [to be determined]" not in doc and "Typikon" not in doc and "{'" not in doc and "{tone}" not in doc and "{mmdd}" not in doc
    for m in must:
        assert m in doc, m
    for a in absent:
        assert a not in doc, a


# ---- Annunciation on the 5th Sunday of Great Lent (data/rules/major_feasts_annunciation_lent5.yaml; ANCA 2018) ----
@needs_db
def test_annunciation_lent5_in_slice_and_complete():
    for svc, d in (("vespers", "2018-03-24"), ("matins", "2018-03-25"), ("liturgy", "2018-03-25")):
        r, s = slots(svc, d)
        assert r.facts["in_slice"] and r.facts["major_feast"] == "annunciation" and r.facts["pascha_days"] == -14
        assert not any(x.status == "missing" for x in s.values()), (svc, [k for k, x in s.items() if x.status == "missing"])
    f = lambda d: calfacts.load_facts(dt.date.fromisoformat(d), "matins")
    assert not f("2035-03-25")["in_slice"] and not f("2040-03-25")["in_slice"]                    # Annunciation on Lent 2-4 Sundays: no ANCA text


@needs_db
def test_annunciation_lent5_vespers_4r6_conflict_accepted():                                      # #42: Typikon p.291 (and ANCA) 4R+6; p.305 prints 6R+4
    _, v = slots("vespers", "2018-03-24")
    r = v["vespers.lihc.stichera"]
    assert (r.fill["res"], r.fill["other"]) == (4, [6]) and r.rule["id"] == "mf.lent5.ves.lihc"
    assert r.rule["source"] == "typikon" and r.rule["status"] == "explicit"
    assert r.rule["conflict"]["status"] == "accepted" and "p.305" in r.rule["conflict"]["with"][0] and "6 Resurrection + 4" in r.rule["conflict"]["with"][0]
    assert v["vespers.apolytikia"].fill["res_tone"] == 1 and v["vespers.aposticha"].fill["owner"] == "resurrection"
    assert (v["vespers.prokeimenon"].fill["kind"], v["vespers.prokeimenon"].fill["tone"]) == ("lord_is_king", 6)


@needs_db
def test_annunciation_lent5_matins_liturgy_parts_and_conflicts():
    _, m = slots("matins", "2018-03-25")
    assert (m["matins.praises"].fill["total"], m["matins.praises"].fill["res"], m["matins.praises"].fill["other"]) == (8, 4, [4])
    assert m["matins.evlogetaria"].rule["conflict"]["status"] == "accepted"                      # #39 class: ANCA sings them
    assert m["matins.prokeimenon"].rule["conflict"]["status"] == "accepted" and m["matins.eothinon_gospel"].fill["ref"] == "Luke 1:39-49,56"
    assert m["matins.kontakion"].fill["kind"] == "feast" and m["matins.kathismata"].fill["tone"] == 1
    _, l = slots("liturgy", "2018-03-25")
    assert (l["liturgy.kontakion"].fill["kind"], l["liturgy.kontakion"].fill["tone"]) == ("annunciation", 8)
    assert l["liturgy.antiphons"].fill["refrain2"] == "feast" and l["liturgy.eisodikon"].fill["kind"] == "feast"
    assert l["liturgy.dismissal_phrase"].fill["phrase"] == "feast_and_resurrection" and l["liturgy.author"].fill["author"] == "Basil the Great"  # DB basil flag (ANCA Chrysostom: logged divergence)
    assert l["liturgy.apolytikia"].fill["patron"] is False and l["liturgy.dismissal"].fill["saint_named"] is False


@needs_db
def test_annunciation_lent5_documents(tmp_path):
    for svc, d in (("vespers", "2018-03-24"), ("matins", "2018-03-25"), ("liturgy", "2018-03-25")):
        assert cli.main([d, svc, "--no-compare", "--out", str(tmp_path)]) == 0
        doc = (tmp_path / f"{d}-{svc}.md").read_text()
        assert "Incomplete" not in doc and "- [to be determined]" not in doc and "Typikon" not in doc and "{'" not in doc
    assert "4 stichera of the Resurrection" in (tmp_path / "2018-03-24-vespers.md").read_text()
    assert "Hebrews 2:11-18" in (tmp_path / "2018-03-25-liturgy.md").read_text()


@needs_db
def test_annunciation_eve_apolytikion_thrice_no_conflict():
    _, v = slots("vespers", "2026-03-24")
    assert "thrice" in v["vespers.apolytikia"].fill["parts"][0] and "conflict" not in v["vespers.apolytikia"].rule


# ---- Saturday of Lent week 4: Annunciation leavetaking Vespers Glory (#42 'misreading') ----
@needs_db
def test_lent4_leavetaking_vespers_glory_is_annunciation_misreading():
    _, v = slots("vespers", "2023-03-25")
    r = v["vespers.lihc.stichera"]
    assert (r.fill["res"], r.fill["other"]) == (4, [3, 3]) and r.rule["id"] == "tri.ves.lihc.mar26_lent4"
    assert "Glory: doxastikon of the Annunciation" in r.fill["parts"][-1]
    assert r.rule["conflict"]["status"] == "misreading" and "9 stichera" in r.rule["conflict"]["with"][0]


# ---- ANCA key check against cached texts (skipped without the cache) ----
CACHE = os.path.join(os.environ.get("CLAUDE_JOB_DIR", ""), "tmp", "cache")


def _cached(date, kind):
    p = os.path.join(CACHE, f"anca-{date}-{kind}.txt")
    return os.path.exists(p) and os.path.getsize(p) > 0


@needs_db
@pytest.mark.parametrize("date,svc,kind", [
    ("2018-03-24", "vespers", "VESP"), ("2018-03-25", "matins", "ORTHROS"), ("2018-03-25", "liturgy", "READ"),
    ("2019-03-25", "matins", "ORTHROS"), ("2019-03-25", "liturgy", "READ"), ("2026-03-25", "matins", "ORTHROS"), ("2026-03-25", "liturgy", "READ"),
    ("2019-03-24", "vespers", "VESP"), ("2026-03-24", "vespers", "VESP"), ("2020-03-24", "vespers", "VESP"), ("2023-03-25", "vespers", "VESP")])
def test_annunciation_cases_no_unexplained_anca_diff(tmp_path, date, svc, kind):
    if not _cached(date, kind):
        pytest.skip("ANCA text not cached")
    assert cli.main([date, svc, "--offline", "--cache", CACHE, "--fail-on-diff", "--out", str(tmp_path)]) == 0


# ---- Circumcision / St Basil (Jan 1) on a Sunday (data/rules/major_feasts_jan1_sunday.yaml; ANCA 2022-12-31 Vespers, 2023-01-01 Matins/Liturgy) ----
JAN1_SUNDAY = [("vespers", "2022-12-31"), ("matins", "2023-01-01"), ("liturgy", "2023-01-01")]


@needs_db
def test_jan1_sunday_in_slice_and_nothing_missing():
    for svc, d in JAN1_SUNDAY:
        r, s = slots(svc, d)
        assert r.facts["in_slice"] and r.facts["major_feast"] == "circumcision" and r.facts["weekday"] == "Sunday"
        missing = [k for k, x in s.items() if x.status == "missing"]
        assert missing == [], (svc, missing)
    pk = slots("liturgy", "2023-01-01")[1]["liturgy.prokeimenon"]
    assert pk.status == "inferred" and pk.rule["source"] == "anca" and "ticket" not in pk.rule and pk.fill["owner"] == "saint"
    assert "2023-01-01" in pk.rule["evidence"] and "2026-01-01" in pk.rule["evidence"] and "Psalm 48" in pk.fill["parts"][0]
    assert pk.rule["conflict"]["status"] == "accepted" and "p.166" in pk.rule["conflict"]["with"][0]
    assert calfacts.load_facts(dt.date(2034, 1, 1), "matins")["in_slice"]                                        # same order, any year (rules are year-independent; only 2023 ANCA-verified)
    assert calfacts.load_facts(dt.date(2026, 1, 1), "matins")["in_slice"]                                        # weekday order unchanged


@needs_db
def test_jan1_sunday_vespers_order_typikon_p165():
    _, v = slots("vespers", "2022-12-31")
    st = v["vespers.lihc.stichera"]
    assert (st.fill["res"], st.fill["other"]) == (4, [3, 3]) and st.rule["id"] == "mf.jan1.sun.ves.lihc"
    assert st.rule["source"] == "typikon" and st.rule["status"] == "explicit" and "p.165" in st.rule["locator"]
    assert "Now: theotokion of the Resurrection" in st.fill["parts"][-1]                                          # not the Circumcision doxastikon (p.165)
    assert v["vespers.aposticha"].fill["owner"] == "resurrection" and v["vespers.readings"].fill["count"] == 3
    assert [p.split(" — ")[0] for p in v["vespers.apolytikia"].fill["parts"]] == [
        "Apolytikion of the Resurrection", "Apolytikion of St Basil the Great", "Apolytikion of the Circumcision"]
    c = v["vespers.litia"].rule["conflict"]
    assert c["status"] == "accepted" and "mf.ves.litia" in c["with"]
    # the Nativity-leavetaking Sunday orders (pp.157, 161; 3R+4+3) are for Dec 31 on a Sunday: not this day
    assert st.fill["res"] != 3 and not any("Nativity" in p for p in st.fill["parts"])


@needs_db
def test_jan1_sunday_matins_evlogetaria_not_a_theotokos_class_conflict():
    _, m = slots("matins", "2023-01-01")
    e = m["matins.evlogetaria"]
    assert e.rule["id"] == "mf.jan1.sun.mat.evlogetaria" and e.rule["source"] == "typikon" and e.rule["status"] == "explicit"
    assert "conflict" not in e.rule                                                                               # #39 'not sung' conflict is Theotokos-class only
    assert m["matins.praises"].fill["res"] == 4 and m["matins.praises"].fill["other"] == [4]
    assert m["matins.prokeimenon"].fill["kind"] == "resurrectional" and m["matins.eothinon_gospel"].fill["number"] == 7
    k = m["matins.kathismata"].rule
    assert k["source"] == "anca" and k["conflict"]["status"] == "open" and "p.165" in k["conflict"]["with"][0]


@needs_db
def test_jan1_sunday_liturgy_parts_and_open_conflicts():
    _, l = slots("liturgy", "2023-01-01")
    assert l["liturgy.author"].fill["author"] == "Basil the Great"
    assert l["liturgy.antiphons"].fill["refrain2"] == "feast" and l["liturgy.eisodikon"].fill["kind"] == "sunday"
    assert l["liturgy.kontakion"].fill["kind"] == "circumcision" and l["liturgy.final_hymn"].fill["kind"] == "feast_troparion"
    assert l["liturgy.communion"].fill["kind"] == "praise_the_lord" and l["liturgy.gospel"].fill["ref"] == "Luke 2:20-21, 40-52"
    assert l["liturgy.epistle"].fill["ref"] == "Colossians 2:8-12"
    assert (l["liturgy.dismissal_phrase"].fill["phrase"], l["liturgy.dismissal_phrase"].fill["clause"]) == ("feast_and_resurrection", "none")
    for slot, frag in (("liturgy.apolytikia", "patron"), ("liturgy.megalynarion", "Let us extol"), ("liturgy.dismissal", None)):
        r = l[slot].rule
        assert r["id"].startswith("mf.jan1.sun.lit.") and r["source"] == "anca" and r["status"] == "inferred", slot
        assert r["conflict"]["status"] == "open" and (frag is None or frag in " ".join(r["conflict"]["with"]) + r["conflict"]["note"]), slot
    ep = l["liturgy.epistle"].rule                                                                                # accepted (not open): DB single Jan 1 Epistle, ANCA 2023/2026
    assert ep["id"] == "mf.jan1.sun.lit.epistle" and ep["conflict"]["status"] == "accepted" and "Epistle for St. Basil" in " ".join(ep["conflict"]["with"])
    assert l["liturgy.apolytikia"].fill["patron"] is True
    assert l["liturgy.megalynarion"].fill["kind"] == "in_thee_rejoiceth"


@needs_db
def test_jan1_sunday_documents(tmp_path):
    for svc, d in JAN1_SUNDAY:
        assert cli.main([d, svc, "--no-compare", "--out", str(tmp_path)]) == 0
        doc = (tmp_path / f"{d}-{svc}.md").read_text()
        assert "Incomplete" not in doc and "Typikon" not in doc and "{'" not in doc and "{tone}" not in doc and "{mmdd}" not in doc
        assert "[to be determined]" not in doc
    assert "My mouth shall speak of wisdom" in (tmp_path / "2023-01-01-liturgy.md").read_text()
    assert "3 stichera of St Basil" in (tmp_path / "2022-12-31-vespers.md").read_text()
    assert "Resurrectional evlogetaria" in (tmp_path / "2023-01-01-matins.md").read_text()
    assert "Colossians 2:8-12" in (tmp_path / "2023-01-01-liturgy.md").read_text()


@needs_db
@pytest.mark.parametrize("date,svc,kind", [("2022-12-31", "vespers", "VESP"), ("2023-01-01", "matins", "ORTHROS"), ("2023-01-01", "liturgy", "READ")])
def test_jan1_sunday_no_unexplained_anca_diff(tmp_path, date, svc, kind):
    if not _cached(date, kind):
        pytest.skip("ANCA text not cached")
    assert cli.main([date, svc, "--offline", "--cache", CACHE, "--fail-on-diff", "--out", str(tmp_path)]) == 0


def test_jan1_sunday_anca_parsers():
    k = anca.parse_feast_liturgy("Eisodikon (Entrance Hymn) is “O come, let us worship… save us, O Son of God, Who art risen from the dead…” as on ordinary Sundays.")
    assert k["liturgy.eisodikon"]["kind"] == "sunday"
    k = anca.parse_feast_liturgy("After Communion, instead of singing “We have seen the true light”, sing the Apolytikion of the Circumcision in Tone One.")
    assert k["liturgy.final_hymn"]["kind"] == "feast_troparion"


def test_no_anca_sunday_text_for_transfiguration_elevation():
    """ANCA published no service texts for Aug 6 2023 / Sep 14 2025 (liturgicday pages 3540/3541/4310/4311 list none;
    dated and undated names 404; the undated 'Aug 06'/'Sept 14' files are the 2026 weekday texts). Re-check before enabling
    '08-06:sunday' / '09-14:sunday': if this fails, ANCA texts now exist and the Sunday Rules can be verified."""
    for d in ("2023-08-05", "2023-08-06", "2025-09-14"):
        assert not [l for l in anca._index()[d]["links"] if "VESP" in l or "ORTHROS" in l or "READ" in l or "Abbr" in l], d
    assert not [k for k in ("2023-08-05", "2023-08-06", "2025-09-14") if k in anca._feast_index()]
    enabled = calfacts._slices()["supported_fixed_major"]
    assert "08-06:sunday" not in enabled and "09-14:sunday" not in enabled


# ---- audited Source conflict statuses (user-approved; the status lives on the Rule, no DB needed) ----
def test_audited_conflict_statuses():
    from yocal_rules.rules import load_catalogue
    rules = {r["id"]: r for r in load_catalogue()[0]}
    want = {"pascha.ves.lihc": "misreading", "mf.ves.litia": "accepted", "mf.sun.ves.litia": "accepted", "mf.lent5.ves.litia": "accepted",
            "mf.jan1.sun.ves.litia": "accepted", "mf.nat.mon.ves.litia": "accepted", "mf.thy.mon.ves.litia": "accepted", "mf.nat.ves.litia": "accepted", "mf.thy.ves.litia": "accepted",
            "mf.lent5.mat.prokeimenon": "accepted", "mf.lent5.mat.praises": "misreading", "mf.jan1.sun.lit.epistle": "accepted",
            # unchanged
            "mf.lent5.ves.lihc": "accepted", "mf.sun.ves.lihc.presentation": "accepted", "mf.sun.mat.evlogetaria": "accepted",
            "mf.lent5.mat.evlogetaria": "accepted", "agape.lihc.george": "open", "mf.jan1.sun.mat.kathismata": "open",
            "mf.jan1.sun.lit.apolytikia": "open", "mf.jan1.sun.lit.megalynarion": "open", "mf.jan1.sun.lit.dismissal": "open",
            "mf.nat.mon.ves.readings": "open"}
    for rid, st in want.items():
        assert rules[rid]["conflict"]["status"] == st, rid
    note = rules["pascha.ves.lihc"]["conflict"]["note"]
    assert "Residual" in note and "Glory" in note


# ---- slices.yaml verified_years: pattern claims made explicit (fact + banner) ----
def test_slices_loader_keeps_plain_keys_and_verified_years():
    sl = calfacts._slices()
    assert "09-08:sunday" in sl["supported_fixed_major"] and "ascension" in sl["supported_movable_major"] and "agape" in sl["supported_pascha"]
    assert sl["verified_years"]["supported_fixed_major"]["09-08:sunday"] == [2019, 2024]
    assert sl["verified_years"]["supported_fixed_major"]["02-02:sunday"] == [2020, 2025]
    assert sl["verified_years"]["supported_fixed_major"]["01-01:sunday"] == [2023]
    assert sl["verified_years"]["supported_fixed_major"]["03-25:Monday"] == [2019] and sl["verified_years"]["supported_fixed_major"]["03-25:Wednesday"] == [2026]
    assert sl["verified_years"]["supported_fixed_major"]["03-25:sunday@-14"] == [2018]
    assert sl["verified_years"]["supported_major_eve_vespers"] == {"03-25:Sunday": [2019], "03-25:Tuesday": [2020, 2026]}
    assert sl["verified_years"]["supported_pascha"] == {"vespers": [2026], "matins": [2026], "liturgy": [2026], "agape": [2020, 2024, 2026]}
    assert sl["verified_years"]["supported_movable_major"] == {"ascension": [2026]}
    assert "supported_seasons" in sl and sl["verified_years"]["supported_seasons"] == {}                  # ordinary Sunday/season slices carry none


@needs_db
@pytest.mark.parametrize("date,svc,years,verified", [
    ("2024-09-08", "matins", [2019, 2024], True),                  # Sunday order, verified year
    ("2030-09-08", "matins", [2019, 2024], False),                 # same pattern, no ANCA text for this year
    ("2023-01-01", "liturgy", [2023], True),
    ("2022-12-31", "vespers", [2023], True),                       # eve Vespers: liturgical date's year
    ("2026-03-25", "liturgy", [2026], True),                       # day-only key 03-25:Wednesday
    ("2018-03-25", "matins", [2018], True),                        # sunday@-14
    ("2019-03-24", "vespers", [2019], True),                       # eve key 03-25:Sunday
    ("2020-03-24", "vespers", [2020, 2026], True),                 # eve key 03-25:Tuesday
    ("2026-05-21", "liturgy", [2026], True),                       # movable: ascension
    ("2026-04-12", "agape", [2020, 2024, 2026], True),
    ("2026-04-11", "vespers", [2026], True),
    ("2026-08-06", "matins", [2026], True),                        # plain mm-dd key
    ("2031-08-06", "matins", [2026], False),
])
def test_slice_verified_years_fact(date, svc, years, verified):
    f = calfacts.load_facts(dt.date.fromisoformat(date), svc)
    assert f["in_slice"] and f["slice_verified_years"] == years and f["verified"] is verified


@needs_db
@pytest.mark.parametrize("date,svc", [("2026-11-01", "matins"), ("2026-04-19", "matins"), ("2025-03-25", "matins"), ("2026-02-15", "liturgy")])
def test_slice_verified_years_empty_without_list_or_out_of_slice(date, svc):
    f = calfacts.load_facts(dt.date.fromisoformat(date), svc)                                            # ordinary Sunday, Thomas, Tuesday feast (out), Meatfare
    assert f["slice_verified_years"] == [] and f["verified"] is False


@needs_db
def test_verified_and_pattern_enabled_banners(tmp_path):
    for date, line in (("2024-09-08", "> **Verified** against ANCA 2019, 2024 (Rules pattern)."),
                       ("2030-09-08", "> **Pattern-enabled:** no ANCA text for this year; verified in 2019, 2024.")):
        assert cli.main([date, "matins", "--no-compare", "--out", str(tmp_path)]) == 0
        doc = (tmp_path / f"{date}-matins.md").read_text()
        assert doc.count(line + "\n") == 1 and "Incomplete" not in doc
        other = "Pattern-enabled" if "Verified" in line else "Verified"
        assert other not in doc
    assert cli.main(["2026-11-01", "matins", "--no-compare", "--out", str(tmp_path)]) == 0                  # ordinary Sunday: nothing new
    doc = (tmp_path / "2026-11-01-matins.md").read_text()
    assert "Verified" not in doc and "Pattern-enabled" not in doc and "Incomplete" not in doc
    assert cli.main(["2025-03-25", "matins", "--no-compare", "--out", str(tmp_path)]) == 0                  # out of slice: Incomplete only
    doc = (tmp_path / "2025-03-25-matins.md").read_text()
    assert "Incomplete" in doc and "Verified" not in doc and "Pattern-enabled" not in doc


@needs_db
def test_banner_does_not_change_slot_content(tmp_path):
    cli.main(["2030-09-08", "matins", "--no-compare", "--out", str(tmp_path)])
    banner = (tmp_path / "2030-09-08-matins.md").read_text()
    r = assemble.build("matins", dt.date(2030, 9, 8))
    assert all(x.status != "missing" for _, _, x in r.slots)
    body = banner.split("Pattern-enabled")[1].split("\n", 2)[2]
    assert body.startswith("## ") and "[to be determined]" not in body
