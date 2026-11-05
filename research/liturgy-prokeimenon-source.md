# Liturgy prokeimenon / alleluia source check (Sunday + saint's Epistle)

Issue: cmbryan/yocal#22 (map #5). Follow-up to `research/prokeimenon-alleluia-rules.md` (#21). Researched 2026-11-05. Throwaway research branch, never merged.
Public repo: paraphrase only, titles/URLs, short incipits. No PDFs committed.

Tags: **E** explicit (source + cite), **I** inferred, **M** missing. Trust: P = primary/authoritative, S = secondary compilation, R = other tradition.

## TL;DR

- **No Antiochian primary source states the Liturgy prokeimenon rule.** Re-checked Antiochian Typikon (Khoury/Morris 2011) and Bp Basil charts: silent. Rule stays **I** for Antiochian. Typikon does state *whose Epistle* is read (**E**).
- **New: Greek-usage corroboration (S, E-level wording).** A priest-compiled Greek Apostolos-of-Sundays guide lists dates where, on a Sunday, the saint's Apostle is read, and prints the saint's own prokeimenon with it. Matches ANCA/DCS. Not Violakis itself.
- **Alleluia verse set**: Greek guide (S) keeps the **Sunday-tone alleluia** with the saint's Apostle/prokeimenon (23 Oct entry). Matches DCS. Antiochian: **M**.
- **Russian/Slavic/Ruthenian (R)**: combine Sunday + saint (prokeimena, Epistles, alleluias), Sunday first. Differs from Antiochian/Greek.
- **Violakis 1888 scan not read**: host blocks automated fetch (403). OLG not reachable (no public page; email only).

## 1. Source results

