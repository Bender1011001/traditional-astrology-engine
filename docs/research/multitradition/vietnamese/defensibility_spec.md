# Vietnamese defensibility spec

Status: governing spec for the Vietnamese section — research stage, nothing shipped
Updated: 2026-08-04
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

## What this track is, and the correction that created it

Until 2026-08-04 this track was a **calendar track**. Its audit concluded, correctly, that
there is no defensible single "Vietnamese astrology" engine, and it built a bounded
modern-lunisolar rule pack. But its own capability map already listed `Tử Vi` chart
construction as `source_limited` for want of controlling editions, and nothing had been
done about it since.

That was a ceiling asserted without a hunt. **Tử Vi Đẩu Số is the dominant living
Vietnamese natal tradition** — the thing an ordinary Vietnamese person means by having
their chart read — and treating the track as calendar-only meant the corpus had a
Vietnamese calendar and no Vietnamese astrology.

The hunt was run. What came back is one Vietnamese-language delineation source covering
all twelve palaces, one openly licensed modern reception book with no technique in it, one
bibliographic record naming the edition that would unblock construction, and two
documented negative results from Hán-Nôm repositories. That is enough to build a real
delineation pack and not enough to build a chart. Both halves of that sentence are in the
checklist below.

## The distinction this track exists to hold

**Vietnamese Tử Vi is not the Chinese 紫微斗數全書, and it is not a translation of it.**
Both are valuable; conflating them is the failure mode. Every item in this track is
labelled with which it is.

The evidence that they are distinguishable, from the one witness in hand:

| Observation | Where |
|---|---|
| composed in Vietnamese **lục bát verse**, with Vietnamese star names throughout | the whole text |
| palace enumeration is the **exact reverse** of the Chinese order about the life palace | the twelve ordinal openings |
| ~104 of the Phúc Đức section's 133 lines are **ancestral-tomb geomancy** worked with Tử Vi stars | PTV_L0154-L0257 |
| **Tuần and Triệt** operate as named agents on palaces | PTV_L0118, L0176, L0489 |

The second and third are the load-bearing ones. The reversal is mechanically checkable
and has no counterexample. The tomb block is a whole technique — reading the siting and
orientation of ancestral graves out of a natal chart, with Thanh Long as the dragon water
on the left and Bạch Hổ as the tiger water on the right, `phân kim` set from the branch
characters, and an eighteen-entry table mapping Tử Vi stars onto five-phase categories
and landforms. That is not in the Chinese work's 福德 palace.

Both comparisons currently rest on general knowledge of the Quanshu rather than on a held
edition, and both rules say so. Pinning a Quanshu edition is the cheapest single
improvement available to this track.

## Core-technique checklist

