# Prokeimenon and alleluia-verse rules (Sat Vespers, Sun Matins, Liturgy)

Issue: cmbryan/yocal#21 (map #5). Researched 2026-11-05. Research branch, throwaway, never merged.
Public repo: nothing copied. Paraphrase + short hymn incipits only. No PDFs committed.

Status tags: **E** explicit (source + cite), **I** inferred (evidence listed), **M** missing (no source found).
Cites: `Typ Ch I §3 p.13` = Antiochian Typikon (Khoury/Morris 2011), printed page. `Wichita Chart II p.30` = Bp Basil Parish Typikon Charts (dowama.org `Chart1/2/3.pdf`, `Descriptions of Ranks.pdf`), printed page. ANCA = antiochian.org `servicetexts/<Mon DD YYYY> {VESP,ORTHROS,READ,Abbr}.pdf`. DCS = Digital Chant Stand `h/s/YYYY/MM/DD/{ve,ma,li,li2,li3}`, data-keys.

## TL;DR

- **Sat Vespers**: E. "The Lord is King" (tone 6) for plain/saint/Theotokos-feast Sundays. Master-feast and Triodion/Pascha exceptions E but internally contradictory in Typikon; Wichita resolves.
- **Sun Matins**: E. Prokeimenon = Octoechos, tone of week, *including* when a saint is celebrated (Typikon + Wichita; 15 ANCA + 4 DCS dates agree). Feast prokeimenon only for Theotokos/Master feast on Sunday.
- **Sun Liturgy prokeimenon**: **M in all Antiochian sources read** (Typikon, Wichita charts have no Liturgy prokeimenon row). **I**: prokeimenon follows the owner of the Epistle. Saint's Epistle read => saint's prokeimenon only, no Resurrection/Sunday one. Matches the Nov 1 2026 ANCA observation. Not a gap in ANCA: it is the rule.
- **Alleluia verse**: Typikon says only "Alleluia 3x tone 2 after every Epistle" (E, no verses, no verse rule => M for verses). ANCA key has no alleluia verses at all. DCS has Sunday-mode verses (`psLI.sunday.mN.alleluia`) and keeps them even when the saint's prokeimenon/Epistle is used (I, GOA only, non-blocking).
- Russian/Ruthenian usage differs (combine two prokeimena and two alleluias on Sunday+saint). Antiochian answer keys do not.

## 1. Source search result (where do the rules live?)

| Source | Sat Vespers | Sun Matins | Liturgy prokeimenon | Alleluia |
|---|---|---|---|---|
| Antiochian Typikon | E (Ch I §3 p.13; contradictory on Lord feast) | E (Ch I §5 p.25) | **silent** (Ch I §6 p.34-41; Ch III Sunday Liturgy; Menaion Liturgy entries list "Epistle and Alleluia", never a prokeimenon) | E 3x tone 2 only (Ch I §6 p.38) |
| Wichita Charts I-III | E (Chart II p.30, Chart III p.37, Descriptions fn 5) | E (Chart I p.24, II p.32, III p.38) | **silent** (Liturgy block lists antiphon refrains, apolytikia, Epistle/Gospel owner, koinonikon; no prokeimenon row) | silent |
| ANCA Liturgy Variables (READ) | n/a | n/a | one prokeimenon + verse, printed under heading "The Epistle (For <owner>)" | not printed |
| ANCA Abbr rubrics | "Lord is King" tone 6 | "Hypakoe, Anabathmoi, Prokeimenon ... " (Resurrectional) | "see Variables" | silent |
| DCS | `psVE.prokeimenon.saturday` | `psMA.sunday.mN.prokeimenon` (Menaion key only on non-Sunday feasts) | `psLI.sunday.mN.prokeimenon` or `psLI.mMM.dDD.prokeimenon` | `psLI.sunday.mN.alleluia` / `psLI.mMM.dDD.alleluia` |
| MCI (Ruthenian) Divine Liturgy for Sundays; UOC-USA Ustav | n/a | n/a | combine two (Sunday + saint) | combine two |

