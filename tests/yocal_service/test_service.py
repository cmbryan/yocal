import datetime as dt
import os
import sqlite3

import pytest

from yocal_service import anca_read, db, dcs_page, music, template

DCS_ROW = """<tr><td><p class='designation'><span class='kvp' data-key='titles_en_US_goa|ti.Antiphon1'>Antiphon 1. Mode 2.</span></p></td></tr>
<tr><td><span class='kvp' data-key='p|media.key'><div class='media-group'><ul>
<li><a href='js/viewer/web/viewer.html?file=/media/m/dedes/en/eu/lichrysbasil/w/antiphon1.pdf'><span class='mediaMenuItemPeople'>SDedes</span></a></li>
<li><a href='js/viewer/web/viewer.html?file=/media/m/thyateira/en/eu/lichrysbasil/b/antiphon1.pdf'><span class='mediaMenuItemPeople'>Thyateira</span></a></li>
</ul></div></span></td></tr>"""


def test_dcs_media_grouped_under_designation():
    rows = dcs_page.parse(DCS_ROW)
    media = [r for r in rows if r["kind"] == "media"][0]
    assert media["title"] == "Antiphon 1. Mode 2."
    assert [a["form"] for a in media["assets"]] == ["western", "byzantine"]
    assert media["assets"][0]["url"].startswith("https://dcs.goarch.org/media/m/dedes/")


def test_match_orders_anca_before_dcs():
    anca = [{"source": "anca", "url": "https://x/musiclibrary/a.pdf", "title": "", "label": "", "context": "RESURRECTIONAL APOLYTIKION IN TONE SEVEN", "form": "score"}]
    dcs = music.dcs_candidates(dcs_page.parse(DCS_ROW))
    got = music.match({"key": "k", "title": "t", "anca": "RESURRECTIONAL APOLYTIKION", "dcs": r"^antiphon1\."}, anca, dcs)
    assert [c["source"] for c in got] == ["anca", "dcs", "dcs"]
    assert "thyateira" in got[1]["url"] or "thyateira" in got[2]["url"]


def test_cache_roundtrip_keeps_source(tmp_path):
    con = db.connect(str(tmp_path / "m.db"))
    c = {"source": "dcs", "url": "https://dcs.goarch.org/media/m/dedes/en/eu/lichrysbasil/w/antiphon1.pdf", "label": "SDedes", "form": "western"}
    assets = music.record(con, "liturgy", dt.date(2026, 11, 15), "antiphon1", "Antiphon 1", [c, dict(c, url=c["url"].replace("dedes", "thyateira"), label="Thyateira")])
    assert [a["cached"] for a in assets] == [False, False]
    assert {a["source"] for a in assets} == {"dcs"}
    # a date without its own links reuses the last stored refs for the slot
    assert len(music.previous_refs(con, "liturgy", "antiphon1")) == 2


def test_anca_read_blocks():
    txt = "   RESURRECTIONAL APOLYTIKION IN TONE SEVEN (KAZAN)\nThou didst abolish death.\n\n   THE GOSPEL\n   (For the Eighth Sunday of Luke)\nThe reading from the holy Gospel according to St. Luke. (10:25-37)\nAt that time.\n"
    b = anca_read.parse(txt)
    assert [x["heading"] for x in b] == ["RESURRECTIONAL APOLYTIKION IN TONE SEVEN (KAZAN)", "THE GOSPEL"]
    assert b[1]["sub"] == ["(For the Eighth Sunday of Luke)"]


def test_template_noise_filter_and_spans():
    assert template.is_noise("  Lord,    have mer - cy.   Lord, have mer - cy. - men")
    assert not template.is_noise("Priest: Blessed is our God, always, now and ever.")
    raw = ["Deacon: Wisdom!", "Reader: The reading is from X", "The reader turns westward", "Deacon: Let us attend."]
    out = template.apply_spans(raw, [{"after": "^Deacon: Wisdom!$", "until": "^The reader turns", "slot": "epistle_intro"}])
    assert out[1] == "@@SLOT:epistle_intro@@"
    blocks = template.blocks_from(out)
    assert [b["t"] for b in blocks] == ["line", "slot", "rubric", "line"][:len(blocks)] or blocks[1]["t"] == "slot"


