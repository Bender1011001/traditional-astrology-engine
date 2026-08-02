# Tibetan astro-science (rtsis) defensibility spec

Status: governing spec for the Tibetan section — research stage; calendar and year-character
computable and implemented, elemental-divination layer access-established but not yet extractable
Updated: 2026-08-02
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

This track did not have a `defensibility_spec.md` before this pass, which made it invisible to
`ceiling_report.py` despite carrying real implemented work (the Phugpa calendar pack and the
`tibetan.py` year-character module). This file closes that gap and, separately, resolves the
single most consequential open question the track carried: whether `sMewa` and `sPar-kha` are
genuinely blocked on a missing or unlicensed source, or whether that was an unexamined assumption.

**They were an unexamined assumption, and it was false in the same shape as two other false
blockers this repository has already found and dissolved** (the 16th-century Nahuatl Florentine
Codex; CC-BY-SA Arabic/Latin texts). The controlling primary source — the *nag-rtsis* half of the
**White Beryl** (*bai DUr dkar po*) by Sangye Gyatso, plus his own companion clarification treatise
*bai DUr g.ya' sel* — is public domain, named, hash-pinned, and was retrieved in full this pass
(`sources/access_manifest.json`). What replaces the false "no sourced anchor" claim is a real but
different blocker: this specific 1972 photostat of a xylograph print could not be read to
sentence-level transcription confidence in a single pass. That is an evidentiary-quality gate, not
a rights gate, and the two must not be conflated going forward. See `source_audit.md`'s
2026-08-02 section for the full investigation.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Phugpa calendar: Tibetan month/day, intercalation, skipped/repeated dates, weekday, Losar | `phugpa_calendar_spec.json` + `phugpa_calendar_rule_manifest.json` (10 rules), reconstructing Janson's arXiv 1401.6285 formulas from the White Beryl's *skar-rtsis* half; validated against `phugpa_calendar_validation_vectors.json` (31 published Losar dates, all Table-7 leap months 2000-2020, the full 2012 skipped/repeated inventory, three epoch profiles, the standard-vs-Lochen `a2` fork) | `implemented` — calendar facts only, no institutional almanac concordance yet |
| 2 | Sexagenary year character: element, animal, polarity | `src/engine/multitradition/tibetan.py::year_character`, verified at two independent anchors (1027 CE = Female Fire Rabbit, first rabjung; 1984 CE = Male Wood Mouse) sharing the BaZi kernel's sexagenary cycle with Tibetan naming | `implemented` |
| 3 | Rabjung 60-year cycle number and position within cycle | `src/engine/multitradition/tibetan.py::build`, counted from 1027 CE | `implemented` |
| 4 | sMewa (nine numeric squares / magic-square cycle) construction | *bai DUr dkar po* vol. 2, *byung-rtsis*/*nag-rtsis* chapter block (file-pages 308-348, 443-611 of `bdrc-W30116`); source confirmed public domain and retrieved in full; one folio (308) directly visually confirmed as genuine legible prose | `source_gated` — reclassified from the prior implicit refusal; blocked on transcription legibility of this print, not on rights (see `whitebeyl_rule_manifest.json`) |
| 5 | sPar-kha (eight trigrams) construction and year/sex assignment | same chapter block, same source, same blocker | `source_gated` — same reclassification and same blocker as row 4 |
| 6 | Life-force squares (`srog`/`lus`/`dbang-thang`/`rlung-rta`) derived from the natal mewa | presumed to sit in the same chapter block per the tradition's own structure (Men-Tsee-Khang's curriculum lists these alongside sMewa/sPar-kha); not independently folio-located this pass | `source_gated` — same blocker class as rows 4-5, weaker locator confidence |
| 7 | Parkha-mewa compatibility and elemental-combination judgment tables | same presumption as row 6 | `source_gated` |
| 8 | Obstacle-year (`lo-skag`) arithmetic | `tibetan.py` previously refused this citing unfixed conventions; this pass did not independently verify whether it lives in the same chapter block | `source_gated` — carried over, not strengthened or weakened this pass |
| 9 | Institutional (Men-Tsee-Khang) almanac concordance for the Phugpa calendar pack | `mentseekhang_calendar_almanac` registry entry: commercial publication, not yet purchased/compared | `source_gated` — access is a purchase/licensing question, genuinely distinct from the White Beryl finding above |
| 10 | Any natal narrative, medical, deceased, or death-timing reading from mewa/parkha/life-force, even once construction rules exist | Men-Tsee-Khang's own cultural-safety gates (`source_audit.md` "Cultural and safety gates") | `refused` — policy refusal, independent of computability |
| 11 | Merger of Tibetan `byung-rtsis` with Sukuyodo, Onmyodo, or BaZi on the strength of a shared distant Chinese five-phase/Yijing-derived numerological root | `whitebeyl_rule_manifest.json` boundary rule; Men-Tsee-Khang's own `rGya-rTsis rNying-Ma` vs `gSar-Ma` internal taxonomy | `refused` — separation discipline, matching how Sukuyodo/Onmyodo are already kept apart in this repository despite a shared root |

Row 2 lands its formulas in "the Ascendant-like `Dus-'Byor`" and "day
boundary" of the year — the `configured_method` disclosed in `tibetan.py`
(BaZi Li Chun proxy for the year boundary, since a true Losar boundary needs
row 1's full month calculation) still applies and is repeated below.

## Judgment hierarchy

The tradition's own curriculum order (Men-Tsee-Khang's first-professional syllabus, cited in
`source_audit.md`) runs astronomy before elemental astrology before natal interpretation. This
track's composer, once one exists, must execute in that order and stop where the checklist stops:

1. **Resolve the Phugpa calendar month and day first.** Everything downstream — Losar, the year
   boundary, and (once unblocked) sMewa/sPar-kha's own year-keying — depends on it.
2. **Derive the sexagenary year character and rabjung position** from the resolved year. Disclose
   the BaZi-Li-Chun-proxy convention whenever the birth falls between the civil-year boundary and
   the true, not-yet-computed Losar boundary — the two can legitimately disagree.
3. **sMewa before sPar-kha.** Every source description this pass found (Men-Tsee-Khang's own
   curriculum list, and the chapter structure visually confirmed in the White Beryl) presents the
   nine-number square first and the eight-trigram assignment second; life-force and compatibility
   tables are consumers of both, not parallel to them.
4. **Do not compute rows 4-8 until they are legible.** A plausible-looking mewa or parkha number is
   indistinguishable from a wrong one, and this repository has already stated that principle for
   this exact track before this pass began (`tibetan.py`'s own refusal comment). This pass changed
   *why* they are blocked; it did not remove the block.
5. **Never let row 9 (institutional almanac purchase) block rows 4-8.** They are different
   documents with different blockers, and conflating them was part of the original error.

## Worked-example inventory

| Source | Contains | Usable now |
|---|---|---|
| Janson 2014, Tables 1, 7, 8, 9 | 31 published Losar dates, all 2000-2020 Phugpa leap months, the complete 2012 skipped/repeated-day inventory | **yes, all reproduced.** `phugpa_calendar_validation_vectors.json` |
| Two sexagenary anchor years (1027, 1984) | element/animal/polarity cross-check | **yes.** Encoded directly in `tibetan.py::year_character`'s own docstring and reproduced by its logic |
| White Beryl vol. 2, *byung-rtsis* chapter block (file-pages 308-348, 443-611) | presumably contains worked constructions of sMewa/sPar-kha for named years, as other classical corpora in this repository do | **no worked example reproduced this pass.** The one folio inspected (308) is continuous prose, not an isolated diagram; whether a dated worked example exists elsewhere in the ~60-page block is unknown until it is read |
| Men-Tsee-Khang first-professional curriculum exercises | official competency exercises for sMewa/sPar-kha calculation | **not retrieved** — curriculum names the competency, not the worked exercises themselves (`tibetan_mentseekhang_first_professional_curriculum_2023` registry entry) |
| A purchased Men-Tsee-Khang almanac | year-by-year mewa/parkha as published for a living audience | **not acquired** — a commercial-purchase gate, separate from the White Beryl access question this pass resolved |

The calendar pack's worked-example coverage is genuinely strong (31 Losar dates plus a full leap
and skipped/repeated inventory, all passing). The elemental layer has **zero** worked examples
reproduced, and that is the honest weak point of this track, stated first rather than buried.

## Refusal list

- **No sMewa or sPar-kha value for any birth, yet.** The source is real and accessible; the
  transcription is not yet reliable. Emitting a number here before the block clears would be
  indistinguishable, to a reader, from having invented it — which is precisely the failure this
  standard exists to prevent.
- **No life-force (`srog`/`lus`/`dbang-thang`/`rlung-rta`), obstacle-year, or compatibility
  judgment.** All are downstream of sMewa/sPar-kha and inherit their block; none was independently
  strengthened this pass either.
- **No natal narrative, medical, deceased, or death-timing content**, even after construction rules
  exist. This is a standing policy refusal from Men-Tsee-Khang's own stated cultural-safety gates,
  independent of what becomes computable.
- **No merger with Sukuyodo, Onmyodo, or BaZi.** All four ultimately touch a Chinese five-phase or
  Yijing-derived numerological substrate at some historical distance, but each is a separate
  corpus, separate transmission history, and separate technical vocabulary in this repository, and
  none may backfill another's gaps. See `whitebeyl_rule_manifest.json`'s boundary rule.
- **No use of the unsourced popular-web mewa/parkha arithmetic** found during this investigation
  (`tibastro.be/Parkha/ParkhaGeneral`, `kunjung.org/general-4`). Both state specific numeric
  procedures with zero citation to the White Beryl or any named scholarly source. Using them would
  reproduce exactly the "generic Tibetan astrology engine assembled from English popular books"
  failure this track's own `source_audit.md` already named as unacceptable before this pass began.
- **No institutional-almanac claim without purchase.** The Men-Tsee-Khang almanac series is a
  commercial living-tradition publication; nothing here is checked against it, and that gate is
  unrelated to the White Beryl finding above.
- **No silent completion of the Phugpa-vs-Tsurphu fork**, per the calendar pack's existing
  `forbidden_merges` contract — unchanged by this pass.

## Conventions requiring disclosure

| Convention | Chosen | Note |
|---|---|---|
| Year boundary for the sexagenary year character | BaZi Li Chun pillar-year proxy | Disclosed in `tibetan.py` as `CONFIGURED_METHOD`; the true Losar boundary requires the full Phugpa month calculation and typically falls weeks later, so a birth between the two boundaries may get the previous year's character |
| Sexagenary cycle basis | shared with the validated BaZi kernel, Tibetan naming applied | Verified at two independent anchors (1027, 1984), not asserted from a single source |
| White Beryl edition of record | 1972 New Delhi: T. Tsepal Taikhang reprint from the Lhasa blocks of Burmiok Athing (`bdrc-W30116`) | Public domain per Internet Archive/BDRC metadata; geoblocked inside the PRC only (`restrictedInChina`), which is a distribution policy, not a rights restriction |
| Companion text | *bai DUr g.ya' sel*, 18th-c. sde-dge redaction, 1976 facsimile (`bdrc-W1KG12689`) | Fully open access (`openAccess`), but confirmed **more** cursive and **less** legible than the White Beryl print at the same zoom — held as a future cross-check, not a shortcut |
| Translation/rendering status | none produced yet for the elemental layer | Any future rendering from these two sources is graded `engine_translation_unreviewed`, per this standard's own rule that translation is not a gate for quotation of a public-domain original |
| Text-locating method | PDF embedded-text-layer keyword search (unreliable OCR) used only to locate candidate pages, never as evidence of content | Every claim about what a page *says* rests on direct visual inspection of the rendered image, not the OCR; only one page (folio 308) has been so inspected |
| Rights framing | "no sourced anchor" (pre-2026-08-02) | Corrected to: source identified and public domain; blocked on transcription legibility, not rights |

## Current implementation gap

The calendar half of this track is in genuinely good shape: ten rules, ten compound validation
vectors, exact-rational arithmetic, two independently-anchored sexagenary checks, and a working
year-character module. None of that changed this pass.

The elemental half changed from "assumed blocked, not investigated" to "access proven, extraction
not yet done." Concretely, this pass:

- retrieved both volumes of the White Beryl and both volumes of its companion clarification
  treatise in full (4 PDFs, hash-pinned in `sources/access_manifest.json`);
- confirmed both are public domain, with only a China-specific distribution geoblock on one of the
  two works, and no restriction at all on the other;
- located a 20-page candidate chapter block for elemental astrology within the White Beryl's
  646-page second volume;
- directly visually confirmed one folio (308) as genuine, legible, on-topic Tibetan prose — not a
  missing, blank, or corrupted page;
- confirmed the automated OCR layer is unusable for both works, and that the companion text is
  *less* legible than the White Beryl itself, closing off both obvious shortcuts;
- explicitly identified and rejected two unsourced popular websites as a substitute source, naming
  them so a future pass does not rediscover and mistakenly promote them;
- wrote the boundary/provenance findings up as five rules in `whitebeyl_rule_manifest.json` with
  citations to the hash-pinned page images, and as reproducible vectors in
  `whitebeyl_validation_vectors.json` — none of which assert any mewa/parkha numeric content.

What would move it next, in order of leverage:

1. **Legible transcription of White Beryl vol. 2, file-pages 308-348 and 443-611** — either an
   expert Classical Tibetan paleographic pass over this specific 1972 print, or locating a modern
   computer-typeset reprint of the same chapters that would OCR and read far more reliably. Neither
   requires any new rights work; both are document/reading problems, not composer problems.
2. **Extraction of sMewa and sPar-kha construction rules** from whichever route clears step 1, with
   exact passage citations and `engine_translation_unreviewed` grading, following this repository's
   house style exactly (Byzantine's page-image method is the closest precedent).
3. **Independent Classical Tibetan review** of whatever is extracted, before any rule is promoted
   out of `research_only` — this standard's own bar for rule promotion, not a new requirement
   invented for this track.
4. **Locating the life-force and compatibility material** within the same chapter block, and only
   then reconsidering rows 6-7 of the checklist above.
5. **Purchasing Men-Tsee-Khang almanacs** to unblock row 9 — genuinely a different, commercial
   gate, and not a prerequisite for any of steps 1-4.

Nothing on the checklist above is `computable` in the sense of "the inputs exist and the remaining
work is purely composer work we are simply choosing not to do." Rows 4-8 are blocked on a document
problem (legible transcription) and a review problem (independent Tibetan reading), exactly the two
categories this standard's own template distinguishes from an engine gap.
