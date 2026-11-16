# Recognition bake-off: review sheet (PROTOTYPE, throwaway)

Ticket: "Recognition bake-off: templates vs vision LLM" (cmbryan/yocal#80). Branch `proto/recognition-bakeoff`.

## What was run

- **Sample:** 2 neume lines from each of 9 books. `clean` tier = flatbed scans (~300 dpi). `photo` tier = FETCHED spreads at 1536×1024 for two pages (≈100 dpi a page). Definitions: `samples.json`. Line bands were cropped by hand, the same for both arms; segmentation is not under test.
- **CV arm (`cv_arm.py`):** connected components → 1-NN against components from 1905 Anastasimatarion p.3, labelled once → geometric assembly. Templates come from **one typeface only**. Adaptive threshold for photos. Low-confidence threshold 0.3.
  - ⚠ `C1905` is the CV training page (in-sample), so don't count it for CV.
- **LLM arm (`llm_arm.py`, `llm/transcripts.txt`):** Claude, in this session, read each line crop and wrote Glyph Groups. No API call; the cost below is estimated. Low-confidence threshold 0.5.
- Both arms go through the same tables and exporter (`vocab.py`), so differences are recognition plus assembly only.
- Outputs: `out/cv/<book>.byzx`, `out/llm/<book>.byzx`. Originals: `crops/<book>-0.png`, `crops/<book>-1.png` (local only, gitignored). Regenerate with `python crops.py`, `python llm_arm.py`, `python cv_arm.py` (use `../../.venv/bin/python`).
- Flags appear as annotations `? low_confidence|ambiguous_attachment|unmapped_combo`. Lyrics are not produced. A lineBreak marks the line boundary.
- The exporter's minimal file is schema-derived and has not been tested in Neanes. If it won't open, note the error; that settles the "export template" fog item.

## How to tally

For each book and arm, open the `.byzx` in Neanes next to the two crops and count, per neume group:

- **wrong**: quantity neume or any mark (time/gorgon/qualitative/fthora/martyria) differs;
- **missing**: a group in the original has no group in the output;
- **extra**: an output group with no group in the original;
- **flag hit**: of the wrong groups, how many carry a `?` (a flag that points you to the error).

Error rate = (wrong + missing + extra) / groups in original.

| book | tier | groups in original | CV wrong | CV miss | CV extra | CV flag hit | LLM wrong | LLM miss | LLM extra | LLM flag hit |
|---|---|---|---|---|---|---|---|---|---|---|
| C1905 | clean (CV in-sample) | | | | | | | | | |
| C1825 | clean | | | | | | | | | |
| C1845 | clean | | | | | | | | | |
| C1850 | clean | | | | | | | | | |
| F1820 | photo | | | | | | | | | |
| F1824 | photo | | | | | | | | | |
| F1835 | photo | | | | | | | | | |
| F1837 | photo | | | | | | | | | |
| F1841 | photo | | | | | | | | | |

## Groups and flags as produced (machine count)

| book | CV groups | CV flagged | LLM groups | LLM flagged |
|---|---|---|---|---|
| C1905 | 31 | 5 | 33 | 7 |
| C1825 | 32 | 13 | 37 | 5 |
| C1845 | 31 | 24 | 35 | 13 |
| C1850 | 28 | 18 | 40 | 10 |
| F1820 | 18 | 18 | 30 | 7 |
| F1824 | 30 | 24 | 33 | 12 |
| F1835 | 28 | 23 | 32 | 16 |
| F1837 | 32 | 20 | 37 | 9 |
| F1841 | 20 | 17 | 45 | 8 |

## Cost / effort notes (agent's estimate; check)

- **CV:** one hand-labelling pass for each typeface (≈30–60 min: cluster montage, then label). It also needs a threshold and a binarisation tuned to each tier. On photos, components merge or break, and whole groups are lost (F1820, F1841 output far fewer groups than the LLM). Runtime and money cost are negligible.
- **LLM:** no per-typeface setup. One line crop is ≈1–2k input tokens plus ≈0.5k output; a page is ~10 lines. API price and latency aren't measured; a follow-up would measure them with a key.
- **Observed while transcribing (LLM arm):** small marks at photo resolution (klasma vs. apostrophos above, gorgon dots, apli vs. dot) were often guesses; those are the `?` flags. Root signs printed at lyric height (C1850) were read, but CV never sees them because they fall outside the neume band.
- **F1820** uses an elongated older type: neither arm is reliable there.