@pytest.mark.skipif(not os.path.exists(template.TEMPLATE) or not os.path.exists("db/yocal/YOCal_Master.db"), reason="needs local template + calendar DB")
def test_api_service_and_date_validation(tmp_path, monkeypatch):
    monkeypatch.setenv("YOCAL_MUSIC_DB", str(tmp_path / "m.db"))
    from yocal_service.app import create_app
    c = create_app().test_client()
    r = c.get("/api/service?date=2026-11-15&offline=1")
    assert r.status_code == 200
    d = r.get_json()
    assert d["service"] == "liturgy" and d["tone"] == 7 or d["tone"] == "7"
    assert [s["id"] for s in d["sections"]][:2] == ["enarxis", "litany_peace"]
    assert c.get("/api/service?date=2026-11-12").status_code == 422
    assert c.get("/api/service?date=2026-11-15&service=vespers").status_code == 404
    assert c.get("/api/services").get_json() == [{"id": "liturgy", "title": "Divine Liturgy"}]


def test_seasonal_conditions():
    from yocal_service import compose as c
    bright = [{"pascha_days": [0, 6]}, {"pascha_days": [38, 38]}]
    assert c.applies(bright, {"pascha_days": 0}) and c.applies(bright, {"pascha_days": 38})
    assert not c.applies(bright, {"pascha_days": 7}) and not c.applies(bright, {"pascha_days": -300})
    assert c.applies([{"pascha_days": [7, 37]}], {"pascha_days": 14})
    assert c.applies([{}], {})  # always


def test_inline_seasonal_strips_brackets_and_condition():
    from yocal_service import compose as c
    b = {"t": "seasonal", "label": "Deacon serving", "strip": r"^\[?Omitted if a deacon is not serving:\s*",
         "blocks": [{"t": "rubric", "text": "[Omitted if a deacon is not serving: He faces the people."}, {"t": "line", "role": "Deacon", "text": "And for all.]"}]}
    out = c.inline_seasonal(b)
    assert out[0]["text"] == "He faces the people." and out[1]["text"] == "And for all." and out[0]["seasonal"] == "Deacon serving"


def test_translation_key_and_resolve():
    from yocal_service import translations as t
    blk = {"heading": "THE EISODIKON OF PASCHA (CHANT)", "body": ["In the gathering places bless God."]}
    k = t.key(blk["heading"], blk["body"])
    assert k.startswith("the-eisodikon-of-pascha:")
    ps, k2, pending = t.resolve(blk, store={})
    assert pending and ps[0]["source"] == "anca_pending" and k2 == k
    ps, _, pending = t.resolve(blk, store={k: {"text": "Our own.\n\nSecond."}})
    assert not pending and [p["text"] for p in ps] == ["Our own.", "Second."] and ps[0]["source"] == "parish"


def test_seasonal_hymn_replaces_booklet_blocks():
    from yocal_service import compose as c, anca_read
    class D:
        def ablocks(self, rx): return anca_read.find([{"heading": "THE ANTI-TRISAGION HYMN", "sub": [], "body": ["As many as are baptised."]}], rx)
    cfg = [{"anca": "^THE ANTI-TRISAGION", "section": "trisagion", "lead": {"role": "Choir", "text": "Amen."},
            "drop": [{"text": "^Amen\\. Holy God"}, {"role": "^Choir$", "text": "^$"}]}]
    blocks = [{"t": "line", "role": "Priest", "text": "For you"}, {"t": "line", "role": "Choir", "text": "Amen. Holy God, Holy Mighty"},
              {"t": "line", "role": "Choir", "text": ""}, {"t": "line", "role": "Deacon", "text": "Let us attend!"}]
    pend = []
    out = c.seasonal_hymns(D(), "trisagion", blocks, cfg, {}, pend)
    assert [b.get("text") or b["t"] for b in out] == ["For you", "Amen.", "variable", "Let us attend!"] and len(pend) == 1
    assert c.seasonal_hymns(D(), "other", blocks, cfg, {}, pend) == blocks