Statuses are as the standard defines them. **Nothing here is `implemented`**: there is no
Vietnamese engine module and no composer section. Nothing is `computable` either, and the
reason is structural rather than procedural — see below.

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Twelve-palace chart construction from a birth (cung Mệnh from lunar month and hour, cung Thân, ngũ hành cục, placement of Tử Vi and the two series) | none held. The 1957 *Tử Vi Đẩu Số Tân Biên* opens with a `Lập thành` section that is exactly this, and it is not acquired | `source_gated` — the pack fails closed. Borrowing the Chinese procedure is forbidden by `vietnam.tuvi.no_chart_construction_in_this_witness` |
| 2 | Placement of Tuần and Triệt | no placement rule in any held source, though both operate in the phú | `source_gated` — the tradition's own distinctive pair, and this repository cannot place them |
| 3 | Per-palace, per-star delineation | the phú, all twelve palaces, read and encoded | `source_gated` — 49 delineation cells are encoded across five palaces, plus an 18-entry landform table with Vietnamese quoted verbatim; promotion needs a Vietnamese reviewer and, for several, a better witness than degraded OCR |
| 4 | The palace judgement **order** | the phú states its own order aloud, one to twelve | `source_gated` — the order is established for this witness; whether it is Vietnamese practice generally, or reflects placement rather than recitation, is not |
| 5 | Phúc Đức as ancestral-tomb geomancy | PTV_L0154-L0257 with its eighteen-entry landform table | `source_gated` — the largest single block of the witness and the strongest Vietnamese-distinctive finding; one witness is not a tradition |
| 6 | Timing by Thái Tuế and the annual cycle against period palaces | the `Đoán sinh tử` section states the mechanism | `source_gated` for the mechanism as description; the section's actual purpose is refused, see row 12 |
| 7 | The modern Vietnamese lunisolar calendar | the separate `calendar_rule_manifest.json`, five rules, grade D | `source_gated` — pending independent recomputation against a named ephemeris and Vietnamese almanacs |
| 8 | Historical royal-calendar conversion | Phạm & Lê 2021 maps the witnesses; no dated almanac concordance held | `source_gated` — no proleptic use of the modern calendar is permitted |
| 9 | A named Vietnamese school with a stated lineage | the phú names a 1968 printing and a traditional attribution; the bibliographic record names the 1957 edition | `source_gated` — a lineage is named, none is established |
| 10 | Reproduction of published Vietnamese worked charts | none held | `source_gated` — the audit asks for ten; there are zero, and there cannot be any until row 1 lands |
| 11 | Nôm-script manuscript witnesses | searched, not found | `source_gated` — documented negative results, not an untested absence |
| 12 | Lifespan, death-timing and death-on-the-road output | the phú states spans of 60, 70, 80-90 years and two `lộ tử` clauses | `refused` — recorded verbatim in the trace, never rendered |
| 13 | Illness and disability output | the whole Tật Ách palace is a star-to-ailment table, including blindness and madness | `refused` — the palace is refused entire; that the tradition has one may be described |
| 14 | Reproductive prediction | Tử Tức predicts the sex of the first child, the number of children, childlessness | `refused` |
| 15 | Sexual-conduct and morality judgements | `dâm dục` clauses in Mệnh, Phu Thê and Huynh Đệ | `refused` per cell, inside otherwise emittable palaces |
| 16 | A separate reading procedure for women | the appended `Số đàn bà, con gái` section, whose premise is that a woman of rank owes her position to her husband | `refused` — this cannot be operated even faithfully |
| 17 | Class judgements about servants | PTV_L0314-L0315 | `refused` per cell |
| 18 | Advice on graves, burial or siting | the Phúc Đức tomb block | `refused` — the block is described as what the source does; no siting advice is ever issued |
| 19 | Relabelling Chinese Ziwei Doushu output as Vietnamese | — | `refused` — `vietnam.boundary.vietnamese_tuvi_is_not_the_chinese_quanshu`; this track shares no source, rule or vector with `ziwei/` |
| 20 | Emending the unreadable third of the witness | PTV_L0548-L0778, photographs of the 1968 book | `refused` — left unemended and marked unusable, as the Sukuyōdō pack leaves its two corrupt 羅剎日 rows |

### Why nothing is `computable`

`computable` means the inputs exist and the remaining work is ours. Here the inputs do not
exist, and the gap is unusually clean: **this track has delineation without construction.**

The phú judges a chart it assumes is already built. It never says how to find the life
palace, the body palace, the ngũ hành cục, where Tử Vi goes, or where Tuần and Triệt fall.
So the pack holds 49 cells of judgement and cannot produce a single chart to apply them
to — the mirror image of the Sukuyōdō track, which holds a complete relational system and
cannot place the reader in it.

The temptation is obvious and is refused explicitly: this repository already has a working
`ziwei/` module. Running it and relabelling the output Vietnamese would produce something
that looked right and was wrong, because the Vietnamese schools are reported to disagree
with the Chinese and with each other on precisely the construction questions — the
starting palace, star totals, the placement of Hỏa and Linh, annual-limit method. Every
one of those is decided during construction. Borrowing would pick a side in a live dispute
and stamp it Vietnamese.

## Judgment hierarchy

From the witness, which is explicit about its own order:

1. **Mệnh first, judged by the star that guards it.** PTV_L0021-L0022 says so in as many
   words: *cứ sao thủ Mệnh đoán nên tính tình* — judge the disposition from the star
   occupying the life palace.
2. **Then Phụ Mẫu, then Phúc Đức.** This is where the Vietnamese order departs from the
   Chinese, which goes to siblings and spouse next. A composer running the Chinese order
   would be presenting another tradition's priorities under this one's name.
3. **Within a palace, the placement fork before the verdict.** The phú's standard device
   is a single couplet carrying both branches — `miếu`/`nhập miếu` against `hãm` — and
   the two branches routinely reverse the judgement outright. Flattening them into one
   sentence is the reliable tell.
4. **Phúc Đức carries two distinct readings** and they must not be merged: the longevity
   block (refused) and the tomb block (recorded, never advice).
5. **Timing last**, and never for death.

## Worked-example inventory

| Source | Contains | Usable now |
|---|---|---|
| the phú's twelve numbered openings | the tradition's own palace order, stated by ordinal | **yes.** The reversal against the Chinese order holds at every position with no counterexample. Vector `vietnam.tuvi.v.palace_order_reversal` |
| the Phúc Đức landform table | eighteen star-to-landform assignments | **yes** as an inventory. Vector `vietnam.tuvi.v.landform_table_entries` |
| the `Lập thành` section of the 1957 edition | the construction procedure | **no — not held.** This is the acquisition that turns the track from a delineation pack into a system |
| a published Vietnamese worked chart with its judgement | — | **no such example is in the corpus.** The audit asks for ten, including a leap-month birth and every double-hour boundary. There are zero, and there is no way to attempt one without row 1 |

