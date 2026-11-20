# Public-domain Byzantine notation sources → hymn ids

Machine-readable index: `byzantine_pd.yaml`. Built from each book's printed contents list (Πίναξ), not by reading the music page by page. **verify** = the TOC entry implies the match but the pages haven't been checked.
All music is Chrysanthine "New Method" with Greek text underlay. Tone abbreviations: 1–4 = authentic, pl1/pl2/pl4 = plagal, grave = βαρύς (pl3).

## Books

| key | book | PDF | PDF page = |
|---|---|---|---|
| TA1 | Ταμείον Ανθολογίας, Konstantinos Protopsaltis, Constantinople 1845, vol.1 (Vespers, Matins, Holy Week) | `Ταμείον ανθολογίας … 1845.pdf` | printed + 6 |
| TA2 | same, vol.2 (Cherubic, Koinonika, Liturgy) — bound in same PDF | same | printed + 301 |
| PD2 | Μουσική Πανδέκτη vol.2 (Matins), Constantinople 1850 | `Μουσική Πανδέκτη Τόμος Β' … 1850.pdf` | printed |

TOC pages: TA1 PDF 4; TA2 PDF 5–6; PD2 PDF 854–856. Neither book contains the variable propers (Octoechos stichera, canons, feast troparia/kontakia), except where noted below.

## Mapped to project hymn ids

| hymn id | source | printed p. | PDF p. | tones / notes |
|---|---|---|---|---|
| `oct/t1..8/sun/apolytikion` | PD2 "Θεός Κύριος μετά Απολυτικ. και Θεοτοκ." Petros Lambadarios | 5–16 | 5–16 | God is the Lord + resurrectional apolytikia + theotokia, all tones — **verify** |
| `eothinon/01..11/doxastikon` | PD2 "Τα ένδεκα Εωθινά" Iakovos Protopsaltis | 538–573 | 538–573 | all 11 |
| `lit/matins/evlogetaria` | PD2 "Ευλογητάρια" Petros | 30–35 | 30–35 | pl1 |
| `lit/matins/doxology` | PD2 short doxologies by tone, Petros Lambadarios | 574–603 | 574–603 | syntomon, all tones (best parish fit) |
| | PD2 short doxology, Gregorios | 604–611 | 604–611 | grave |
| | PD2 short doxologies by tone, Manuel Protopsaltis | 612–645 | 612–645 | |
| | PD2 slow (argai) doxologies, various | 646–760+ | same | elaborate |
| | TA1 doxologies | 183–286 | 189–292 | 257 = "συντομαι εἰς ἤ ἤχους" (short, 8 tones) |
| `lit/communion/sunday` (Αἰνεῖτε) | TA2 Koinonika | 127, 150, 163, 182, 222, 230, 249 | 428, 451, 464, 483, 523, 531, 550 | tones 1, 2, 3, 4, pl1, grave, pl4 (no pl2) — page = start of that tone's section |
| `lit/communion/cup_of_salvation` (Ποτήριον) | TA2 Koinonika | in tone sections 1, 2, 3, 4, grave | | |
| `lit/communion/common/angels` (Ὁ ποιῶν τοὺς Ἀγγέλους) | TA2 | tone sections 1, 3, 4, pl4 | | |
| `lit/communion/common/remembrance` (Εἰς μνημόσυνον) | TA2 | tone sections 1, 2, 4, pl1, grave, pl4 | | |
| `lit/communion/common/apostles` (Εἰς πᾶσαν τὴν γῆν) | TA2 | tone sections 1, 2, 4, grave | | |
| `mov/56/communion` (righteous: Ἀγαλλιᾶσθε) | TA2 | tone sections 4, pl1, grave | | also martyrs' common |
| `mov/7/communion` (Thomas: Ἐπαίνει Ἱερουσαλήμ) | TA2 "τοῦ Θωμᾶ" | tone section pl1 | | |
| `mov/0/communion` (Σῶμα Χριστοῦ) | TA2 "τῆς Ἀναστάσεως" | tone sections 1, 2, 3, 4, pl1, grave | | **verify** that "of the Resurrection" = Σῶμα Χριστοῦ |
| `mov/39/communion` Ascension | TA2 | tone section 4 | | |
| `mov/49/communion` Pentecost | TA2 "τοῦ Ἁγίου Πνεύματος" | tone sections 1, 4 | | |
| `men/12-25/communion` Nativity | TA2 "τῶν Χριστοῦ Γεννῶν" | tone sections 2, grave, pl4 | | |
| `men/01-06/communion` Theophany | TA2 | tone section 2 | | |
| `men/03-25/communion` Annunciation | TA2 | tone sections 3, 4 | | |
| `men/08-06/communion` Transfiguration | TA2 | tone sections 1, 2, 3, pl1, pl4 | | |
| `men/09-14/communion` Elevation (Ἐσημειώθη) | TA2 "τοῦ Σταυροῦ" | tone sections 2, 3, grave, pl4 | | |
| `men/09-01/communion` Indiction | TA2 "τῆς Ἰνδίκτου" | tone sections 1, 4 | | |
| `lit/trisagion/baptized` | TA1 "Δύναμις· Ὅσοι εἰς Χριστόν" | 293 | 299 | Dynamis ending only |
| `lit/trisagion/cross` | TA1 "Τρισάγιον τοῦ Σταυροῦ" + "Δύναμις· Τὸν Σταυρόν σου" | 287, 293 | 293, 299 | **verify** whether 287 is Τὸν Σταυρόν σου |
| `lit/megalynarion/basil` (Ἐπὶ σοὶ χαίρει) | TA2 "Λειτουργία τοῦ Μ. Βασιλείου" | 99–103 | 400–404 | **verify** it contains Ἐπὶ σοὶ χαίρει |
| `lit/sun/t*/alleluia` | TA1 "Ἀλληλουάριον τοῦ Εὐαγγελίου" | 294 | 300 | generic alleluia melody, not per-tone verses |

