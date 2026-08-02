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
| 2 | Halb and hayyiz, with the one-way implication | al-Biruni pack, incl. the Mars case | `computable` — pack validated, composer work only |
| 3 | Planetary and sign gender/sect classification | al-Biruni pack | `computable` |
| 4 | Mercury's conditional classification | al-Biruni pack (explicitly conditional) | `computable` — and note al-Qabisi appears to classify Mercury male/diurnal instead |
| 5 | Firdaria ordering, diurnal and nocturnal | al-Biruni pack (validated) | `computable` |
| 6 | Equal-seventh subperiod structure | al-Biruni pack (validated) | `computable` |
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