Not read (paywalled / Greek scan): Violakis Greek 1888, Denver bilingual, Bogdanos, Getcha, Andreev selected chapters (not searched for Liturgy prokeimenon). Violakis is the likely origin of the Liturgy rule; see questions.

## 2. Per-case findings

### 2.1 Saturday Great Vespers (prokeimenon)

| Case | Rule | Status | Evidence |
|---|---|---|---|
| Plain Sunday eve | "The Lord is King" (tone 6, with its verses) | **E** | Typ Ch I §3 p.13; Wichita Chart II p.30 (all ranks 5th-2nd). ANCA VESP 15/15 sampled eves: heading "Saturday Prokeimenon in Tone Six". DCS `psVE.prokeimenon.saturday` Nov 7/14/21. |
| Saint (any rank) on Sunday | Same: "Lord is King" | **E** | Wichita Chart II p.30; ANCA Oct 31 (Cosmas/Damian), Nov 7 (Archangels), Oct 17 (Luke), Jan 24 (Gregory). |
| Theotokos feast / afterfeast on Sunday | Same | **E** | Wichita Chart II p.30 (2nd class column); Chart III p.37 festal-season Sunday column says "of the day" (see next). ANCA Nov 21 2026 (afterfeast Entrance, Sunday Nov 22): Lord is King. |
| Festal season / leavetaking coinciding with Sunday | Wichita Chart III p.37 prints "of the day" (ambiguous, does not say Lord is King) | **E but ambiguous** | ANCA Sep 19 2026 (afterfeast Cross), Nov 21: Lord is King. Treat as I: Lord is King. |
| Eve of a Master (Lord) feast, any weekday | Feast's own Great Prokeimenon ("Who is so great a God" / "Our God in heaven") | **E** | Typ Ch I §3 p.13; Wichita Chart II p.30 (1st class "of the day"); Typ Menaion Nativity eve says "prokeimenon of the day". |
| Master feast falling on Saturday (Sep 14, Dec 25, Jan 6, Aug 6) | Typikon Ch I §3 p.13 contradicts itself: bullet 1 "always Lord is King, exceptions Nativity and Epiphany"; bullet 3 "Lord feast on Saturday: feast prokeimenon". Wichita (Descriptions of Ranks fn 5): the great prokeimenon goes to Friday evening; Saturday evening is "Lord is King" | **E, conflicting; resolution I (Wichita)** | No 2026 sample. Check with ANCA when a Saturday Master feast occurs (2027: Aug 6 is Friday; Sep 14 2030 is Saturday). |
| Sunday that is itself a Master feast (e.g. Sep 14 2025) | Sat evening = feast eve => Great Prokeimenon of feast | **I** | Follows from rows above; ANCA 2025-09-14 liturgicday page rendered with no service-text links, filenames not located. No key sample. |
| Triodion: eves of Cheesefare Sunday and Lent Sundays | Great Prokeimenon from Triodion | **E (Typikon) but ANCA disagrees** | Typ Ch I §3 p.13. ANCA Feb 28 2026 VESP (eve of Lent 1) and Abbr use "Lord is King". Publican eve (Jan 31) Lord is King, consistent. Text of Great Prokeimenon: M (in Triodion book). |
| Palm Sunday eve; Thomas Sunday eve; Holy Saturday; Bright Week | Palm Sun eve: Daily Vespers, Sunday-evening prokeimenon "Behold now bless ye"; Thomas Sun eve: Great Vespers with great prokeimenon; Holy Sat: "Arise O God" after Epistle; Bright Week: from Pentecostarion | **E** | Wichita Descriptions fn 5; Typ Ch I §3 p.13. Text sets for Bright Week: M (Pentecostarion). |

### 2.2 Sunday Matins (prokeimenon, between anabathmoi and Gospel)

