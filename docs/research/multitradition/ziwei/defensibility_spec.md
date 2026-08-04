# Zi Wei Dou Shu (紫微斗數) defensibility spec

Status: governing spec for the Zi Wei section — research stage, nothing shipped
Updated: 2026-08-04
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

**This track transcribes one candidate lineage, not the tradition at large.** Behind it now
sit two packs. The older `calculation_rule_manifest.json` holds seven grade-D construction
rules read from a single Wikisource page. The new
`quanshu_full_rule_manifest.json` holds **83 rules and 100 vectors** covering all three
juan of *Ziwei Doushu Quanshu* as Chinese Wikisource transmits it — every juan retrieved as
raw wikitext and hash-pinned with its revision id in `sources/access_manifest.json`.

A different three-juan work under the same title survives in the Zhengtong Daozang with
different star names and a different construction; it is a homonym, not a variant, and is
never used to fill a gap here.

## What changed on 2026-08-04

The previous version of this spec said the pack held "no five-phase bureau table and no
Zi Wei placement table" and described the engine's output as "an empty board". That was
wrong, and the correction is documented in the addendum to `source_audit.md`.

Both tables were on the page the earlier pass had already read. They are printed as
ASCII-art grids inside `<nowiki>` blocks and as a captioned diagram, not as prose, and a
prose-oriented extraction walked past them. The bureau itself is not printed as a grid at
all: it is the **composition of two printed tables** — the Five Tigers stem sequence and
the sixty-jiazi nayin song — and the chapter performs that composition itself, once, in its
opening paragraph (`如甲生人安命在寅…是丙寅丁卯炉中火…却去火局寻某日生期起紫微帝王`).

A dated facsimile of the same lineage has also been located and hash-pinned: the **Ming
Nanyangtang printing of 新鋟希夷陳先生紫微斗數全書 in seven juan** (Internet Archive
`20260506_20260506_1217`, 266 leaves). Its OCR layer is unusable; its page images are
retrievable one at a time. Collation against it is the one acquisition still owed.

## What this tradition actually does

A Zi Wei reading starts from the **lunar birth month**, not the solar date BaZi uses, and
places fourteen main stars and dozens of auxiliaries into twelve palaces built around a
life palace and a body palace. The month fixes the palaces; the **lunar day**, through the
five-phase bureau, fixes where Zi Wei itself stands, and therefore where all fourteen main
stars stand.

