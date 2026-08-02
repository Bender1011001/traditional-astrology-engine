# Islamicate / Persian defensibility spec

Status: governing spec for the Islamicate section  
Updated: 2026-08-02  
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

The adversary is a scholar of Arabic astrology. This tradition shares the Western
calculation core, so the failure mode is not arithmetic — it is presenting
Hellenistic technique under an Arabic label, or asserting doctrine from a
translation lineage that disagrees with the Arabic.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Sect and its planetary consequences | al-Biruni pack (validated) | `implemented` |
| 2 | Halb and hayyiz, with the one-way implication | al-Biruni pack, incl. the Mars case | `implemented` |
| 3 | Planetary and sign gender/sect classification | al-Biruni pack | `implemented` |
| 4 | Mercury's conditional classification | al-Biruni pack (explicitly conditional) | `implemented` (fails closed in 3 of 4 fixtures - 385-386 states no conflict priority) |
| 5 | Firdaria ordering, diurnal and nocturnal | al-Biruni pack (validated) | `implemented` |
| 6 | Equal-seventh subperiod structure | al-Biruni pack (validated) | `implemented` |
| 7 | Firdaria **durations and dates** | al-Qabisi *Introduction* Ch. II (direct extraction) — all 9 bodies incl. both nodes, summing to 75 years | `implemented` - all 9 periods and their running ages computed in `src/engine/multitradition/islamicate.py`; the 75-year total is asserted by self-check. Calendar DATES are still not emitted (ages only). |
| 8 | Lunar mansions (manazil) | pre-Islamic Arabian track, source-limited | `source_gated` |
| 9 | Lots beyond Fortune/Spirit in the Arabic tradition | al-Qabisi *Introduction* Ch. V, *jumal al-sihaam* (direct extraction) — ~50 lots across all 12 houses, several named-attributed (Hermes, Valens, al-Andarzaghar, Dorotheus) | `implemented` - `cast_lot()` plus `named_lots()`: Fortune, Spirit, Life, and the marriage/enemies lots whose formulas use only planets and the Ascendant, including the Hermes-vs-Valens attributed fork. House-cusp lots (Wealth, Death, Sultanate) are NAMED AS OMITTED, not approximated, since this section computes whole-sign places not cusps. |
| 10 | Tasyir / directions | al-Qabisi *Introduction* Ch. IV (direct extraction) — ascensional directions with the mean-solar-motion rate, plus a separate bound-based system (al-jarbakhtar) | `implemented` - `jarbakhtar()` runs the Ascendant's bound-directions by true oblique ascension for the birth latitude, at al-Qabisi's own 1deg=1yr / 5'=1mo / 1'=6d rate. The 59'08"/day revolution constant is implemented and verified 0.33 arcsec from modern mean solar motion. Directions of arbitrary significators to arbitrary promittors are still not run and are named as such. |
| 11 | Conjunctional/mundane doctrine | Abu Ma'shar Great Introduction | `source_gated` (al-Qabisi's own six-cycle conjunction doctrine and kingship-duration lots are now sourced from Ch. IV/V — see items 15-16 — but remain `refused` for any customer-facing mundane output by design, not merely gated) |
| 12 | Hyleg (prorogator) candidate-place algorithm | al-Qabisi *Introduction* Ch. IV (direct extraction) | `implemented` - `hyleg_candidates()` + `settle_hyleg()`, with the gender conditions AND al-Qabisi's final gate (a dignity lord of the degree must behold the place) both applied, using his own Ch. I sign-aspect table. Whole-sign aspect is a disclosed choice: he defines the ray as falling at the same degree and never states an orb. |
| 13 | Kadkhudah (alcocoden) selection, incl. a named Dorotheus priority-order fork | al-Qabisi *Introduction* Ch. IV (direct extraction) | `implemented` - `kadkhudah_for()` on the settled hyleg, with the aspect gate applied and non-beholding lords listed as skipped. Both the default order and the named Dorotheus fork are computed; neither is asserted over the other. |
| 14 | Annual (whole-sign) profection, with a fully-worked and independently-verified numeric example | al-Qabisi *Introduction* Ch. IV (direct extraction) | `implemented` - `profect()`; al-Qabisi's own Ch. IV worked example reproduces exactly, all five points plus the Mars year-lord. |
| 15 | Essential dignity tables (domicile, exaltation, triplicity, bounds, face) and al-Qabisi's own numerical 5/4/3/2/1 dignity-scoring table | al-Qabisi *Introduction* Ch. I (direct extraction) | `implemented` - `mustawli()` scores 5/4/3/2/1 over the five dignity lords; al-Qabisi's own Ch. I para 77 example reproduces exactly (Mars 6, Sun 7, Sun prevails, Jupiter 2 as bound lord). |
| 16 | Planetary condition doctrine beyond halb/hayyiz: reception, prevention, translation/collection of light, refranation, and a full planetary friendship/enmity table | al-Qabisi *Introduction* Ch. III (direct extraction) | `implemented` in part - `planetary_condition()` computes reception (qabul) and feral (wahshi) from position. Translation/collection of light, prevention, the frustration variants and radd are NOT decided: they need planetary speed, retrogradation and combustion state this section does not receive, and each is named rather than guessed. The friendship table is deliberately NOT symmetrised - the source states it asymmetrically and flattening it would destroy that. |

