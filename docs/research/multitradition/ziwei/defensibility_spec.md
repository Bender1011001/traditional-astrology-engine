# Zi Wei Dou Shu (紫微斗數) defensibility spec

Status: governing spec for the Zi Wei section — research stage, nothing shipped
Updated: 2026-08-02
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

**This track transcribes one candidate lineage, not the tradition at large.** The pack
behind it is seven construction rules read from the Chinese Wikisource text of *Ziwei
Doushu Quanshu* juan 2. The base facsimile is unidentified, no collation history is
recorded, and the page's relation to the Quanji or Jielan printings is unknown. Every rule
in the pack therefore carries evidence grade D — strong enough to place a palace, nowhere
near strong enough to say what a palace means. A different three-juan work under the same
title survives in the Zhengtong Daozang with different star names and a different
construction; it is a homonym, not a variant, and is never used to fill a gap here.

## What this tradition actually does

A Zi Wei reading starts from the **lunar birth month**, not the solar date BaZi uses, and
places fourteen main stars and dozens of auxiliaries into twelve palaces built around a
life palace and a body palace. Nearly everything downstream — the topic palaces, the
month- and hour-keyed auxiliary stars, the year-keyed Four Transformations, the decade and
annual limits — depends on getting that first lunar month right, and the transcription
this track holds supplies no calendar of its own.

The product-layer resolution is the load-bearing decision in this track: rather than
assert a meridian the pack does not specify, this section runs the panel's own validated
lunisolar kernel under three real calendar regimes (Purple Mountain 120°E, pre-1929
Beijing local mean time, and the Vietnamese 105°E profile already validated elsewhere in
the panel) and only builds the chart when all three land on the same chart month. That
gate is what turns an assumption into a checked claim: the reader is not asked to trust a
meridian, only to see that no plausible one moves the answer.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Civil-to-lunisolar chart-month resolution | pack states life/body placement needs the lunar month and supplies no conversion; product-layer kernel runs three calendar regimes and gates on agreement | `implemented` as a disclosed configured method, gated rather than asserted |
| 2 | Intercalary-month normalization (leap month uses the FOLLOWING month number) | explicit worked example in *An shen ming li* | `implemented` |
| 3 | Life palace placement | month palace (lunar month 1 at Yin) treated as Zi hour, counted backward to birth hour; three explicit worked examples | `implemented` |
| 4 | Body palace placement | same month palace, counted forward; same three worked examples | `implemented` |
| 5 | Twelve topic palace assignment | reverse branch order from the life palace; one explicit worked example | `implemented` |
| 6 | Zuofu / Youbi placement | month 1 at Chen/Xu respectively; two explicit worked examples (months 1 and 2) | `implemented` |
| 7 | Wenchang / Wenqu placement | Zi hour at Xu/Chen respectively; two explicit worked examples (Zi and Chou hours) | `implemented` |
| 8 | Four Transformations by birth-year stem | full ten-stem table with the Jia row explicitly worked; rule permits computation if lineage is always shown and no later school is merged in | `implemented`, lineage disclosed every time it is shown |
| 9 | Five Tigers palace-stem starting sequence | table is transcribed, but its own publication limit reads "do not use this table until Chinese characters and pairings are collated against the selected facsimile," and the vector marks it `implementation_allowed_before_facsimile_collation: false` | `refused` — the only rule in the pack that forbids its own use outright |
| 10 | Five-phase bureau (局) and the resulting main-star sequence | no table in this pack at all | `source_gated` — arithmetic is simply absent, and it is keyed to the lunar day, which (unlike the month) does move across calendar regimes for some births |
| 11 | Zi Wei's own star and the thirteen other main stars | no placement table in this pack | `source_gated` — same absence as row 10 |
| 12 | Decade and annual limits | direction depends on birth-year stem parity combined with the subject's sex, which this panel does not collect, and the audit requires a declared historical convention before the rule may run at all | `source_gated` — blocked on an input this panel does not take, not on missing arithmetic |
| 13 | Brightness / temple / exaltation table | no table in this pack | `source_gated` |
| 14 | Any star meaning or synthesized reading | every rule carries a publication limit forbidding prose before construction reproduces facsimile-backed worked charts | `refused` |
| 15 | Merger with the Zhengtong Daozang homonym | different star names, different construction, same title | `refused` |

**At ceiling.** Nothing above is `computable` — every remaining gap is blocked on a
missing source table, a missing input this panel deliberately does not collect, or the
source's own instruction not to use a table, not on unclaimed engine work.

## Judgment hierarchy

1. **Resolve the chart month first**, across all three calendar regimes. If they disagree,
   refuse the whole chart rather than guess — this is the gate, not a formality, and a
   birth within a day or two of a new moon can legitimately land there.
2. **Place the month palace**, then life and body palace from it by the birth double-hour.
3. **Place the twelve topic palaces** in reverse order from the life palace.
4. **Place the month-keyed auxiliaries** (Zuofu, Youbi) and the **hour-keyed auxiliaries**
   (Wenchang, Wenqu) — these do not depend on the bureau or the main stars, so they are
   reachable even though the board they sit on is otherwise empty.
