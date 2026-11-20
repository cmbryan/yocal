"""Great Vespers booklet template (#85): section map, abbreviated-role extraction, fixed text vs Rules slots.
Template-dependent tests need the git-ignored local template (`python -m yocal_service.build_template PDF --service vespers`) and the calendar DB."""
import datetime as dt
import os
import re
import subprocess

import pytest
import yaml

from yocal_service import compose, template

SLOT_ORDER = ["vespers.kathisma", "vespers.lihc.stichera", "vespers.prokeimenon", "vespers.readings", "vespers.litia",
              "vespers.aposticha", "vespers.apolytikia"]
FEAST_ONLY = {"readings", "litia", "litia_litany", "artoklasia"}
FIXED_ORDER = ["opening", "psalm_103", "anoixantaria", "litany_peace", "little_litany", "litany_fervent", "evening_prayer", "litany_supplication", "bowing_heads"]
LEAK = re.compile(r"temple|zachari|holies|exodus|ezekiel|tent of|prelude|maiden", re.I)  # words of the booklet's Nov 21 propers
needs_template = pytest.mark.skipif(not template.available("vespers") or not os.path.exists("db/yocal/YOCal_Master.db"),
                                    reason="needs local vespers template + calendar DB")


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    """Never write test data into the real sources store or music cache."""
    monkeypatch.setenv("YOCAL_SOURCES", str(tmp_path / "sources"))
    monkeypatch.setenv("YOCAL_MUSIC_DB", str(tmp_path / "m.db"))


def _cfg():
    return yaml.safe_load(open(template.CONFIGS["vespers"], encoding="utf-8"))


def _slots(sec: dict) -> list:
    return ([sec["replace"]] if sec.get("replace") else []) + [sp["slot"] for sp in sec.get("spans", [])]


def test_vespers_section_map():
    cfg = _cfg()
    ids = [s["id"] for s in cfg["sections"]]
    assert len(ids) == len(set(ids))
    assert [x for s in cfg["sections"] for x in _slots(s)] == SLOT_ORDER
    assert all(s in compose.RESOLVERS and compose.ENGINE_SLOT[s] == s for s in SLOT_ORDER)
    rules_slots = yaml.safe_load(open("yocal_rules/data/rules/slots.yaml", encoding="utf-8"))
    assert {s for s in rules_slots if s.startswith("vespers.")} <= set(SLOT_ORDER)  # every Rules slot has a place in the service
    assert {s["id"] for s in cfg["sections"] if s.get("when_slot")} == FEAST_ONLY | {"little_litany"}
    assert ids.index("entrance") + 1 == ids.index("gladsome_light") and not _slots(cfg["sections"][ids.index("gladsome_light")])


def test_abbreviated_roles_wrapping_headings_and_cues():
    lines = ["   A rubric that is long enough to keep here.",
             "P: Blessed be the first petition, and",
             "   the wrapped part.",
             "C: Amen.",
             "    Second verse kept with the choir.",
             "   The deacon goes out now to the doors.",
             "                              A Centred Heading",
             "D: Peace be with all.          SETTING NEXT PAGE",
             "(Loudly):",
             "   Glory be now and ever."]
    got = [(b["t"], b.get("role", ""), b["text"]) for b in template.blocks_from(lines, {"P": "Priest", "D": "Deacon", "C": "Choir"})]
    assert got == [("rubric", "", "A rubric that is long enough to keep here."),
                   ("line", "Priest", "Blessed be the first petition, and the wrapped part."),
                   ("line", "Choir", "Amen. Second verse kept with the choir."),
                   ("rubric", "", "The deacon goes out now to the doors."),
                   ("line", "Deacon", "Peace be with all."),
                   ("line", "Deacon", "(Loudly) Glory be now and ever.")]
    assert all(b.get("role") != "Priest" for b in template.blocks_from(lines))  # abbreviations only when the config maps them


def test_vespers_template_text_is_git_ignored():
    path = os.path.relpath(template.TEMPLATES["vespers"])
    assert subprocess.run(["git", "check-ignore", "-q", path]).returncode == 0
    assert not subprocess.run(["git", "ls-files", os.path.dirname(path)], capture_output=True, text=True).stdout.strip()