def test_anca_read_wrapped_heading():
    from yocal_service import anca_read
    b = anca_read.parse("KONTAKION FOR SUNDAYS IN GREAT LENT\nIN TONE EIGHT (CHANT)\nTo thee, the Champion.\n")
    assert len(b) == 1 and b[0]["body"] == ["To thee, the Champion."]


def test_communion_hymn_follows_rule_then_anca():
    from yocal_service import compose as c, anca_read
    class D:
        def __init__(s, anca): s.anca = anca; s.dcs = []
        def ablocks(s, rx): return anca_read.find(s.anca, rx)
        def dfirst(s, *a): return None
    eng = lambda k: {"liturgy.communion": {"fill": {"kind": k}}}
    # ANCA file with no Koinonikon heading -> Sunday hymn even if the Rule says saint (project default: follow ANCA)
    anca = [{"heading": "THE EPISTLE", "sub": [], "body": ["x"]}]
    assert c.v_communion_hymn(D(anca), {}, engine=eng("saint"))
    assert c.v_communion_hymn(D([]), {}, engine=eng("saint")) == []  # no ANCA file: the saint's hymn has no text here
    assert c.v_communion_hymn(D([]), {}, engine=eng("praise_the_lord"))


def test_translation_applies_to_other_headings():
    from yocal_service import translations as t
    store = {"koinonikon-for-st-luke:aaaa": {"text": "Our hymn.", "applies_to": ["^koinonikon-(for|of)-(st-)?(luke|mark)"]}}
    mark = {"heading": "KOINONIKON FOR ST. MARK IN TONE EIGHT", "body": ["His sound."]}
    ps, _, pend = t.resolve(mark, store=store)
    assert not pend and ps[0]["text"] == "Our hymn." and ps[0]["source"] == "parish"
    other = {"heading": "KOINONIKON FOR ST. PAUL", "body": ["x"]}
    assert t.resolve(other, store=store)[2]


def test_booklet_readings_selection(monkeypatch):
    from yocal_service import booklet_readings as b
    L = [["Reader", "r"], ["Choir", "c"]]
    items = [{"booklet": "A", "date": "2025-11-23", "sunday_tone": 7, "prokeimenon": {"title": "The Prokeimenon (Tone 7)", "tone": 7, "lines": L}, "alleluia": {"title": "The Alleluia (Tone 7)", "tone": 7, "lines": L}},
             {"booklet": "B", "date": "2025-12-14", "sunday_tone": 2, "prokeimenon": {"title": "Prokeimenon for the Forefathers (Tone 8)", "tone": 8, "lines": L}},
             {"booklet": "C", "date": "2026-11-08", "sunday_tone": 6, "prokeimenon": {"title": "The Prokeimenon (Tone 4)", "tone": 4, "lines": L}}]  # Archangels: not the Sunday tone
    monkeypatch.setattr(b, "load", lambda: items)
    assert b.select("prokeimenon", {"tone": 7, "desig": "x", "desig_g": ""})["booklet"] == "A"
    assert b.select("prokeimenon", {"tone": 4, "desig": "x", "desig_g": ""}) is None  # the saint's Tone 4 item is skipped
    assert b.select("prokeimenon", {"tone": 3, "desig": "Sunday of the Holy Forefathers", "desig_g": ""})["booklet"] == "B"
    assert b.select("alleluia", {"tone": 3, "desig": "x", "desig_g": ""}) is None


def test_alleluia_uses_tone_of_week_from_dcs_table(monkeypatch):
    from yocal_service import compose as c, dcs_tones, booklet_readings
    monkeypatch.setattr(booklet_readings, "select", lambda kind, f: None)
    monkeypatch.setattr(dcs_tones, "get", lambda tone: {"source": "S", "alleluia": {"v1": "verse one", "v2": "verse two"}} if tone == 3 else {})
    ps = c.v_alleluia(None, {"tone": 3})
    assert [p["role"] for p in ps] == ["Choir", "Reader", "Choir", "Reader", "Choir"] and ps[0]["heading"] == "The Alleluia (Tone 3)" and ps[1]["credit"] == "S"
    assert c.v_alleluia(None, {"tone": 5})[-1]["source"] == "gap"  # no verses for that tone: flagged, not invented
