import datetime as dt

from yocal_rules import anca, dcs


def _span(topic, field):
    return f"<span class='kvp' data-key='{topic}_en_US_x|{field}'>text</span>"


def test_dcs_festal_vespers_menaion_keys():
    t = "me.m11.d21"
    html = "".join(
        [_span(t, f"meVE.Stichera0{i}.text") for i in range(1, 7)]
        + [_span("liturgical.verses", "psVE.prokeimenon.friday.v1.text")]
        + [_span(f"le.pr.me.r{r}", "leprVE.reading.text") for r in (100, 101, 40)]
        + [_span(t, "meVE.Aposticha1.text"), _span(t, "meVE.Apolytikion1.text")])
    k, _ = dcs.parse("vespers", {"ve": html})
    assert k["vespers.lihc.stichera"] == dict(res=0, other=[6], total=6)
    assert k["vespers.prokeimenon"] == dict(kind="daily")
    assert k["vespers.readings"] == dict(count=3)
    assert k["vespers.aposticha"] == dict(owner="feast")
    assert k["vespers.apolytikia"] == dict(saint=True)


def test_dcs_octoechos_vespers_unaffected_by_festal_branch():
    html = _span("oc.m8.d6", "ocVE.Stichera01.text") + _span("me.m11.d21", "meVE.Stichera01.text")
    k, _ = dcs.parse("vespers", {"ve": html})
    assert k["vespers.lihc.stichera"] == dict(res=1)


def test_anca_entrance_files_mapped_to_2026():
    d = dt.date(2026, 11, 20)
    assert anca.candidate_urls(d, "VESP") == [anca.BASE + "/servicetexts/Nov%2020%20VESP.pdf"]
    d = dt.date(2026, 11, 21)
    assert anca.candidate_urls(d, "ORTHROS") == [anca.BASE + "/servicetexts/Nov%2021%20ORTHROS.pdf"]
    assert anca.candidate_urls(d, "READ") == [anca.BASE + "/servicetexts/Nov%2021%20READ.pdf"]


def test_dcs_festal_matins_menaion_keys():
    t = "me.m11.d21"
    html = "".join(
        [_span(t, "meVE.Apolytikion1.text"), _span(t, "meMA.Kontakion1.text"), _span("he.k", "ka.MM.Christmas1.title"),
         _span("le.go.ge.theotokos", "legeMA.Gospel.chapverse").replace(">text<", ">39 – 49, 56<")]
        + [_span(t, f"meMA.Lauds{i}.text") for i in range(1, 5)] + [_span(t, "meMA.LaudsGlory.text")])
    k, _ = dcs.parse("matins", {"ma": html})
    assert k["matins.apolytikia"] == dict(saint=True)
    assert k["matins.kontakion"] == dict(kind="feast")
    assert k["matins.praises"] == dict(res=0, other=[4], total=4)
    assert k["matins.katavasia"] == dict(of="nativity")
    assert k["matins.eothinon_gospel"] == dict(ref="39 – 49, 56")


def test_dcs_sunday_matins_unaffected_by_festal_branch():
    html = _span("oc.m8.d1", "ocMA.Kontakion1.text") + _span("me.m11.d21", "meMA.Kontakion1.text")
    k, _ = dcs.parse("matins", {"ma": html})
    assert k["matins.kontakion"] == dict(kind="resurrectional", tone=8)


def test_entrance_weekday_alleluia_uses_feast_verses_id():
    import datetime as dt
    from yocal_rules import assemble, calfacts, hymns
    r = assemble.build("liturgy", dt.date(2026, 11, 21), calfacts.DEFAULT_DB, False)
    res = next(x for s, m, x in r.slots if s == "liturgy.alleluia")
    assert [h.id for h in hymns.for_slot("liturgy.alleluia", res, r.facts)] == ["men/11-21/alleluia"]


def test_other_festal_alleluia_rules_name_feast_verses():
    import datetime as dt
    from yocal_rules import assemble, calfacts, hymns
    for d, hid in [(dt.date(2026, 12, 25), "men/12-25/alleluia"), (dt.date(2027, 1, 6), "men/01-06/alleluia"), (dt.date(2027, 6, 10), "mov/39/alleluia")]:
        r = assemble.build("liturgy", d, calfacts.DEFAULT_DB, False)
        res = next(x for s, m, x in r.slots if s == "liturgy.alleluia")
        assert [h.id for h in hymns.for_slot("liturgy.alleluia", res, r.facts)] == [hid], d