## Fixed parts with no hymn id (booklet ordinary), useful later

- Cherubic Hymn: TA2 p.1–97 (3 per tone, Konstantinos; weekly set by Petros p.89). Ἀγαπήσω σε Κύριε p.98; Presanctified p.104; Νῦν αἱ Δυνάμεις p.105
- Magnificat (Ἄξιον ἐστίν τοῦ Ὄρθρου, i.e. "More honourable"): PD2 p.1; Τιμιωτέρα short (Petros) p.501, slow p.509
- Polyeleos: PD2 p.36–353; TA1 p.110, 132, 153
- Πᾶσα πνοή, before the Gospel: PD2 p.460. Before the Praises (Lauds): PD2 p.419–499 + p.523 (all tones); TA1 p.165, 169
- Psalm 140 / Vespers: TA1 Ἀνοιξαντάρια p.1, Κεκραγάρια p.24, Φῶς ἱλαρόν p.43, Θεοτόκε Παρθένε p.51
- Holy Week and Akathist: TA1 p.73–104; PD2 p.17–29

## HE: Heirmologion, Constantinople 1825 (Chourmouzios ed.)

File: `Ειρμολόγιον Πέτρου Λαμπαδαρίου και Πέτρου Βυζαντίου (1825).pdf` (527 pp; TOC PDF 521–522). Two parts:
- **HE1**, Petros Peloponnesios, katavasiai of the year (long heirmologic style). PDF = printed + 4 (p.1 ≈ PDF 4–5).
- **HE2**, Petros Byzantios, short heirmologion (closest to parish use). PDF = printed + 300 up to about p.185, then + 290 (about 10 pages of the Funeral service are missing from the scan).

