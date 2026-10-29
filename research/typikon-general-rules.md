# Typikon general rules: Sat Great Vespers, Sunday Matins, Sunday Liturgy

Issue #6 (map #5). Research branch, throwaway, never merged.

## Source + conventions

- Source: Antiochian Typikon (Bp Demetri Khoury / Fr John Morris, 2011). Scope read: Intro (pp.3-5), Ch I (pp.8-41), Ch II (pp.42-47), Ch III (pp.48-53), Ch IV (pp.54-57), Ch IX (pp.568-572), Glossary (pp.575-580). Triodion/Pentecostarion/Menaia chapters only grepped for pointers.
- Cite form: `Ch I §3 p.12` = "Antiochian Typikon, Ch I §3 (Vespers), p.12". Page = printed "Back to Table of Contents NN" footer of the page holding the text. Book's own TOC is off by one in places (e.g. §5 Matins listed p.19, text starts p.20).
- Ch I §: 1 Opening p.8-9; 2 9th Hour p.10; 3 Vespers p.11-16; 4 Dismissals p.17-19; 5 Matins p.20-33; 6 Liturgy p.34-41.
- All content paraphrased; quotes are short hymn incipits only. No PDF/long excerpts committed.
- Terms: Res = Resurrection (Octoechos, tone of week); LIHC = "O Lord I have cried" (Ps 140 etc.); doxastikon = "Glory"; GN = "Glory..., Now..." slot.
- Status tags: **E** explicit rule; **C** conditional/variant (coincidence, belongs to map's "not yet specified" precedence ticket; listed for completeness); **D** deferred to another book; **G** gap/ambiguity (section 6).

## 1. Source caveats that affect design

1. Typikon is monastic-origin; parishes must apply it via their bishop; outlines in Ch IX are explicitly the N. American Antiochian (NA) usage from the 2010 Liturgical Guide, not the Arabic Typikon proper (Intro p.4-5; Ch IX p.568 fn 342). Editor's note: real practice may differ significantly from Typikon (Intro p.3 fn 2).
2. Three explicit NA-vs-Violakis (1888 Greek) divergences (Intro p.4; fn at Ch I §5 p.25, p.29, p.33; Ch III p.50-51 fn 36-37):
   - Katavasia sung after each ode (traditional), not all together after ode 8.
   - Matins Gospel sung before the canons (after prokeimenon), not between odes 8 and 9. Ch III p.50 text itself still describes Violakis order; Ch IX p.570 outline uses NA order.
   - Post-Great-Doxology troparion alternates: tone of week 1-4 "Today salvation...", 5-8 "Having risen..." (Typikon text: always "Today salvation", priest/bishop decides). Ch IX p.571 gives the NA alternation.
   - **Design: use NA order; Typikon text alone is not sufficient.**
3. Old-vs-New calendar: Typikon declines to give New Calendar directions; defer to bishop (Intro p.5).

## 2. Cross-cutting rules

| Topic | Rule | Cite |
|---|---|---|
| Tone of week | Used as a pure parameter ("Res in tone of the week") for stichera, aposticha, apolytikion, God-is-the-Lord, kathismata, hypakoe, anabathmoi, prokeimenon, canon, Typika/Beatitudes, praises, exaposteilarion. Sat eve Vespers uses the Sunday's tone. Typikon never defines how tone is assigned. Glossary only: 8-tone cycle starts Tone 1 on 2nd Sunday after Pentecost. **D/G** | Ch I §3 p.12; Glossary "Tone" p.580 |
| Tone-dependent fixed choice | Post-Doxology troparion by tone (1-4 vs 5-8) **E** (NA). Beatitudes/Typika psalm tones fixed (Ps 102 tone 8, Ps 145 tone 2). Great Doxology and post-Doxology troparion sung in tone of the Matins praises "Glory" (Ch III). | Ch I §5 p.33; Ch III p.51 |
| Eothinon | 11 Resurrection Gospels, each with its own hymns, exaposteilarion, "Glory" (Glossary). Typikon says "one of the 11" is read but gives **no rotation rule** (**D/G**; calendar already yields). Eothinon "Glory" + exaposteilarion summarise the Gospel. | Ch I §5 p.29 fn 21, p.31; Glossary p.576 |
| Great vs Small Vespers | Saturday evening service is Great Vespers (1st kathisma "every Saturday"). Small Vespers appears only as part of All-Night Vigil (52 Saturdays + listed feasts): Great Vespers then moves later. Typikon gives no parish criterion for when Vigil applies. | Ch I §3 p.11; Ch I §4 p.18; Ch IV p.54 |
| Liturgy author | Chrysostom/Basil: nothing in Intro/Ch I-IV/IX assigns Basil to any Sunday. Only: Great Dismissal names the author (Ch I §4 p.17); some Basil/Chrysostom-specific hymns (Cherubic same; "It is truly meet" vs "In thee rejoiceth"; Ch I §6 p.38); Communion hymn rule when Royal Hours+Vespers lead into Basil (p.39). Pointer only: Triodion chapter states Basil for Lent Sundays 1, 3, 4 (Ch VI pp.488, 493, 495), and Holy Thursday/Saturday. **G** | as cited |
| Dismissal | Great Dismissal at Great Vespers, Matins, Liturgy. Sunday adds Resurrection phrase ("who rose again from the dead"); after a Lord feast on Sunday, feast phrase first then Resurrection phrase. Saint of day named only if saint has a doxastikon. Liturgy adds author name before saint. | Ch I §4 p.17-18 |
| "Celebrated" saint | A saint without a doxastikon at LIHC gets no troparion at Vespers, Matins or Liturgy on a Sunday (only Res troparion + theotokion). Defines what "saint celebrated" means in Ch III. Rank terms (great saint, polyeleos) not defined here; come from Menaion (**D**). | Ch I §3 p.16 |

## 3. Saturday Great Vespers (eve of Sunday)

Slot order (Ch III p.48-49; Ch IX p.568 outline; Ch I §3). Items marked [V] are the Variable parts.

| # | Slot | Rule (plain Sunday unless noted) | Tag | Cite |
|---|---|---|---|---|
| 0 | 9th Hour before | Sat evening: troparion "O Holy Apostles and Martyrs" + kontakion "O Lord, healer of mankind"; Sunday proper: Res troparion + hypakoe instead of kontakion. Sunday/great-feast Vespers: dismissal of 9th Hour from Royal Doors, Vespers begins. | E | Ch I §2 p.10; Ch II p.42 |
| 1 | Opening, Ps 103, Great Ektenia | Fixed. | E | Ch IX p.568 |
| 2 | 1st Kathisma (Ps 1-8) | Read every Saturday at Great Vespers even on a Lord/great-saint feast. Omitted with Res verses if Nativity, Theophany, Transfiguration, or Pentecost evening fall on Sunday (Nativity/Theophany on Saturday: Res hymns still take precedence; text ambiguous, **G**). Palm Sun, Thomas Sun, Cross on Sunday: kathisma read, Res service omitted. Ch IX outline omits this slot. | E/C | Ch I §3 p.11; Ch III p.48; Ch IX p.568 |
| 2a | "First three psalms" | Read on eve of Theotokos feasts (not Presentation/Annunciation); omitted on Sun/Fri eve if great feast next day; omitted on eve of great-saint feast except Sat/Mon. Wording unclear in relation to Sat kathisma. | C/G | Ch I §3 p.11 |
| 3 | LIHC psalms | Ps 140 with verses in tone; "Set a watch" verses skipped on feasts; only as many verses as stichera. Psalm numbering inconsistent across Ch I (140,142,130,116), Ch III (140,141), Ch IX (141,142,130,117). | E/G | Ch I §3 p.11-12; Ch III p.48; Ch IX p.568 |
| 4 | LIHC stichera [V] | **No saint doxastikon:** 7 Res + 3 saint; Glory/Now in tone of week. **Saint with doxastikon:** 6 Res + 4 saint; Glory = saint; Now = tone of week (Ch III). Alternative 4 Res + 6 saint (10 total) listed for: Archangels, Nativity of Baptist, Peter&Paul, John Evangelist (Sep 26), 3 Hierarchs (not on Triodion Sunday), Fathers of 4th/7th Councils, Demetrius, Nicholas. Total 10 in every stated case. No saint at all: **not stated (G)**. Count of Octoechos Res stichera available/which ones: **D**. | E | Ch I §3 p.12; Ch III p.48 |
| 4a | LIHC variants | Sun between Theotokos feast and leavetaking: 10 = 6 Res + 4 feast. Great saint on Sun after Lord feast or on Theotokos leavetaking: 4 Res + 3 feast + 3 saint. Res stichera omitted on Nativity, Epiphany, Palm Sun, Thomas Sun, Pentecost, Transfiguration, Cross, Sun before Nativity on Dec 24 (apolytikion still sung at Matins/Liturgy). | C | Ch I §3 p.12 |
| 5 | LIHC "Glory/Now" [V] | Plain: tone of week. Variants (C): Theotokos feast on Sunday: both for feast; Theotokos leavetaking (not Dormition): only feast Glory/Now; Lord leavetaking, Sundays between Lord feast and leavetaking, great-saint feast on Sunday: Glory = feast (or saint), Now = 1st theotokion of tone of week; Presentation on Triodion Sun 1-4: Glory Triodion, Now feast; Annunciation on Lent 3 or Lazarus Sat: Glory Triodion, Now Annunciation; on Pascha: Glory Pentecostarion, Now Annunciation; on Palm Sun/Bright Mon: both Annunciation; George/John Evangelist May 8/Constantine+Helen on Pentecostarion Sundays: Glory saint, Now Sunday/Lord feast; saint lacking Glory: theotokion of tone; great martyr on Sun of Lord/Theotokos feast: Glory saint, Now tone of week. | C | Ch I §3 p.13 |
| 6 | Little Entrance, O Gladsome Light | Fixed. | E | Ch III p.49 |
| 7 | Prokeimenon | Sat eve: "The Lord is King" (3x). Rule says always, even if Lord feast on Saturday, exceptions Nativity and Epiphany; next bullet says a Lord feast on Saturday takes its own prokeimenon (contradiction, **G**). Triodion: Great Prokeimenon on eves of Cheesefare and Lent Sundays; Bright Week from Pentecostarion. | E/G | Ch I §3 p.13; Ch III p.49 |
| 8 | Readings | Only if a Lord feast or great saint falls on Sunday: Prophet readings (intro "Wisdom!"). Peter&Paul, John Evangelist, James, Andrew: Epistle readings. Plain Sunday: none stated in either Ch I or Ch III (inferred none). | C | Ch I §3 p.13-14 |
| 9 | Fervent Ektenia, Evening Prayer, Litany of Supplication | Fixed. | E | Ch III p.49 |
| 10 | Litia + Artoklasia | Feasts only (see map "not yet specified"). Outline of mechanics in Ch IX. Not part of plain Sunday outline. | C | Ch I §3 p.14; Ch IX p.568 |
| 11 | Aposticha [V] | Res aposticha in tone of week never omitted on Sunday eve unless the whole Res service is omitted. Form: first sticheron without verse; 3 Ps 92 verses before the last 3 stichera (so at least 4 stichera). Between Thomas Sun and pre-Ascension Sun: first Res sticheron then Paschal stichera. Total count: **D**. | E | Ch I §3 p.14; Ch III p.49 |
| 12 | Aposticha Glory/Now [V] | Plain: GN for Theotokos in tone of week. Saint with Glory: Glory saint, Now Theotokos in tone of the Glory (Ch III). Ch I p.15 says Now = "Resurrection in the tone of the Glory" (**G**, wording differs). Single combined "Glory-Now" (C): Theotokos feast on Sun, Sundays after Theotokos/Lord feasts, leavetaking or forefeast on Sunday, Lent Sundays 1-3 ("3 Sundays of Great Lent"), Myrrhbearers, Joachim and Anna, Archangels. Others C: Presentation on Triodion Sun 1-4 (Glory Triodion, Now feast); Annunciation Lent 3/Palm Sun (same) or Pascha; great saint after Lord feast (Glory saint, Now feast; no special Glory: theotokion). | E/C | Ch I §3 p.14-15; Ch III p.49 |
| 13 | Simeon, Trisagion prayers | Fixed. | E | Ch III p.49 |
| 14 | Troparia [V] | Plain Sunday: Res apolytikion; GN = theotokion of tone of week. Great saint with LIHC Glory: Res; Glory saint; Now = theotokion in tone of the saint's troparion (Ch III) [vs Ch I p.16 case: after Lord feast, Now = feast]. Saint without LIHC Glory: no saint troparion. Variants C: Theotokos feast/leavetaking of Lord feast: Res + Glory feast + Now feast; Sunday after feast: Res (1x) + GN feast (Matins: Res 2x + feast 1x); forefeast on Sunday: Res (1x) + GN forefeast; Annunciation on Lent 3/Lazarus Sat/Palm Sun have own combos. | E/C | Ch I §3 p.15-16; Ch III p.49 |
| 15 | Dismissal | Deacon "Wisdom", choir "Master bless", Great Dismissal (Res phrase). If Artoklasia held, alternate formula. | E | Ch III p.49; Ch I §4 p.17 |

Vigil variant (Ch IV p.54-56), E but distinct Service: Small Vespers first (3 stichera, first repeated = 4; GN Theotokos; prokeimenon; evening prayer; Simeon; troparia; dismissal), then Great Vespers later with 1st kathisma tone 8, Little Entrance at "For his mercy...", litia of temple patron, 5 loaves, Apostolic reading (Acts Pascha-All Saints; else Epistles/Revelation), then vigil Matins. Not tied to Sunday-specific Variable parts beyond those above.

## 4. Sunday Matins

Slot order (Ch I §5; Ch III p.49-51; Ch IX p.570-571). NA order assumed (Gospel before canons).

| # | Slot | Rule (plain Sunday unless noted) | Tag | Cite |
|---|---|---|---|---|
| 0 | Midnight Office | Replaced on Sundays by triadikos canon + 4 triadika megalynaria + hypakoe of tone (troparion of feast instead if Theotokos/great saint; litia of saint inserted; Triodion Sundays: 3 penitential troparia instead of hypakoe). Separate Service, not in issue scope. | E | Ch I §5 p.20; Ch III p.49 |
| 1 | Opening, 6 Psalms, Great Ektenia | Fixed. Ch IX gives fixed opening troparia (O Lord save thy people / Glory Cross / Now Theotokos). | E | Ch IX p.570 |
| 2 | "God is the Lord" + troparia [V] | Tone of week, 4x. Plain: Res apolytikion, Glory = Res again, Now = theotokion (net Res 2x + theotokion 1x). Saint celebrated: Res (1x), Glory saint, Now theotokion in tone of saint's troparion. C: Theotokos feast / Lord leavetaking: Res, Glory feast, Now feast; Sunday after Lord/Theotokos feast: Res, Glory Res, Now feast; great saint on feast Sunday: Res, Glory saint, Now feast. Lent/Triodion weekday alleluia variants not Sunday. | E/C | Ch I §5 p.21; Ch III p.49-50; Ch I §3 p.16 |
| 3 | Psalter kathismata | Sunday: Kathismata 2 and 3 (Ps 9-23); 3rd replaced by Ps 118 "Blessed are the blameless" on Lent weeks 1-4,6; 2,3,17 on Lent wk 5 and Thomas Sun to Sep 21; 2,3 + Polyeleos on Palm Sun. Greek-derived table (Sep 22-Dec 20, Jan 15-Sat before Meatfare) says Sun = 2,3,19 (as in book; conflicts with 2,3,17 elsewhere, **G**). Modern practice may read Psalms/Polyeleos before Matins on non-feast Sundays. | E/G | Ch I §5 p.22-24 |
| 3a | Polyeleos | Only if saint celebrated (Ch III) / feasts: Ps 134-135 (Lord feasts, great saints), Ps 44 (Theotokos), Ps 136 (Meatfare, Cheesefare). Chanted before 3rd kathisma. Plain Sunday: none (inferred from Ch III). | E/C | Ch I §5 p.22; Ch III p.50 |
| 4 | Poetic kathismata [V] | Plain: 2 Octoechos kathismata (Glossary p.579; Glory/Now pattern Res/Res/theotokion is inferred from the Theotokos-feast variant, not stated). Great saint: 1st and 2nd Res, 3rd for saint; "greater" saint: Res hymns in first two, Glory saint, Now Theotokos, whole 3rd for saint (allocation wording unclear, **G**). Theotokos feast on Sunday: two Res kathismata with Now from feast, 3rd whole feast. Sunday after/leavetaking of Theotokos feast: two Res (Now from feast), no 3rd. | E/C | Ch I §5 p.25; Ch III p.50; Glossary p.579 |
| 5 | Evlogetaria, hypakoe, anabathmoi, prokeimenon | Plain: evlogetaria, little ektenia, hypakoe (tone), anabathmoi (tone), prokeimenon (tone). Omitted evlogetaria when Theotokos feast on Sunday (but NA keeps evlogetaria + eothinon Gospel). Anabathmoi: 3 antiphons tones 1-7, 4 for tone 8; Ps 128 on major feasts. Actual hymn/verse text: **D** (Octoechos). Prokeimenon text not given anywhere: **D/G**. | E/D | Ch I §5 p.25-26 fn 18; Glossary p.575 |
| 6 | Matins Gospel + hymns [V] | Eothinon Gospel (which one: **D/G**). Order: Gospel, "In that we have beheld the Resurrection", Ps 50, Glory/Now "intercessions of apostles/Theotokos", "Have mercy" + idiomelon "Jesus having risen", Intercession, Kyrie x12. Triodion Sundays: replaced hymns ("Open unto me", "Prepare for me", "If I think upon the multitude"). Violakis position (after ode 8) overridden by NA. | E | Ch I §5 p.29; Ch III p.50; Ch IX p.570 |
| 7 | Canons [V] | Octoechos Res canon "rarely omitted"; omitted/replaced: Lent Sun 3 and Sun before Nativity (Genealogy) (first hymns Res, special refrain), Pentecostarion Sundays (Myrrhbearers, Paralytic, Samaritan, Blind Man) use Pentecostarion canon. With great saint: 4 Res + 4 saint troparia per ode (refrains "Glory to thy holy Resurrection" / "Saint of God, intercede"). Theotokos/Lord feast on Sunday: Octoechos heirmos + 3 troparia then feast canon; two feast canons: 12 per ode; Sunday after two-canon feast: one. No saint: count not stated (**G**). Ch IX outline lacks canon slot. | E/C | Ch I §5 p.26-27; Ch III p.50; Ch IX p.570 |
| 8 | 3rd-ode kathisma | Kathisma of saint of day + theotokion after little ektenia; if Theotokos feast: Octoechos kontakion/oikos first, then kathisma 1x; same on Triodion Sundays and great-saint feasts. | E | Ch I §5 p.27-28; Ch III p.50 |
| 9 | 6th-ode kontakion/oikos | Ordinary Sundays: Octoechos kontakion + oikos (+ monologion of saint, Ch III). Menaion/Triodion/Pentecostarion kontakion instead on: Theotokos feast, Triodion Sundays except Lent 2, 4, 5, Pentecostarion Sundays, Forefathers, Genealogy, Sun after Nativity, 3 Holy Fathers Sundays, All Saints; and on listed saint feasts on Sundays (Baptist nativity, Peter&Paul, John Evangelist Sep 26, Andrew, 3 Hierarchs pre-Triodion, Archangels, Demetrius, Nicholas; George/John May 8/Const+Helen in Pentecostarion), except Thomas, Pentecost, All Saints. | E | Ch I §5 p.28; Ch III p.50 |
| 10 | Katavasia | "I shall open my mouth" (Akathist) from Cross leavetaking to Nov 21; Presentation leavetaking to Triodion; Lent Sun 2,4,5; All Saints to Jul 27; saint feasts within these. Feast katavasia between forefeast and the Sunday after a Lord/Theotokos feast. Triodion/Pentecostarion seasonal ones. Glossary gives a second, date-based katavasia table that differs in places (e.g. Sep 22-Nov 7 Theotokos; Nov 8-20 Presentation): **G**. Sung after each ode (NA). | E/G | Ch I §5 p.27-29; Glossary p.576-577 |
| 11 | 9th ode / "More honorable" | "More honorable" + 9th ode verses throughout year; replaced by feast 9th ode with megalynaria on Lord/Theotokos feasts, Holy Week, Pentecostarion Sundays to Ascension; leavetaking variants. | E/C | Ch I §5 p.29-30 |
| 12 | "Holy is the Lord", Exaposteilaria [V] | Plain: exaposteilarion of eothinon, then Theotokos (Ch III). Saint celebrated: eothinon, saint, Theotokos. Variants C: Theotokos feast/leavetaking: Res 1x, feast 2x; Sunday after Lord feast: Res, feast, day; Paschal-season sets. "Holy is the Lord" 3x (NA; book says 2x if "Exult ye" follows). | E/C | Ch I §5 p.30; Ch III p.51 |
| 13 | Praises (Ainoi) stichera [V] | Plain: 8 Res stichera (verses "Praise God in his Sanctuary", "Arise O God", "I will confess thee"). With saint stichera: Res + saint, last two saint verses taken from Vespers aposticha of the saint (counts unstated, **G**). Variants C: Theotokos/leavetaking: 4 Res + 4 feast; great saint after Lord feast: 3 Res + 2 feast + 3 saint; Triodion Sun 1-2: 9 = 4 Res + 2 Triodion + 3 saint; Annunciation on Lent 3: 2 Res + 3 Cross + 3 feast; on Lent 4/5: 4 + 4. Octoechos availability: **D**. | E/C | Ch I §5 p.30-31; Ch III p.51 |
| 14 | Praises "Glory" [V] | Default: eothinon doxastikon; Now = "Most blessed art thou" in tone of the Glory. Replaced by Sunday's own Glory: Triodion Sundays, Pentecostarion Sundays, Forefathers, Genealogy, Sun after Nativity, Sun before Epiphany (if Jan 5), 3 Holy Fathers Sundays. Replaced by feast Glory on: Baptist (Nativity, Synaxis, Beheading), Peter&Paul, 12 Apostles, 4 Evangelists, Archangels, 3 Hierarchs (pre-Triodion), Sep 1, temple patron, every great feast; optionally George/Demetrius/Nicholas/Const+Helen. Pentecostarion Sundays (Myrrhbearers..Blind Man): "Today is the day of the Resurrection". | E/C | Ch I §5 p.31-32 |
| 15 | Great Doxology + troparion | Great Doxology on Sunday in tone of the Glory of the Praises; then "Today salvation" (tones 1-4) / "Having risen" (tones 5-8) NA. Palm/Thomas Sun: feast troparion. Great Lord feast on Sunday w/o Res service: omit. | E | Ch I §5 p.32-33; Ch III p.51; Ch IX p.571 |
| 16 | After Doxology | Ch III: "The Divine Liturgy then begins." Ch IX outline "when followed by the Divine Liturgy". Case of Sunday Matins not followed by Liturgy (aposticha etc.) not stated for Sunday (**G**). | G | Ch III p.51; Ch IX p.570 |

## 5. Sunday Divine Liturgy

No Liturgy outline in Ch IX. Rules from Ch I §6 p.34-41 and Ch III p.51-53.

| # | Slot | Rule (plain Sunday unless noted) | Tag | Cite |
|---|---|---|---|---|
| 1 | Typika + Beatitudes [V] | Every Sunday: Typika (Ps 102 tone 8, Ps 145 tone 2) + Beatitudes with 8 Res hymns in tone of week. First 4 Beatitudes without hymns; from 5th, Res hymns, then Glory/Now sticherion. Lord/Theotokos feast on Sunday: 8 = 4 Res + 4 from feast canon ode 6; then feast antiphons and entrance hymns apply (rules at p.34: wording inconsistent about which antiphon is Res, **G**). Saint feast on Sat/weekday: Typika. | E/C | Ch I §6 p.34; Ch III p.51 |
| 2 | Little Entrance + entrance hymn | During Beatitudes. "O come let us worship... risen from the dead" (Sundays and Sundays after Theotokos feast); special entrance hymns for Presentation, Annunciation, leavetakings; Thomas Sun to Ascension: "Come let us worship". | E/C | Ch I §6 p.34-35; Ch III p.51 |
| 3 | Troparia [V] | Res apolytikion always first (Ch I §6). Plain: Res + temple patron (+ saint only if celebrated, i.e. doxastikon at LIHC) then kontakion. After great feast / leavetaking / great saint: Res, feast, saint, patron. Departed: troparion of departed before patron. | E | Ch I §6 p.35; Ch III p.52; Ch I §3 p.16 |
| 4 | Kontakion [V] | Seasonal schedule (Sep 1 Indiction; Cross; "O undisputed Intercessor" from Cross leavetaking to Nov 8; Nativity/Epiphany/Presentation cycles; Lent: "To thee the Champion Leader"; Pascha, Thomas, Mid-Pent, Pentecost, All Saints; Apostles fast to Jul 27; Transfiguration; Dormition cycle; Nativity of Theotokos). Typikon does not say whether the Octoechos Sunday (Res) kontakion is used at the Liturgy; the list is applied by calendar (**G**). Weekday kontakia list not relevant to Sunday. | E/G | Ch I §6 p.35-37 |
| 5 | Trisagion | Fixed; exceptions: "As many as have been baptized" (Nativity, Epiphany, Lazarus Sat, Holy Sat, Pascha-Bright Week, Pentecost etc.), "Before thy cross" (Cross, Lent 3). | E | Ch I §6 p.37 |
| 6 | Epistle / Gospel [V] | Sunday readings from lectionary (**D**). Great saint on Sunday: Epistle of saint + Gospel of Sunday. Both of feast on: Baptist feasts, Peter&Paul, 12 Apostles, Evangelists, 3 Holy Fathers Sundays, 3 Hierarchs (pre-Triodion). Nativity of Theotokos on Sunday: Sunday-before-Cross readings (as stated). Presentation on Triodion Sunday: Epistle feast + Gospel Sunday (Matins Gospel: feast Liturgy Gospel). Annunciation cases (Lent 3: Epistle Sun + Gospel feast; Lent 4-5: both feast; Lazarus/Palm Sat/Sun: Epistle feast, Gospel Sun). Dormition: both feast. Prokeimenon before Epistle not specified: **D/G**. | E/C | Ch I §6 p.37-38 |
| 7 | Alleluia after Epistle | Alleluia 3x tone 2 every Liturgy (incl. Bright Week), except Holy Sat. | E | Ch I §6 p.38 |
| 8 | Cherubic Hymn | Standard (Holy Thu/Sat special). | E | Ch I §6 p.38 |
| 9 | "It is truly meet" | Chrysostom: "It is truly meet" after "Especially"; where megalynarion sung, 9th ode with megalynaria on Lord/Theotokos feasts; Basil: "In thee rejoiceth"; Thomas Sun / Paschal Sundays special. Plain Sunday: "It is truly meet" (Ch III). | E | Ch I §6 p.38-39; Ch III p.52 |
| 10 | Communion hymn [V] | "Praise ye the Lord" on every Sunday not a Lord/Theotokos feast or leavetaking. Own feast hymn: Lord feasts; Sep 1; Aug 1; Baptist, Peter&Paul, apostle, evangelist, Andrew, 3 Hierarchs, Const+Helen, Archangels (Nov 8) falling on Sunday. Theotokos feast on Sunday: "I will take the cup of salvation"; Annunciation: "The Lord hath chosen Zion". Lent 3: "The light of thy countenance". 4 Sundays after Thomas: "Receive ye the Body". All Saints/Joachim and Anna: "Rejoice in the Lord". | E | Ch I §6 p.39-40; Ch III p.53 |
| 11 | Post-communion | "We have seen the true light" (exceptions: feast troparion on Lord feasts/Lent 3/Lazarus Sat; Paschal and Ascension variants). "Blessed be the Name" 3x tone 2. | E | Ch I §6 p.40; Ch III p.53 |
| 12 | Dismissal | Great Dismissal with Res phrase, author name (Chrysostom/Basil), saint of day only if doxastikon. | E | Ch I §4 p.17 |

## 6. Gaps, ambiguities, internal inconsistencies (for tickets)

1. **Basil vs Chrysostom**: no general assignment in scope chapters (G). Lent Sundays 1,3,4 named in Triodion chapter only; Sunday 2/5 and Palm Sunday unverified here.
2. **Tone-of-week assignment**: not defined except glossary note (Tone 1 at 2nd Sunday after Pentecost). No Pentecostarion tone-restart rule read.
3. **Eothinon rotation**: absent; only "one of 11". Needed externally (Octoechos/Gospel book).
4. **No-saint plain Sunday**: LIHC stichera count (Res only?), Matins canon content, Matins praises when saint has no stichera: only partially stated.
5. **Octoechos content counts** (how many Res stichera/aposticha/canons exist, which are chosen when fewer slots): deferred to Octoechos; Typikon gives slot counts only.
6. **Sunday Liturgy kontakion** vs Octoechos Res kontakion; **prokeimenon** (Sat Vespers: fixed "Lord is King"; Matins, Liturgy: unnamed); **Liturgy Epistle/Gospel lectionary**: deferred.
7. **Prokeimenon contradiction** for Saturday Vespers on a Lord feast (Ch I §3 p.13): "always The Lord is King" vs "own prokeimenon".
8. **"Now" allocation wording**: Vespers aposticha Now = Res (Ch I p.15) vs Theotokos (Ch III p.49). Great saint on Sunday LIHC Now: "1st theotokion of tone" (Ch I p.13) vs "tone of week" (Ch III p.48).
9. **Katavasia calendars**: Ch I §5 p.28 vs Glossary table p.576-577 differ.
10. **Kathisma table**: Sunday 3rd kathisma 19 vs 17 across seasonal tables (p.22-24).
11. **Psalm numbering** for LIHC group differs across Ch I/III/IX.
12. **Ch IX outlines are partial**: Great Vespers omits 1st kathisma; Matins omits canons, polyeleos, Psalter kathismata; no Liturgy outline; no Small Vespers outline (Ch IV only for Vigil).
13. **Great vs Small Vespers choice** and Vigil adoption: parish-level, bishop-delegated (Intro p.4-5); no rule.
14. **Rank vocabulary** (great saint, polyeleos feast, has doxastikon) not defined in scope chapters; defined per feast in Menaion chapters (Ch V).
15. **Matins Praises with saint stichera**: resulting counts not stated; "last two verses replaced by two Vespers aposticha stichera" (Ch III p.51).
16. **Optional readings**: "Some chant..." (Ch I p.32), "if presiding priest wishes" (More honorable on 3 Hierarchs) and tone-of-troparion choice = pastor/bishop discretion; encode as configurable.
17. **Sunday Matins not followed by Liturgy**: not specified.
18. **Annunciation-on-Palm-Sunday etc.** differ between slots (Vespers LIHC both Annunciation; aposticha Glory Triodion): coincidence ticket.
19. **Antiphon rule wording for Theotokos feast on Sunday** (Ch I §6 p.34) ambiguous about Res vs feast antiphons.
20. **Nativity/Theophany on Saturday**: kathisma/Res hymns rule in Ch I §3 p.11 ambiguous.

## 7. Deferred to other books (not read here)

- Octoechos: Res stichera/aposticha/apolytikion/theotokia/kathismata/hypakoe/anabathmoi/canons/kontakion/prokeimenon, eothinon hymns, exaposteilaria, praises; tone-of-week assignment.
- Menaion (Ch V): saint rank (doxastikon/polyeleos), Glory/stichera/troparia/canons per day; feast-specific coincidence rules.
- Triodion (Ch VI) / Pentecostarion (Ch VII): Sunday-specific replacements, Basil on Lent Sundays, Great Prokeimenon, kathisma/katavasia overrides. Pointers: Pharisee Sun p.470; Orthodoxy Sun p.486; Lent 2 p.489; Lent 3 p.490; Lent 4 p.494; Lent 5 p.502.
- Gospel book / lectionary: Sunday Epistle/Gospel and eothinon.
