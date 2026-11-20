"""Issue #88: ANCA LITART ingest (heading-keyed) and scores per hymn id. Synthetic texts only; no network, temp store."""
import io

import pytest

from yocal_service import anca_texts as A, db, music, store

F = {"principal_name": "Entrance of the Theotokos", "other_commem": "", "menaion_key": "11-21", "mmdd": "11-21",
     "pascha_days": -150, "major_feast": "entrance", "feast_period": ""}

# Layout as pdftotext -layout prints ANCA LITART files (placeholder words, not hymn text)
LITART = """\
           The Litia and Artoklasia of November 21
                 Entrance of the Theotokos
                (served on the evening prior)

   At the discretion of the pastor, the other litia hymns from the Menaion may be chanted before
    the doxasticon.

          DOXASTICA AT THE LITIA PROCESSION IN TONE FIVE
Glory to the Father, and to the Son, and to the Holy Spirit.
Alpha beta gamma delta
epsilon zeta.

Both now and ever, and unto ages of ages. Amen.
Eta theta iota.

   After the Litia hymns are chanted stichirarically (slowly), the clergy begin.

                                  The Litia
Deacon:        Have mercy on us, O God.
Choir:         Lord, have mercy. (THRICE)
November 20, 2026                  Litia/Artoklasia 1             Entrance of Theotokos
                                The Artoklasia
                 THEOTOKION IN TONE FIVE (BP BASIL) (EL MASSIH)
Clergy:        Kappa lambda mu
               nu xi;
Choir:         Omicron pi.
Deacon:        Let us pray to the Lord.
Choir:         Lord, have mercy.

   The clergy sing the following troparion once, and then the choir sings it twice.

                             TROPARION IN TONE SEVEN
Rho sigma tau
upsilon.

   Great Vespers resumes with the aposticha.
                                   THE GREAT DISMISSAL
"""


@pytest.fixture(autouse=True)
def _isolated_sources(tmp_path, monkeypatch):
    monkeypatch.setenv("YOCAL_SOURCES", str(tmp_path / "sources"))


def test_litart_headings_name_the_hymns():
    out, st = A.litart_blocks(LITART, lambda: F)
    got = {h: (t, tone) for h, t, _, tone in out}
    assert got == {"men/11-21/doxastikonlity": ("Alpha beta gamma delta epsilon zeta.", 5),
                   "men/11-21/doxastikonlitynow": ("Eta theta iota.", 5),
                   "lit/vespers/theotoke_parthene": ("Kappa lambda mu nu xi; Omicron pi.", 5),
                   "lit/vespers/artoklasia_ps33": ("Rho sigma tau upsilon.", 7)}
    assert not st


def test_litart_one_glory_now_and_unclear_owner_skipped():
    one = LITART.replace("Glory to the Father, and to the Son, and to the Holy Spirit.",
                         "Glory to the Father, and to the Son, and to the Holy Spirit; both now and\never, and unto ages of ages. Amen.")
    one = one.replace("Both now and ever, and unto ages of ages. Amen.\nEta theta iota.\n", "")
    out, _ = A.litart_blocks(one, lambda: F)
    assert [h for h, *_ in out][:1] == ["men/11-21/doxastikonlity"] and out[0][1] == "Alpha beta gamma delta epsilon zeta."
    two = LITART.replace("                 Entrance of the Theotokos\n",
                         "                 Sunday of the After-feast of the Ascension\n     Holy Fathers of the First Ecumenical Council\n")
    out, st = A.litart_blocks(two, lambda: {**F, "pascha_days": 42, "major_feast": ""})
    assert [h for h, *_ in out] == ["lit/vespers/theotoke_parthene", "lit/vespers/artoklasia_ps33"]  # whose doxastikon: unclear -> skipped
    assert any("owner unclear" in k for k in st)


def test_ingest_litart_saves_under_heading_ids(tmp_path):
    from yocal_service import texts
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "anca-2026-11-20-LITART.txt").write_text(LITART, encoding="utf-8")
    tx = texts.Texts(str(tmp_path / "sources"))
    st = A.ingest_litart(tx, texts.put, str(cache), lambda d: F if d.isoformat() == "2026-11-21" else None)  # the eve's file: next day
    assert st["litart stored"] == 4
    assert tx.rows["anca"]["men/11-21/doxastikonlity"]["origin"] == "ANCA Litia and Artoklasia 2026-11-20"


def test_dcs_media_meta():
    m = music.dcs_media_meta
    assert m("https://dcs.goarch.org/media/m/barrett/en/ho/ho10/b/litytheotokeparthene5.pdf") == \
        {"composer": "barrett", "lang": "en", "notation": "byzantine", "mode": 5}
    assert m("https://dcs.goarch.org/media/m/dedes/en/ho/ho10/w/litykyrieeleisonmode5.pdf")["mode"] == 5
    assert "mode" not in m("https://dcs.goarch.org/media/m/dedes/en/ho/ho10/w/lityartohymn.pdf")
    assert m("https://x/musiclibrary/a.pdf") == {}


class _Resp(io.BytesIO):
    headers = type("H", (), {"get_content_type": staticmethod(lambda: "application/pdf")})()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_scores_saved_once_and_linked_to_hymn_ids(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(music.urllib.request, "urlopen", lambda req, timeout=0: calls.append(req.full_url) or _Resp(b"%PDF-1 " + req.full_url.encode()))
    base = "https://dcs.goarch.org/media/m/{}/en/ho/ho10/{}/litytheotokeparthene{}.pdf"
    table = {"lit/vespers/theotoke_parthene": {"title": "T", "prefer": {"lang": "en", "mode": 5, "notation": "western"},
                                               "scores": [base.format("barrett", "b", 1), base.format("dedes", "w", 5), {"url": base.format("barrett", "b", 5)}]},
             "lit/vespers/artoklasia_ps33": {"scores": [{"url": "https://dcs.goarch.org/media/m/dedes/en/ho/ho10/w/lityartohymn.pdf", "mode": 7}]}}
    con = db.connect(str(tmp_path / "m.db"))
    assert music.fetch_hymn_music(con, table, delay=0) == {"saved": 4, "skipped": 0, "failed": 0}
    assert music.fetch_hymn_music(con, table, delay=0)["skipped"] == 4 and len(calls) == 4      # saved once
    rows = {r["url"]: r for r in store.read_jsonl(store.path("music", "index.jsonl"))}
    rich = rows["https://dcs.goarch.org/media/m/dedes/en/ho/ho10/w/lityartohymn.pdf"]
    assert rich["hymns"] == ["lit/vespers/artoklasia_ps33"] and rich["mode"] == 7 and rich["file"] == rich["sha256"] + ".pdf"
    best = music.hymn_assets(con, "lit/vespers/theotoke_parthene", table["lit/vespers/theotoke_parthene"]["prefer"])
    assert [a["url"] for a in best][0] == base.format("dedes", "w", 5) and len(best) == 3
    con2 = db.connect(str(tmp_path / "fresh.db"))                                                # a fresh machine: links rebuilt from the index
    assert len(music.hymn_assets(con2, "lit/vespers/artoklasia_ps33", {})) == 1
