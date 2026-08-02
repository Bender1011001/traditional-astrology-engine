# BaZi defensibility spec

Status: governing spec for the Four Pillars reading section  
Updated: 2026-08-01  
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

The adversary is a Ziping practitioner. That reader will look for month command
(得令) before anything else, and will reject a five-element percentage score
outright — the source audit already established that the inspected `Yuanhai
Ziping` gives a hierarchy of conditional judgments, not a tally.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Four pillars under named boundary conventions | HKO tables (validated kernel) + disclosed Li Chun/jie conventions | `implemented` |
| 2 | Day master identification | `Yuanhai Ziping` 看命入式: the day stem is the subject | `implemented` |
| 3 | Hidden stems (藏干) in each branch | `Sanming Tonghui` juan 1 | `implemented` (main qi drives judgment; middle/residual reported without weight) |
| 4 | **Month command (月令 / 得令)**: does the day master obtain the season | `Yuanhai Ziping` 看命入式, step 2 | `implemented` (wang/xiang/xiu/qiu/si + rooting) |
| 5 | Rootedness (通根) and relative strength class | `Yuanhai Ziping` step 3 | `computable` — depends on 3 |
| 6 | Ten Gods (十神) from every stem and hidden stem to the day master | `Yuanhai Ziping` relation families | `implemented` |
| 7 | Branch relations: combinations (合), clashes (冲), harms, punishments, frames | `Sanming Tonghui` juan 1 | `computable` |
| 8 | Pattern (格局) candidacy and completion/defeat tests | `Yuanhai Ziping` 神趣八法 | `source_gated` — school-specific precedence |
| 9 | Transformation (化) and following (从) structures | `Yuanhai Ziping` 神趣八法 | `source_gated` |
| 10 | Luck pillars: direction, commencement age, sequence | convention matrix; direction is sex-dependent | `implemented` (both directions emitted) |
| 11 | Annual/monthly period interaction with the qualified natal structure | `Yuanhai Ziping` step 6 | `computable` after 4-5 |
| 12 | Useful/avoidant element (用神) selection | school-specific | `source_gated` — preserve disagreement, never average |
| 13 | Na Yin (纳音) | `Sanming Tonghui` juan 1 | `computable` |
| 14 | Auxiliary stars (神煞) | source/school-specific | `refused` unless enabled per named pack |

**Items 3, 4 and 6 are now implemented** (2026-08-01), in the hierarchy's own
order. The section is no longer a pillar calculator. Remaining blockers are 5
(strength class, which is school-dependent) and 7 (branch relations).

## Judgment hierarchy

Taken directly from the inspected `Yuanhai Ziping` 看命入式 and recorded in the
source audit. The composer must follow it; steps may not be reordered.

1. Establish the day stem as the subject.
2. Determine month command, seasonal depth, and whether the subject has timely
   support.
3. Determine rootedness and relative strength.
4. Identify eligible relations and pattern candidates.
5. Test whether each candidate completes, is damaged, competes, transforms,
   follows, or fails.
6. Apply luck and annual periods to the already-qualified natal structure.
7. Render judgment with all supporting and defeating predicates exposed.

Step 6 is explicit that periods apply to the *qualified* structure. A reading that
narrates luck pillars before establishing strength has inverted the tradition.

## Worked-example inventory

| Source | Location | Contains | Usable now |
|---|---|---|---|
| `Sanming Tonghui` | Wikisource juan 1-9 (10-12 missing) | case charts (命例) in later juan | partially — volumes 10-12 absent; the work page warns that later commercial printings **inserted** late-Ming official charts, so any case chart must be checked against a dated scan before use |
| `Yuanhai Ziping` | Wikisource full transcription | terse judgments in 杂论口诀 | discovery only — the page is categorized as a work without a cited source |
| `Mingli Jicheng` juan 1 | NLC/Wikimedia page-image PDF | unknown; no OCR layer | needs visual transcription of title page and contents first |

**Important caveat for this tradition specifically:** the interpolation warning on
`Sanming Tonghui` means BaZi worked examples cannot be trusted as golden cases
until edition control exists. This is a stronger gate than in Jyotisha, and it is
why item 8 and 12 stay source-gated.

## Refusal list

- **No five-element percentage score.** The source audit's first architectural
  conclusion. Numerical measures may assist a documented rule; they may never
  substitute for the categorical and conditional logic.
- **No useful-element (用神) verdict** presented as settled while schools
  disagree. Where computed, disagreements are preserved, not averaged.
- **No health, disease, disability, fertility, lifespan, criminality, sexual
  morality, or class/gender delineation** rendered to a reader, per the audit's
  safety policy — retained in the audit trace with the suppression reason.
- **No pattern verdict** until month command and strength are established.
- **No auxiliary-star claim** except inside a named school pack.

## Conventions requiring disclosure

| Convention | Chosen | Alternatives |
|---|---|---|
| Year boundary | Li Chun (315 degrees) | lunar new year; civil January 1 |
| Month boundary | twelve jie by Swiss Ephemeris solar longitude | printed almanac; mean motion |
| Day anchor | JDN 2433191 = Jia-Zi (cross-checked at 2000-01-01) | any registered concordance |
| Day rollover | civil midnight | late-Zi rollover at 23:00 |
| Hour clock | true solar time primary | clock time; local mean time |
| Luck direction | both emitted (sex not in input contract) | single direction once sex is supplied |

## Current implementation gap

The shipped panel covers items 1, 2, 3, 4, 6, 10 and 13's inputs, and emits a
reading in the Ziping order. Next: **branch relations (7)** - combinations,
clashes, harms, punishments - then strength class (5) only if a named school
pack fixes its criteria. Items 8, 9 and 12 stay gated until edition control
resolves the interpolation problem. A structural worked-example suite (10/10,
mutation-tested) now covers the anchor, hidden stems, Ten Gods and seasonal
command.