5. **Resolve the birth-year sui** — lunar-new-year convention primary, Li Chun convention
   cross-checked — before computing Four Transformations, since the two boundaries can
   disagree for a birth in the narrow window between them.
6. **Stop there.** No bureau, no main star, no brightness, no meaning. The palaces below
   are an empty board: correct houses, with no pieces placed in them and no judgment
   rendered about what is.

## Worked-example inventory

| Source | Contains | Usable now |
|---|---|---|
| *An shen ming li*, three life/body examples (month 1 at Zi, Chou, Yin hours) | life and body palace for three birth hours at a fixed month | **yes, and all three pass.** Vectors `ziwei.quanshu.life_body.month1_{zi,chou,yin}` |
| *An shen ming li*, intercalary-month-1 example | leap-month normalization | **yes.** Vector `ziwei.quanshu.leap_month1_normalization` |
| *An Wenchang Wenqu xing jue*, Zi- and Chou-hour examples | Wenchang/Wenqu placement | **yes, both pass.** Vectors `ziwei.quanshu.wenchang_wenqu.{zi,chou}` |
| *An Zuofu Youbi xing jue*, month-1 and month-2 examples | Zuofu/Youbi placement | **yes, both pass.** Vectors `ziwei.quanshu.zuofu_youbi.month{1,2}` |
| Ten-stem Four Transformations verse, Jia explanation | the Jia row of the transformation table | **yes.** Vector `ziwei.quanshu.four_transformations.jia` |
| Topic-palace reverse-assignment example from Zi | twelve topics from a life palace at Zi | **yes.** Vector `ziwei.quanshu.topic_palaces.reverse_from_zi` |
| A dated nativity with a facsimile-attested full chart | — | **no such example is in the retrieved corpus.** This is the track's real worked-example gap, and it is what facsimile collation would supply |

All ten of the pack's own vectors are reproduced exactly by the engine; none of them is
this panel's own birth data, and the calendar-regime self-check (three meridians, one
chart month, a lunar day that does move) is an engine-generated cross-check, not a source
worked example.

## Refusal list

- **No five-phase bureau, no main-star placement.** The pack transcribes neither table.
  The palaces are real; the board is empty.
- **No Five Tigers table**, on the source's own explicit instruction not to use it before
  facsimile collation — the only rule in this pack that forbids its own use outright.
- **No decade or annual limits.** The direction depends on a sex input this panel does not
  collect, and the audit requires a declared historical convention first regardless.
- **No star meaning, no synthesized reading.** Every rule's publication limit forbids
  prose before facsimile-backed worked charts exist. A placement is a position, not a
  judgment.
- **No merger with the Zhengtong Daozang homonym**, which shares a title and nothing else.
- **No assertion of a single calendar meridian.** Three are computed and checked for
  agreement; none is presented as simply correct.
- **No later-school Four Transformations table merged in.** This transcription's row is
  shown with its lineage every time; its own rule records `conflicts_with` a later-school
  table, and this section holds exactly one witness, not a resolution between them.

## Conventions requiring disclosure

| Convention | Chosen | Note |
|---|---|---|
| Civil-to-lunisolar conversion | panel's validated true-new-moon / true-solar-term kernel, run under three meridians and gated on agreement | not a `ziwei_default`; the pack's own refusal to pick a meridian is why three are computed instead of one |
| Double-hour partition | BaZi sexagenary kernel's shichen boundary (Zi at 23:00) | only two of twelve double-hours (Zi, Chou) have golden vectors in this pack; the rest rest on the stated counting rule alone |
| Birth-year sui resolution | lunar-new-year convention primary | cross-checked against the Li Chun convention (BaZi's own boundary) using the same precise solar-longitude search; disclosed as `LIVE` whenever the two disagree for a given birth |
| Romanization | engine normalization for stems/branches | the facsimile-backed rule must retain the Chinese characters; romanization is never load-bearing |
| Rights / edition status | Chinese Wikisource transcription, base facsimile unidentified | not a controlling edition; every fact in this track is graded D until collation |

## Current implementation gap

The palaces construct; nothing sits on them. What would move it, in order of leverage:

1. **Facsimile identification and collation.** The whole pack is one unidentified
   Wikisource transcription. Naming and collating against the Quanji or Jielan printing —
   or against Pingree/Heilen-grade critical apparatus, if one exists for this text — is
   the single acquisition that would let every grade-D rule here be reconsidered.
2. **A five-phase bureau table and a main-star placement table from that facsimile.** Both
   are absent outright; nothing here approximates them.
3. **Independent Chinese review** of all seven encoded rules and their worked examples,
   plus a second encoder reproducing the extraction without seeing this pack.
4. **A sourced double-hour boundary** beyond the two golden vectors (Zi, Chou) this pack
   supplies, so the remaining ten double-hours rest on more than the stated counting rule.
5. **A declared historical sex/gender convention and safe modern input mapping**, which
   would unblock decade and annual limits without this panel guessing at either.

Note that items 1 and 2 are document problems and item 3 is a review problem; neither is a
composer problem, which is why the checklist above carries no `computable` row.
