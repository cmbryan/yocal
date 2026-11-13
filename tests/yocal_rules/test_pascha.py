"""Work package P: Pascha (data/rules/pascha.yaml): Holy Saturday Vesperal Liturgy, Paschal Matins, Paschal Liturgy, Agape Vespers."""
import datetime as dt
import os

import pytest

from yocal_rules import anca, assemble, calfacts, cli

needs_db = pytest.mark.skipif(not os.path.exists(calfacts.DEFAULT_DB), reason="calendar DB not built")
CACHE = os.path.join(os.environ.get("CLAUDE_JOB_DIR", ""), "tmp", "cache")


def slots(service, date):
    r = assemble.build(service, dt.date.fromisoformat(date))
    return r, {s: x for s, _, x in r.slots}


def _cached(date, kind):
    p = os.path.join(CACHE, f"anca-{date}-{kind}.txt")
    return os.path.exists(p) and os.path.getsize(p) > 0


# ---- slice and scope ----
@needs_db
def test_pascha_services_in_slice_bright_week_is_not():
    for svc, d in [("vespers", "2026-04-11"), ("matins", "2026-04-12"), ("liturgy", "2026-04-12"), ("agape", "2026-04-12")]:
        f = calfacts.load_facts(dt.date.fromisoformat(d), svc)
        assert f["in_slice"] and f["pascha_days"] == 0, (svc, f["slice_reasons"])
    assert calfacts.load_facts(dt.date(2026, 4, 13), "matins")["slice_reasons"] == ["not a Sunday"]  # Bright Monday: not modelled


@needs_db
def test_agape_only_on_pascha_day():
    with pytest.raises(assemble.OutOfScope):
        assemble.build("agape", dt.date(2026, 4, 19))
    with pytest.raises(assemble.OutOfScope):
        assemble.build("agape", dt.date(2026, 4, 11))


@needs_db
def test_pascha_years_fully_determined_no_missing():
    """Every Pascha 2018-2030: all four services build, in slice, no missing slot."""
    for y in range(2018, 2031):
        p = calfacts.pascha(y)
        for svc, d in [("vespers", p - dt.timedelta(days=1)), ("matins", p), ("liturgy", p), ("agape", p)]:
            r = assemble.build(svc, d)
            assert r.facts["in_slice"], (y, svc, r.facts["slice_reasons"])
            assert [s for s, _, x in r.slots if x.status == "missing"] == [], (y, svc)


# ---- Holy Saturday Vesperal Liturgy (Vespers part) ----
@needs_db
def test_holy_saturday_vespers_rules():
    r, v = slots("vespers", "2026-04-11")
    assert [s for s, _, _ in r.slots] == ["vespers.lihc.stichera", "vespers.prokeimenon", "vespers.readings", "vespers.litia", "vespers.aposticha", "vespers.apolytikia"]
    assert (v["vespers.lihc.stichera"].fill["res"], v["vespers.lihc.stichera"].fill["other"]) == (4, [4])  # 4R + 4 (#42 item 4)
    assert v["vespers.lihc.stichera"].rule["conflict"]["status"] == "misreading"  # count part (#42 item 4); Glory/Now wording residual in the note
    assert "Residual" in v["vespers.lihc.stichera"].rule["conflict"]["note"]
    assert v["vespers.prokeimenon"].fill["kind"] == "arise_o_god"
    assert v["vespers.readings"].fill["count"] == 15 and v["vespers.litia"].fill["litia"] is False


# ---- Paschal Matins ----
@needs_db
def test_paschal_matins_rules_and_slots():
    r, m = slots("matins", "2026-04-12")
    ids = [s for s, _, _ in r.slots]
    assert "matins.katavasia" in ids and "matins.evlogetaria" not in ids       # feast slots only where Pascha has an order for them
    assert m["matins.praises"].fill["total"] == 8 and m["matins.praises"].fill["other"] == [4] and m["matins.praises"].fill["res"] == 4
    assert m["matins.kontakion"].fill["kind"] == "feast" and m["matins.katavasia"].rule["source"] == "anca"


