import datetime as dt
import os

import pytest
from yocal_rules import assemble, calfacts, compare
from yocal_rules.rules import Resolution

needs_db = pytest.mark.skipif(not os.path.exists(calfacts.DEFAULT_DB), reason="calendar DB not built")


def test_named_sunday_before_theophany():
    assert calfacts.named_sunday(dt.date(2025, 1, 5)) == "before_theophany"
    assert calfacts.named_sunday(dt.date(2026, 1, 4)) == "before_theophany"
    assert calfacts.named_sunday(dt.date(2025, 1, 12)) is None


def test_kyriaki_sunday_epistle_owner_saint():
    from yocal_rules import rules
    f = calfacts.load_facts(dt.date(2024, 7, 7), "liturgy")
    assert f["epistle_owner"] == "saint"


# ---- regression: 2022-26 ANCA sweep diffs on general Sunday Rules
@needs_db
@pytest.mark.parametrize("d,ref,rid", [(dt.date(2025, 6, 22), "Acts 11:19-30", "db.liturgy.epistle"),
                                       (dt.date(2026, 6, 14), "Acts 11:19-30", "db.liturgy.epistle"),
                                       (dt.date(2023, 6, 18), "Acts 11:19-30", "db.liturgy.epistle")])
def test_all_saints_of_antioch_epistle_follows_db_every_year(d, ref, rid):
    x = {s: v for s, _, v in assemble.build("liturgy", d).slots}["liturgy.epistle"]
    assert x.fill["owner"] == "saint" and x.fill["ref"] == ref and x.rule_id == rid


def test_anca_typo_dismissal_phrase_2024_02_11_is_logged_divergence():
    slot = "liturgy.dismissal_phrase"
    res = Resolution(slot, "explicit", {"id": "lit.dismissal_phrase.sunday"}, {"phrase": "resurrection"})
    k = {slot: {"phrase": "feast_and_resurrection", "clause": "none"}}
    log = compare.load_divergence()
    c = compare.compare(res, k, "anca", dict(date="2024-02-11", mmdd="02-11"), "liturgy", log)
    assert c.state == "diff" and not c.blocking and c.cls == "divergence:anca_typo"
    assert compare.compare(res, k, "anca", dict(date="2024-02-18", mmdd="02-18"), "liturgy", log).blocking