@needs_template
def test_vespers_template_fixed_text_and_slots():
    secs = {s["id"]: s for s in template.load("vespers")["sections"]}
    assert [b["slot"] for s in secs.values() for b in s["blocks"] if b["t"] == "slot"] == SLOT_ORDER
    gl = secs["gladsome_light"]["blocks"]
    assert [b["role"] for b in gl] == ["Choir"] and gl[0]["text"].lower().startswith("gladsome light") and len(gl[0]["text"]) > 200
    assert any(b.get("role") == "Deacon" and b["text"].startswith("Wisdom") for b in secs["entrance"]["blocks"])
    for sid in ("psalter", "litia", "aposticha", "apolytikia"):  # wholly variable: nothing of the booklet's text kept
        assert [b["t"] for b in secs[sid]["blocks"]] == ["slot"]
    fixed = [b.get("text", "") for s in secs.values() for b in s["blocks"] if b["t"] != "slot"]
    assert not [t for t in fixed if LEAK.search(t)], "booklet Nov-21 propers leaked into fixed text"
    assert not [t for t in fixed if template.MUSIC_GLYPH.search(t) or template.SCORE_TITLE.search(t)]


@needs_template
def test_vespers_feast_eve_and_ordinary_saturday():
    def run(d):
        r = compose.compose(dt.date.fromisoformat(d), "vespers", offline=True, fetch_music=False)
        return r, {s["id"]: s for s in r["sections"]}

    r, secs = run("2026-11-20")  # eve of the Entrance: readings and Lity appointed by the Rules
    assert r["sections"] and not r["notes"]
    assert FEAST_ONLY <= set(secs)
    assert [b["slot"] for s in r["sections"] for b in s["blocks"] if b["t"] == "variable"] == SLOT_ORDER
    assert [b["t"] for b in secs["gladsome_light"]["blocks"]] == ["line"]
    var = {b["slot"]: b for s in r["sections"] for b in s["blocks"] if b["t"] == "variable"}
    assert var["vespers.readings"]["caption"] and var["vespers.kathisma"]["caption"] == ["No Rule decides this part yet."]

    r, secs = run("2026-11-14")  # ordinary Saturday: no readings, no Lity
    assert not FEAST_ONLY & set(secs)
    assert list(secs)[:3] == ["opening", "psalm_103", "anoixantaria"] and list(secs)[-2:] == ["closing", "dismissal"]
    assert any(p.get("hymn") == "oct/t7/sun/apolytikion" for b in secs["apolytikia"]["blocks"] for p in b["paragraphs"])


@needs_template
def test_vespers_fixed_litanies_and_prayers():
    tpl = {s["id"]: s for s in template.load("vespers")["sections"]}
    assert [i for i in tpl if i in FIXED_ORDER] == FIXED_ORDER  # booklet order
    assert tpl["little_litany"]["when_slot"] == "vespers.kathisma"  # follows the Psalter reading; Rules slot is #84
    lines = lambda i: [(b["role"], b["text"]) for b in tpl[i]["blocks"] if b["t"] == "line"]
    assert lines("opening")[0] == ("Priest", "Blessed is our God, always, now and for ever and to the ages of ages.")
    assert lines("opening")[1][1].count("Come, let us worship") == 3 and lines("opening")[1][0] == "Reader"
    assert tpl["psalm_103"]["blocks"][0]["role"] == "Reader" and tpl["psalm_103"]["blocks"][0]["text"].startswith("Bless the Lord, my soul")
    assert not tpl["anoixantaria"]["blocks"]  # score only
    assert lines("litany_peace")[0] == ("Deacon", "In peace let us pray to the Lord.") and lines("litany_peace")[-2][0] == "Priest"
    ff = lines("litany_fervent")
    assert ff[0][1].startswith("Let us all say") and ff[-1] == ("Choir", "Amen.") and any("[and for the servants of God N. & N." in t for _, t in ff)  # bracketed names kept as printed
    assert lines("evening_prayer")[0][0] == "Reader" and lines("evening_prayer")[0][1].startswith("Grant, Lord, to keep us this evening")
    assert lines("litany_supplication")[0][1].startswith("Let us complete our evening prayer")
    bh = lines("bowing_heads")
    assert [r for r, _ in bh[:4]] == ["Priest", "Choir", "Deacon", "Choir"] and bh[2][1].startswith("Bow your heads")
    assert bh[-2][1].startswith("(Loudly) May the might of Your kingdom") and bh[-1] == ("Choir", "Amen.")
    assert not any("Bow your heads" in t for _, t in lines("litany_supplication"))


