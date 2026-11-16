# Neanes `.byzx` format and symbol inventory (issue #78)

Source: `github.com/neanes/neanes` @ `d7f3096` (2026-11-14). Paths below relative to that repo.

## Container
- `.byzx` = plain UTF-8 JSON, pretty-printed (`JSON.stringify(score, null, 2)`). `electron/main/files/scoreFiles.ts:14`
- `.byz` = ZIP (DEFLATE) holding one `<name>.byzx` (compact JSON). Loader takes first entry matching `/\.byzx$/`. `scoreFiles.ts:9-28`
- Schema = TS classes in `src/models/save/v1/*.ts`; serializer/loader `src/services/SaveService.ts`.

## Versioning
- Root `version` (currently `"1.1"`, `save/v1/Score.ts`) + `appVersion` (informational).
- Loader: missing/non-string `version` -> error; `startsWith('1.')` -> v1 loader; anything else -> "Unrecognized file version". `SaveService.ts:898-906`. Emit `"1.1"`.
- Loader is field-by-field copy into in-memory model; legacy fields migrated (e.g. `measureBar` -> `measureBarRight`, pre-paragraph-style font fields). Unknown keys are not copied, so **custom keys are dropped on next save** (inference from explicit copy code, `LoadNote_v1` etc.).
- Serializer omits falsy/default fields (`x || undefined`), so files are sparse. Enum strings are the stable contract; enum member names != values in a few cases (below).

## Root schema (`Score`)
```
{ version, appVersion, documentProperties?{title,author},
  pageSetup{...},            // REQUIRED: LoadPageSetup_v1 reads p.pageHeight etc. unguarded
  paragraphStyles?[], headers?{default,chapterOpening,even,odd,firstPage},
  footers?{...}, staff{elements: ScoreElement[], lyrics{locked?,text}},
  footnotes?[{id, marker?, staff}] }
```
`pageSetup` units = px @96/in (`Unit.fromInch`). Defaults: Letter, 816x1056, margins 96, header/footer margin 48.

## Elements (`staff.elements[]`, discriminated by `elementType`)
`Note | Martyria | Empty | TextBox | RichTextBox | DropCap | ModeKey | Tempo | ImageBox | Annotation | AlternateLine` (`save/v1/Element.ts`). Common: `id?`, `lineBreak?`, `pageBreak?`, `lineBreakType?` (`Center` only written).

### Note (one neume group + one syllable)
| field | enum | role |
|---|---|---|
| `quantitativeNeume` (required) | `QuantitativeNeume` | interval/quantity neume, incl. rests |
| `timeNeume` | `TimeNeume` | klasma, apli/dipli/..., koronis |
| `gorgonNeume`, `secondaryGorgonNeume` | `GorgonNeume` | gorgon family, argon |
| `vocalExpressionNeume` | `VocalExpressionNeume` | qualitative marks |
| `fthora`, `secondaryFthora`, `tertiaryFthora` | `Fthora` | fthorai/chroai (Zygos/Kliton/Spathi) |
| `chromaticFthoraNote` (+secondary/tertiary) | `ScaleNote` | note a chromatic fthora applies to |
| `accidental` (+secondary/tertiary) | `Accidental` | diesis/yfesis |
| `measureBarLeft/Right` | `MeasureBar` | |
| `measureNumber` | `MeasureNumber` | |
| `ison` | `Ison` | ison indicator |
| `tie` | `Tie` | yfen |
| `noteIndicator`, `vareia`, `koronis`, `stavros` | bool | |
| `lyrics`, `isMelisma`, `isMelismaStart`, `isHyphen`, `acceptsLyrics` | str/bool/`Default|Yes|No|MelismaOnly` | text underlay |
| `lyricsColor` | CSS colour | colours syllable only |
| `annotations[]` | `{elementType:"Annotation",x,y,text}` | free text near neume |
| `footnoteId` | string -> `footnotes[].id` | |
| `*OffsetX/Y` | number | per-mark nudges |

