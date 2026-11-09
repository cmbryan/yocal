# Lenten Triodion rubrics for Typikon-deferred days (issue #41)

Throwaway research branch, not for merge. Paraphrase only; page/section cites; no texts copied.

## Answer

Yes, mostly. Free Triodion texts give explicit slot orders for 3 of the 4 gap areas. Cheesefare Sunday is absent from Fordham but present in st-sergius.org. Upgrade targets below. Liturgy-side Rules (Basil vs Chrysostom, prokeimenon) remain inferred/ANCA-led.

## Sources checked

| ID | Source | Notes |
|---|---|---|
| F | Fordham Internet Medieval Sourcebook, Lenten Triodion ASCII (Community of the Holy Myrrhbearers, OCA; `sourcebooks.fordham.edu/basis/triodion.asp`, files `triodion/*.txt`; readme.txt) | Index lists Last Judgment (`lstjudg.txt`), Prodigal, Lent 1-6 Sat/Sun, Holy Week. NO Cheesefare Sunday file. Publican link (`pubnphar.txt`) returns 404. Sparse rubrics: headings like "6 stikhera of the Resurrection" mislead (text printed is the Triodion part). Liturgy parts partial. Not for commercial use (readme). |
| S | st-sergius.org (All-Saints GOC) English Lenten Triodion PDFs (`services/triod/0-37.pdf` Meatfare Sun, `0-47` Cheesefare Sun, `57` Lent 5 Sun, `56` Lent 5 Sat, `66` Lazarus Sat, `67` Palm Sun) | Best: explicit counts per slot, Vespers/Matins/Liturgy. Based on Ware-like English; copyright unknown, cite only. |
| O | orthlib.info Triodion-Fasting (Russian/Slavonic PDFs, `04_Triod-Fast-Meatfare_ned_myas.pdf`, `07_..Cheesefare_ned_syrn.pdf`) | Index confirmed; Slavonic text not read (language). Cross-check only. |
| T | Antiochian Typikon (local) pp.473-475 (Meatfare, Cheesefare), p.502, 504-506 (see #8 findings) | Defers to "the Triodion". |
| A | ANCA 2026 Liturgy Variables + Orthros PDFs (`prototypes/anca-compare/pdfs_sun`, `sun_keys.csv` 2018-2026) | Answer key. No Saturday Vespers PDFs held locally for these dates. |

Ware 1978 (Faber) not obtainable; per Fordham readme it covers Sundays and major items. Not consulted. Gap noted, since the issue flagged it.

## Findings by day

### 1. Meatfare Sunday (Sat Vespers, Matins, Liturgy)
- **Sat Vespers** (T p.473: 10 = 6 Res + 4 Triodion). F lstjudg: Triodion stichera in tone 6 x4, Glory tone 8, Now tone-of-week dogmatikon. Aposticha: Res; Glory Triodion tone 8 (Now Theotokion). Troparia: Res + Triodion kontakion tone 1 (F). S 0-37: great prokeimenon "The Lord is king".
  - Upgrade: **inferred -> explicit** (Triodion, 6+4 count agrees with Typikon).
- **Matins** (S 0-37, F): Polyeleos Ps 136/137 w/ Alleluia; Res Gospel then repentance Ps 50 verses; Triodion canon (Theodore the Studite, tone 6) after Res canon; Triodion sessional after ode 3; Triodion kontakion + oikos after ode 6 (Res kontakion not sung); Triodion katavasia; exapostilaria: eothinon + Triodion; **Praises 5 Res + Triodion** (S: "5 Resurrection stichera" then Triodion; F idem, 3 Triodion tone 6/8/1; Glory repeat; Now Theotokion); Great Doxology.
  - ANCA 2026-02-15: praises verses 1-5 Res, verse 6-8 Triodion (tone 6) -> **matches 5+Triodion**. Orthros kontakion tone 1 text = Triodion. ANCA prints Triodion canon only as katavasia; one exaposteilarion (eothinon), no separate Triodion exaposteilarion shown. **Typikon Matins slots remain unstated; Triodion explicit.** Note: ANCA exaposteilarion differs from S (S lists 2).
- **Liturgy**: S: Typika/Beatitudes 6 + 4 from ode 6 of canon; kontakion Triodion tone 1; Epistle 1 Cor 8:8-9:2, Gospel Mt 25:31-46; **prokeimenon Triodion tone 3 "Great is our Lord"** and Alleluia Triodion tone 8 (F agrees). Chrysostom.
  - **Divergence**: ANCA uses a tone-of-week Sunday prokeimenon (text varies by year: tone-7 2019 "The Lord is my strength...", tone-3 2026 "Sing praises...") and no fixed Triodion prokeimenon. Treat ANCA as key; log Triodion prokeimenon as divergence (acceptable?). Reading refs match ANCA (1 Cor 8:8-9:2; Mt 25:31-46).
- Sunday-evening Vespers: aposticha Triodion tone 8 (F, T p.473).

### 2. Cheesefare (Forgiveness) Sunday
- Not in F. S 0-47:
  - **Sat Vespers**: 10 = 6 Res + 4 Triodion tone 6 (Adam theme); Glory Triodion tone 6; Now tone-of-week dogmatikon; "The Lord is king" prokeimenon; aposticha Res + Glory Triodion. Agrees with T p.475 (6+4). **Explicit.**
  - **Matins**: Triodion canon; kontakion Triodion tone 6; exapostilaria: eothinon + Triodion ("Glory", tone 3); **Praises 5 Res + 4 Triodion stichera, Glory, Now** (S); Great Doxology.
    - ANCA 2026-02-22: praises 5 Res (verses 1-5) + Triodion verses 6-8 + Glory + Now: **count differs** (3 vs 4 Triodion stichera). Unresolved: S has "4 stichera tone 5" while ANCA prints 3 + Glory. Mark **ANCA anomaly or abridgement, check Slavonic (O)**.
  - **Liturgy**: Typika/Beatitudes 6 + 4 from ode 6; kontakion Triodion tone 6; prokeimenon **tone 8 "Make your vows"** (Triodion); Alleluia Triodion tone 6; Rom 13:11-14:4; Mt 6:14-21; Chrysostom. ANCA readings match; ANCA prokeimenon varies by year ("Sing praises" 2018/20/25, "O chant unto our God" 2021-23, "Make your vows" only 2024 (tone 8), "How magnified are Thy works" 2026) -> ANCA follows tone-of-week, not Triodion.
- Forgiveness evening Vespers (T p.475): already explicit in Typikon.

### 3. Lent 5 Sunday (Mary of Egypt) Vespers
- **Sat Vespers** (T p.502 only "order from the Triodion"): F lent5sat and S 57 agree: **10 = 6 Res + 4 Mary of Egypt (3 stichera, first sung twice)**; Glory Mary tone 4; Now tone-of-week dogmatikon; entrance, "The Lord is king"; aposticha Res + Glory Mary tone 2 + Now Theotokion (F). Troparia: Res + Mary (tone 8) + kontakion tone 3 (F).
  - **Upgrade: Typikon gap -> explicit (6+4)**. Pattern same as Lent 1-4.
- Matins (T p.502 explicit): S 57 adds 2 Triodion canons, kontakion Mary tone 3 after ode 3 (S shows Res kontakion after ode 6), exapost: eothinon + Mary + Theotokion, praises 8 = **4 Res + 4 Mary (verses)** with Glory Triodion tone 2. ANCA 2026-03-29 praises: 4 Res + Mary stichera + Glory (doxasticon) -> agrees.
- **Liturgy**: S 57: Typika 8 from Octoechos; Mary troparion/kontakion; prokeimenon Res + Mary prokeimenon tone 4; Heb 9:11-14; Mk 10:32-45. **No Basil/Chrysostom rubric in S or F.** ANCA 2026-03-29: **Liturgy of St Basil**, Heb 9:11-14, Mk 10:32-45, Res apolytikion + Mary apolytikion, ordinary kontakion tone 2 (Theotokos). So **Basil on Lent 5 stays inferred from ANCA** (Typikon explicit only Lent 1, 3, 4; #8). Kontakion: ANCA prints the ordinary Theotokos kontakion tone 2; Typikon general rule is "Champion Leader" Lent 1-5 (except Lent 5 after Annunciation, see #8): flag as ANCA divergence to check.

### 4. Palm Sunday Vespers (day/order)
- **Day = Saturday evening.** F lent6sat "Saturday Vespers" for Palm week and S 67 explicit "Saturday Vespers prokeimenon" for Palm Sunday Vespers; separate Sunday-evening Vespers (6 stichera) belongs to Holy Week. **Resolves Typikon p.504 day gap** (Typikon heading "Great Vespers" unplaced).
- Order (S 67, F): 10 stichera tone 6 = 5, each twice ("Today the grace of the Holy Spirit..."); Glory/Now repeat first; litya (F: tone 1 + Glory tone 3 Lazarus); aposticha 3 stichera tone 8 + Glory tone 6 + Now repeat; "Saturday" prokeimenon tone 6. **Agrees with Typikon counts** (10 = 5x2); adds litya (Typikon silent).
- Matins/Liturgy already explicit (T pp.504-506; ANCA 2026-04-05: Chrysostom, 3 antiphons, Phil 4:4-9, Jn 12:1-18, proper eisodikon, no exaposteilarion, Prayer of the Palms). F/S agree: no Res stichera, Triodion canon only.
- ANCA Vespers for Sat before Palm: not held locally (anca-compare has only Sunday ORTHROS/READ). Not compared.

## Summary table: upgrade of ANCA-inferred / gap items

| Day / slot | Typikon | Triodion (S/F) | ANCA | New status |
|---|---|---|---|---|
| Meatfare Sat Vespers | 6+4, rest deferred | 4 Triodion stichera, Glory, aposticha | n/a | explicit (S) |
| Meatfare Matins praises | deferred | 5 Res + Triodion | 5 Res + 3 Triodion | explicit, consistent |
| Meatfare Liturgy prokeimenon | silent | Triodion tone 3 | tone-of-week | **divergence** |
| Cheesefare Sat Vespers | 6+4 | 6+4, Glory Triodion | n/a | explicit |
| Cheesefare Matins praises | deferred | 5 Res + 4 Triodion + Glory + Now | 5 + 3 + Glory + Now | **count mismatch (open)** |
| Cheesefare Liturgy prokeimenon | silent | tone 8 fixed | tone-of-week | divergence |
| Lent 5 Sat Vespers | "from Triodion" | 6 Res + 4 Mary, Glory Mary | n/a | explicit |
| Lent 5 Liturgy Basil | not stated | not stated | Basil | stays inferred (ANCA) |
| Palm Sat Vespers day | unstated | Saturday evening | n/a | explicit |

## Coverage gaps

- Fordham: no Cheesefare Sunday, Publican file dead. Rubrics terse, some "6 stikhera of the Resurrection" labels cover the Octoechos part only. Not authoritative on Liturgy/Basil.
- st-sergius: GOC (Old Calendar, Greek-style) Triodion, not Antiochian; sources/translations unstated. Tone placement could differ from Antiochian use. Not a Typikon.
- orthlib.info Slavonic/Russian PDFs not read; cross-check pending (Russian practice, not Antiochian).
- Ware 1978 not accessed. Coverage claimed incomplete for some offices (issue note).
- No ANCA Sat Vespers PDFs for Triodion dates; download needed to test Vespers counts against key.
- Prokeimenon/Basil/praises-count mismatches go to divergence log candidates; Typikon itself silent.

## Recommended Rule treatment

1. Adopt S (with F corroboration) as supplementary source for Meatfare/Cheesefare/Lent 5 Vespers counts: explicit, authority rank 4 ("other typika"; Typikon defers to "the Triodion").
2. Keep Basil on Lent 5 as inferred (sun_keys.csv: Basil every Lent 5 row 2019-2026).
3. Palm Sunday Great Vespers: Saturday evening, 5x2 + 3 aposticha. Closes #8 gap.
4. Log prokeimenon divergence for Meatfare and Cheesefare as ANCA-follows-tone, not an ANCA error.
5. Open: resolve Cheesefare praises 3 vs 4 Triodion stichera via Slavonic/ANCA Vespers.