| Case | Rule | Status | Evidence |
|---|---|---|---|
| Plain Sunday | Prokeimenon of tone of week (Resurrectional, Octoechos, "Arise O Lord" family, twice + stichos) | **E** | Typ Ch I §5 p.25; Wichita Chart II p.32 ("Octoechos"). ANCA ORTHROS "Resurrectional Prokeimenon in Tone N": all 15 sampled Sundays. |
| Saint of any sampled rank on Sunday (3rd class "Vigil/Polyeleos" or lower) | Still Resurrection/tone of week. Saint gets only the Matins Gospel replaced? No: eothinon stays | **E** | Wichita Chart II p.32 (Octoechos for classes 5-3). ANCA Nov 1 (Cosmas/Damian), Nov 8 (Archangels), Oct 18 (Luke), Jan 25 (Gregory): resurrectional. DCS `psMA.sunday.m5` (Nov 1), `m6` (Nov 8). |
| Festal season / afterfeast / leavetaking on Sunday | Prokeimenon "of the tone" | **E** | Wichita Chart III p.38. ANCA Nov 22 (Entrance afterfeast), Sep 20 (Cross afterfeast), Sep 13 forefeast: resurrectional. |
| Theotokos feast on Sunday (2nd class) | Prokeimenon of the feast (+ feast Matins Gospel) | **E**, no sample | Typ Ch I §5 p.25; Wichita Chart II p.32. Feast text for the prokeimenon: Menaion (e.g. Nativity of Theotokos "I shall call on thy name" cited in Typ Menaion Sep 8, p.65). |
| Master feast on Sunday (1st class) | Prokeimenon of the feast | **E**, no sample | Wichita Chart II p.32. |
| Triodion Sundays | Resurrectional of tone (Gospel hymns changed per Typ Ch III) | **I** | ANCA Feb 1 (Publican), Mar 1 (Lent 1): resurrectional. |
| Pentecostarion Sundays | Not checked | **M** | Out of this ticket's evidence. |
| Text of the Sunday Matins prokeimenon | 8 fixed Octoechos items by tone; deferred to Octoechos | **D** | ANCA/DCS carry text. DCS key `psMA.sunday.m<N>.prokeimenon`. |

### 2.3 Sunday Divine Liturgy (prokeimenon)

**Explicit rule: none found (M).** Typ Ch I §6 (p.34-41) lists Trisagion, Epistle/Gospel owner (p.37-38) and Alleluia (p.38) but no prokeimenon slot. The Typikon's own Menaion entries for Liturgies list "The Epistle and Alleluia" (e.g. Nativity Basil Liturgy, p.~140) with no prokeimenon either. Wichita Chart II p.34 Liturgy block likewise has no prokeimenon row. (The Typikon does mention a Liturgy prokeimenon only for Holy Saturday, Ch I §6 p.38.)

**Inferred rule (I): the prokeimenon (and its verse) is the one belonging to the Epistle that is read; prokeimenon owner = Epistle owner.** Epistle owner per Typ Ch I §6 p.37-38 and Wichita Chart II p.34 + fn 4. Evidence: 16 ANCA READ files (Epistle block prints the prokeimenon under heading "(For <owner>)") and 5 DCS Liturgies (key owner matches `le.ep.*` owner).

