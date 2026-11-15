from yocal_rules import dcs


def test_matins_prokeimenon_from_dcs_key():
    html = ("<span class='kvp' data-key='liturgical.verses_en_US_saas|psMA.sunday.m7.prokeimenon.v1.text'>"
            "Psalm 7</span>")
    k, _ = dcs.parse("matins", {"ma": html})
    assert k["matins.prokeimenon"] == dict(kind="resurrectional", tone=7)


def test_matins_prokeimenon_absent():
    k, _ = dcs.parse("matins", {"ma": ""})
    assert "matins.prokeimenon" not in k
