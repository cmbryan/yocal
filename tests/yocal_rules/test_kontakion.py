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


def test_entrance_afterfeast_sunday_2026_follows_anca_both():
    from yocal_rules import compare
    d = dt.date(2026, 11, 22)
    r = assemble.build("matins", d)
    ours = next(x for s, _, x in r.slots if s == "matins.kontakion")
    assert ours.fill["kind"] == "both" and ours.rule_id == "mat.kontakion.anca_both.afterfeast"
    assert ours.shadowed and "mat.kontakion.default" in ours.shadowed  # Typikon reading kept shadowed
    c = compare.compare(ours, {"matins.kontakion": {"kind": "both"}}, "anca", r.facts, "matins", compare.load_divergence())
    assert c.state == "match"


def test_anca_both_starts_2026_june_and_keeps_pre_2026_and_pascha():
    assert _slot("matins", "2025-11-23", "matins.kontakion").fill["kind"] == "resurrectional"  # before ANCA's 2026 practice
    assert _slot("matins", "2026-05-31", "matins.kontakion").fill["kind"] == "feast"  # Pentecost: feast's only before 2026-06-07
    assert _slot("matins", "2026-04-12", "matins.kontakion").fill["kind"] == "feast"  # Pascha: its own kontakion, not 'both'
    assert _slot("matins", "2026-06-07", "matins.kontakion").fill["kind"] == "both"  # Sunday of All Saints
    assert _slot("matins", "2026-06-14", "matins.kontakion").fill["kind"] == "feast"  # All Saints of Antioch: own kontakion only


def test_anca_both_crosses_the_year_before_pascha():
    for d in ("2027-01-03", "2027-02-07"):  # forefeast of Theophany, afterfeast of the Meeting
        assert _slot("matins", d, "matins.kontakion").fill["kind"] == "both", d


def test_anca_both_not_where_resurrection_service_is_omitted():
    for d in ("2027-05-02", "2027-05-09", "2027-06-20", "2028-08-06", "2031-09-14", "2033-12-25"):  # Pascha, Thomas, Pentecost, Lord's feasts on a Sunday
        assert _slot("matins", d, "matins.kontakion").fill["kind"] == "feast", d


def test_anca_both_keeps_the_feast_owner():
    k = _slot("matins", "2026-11-08", "matins.kontakion")  # Archangels: Typikon feast rule decides the owner
    assert k.rule_id == "mat.kontakion.anca_both.feast" and k.fill["kind"] == "both"
    assert k.fill["owner"].startswith("the saint") and "mat.kontakion.listed_saints" in k.shadowed


def test_anca_both_hymns_entrance_afterfeast():
    from yocal_rules import hymns
    r = assemble.build("matins", dt.date(2026, 11, 22))
    k = next(x for s, _, x in r.slots if s == "matins.kontakion")
    assert [h.id for h in hymns.matins_kontakion(k.fill, r.facts)] == [
        "oct/t8/sun/kontakion", "oct/t8/sun/oikos", "men/11-21/kontakion"]


def test_liturgy_author():
    assert _slot("liturgy", "2022-03-13", "liturgy.author").fill["author"] == "Basil the Great"
    assert _slot("liturgy", "2022-07-03", "liturgy.author").fill["author"] == "John Chrysostom"
    from yocal_rules import calfacts
    assert calfacts.load_facts(dt.date(2022, 4, 10), "liturgy")["liturgy_author"] == "Basil the Great"