Secondary/tertiary positions are encoded in the enum value suffix too (`Gorgon...Secondary`, `Fthora..._TopSecondary`, `Sharp_2_LeftTertiary`), not only in the field name.

### Martyria
`note: Note`, `rootSign: RootSign`, `scale: Scale`, `auto?` (Neanes computes note/root sign from context when true), `rootSignOverride?`, `fthora?`, `chromaticFthoraNote?`, `tempo/tempoLeft/tempoRight?: TempoSign`, `quantitativeNeume?` (martyria-with-neume), `measureBarLeft/Right?`, `alignRight?`, `bpm?`.

### ModeKey (mode signature)
`mode: 1..8`, `scale: Scale`, `scaleNote: ScaleNote` (base), `martyria: ModeSign`, `note?`, `note2?: ModeSign`, `fthoraAboveNote?`, `fthoraAboveNote2?`, `fthoraAboveQuantitativeNeumeRight?: Fthora`, `quantitativeNeumeRight?: QuantitativeNeume`, `quantitativeNeumeAboveNote(2)?: ModeSign`, `fthora?`, `tempo?`, `bpm`, `ambitus*`, `templateId?` (ties to presets in `src/models/ModeKeys.ts`), styling (`color`, `fontSize`, `height`...).

### Tempo
`neume: TempoSign`, `bpm`.

### Rests
No separate element. Rests are `QuantitativeNeume.VareiaDotted` (1 beat), `VareiaDotted2/3/4` (2-4 beats) (`NeumeKeyboardDocumentation.ts:208`). `Breath` and `Cross` are also quantitative-slot values. `vareia: true` on a Note = vareia before neume.

## Symbol inventory (enum value strings; `src/models/save/v1/Neumes.ts`)
**QuantitativeNeume**: Ison; Oligon, OligonPlusKentimaBelow, OligonPlusKentimaAbove, OligonPlusHypsiliRight, OligonPlusHypsiliLeft, OligonPlusHypsiliPlusKentimaHorizontal, OligonPlusHypsiliPlusKentimaVertical, OligonPlusDoubleHypsili, OligonKentimataDoubleYpsili, OligonKentimaDoubleYpsiliRight, OligonKentimaDoubleYpsiliLeft, OligonTripleYpsili, OligonKentimataTripleYpsili, OligonKentimaTripleYpsili; PetastiWithIson, Petasti, PetastiPlusOligon, PetastiPlusKentimaAbove, PetastiPlusHypsiliRight, PetastiPlusHypsiliLeft, PetastiPlusHypsiliPlusKentimaHorizontal, PetastiPlusHypsiliPlusKentimaVertical, PetastiPlusDoubleHypsili, PetastiKentimataDoubleYpsili, PetastiKentimaDoubleYpsiliRight, PetastiKentimaDoubleYpsiliLeft, PetastiTripleYpsili, PetastiKentimataTripleYpsili, PetastiKentimaTripleYpsili; Apostrophos, Elaphron, ElaphronPlusApostrophos, Hamili, HamiliPlusApostrophos, HamiliPlusElaphron, HamiliPlusElaphronPlusApostrophos, DoubleHamili, DoubleHamiliApostrofos, DoubleHamiliElafron, DoubleHamiliElafronApostrofos, TripleHamili; PetastiPlusApostrophos, PetastiPlusElaphron, PetastiPlusElaphronPlusApostrophos, PetastiHamili, PetastiHamiliApostrofos, PetastiHamiliElafron, PetastiHamiliElafronApostrofos, PetastiDoubleHamili, PetastiDoubleHamiliApostrofos; OligonPlusKentemata, KentemataPlusOligon, OligonPlusIsonPlusKentemata, OligonPlusApostrophosPlusKentemata, OligonPlusHyporoePlusKentemata, OligonPlusElaphronPlusKentemata, OligonPlusElaphronPlusApostrophosPlusKentemata, OligonPlusHamiliPlusKentemata; RunningElaphron, Hyporoe, PetastiPlusRunningElaphron, PetastiPlusHyporoe; OligonPlusIson, OligonPlusApostrophos, OligonPlusElaphron, OligonPlusHyporoe, OligonPlusElaphronPlusApostrophos, OligonPlusHamili; Kentima, OligonPlusKentima, Kentemata; DoubleApostrophos, OligonPlusRunningElaphronPlusKentemata, IsonPlusApostrophos, OligonKentimaMiddleKentimata, OligonPlusKentemataPlusHypsiliLeft, OligonPlusKentemataPlusHypsiliRight; VareiaDotted, VareiaDotted2, VareiaDotted3, VareiaDotted4, Cross, Breath.

