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


def _store(tmp_path):
    from yocal_service import texts
    tx = texts.Texts(str(tmp_path / "sources"))
    texts.put(tx, "dcs", "oc.m3.d1|ocVE.Apolytikion.text", "Let the heavens * rejoice.", "GOA DCS 2026-12-06 li", "2026-12-06")
    texts.put(tx, "dcs", "liturgical.verses|psLI.sunday.m3.alleluia.v1.text", "DCS verse one", "GOA DCS x", "2026-12-06")
    texts.put(tx, "parish", "lit/sun/t3/alleluia", "verse one\n\nverse two", "parish booklet B", "2025-12-21")
    texts.put(tx, "anca", "men/12-06/apolytikion", "A rule of faith.", "ANCA 2025-12-06", "2025-12-06")
    tx.save()
    return tx


@pytest.fixture(autouse=True)
def _isolated_sources(tmp_path, monkeypatch):
    """Never write test data into the real sources store."""
    monkeypatch.setenv("YOCAL_SOURCES", str(tmp_path / "sources"))


def test_texts_saved_as_sorted_jsonl_and_reloaded(tmp_path):
    from yocal_service import texts
    _store(tmp_path)
    lines = open(tmp_path / "sources" / "texts" / "dcs.jsonl", encoding="utf-8").read().splitlines()
    assert [l.split('"key": ')[1][:12] for l in lines] == sorted(l.split('"key": ')[1][:12] for l in lines)
    assert texts.get(texts.Texts(str(tmp_path / "sources")), "lit/sun/t3/alleluia", parish={})["parts"] == ["verse one", "verse two"]


def test_music_bytes_live_in_sources_store(tmp_path):
    from yocal_service import music
    con = db.connect(str(tmp_path / "m.db"))
    aid = music.upsert_asset(con, {"url": "https://x/a.pdf", "source": "dcs", "label": "L", "form": "western"}, "T")
    con.execute("UPDATE music_asset SET content=? WHERE id=?", (b"%PDF-1 test", aid))
    assert music.export_db_blobs(con) == 1
    data, mime = music.content(con, aid)
    assert data is None  # mime unknown in legacy row -> .bin name; fix up through the index on a fresh cache:
    con2 = db.connect(str(tmp_path / "m2.db"))
    a2 = con2.execute("select id from music_asset where url='https://x/a.pdf'").fetchone()[0]
    assert music.content(con2, a2)[0] == b"%PDF-1 test" and music.asset_info(con2, a2)["cached"]


def test_text_precedence_parish_dcs_anca(tmp_path):
    from yocal_service import texts
    con = _store(tmp_path)
    t = texts.get(con, "lit/sun/t3/alleluia", parish={})
    assert t["source"] == "parish" and t["parts"] == ["verse one", "verse two"] and not t["pending"]
    t = texts.get(con, "oct/t3/sun/apolytikion", parish={})
    assert t["source"] == "dcs" and t["pending"] and t["parts"] == ["Let the heavens rejoice."]  # phrase marker dropped
    assert texts.get(con, "men/12-06/apolytikion", parish={})["source"] == "anca"
    assert texts.get(con, "oct/t3/sun/apolytikion", parish={"oct/t3/sun/apolytikion": {"text": "Ours."}})["parts"] == ["Ours."]
    assert texts.get(con, "men/12-07/apolytikion", parish={}) is None  # not saved: a gap, no per-date fallback


def test_newer_copy_replaces_older(tmp_path):
    from yocal_service import texts
    con = _store(tmp_path)
    texts.put(con, "dcs", "oc.m3.d1|ocVE.Apolytikion.text", "old", "x", "2025-01-01")  # older copy: ignored
    assert texts.get(con, "oct/t3/sun/apolytikion", parish={})["parts"] == ["Let the heavens rejoice."]
    texts.put(con, "dcs", "oc.m3.d1|ocVE.Apolytikion.text", "new", "y", "2027-01-01")
    assert texts.get(con, "oct/t3/sun/apolytikion", parish={})["parts"] == ["new"]


