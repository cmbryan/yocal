# Brief: index Pergamos music books (subagent instructions)

Goal: make every *parish-usable* setting in these books findable by hymn id, for transcription into yocal services (Vespers, Orthros, Divine Liturgy). Skip long papadic/kalophonic pieces (kratemata, kalophonic heirmoi, mathemata, argon cherubika/koinonika > a few pages): list them only as one-line "papadic" entries without mapping.

Inputs
- PDFs: /home/chris/Documents/yocal/FETCHED/<id> *.pdf. Each PDF page = one scan image, normally a TWO-PAGE SPREAD (left = even printed page, right = odd), sometimes single pages. Not in git; CC BY-NC-ND.
- Worked example (copy its format exactly): yocal_rules/data/sources/pergamos/168182.yaml
- Hymn-id scheme: yocal_rules/hymns.py (read the docstring/regexes) and existing mappings in yocal_rules/data/sources/byzantine_pd.yaml + byzantine_pd.md. Ids: oct/t{1-8}/sun/{apolytikion,kontakion,hypakoe,prokeimenon,canon,lauds1..}, eothinon/NN/{doxastikon,exaposteilarion,theotokion}, men/MM-DD/{apolytikion,kontakion,doxastikon,...}, mov/<days from Pascha>/..., lit/... (liturgy fixed parts). Tones 1,2,3,4, pl1=5, pl2=6, grave=7, pl4=8.

Method (per book)
1. Find the contents list (Πίναξ / Περιεχόμενα), usually the last or first few images. Render cheaply to locate: `pdftoppm -r 40 -gray -f N -l N -png`; then extract full res: `pdfimages -f N -l N -j PDF out` and crop to one page with PIL before reading. Scratch files ONLY under /tmp/claude-1000/-home-chris-Documents-yocal/f5eb3615-b42f-4527-9fd0-210e22c51395/scratchpad/<your-group>/.
2. Transcribe entries: printed page, title (polytonic as printed, abbreviations expanded only when certain), composer, tone, feast date/moveable. If no contents list, index from running headers / section titles by sampling pages (state that in `summary`).
3. Calibrate printed page -> PDF image: read page numbers on 2+ widely separated images; record `spread: {add: N}` (image = printed // 2 + N) or `single: {add: N}` (image = printed + N); piecewise list if it changes, with what you checked.
4. Add `hymn:` to entries that clearly match an id (use {t}-free concrete ids; for a section covering all 8 tones use e.g. `oct/t{t}/sun/apolytikion` and `tones: [..]`). Add `status: toc` (from contents only) or `page` (you looked). Flag uncertain readings with `note: "verify ..."`. Never guess a reading; mark `[?]`.
5. Especially look for, and report explicitly even if absent: litany responses (Κύριε ἐλέησον, Παράσχου Κύριε, Σοὶ Κύριε, Ἀμήν, Καὶ τῷ πνεύματί σου), Liturgy fixed parts (antiphons, Ὅσοι εἰς Χριστόν, Ἄξιον ἐστίν, Εἷς Ἅγιος, Εὐλογητὸς ὁ ἐρχόμενος, Εἴδομεν τὸ φῶς), resurrectional apolytikia/kontakia, prokeimena.

Output
- One file per book: yocal_rules/data/sources/pergamos/<id>.yaml (key: PG<last 3 digits>).
- Do not edit byzantine_pd.yaml/.md or any other file; do not commit.
- Final reply (short): per book — what it is, contents images, calibration, count of entries, count mapped to hymn ids, litany-responses found? (yes/no + where), anything doubtful.
