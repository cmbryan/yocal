"""Work package F: Triodion (Publican .. Cheesefare) and Great Lent Sundays (Lent 1-5, Palm Sunday)."""
import datetime as dt
import os

import pytest

from yocal_rules import anca, assemble, calfacts, cli, dcs
from yocal_rules.rules import load_catalogue

pytestmark = pytest.mark.skipif(not os.path.exists(calfacts.DEFAULT_DB), reason="calendar DB not built")
CACHE = os.path.join(os.environ.get("CLAUDE_JOB_DIR", ""), "tmp", "cache")


def _res(service, d, slot):
    r = assemble.build(service, dt.date.fromisoformat(d))
    return next(x for s, _, x in r.slots if s == slot)


def test_catalogue_loads_and_seasons_in_slice():
    load_catalogue()
    assert calfacts.load_facts(dt.date(2026, 2, 15), "matins")["in_slice"]  # Meatfare
    assert calfacts.load_facts(dt.date(2026, 3, 15), "matins")["in_slice"]  # Lent 3
    assert calfacts.load_facts(dt.date(2026, 3, 14), "vespers")["fore_after"] == ""


@pytest.mark.parametrize("sat,res,other", [
    ("2024-02-24", 7, [3]),     # Publican p.470
    ("2024-03-02", 7, [3]),     # Prodigal p.471
    ("2024-03-09", 6, [4]),     # Meatfare p.474
    ("2026-02-21", 6, [4]),     # Cheesefare p.475
    ("2026-03-14", 6, [4]),     # Lent 3 p.491
    ("2026-03-28", 6, [4]),     # Lent 5 (ANCA, Triodion)
    ("2026-04-04", 0, [10]),    # Palm Sunday p.504
    ("2026-01-31", 4, [3, 3]),  # Feb 1 on the Publican p.217
    ("2026-02-07", 4, [3, 3]),  # Sunday after the Presentation on the Prodigal p.225
    ("2025-03-08", 4, [3, 3]),  # Forty Martyrs on Lent 1 p.265
    ("2023-03-25", 4, [3, 3]),  # Annunciation leavetaking, Lent 4 eve p.289
    ("2024-03-23", 6, [4]),     # Annunciation forefeast on Lent 1: forefeast omitted
])
def test_vespers_stichera(sat, res, other):
    x = _res("vespers", sat, "vespers.lihc.stichera")
    assert (x.fill["res"], x.fill["other"]) == (res, other)


def test_prokeimenon_apolytikia():
    assert _res("vespers", "2026-03-28", "vespers.prokeimenon").fill["kind"] == "lord_is_king"
    assert _res("vespers", "2026-04-04", "vespers.prokeimenon").fill["tone"] == 6
    assert _res("matins", "2026-02-15", "matins.apolytikia").fill["saint"] is False
    assert _res("liturgy", "2026-03-22", "liturgy.apolytikia").fill["saint"] is True
    p = _res("liturgy", "2026-04-05", "liturgy.apolytikia").fill
    assert p["res_tone"] is None and p["saint"] is True


def test_praises_and_conflicts():
    x = _res("matins", "2026-03-08", "matins.praises")  # Lent 2: ANCA 8 followed, Typikon 9 shadowed
    assert (x.fill["total"], x.rule_id) == (8, "tri.mat.praises.lent2")
    assert "tri.mat.praises.lent2.typikon" in x.shadowed
    assert _res("matins", "2026-02-15", "matins.praises").fill["res"] == 5
    assert _res("matins", "2026-04-05", "matins.praises").fill["total"] == 4


def test_dismissal_and_author():
    assert _res("liturgy", "2026-02-22", "liturgy.dismissal").fill["saint_named"] is False
    assert _res("liturgy", "2026-03-08", "liturgy.dismissal").fill["saint_named"] is True
    assert _res("liturgy", "2025-03-09", "liturgy.dismissal").fill["saint_named"] is True  # Forty Martyrs
    assert _res("liturgy", "2026-03-15", "liturgy.author").fill["author"] == "Basil the Great"
    assert _res("liturgy", "2026-04-05", "liturgy.author").fill["author"] == "John Chrysostom"
    assert _res("liturgy", "2026-03-15", "liturgy.dismissal_phrase").fill["clause"] == "cross"


def test_unencoded_coincidences_are_missing():
    # Annunciation forefeast on Lent 2 (2019-03-24) and Theodore Tyro on the Publican (2019-02-17): not guessed
    assert _res("vespers", "2019-03-23", "vespers.lihc.stichera").status == "missing"
    assert _res("matins", "2019-02-17", "matins.praises").status == "missing"
    assert _res("liturgy", "2019-02-17", "liturgy.dismissal").status == "missing"


def test_anca_parsers_triodion_quirks():
    assert anca._liturgy_kontakion_kind("KONTAKION OF PALM SUNDAY IN TONE SIX") == "palm_sunday"
    sp = ("  For the Prodigal Son\n(Tone Two) Verse 6. Praise Him\n(Tone Four) Verse 7. Arise\n"
          "  For the Resurrection from the Octoechos\nVerse 1. x\n")
    assert anca.parse_praises(sp) == {"res": 1, "other": [2]}
    assert anca.split_abbr("a\nFestal Orthros on Palm Sunday Morning\nb")[1].strip() == "Morning\nb"
    url = anca.candidate_urls(dt.date(2026, 4, 5), "READ")[0]
    assert url.endswith("7-Palm-Sunday-READ.pdf")


def test_dcs_empty_shell_is_no_key(tmp_path, monkeypatch):
    class R:
        def read(self):
            return b"<html><body>Triodion</body></html>"  # HTTP 200, no data-key spans
    monkeypatch.setattr(dcs.urllib.request, "urlopen", lambda *a, **k: R())
    assert dcs.fetch(dt.date(2026, 2, 8), "ma", str(tmp_path)) is None
    k, _, notes = dcs.key_for("matins", dt.date(2026, 2, 8), str(tmp_path), offline=True)
    assert k == {} and notes


@pytest.mark.parametrize("sat", ["2026-03-14", "2026-02-07"])  # Lent 3 (Cross) and the Prodigal (Triodion)
def test_weekend_document(tmp_path, sat):
    assert cli.main(["weekend", sat, "--no-compare", "--out", str(tmp_path)]) == 0
    text = (tmp_path / f"{sat}-weekend.md").read_text(encoding="utf-8")
    assert "{tone}" not in text and "{sunday}" not in text
    assert "— Triodion" in text
    assert "Incomplete" not in text
    if sat == "2026-03-14":
        assert "6 resurrectional stichera — Octoechos Tone 7" in text
        assert "Prokeimenon of the Cross" in text and "Basil the Great" in text
    else:
        assert "3 stichera of the afterfeast of the Presentation" in text


@pytest.mark.skipif(not os.path.exists(os.path.join(CACHE, "anca-2026-03-15-READ.txt")), reason="ANCA cache not present")
def test_anca_compare_lent3_no_unexplained():
    for svc, d in (("vespers", "2026-03-14"), ("matins", "2026-03-15"), ("liturgy", "2026-03-15")):
        r = assemble.compare_keys(assemble.build(svc, dt.date.fromisoformat(d)), CACHE, offline=True, dcs_on=False)
        assert not [s for s, c in r.comparisons["anca"].items() if c.blocking], (svc, d)
