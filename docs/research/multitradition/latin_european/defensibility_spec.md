# Latin-European (Lilly, Christian Astrology 1647) defensibility spec

Status: first delineation pack encoded (research_only); governs what a Latin-European reading may claim
Updated: 2026-08-03

The adversary for this section is a practicing horary/traditional astrologer who knows *Christian
Astrology* page by page. Sources of authority: the 1647 first edition, pinned and hashed in
`sources/access_manifest.json`; rules in `lilly_ca_rule_manifest.json`.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Essential dignity scoring (5/4/3/2/1; −5/−4/−5), incl. mutual-reception clauses | CA 1647 p. 115 table, page-photograph verified | `implemented` (engine computes the ladder; the mutual-reception scoring clauses and detriment/fall/peregrine negatives now source-pinned) |
| 2 | Accidental fortitude/debility scoring, all 33 rows | CA 1647 p. 115 table | `implemented` (engine computes accidental dignities; full 1647 point set now encoded for verification, incl. the 8th/6th = 2 reading) |
| 3 | Regiomontanus house cusps | Lilly's practice throughout CA | `implemented` |
| 4 | Aspects with per-planet orbs and moieties; application/separation; partill/platick | CA 1647 pp. 105-110 | `implemented` (engine computes aspects; Lilly's moiety doctrine encoded as rules lilly.ca1.orb_table, .separation_and_moieties for conformance checking) |
| 5 | Reception (types, ranking, mutual-reception effect) | CA 1647 p. 112 | `implemented` (engine computes sign-based receptions; effect doctrine encoded as lilly.ca1.reception) |
| 6 | Void of course with Lilly's exception signs | CA 1647 pp. 112, 122 | `implemented` (encoded lilly.ca1.void_of_course; degree-level application check is part of the engine's aspect machinery) |
| 7 | Planet natures with well/ill-dignified delineation fork | CA 1647 Book 1 chs. VIII-XIV | `implemented` (seven nature rules encoded and keyed to the dignity state the engine already computes) |
| 8 | Solar conditions (combustion, under-beams, cazimi), hayz, besieging, peregrine | CA 1647 pp. 112-114 | `implemented` (thresholds encoded; engine computes Sun-distance and sect facts) |
| 9 | Ptolemaic terms table digits (p. 104) for degree-level term dignity in Lilly mode | CA 1647 p. 104; planet chapters | `source_gated` (OCR-degraded in both witnesses; must be keyed from page photographs — a Lilly-mode scorer must NOT substitute the Egyptian bounds, see conflicts on lilly.ca1.terms_source_ptolemaic) |
| 10 | Considerations before judgment; perfection of questions | CA 1647 pp. 121-126 | `implemented` as domain-`other` research rules with horary scope notes (they gate horary judgment, not natal delineation) |
| 11 | CA Book 3 nativity apparatus (temperament collection, directions, worked nativity) | CA 1647 Book 3 | `source_gated` (Book 3 not yet mined in this pass; witnesses are pinned and legible, so this is queued extraction work under the same witnesses, not an access blocker) |
| 12 | Length-of-life judgment (Hyleg/Alcocoden), death timing | CA 1647 Book 3 | `refused` (see refusal list) |

## Judgment hierarchy

Lilly's own order of operations, as his worked figures execute it (CA pp. 135-146, 177-181):

1. Fitness to judge (horary only): considerations before judgment — radicality, degree gates, Moon
   condition. Natal readings skip this gate but must not silently import it.
2. Identify significators: ascendant/house rulership first; the Moon as co-significator.
3. Essential dignity of the significators (p. 104 table; scored per p. 115).
4. Accidental condition: house placement, motion, solar condition, aspects to benefics/malefics,
   fixed stars (Regulus/Spica/Algol) — scored per p. 115, debilities subtracted from fortitudes.
5. Aspect/reception machinery between significators: application, separation, prohibition,
   refranation, translation, collection, frustration, reception — in Lilly this machinery IS the
   judgment engine; dignity scores weight it, never replace it.
6. Delineation keyed to the dignity state (well vs ill dignified planet-nature forks).

A composer that flattens 3-5 into parallel bullets has failed the standard; the scores exist to
serve step 5.

## Worked-example inventory

- **Book 2 riches figure, CA pp. 177-186** — Lilly's own fortitude/debility scoring of every planet
  (Jupiter 20, Venus net 18, Mercury net 13, Moon net 5; collected table pp. 180-181). **Encoded**
  as five vectors; his arithmetic reproduces exactly from the encoded p. 115 table.
- **Book 1 first figure, CA pp. 135-146** — the demonstration figure with per-planet fortitudes
  referenced at p. 145. Legible in the pinned witnesses; not yet encoded.
- **Ship-at-sea judgments, CA pp. 157-166** — full horary judgments with stated reasoning; legible;
  not yet encoded.
- **Book 3 worked nativity** — present in CA Book 3; not yet mined (checklist row 11).

## Refusal list

- **No death-timing or length-of-life output.** CA Book 3's Hyleg/Alcocoden apparatus and every
  lifespan computation are deliberately unextracted; any rule that would emit one is refused with
  reason "death-timing/lifespan claim" (output_policy: refused). This repository-wide policy
  outranks the source.
- **No criminal or moralizing fate-claims about a native.** Lilly's thief-finding and
  "Highway-Theefe" delineations are quoted where they sit inside doctrine passages but must never
  be emitted as claims about a customer (customer_prediction: false everywhere).
- **No horary verdicts dressed as natal readings.** Considerations before judgment and the
  perfection modes are horary gates (domain `other` with scope notes); a natal reading may cite the
  shared machinery (aspects, reception) but not the question-gates.
- **No medical treatment claims** from the planet-member tables (CA pp. 119-120); anatomical
  correspondences may be described historically, never as diagnosis.
- **No degree-level term dignities in Lilly mode until the p. 104 Ptolemaic digits are keyed** —
  emitting Egyptian-bounds terms under Lilly's name would be a source misstatement (checklist row 9).

## Conventions requiring disclosure

- **Orb column choice.** Lilly prints two orb columns and says he uses either "without error";
  Jupiter's own chapter gives 9° against the table's 12°. Any consumer must disclose which column it
  scores with (`configured_method`), and the encoded rule carries both.
- **Translation-of-light form.** Lilly states it twice — without (p. 111) and with (p. 126) the
  reception requirement. The chosen form must be disclosed.
- **Combustion orb.** The stated rule is 8°30′; Lilly's personal opinion (moiety of the planet's own
  orb, "I know many are against this opinion") is recorded; the 8°30′ reading is the default.
- **8th/6th-house debility = 2 points** per the 1647 page photograph; later tabulations print 4.
  The witness reading is kept and the variance disclosed.
- **Quotation restorations.** Long-s normalized to 's'; OCR-garbled planet/sign sigils restored in
  square brackets from context; all residual numeric doubts recorded inside the affected rule.
- **House system.** Lilly works in Regiomontanus; the engine's Latin-European track already
  computes Regiomontanus cusps and must not silently substitute another system.

## Current implementation gap

`build_latin_european` computes the dignity scores, cusps and accidental dignities but the composer
does not yet cite this pack; the pack is `research_only` pending independent specialist review of
the renderings (early-modern English is low-risk, but the review gate for rule promotion holds).
The two `source_gated` rows (Ptolemaic term digits; CA Book 3 nativity apparatus) name the exact
follow-up extractions, both possible under the already-pinned witnesses. Nothing in this spec is
blocked on access: the 1647 text is pinned, hashed and legible, and the tables are page-photograph
verified.