That split is the whole shape of this track's evidence problem. The product layer supplies
the civil-to-lunisolar conversion the pack lacks, and runs it under three real calendar
regimes (Purple Mountain 120°E, pre-1929 Beijing local mean time, and the Vietnamese 105°E
profile) rather than asserting a meridian. The chart **month** survives all three for most
births. The chart **day** does not always, and where it does not, the bureau — and with it
the entire main-star board — is genuinely undetermined rather than merely unimplemented.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Civil-to-lunisolar chart-month resolution | pack supplies no calendar; product-layer kernel runs three regimes and gates on agreement | `implemented` as a disclosed configured method |
| 2 | Intercalary-month normalization | explicit worked example in *An shen ming li* | `implemented` |
| 3 | Life palace placement | month palace treated as Zi hour, counted backward; three worked examples | `implemented` |
| 4 | Body palace placement | same, counted forward | `implemented` |
| 5 | Twelve topic palace assignment | reverse branch order from the life palace | `implemented` |
| 6 | Zuofu / Youbi placement | month 1 at Chen/Xu; two worked examples | `implemented` |
| 7 | Wenchang / Wenqu placement | Zi hour at Xu/Chen; two worked examples | `implemented` |
| 8 | Four Transformations by year stem | full ten-stem table, Jia row worked | `implemented`, lineage disclosed |
| 9 | Five Tigers palace-stem sequence | characters now recorded; the chapter's own worked example exercises the Jia/Ji row end to end | **`implemented`** — the blanket prohibition is narrowed to "always show the derivation", under rule `…five_tigers_starting_stem_recorroborated` |
| 10 | **Sixty-jiazi nayin table** | printed in full, thirty couplets, two graphic defects repairable against the closed cycle | **`implemented`** — new |
| 11 | **Five-phase bureau (五行局)** | Five Tigers ∘ nayin, composed by the chapter itself in a worked example; 10×12 table derived | **`implemented`** — new, gated on the lunar day surviving all three calendar regimes |
| 12 | **Zi Wei placement by bureau and lunar day** | five printed verses and five printed day-grids; one closed form reproduces 58/60 printed cells and 10/10 verse anchors | **`implemented`** — new, behind the same day gate |
| 13 | **Tian Fu placement** | `安天府图` diagram plus caption 如紫居丑则府居卯 | **`implemented`** — new |
| 14 | **All fourteen main stars** | `安南北斗诸星诀`, six counted back from Zi Wei and eight forward from Tian Fu; the first couplet closes its own circle | **`implemented`** — new |
| 15 | **Brightness table 廟旺得地利益平和不得地落陷** | printed grid; 12 rows × 20 stars = 240 cells, no repetition, absences structurally required | **`implemented`** — new, attached to every placed main star |
| 16 | **Seventeen auxiliary natal tables** | Kui/Yue, Lu Cun, Yang/Tuo, Tian Ma, Huo/Ling, Kong/Jie, Ku/Xu, Long Chi/Feng Ge, Tai Fu/Feng Gao, Hong Luan/Tian Xi, Xing/Yao, Jie Lu and Xun Kong voids, Shang/Shi, San Tai/Ba Zuo | **`implemented`** — new; San Tai and Ba Zuo sit behind the lunar-day gate, the rest do not |
| 17 | **Ming Zhu / Shen Zhu** | two printed tables with worked examples | **`implemented`** — new |
| 18 | **Star element and Dipper attributions** | eighteen printed lines, count confirmed by the closing sentence | **`implemented`** — new, attached to the placed main stars |
| 19 | **Judgment hierarchy (juan 3 谈星要论)** | the chapter numbers its own steps 第一 / 次 / 三 / 四 | **`implemented`** — published as an ordered source fact; not executed, because this section renders no reading |
| 20 | Twelve-stage cycle, twelve gods, decade limits, small limits | tables complete; **direction** depends on birth-year parity combined with sex as a historical binary | `source_gated` — blocked on an input this panel does not take, not on arithmetic |
| 21 | **Child limits (童限)** | complete and **not** sex-gated | **`implemented`** — new; the one limit rule in the work that is reachable |
| 22 | Target-year layer: four annual flying stars, Dou Jun, Tian De / Yue De / Jie Shen, flying three slayers, flowing Lu/Yang/Tuo | all five tables transcribed and vector-covered | `source_gated` — every one is keyed to a target year, and this panel reads a birth rather than a year |
| 23 | Star meanings, palace judgments | 420 delineation and judgment cells encoded from juan 2's fourteen life-palace entries and eleven topic-palace chapters, juan 1's star question-and-answer chapter, and juan 3's limit chapters | `refused` — every cell is research evidence with per-cell output policy, **193 refused outright**, and none of it reaches the section |
| 24 | Facsimile collation | Ming Nanyangtang printing identified and pinned; OCR unusable; page images retrievable and one leaf spot-collated | `source_gated` — the one remaining acquisition |
| 25 | A dated worked nativity | none printed anywhere in the work | `refused` — the source does not contain one, and no facsimile will supply it |
| 26 | Merger with the Zhengtong Daozang homonym | different star names, different construction | `refused` |

**Rows 9–19 and 21 moved from `source_gated` to `implemented` on 2026-08-04**, and the
engine module was rewired the same day to consume them. The section now emits a real board:
the bureau with its two-step derivation shown, Zi Wei, Tian Fu, all fourteen main stars with
their brightness and their element/Dipper attributions, seventeen auxiliary tables, the
child-limit sequence, and juan 3's own order of judgment — and still not one word of
meaning.

## Judgment hierarchy

The tradition states its own order, in juan 3's opening chapter `谈星要论`, and the
composer must execute it in that order rather than inventing one:

0. **Check the voids first.** `禄马不落空亡天空截空最紧，旬空次之` — confirm the body and
   life palaces and Lu and Ma have not fallen into a void, Tian Kong and Jie Kong first,
   Xun Kong second.
1. **The life palace** — its benefics and malefics, its brightness, its transformations to
   Lu or Ji, and the generation-and-control relations there (`第一看命宫`).
2. **The body ruler** on the same terms (`次看身主`).
3. **The travel, wealth and office palaces** — the three that stand in aspect — for
   affliction, opposition and breakage (`三看迁移财帛官禄三方`).
4. **The fortune-and-virtue palace**, read against the wealth palace it faces
   (`四看福德宫…以福德宫对财帛宫也`).

Before any of that the chart must be built, and this repository's own gates apply in this
order:

- **Resolve the chart month across all three calendar regimes.** If they disagree, refuse
  the whole chart. A birth within a day or two of a new moon legitimately lands here.
- **Resolve the lunar day across all three regimes.** If they disagree, the bureau is not
  determined, and Zi Wei, Tian Fu and all fourteen main stars must stay unplaced *even
  though the tables now exist*. This is a real gate, not a leftover: the day genuinely
  moves between meridians for some births.
- Place the month palace, then life and body; then the twelve topics in reverse; then the
  bureau; then Zi Wei; then Tian Fu; then the two main-star series; then the auxiliaries.
- **Stop before the limits.** Every decade and annual rule in this work is sex-gated.

The chapter's closing paragraph sorts whole lives into upper, middle and lower grades and
ends at `六畜之命`, a beast's fate. The **order** is taken from this chapter. The **ranking
of persons is refused.**

## Worked-example inventory

| Source | Contains | Usable now |
|---|---|---|
| *An shen ming li*, three life/body examples | life and body for three birth hours | **yes, all three pass** |
| *An shen ming li*, intercalary-month-1 example | leap-month normalization | **yes** |
| *An shen ming li*, opening paragraph | **the whole bureau derivation**: Jia year → 丙 at Yin → 丙寅 → 炉中火 → 火六局 → look up the day | **yes** — the single most load-bearing worked example in the work |
| *An Wenchang Wenqu xing jue*, Zi and Chou hours | Wenchang/Wenqu | **yes, both pass** |
| *An Zuofu Youbi xing jue*, months 1 and 2 | Zuofu/Youbi | **yes, both pass** |
| Ten-stem Four Transformations verse, Jia row | transformation table | **yes** |
| Topic-palace reverse example from Zi | twelve topics | **yes** |
| Five bureau verses, ten stated day anchors | Zi Wei at days 1 and 2 in each bureau | **yes, 10 / 10 reproduced by the closed form** |
| Five bureau day-grids, sixty cells | Zi Wei for every lunar day | **58 / 60 reproduced**; the two failures are isolated single-character defects, located and documented |
| `安天府图` caption, 紫居丑则府居卯 | Tian Fu reflection | **yes** |
| `安擎羊陀罗二星诀`, 癸禄在子 | Qing Yang / Tuo Luo | **yes** |
| `天空地劫诀`, three hour cases | Kong / Jie, including the Wu-hour rejoin | **yes, all three** |
| `安流禄流羊流陀诀`, 己丑流年 | annual Lu/Yang/Tuo, and a second check on the natal Lu Cun row for Ji | **yes** |
| `安命主`, two cases | life ruler at Wu and at Zi | **yes** |
| **A dated nativity with a full worked chart** | — | **no such example exists in this work.** This remains the track's real worked-example gap, and no facsimile will supply it because the work does not print one |

Two cross-checks are engine-generated rather than source examples and are labelled as such:
the three-meridian calendar check, and the closed-form collation against the printed grids.

## Refusal list

- **No lifespan, death date or fatal-limit output.** `定男女竹萝三限` ends by instructing
  the reader to judge coinciding limits as a death limit; `论大限十年祸福` predicts death
  within a named year. Both are encoded and both are refused absolutely.
- **No child-mortality divination.** `论安命金锁铁蛇关` exists to tell whether a child will
  live or die, and names palaces meaning "ill but savable" and "dies". Refused absolutely,
  for any subject, at any age.
- **No medical prediction.** The entire `六疾厄` chapter — 23 cells — is refused at chapter
  level rather than line by line, because the chapter's whole subject is which organ fails.
- **No claims about relatives.** The sibling, children, spouse and parents chapters predict
  how many siblings a person has, whether their children survive, and whether they will
  harm a spouse. 87 of those cells are refused as third-party claims.
- **No gendered life-grading.** `定十二宫弱强` grades which palaces matter by sex;
  `女命骨髓赋` is a whole chapter scoring women on chastity, marital rank and widowhood;
  every star's `入女命吉凶诀` verse is of the same kind. All refused, encoded unexcerpted so
  the refusal names a real chapter rather than gesturing at one.
- **No moral or class verdict on a person.** `定富贵贫贱十等论` sorts lives into ten ranks;
  `谈星要论` ends at "a beast's fate". Refused.
- **No decade or annual limits.** Direction depends on a sex input this panel does not
  collect, and the audit requires a declared historical convention first regardless.