**TimeNeume**: Klasma_Top, Klasma_Bottom, Hapli, Dipli, Tripli, Tetrapli, Koronis.

**GorgonNeume**: Gorgon_Top, Gorgon_Bottom, Digorgon, Trigorgon, GorgonDottedLeft, GorgonDottedRight, DigorgonDottedLeft1, DigorgonDottedLeft2, DigorgonDottedRight, TrigorgonDottedLeft1, TrigorgonDottedLeft2, TrigorgonDottedRight, GorgonSecondary, GorgonDottedLeftSecondary, GorgonDottedRightSecondary, DigorgonSecondary, DigorgonDottedLeft1Secondary, DigorgonDottedLeft2Secondary, DigorgonDottedRightSecondary, TrigorgonSecondary, TrigorgonDottedLeft1Secondary, TrigorgonDottedLeft2Secondary, TrigorgonDottedRightSecondary, Argon, Hemiolion, Diargon.

**VocalExpressionNeume** (qualitative): Vareia, HomalonConnecting, Homalon, Antikenoma, Psifiston, PsifistonSlanted, Heteron, HeteronConnecting, HeteronConnectingLong, Endofonon, Cross_Top.

**Fthora**: for each of DiatonicNiLow, DiatonicPa, DiatonicVou, DiatonicGa, DiatonicThi, DiatonicKe, DiatonicZo, DiatonicNiHigh, HardChromaticPa, HardChromaticThi, SoftChromaticPa, SoftChromaticThi, Enharmonic, Zygos, Kliton, Spathi: `X_Top`, `X_TopSecondary`, `X_TopTertiary`, `X_Bottom`, plus bare `X` (martyria/mode-key use). Plus GeneralSharp_/GeneralFlat_ {Top, TopSecondary, TopTertiary, Bottom}. Chroai = Zygos, Kliton, Spathi.

**Accidental**: Sharp_{2,4,6,8}_Left[Secondary|Tertiary], Flat_{2,4,6,8}_Right[Secondary|Tertiary].

**Note / ScaleNote** (same values): ZoLow NiLow PaLow VouLow GaLow ThiLow KeLow Zo Ni Pa Vou Ga Thi Ke ZoHigh NiHigh PaHigh VouHigh GaHigh ThiHigh KeHigh.

**RootSign** (martyria lower sign): Delta, Alpha, Legetos, Nana, Tilt, TiltLow, **Varys** (member `Zo`), **VarysLow** (member `ZoLow`), Squiggle, SquiggleLow, Zygos, ZygosLow, SoftChromaticSquiggle(Low), DeltaDotted(Low), AlphaDotted(Low), SoftChromaticPaRootSign(Low), NanaLow, DeltaLow, AlphaLow, LegetosLow.

**Scale**: Diatonic, SoftChromatic, HardChromatic, EnharmonicGa, EnharmonicZo, EnharmonicZoHigh, EnharmonicVou, EnharmonicVouHigh, Zygos, Spathi, SpathiGa, Kliton. (`save/v1/Scales.ts`)

