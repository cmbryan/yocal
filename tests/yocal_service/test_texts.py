"""ANCA heading -> hymn id ingestion, text verification (issue #64), crawl link choice. No network, no real store."""
import os

import pytest

from yocal_service import anca_texts as A, crawl, texts

F = {"principal_name": "Holy Apostle and Evangelist Matthew", "other_commem": "St. Fulvianus, prince of Ethiopia", "menaion_key": "11-16",
     "mmdd": "11-16", "pascha_days": -150, "major_feast": "", "feast_period": ""}
ff = lambda: F


@pytest.fixture(autouse=True)
def _isolated_sources(tmp_path, monkeypatch):
    monkeypatch.setenv("YOCAL_SOURCES", str(tmp_path / "sources"))


@pytest.mark.parametrize("heading,sub,want", [
    ("RESURRECTIONAL APOLYTIKION IN TONE SIX", [], "oct/t6/sun/apolytikion"),
    ("APOLYTIKION OF ST. MATTHEW THE EVANGELIST IN TONE THREE", [], "men/11-16/apolytikion"),
    ("KONTAKION OF ENTRANCE OF THE THEOTOKOS IN TONE FOUR", ["(**Thou Who wast raised up**)"], "men/11-21/kontakion"),
    ("ORDINARY KONTAKION IN TONE TWO (CHANT) (CHORAL)", [], "hor/kontakion/protection"),
    ("KONTAKION FOR SUNDAYS IN GREAT LENT IN TONE EIGHT", [], "men/03-25/kontakion"),
    ("KOINONIKON (COMMUNION HYMN) FOR THE APOSTLE IN TONE EIGHT", [], "lit/communion/common/apostle"),
    ("KOINONIKON OF PASCHA IN TONE EIGHT", [], "mov/0/communion"),
    ("PASCHAL APOLYTIKION IN TONE FIVE", [], "mov/0/troparion"),
    ("APOLYTIKION FOR MID-PENTECOST IN TONE EIGHT", [], "mov/24/apolytikion"),
    ("APOLYTIKION OF ST. GREGORY PALAMAS IN TONE EIGHT", [], "mov/-35/apolytikion"),
    ("APOLYTIKION OF SUNDAY BEFORE THE NATIVITY IN TONE TWO", [], "named/before_nativity/apolytikion"),
    ("KONTAKION OF THE FOREFEAST OF THEOTOKOS’ NATIVITY IN TONE THREE", [], "men/09-07/kontakion"),
    ("THE EPISTLE", ["(For the Sunday after Nativity of Christ)"], "named/after_nativity/prokeimenon"),
    ("THE EPISTLE", ["(For the 24th Sunday after Pentecost)"], "lit/sun/t6/prokeimenon"),
    ("THE EPISTLE", ["(For St. Matthew)"], "men/11-16/prokeimenon"),
])
def test_heading_names_the_hymn(heading, sub, want):
    assert A.heading_id(heading, sub, ff, 6) == (want, None)


@pytest.mark.parametrize("heading,sub,why", [
    ("APOLYTIKION OF ST. FULVIANUS IN TONE FOUR", [], "not the principal"),        # second commemoration: DCS numbering unknown
    ("APOLYTIKION OF ST. ARTEMIUS IN TONE FOUR", [], "not in the calendar"),
    ("THE EPISTLE", [], "owner not printed"),
    ("THE EPISTLE", ["(For the Saturday before Theophany)"], "weekday proper"),
    ("THE EPISTLE", ["(For the Saturday of Souls before Pentecost)"], "weekday proper"),
    ("THE EPISTLE", ["(For the Day before Pentecost)"], "weekday proper"),
    ("ORDINARY KONTAKION IN TONE SIX", [], "not in tone 2"),
    ("APOLYTIKION OF THE HOLY FATHERS IN TONE EIGHT", [], "which council"),
])
def test_ambiguous_headings_are_skipped(heading, sub, why):
    hid, reason = A.heading_id(heading, sub, ff, 6)
    assert hid is None and why in reason


def test_saint_spelling_variants_match():
    f = {**F, "principal_name": "Saint Theodosius the Great, the Cœnobiarch", "menaion_key": "01-11"}
    assert A.heading_id("APOLYTIKION OF ST. THEODOSIOS IN TONE EIGHT", [], lambda: f, 1)[0] == "men/01-11/apolytikion"


def test_holy_fathers_by_file_date():
    assert A.heading_id("APOLYTIKION OF THE HOLY FATHERS IN TONE EIGHT", [], lambda: {**F, "mmdd": "10-12"}, 1)[0] == "named/fathers_7th_council/apolytikion"
    assert A.heading_id("APOLYTIKION OF THE HOLY FATHERS IN TONE EIGHT", [], lambda: {**F, "pascha_days": 42}, 1)[0] == "mov/42/apolytikion"


