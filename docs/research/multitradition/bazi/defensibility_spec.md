# BaZi defensibility spec

Status: governing spec for the Four Pillars reading section  
Updated: 2026-08-02  
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
| 4 | **Month command (月令 / 得令)**: does the day master obtain the season | `Yuanhai Ziping` 看命入式, step 2; delineation of the states now cited to 四言獨步 items 200/206/210/213 (ctext.org) | `implemented` (wang/xiang/xiu/qiu/si + rooting) |
| 5 | Rootedness (通根) and relative strength class | `Yuanhai Ziping` step 3 | `source_gated` - schools diverge and the Sanming Tonghui interpolation problem blocks adjudication |
| 6 | Ten Gods (十神) from every stem and hidden stem to the day master | `Yuanhai Ziping` relation families; position/relation delineation now cited to 四言獨步 and 萬金賦 items 50-53, 64-66, 218-222 (ctext.org) | `implemented` |
| 7 | Branch relations: combinations (合), clashes (冲), harms, punishments, frames | `Sanming Tonghui` juan 1; delineation of what a clash/combination/storage-branch means now cited to 四言獨步 and 五言獨步 items 207-213, 341 (ctext.org) | `implemented` (six harmonies/clashes/harms/destructions, san he + san hui frames, all punishment types incl. self) |
| 8 | Pattern (格局) candidacy and completion/defeat tests | `Yuanhai Ziping` 神趣八法 | `source_gated` — school-specific precedence |
| 9 | Transformation (化) and following (从) structures | `Yuanhai Ziping` 神趣八法 | `source_gated` |
| 10 | Luck pillars: direction, commencement age, sequence | convention matrix; direction is sex-dependent | `implemented` (both directions emitted) |
| 11 | Annual/monthly period interaction with the qualified natal structure | `Yuanhai Ziping` step 6 | `implemented` (luck pillars emitted against the qualified structure) |
| 12 | Useful/avoidant element (用神) selection | school-specific | `source_gated` — preserve disagreement, never average |
| 13 | Na Yin (纳音) | `Sanming Tonghui` juan 1 | `implemented` (30-pair table; each element exactly 6 pairs) |
| 14 | Auxiliary stars (神煞) | source/school-specific | `refused` unless enabled per named pack |

**Items 3, 4, 6 and 7 are implemented**, in the hierarchy's own order. Every
technique this tradition's own authorities treat as a prerequisite to judgment
is now computed. What remains is **item 5 (strength class)** and items 8/9/12
(pattern, transformation, useful god) — and those are not implementation gaps.
They are the points where the schools genuinely disagree, and the spec's own
refusal list forbids asserting one school's answer as settled. A section that
named a pattern here would be *less* defensible, not more.