# ---- Paschal Liturgy ----
@needs_db
def test_paschal_liturgy_feast_slots():
    r, l = slots("liturgy", "2026-04-12")
    assert l["liturgy.antiphons"].fill["refrain2"] == "resurrection" and l["liturgy.trisagion"].fill["kind"] == "baptized"
    assert l["liturgy.final_hymn"].fill["kind"] == "christ_is_risen" and l["liturgy.megalynarion"].fill["kind"] == "feast"
    assert l["liturgy.prokeimenon"].rule_id == "pascha.lit.prokeimenon" and l["liturgy.prokeimenon"].status == "inferred"
    assert (l["liturgy.epistle"].fill["ref"], l["liturgy.gospel"].fill["ref"]) == ("Acts 1:1-8", "John 1:1-17")
    assert l["liturgy.dismissal"].fill["saint_named"] is False


# ---- Agape Vespers ----
@needs_db
@pytest.mark.parametrize("date,george", [("2026-04-12", False), ("2020-04-19", False), ("2025-04-20", False), ("2024-05-05", True), ("2021-05-02", True), ("2027-05-02", True)])
def test_agape_plain_vs_st_george(date, george):
    _, a = slots("agape", date)
    f = assemble.build("agape", dt.date.fromisoformat(date)).facts
    assert f["bright_monday_george"] is george
    st = a["agape.lihc.stichera"]
    assert (st.fill["res"], st.fill["other"]) == ((4, [4]) if george else (6, []))
    assert a["agape.apolytikia"].fill["saint"] is george and a["agape.dismissal"].fill["saint_named"] is george
    assert a["agape.aposticha"].fill["glory"] == ("saint" if george else "pascha")
    assert (a["agape.prokeimenon"].fill["kind"], a["agape.prokeimenon"].fill["tone"]) == ("great", 7)
    assert a["agape.gospel"].fill["ref"] == "John 20:19-20; John 20:21-23; John 20:24-25"  # DB lection (three Gospel readings)
    assert bool(st.rule.get("conflict")) is george and (not george or st.rule["conflict"]["status"] == "open")


# ---- documents ----
@needs_db
@pytest.mark.parametrize("date,service", [("2026-04-11", "vespers"), ("2026-04-12", "matins"), ("2026-04-12", "liturgy"), ("2026-04-12", "agape"), ("2024-05-05", "agape")])
def test_documents_complete(tmp_path, date, service):
    assert cli.main([date, service, "--no-compare", "--out", str(tmp_path)]) == 0
    doc = (tmp_path / f"{date}-{service}.md").read_text()
    assert "Incomplete" not in doc and "[to be determined]" not in doc and "{" not in doc
    if service == "agape":
        assert doc.startswith("# Agape Vespers")
    if service == "vespers":
        assert doc.startswith("# Vesperal Liturgy of Holy Saturday")


@needs_db
def test_pascha_weekend_adds_agape(tmp_path):
    assert cli.main(["weekend", "2026-04-11", "--no-compare", "--out", str(tmp_path)]) == 0
    names = {p.name for p in tmp_path.iterdir()}
    assert {"2026-04-11-vespers.md", "2026-04-12-matins.md", "2026-04-12-liturgy.md", "2026-04-12-agape.md", "2026-04-11-weekend.md"} <= names


