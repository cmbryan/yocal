import datetime as dt
from yocal_rules import calfacts


def test_named_sunday_before_theophany():
    assert calfacts.named_sunday(dt.date(2025, 1, 5)) == "before_theophany"
    assert calfacts.named_sunday(dt.date(2026, 1, 4)) == "before_theophany"
    assert calfacts.named_sunday(dt.date(2025, 1, 12)) is None


def test_kyriaki_sunday_epistle_owner_saint():
    from yocal_rules import rules
    f = calfacts.load_facts(dt.date(2024, 7, 7), "liturgy")
    assert f["epistle_owner"] == "saint"