**ModeSign** (values prefixed `ModeSign.`): Ni Pa Vou Ga Thi Ke Zo Ekhos Plagal First FirstCapital Second SecondCapital Third ThirdCapital Fourth FourthCapital Varys Alpha AlphaWithDeltaHat AlphaWithHypsili SoftChromatic2 SoftChromatic6 Nana VarysZo Delta DeltaWithDeltaHat DeltaWithHypsili NanaOld Legetos ElaphronPlusApostrophos Elaphron OligonPlusKentima OligonPlusHypsili.

**TempoSign**: VerySlow Slower Slow Medium Moderate Quick Quicker VeryQuick, each also `...Above`.

**Ison** (prefixed `Ison.`): Unison GaLow ThiLow KeLow Zo Ni Pa Vou Ga Thi Ke ZoHigh. **NoteIndicator** (prefixed `NoteIndicator.`): Ni..Zo (save field is bool `noteIndicator`). **Tie**: YfenAbove, YfenBelow. **MeasureBar**: MeasureBar{Right,Top,Double,ShortDouble,Theseos,ShortTheseos}[Above]. **MeasureNumber**: Two..Eight.

## Per-glyph uncertainty flag
No dedicated confidence/flag field. Options that survive load/save:
1. **`annotations[]`** on Note: visible text (e.g. `"?"`/`"OCR 0.42"`) at x/y offset; rendered on page -> best visual finder. Empty-text annotations are stripped on save.
2. **`footnoteId`** + `footnotes[]`: numbered marker + note text at page foot; enumerable.
3. **`lyricsColor`** (e.g. `#ff00ff`): colours syllable only; neume colours are document-wide (`pageSetup.*DefaultColor`), no per-element neume colour.
4. Custom JSON keys: NOT viable, dropped on first resave.
Recommendation: annotation `"?"` (+ optional lyricsColor) for review; strip before publishing.

## Minimal valid example
Loader needs `version` and `pageSetup` (unguarded reads); other sections defaulted. Safest pipeline: take a blank file saved by Neanes as template, replace `staff.elements`. Hand-written minimum:
```json
{
  "version": "1.1",
  "appVersion": "0.0.0",
  "pageSetup": {
    "pageSize": "Letter", "pageSizeUnit": "in",
    "pageWidth": 816, "pageHeight": 1056,
    "topMargin": 96, "bottomMargin": 96, "leftMargin": 96, "rightMargin": 96,
    "headerMargin": 48, "footerMargin": 48, "firstPageNumber": 1
  },
  "staff": {
    "lyrics": { "text": "" },
    "elements": [
      { "elementType": "ModeKey", "mode": 1, "scale": "Diatonic", "scaleNote": "Pa",
        "martyria": "ModeSign.Alpha", "note": "ModeSign.Pa", "bpm": 120,
        "alignment": "center", "color": "#000000", "fontSize": 16,
        "strokeWidth": 0, "height": 20, "heightAdjustment": 0 },
      { "elementType": "Martyria", "auto": true, "note": "Pa", "rootSign": "Alpha", "scale": "Diatonic" },
      { "elementType": "Note", "quantitativeNeume": "Ison", "lyrics": "A" },
      { "elementType": "Note", "quantitativeNeume": "Oligon", "timeNeume": "Klasma_Top", "lyrics": "men",
        "annotations": [ { "elementType": "Annotation", "x": 0, "y": -20, "text": "?" } ] },
      { "elementType": "Note", "quantitativeNeume": "Apostrophos", "gorgonNeume": "Gorgon_Top", "fthora": "DiatonicVou_Top" },
      { "elementType": "Note", "quantitativeNeume": "VareiaDotted" },
      { "elementType": "Empty" }
    ]
  }
}
```
Unverified by opening in Neanes; schema-derived. Validate with a round-trip (open, save, diff) before relying on it.