@needs_template
def test_vespers_fixed_parts_render_in_order_without_slots():
    for d in ("2026-11-20", "2026-11-14"):  # feast eve; ordinary Saturday (no readings/Lity)
        ids = [s["id"] for s in compose.compose(dt.date.fromisoformat(d), "vespers", offline=True, fetch_music=False)["sections"]]
        got = [i for i in ids if i in FIXED_ORDER]
        assert got == [i for i in FIXED_ORDER if i != "little_litany"], d  # Little Litany waits for the kathisma Rule (#84)
        assert ids.index("prokeimenon") < ids.index("litany_fervent")  # fervent litany follows the prokeimenon even with no readings


@needs_template
def test_api_vespers_service():
    from yocal_service.app import create_app
    d = create_app().test_client().get("/api/service?date=2026-11-20&service=vespers&offline=1").get_json()
    assert d["service"] == "vespers" and "gladsome_light" in [s["id"] for s in d["sections"]]


def _texts(sec: dict) -> list:
    return [b.get("text", "") for b in sec["blocks"] if b["t"] != "variable"]


@needs_template
def test_vespers_closing_order_and_conditional_rubrics():
    def run(d):
        r = compose.compose(dt.date.fromisoformat(d), "vespers", offline=True, fetch_music=False)
        return [s["id"] for s in r["sections"]], {s["id"]: s for s in r["sections"]}

    ids, secs = run("2026-11-20")  # eve of the Entrance: Artoklasia appointed
    assert ids[ids.index("aposticha"):] == ["aposticha", "nunc_dimittis", "trisagion", "apolytikia", "closing", "dismissal"]
    assert ids.index("artoklasia") < ids.index("aposticha")
    assert secs["nunc_dimittis"]["blocks"][0]["text"].startswith("Now, Master")
    assert "Our Father" in secs["trisagion"]["blocks"][0]["text"] and secs["trisagion"]["blocks"][1]["role"] == "Priest"
    assert [b["t"] for b in secs["apolytikia"]["blocks"]] == ["variable"]
    assert secs["closing"]["blocks"][0]["text"] == "Let us pray to the Lord." and secs["closing"]["blocks"][2]["text"].startswith("The blessing of the Lord")
    assert any(t.startswith("Glory to you, Christ God") for t in _texts(secs["dismissal"]))
    assert _texts(secs["dismissal"])[-1].startswith("If there has been an Artoklasia")  # last block of the Dismissal
    assert not any("Akathist" in t for t in _texts(secs["nunc_dimittis"]))  # Lenten Fridays only
    assert any("the saint of the day" in t for t in _texts(secs["dismissal"]))  # placeholders printed as in the booklet (open question)

    ids, secs = run("2026-11-14")  # ordinary Saturday: no Artoklasia, no Akathist
    assert not any(t.startswith("If there has been an Artoklasia") for t in _texts(secs["dismissal"]))
    assert not any("Akathist" in t for t in _texts(secs["nunc_dimittis"]))
    assert ids[ids.index("nunc_dimittis"):] == ["nunc_dimittis", "trisagion", "apolytikia", "closing", "dismissal"]


def test_block_conditions():
    class X:
        def __init__(self, fill):
            self.fill = fill

    akathist = {"t": "rubric", "when": [{"season": "lent", "weekday": "Friday"}]}
    assert compose.block_shown(akathist, {"season": "lent", "weekday": "Friday"}, {})
    assert not compose.block_shown(akathist, {"season": "lent", "weekday": "Saturday"}, {})
    assert not compose.block_shown(akathist, {"season": "ordinary", "weekday": "Friday"}, {})
    art = {"t": "rubric", "when_slot": "vespers.litia", "when_fill": {"litia": True}}
    assert compose.block_shown(art, {}, {"vespers.litia": X({"litia": True})})
    assert not compose.block_shown(art, {}, {"vespers.litia": X({"litia": False})})  # Pascha: slot resolved, no Litia
    assert not compose.block_shown(art, {}, {})
    assert compose.block_shown({"t": "line"}, {}, {})