READ = """   RESURRECTIONAL APOLYTIKION IN TONE SIX
When Mary stood at Thy grave, * looking for Thy sacred body.

   KOINONIKON (COMMUNION HYMN) OF PASCHA IN TONE EIGHT
Receive ye the Body of Christ. Alleluia. Alleluia. Alleluia.

   THE EPISTLE
   (For the 24th Sunday after Pentecost)
Save, O Lord, Thy people. Unto Thee, O Lord, have I cried. The reading from the Epistle. Brethren, ...
"""


def test_anca_ingest_by_heading(tmp_path):
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "anca-2025-11-16-READ.txt").write_text(READ, encoding="utf-8")
    tx = texts.Texts(str(tmp_path / "sources"))
    st = A.ingest(tx, texts.put, str(cache), lambda d: F)
    assert st["stored"] == 3
    assert tx.rows["anca"]["oct/t6/sun/apolytikion"]["tone"] == 6
    assert tx.rows["anca"]["mov/0/communion"]["text"] == "Receive ye the Body of Christ."  # Alleluia added when shown
    assert texts._split(tx.rows["anca"]["lit/sun/t6/prokeimenon"]["text"]) == ["Save, O Lord, Thy people.", "Unto Thee, O Lord, have I cried."]
    tx.save()
    assert os.path.exists(tmp_path / "sources" / "texts" / "anca.jsonl")


def _tx(tmp_path):
    tx = texts.Texts(str(tmp_path / "sources"))
    texts.put(tx, "dcs", "oc.m6.d1|ocVE.Apolytikion.text", "When Mary stood at Your grave, looking for Your sacred body, angelic powers shone.",
              "d", "2026-11-22", label="Resurrectional Apolytikion. Plagal of the Second Mode.")
    texts.put(tx, "anca", "oct/t6/sun/apolytikion", "When Mary stood at Thy grave, looking for Thy sacred body, angelic powers shone.", "a", "2025-11-16", tone=6)
    texts.put(tx, "dcs", "me.m01.d15|meVE.Apolytikion1.text", "From infancy fervently you loved the Lord.", "d", "2027-01-15", label="Apolytikion. For St. John. Mode 1.")
    texts.put(tx, "anca", "men/01-15/apolytikion", "The barren wilderness thou didst make fertile with thy tears.", "a", "2023-01-15", tone=8)
    texts.put(tx, "dcs", "me.m02.d02|meMA.Kontakion1.text", "You sanctified the womb.", "d", "2027-02-02", label="Apolytikion of the Feast. Mode 1.")
    return tx


def test_verify_statuses(tmp_path):
    res = texts.verify(_tx(tmp_path), {"oct/t6/sun/apolytikion": 400, "men/01-15/apolytikion": 10, "men/02-02/kontakion": 5, "men/09-09/kontakion": 3}, parish={},
                       principal=lambda mmdd: {"01-15": "Saint Paul of Thebes"}.get(mmdd, ""))
    r = res["ids"]
    assert r["oct/t6/sun/apolytikion"]["status"] == "agree" and not r["oct/t6/sun/apolytikion"]["notes"]  # plagal second = tone 6
    assert r["men/01-15/apolytikion"]["status"] == "conflict" and any("mode 1 vs tone 8" in n for n in r["men/01-15/apolytikion"]["notes"])
    assert any("calendar principal is 'Saint Paul of Thebes'" in n for n in r["men/01-15/apolytikion"]["notes"])
    assert r["men/02-02/kontakion"]["status"] == "label"  # DCS calls the text an apolytikion
    assert r["men/09-09/kontakion"]["status"] == "none"
    assert "conflict (1)" in texts.report(res)


def test_mode_of():
    assert texts.mode_of("Apolytikion. Mode 4.") == 4 and texts.mode_of("Plagal of the First Mode") == 5 and texts.mode_of("Grave Mode") == 7
    assert texts.mode_of("Kontakion.") is None


def test_crawl_picks_liturgy_variables_pdf():
    links = ["/servicetexts/x%20Orthros%20FINAL.pdf", "/servicetexts/x%20Variables%20Bilingual.pdf", "/servicetexts/x%20Variables%20FINAL.pdf",
             "/servicetexts/x%20Variables%20FINAL.rtf"]
    assert crawl._read_link(links) == "/servicetexts/x%20Variables%20FINAL.pdf"
    assert crawl._read_link(["/servicetexts/Nov%2016%202025%20READ.pdf"] + links) == "/servicetexts/Nov%2016%202025%20READ.pdf"