# ---- ANCA parsers on synthetic text (no cache needed) ----
def test_parse_holy_saturday_counts():
    txt = ("“O LORD I HAVE CRIED” IN TONE ONE\nVerse 10. a\nVerse 9. b\n\n    For the Resurrection in Tone One\n"
           + "".join(f"Verse {n}. x\nhymn\n" for n in (8, 7, 6, 5)) + "\n    For the Harrowing of Hades in Tone Eight\n"
           + "".join(f"Verse {n}. x\nhymn\n" for n in (4, 3, 2, 1)) + "DOXASTICON FOR HOLY SATURDAY\n"
           "The Daily Prokeimenon is not sung on this day.\nTHE ANTI-ALLELUARION IN TONE SEVEN\n"
           + "Reader:  The reading from the book of Genesis. (1:1)\nReader:  The reading from the Prophecy of Isaiah. (60:1)\n"
           "Reader:  The reading from the Epistle of St. Paul to the Romans. (6:3-11)\n")
    k = anca.parse_holy_saturday(txt)
    assert k["vespers.lihc.stichera"] == {"res": 4, "other": [4], "total": 8}
    assert k["vespers.prokeimenon"] == {"kind": "arise_o_god", "tone": 7} and k["vespers.readings"] == {"count": 2}


def test_parse_agape_page_header_inside_dismissal():
    txt = ("“O LORD I HAVE CRIED” IN TONE TWO\n    For the Resurrection in Tone Two\nVerse 6. a\nh\nVerse 5. a\nh\nDOXASTICON FOR THE RESURRECTION\n"
           "APOSTICHON FOR THE RESURRECTION IN TONE TWO\nTHE PASCHAL STICHERA IN TONE FIVE\nTHE DISMISSAL\nof the holy and righteous ancestors of God, Joachim and\n"
           "Agape Vespers        Great Vespers 9        with St. George\nAnna; of the holy Great-martyr George the trophy-bearer, whose\nmemory we celebrate today, and of all the saints: have mercy\n")
    k = anca.parse_agape(txt)
    assert k["agape.dismissal"] == {"saint_named": True} and k["agape.lihc.stichera"]["res"] == 2 and k["agape.aposticha"]["glory"] == "pascha"


def test_parse_paschal_vigil_outline():
    txt = ("4.    The Priest then reads the Gospel: Mark 16:1-8 (2nd Eothinon Gospel).\n"
           "    g. To be read:\n        Kontakion: “Though Thou, O deathless one…”\n"
           "NOTE: The Irmos is repeated.\n           Katavasia (repeat the Irmos): “Today is the day”\n"
           "8.    Praises (Ainoi) in Tone 1:\n  a.  4 stichera for the Resurrection in Tone 1\n  b.  4 Pascha Stichera (Paschals)\n  c.  Doxasticon: Glory...\n"
           "9.    Following either the Doxasticon\n")
    k = anca.parse_paschal_vigil(txt)
    assert k["matins.eothinon_gospel"] == {"number": 2} and k["matins.kontakion"] == {"kind": "feast"} and k["matins.katavasia"] == {"of": "feast"}
    assert k["matins.praises"] == {"total": 8, "res": 4, "other": [4], "glory": "other"}


def test_parse_pascha_liturgy_final_hymn():
    assert anca.parse_feast_liturgy("• Instead of “We have seen the true light,” sing “Christ is Risen” ONCE.")["liturgy.final_hymn"] == {"kind": "christ_is_risen"}


# ---- ANCA key check against cached texts (skipped without the cache) ----
@needs_db
@pytest.mark.parametrize("date,svc,kind", [("2026-04-11", "vespers", "VDL"), ("2026-04-12", "matins", "VIGIL"), ("2026-04-12", "liturgy", "READ"),
                                           ("2026-04-12", "agape", "VESP"), ("2024-05-05", "agape", "VESP"), ("2020-04-19", "agape", "VESP")])
def test_pascha_no_unexplained_anca_diff(tmp_path, date, svc, kind):
    if not _cached(date, kind):
        pytest.skip("ANCA text not cached")
    assert cli.main([date, svc, "--offline", "--cache", CACHE, "--fail-on-diff", "--out", str(tmp_path)]) == 0
    r = assemble.build(svc, dt.date.fromisoformat(date))
    assemble.compare_keys(r, CACHE, offline=True, dcs_on=False)
    states = [c.state for c in r.comparisons["anca"].values()]
    assert "diff" not in states and "key_only" not in states and states.count("match") >= 3
