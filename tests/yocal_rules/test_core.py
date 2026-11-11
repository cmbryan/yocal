import datetime as dt
import os

import pytest

from yocal_rules import anca, assemble, calfacts, cli, compare, dcs
from yocal_rules.refs import norm_ref
from yocal_rules.rules import Resolution, RuleError, evaluate, load_catalogue

DB = calfacts.DEFAULT_DB
needs_db = pytest.mark.skipif(not os.path.exists(DB), reason="calendar DB not built")

F = dict(weekday="Sunday", mmdd="11-01", in_slice=True, saint_has_glory=True, saint_in_calendar=True, basil=False,
         tone=5, date="2026-11-01")


def rule(i, tier, slot="s", status="explicit", when=(), fill=None):
    r = dict(id=i, slot=slot, tier=tier, when=list(when), fill=fill or {}, source="typikon", locator="x", status=status)
    return r


# ---- refs
def test_ref_normaliser_equates_split_and_spanning_forms():
    assert norm_ref("12:27 – 31; 13:1 – 8") == norm_ref("1 Corinthians 12:27-13:8") == norm_ref("(12:27-13:8)")


def test_ref_normaliser_distinguishes_verse_ranges():
    assert norm_ref("Romans 5:1-10") != norm_ref("Romans 5:1-11")


# ---- rules
def test_lowest_tier_wins_and_shadowed_listed():
    out = evaluate([rule("a", 4), rule("b", 1)], F, ["s"])
    assert out["s"].rule_id == "b" and out["s"].shadowed == ["a"]


def test_tier_tie_is_a_build_error():
    with pytest.raises(RuleError):
        evaluate([rule("a", 2), rule("b", 2)], F, ["s"])


def test_slot_without_rule_is_missing_not_dropped():
    out = evaluate([], F, ["s"])
    assert out["s"].status == "missing" and out["s"].rule is None


def test_fact_substitution():
    out = evaluate([rule("a", 4, fill={"tone": "$tone"})], F, ["s"])
    assert out["s"].fill == {"tone": 5}


def test_shipped_catalogue_validates():
    rules, sources, slots = load_catalogue()
    assert rules and slots


# ---- compare
def res(fill, status="explicit", slot="liturgy.kontakion"):
    return Resolution(slot, status, rule("r", 4, slot=slot, status=status), fill)


def test_compare_states():
    f = dict(date="2026-11-01", mmdd="11-01")
    k = {"liturgy.kontakion": {"kind": "ordinary_theotokos", "tone": 2}}
    assert compare.compare(res({"kind": "ordinary_theotokos", "tone": 2}), k, "anca", f, "liturgy", []).state == "match"
    c = compare.compare(res({"kind": "ordinary_theotokos", "tone": 4}), k, "anca", f, "liturgy", [])
    assert c.state == "diff" and c.blocking
    assert compare.compare(res({"tone": 4}), k, "dcs", f, "liturgy", []).blocking is False
    assert compare.compare(res({"tone": 2}, slot="liturgy.gospel"), k, "anca", f, "liturgy", []).state == "not_in_key"
    assert compare.compare(res({"tone": 2}), {}, "anca", f, "liturgy", []).state == "no_key"
    miss = Resolution("liturgy.kontakion", "missing", None)
    assert compare.compare(miss, k, "anca", f, "liturgy", []).state == "key_only"


def test_divergence_log_entry_explains_a_diff():
    f = dict(date="2026-11-08", mmdd="11-08")
    log = [dict(slot="liturgy.kontakion", source="anca", scope={"mmdd": "11-08"}, **{"class": "anca_anomaly"})]
    k = {"liturgy.kontakion": {"tone": 4}}
    c = compare.compare(res({"tone": 2}), k, "anca", f, "liturgy", log)
    assert c.state == "diff" and not c.blocking and c.cls == "divergence:anca_anomaly"


# ---- ANCA / DCS parsers (synthetic text; no copyrighted content)
def test_anca_apolytikia_and_liturgy_parse():
    txt = """
 •   During the little entrance, chant the resurrectional apolytikion.
        RESURRECTIONAL APOLYTIKION IN TONE FIVE (KAZAN)
 words
       APOLYTIKION OF SS. FOO AND BAR IN TONE EIGHT
 words
 •   Now sing the apolytikion of the patron saint or feast of the temple.
       ORDINARY KONTAKION IN TONE TWO (CHANT)
                                              THE EPISTLE
                    (For Ss. Foo and Bar)
          The reading from the First Epistle of St. Paul to the Corinthians. (12:27-13:8)
          THE GOSPEL
   The Reading from the Holy Gospel according to St. Luke. (16:19-31)
"""
    k = anca.parse_liturgy(txt)
    assert k["liturgy.apolytikia"]["res_tone"] == 5 and k["liturgy.apolytikia"]["saint"]
    assert k["liturgy.kontakion"] == {"kind": "ordinary_theotokos", "tone": 2}
    assert k["liturgy.epistle"] == {"owner": "saint", "ref": "12:27-13:8"}
    assert k["liturgy.gospel"]["ref"] == "16:19-31"


