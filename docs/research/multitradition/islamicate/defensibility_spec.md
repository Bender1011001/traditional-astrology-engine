# Islamicate / Persian defensibility spec

Status: governing spec for the Islamicate section  
Updated: 2026-08-01  
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
| 7 | Firdaria **durations and dates** | — | `refused` from this pack: section 395 supplies neither node periods nor a major-duration table |
| 8 | Lunar mansions (manazil) | pre-Islamic Arabian track, source-limited | `source_gated` |
| 9 | Lots beyond Fortune/Spirit in the Arabic tradition | al-Biruni's lot chapters | `source_gated` |
| 10 | Tasyir / directions | Abu Ma'shar, al-Qabisi | `source_gated` |
| 11 | Conjunctional/mundane doctrine | Abu Ma'shar Great Introduction | `source_gated` |

## Judgment hierarchy

1. Sect, established first — it conditions every subsequent malefic/benefic
   judgment.
2. Planetary condition including halb/hayyiz, respecting the one-way implication
   the pack encodes (hayyiz implies halb; halb does not imply hayyiz).
3. Dignity and reception on the shared classical core.
4. Firdaria ordering as a structural fact — without asserting durations.
5. Author attribution on every doctrinal claim: al-Biruni, Abu Ma'shar, and
   al-Qabisi are not interchangeable.

## Worked-example inventory

| Source | Contains | Usable now |
|---|---|---|
| al-Biruni, *Kitab al-Tafhim* | instructional question/answer format; the Halle facing-text edition is inspected | limited — instructional, not worked charts |
| Abu Ma'shar, *Great Introduction* | Brill Arabic/English edition identified | edition access gated |
| al-Qabisi, *Introduction* | Aragno Arabic/English/Latin edition identified | edition access gated |
| Wurzburg TEI witnesses (7, hash-pinned) | Arabic + Hermann/John/Adelard Latin lineages | available for **variant** work, not for doctrine promotion |

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

- **No firdaria dates or durations** sourced to al-Biruni section 395.
- **No merging of Arabic and Latin lineages.** Where Hermann, John, or Adelard
  differ from the Arabic, both are shown with the lineage named.
- **No attribution of a doctrine to "Islamic astrology" generically** — every
  claim names its author and work.
- **No talismanic or ritual instruction.** That module is `not_implemented` by
  design.
- **No mundane/dynastic prediction.**

## Conventions requiring disclosure

Inherits the Western core's conventions (house system, orbs, ephemeris). Adds:
lineage selection must be stated wherever Arabic and Latin witnesses diverge.

## Current implementation gap

The shipped section is a profile: it names available and gated layers without
computing them. Next work: compute halb/hayyiz and the firdaria **ordering** from
the validated pack (items 2-6), and surface the variant concordance as visible
content rather than a research artifact.