| Date (2026 unless noted) | Day | Epistle owner (ANCA heading) | Prokeimenon shown | DCS |
|---|---|---|---|---|
| Nov 1 | Cosmas/Damian on Sun (T5) | Ss. Cosmas and Damian | saint's (Ps 15, "saints on his earth") only; no Resurrection one | `psLI.m11.d01.prokeimenon`, Epistle `le.ep.me.m11.d01` |
| Nov 8 | Archangels on Sun (T6) | Archangels | saint's (Ps 103 "He makes his angels spirits") | `psLI.m11.d08.prokeimenon`, `le.ep.me.m11.d08` |
| Oct 18 | Luke on Sun (T3) | St Luke | saint's | n/a (page gone) |
| Jan 25 | Gregory Theologian on Sun (T8) | Gregory | saint's | n/a |
| Nov 15 | plain Sun (T7) | Sunday | tone-7 Sunday prokeimenon | `psLI.sunday.m7.prokeimenon` |
| Nov 22 | afterfeast Entrance on Sun (T8) | Sunday | tone-8 Sunday prokeimenon | `psLI.sunday.m8.prokeimenon` |
| Oct 4, Oct 25, Sep 6, Sep 27, Aug 30 | plain Suns T1,T4,T5,T8,T4 | Sunday | Sunday prokeimenon of tone | n/a |
| Sep 20 | Sun after Cross (T7) | Sunday after Cross | tone-7 Sunday prokeimenon | n/a |
| Sep 13 | Sun before Cross (T6) | Sunday before Cross | tone-6 Sunday prokeimenon | n/a |
| Oct 11 | Fathers of 7th Council (T2) | Holy Fathers | tone-2 Sunday prokeimenon | n/a |
| Feb 1 | Publican (T1) | Sunday of Publican | tone-1 Sunday prokeimenon | page empty shell |
| Mar 1 | Lent 1 (T5) | First Sunday of Lent | tone-**2** text (differs from T5 set): Triodion-proper | n/a |

Sunday prokeimenon-by-tone set (Liturgy; different from the Matins "Resurrectional" set): observed T1 "Let thy mercy", T2 "Blessed art thou ... fathers", T4 "O Lord how magnified", T5 "Thou O Lord wilt keep", T6 "O Lord save thy people", T7 "The Lord will give strength", T8 "Make your vows". T3 not observed on a plain Sunday. Text-level data lives in ANCA/DCS keys (`psLI.sunday.m1..8.prokeimenon`).

Per-case summary:

| Case | Prokeimenon | Status |
|---|---|---|
| Plain Sunday | Sunday prokeimenon of tone | **I** (ANCA 8 dates, DCS 2) |
| Saint on Sunday whose Epistle is read (Typ Ch I §6 p.37-38 list; Chart II p.34 3rd class; includes Cosmas/Damian, Archangels, Luke, Gregory) | Saint's prokeimenon **only**; no Sunday/Resurrection prokeimenon | **I** (ANCA 4 + DCS 2); owner-of-Epistle part is **E** |
| Saint on Sunday whose Epistle is *not* read (lesser, Oct 4 Hierotheos) | Sunday's | **I** (ANCA Oct 4, Oct 25) |
| Saint whose Epistle *and* Gospel replace Sunday's (Chart II fn 4 list: Forerunner, Peter and Paul, Evangelists, Councils, Three Hierarchs) | Saint's | **I** (Epistle-owner rule), no sample |
| Theotokos/Master feast on Sunday (Epistle of the feast, Typ Ch I §6 p.37-38; Chart II p.34) | Feast's prokeimenon | **I**, no sample |
| Theotokos feast on a weekday/Saturday (Sep 8; Nov 21 Sat) | Feast prokeimenon | **I** (ANCA Sep 8 READ "(Epistle) Magnificat" verses; DCS `psLI.m11.d21.prokeimenon`) |
| Festal season/afterfeast/leavetaking on Sunday (Chart III) | Sunday's (Epistle of day) | **I** (ANCA Nov 22, Sep 20; Chart III footnote 3 p.36 for leavetaking weekday only) |
| Lent/Triodion Sundays | Triodion/Sunday-proper; Mar 1 not the tone-5 text | **I**, thin; text source M |
| Two prokeimena (Sunday + saint) | Not observed in ANCA/DCS. Ruthenian (MCI) and Russian practice combine both | Divergence note only |

### 2.4 Alleluia (after Epistle)