## Judgment hierarchy

1. Sect, established first — it conditions every subsequent malefic/benefic
   judgment.
2. Planetary condition including halb/hayyiz, respecting the one-way implication
   the pack encodes (hayyiz implies halb; halb does not imply hayyiz).
3. Dignity and reception on the shared classical core.
4. Firdaria ordering as a structural fact — durations are now sourced from
   al-Qabisi (item 7) but composer wiring is not yet built.
5. Where al-Qabisi's own length-of-life structure is invoked, it is strictly
   ordered: hyleg first (candidate-place algorithm), kadkhudah second
   (conditioned on the established hyleg), al-wali third — never computed in
   parallel or independently of one another. No lifespan number is asserted
   at any stage.
6. Author attribution on every doctrinal claim: al-Biruni, Abu Ma'shar, and
   al-Qabisi are not interchangeable. Within al-Qabisi's own text, further
   attribution is preserved rather than flattened — e.g. Dorotheus's named
   dissent on kadkhudah priority, Ptolemy's named "whole-sign exaltation"
   report, and Hermes/Valens/al-Andarzaghar's named lot variants are each
   kept as attributed forks, not merged into "al-Qabisi says."

## Worked-example inventory

| Source | Contains | Usable now |
|---|---|---|
| al-Biruni, *Kitab al-Tafhim* | instructional question/answer format; the Halle facing-text edition is inspected | limited — instructional, not worked charts |
| Abu Ma'shar, *Great Introduction* | Brill Arabic/English edition identified; Arabic TEI already downloaded | edition access gated for the English/apparatus; Arabic TEI itself is readable now (not yet extracted) |
| al-Qabisi, *Introduction* | direct Arabic extraction complete (Ch. I-V, 2026-08-02) | **usable now** — two fully-worked, independently-verified numeric examples: (1) whole-sign annual profection for a 5-point sample chart (Ascendant, Sun, Moon, MC, Lot of Fortune all reproduced correctly by the standard `(natal_index + years) mod 12` formula); (2) the `mustawli` dignity-scoring worked example (2nd-house cusp at 5° Aries, Sun wins with 7 points against Mars's 6 and Jupiter's 2 — arithmetic reproduced and confirmed). See `al_qabisi_rule_manifest.json` rules `islam.qabisi.ch4.annual_profection_worked_example` and `islam.qabisi.ch1.mustawli_worked_example` |
| Wurzburg TEI witnesses (7, hash-pinned) | Arabic + Hermann/John/Adelard Latin lineages | available for **variant** work, not for doctrine promotion; al-Qabisi's Arabic member of this set has now been promoted to direct-extraction status (research-verified, specialist review pending) |

The genuinely valuable artifact already in hand is the **30-passage candidate
concordance with 8 preserved variants** — including the Mars firdaria
disagreement (Arabic 7 years vs Hermann 8), John's listed values totalling 74
against a stated 75, and Adelard's 75 against a stated 77. Publishing those
disagreements is itself a defendable contribution: it is exactly what a
specialist would want to see and what no astrology product shows.

## Correction: the modern translations were never the gate

This spec originally listed the Brill (2019), Aragno (2004), and 1994 modern
translations as gates on Abu Ma'shar and al-Qabisi. That was a conflation and is
withdrawn — see "Translation is not a gate for quotation" in
[../DEFENSIBILITY.md](../DEFENSIBILITY.md).

The Arabic originals are 9th-10th century and public domain. **Seven TEI
witnesses are already downloaded and hash-verified in this repository**, covering
separate Arabic, Hermann, John, and Adelard lineages, with 30 candidate passages
already catalogued across five concepts. That text can be read and rendered now.

What the modern critical editions genuinely supply is the **apparatus** —
manuscript stemma, variant collation, and editorial argument — which is real
scholarly value that a bare TEI transcription does not carry and that a reader
cannot reconstruct. The gates have been rewritten to ask for the apparatus rather
than the translation.

Practical consequence: the 8 preserved variants (including the Mars firdaria
disagreement, Arabic 7 years against Hermann's 8, and the John/Adelard arithmetic
that does not sum to its own stated total) can be **presented now**, with the
Arabic and Latin quoted, rendered, and attributed by lineage. That is publishable
content today, and it is exactly the material a specialist would want to see.

## Refusal list

- **No firdaria dates or durations** sourced to al-Biruni section 395 specifically
  (the al-Qabisi-sourced duration table in item 7 is a separate, attributed pack).