def test_anca_ordinal_words():
    assert anca._word("ELEVENTH") == 11 and anca._word("FIFTH") == 5 and anca._word("six") == 6


def test_dcs_parse_liturgy_keys():
    def kv(k, t="x"):
        return f"<span class='kvp' data-key='{k}'>{t}</span>"
    html = "".join([
        kv("he.a.m5_en_US_goadedes|heAU.Foo.text"), kv("me.m11.d01_en_US_dedes|meVE.Apolytikion1.text"),
        kv("ho.ho07_en_US_dedes|hoTY.Key0408.text"),
        kv("le.ep.me.m11.d01_en_US_rsv|lemeLI.Epistle.chapverse", "12:27 – 31; 13:1 – 8"),
        kv("le.go.lu.d035_en_US_rsv|leluLI.Gospel.chapverse", "16:19 – 31"),
        kv("menaion.verses_en_US_saas|psLI.m11.d01.prokeimenon.v1.text"),
    ])
    k, _ = dcs.parse("liturgy", {"li": html, "h91": html})
    assert k["liturgy.apolytikia"] == {"res_tone": 5, "saint": True}
    assert k["liturgy.kontakion"] == {"kind": "ordinary_theotokos", "tone": 2}
    assert k["liturgy.epistle"]["owner"] == "saint" and k["liturgy.prokeimenon"]["owner"] == "saint"
    assert norm_ref(k["liturgy.gospel"]["ref"]) == norm_ref("Luke 16:19-31")


# ---- calendar / assembly (needs built DB)
@needs_db
def test_nov_1_2026_liturgy_resolves_without_missing():
    r = assemble.build("liturgy", dt.date(2026, 11, 1))
    got = {s: x for s, _, x in r.slots}
    assert not [s for s, x in got.items() if x.status == "missing"]
    assert got["liturgy.apolytikia"].fill == {"res_tone": 5, "saint": True}
    assert got["liturgy.epistle"].fill["owner"] == "saint"


@needs_db
def test_vespers_belongs_to_the_sunday():
    r = assemble.build("vespers", dt.date(2026, 10, 31))
    assert r.facts["date"] == "2026-11-01"
    assert dict((s, x) for s, _, x in r.slots)["vespers.lihc.stichera"].fill == {"res": 6, "other": [4]}


@needs_db
def test_weekday_is_out_of_scope():
    with pytest.raises(assemble.OutOfScope):
        assemble.build("liturgy", dt.date(2026, 11, 3))


@needs_db
def test_outside_slice_rules_are_withheld_not_misapplied():
    r = assemble.build("liturgy", dt.date(2024, 6, 30))  # Leavetaking of Peter and Paul (fore/after category not enabled; 2026-09-13 now is, H)
    assert not r.facts["in_slice"]
    assert {s: x for s, _, x in r.slots}["liturgy.apolytikia"].status == "missing"


@needs_db
def test_service_document_has_no_provenance(tmp_path):
    assert cli.main(["2026-11-01", "liturgy", "--no-compare", "--out", str(tmp_path)]) == 0
    doc = (tmp_path / "2026-11-01-liturgy.md").read_text()
    sup = (tmp_path / "2026-11-01-liturgy-supplement.md").read_text()
    assert "Typikon" not in doc and "explicit" not in doc and "lit.epistle.owner" not in doc
    assert "lit.epistle.owner" in sup and "Typikon" in sup.replace("typikon", "Typikon")


# ---- glory evidence (#28/#31) and inferred 4R+6 (#32)
def test_glory_is_alwb_or_bp_basil_never_a_veto():
    # 11-01: ALWB says no glory, Bp Basil '2 Glories' implies it
    g, src = calfacts.principal_glory("11-01", "Holy Wonderworkers and Unmercenaries Cosmas and Damian of Asia Minor")
    assert g is True and "Bp Basil" in src
    # 10-25 ALWB glory stays glory even if Bp Basil is Simple
    assert calfacts.principal_glory("10-25", "")[0] is True


def test_ref_union_of_verse_pieces():
    assert norm_ref("Luke 8:5-8a,9-15,8b") == norm_ref("8:5-15")


def test_divergence_entry_matches_on_context_fact_and_values():
    f = dict(date="2026-11-10", mmdd="11-10", two_sets_of_3=True)
    log = compare.load_divergence()
    r = res({"res": 4, "other": [6]}, slot="vespers.lihc.stichera")
    k = {"vespers.lihc.stichera": {"res": 6, "other": [4]}}
    c = compare.compare(r, k, "anca", f, "vespers", log)
    assert c.state == "diff" and not c.blocking and c.cls == "divergence:anca_year_variant"
    k = {"vespers.lihc.stichera": {"res": 7, "other": [3]}}
    assert not compare.compare(r, k, "anca", f, "vespers", log).blocking
    # an unflagged date is not covered
    assert compare.compare(r, k, "anca", dict(f, two_sets_of_3=False), "vespers", log).blocking