def test_slots_render_rules_hymns_from_store(tmp_path):
    from yocal_service import compose as c
    from yocal_rules import hymns
    ctx = {"con": _store(tmp_path), "parish": {}, "pending": [],
           "hymns": {"liturgy.apolytikia": [hymns.Hymn("oct/t3/sun/apolytikion", "Resurrectional Apolytikion (Tone 3)", 3, "apolytikion"),
                                            hymns.Hymn("men/12-07/apolytikion", "Apolytikion of St Ambrose", None, "apolytikion")],
                     "liturgy.alleluia": [hymns.Hymn("lit/sun/t3/alleluia", "The Alleluia (Tone 3)", 3, "alleluia")],
                     "liturgy.kontakion": None}}
    ps = c.v_apolytikia(None, {}, ctx)
    assert [p["source"] for p in ps] == ["dcs_pending", "gap"] and ps[0]["hymn"] == "oct/t3/sun/apolytikion"
    assert [p["role"] for p in c.v_alleluia(None, {}, ctx)] == ["Choir", "Reader", "Choir", "Reader", "Choir"]
    assert c.v_kontakion(None, {}, ctx) == []  # the Rule names no hymn yet: the slot shows as missing
    assert [x["key"] for x in ctx["pending"]] == ["oct/t3/sun/apolytikion"]
    assert c.v_res_apolytikion(None, {}, ctx)[0]["text"] == "Let the heavens rejoice."


def test_dismissal_from_rules_and_calendar():
    from yocal_service import compose as c
    tpl = ("May [insert the appointed characteristic phrase], Christ our true God, of our father among the saints, John Chrysostom, archbishop of Constantinople; "
           "or Basil the Great, archbishop of Cæsarea whose Liturgy we have celebrated; of the holy and righteous ancestors of God, Joachim and Anna; "
           "of N., [the saint(s) of the day] whose memory we celebrate and of all the Saints")
    d = {"phrase": "he who rose from the dead", "phrase_kind": "resurrection", "clause": None, "author": "Basil the Great",
         "saints": "Holy Martyrs and Confessors Gurias (299), Samonas (306), and Abibus (Habib) (322), of Edessa"}
    t = c.v_dismissal(None, {}, {"dismissal": d}, template_text=tpl)[0]["text"]
    assert t.startswith("May he who rose from the dead,") and "Basil the Great, archbishop of Cæsarea, whose Liturgy" and "Chrysostom" not in t
    assert "of the holy martyrs and confessors Gurias, Samonas, and Abibus (Habib), of Edessa, whose memory" in t
    t = c.v_dismissal(None, {}, {"dismissal": dict(d, saints=None)}, template_text=tpl)[0]["text"]
    assert "Joachim and Anna; and of all the Saints" in t


@pytest.mark.skipif(not os.path.exists(template.TEMPLATE) or not os.path.exists("db/yocal/YOCal_Master.db"), reason="needs local template + calendar DB")
@pytest.mark.parametrize("date", ["2026-11-15", "2027-03-28", "2027-05-16", "2027-05-02",
                                  pytest.param("2026-11-22", marks=pytest.mark.xfail(strict=True, reason="festal antiphons still taken from the ANCA/DCS page (seasonal_hymns): needs Rules"))])
def test_rule_slots_do_not_depend_on_anca_or_dcs(tmp_path, monkeypatch, date):
    """Guard: the converted slots come from Rules + store only; with no ANCA/DCS page at all they are identical."""
    from yocal_service import compose as c
    monkeypatch.setenv("YOCAL_SOURCES", _store(tmp_path).root)
    run = lambda: {b["slot"]: b["paragraphs"] for s in c.compose(dt.date.fromisoformat(date), offline=True, fetch_music=False)["sections"]
                   for b in s["blocks"] if b["t"] == "variable" and b["slot"] in c.RESOLVERS}
    with_pages = run()

    def blank(self, date, offline):
        self.date, self.anca, self.dcs, self.dcs2 = date, [], [], []
    monkeypatch.setattr(c.Day, "__init__", blank)
    assert run() == with_pages