- **No merging of Arabic and Latin lineages.** Where Hermann, John, or Adelard
  differ from the Arabic, both are shown with the lineage named.
- **No attribution of a doctrine to "Islamic astrology" generically** — every
  claim names its author and work.
- **No talismanic or ritual instruction.** That module is `not_implemented` by
  design.
- **No mundane/dynastic prediction.** Extends explicitly to al-Qabisi's own
  material now sourced: the six conjunction/ingress cycles, the world-year
  profection method (al-Kindi's chronology), and the "two greatest lots" for
  kingship duration are recorded as source content only; none may be rendered
  as a customer-facing forecast.
- **No war/political-timing output** from al-bust (the India-attributed
  post-conjunction election-hour system in al-Qabisi Ch. IV), which includes
  an explicit doctrine on the bodily and material risk of beginning a war in
  specific hours. Historical documentation only.
- **No commodity-price or economic prediction** from al-Qabisi's own
  commodity-price lots (Ch. V) — food, grain, and medicine lots cast from a
  year-revolution Ascendant. Al-Qabisi himself flags this exact material as
  weak doctrine (`wa-in kana al-qawl fiha da'ifan`); this is the source's own
  caveat, preserved rather than invented, and does not soften the refusal.
- **No length-of-life number or date** computed from the hyleg/kadkhudah/wali
  sequence now sourced from Ch. IV. The candidate-place algorithm, the
  priority order (including Dorotheus's named dissent), and the tie-break
  rules are recorded as structure; no age, date, or verdict is asserted.
- **No ethnic, religious, or physiognomic claim about a living person** from
  the Masha'allah-attributed material quoted in Ch. II's planetary-nature
  passages (e.g. religious/clothing associations, physical-type descriptions
  by planet). Historical quotation only.

## Conventions requiring disclosure

Inherits the Western core's conventions (house system, orbs, ephemeris). Adds:
lineage selection must be stated wherever Arabic and Latin witnesses diverge.

Newly disclosed by the al-Qabisi direct extraction (2026-08-02):

- **Al-Qabisi's own numerical essential-dignity scoring (domicile +5,
  exaltation +4, triplicity +3, bound +2, face +1) predates, and is textually
  identical to, the scoring table this repository's own
  `src/engine/multitradition/hellenistic.py` currently documents as "a later
  Latin development" attributed to William Lilly (1647).** Al-Qabisi states
  it in Arabic roughly seven centuries earlier. This does not change what the
  Hellenistic section refuses (the scoring table is still absent from Valens
  and Dorotheus's own qualitative judgment, which is the actual Hellenistic
  distinctive), but the "Latin anachronism" framing in that file's comments is
  now known to be imprecise about the scoring table's origin and should be
  revisited by whoever owns that integration.
- **Exaltation is degree-specific in al-Qabisi's own preferred table** (Sun
  Aries 19°, etc. — identical to this repo's `EXALTATION`), but al-Qabisi
  separately reports, and names, a **whole-sign** exaltation view attributed
  to Ptolemy ("Ptolemy makes the whole sign of Aries the Sun's exaltation").
  Both are disclosed; neither is silently preferred.
- **`khali al-sayr` (void of course) is stated for any planet in al-Qabisi's
  text**, not the Moon specifically. Later Latin practice's Moon-only "void of
  course" is a narrowing of this broader Arabic concept, not a contradiction
  of it, and both scopes should be distinguished wherever void-of-course is
  computed.
- **The malefic-proximity orb for accidental misfortune is variable** (scaled
  to that malefic's own bound-width at the point in question) except for two
  flat numeric thresholds al-Qabisi states directly: 12 degrees from either
  node, and 4 degrees from the Sun specifically. These three orb conventions
  are distinct from each other and from the general 6-degree application orb.

## Current implementation gap

Two gaps, now of different kinds. (1) The pre-existing gap remains: the
shipped section is a profile that names available layers without computing
them; halb/hayyiz and firdaria **ordering** from the validated al-Biruni pack
(items 2-6) still need composer wiring, and the variant concordance still
needs to surface as visible content rather than a research artifact. (2) A
new, larger layer is now *sourced* but equally not yet computed: 54 rules and
14 validation vectors freshly extracted directly from al-Qabisi's Arabic
(`al_qabisi_rule_manifest.json`, `al_qabisi_validation_vectors.json`) cover
essential dignity (with five full programmatically-verified table matches
against existing code and one Lilly-anachronism finding), the complete
firdaria duration table with nodes, the hyleg/kadkhudah/wali sequence, a fully
verified annual-profection worked example, primary/bound directions, and a
~50-lot compendium. None of this is `live_engine` or customer-eligible yet.
The concrete next step is independent Arabic specialist review of these 54
rules and a second independent passage-to-predicate reader (per the
corpus-wide validation gates in `source_audit.md`), after which composer
wiring can proceed for both the al-Biruni and al-Qabisi layers together
without collapsing their authorship.