| hymn id / slot | source | printed p. | PDF p. | notes |
|---|---|---|---|---|
| `oct/t1..8/sun/canon` | HE2 "Εἱρμοὶ τῶν Κανόνων κατ' ἦχον" | 3–147 | 303–447 | heirmoi by tone (incl. the resurrectional canons' heirmoi); troparia are sung to these, but their text isn't printed here |
| `{feast}/megalynarion` (9th-ode heirmos in place of "It is truly meet") | HE1 "Καταβασίαι ψαλλόμεναι ἀντὶ τοῦ Ἄξιον ἐστί" | 278–296 | 282–300 | confirmed on pages: Theophany, Annunciation, Transfiguration, Dormition, Elevation, Lazarus Sat, Palm, Pascha, Thomas, Mid-Pentecost, Ascension, Pentecost; Nativity and others **verify** |
| `matins.katavasia` (slot; no hymn ids yet) | HE1 katavasiai, full canons | 1–137 | 4–141 | see breakdown below |
| `lit/matins/evlogetaria` | HE1 | 210 | 214 | |
| `oct/t*/sun/lauds*` (verses only) | HE2 "Στιχολογία τῶν Αἴνων κατ' ἦχον" (Chourmouzios) | 195– | ≈485– | Πᾶσα πνοή + Praises psalm verses by tone; the stichera themselves are not here |
| model melodies (automela) | HE1 Προσόμοια p.216, Καθίσματα p.239; HE2 Προσόμοια p.148, Καθίσματα p.162 | | 220, 243; 448, 462 | needed for any hymn "to the melody of…" |
| Paschal stichera | HE2 Προσόμοια τοῦ Πάσχα | 172 | 472 | |
| Anavathmoi, Exaposteilaria by tone | HE1 | 265, 270 | 269, 274 | no ids yet |

Katavasiai (HE1, printed p. → `of:`): Dormition 1 · Nativity 9 · Sunday of the Cross 23 · Pascha 28 · Thomas 35 · Theophany 41 · Prodigal 56 · Presentation 61 · Annunciation & Entrance 67 · Transfiguration 74 · 1st Sunday of Lent 78 · Palm 83 · Pentecost 88 · Ascension 93 · Publican & Cheesefare 97 · Meatfare 102 · Pentecost (2nd) 107 · grave-tone tetraphonos 112 · Elevation 117 · Lazarus 124 · Mid-Pentecost 129 · Annunciation ode 4 135 · Elevation ode 7 137. Holy Week canons 138–209.

## AN: Anastasimatarion of Ioannis Protopsaltis, Constantinople 1905

File: `anastasimatarion-ioannou-protopsaltou-1905.pdf` (611 pp; TOC PDF 610–611). PDF = printed + 2 (checked at p.198, 398, 558). Combines Petros Lambadarios's slow (argon) setting with the short (syntomon) one. Ioannis died in 1866, so the music is out of copyright; the 1905 printing adds no new authorship.

Per tone, the printed page where each section starts (PDF = +2):

| tone | Vespers (+ aposticha, apolytikion) | Matins kathismata, anavathmoi, canons | slow katavasiai + Magnificat | Praises + Eothinon + doxology | penitential/martyrika + funeral |
|---|---|---|---|---|---|
| 1 | 1 | 14 (+ evlogetaria), 20 | 33 | 38 | 49 |
| 2 | 53 | 65 | 82 | 86 | 97 |
| 3 | 102 | 115 | 133 | 138 | 152 |
| 4 | 157 | 171 | 188 | 193 | 205 |
| pl1 | 209 | 223 | 239 | 243 | 258 |
| pl2 | 263 | 277 | 293 | 298 | 310 |
| grave | 314 | 327 | 352 | 360 | 378 |
| pl4 | 382 | 394 | 414 | 420 | 431 |

Then: last 3 Eothina 436 · **short Anastasimatarion 441–538** · 3 slow 9th odes 539 · Akathist canon 547 · Small Paraklesis 564 · Great Paraklesis 582 · Τὸν ἥλιον κρύψαντα 598 · Theotokos katavasiai for the whole year 603.

Mapping (to confirm page by page while transcribing):
- `oct/t*/sun/apolytikion`: end of each tone's Vespers section — **verify**
- `oct/t*/sun/hypakoe`, `oct/t*/sun/canon` (full: heirmoi + troparia), `oct/t*/sun/kontakion`/`oikos` (likely after ode 6), `oct/t*/sun/prokeimenon` (after the anavathmoi): in the "kathismata … canons" section — **verify**
- `oct/t*/sun/lauds1..n`: "Praises" section; the short versions are in the 441–538 section
- `eothinon/01..11/doxastikon`: spread across the Praises sections + 436 (the parish probably wants the short ones; PD2 p.538 has all 11 together)
- `lit/matins/doxology`: one per tone, at the end of each Praises section
- `lit/matins/evlogetaria`: tone 1, p.14
- `matins.katavasia` (Theotokos, year-round): 603

## Gaps (still need other PD books)

The Octoechos ids are now covered by AN (pending page checks). Still missing: `lit/sun/t*/prokeimenon` (Liturgy), `eothinon/*/theotokion`, every `men/*` and `mov/*` apolytikion/kontakion/antiphon/eisodikon, `lit/communion/common/apostle`, `lit/communion/sunday` in pl2.
Candidates: Iakovos *Doxastarion* or a Menaion/Doxastarion in music; Pandekti vols 1, 3, 4.

## Pergamos books (PG*)

38 printed books (1820–51) from the University of Athens Psachos collection, downloaded by `scripts/pergamos_fetch.py --out FETCHED` (not in git; scans CC BY-NC-ND). Each indexed book has `pergamos/<id>.yaml`: contents list (Πίναξ) transcribed, `layout` (printed page → PDF image; most scans are two-page spreads), entries mapped to hymn ids where clear. Indexing brief: `pergamos/BRIEF.md`. Skipped as papadic/secular/theory: 168132, 168140, 168146, 168164, 168165, 168176.

**Lookup across all books (this file + Pergamos):**
- `python scripts/hymn_sources.py men/12-25/apolytikion` (globs work: `'oct/t3/sun/*'`)
- `python scripts/hymn_sources.py --grep "Ἄξιον ἐστί"` searches titles/notes incl. unmapped entries
- `python scripts/hymn_sources.py --write` regenerates `hymn_sources.md`

Most useful for the services: PG183 (Pandekti vol 4, Liturgy), PG170 (Melifonos Terpsinoi, Liturgy fixed parts), PG056/PG156 (Tameion Liturgy volumes), PG138 (feast apolytikia/idiomela), PG059 (complete copy of HE1/HE2; HE1 p.258 Sunday apolytikia by tone), PG160/PG175/PG179 (Anastasimataria), PG149/PG152/PG177 (Doxastaria), PG174 (Preyer, Western 4-part Liturgy). Duplicates: PG181 = PD2, PG166 = TA1, PG168 ≈ TA2.

Open id questions (proposed, not in `hymns.py`): doxastikon slot suffixes (`doxastikonvespers/lity/aposticha/praises`), `named/{forefathers,before_nativity,after_nativity}/doxastikon`, Vespers ids (`ves/*`, PG180), Liturgy fixed parts (`lit/heis_hagios`, `lit/cherubikon/standard`, …, PG174/PG170).

Litany responses: only the threefold Κύριε ἐλέησον of the Augmented Litany after the Gospel, in 8 tones (PG056 p.26, PG156 p.145, PG170 vol.2 p.24, PG183 p.58; mostly Chourmouzios). No rubric on which tone is used. No book has the Great Litany responses (single Κύριε ἐλέησον, Παράσχου Κύριε, Σοὶ Κύριε).
