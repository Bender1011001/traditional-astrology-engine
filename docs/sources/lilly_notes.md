# William Lilly, *Christian Astrology* (London 1647, first edition)

Wellcome facsimile, 894 PDF pages. **Lilly wrote in English, so this scan IS the original** — there is no translation layer, and the earlier `translation_inspected` status on his rules was a category error.

Pagination: PDF page ≈ printed page + 33 (verified: pdf 145 → printed 112; pdf 148 → printed 115).

---

## Reception — printed p. 112

> *Reception is when two Planets that are significators in any Question or matter, are in each others dignity … here is reception of these two Planets by Houses; and certainly **this is the strongest and best of all receptions**. It may be by triplicity, terme or face, or any essentiall dignity … The use of this is much; for many times when as the effecting of a matter is denyed …*

Three things the text states plainly:

1. Reception is mutual presence **in each other's dignity** — not one-way.
2. Reception **by domicile is the strongest**; but it may be by *any* essential dignity, including triplicity, term, or face.
3. Its function is to **effect a matter otherwise denied** — that is the reason Lilly gives for caring about it.

---

## ⚠ The Fortitudes table — printed p. 115, and a gap it exposes

> *A ready Table whereby to examine the Fortitudes and Debilities of the Planets.*

| Lilly | value | ours (`DignityCalculator`) |
|---|---|---|
| own house **or mutuall reception by house** | 5 | `DOMICILE = 5` |
| exaltation **or reception by exaltation** | 4 | `EXALTATION = 4` |
| own Triplicity | 3 | `TRIPLICITY = 3` |
| own Terme | 2 | `TERM = 2` |
| Decanate or Face | 1 | `FACE = 1` |
| Detriment | −5 | `DETRIMENT = -5` |
| Fall | −4 | `FALL = -4` |
| Peregrine | −5 | `PEREGRINE = -5` |

**All eight point values match exactly.** The table is Lilly's.

**But the two reception clauses are not implemented.** Lilly's own rubric awards a planet in *mutual reception by house* the **same 5 points** as a planet in its own house, and *reception by exaltation* the **same 4** as exaltation. `grep -n reception src/engine/dignities.py` returns nothing but a comment: reception is computed elsewhere (`reception.py`) and never reaches the dignity score.

**Unlike the Dorotheus "share", this gap has an explicit weight in the source** — 5 and 4, printed in the table. So it is implementable without guessing. It is nevertheless **not patched here**, because awarding 5 points for mutual reception changes essential-dignity totals on any chart containing one, and the almuten is decided by those totals — so it would silently move the chart ruler in some nativities. That is a decision to take deliberately, not a side effect of a reading session.

Also worth noting for the accidental-fortitude table on the same page (angularity, direct motion, swift motion, orientality for Saturn/Jupiter/Mars and occidentality for Mercury/Venus): not audited against our implementation in this pass.

---

## Status

Both `lilly_reception` and `lilly_planetary_conditions` move from `translation_inspected` to `facsimile_inspected_1647_first_edition` — the correct status for an author who wrote in English.

---

## The accidental fortitudes table read (printed p. 115) — ours matches, with one real gap (2026-08-11)

Read from the facsimile image, not the OCR. **All seven house tiers match `calculate_accidental_dignity` exactly:**

| position | Lilly | ours |
|---|---|---|
| Mid-heaven or Ascendant | 5 | +5 |
| 7th, 4th, 11th | 4 | +4 |
| 2nd and 5th | 3 | +3 |
| 9th | 2 | +2 |
| **3rd** | **1** | **+1** |
| **8th and 6th** | **2** (debility) | **−2** |
| 12th | 5 (debility) | −5 |

### A near-miss worth recording

The OCR of this page rendered the 3rd house as **2** and the 8th/6th as **4**, which would have made two discrepancies against a table our code cites to "Lilly, CA p. 115". **Both were OCR artifacts.** The printed page gives 1 and 2, exactly as we have them.

This is the fourth time in one session that rendering the page instead of trusting extracted text prevented a false bug report — after the Firmicus midpoint miscalculation, the Ptolemy "missing Jupiter line", and the three Picatrix truncation retractions. **Extracted text is a lead, never a verdict.**

### The real gap: Lilly's fixed-star fortitudes

Verified absent from our accidental scoring (`'Regulus' in block or 'Cor Leonis' in block or 'Spica' in block` → False):

| Lilly | value |
|---|---|
| In conjunction with **Cor Leonis** (Regulus), 24° Leo | **+6** — his single largest accidental fortitude |
| In conjunction with **Spica**, 18° Libra | **+5** |
| In conjunction with **Caput Algol**, 20° Taurus, or within five degrees | **−5** |
| Partill conjunction with the Dragon's Head ☊ | +4 |
| Partill conjunction with the Dragon's Tail ☋ | −4 |

Regulus at +6 outranks every other item in the table, including the Mid-heaven at 5. A planet on Regulus is, for Lilly, more accidentally fortified than a planet on the MC. We score neither star.

This is implementable without judgment — the degrees and values are printed — but it is a scoring change and belongs with the other pending decisions, not a silent addition. Note it interacts with the existing project caution about fixed-star output carrying modern popular boilerplate: these five are Lilly's own, with his own numbers.

---

## 2026-08-20 — Book III read end to end, all ~40 nativity chapters, plus rectification and directions