**No row above changed status in the 2026-08-02 pass.** A 22-rule DELINEATION
manifest (`bazi/yuanhai_ziping_delineation_manifest.json`, with
`bazi/yuanhai_ziping_delineation_validation_vectors.json`) was added, stating
what a Ten God in a given pillar, a branch relation, or a month-command state
classically MEANS - sourced directly to ctext.org's transcription of `Yuanhai
Ziping` (a second, independent digitization from the Wikisource page already
cited, discovered in this pass; see the source audit). This deepens items 4, 6,
and 7 (already `implemented`) with citations for their meaning, not just their
computation. It does **not** move item 5 to `implemented`: the new rules are
qualitative doctrine ("what a rooted, seasonally-strong Seven Killings at the
Hour pillar means"), not a strength-CLASS decision procedure, and the schools'
disagreement on that procedure is untouched. It does not touch items 8/9/12
either - no rule names or completes a 格局, selects a 用神, or asserts a
following/transformation verdict as settled.

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
| `Sanming Tonghui` | Wikisource juan 1-9 (10-12 missing); **ctext.org now hosts juan 10-12 in full**, OCR'd from an identified Qing-court Siku Quanshu recension (Zhejiang University Library scan; also independently held complete at ANU in the Xu Dishan collection) | case charts (命例) in later juan; juan 12 has five, naming 吳嶽, 譚論, 胡宗憲, 李邦珍, 姚淶 | partially — the "volumes 10-12 absent" half of the old blocker is resolved for LOCATION; the authenticity half is not: these are exactly the late-Ming-official charts the interpolation warning describes, now nameable but still unverified against a page image. One chart (譚論, 財官印俱旺) was hand-cross-checked against the engine's own Ten-God tables and found internally consistent — see `bazi/worked_examples.json` and the source audit |
| `Yuanhai Ziping` | Wikisource full transcription; **ctext.org hosts a second, independent transcription** (chapter=901791) with sections (萬金賦, 四言獨步, 五言獨步, 五行生克賦, 珞琭子消息賦) absent from the earlier Wikisource-only catalogue | terse judgments in 杂论口诀 (Wikisource); 22 delineation aphorisms now extracted from the ctext sections into `bazi/yuanhai_ziping_delineation_manifest.json` | delineation aphorisms usable now (research-only, `evidence_grade C`); a named facsimile lead (故宮珍本叢刊 / Hainan Publishing House) was found but not opened, so edition control is still absent — worked-example CHARTS were not found in this text specifically |
| `Mingli Jicheng` juan 1 | NLC/Wikimedia page-image PDF | unknown; no OCR layer | needs visual transcription of title page and contents first |

**Important caveat for this tradition specifically:** the interpolation warning on
`Sanming Tonghui` means BaZi worked examples cannot be trusted as golden cases
until edition control exists. This is a stronger gate than in Jyotisha, and it is
why item 8 and 12 stay source-gated. The 2026-08-02 pass narrowed this gate
(named the specific disputed charts, identified the underlying court recension
and two independent facsimile holdings) but did not close it — no page image was
personally opened and collated against the ctext OCR in this pass.

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

The shipped panel covers items 1, 2, 3, 4, 6, 7, 10 and 13's inputs and emits a
reading in the Ziping order: subject, month command, roots, Ten Gods, branch
relations, absences.

**This is the ceiling the sources currently permit.** Strength class (5) and
pattern (8/9/12) are the next techniques in the hierarchy, and both are
school-divergent; the `Sanming Tonghui` interpolation problem means no edition
in hand can adjudicate between schools. Implementing them would require picking
a school and presenting its answer as the tradition's, which the refusal list
prohibits. Raising this section further therefore needs *source* work — a dated
scan resolving the interpolations, then a named school pack — not more code.

A structural worked-example suite (10/10, mutation-tested) covers the day
anchor, hidden stems, Ten Gods and seasonal command; branch-relation tables are
covered by structural tests (each of the four pair tables partitions all twelve
branches exactly once; clashes are exactly six positions apart; both frame sets
partition the twelve).

**2026-08-02 addition: a delineation research pack, still behind the same gates.**
`bazi/yuanhai_ziping_delineation_manifest.json` (22 rules) and its matching
`bazi/yuanhai_ziping_delineation_validation_vectors.json` (23 vectors) state what
the already-implemented computations classically MEAN in position (Ten God per
pillar), in relation (branch clashes, combinations, storage branches), and in
transition (luck-pillar interactions). This is a citation layer for a future
composer, not a change to what the panel computes or narrates today - no engine
or composer code was touched. Content that states a lifespan, death,
violent-punishment, or gendered claim is marked `output_policy: refused` inside
the rule and kept as historical quotation only, consistent with the refusal list
below. The single biggest remaining gap is unchanged in kind, though narrower in
scope: **item 5 (strength class) and items 8/9/12 (pattern, transformation,
useful god) still require a resolved edition** - specifically, a page-image
collation of the newly-identified Sanming Tonghui facsimiles (ANU Xu Dishan
collection; Zhejiang University Library / Siku Quanshu scan) against the ctext
transcription, to determine which juan-12 case charts are original to Wan
Minying's text. That collation, not more delineation-rule extraction, is the next
highest-value step; only it can move item 5 or the worked-example inventory
status further.
