# Hellenistic (Firmicus / Ptolemy) delineation defensibility spec

Status: governing spec for the Hellenistic delineation layer - research stage,
nothing shipped as a customer-facing reading
Updated: 2026-08-02
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

The calculation side of this tradition is already live:
`src/engine/multitradition/hellenistic.py` computes sect, the five essential
dignities (domicile, exaltation, Dorothean and Ptolemaic triplicity, Egyptian
bound, Chaldean face), retrograde status, whole-sign houses, and the Hermetic
Lots of Fortune and Spirit with sect reversal. That file explicitly and
correctly REFUSES a Lilly-style numerical dignity score, Arabic-derived lots,
and any length-of-life verdict as anachronistic for this tradition. What this
pack adds is the delineation layer underneath those computed facts: what it
actually MEANT, to Firmicus and Ptolemy in their own words, for a placement to
carry each of those facts.

The adversary here is a specialist in Hellenistic astrology who has read Valens,
Firmicus, Dorotheus and Ptolemy in the original languages. Their first move is
not "is your dignity table right" (it already matches the engine's own reference
data, checked field-by-field below) - it is **"you claimed to prioritize Valens
and worked examples; where are they."** This spec answers that directly rather
than burying it: Valens's Greek critical edition (Kroll 1908) was fetched but its
OCR text layer is a total, whole-document failure (zero recoverable Greek
characters - see `source_audit.md`), and no worked, dated nativity chart was
located in either fetched Firmicus volume in this pass. Both are named as the
biggest remaining gap, not silently dropped.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Sect (day/night) as the first judgment | Firmicus Math. II.7 (gaudent-trio), II.20 (explicit ordering instruction); Ptolemy Apot. I ξ' (full diurnal/nocturnal assignment with physical rationale) | `implemented` in this pack |
| 2 | Consequence of sect status when a planet is angular (1st/4th/7th/10th) | Firmicus Math. II.20.11-13 | `implemented` in this pack |
| 3 | Mercury as common to both sects, resolved by solar phase | Ptolemy Apot. I ξ' | `implemented` in this pack - matches the engine's own Mercury sect_status label exactly |
| 4 | Jupiter's specific exclusion from the nocturnal sect (day-only joy) | Firmicus Math. III (De Iove) | `implemented` in this pack |
| 5 | Domicile (rulership) table, all 12 signs, with the masculine/feminine gender rationale | Firmicus Math. II.2 | `implemented` in this pack - exact match against `hellenistic.py`'s DOMICILE table |
| 6 | Exaltation degree table, all 7 classical planets | Firmicus Math. II.3 | `implemented` in this pack - exact match against `hellenistic.py`'s EXALTATION table, all 7/7 |
| 7 | Ranking exaltation above domicile as a dignity hierarchy claim | Firmicus Math. II.3.6 (sentence truncated by a manuscript lacuna) | `implemented` in this pack, disclosed as textually incomplete |
| 8 | A reported (not adopted) Babylonian counter-doctrine equating exaltation sign with domicile | Firmicus Math. II.3.6 | `implemented` in this pack, as a disclosed fork against the engine's own (separate domicile/exaltation) model |
| 9 | Decan (face) table, all 36 decans, plus the doctrine that a planet in its own decan is judged as if in its own domicile | Firmicus Math. II.4 | `implemented` in this pack - hand-verified against `hellenistic.py`'s `_face_ruler()` for 4 of 12 signs (all matched) |
| 10 | Egyptian bound (term) table computation | Firmicus Math. II.6 | `implemented` (already engine-computed; this pack additionally verifies Capricorn as an exact match and discloses a genuine manuscript-transmission fork at Sagittarius) |
| 11 | What it explicitly SIGNIFIES to stand in one's own bound (distinct from the decan doctrine) | Firmicus Math. V.2 (the Ascendant in the bounds of each planet, with in-bound co-presence sub-cases) and V.6 (the Moon in each planet's bounds/decan, phase-split) | `implemented` in the Mathesis delineation pack (`hel.mathesis.b5.ascendant_bound_lord`, `hel.mathesis.b5.moon_in_dignities`) - the 2026-08-02 gap is closed |
| 12 | Dorothean triplicity table (the engine's live Hellenistic default) | Dorotheus's own *Carmen Astrologicum* was not fetched this pass (optional per this task's brief; survives mainly through Arabic transmission) | `source_gated` - the engine's table cannot be corroborated from a primary Dorothean source in this pass |
| 13 | Ptolemaic triplicity table, fire triangle, with Mars as participating co-lord by domicile | Ptolemy Apot. I, triplicity chapter | `implemented` in this pack - exact match against `hellenistic.py`'s PTOLEMAIC_TRIPLICITY['Fire'] |
| 14 | Ptolemaic triplicity, the remaining three elements (Earth, Air, Water) | same chapter, not individually re-read past the fire triangle in this pass | `source_gated` - only Fire was independently verified from the primary Greek in this pass |
| 15 | Domicile-lord "host and guest" doctrine: a planet's fortune is conditioned by the condition of its own sign's ruler elsewhere in the chart | Firmicus Math. II.20.6-9 | `implemented` in this pack |
| 16 | Parents (4th/10th place topic): Sun+Saturn father-significators, Moon+Venus mother-significators, modulated by same-sect vs opposite-sect bodyguarding | Ptolemy Apot. III.5 | `implemented` in this pack |
| 17 | Children topic: ruler occidentality plus alien-sect placement diminishes the outcome | Ptolemy Apot. III (children chapter) | `implemented` in this pack, narrowly scoped to the one surviving clause read |
| 18 | Retrograde status delineation | `hellenistic.py` already computes `placements[].retrograde` | `source_gated` - no retrograde-specific delineation was located in the chapters read this pass |
| 19 | Lots of Fortune and Spirit topical meaning (Fortune=body/circumstance, Spirit=action) | Fortune: Firmicus Math. IV.17 (computation with sect reversal, significations, double ruler procedure, verdict) - now quoted at source in `hel.mathesis.b4.lot_of_fortune`. Spirit: still only asserted in `hellenistic.py`'s inherited prose | `source_gated` - Fortune is now `implemented`; Spirit's topical meaning remains unsourced from a primary text in this corpus |
| 20 | Whole-sign houses as the topical framework | structural/configured method, already disclosed in `hellenistic.py` | `implemented` (pre-existing engine disclosure; not a delineation rule this pack adds) |
| 21 | Manuscript-provenance discipline: Firmicus Book II's own index names seven lost chapters (VIII-XIV) | Firmicus Math., apparatus to II.7 | `implemented` in this pack as a governance rule, following the Byzantine pack's precedent for the same kind of disclosure |
| 22 | Numerical (Lilly-style) essential/accidental dignity score | anachronistic for this tradition; already refused by `hellenistic.py` itself | `refused` |
| 23 | Length-of-life / hyleg-anareta verdict, including the specific 12-year arithmetic attached to Jupiter's night-joy failure (Firmicus III, De Iove) | doctrine survives but in conflicting, unreconciled forms; already refused by `hellenistic.py` | `refused` - the sect fact is used, the longevity arithmetic built on it is not |
| 24 | Arabic-derived lots, firdaria, and expanded parts | out of period for this tradition; already refused by `hellenistic.py` | `refused` |
| 25 | A worked, dated nativity chart reproduced from a classical author's own judgment | Valens (Kroll 1908 Greek): fetched but OCR-corrupted beyond use. Firmicus (both volumes): keyword-searched, none found this pass. Ptolemy: not expected by genre (Tetrabiblos is theory-first and is not known to carry worked charts) | `source_gated` - see the worked-example inventory below; this is the pack's single biggest named gap |
| 26 | Planet-in-place delineations for all seven planets, sect-split as the text splits them (the core natal lookup) | Firmicus Math. III.2-7, III.13 | `implemented` in the Mathesis delineation pack (`hel.mathesis.b3.planet_in_house.*`, 107 house cells; Moon covers only the places III.13 delineates in anchorable form) |
| 27 | Topical signification of all twelve places | Firmicus Math. II.19 (with II.17 idle-places and the Moon's 8th-place night joy) | `implemented` (`hel.mathesis.b2.place_significations`, `hel.mathesis.b2.idle_places`) |
| 28 | Planet-in-sign delineations | Firmicus Math. V.3 (Saturn, complete) and V.4 (Jupiter, Cancer-Capricorn only; the rest of the planets-in-signs chapters are lost in the great Book V lacuna) | `source_gated` - Saturn 12/12 and Jupiter 7/12 are `implemented`; Jupiter Aries-Gemini/Aquarius-Pisces and all of Mars/Sun/Venus in signs are a lacuna of the transmission, disclosed in the rules, not fillable from Firmicus |
| 29 | Moon applications/separations (defluxio) with lunar-phase and sect splits, incl. the void-of-application Moon | Firmicus Math. IV.9-15 | `implemented` for the from-Saturn, from-Jupiter and from-Mars series and the void series through Mars; the from-Sun/-Venus/-Mercury series are partially encoded with the unmined remainder named per rule in `exceptions` |
| 30 | Two-planet aspect-figure delineations (trine/square/opposition/conjunction), with dexter-overcoming and sect conditions | Firmicus Math. VI.3-27; Kroll's apparatus prints the Dorotheus-descended Greek parallels (Anon. De planetis, CCAG II) | `implemented` for six precisely-stateable cells (Saturn-Jupiter all four figures; Jupiter-Venus, Jupiter-Mercury trines); the remaining pair-chapters follow the same template and are named unmined |
| 31 | Delineation keyed to the decan (face) lord the engine computes | Firmicus Math. V.5-V.6 ('in domo vel in decano Solis', 'in decano suo' cells for Mercury and the Moon) | `implemented` as far as the V.5 fragment and V.6 survive; a full 36-decan delineation set exists only in Book VIII's rising-decan material, unmined |

Nothing on this checklist is `computable` in the DEFENSIBILITY.md sense of "our
gap, and actionable by the composer alone" - items 12, 14, 18, 19 (Spirit), 25
and 28 are blocked on a named missing document, a named unperformed close-read,
a named access failure, or a lacuna of the manuscript transmission itself, and
items 22-24 are standing tradition-level refusals inherited from the live
engine's own disclosures. Items 26-31 were added by the 2026-08-03
delineation-at-volume pass (`mathesis_delineation_rule_manifest.json`).

## Judgment hierarchy

Firmicus states the hierarchy himself (II.20.11-12: check sect before anything
else, then invert the same test for a night chart), so this section does not
invent an order:

1. **Determine sect first.** Day or night nativity (`facts.sect`), independent of
   any placement. This governs everything that follows and reverses between a
   day chart and a night chart (Firmicus II.20.12: "eodem inmutato ordine
   potestatis").
2. **Read each placement's dignity as a set of rulership relations**, not a
   total: domicile, exaltation, triplicity (both Dorothean, live, and Ptolemaic,
   disclosed as a fork), bound, and decan/face. A planet in its own decan is
   treated as though in its own domicile even when the sign belongs to another
   (Firmicus II.4) - this is checked explicitly, not folded into a score.
3. **Assess the condition of each placement's domicile lord separately**, per
   Firmicus's host/guest doctrine (II.20.6-9): a planet's own placement facts are
   not the whole story if its sign's ruler is badly placed elsewhere.
4. **Combine sect status with angularity** for the single strongest good/bad
   signal in the chart (Firmicus II.20.11-13): a sect-favored planet angular is
   the best available configuration; a sect-contrary planet angular is the
   worst.
5. **Only then move to the delineation lookups** - place significations
   (II.19), planet-in-place (III.2-13, selecting the by_day/by_night sub-cell
   by the sect determined in step 1), planet-in-sign and dignity-host cells
   (V.2-6, selecting by bound/decan lord and lunar phase), Moon-flow (IV.9-15,
   selecting by phase and sect), aspect pairs (VI), and the house-topic
   delineations (parents, children; Ptolemy III.5, III children chapter) -
   topic-specific judgments are downstream of, not a substitute for, steps 1-4.
6. **Refuse throughout**: no numerical total is produced at any step (per the
   engine's own disclosure), no longevity number is produced even where the
   sect fact that would feed one is used (Jupiter's night-joy failure is stated,
   its twelve-year arithmetic is not), and no Arabic-period material is
   introduced.

## Worked-example inventory

| Source | Contains | Usable now |
|---|---|---|
| Firmicus, Mathesis, both fetched volumes (~2.3M characters, Books I-VIII) | doctrine and a very large number of illustrative planet-in-place combinations | **no worked, DATED real nativity located** - a targeted keyword search (`genitura` + person name, `natus est`, consulship-year phrasing, first-person testimonial language) returned nothing; this is a search result over a large text, not a cover-to-cover read, and is named as the pack's top next step |
| Vettius Valens, Anthologiae (Kroll 1908 Greek) | per standard scholarship on this text (confirmed here only through Riley's translation, used for location only, never as authority): dozens of worked example charts throughout the later books and Valens's own datable nativity | **no - the fetched Greek OCR text is a total failure (zero recoverable Greek characters across 1.1M characters); nothing can be quoted from the critical edition itself** |
| Ptolemy, Apotelesmatika (Boll/Boer) | systematic doctrine only | **not applicable - this genre does not carry worked charts; no absence is being hidden here, this is what the text is** |
| Riley's Valens translation (reading aid only) | modern English rendering of the whole work, including (per its own pagination) worked charts later in the text | **not used as source authority for any rule; would need the Greek restored to be usable at all, per this corpus's translation-is-not-a-gate-for-quotation policy** |

**Result: zero worked examples are reproducible today.** This mirrors the
Byzantine pack's own honest finding for a structurally different reason (there,
the surviving chapters simply never included one; here, the single most
promising source is access-blocked and the other fetched source's relevant
books were keyword-searched rather than fully read). The route to a real worked
example runs through repairing Valens's OCR, not through anything already in
hand.

## Refusal list

- **No numerical (Lilly-style) essential or accidental dignity score.** Valens,
  Dorotheus and Firmicus all judge planetary condition qualitatively - by sect,
  rulership relation, and place - not by a summed total. This is already the
  live engine's own position and this pack adds nothing that would undermine it.
- **No length-of-life, hyleg, or anareta verdict**, even where the underlying
  sect fact is used elsewhere. Firmicus's own text ties Jupiter's failure to
  rejoice at night to a specific twelve-year reduction of the decreed lifespan
  (III, De Iove); the sect classification this passage confirms is used in
  `hel.firmicus.jupiter_no_joy_at_night`, but the longevity arithmetic itself is
  explicitly refused as output in that same rule's `publication_limit`.
- **No Arabic-derived lots, firdaria, or expanded parts.** Out of period for
  this tradition; nothing in the fetched Firmicus or Ptolemy material was used
  to introduce any.
- **No claim quoted from Valens's Greek critical edition.** The fetched OCR text
  is corrupted beyond responsible use (see `source_audit.md`); rather than
  reconstruct a plausible-looking Greek quotation from a broken font mapping,
  or substitute Riley's copyrighted translation as if it were the source of
  record, this pack simply does not cite Valens for anything beyond an
  inventoried, blocked lead.
- **No worked-example chart presented as reproduced or verified.** None was
  found; the worked-example inventory says so plainly rather than padding the
  pack with a hypothetical or reconstructed chart.
- **No merging of the Dorothean and Ptolemaic triplicity tables.** The engine
  already discloses this as a fork (`hellenistic.py`'s "Bounds and triplicities"
  disclosure); this pack's rules support the Ptolemaic side of that fork without
  touching or overriding the Dorothean default.
- **No customer-facing prediction of any kind.** Every rule and every vector in
  this pack carries `customer_prediction: false`; this is a research-stage pack
  and nothing in it is wired to a reading composer.
- **Per-cell refusals in the delineation-at-volume pack.** Firmicus routinely
  decrees death timing and manner, lifespan numbers, enslavement and child
  exposure, disease and disability as fate, sexual "infamy", and criminal
  conduct. All such cells are encoded faithfully - the fourth-century text is
  not bowdlerised - and carry `output_policy: refused` with a stated reason
  (55 of 196 cells); where only one clause of an otherwise renderable cell is
  affected, the clause is quarantined in `restricted_clauses` and the rest of
  the cell remains renderable. Refused cells are never rendered as claims
  about a living person.
- **No filling of the Book V lacuna from other authors.** Jupiter in
  Aries-Gemini and Aquarius-Pisces, and Mars/Sun/Venus in the signs, are lost
  in the transmission; the sign rules state this and a validation vector
  (`hel.mathesis.b5.jupiter.aries.lacuna`) pins the engine to reporting the
  gap rather than fabricating a cell.

## Conventions requiring disclosure

| Convention | Chosen | Note |
|---|---|---|
| Controlling editions | Firmicus: Kroll/Skutsch 1897 (vol.1) and Kroll/Skutsch/Ziegler 1913 (vol.2). Ptolemy: Boll/Boer, a later "editio stereotypa correctior" of the 1940 first edition | public domain for Firmicus (pre-1929, US); Ptolemy's specific 1940-descended edition's US rights status is flagged, not assumed clear - see `source_audit.md` |
| Translation | engine's own, from the Latin/Greek | graded `engine_translation_unreviewed`; original text is shown beside every rendering |
| Text of record | the fetched OCR text, not a page image | no page images were fetched for this pack (unlike the Byzantine pack's CCAG page PNGs); every rule is graded B (or C where a specific Roman-numeral transcription risk is flagged) rather than A for exactly this reason |
| Valens exclusion | total OCR failure, not a language or rights decision | zero Greek Unicode characters recovered across 1,100,625 characters; documented at length in `source_audit.md` so a future pass does not have to re-diagnose it |
| Editorial supplements and lacunae | disclosed per rule | Kroll/Skutsch's `<Saturnus>`, `<in>`, and marked lacunae (rows of asterisks, or an editorial ellipsis) are flagged in the `exceptions` field of every rule that depends on one |
| Sagittarius bound fork | Firmicus's own printed manuscript numbers are shown alongside the apparatus's comparanda from Ptolemy/Dorotheus/Paulus/Alexander, and the engine's table is disclosed as following the latter, not Firmicus's specific manuscript reading | a genuine, disclosed manuscript-transmission fork, not an error in either source |
| Mercury's sect | common to both, resolved by solar phase (morning=diurnal, evening=nocturnal) per Ptolemy | the engine's `_sect_status()` returns a fixed "common" label without checking phase; this pack's rule states the doctrine that WOULD resolve it, without claiming the engine currently implements the phase check itself |
| Book II citation discipline | any citation falling in Firmicus's own documented chapter-loss zone (II, chapters VIII-XIV) is anchored to an independently visible heading or running page header | see `hel.firmicus.book2_lost_chapters_disclosed` |
| Cell anchoring (delineation-at-volume pack) | every quoted cell carries the source file name, char offset, and line number into the SHA-256-pinned OCR text; quotations are sliced from the file by offset and end-marker, never retyped | `mathesis_delineation_rule_manifest.json`, every cell |
| Apparatus interleaving | vol. 2's OCR splices the page-foot critical apparatus into the running text at page breaks; affected quotations stop at the last clean clause and say so in cell notes | e.g. the Saturn-in-Capricorn/Pisces and Horoscopus-in-finibus-Mercurii lemmata, split mid-word across the splice |
| Sect and phase splits | wherever Firmicus splits a judgment by sect or lunar phase, the cell carries by_day/by_night or waxing/waning sub-cells exactly as printed; the consuming engine selects by its computed sect/phase and falls back to the cell's top level when no split exists | Book III passim; IV.9-15; V.5-6 |

## Current implementation gap

There is no live Hellenistic delineation composer wired to customers, and no
engine code was changed by these passes. The 2026-08-02 pass built 19 rules and
16 validation vectors (sect/dignity doctrine, tables); the 2026-08-03
delineation-at-volume pass added `mathesis_delineation_rule_manifest.json` -
23 rules, 196 quoted Latin cells (107 planet-in-house cells, 19 planet-in-sign
cells, plus place, bound-lord, dignity-host, Moon-flow, Lot and aspect-pair
cells; 41 cells sect-split into by_day/by_night, 15 phase-split, 55 refused) -
and 37 vectors, all resting on the same two public-domain Kroll/Skutsch(-
Ziegler) volumes. The `hel.mathesis.b3.planet_in_house.{planet}` and
`hel.mathesis.b5.planet_in_sign.{planet}` rules follow the rule-id and
cell-shape convention the per-tradition report engine
(`src/engine/traditions/hellenistic_report.py`) consumes directly.

What that buys, concretely: sect is now a sourced, quoted judgment (not just a
computed fact) with an explicit hierarchy instruction, an angular consequence,
a physical rationale for the malefics' cross-sect assignment, and a named
exception (Jupiter's night exclusion); the exaltation table, the domicile
table, and the decan/face table are each an exact, field-checked match against
the engine's own reference data; one bound-table sign is a verified exact match
and a second is a disclosed, honestly-flagged manuscript fork rather than a
silent discrepancy; the Ptolemaic triplicity fork is now sourced for its fire
triangle; and two house-topic delineations (parents, children) tie the sect
concept to a concrete outcome rather than leaving it abstract.

What it does not buy: any worked chart (the pack's clearest weak point, stated
first rather than buried); a source for the engine's live Dorothean triplicity
default (Dorotheus was not fetched); the remaining three Ptolemaic triplicity
elements past Fire; any delineation for retrograde status or for the Lot of
Spirit; the Moon's 5th-9th places in Book III (not printed in anchorable form
in III.13 as transmitted plus this pass's coverage); the Book V lacuna
material (unfillable from Firmicus); the unmined remainders named per rule in
`exceptions` (the from-Sun/-Venus/-Mercury Moon-flow targets, the void Moon
from the Sun/Venus/Mercury, the V.1 rising-sign-plus-angles chapter, the
remaining Book VI pair-chapters, Book VIII's rising-decan material); and Book
VII, which is dominated by refused topics (exposed infants, slaves, eunuchs,
violent deaths) and was deliberately left unmined rather than encoded as a
wall of refusals.

The single biggest remaining gap is the worked-example chart DEFENSIBILITY.md's
requirement 4 calls "the strongest available proof short of hiring a specialist
per tradition" - and it is a gap for an access reason (Valens) compounded by a
search-depth reason (Firmicus), not a doctrine reason. The next three moves, in
order of value:

1. **Render page images of Valens (Kroll 1908) and read them directly**, exactly
   as the Byzantine pack did for its own OCR-failure case (Lydus). This is the
   only realistic route to both a sourced sect chapter in Valens's own words and
   a real, dated worked nativity.
2. **A genuine cover-to-cover read of Firmicus Books VI-VIII** (not a keyword
   search) specifically hunting for a real illustrative nativity distinguishable
   from a paradigmatic combination - the second-most-promising lead in hand.
3. **Independent Latin and Greek philological review** of all 19 encoded rules,
   plus page-image collation of the specific cited passages, to move this pack's
   evidence grade from B (OCR-read) to A (page-image collated), matching the
   Byzantine pack's standard; and a genuine check (not an assumption) of the
   Boll/Boer 1940-descended edition's current US copyright status before any of
   its quoted Greek is used beyond this research-only pack.
