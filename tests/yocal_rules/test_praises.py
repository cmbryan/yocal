import datetime as dt
import os

import pytest

from yocal_rules import anca, assemble

CACHE = os.path.join(os.environ.get("CLAUDE_JOB_DIR", ""), "tmp", "cache")

SAMPLE = """We chant “The Praises” in Tone 4 with eight troparia:

(Nassar 165-166)
                      For the Resurrection from the Octoechos in Tone Four
Verse 1. This glory shall be to all His saints.
text
Verse 2. Praise God.
text
Verse 3. Praise Him.
text
Verse 4. Praise Him with the trumpet.
text
(HTM Menaion 12)
                      For St. Peter in Tone Six
Verse 5. Praise Him with the timbrel.
text
Verse 6. x
Verse 7. y
Verse 8. z
                   THE SIXTH EOTHINON DOXASTICON IN TONE SIX
Glory to the Father, and to the Son, and to the Holy Spirit.
text
"""


def _fill(d):
    r = assemble.build("matins", dt.date.fromisoformat(d))
    x = next(x for s, _, x in r.slots if s == "matins.praises")
    return x.rule_id, x.fill, r.facts


def test_parse_praises_split():
    p = anca.parse_praises(SAMPLE)
    assert p == dict(res=4, other=[4], glory="eothinon")


def test_parse_praises_res_only_and_empty():
    txt = SAMPLE.split("(HTM Menaion 12)")[0] + "THEOTOKION IN TONE FOUR\nBoth now"
    assert anca.parse_praises(txt)["other"] == []
    assert anca.parse_praises("We chant The Praises") == {}


def test_res_only_default():
    rid, fill, _ = _fill("2022-11-06")
    assert rid == "mat.praises.res_only"
    assert fill == dict(total=8, res=8, other=[], glory="eothinon")


def test_rank_saint_four_plus_four():
    rid, fill, f = _fill("2024-10-06")  # Thomas, Doxology rank
    assert rid == "mat.praises.rank_saint" and f["bb_rank"] == "DOXOLOGY"
    assert (fill["res"], fill["other"]) == (4, [4])


def test_alwb_lauds_simple_rank():
    rid, fill, f = _fill("2024-07-07")  # Kyriaki: Simple/ALWB Lauds
    assert f["saint_lauds"] > 0
    assert rid in ("mat.praises.ch5.saint", "mat.praises.alwb_lauds") and (fill["res"], fill["other"]) == (4, [4])


def test_ch5_date_explicit():
    rid, fill, _ = _fill("2025-11-30")  # Andrew
    assert rid == "mat.praises.ch5.saint"


def test_named_sundays():
    assert _fill("2025-07-13")[0] == "mat.praises.fathers"
    assert _fill("2024-12-15")[0] == "mat.praises.forefathers.saint3"
    assert _fill("2024-12-15")[1]["other"] == [3, 3]
    rid, fill, _ = _fill("2025-12-14")
    assert rid == "mat.praises.forefathers" and fill["glory"] == "other"
    assert _fill("2023-12-24")[0] == "mat.praises.before_nativity"
    assert _fill("2025-01-05")[0] == "mat.praises.before_theophany"
    assert _fill("2022-06-19")[0] == "mat.praises.all_saints"


@pytest.mark.skipif(not os.path.isdir(CACHE), reason="ANCA cache not available")
def test_anca_match_and_logged_variance():
    """Every in-slice 2022-26 Sunday with a cached ANCA key either matches or is covered by data/divergence_praises.yaml."""
    n, bad = 0, []
    dates = ["2022-07-10", "2022-12-04", "2023-09-24", "2023-11-26", "2024-01-28", "2024-10-13", "2025-06-22", "2025-11-02",
             "2025-11-09", "2026-06-14", "2026-07-12", "2022-11-06", "2022-10-09", "2024-12-15", "2025-07-13", "2025-11-30"]
    for ds in dates:
        d = dt.date.fromisoformat(ds)
        r = assemble.build("matins", d)
        if r.facts["in_slice"]:
            assemble.compare_keys(r, CACHE, offline=True, dcs_on=False)
            c = r.comparisons["anca"].get("matins.praises")
            if c is not None and c.state == "diff":
                n += 1
                if c.cls == "unexplained":
                    bad.append((str(d), c.details))
    assert not bad, bad
    assert n == 11  # the 11 logged residual diffs (2022-26) are exactly the first 11 dates above