- **No main star placed when the lunar day is not invariant across calendar regimes.** The
  tables now exist; the input sometimes does not.
- **No merger with the Zhengtong Daozang homonym.**
- **No assertion of a single calendar meridian.**
- **No later-school table merged in** — not for the Four Transformations, and not for
  Huo/Ling, whose placement in this witness is keyed to the year branch alone where later
  schools key it to year branch *and* birth hour. That fork is recorded as `conflicts_with`.
- **No silent rectification.** Juan 3 warns that the Zi and Hai hours are hard to fix and
  that a compass may be needed. That is a caution to quote, not a licence to change a
  reported birth time.

Counted: **193 of 420 encoded delineation and judgment cells carry
`output_policy: "refused"`** with a stated reason and the trigger terms that fired it. A
further 540 cells are pure lookup-table entries — bureau rows, day-to-branch cells,
brightness cells, star attributions — which state a position rather than a judgment and
carry no policy flag.

## Conventions requiring disclosure

| Convention | Chosen | Note |
|---|---|---|
| Civil-to-lunisolar conversion | panel's validated true-new-moon / true-solar-term kernel under three meridians, gated on agreement | not a `ziwei_default` |
| Double-hour partition | BaZi sexagenary kernel's shichen boundary (Zi at 23:00) | juan 3 states the Zi hour straddles the day boundary and that its earlier quarters belong to the previous night's Hai, but prints no table; the engine follows a convention the source discusses and does not tabulate |
| Birth-year sui resolution | lunar-new-year convention primary, Li Chun cross-checked | disclosed as `LIVE` whenever the two disagree |
| Bureau derivation | Five Tigers ∘ nayin, as the chapter's own worked example composes them | the 10×12 grid is derived, not printed; always show the palace stem and the nayin phrase, never just the answer |
| Zi Wei day table | the printed grids are authoritative; the closed form is a derived convenience | where the two disagree (木三局 at Yin, 金四局 at Hai) the disagreement is disclosed, and the closed form is adopted because the verse anchors force it |
| 隔 / 空 in the main-star couplets | read as **exclusive** skips | not stated in the verse; fixed by the requirement that the six offsets close the circle at twelve, which they do on this reading and no other |
| Kui/Yue, Huo/Ling pair order | the order of the couplet | the couplets name a pair per stem-group without saying which member is which; flagged as a reading |
| Tian Shang / Tian Shi | the palace names, not the counted "six positions" | the passage contradicts itself; the counted form would put both stars in the same palace |
| Romanization | engine normalization | the pack retains Chinese characters throughout; romanization is never load-bearing |
| Rights / edition status | Wikisource transcription (CC BY-SA 4.0) of a public-domain work; Ming facsimile identified but not collated | not a controlling edition |

## Current implementation gap

The engine rewiring is **done**. `src/engine/multitradition/ziwei.py` now loads the wider
pack, reads every table out of it rather than restating any of them, and emits the board
behind the lunar-day gate. The panel test that asserted the old ceiling
(`test_ziwei_never_places_a_main_star_or_a_meaning`) has been replaced by
`test_ziwei_places_main_stars_only_when_the_lunar_day_is_invariant`, which asserts the new
one: fourteen stars exactly when the day survives all three meridians, and none at all when
it does not. All 158 multi-tradition panel tests pass.

What remains:

1. **Facsimile collation.** Locate the construction chapter among the Nanyangtang scan's
   266 leaves by page-image inspection and collate the five bureau grids, the Tian Fu
   diagram and the brightness table character by character — starting with the two cells
   where the transcription and the closed form disagree. This is what would move the
   construction rules from C to B.
2. **Independent Chinese review** of all 83 rules and a second encoder reproducing the
   extraction without seeing this pack.
3. **Render the 166 quoted-but-unrendered delineation cells.** They are quoted verbatim
   with locations and policy; 69 cells carry an English rendering and the remaining 166 are
   marked `rendering_status: "verbatim_quoted_rendering_outstanding"` rather than faked.
4. **A declared historical sex/gender convention and a safe modern input mapping**, which
   would unblock the twelve-stage cycle, the twelve gods, and the decade and small limits —
   all of which are otherwise fully transcribed and waiting.
5. **Segment the two marrow rhapsodies.** `斗数骨髓赋` and `女命骨髓赋` are currently held
   whole and refused whole; the first certainly contains quotable doctrine mixed with fatal
   judgment, and only a reviewer should cut it.