| Case | Rule | Status |
|---|---|---|
| Every Liturgy: Alleluia 3x, tone 2, after the Epistle | **E** Typ Ch I §6 p.38 (including Bright Week; Holy Saturday: Great Prokeimenon "Arise O God" replaces it, Ps 81 verses) | **E** |
| Alleluia **verse** (the 2 verses, which set) | Typikon gives none; Wichita none | **M** |
| ANCA | Liturgy Variables print no alleluia verse at all; Abbr silent. Cannot be an answer key | **M** (key gap) |
| DCS plain Sunday | Verse set keyed to Sunday's mode: `psLI.sunday.m<N>.alleluia` (li2/li3). Nov 15 m7, Nov 22 m8 | **I** (GOA) |
| DCS saint on Sunday (Nov 1, Nov 8) | **Sunday's** mode alleluia kept (`psLI.sunday.m5`, `m6`), though Epistle + prokeimenon are the saint's. Not "alleluia follows Epistle" | **I** (GOA only; Antiochian practice unknown) |
| DCS Saturday Theotokos feast (Nov 21) | Feast alleluia `psLI.m11.d21.alleluia` | **I** |
| Triodion/Pentecostarion | Not checked | **M** |
| Ruthenian/Russian | Two alleluias combined for Sunday+saint (MCI Divine Liturgy for Sundays) | divergence note |

Note: Typ Ch I §5 p.21 Lenten "Alleluia" with verses is a Matins slot ("God is the Lord" replacement), not the Liturgy alleluia.

## 3. ANCA / DCS agreement

- ANCA vs DCS agree on all 4 overlapping dates (Nov 1, 8, 15, 22) for Vespers, Matins and Liturgy prokeimenon owner.
- DCS pages for dates before 2026-11-01 now return 404 (earlier note #10 saw them). Only a rolling window is online, so DCS cannot serve as key for earlier samples (e.g. Oct 18, Sep 13). ANCA files persisted for the whole year.
- ANCA typo variant: "Resurrectional Prokemenon" in Aug 30 and Oct 25 ORTHROS headings; a slot parser must accept both spellings.
- ANCA Sep 8 VESP file says "If this commemoration falls on a Sunday, visit the Online Liturgical Guide" (their weekday files defer Sunday-coincidence).

## 4. Implications for the Rule design

- Model Liturgy prokeimenon as a derived slot: `owner = owner(Epistle)`; Epistle owner is already an explicit Rule (Typ Ch I §6 p.37-38, Wichita Chart II p.34 + fn 4). Tag the derivation I with the 16-date evidence.
- Sat Vespers prokeimenon: constant "Lord is King" with an exception table (Master-feast eves, Triodion Lent eves (conflict), Pascha cycle).
- Sun Matins prokeimenon: constant tone-of-week with exception only for Theotokos/Master feast on Sunday.
- Alleluia verse: not derivable from Antiochian sources. Either omit the slot from the review output or mark it M and fill from DCS key.

## 5. New questions / gaps

1. Liturgy prokeimenon: no Antiochian source states it. Confirm in Violakis (Greek 1888 scan, Liturgy/Sunday-with-saint sections) and ask OLG (OLG@antiochian.org). Is "owner of Epistle" the written rule or a convention?
2. Alleluia verse: which verse set does Antiochian practice use when a saint's Epistle is read (DCS keeps Sunday's)? Needs Violakis/OLG.
3. ANCA vs Typikon Ch I §3 p.13 on Triodion eves (Great Prokeimenon): ANCA Lent 1 eve shows "Lord is King". Check Cheesefare (Feb 21 2026) and Lent 2-5 eves in ANCA, and Triodion book.
4. Sat Vespers Lord-feast-on-Saturday contradiction in Typikon: Wichita resolution (Friday = great prokeimenon, Saturday = Lord is King) needs a keyed example. Find ANCA files for a Saturday Master-feast eve/Sunday.
5. No samples yet for Sunday + Theotokos/Master feast Liturgy/Matins. Needs `liturgicday`-page-driven filename discovery (Sep 14 2025 had no links when rendered; try other years).
6. Pentecostarion and Triodion Sunday propers (prokeimenon/alleluia text and when they replace tone sets) not checked. Lent 1 (Mar 1 2026) shows a non-tone text.
7. Russian/Ruthenian combine two prokeimena/alleluias. Confirm Antiochian practice never does (UK parishes may differ).
8. Prokeimenon text table for 8 Sunday tones: use DCS/ANCA keys, no ticket yet.
