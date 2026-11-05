#!/usr/bin/env python3
"""PROTOTYPE (throwaway, wipe me) -- wayfinder ticket #17.

Question: what should the review output look like? Rough service-assembly
listing for Sunday 2026-11-01 Divine Liturgy (Tone 5, Eothinon 11, Cosmas &
Damian on a Sunday, Luke 5) compared slot-by-slot with the ANCA key.

One structured data model (list of dicts), two renderers:
  python PROTOTYPE_review_output.py a   # slot table, one block per slot
  python PROTOTYPE_review_output.py b   # status-grouped, review-by-exception
All data hand-encoded from: Typikon Ch I s6 p.34-40, Ch V Nov 1 p.99-100,
yocal_main/yocal_lections, ANCA "Nov 01 2026 READ.pdf". No hymn text.
"""
import sys

# key_state: match | match_note | not_in_key | key_only | mismatch
# status:    explicit | inferred | missing   (per #14)
SLOTS = [
    dict(slot="liturgy.typika", label="Typika",
         ref="octoechos fixed (Ps 102 t8, Ps 145 t2)", rule="lit.typika.sunday",
         status="explicit", cite="Typikon Ch I s6 p.34",
         key_state="not_in_key", key="READ lists variables only"),
    dict(slot="liturgy.beatitudes.1-4", label="Beatitudes (1-4)",
         ref="(no hymns)", rule="lit.beatitudes.sunday", status="explicit",
         cite="Typikon Ch I s6 p.34", key_state="not_in_key", key=""),
    dict(slot="liturgy.beatitudes.5-8 [4 Res + 4 saint]", label="Beatitudes hymns",
         ref="octoechos t5 sun 'beatitude' x4 + menaion 1101 canon ode6 x4",
         rule="lit.beatitudes.nov01-sun", status="explicit",
         cite="Typikon Ch V Nov 1 p.100 (per-date order)",
         key_state="not_in_key", key="READ omits; DCS/Abbr only maybe"),
    dict(slot="liturgy.entrance_hymn", label="Entrance hymn",
         ref="fixed: Come let us worship ... risen from the dead",
         rule="lit.entrance.sunday", status="explicit",
         cite="Typikon Ch I s6 p.34-35", key_state="match",
         key="Come, let us worship... risen from the dead"),
    dict(slot="liturgy.troparia.1", label="Apolytikion, Resurrection",
         ref="octoechos t5 sun apolytikion", rule="lit.troparia.res-first",
         status="explicit", cite="Typikon Ch I s6 p.35",
         key_state="match", key="Res apolytikion tone 5"),
    dict(slot="liturgy.troparia.2", label="Apolytikion, saint",
         ref="menaion 1101 apolytikion (t8, Cosmas & Damian)",
         rule="lit.troparia.saint-if-doxastikon", status="explicit",
         cite="Typikon Ch I s3 p.16 + Ch V Nov 1 p.99 (saint has LIHC Glory)",
         key_state="match", key="Ss Cosmas & Damian tone 8"),
    dict(slot="liturgy.troparia.3", label="Apolytikion, temple patron",
         ref="$parish", rule="lit.troparia.patron", status="explicit",
         cite="Typikon Ch I s6 p.35", key_state="match",
         key="'sing the patron's apolytikion'"),
    dict(slot="liturgy.kontakion", label="Kontakion",
         ref="fixed: O undisputed Intercessor (Theotokos, t2)",
         rule="lit.kontakion.schedule", status="explicit",
         cite="Typikon Ch I s6 p.35-36 (Cross leavetaking -> Nov 8)",
         note="Res kontakion NOT used: Typikon silent (G); excluded by calendar schedule. Incipit differs from key (HTM: 'O protection of Christians').",
         key_state="match_note", key="Ordinary kontakion tone 2 (O protection of Christians)"),
    dict(slot="liturgy.prokeimenon", label="Prokeimenon",
         ref="??? (Res t5 and/or saint's?)", rule="lit.prokeimenon", status="missing",
         cite="Typikon silent (Ch I s6 p.37-38; gap #6.6)", ticket="(new ticket)",
         key_state="key_only", key="Saint's only: 'In the saints that are in His earth...'; Res prokeimenon absent"),
    dict(slot="liturgy.epistle", label="Epistle",
         ref="calendar 11-01: 1 Cor 12:27-13:8", rule="lit.epistle.saint-on-sunday",
         status="explicit", cite="Typikon Ch V Nov 1 p.100",
         key_state="match", key="1 Cor 12:27-13:8"),
    dict(slot="liturgy.alleluia", label="Alleluia",
         ref="fixed t2", rule="lit.alleluia", status="explicit",
         cite="Typikon Ch I s6 p.38", key_state="not_in_key", key=""),
    dict(slot="liturgy.gospel", label="Gospel",
         ref="calendar L5Sun: Luke 16:19-31", rule="lit.gospel.sunday",
         status="explicit", cite="Typikon Ch V Nov 1 p.100",
         key_state="match", key="Luke 16:19-31"),
    dict(slot="liturgy.liturgy_author", label="Chrysostom vs Basil",
         ref="Chrysostom", rule="lit.author.default", status="explicit",
         cite="rule: Basil 10x/yr (#19 research); Nov 1 not among them",
         key_state="match", key="'Liturgy of St John Chrysostom continues'"),
    dict(slot="liturgy.communion_hymn", label="Communion hymn",
         ref="fixed: Praise ye the Lord", rule="lit.communion.sunday",
         status="explicit", cite="Typikon Ch I s6 p.39-40",
         key_state="not_in_key", key=""),
    dict(slot="liturgy.dismissal.saints", label="Dismissal: saint named",
         ref="Cosmas & Damian (+Theodota)", rule="lit.dismissal.saint-if-doxastikon",
         status="explicit", cite="Typikon Ch I s4 p.17", key_state="match",
         key="names Cosmas, Damian, Theodota"),
]
# UK step: stripped run (no UK commemorations) compared; full run differs by construction.
UK_NOTE = "Full run adds UK saints to dismissal (St Pabiali ... ) -- stripped run compared, not logged."