Session goal: read every chapter of *Christian Astrology* Book III (nativities) that hadn't already been read, in parallel, then decide what changes in the system. Full source-registry entries for each chapter are in `src/database/data/doctrine_sources.json` under `verified_rules`, keys prefixed `lilly_` (14 new entries added this session, alongside the pre-existing `lilly_hyleg_alcocoden_and_years`, `lilly_reception`, `lilly_planetary_conditions`, `lilly_degree_quality_tables`). This note is the human-readable summary; the JSON is the source of truth for citations.

### What got wired into the engine

Two significator-selection cascades, chosen because they were the two techniques that scored real, checkable hits during live testing this session (against a real chart and real photographs) rather than because they were the easiest to code:

- **`lilly_manners_significator_cascade`** (CVII–CVIII) — five ordered fallback rules across all seven planets select the significator of manners; a two-state (well-/ill-dignified) character table then reads that specific planet. Implemented in `src/services/reading_evidence.py` (category `manners_significator`), rendered in `src/services/reading_composer.py` (`_manners_significator_paragraphs`). Lilly gives no Sun/Moon rows in CVIII — if one of the lights wins the cascade, the emitter says so explicitly rather than inventing an entry.
- **`lilly_profession_significator_cascade`** (CXLVIII–CXLIX) — the significator of profession is chosen from exactly three candidates, Mars/Venus/Mercury, through five ordered rules; a planet in strong aspect to a second candidate can "relinquish its claim" and the trade follows both. Implemented the same way (category `profession_significator`).

Both were tested against four real charts (the project's own natal chart, plus Kovalev, Nixon, and Jobs test fixtures) and correctly exercised different rule branches on each — rule 1 on some, rule 2/3/5 on others — with no crashes and no silent empty results. `test_reading_composer.py` and `test_reading_contract.py` pass unchanged.

Both use **Lilly's own orbs** (`_LILLY_ORB` in `reading_evidence.py`: Sun 15°, Moon 12°, Mercury/Venus/Mars 7°, Jupiter/Saturn 9°), not the engine's general Ptolemaic `MOIETIES` table used elsewhere — the two traditions disagree on orb size and mixing them would misattribute the result.

### The other concrete fix: directions now default to Naibod

Lilly names three competing arc-to-time keys (Ptolemy, Maginus, Naibod) and states his own preference explicitly: Naibod "when he has sufficient time to do a nativity properly," in his own words "the most exactest measure that hitherto hath been found out." The engine's `PrimaryDirectionsEngine` already had Naibod implemented (`0.9856°/year`) but every function defaulted to Ptolemy's simpler `1°/year`, and the JSON output labeled every direction "Ptolemy (1 degree = 1 year)" regardless of which key actually ran. Fixed in `src/engine/primary_directions.py` (defaults changed) and `src/engine/forensic_engine.py` (label corrected, key requested explicitly at the call site). **One deliberate exception**: `calculate_circumambulations` stayed on Ptolemy's key — that function implements Ptolemy's own bound-circumambulation technique (Tetrabiblos IV.10), a different author's different technique that happens to share this module; Lilly's stated preference doesn't apply to it. Caught by the test suite (`test_circumambulation_transitions_are_solved_between_year_samples` failed on the first blanket change, which is exactly why it's a good test).

### What was deliberately NOT wired in, and why

- **Physiognomy** (stature, form, grossness — CX/CXI/CXII). Tested against two real photographs of one native this session: two hits, two misses, one confound. Recorded in the doctrine registry as unvalidated; not implemented as delineation code. If it's ever added, it should ship with the same confidence caveat given to the customer that was given here.
- **Violent death** (CLVI) and **falling-sickness/madness** (the 6th-house chapter). Both are severe claims from a source with no modern validation. This matches the project's own existing exclusion of length-of-life/manner-of-death material (see `scope.excluded` and `scope.included_historical_techniques` in `reading_evidence.evidence_packet` — length-of-life techniques are explicitly named as *included for research*, not for customer delineation). Recorded in the registry with an explicit `publication_limit` reinforcing that exclusion; not implemented as customer-facing code.
- **Hyleg/Alcochodon years.** Already covered by the pre-existing `lilly_hyleg_alcocoden_and_years` entry. Confirmed again this session by actually running the full selection procedure end to end (syzygy-ruler test, essential-dignity tally) rather than assuming the fallback — it resolves cleanly on a real chart, but Lilly's own stated doubt ("I rest not satisfied... whom most properly to call the killing planet") and the project's own 11-of-20 failure rate on this technique family stand as the reasons it stays out of customer reports regardless of how cleanly any single chart resolves.
- **Everything else read this session** (general fortune, riches, brethren, parents, marriage/wife-description, children, journeys, religion, dreams, honours, friends, enemies, captivity, revolutions, rectification) — extracted and cited in the doctrine registry, not yet wired into `reading_evidence.py`. These are real, well-sourced techniques and reasonable next candidates; they weren't added this pass because doing seven more cascades in one sitting without the same live-chart testing given to manners and profession would be shipping unverified code, which is the mistake this whole session was trying to catch elsewhere.

### The worked-nativity finding worth remembering on its own

Lilly's own demonstration nativity (pp. 742–764) shows him reverse-engineering sibling-count testimonies to match a known biographical fact after his own stated method predicts the opposite, without flagging the fit as post-hoc — and one of his own predictions (no throat blemish) is corrected by the book's own marginal annotation, which says the native had one. The tradition's founder retrofits known outcomes onto ambiguous rules in his own flagship example. That's a standing caution for reading any of his aphorisms, not just the ones implemented here.