@needs_db
def test_two_sets_flag_drives_inferred_four_six():
    r = assemble.build("vespers", dt.date(2024, 11, 9))  # Nov 10 Sunday eve: Olympas, flagged, no Ch V entry
    x = {s: v for s, _, v in r.slots}["vespers.lihc.stichera"]
    assert (x.fill, x.status) == ({"res": 4, "other": [6]}, "inferred")


def test_anca_adds_glory_entry_covers_listed_dates_only():
    log = compare.load_divergence()
    r = res({"res": 7, "other": [3]}, slot="vespers.lihc.stichera")
    k = {"vespers.lihc.stichera": {"res": 6, "other": [4]}}
    f = dict(date="2025-12-07", mmdd="12-07", two_sets_of_3=False)
    c = compare.compare(r, k, "anca", f, "vespers", log)
    assert c.cls == "divergence:anca_adds_glory" and not c.blocking
    assert compare.compare(r, k, "anca", dict(f, mmdd="06-14"), "vespers", log).blocking  # other dates are not covered
    ap = res({"res_tone": 5, "saint": False}, slot="liturgy.apolytikia")
    assert not compare.compare(ap, {"liturgy.apolytikia": {"res_tone": 5, "saint": True}}, "anca", f, "liturgy", log).blocking


def test_dismissal_parse_variants():
    base = "Priest: May he who rose... Joachim and Anna{x} whose memory we celebrate today, and of all the saints: have mercy THE DISMISSAL"
    assert anca._dismissal_names_saint(base.format(x="; of the holy martyr Foo,"))
    assert anca._dismissal_names_saint(base.format(x="; and of all the saints of all ages, especially of Antioch,"))
    assert not anca._dismissal_names_saint(base.format(x="; and of all the saints of all ages who are well-pleasing to God,"))
    assert not anca._dismissal_names_saint("Joachim and Anna; and of all the saints: have mercy")
    assert anca._dismissal_names_saint(base.format(x="; and Venerable martyrs Foo and Bar,"))


@needs_db
def test_sunday_named_and_archangel_dismissals():
    got = lambda d: {s: x for s, _, x in assemble.build("liturgy", d).slots}["liturgy.dismissal"]
    x = got(dt.date(2025, 12, 14))  # Sunday of the Holy Forefathers
    assert x.rule_id == "lit.dismissal.sunday_named" and x.fill["saint_named"] is True and x.status == "inferred"
    y = got(dt.date(2026, 11, 8))  # Synaxis of the Archangels
    assert y.rule_id == "lit.dismissal.archangel" and y.fill["saint_named"] is False
    z = got(dt.date(2026, 11, 1))  # follows ANCA by default; the Typikon reading is shadowed, conflict recorded
    assert z.rule_id == "lit.dismissal.anca_default" and z.fill["saint_named"] is True
    assert "lit.dismissal.glory" in z.shadowed and z.rule["conflict"]["status"] == "open"
    assert got(dt.date(2025, 6, 29)).fill["saint_named"] is False  # Peter and Paul


def test_epistle_owner_and_acts_parsing():
    base = """THE EPISTLE (For St. Foo)
 The reading from the Acts of the Apostles. (12:1-11)
"""
    k = anca.parse_liturgy(base)
    assert k["liturgy.epistle"] == {"owner": "saint", "ref": "12:1-11"}
    assert anca.parse_liturgy("THE EPISTLE\n (For the Holy Forefathers)\n")["liturgy.epistle"]["owner"] == "sunday"
    assert anca.parse_liturgy("THE EPISTLE\n (For the Holy Fathers)\n")["liturgy.epistle"]["owner"] == "sunday"


def test_luke_8_8_acclamation_is_optional():
    assert norm_ref("12:16-21,8:8") == norm_ref("12:16-21")
    assert norm_ref("Luke 8:8") != ""  # a lone reference is kept


@needs_db
def test_anca_sunday_epistle_overrides_flag_with_open_conflict():
    got = lambda d: {s: x for s, _, x in assemble.build("liturgy", d).slots}
    g = got(dt.date(2026, 6, 14))  # All Saints of Antioch: flag says saint, ANCA reads the Sunday's
    assert g["liturgy.epistle"].rule_id == "lit.epistle.anca_sunday" and g["liturgy.epistle"].fill["owner"] == "sunday"
    assert g["liturgy.prokeimenon"].fill["owner"] == "sunday"
    assert g["liturgy.epistle"].rule["conflict"]["status"] == "open" and "lit.epistle.owner" in g["liturgy.epistle"].shadowed
    n = got(dt.date(2026, 11, 1))  # ordinary saint's Epistle on a Sunday stays the saint's
    assert n["liturgy.epistle"].fill["owner"] == "saint"


def test_date_scoped_divergence_entries():
    f = dict(date="2022-07-03", mmdd="07-03")
    c = compare.compare(res({"ref": "Romans 5:1-10"}, slot="liturgy.epistle"), {"liturgy.epistle": {"ref": "5:1-11"}}, "anca", f, "liturgy", compare.load_divergence())
    assert c.state == "diff" and c.cls == "divergence:verse_split_difference"