SYM = dict(match="=", match_note="=*", not_in_key="?", key_only="!", mismatch="X")


def render_a():
    print("# Sun 2026-11-01  Divine Liturgy  [Tone 5, Eothinon 11; Cosmas & Damian on Sun; Luke 5]")
    print("# comparison: ANCA READ pdf  | stripped-UK run\n")
    for i, s in enumerate(SLOTS, 1):
        print(f"{i:>2}. {s['slot']}  -- {s['label']}")
        print(f"    fill   : {s['ref']}")
        print(f"    rule   : {s['rule']}  [{s['status']}]  {s['cite']}"
              + (f"  -> {s['ticket']}" if s.get('ticket') else ""))
        print(f"    ANCA   : {SYM[s['key_state']]} {s['key'] or '(nothing)'}")
        if s.get("note"):
            print(f"    note   : {s['note']}")
        print()
    print(UK_NOTE)


def render_b():
    print("# Sun 2026-11-01  Divine Liturgy -- review by exception\n")
    n = len(SLOTS)
    ok = [s for s in SLOTS if s["key_state"] in ("match", "match_note")]
    print(f"{n} slots | {len(ok)} match ANCA | "
          f"{sum(s['key_state']=='not_in_key' for s in SLOTS)} not in key | "
          f"{sum(s['key_state']=='key_only' for s in SLOTS)} key-only | "
          f"{sum(s['status']=='missing' for s in SLOTS)} missing rules | "
          f"{sum(s['status']=='inferred' for s in SLOTS)} inferred\n")
    print("== ATTENTION ==")
    for s in SLOTS:
        if s["status"] == "missing" or s["key_state"] in ("key_only", "mismatch") or s.get("note"):
            print(f"! {s['slot']}: rule {s['status']}; ANCA: {s['key'] or '-'}"
                  + (f"\n    {s['note']}" if s.get('note') else "")
                  + (f"\n    {s['ticket']}" if s.get('ticket') else ""))
    print("\n== NOT COVERED BY KEY (cannot verify) ==")
    for s in SLOTS:
        if s["key_state"] == "not_in_key":
            print(f"? {s['slot']}  <- {s['rule']} ({s['cite']})")
    print("\n== MATCHES ==")
    print(", ".join(s["slot"].split(".", 1)[1] for s in ok))
    print("\n" + UK_NOTE)


if __name__ == "__main__":
    {"a": render_a, "b": render_b}[sys.argv[1] if len(sys.argv) > 1 else "a"]()