The honest reading of this table: the track can currently prove things about its **text**
and nothing about its **practice**. That is a real but narrow result and it is not
described as more.

## Refusal list

- **No chart.** No Vietnamese Tử Vi chart is produced for anyone, and the Chinese
  procedure is not borrowed to produce one. The refusal is the deliverable.
- **No lifespan, no death timing.** The phú gives spans of sixty, seventy and eighty-to-
  ninety years and two clauses predicting death on the road, and the `Đoán sinh tử`
  section exists to warn a person of the year they may not survive. All of it stays in
  the trace and none of it reaches a reader.
- **No illness output.** The Tật Ách palace is a diagnosis table — blindness, madness,
  abdominal pain, skin disease. Refused entire. That the tradition has an illness palace
  is describable; no cell may be applied to a person.
- **No reproductive prediction.** The sex of a first child, the number of children,
  childlessness and adoption are all predicted in Tử Tức. None is emitted.
- **No sexual-morality judgement**, about the reader or their relatives — including the
  Huynh Đệ passage predicting that a sister runs off with a man and becomes pregnant.
- **No separate procedure for women.** The appended women's section is refused as
  discriminatory treatment. Operating it faithfully would still be operating it.
- **No class judgement**, including the servants couplet at PTV_L0314-L0315.
- **No advice on graves, burial or siting**, notwithstanding a hundred lines on the
  subject.
- **No financial advice** from the Tài Bạch palace, under the product's standing rule.
- **No relabelling.** A Chinese Quanshu rule may not be called Vietnamese, a Vietnamese
  rule may not be called generic East Asian, and the two may not be blended.
- **No emendation** of the unreadable photographic tail.

Refusing is not the same as deleting. Every refused clause is kept verbatim with its line
address, because a trace that quietly dropped them would misrepresent the source — which
is a different failure from the one being avoided.

## Conventions requiring disclosure

| Convention | Chosen | Note |
|---|---|---|
| Controlling witness | *Phú Tử Vi Lê Quí Đôn*, 2017 transcription | not a manuscript; the transcriber collated against a 1968 printing and supplied missing passages |
| Attribution | **traditional, not established** | the word "traditionally" is mandatory. The attribution is also the rights argument, and the pack rests nothing on it |
| Earliest dated witness actually held | 1968, and only at second hand | the pack may not describe itself as an eighteenth-century source |
| Text quality | OCR of a photocopy | Vietnamese quoted **verbatim as the OCR reads**, with a normalised reading and an English rendering beside it. Recurring defects recorded: `Tỉnh` for `tinh`, `Quyển` for `Quyền`, `Điển` for `Điền`, `Lỉnh` for `Linh` |
| Translation status | single unreviewed engine rendering | a Vietnamese reader has checked nothing yet |
| Coverage bound | PTV_L0001-L0547 | the remaining 231 lines are unrecoverable and are excluded, not guessed |
| Comparison with the Chinese work | from general knowledge | **no Quanshu edition is pinned.** Both comparative claims say so |
| Star name abbreviations | expanded by the reader | the verse abbreviates constantly — `Nhận` for Kình Dương, `Vỉ` for Tử Vi, `Phù` ambiguous between Tả Phù and Quan Phù. Several expansions are uncertain and are flagged |
| Relationship to `ziwei/` | none | no shared source, rule or vector, exactly as Sukuyōdō shares none with Onmyōdō |

## Current implementation gap

Total. **There is no Vietnamese engine module, no composer section and no rendered
output**, for either the calendar pack or this one.

What would move it, in order of leverage:

1. **The `Lập thành` section of *Tử Vi Đẩu Số Tân Biên* (Tín Đức Thư Xã, 1957),** or any
   Vietnamese edition carrying a complete `an sao` table. This single acquisition turns
   49 orphaned delineation cells into a system, and it is the only thing that can. It is
   named, dated and in copyright, so the path is licensing, not searching.
2. **A Vietnamese-language reviewer** for the rule extraction and every rendering. The
   pack currently rests on one non-native reading of degraded OCR.
3. **A pinned edition of the Chinese 紫微斗數全書**, so that the two comparative claims —
   the enumeration reversal and the absence of tomb geomancy in 福德 — rest on a held
   text. Cheap, and it converts the track's two best findings from asserted to shown.
4. **A clean copy of the 1968 printing**, to recover PTV_L0548-L0778.
5. **Vietnamese almanac series**, to promote the separate calendar pack out of grade D.

Items 1 and 4 are acquisition problems, item 2 is a review problem, item 3 is an hour's
work that has not been done. None is a composer problem, which is why no checklist row is
`computable`.