| Source | Trust | Statement about Liturgy prokeimenon / alleluia | Status |
|---|---|---|---|
| Antiochian Typikon (Khoury/Morris 2011) Ch I §VII p.37-38 (`Typikon.pdf` local) | P | Which Epistle/Gospel on Sunday: for a "great saint" on Sunday, Epistle of saint + Gospel of Sunday; saint's Epistle+Gospel for Forerunner feasts, Peter&Paul, 12 Apostles, Evangelists, 3 Fathers Sundays, Three Hierarchs; Nativity of Theotokos on Sunday = Sunday's readings; Dormition = feast's. No prokeimenon mentioned. | Epistle owner **E**; prokeimenon **M** |
| Same, Ch I §VIII p.38 | P | Alleluia 3x tone 2 after every Epistle, none omitted; no verses, no choice rule. fn 28 only defends chanting it in Pascha. Holy Saturday: "Arise O God" replaces it. | Alleluia presence **E**; verses **M** |
| Same, Ch III Sunday Liturgy ~p.51; Menaion Nov 1 p.101, Nov 8 | P | Liturgy order: "Epistle followed by Alleluia"; no prokeimenon slot. Nov 1: Epistle for Cosmas+Damian, Gospel of Sunday. | **M** (prokeimenon) |
| Bp Basil (Wichita) Charts I-III, Descriptions of Ranks (dowama.org/node/31) | P/S | Chart II p.34 "New Testament Readings" row lists Epistle/Gospel owner by rank (fn 4: Forerunner etc. both from saint). Vespers/Orthros prokeimenon rows exist; **no Liturgy prokeimenon or alleluia row** in Charts I-III. "Keeping the Typicon" and ranking letter: nothing on it. | **M** |
| Greek Apostolos guide "Apostolos Kyriakon (kai tinon eorton)" (Fr "G. Th."; Google Doc export, YouTube channel KERMENI; Greek; Apostle book compilation, not Violakis) | S | Header list (p.2): on listed dates falling on Sunday, "we say the Apostle of the saint" (when officially celebrated); includes 1-11, 8-11, 25-1, 23-10, 26-10; separate list where Gospel+Apostle of feast taken (18-10, 16-11, 21-11, 14-9, 25-12...). Each saint entry prints the saint's **own prokeimenon + verse** with that Apostle (e.g. 8-11 "He makes his angels spirits"; 23-10 Ps 18). 23-10 note (p.57): saint's prokeimenon, "alleluiarion of the tone of the Sunday". Leavetaking 13-8 Sunday: prokeimenon+alleluia of the feast. Plain Sundays: "Prokeimenon and Alleluia of the tone of the Sunday". | prokeimenon **E (S)**; alleluia **E (S)**, one note |
| Andreev, *The Typicon* (Russian usage; ponomar.net `typicon_selected.pdf`, 2014 draft) PDF p.24, 31, 36, 40 (+fn 90 p.24, fn 22 p.47) | R | Sunday + saint with polyeleos/vigil: "Prokimenon, Epistle, Alleluia, Gospel, Communion hymn: for Sunday first, then for the Saint." Simple service: Prokimenon+Alleluia in current tone **and** for the saint if appointed; fn 90 cites Rozanov: whenever Epistle+Gospel appointed for the saint, prokeimenon, alleluia, communion verse are chanted for the saint too. | **E (R)**, differs |
| Metropolitan Cantor Institute, Divine Liturgy on Sunday (mci.archpitt.org/setting/Divine_Liturgy_Sunday.html) | R (Ruthenian) | Polyeleos/vigil feast on Sunday: combine two prokeimena (first verse only of first, second's verse omitted) and two alleluias. Great Lord feast replaces Sunday. Lord's postfeast: Sunday only; leavetaking: feast's added. | **E (R)** |
| OCA `liturgics/outlines/prokeimenon-of-the-day` | R | Vespers only; Saturday-evening prokeimenon never replaced. Nothing on Liturgy. | n/a |
| Violakis 1888 (digital.lib.auth.gr/record/125938) | P | Not read: record returns HTTP 403 to scripted fetch; browser download would be needed, plus Greek OCR/eyeballing. Greek Protheoria pages (patirxristos.gr, lavaron.com.gr) also 403. | **M (unread)** |
| Antiochian Online Liturgical Guide (OLG@antiochian.org) | P | No public page found (antiochian.org/liturgicday exposes only service-text PDFs). Needs email. | **M** |
| Getcha *Typikon Decoded*, Denver Violakis EN, Bogdanos | P | Paywalled, not read. | **M** |

## 2. Resolved / updated findings

| Question | Answer | Status | Basis |
|---|---|---|---|
| Rule: Sunday Liturgy prokeimenon when a saint's Epistle is read | Saint's prokeimenon replaces the Sunday one (not combined) | **I** for Antiochian (ANCA 4 dates, DCS 2, from #21), now **corroborated by Greek usage** (S, E-level) | Greek Apostolos guide p.2 list + per-date entries; Typikon Ch I §VII p.37 for owner |
| Same, prokeimenon text | Saint's own prokeimenon from Menaion/Apostle book | **E (S)** | Greek guide entries |
| Rule written in Antiochian Typikon or Bp Basil | No | **M** | Rechecked |
| Rule written in Violakis | Unknown (unread) | **M** | Fetch blocked |
| Alleluia verse set when saint's Epistle read | Sunday-tone alleluia kept (prokeimenon alone is the saint's) | **E (S)** one note; **I** Antiochian (DCS agrees, ANCA silent) | Greek guide p.57 (23-10); DCS keys from #21 |
| Alleluia when Epistle is a feast's and Gospel the feast's (14-9, 21-11 ...) | Feast's own, per DCS key `psLI.mMM.dDD.alleluia` | **I** | DCS (#21) |
| Russian/Ruthenian divergence | Two prokeimena/alleluias combined, Sunday first | **E (R)** | Andreev; MCI |

Rule shape for design (matches #21 recommendation): `prokeimenon.owner = epistle.owner`; `alleluia.owner = epistle.owner` for feast-takes-both cases (Epistle+Gospel of feast), else Sunday tone (saint-Epistle-only case). Tag the alleluia branch I (Antiochian), with the Greek note as supporting evidence.

## 3. Cautions

- Greek guide is a priest's compilation for readers, not an edition; its dates are Old/New Calendar neutral lists. Compare Typikon: Typikon names "great saint"; Greek guide names "officially celebrated" saints and lists them by date. Date lists not diffed against Typikon Menaion here.
- Its alleluia wording is a single parenthetical; no printed alleluia verses anywhere in it. Treat as supporting, not conclusive.
- Antiochian Typikon is a translation of Arman's Arabic typikon, itself checked against Violakis (per #11), so silence in Typikon does not prove Violakis silence.

## 4. New gaps

1. Read Violakis scan (browser download, CC BY-NC-ND per #11) at the Sunday Liturgy / "Kyriake" and Apostle-reading sections; confirm prokeimenon+alleluia rule in Greek. Needs manual download (host 403 to scripts).
2. Email OLG@antiochian.org with the two questions (Liturgy prokeimenon rule; alleluia verse set). Unanswerable from public web.
3. Diff the Greek guide's "saint's Apostle on Sunday" date list (p.2, p.46, p.95 of the PDF) against Typikon Menaion Epistle entries for Sundays, find UK/saint divergences. Not done.
4. Antiochian alleluia verse texts: no source prints them (Typikon, charts, ANCA). Obtain from Antiochian Apostolos/Liturgical Gospel appendix or DCS keys.
5. Triodion/Pentecostarion proper prokeimenon/alleluia (replace vs combine) still unchecked; MCI says "replace or combine" (R).
6. Whether UK parishes combine two prokeimena (Slavic habit) unresolved.
