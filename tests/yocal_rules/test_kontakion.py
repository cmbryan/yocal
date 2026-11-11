import datetime as dt

from yocal_rules import assemble


def _slot(service, d, slot):
    r = assemble.build(service, dt.date.fromisoformat(d))
    return next(x for s, _, x in r.slots if s == slot)


def test_liturgy_windows():
    cases = {
        "2021-11-07": "ordinary_theotokos", "2020-11-08": "entrance", "2022-07-03": "ordinary_theotokos",
        "2022-07-31": "transfiguration", "2022-11-27": "nativity_preparation", "2023-12-24": "nativity_preparation",
        "2025-02-09": "presentation", "2022-02-13": "pharisee_publican", "2022-03-13": "lent_sunday",
        "2022-04-10": "ordinary_theotokos", "2026-03-22": "lent_sunday", "2022-05-01": "pascha", "2022-06-05": "ascension",
    }
    for d, kind in cases.items():
        assert _slot("liturgy", d, "liturgy.kontakion").fill["kind"] == kind, d


def test_matins_kontakion():
    assert _slot("matins", "2022-07-03", "matins.kontakion").fill["kind"] == "resurrectional"
    assert _slot("matins", "2022-03-20", "matins.kontakion").fill["kind"] == "resurrectional"  # Lent 2
    assert _slot("matins", "2022-03-27", "matins.kontakion").fill["kind"] == "feast"  # Lent 3
    assert _slot("matins", "2022-05-08", "matins.kontakion").fill["kind"] == "feast"  # Pentecostarion
    assert _slot("matins", "2025-06-29", "matins.kontakion").fill["kind"] == "feast"  # Peter and Paul
    assert _slot("matins", "2022-06-26", "matins.kontakion").fill["kind"] == "resurrectional"  # All Saints of Antioch not yet kept
    assert _slot("matins", "2025-06-22", "matins.kontakion").fill["kind"] == "feast"


def test_entrance_afterfeast_sunday_2026_both_is_logged_divergence():
    from yocal_rules import compare
    d = dt.date(2026, 11, 22)
    r = assemble.build("matins", d)
    ours = next(x for s, _, x in r.slots if s == "matins.kontakion")
    assert ours.fill["kind"] == "resurrectional"  # Typikon; ANCA 2024-11-24 / 2025-11-23 agree
    c = compare.compare(ours, {"matins.kontakion": {"kind": "both"}}, "anca", r.facts, "matins", compare.load_divergence())
    assert c.state == "diff" and not c.blocking and c.cls == "divergence:anca_2026_resurrectional_plus_feast"


def test_liturgy_author():
    assert _slot("liturgy", "2022-03-13", "liturgy.author").fill["author"] == "Basil the Great"
    assert _slot("liturgy", "2022-07-03", "liturgy.author").fill["author"] == "John Chrysostom"
    from yocal_rules import calfacts
    assert calfacts.load_facts(dt.date(2022, 4, 10), "liturgy")["liturgy_author"] == "Basil the Great"
