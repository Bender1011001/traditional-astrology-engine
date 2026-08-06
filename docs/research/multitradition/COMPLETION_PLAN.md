# Completion plan: every tradition to practitioner standard

Written 2026-08-05. The goal set by the owner: **each tradition should produce a
chart as correct and complete as the best human practitioner of that tradition
would produce.** This document says what that means operationally, measures how
far each track is from it, and sequences the work.

It is written against measurements, not impressions. Every number below is
reproducible from the commands in the appendix.

---

## 1. What "as good as the best human" means here

A strong practitioner does five things. An engine that does four of them is not
90% of a reading; it is a different artifact. So the bar is stated as five
gates, and a track is only "complete" when all five pass.

| Gate | What it means | How we know it passed |
|---|---|---|
| **G1 Construction** | Every figure the tradition casts — chart, subcharts, lots, periods — computed under a named convention | The track's own worked examples reproduce |
| **G2 Weighing** | The tradition's own strength/priority apparatus, so competing testimonies can be ranked | The text's own arbiter rule executes (e.g. BPHS 2.44) |
| **G3 Judgment** | Sourced delineation for what the chart actually shows, in that tradition's voice | Rules fire on a real chart, not merely load |
| **G4 Synthesis** | The tradition's own order of judgment, producing a reading rather than a list | The mined judgment hierarchy drives section order |
| **G5 Honesty** | Forks disclosed, refusals held, unknowns not collapsed into false | Refusal and fork tests pass |

**The distinguishing failure this project has already hit twice** is passing G1
and G3 while failing G2 — a track that reads fluently and cannot weigh. Jyotisha
was in that state until 2026-08-05: thousands of delineation cells from four
authors and no Ṣaḍbala. A practitioner cannot work that way, and neither can a
report.

---

## 2. The four kinds of gap, which cost wildly different amounts

Sorting the remaining work by *kind* matters more than sorting it by tradition,
because the four kinds have different owners and different costs.

| Kind | Definition | Cost | Who can close it |
|---|---|---|---|
| **A. Wiring** | Rules mined, validated, on disk — and no engine reads them | Hours | Me, today |
| **B. Engine** | Computation the tradition needs that nothing computes yet | Days | Me |
| **C. Mining** | Source held, pages legible, nobody has read them | Days, agent-parallel | Me |
| **D. Acquisition** | Source not in the repository at all | Unknown; owner-dependent | Owner (fetch) then me |
| **E. Verification** | Rendered, and not yet checked against the source's own worked examples | Hours to days | Me — see below |

**The headline measurement: 452 rules sit in delineation manifests that no
engine reads.** Calculation manifests are excluded from that figure — they feed
the panel's arithmetic and correctly render nothing. What remains is category A:
the cheapest work in the project and the largest single block of unrealised
value.

Reproduce it with:

```bash
python scripts/audit_engine_coverage.py
```

Measured across 12 varied charts, rule reachability inside the built engines:

| Track | rules | ever reachable | coverage |
|---|---|---|---|
| al-Qabīsī | 86 | 34 | 40% |
| Hellenistic | 131 | 40 | 31% |
| Jyotisha | 295 | 46 | 16% |
| Jaimini | 116 | 18 | 16% |
| Zi Wei | 93 | 8 | 9% |
| BaZi | 55 | 10 | 18% |
| Sukuyōdō | 45 | 0 | 0% |

Low coverage is partly expected — a twelve-house table contributes one cell per
chart. But whole *manifests* at zero are not expected, and there are five of
them inside tracks that already have engines.

---

## 3. Phase 0 — wiring what is already paid for (category A)

This is the first work to do because it is the cheapest per unit of reading
delivered, and because every hour of mining spent before it compounds the
backlog.

| Item | Rules | What it adds |
|---|---|---|
| `jaimini/jaimini_rule_manifest.json` | 41 | A **second independent witness** on argala, kārakas, rāśi dṛṣṭi, daśā direction. Verified: zero id overlap with the technique manifest — this is corroboration, not duplication |
| `bazi/ziping_technique_rule_manifest.json` | 23 | Sānmìng Tōnghuì juan 3 technique, assembled from fragments and never wired. BaZi is the weakest report; this is most of its fix |
| `islamicate/qabisi_lots_rule_manifest.json` | 17 | The per-house named lots with their attributions — the engine currently casts 8 lots and the pack enumerates far more |
| `sukuyodo/sukuyo_rule_manifest.json` delineation cells | ~10 | Sukuyōdō fires **zero** delineations. The mansion natal clauses exist |
| `sukuyodo/japanese_reception_rule_manifest.json` | 13 | The Futian li / Senmyō reki reception layer, currently only quoted in prose |

**Exit test for Phase 0:** no manifest whose rules are delineations sits at zero
reachability. Add a test that asserts it, so this class cannot recur — it is the
same failure as ["loading is not firing"](../../../CLAUDE.md) and it has now
happened twice.

---

## 4. Phase 1 — the two engines that exist but under-deliver

### BaZi (currently 7 delineations, 1,070 words — the weakest built engine)

Failing **G2 and G3**. Its two central Zǐpíng judgments — 身強/身弱 (day-master
strength) and 用神 (the useful god) — are the whole of the tradition's weighing
layer, and both are source-gated. Without them a BaZi report is a list of
pillars.

- **Category A:** wire the 23 technique rules (Phase 0)
- **Category C:** mine Yuānhǎi Zǐpíng juan 1–2 and 4–12, **including juan 12's
  five worked charts** — those are the validation targets that would let strength
  classification be checked rather than asserted
- **Category B:** implement 通根 (root-in-branch), 十神 counting and the seasonal
   旺相休囚死 table, which are what strength is computed *from*

### Zi Wei (9% reachability)

Failing **G3 and G4**. The fourteen stars place correctly; almost nothing is said
about them.

- **Category B:** the auxiliary stars are positioned in the panel and not judged;
  and the chapter's **own first judgment step** — the void-check on 命/身/祿/馬 —
  is not implemented, so the report skips step 0 of its own hierarchy
- **Category A/C:** juan 2 holds a life-palace entry for every star; most cells
  are transcribed and unrendered
- **Category D:** the 7-juan facsimile is barely started

---

## 5. Phase 2 — Jyotisha to full practitioner depth

Jyotisha is the deepest track and the closest to the bar. It now passes G1, G2
and G5. It fails **G3 at scale**: 295 rules, 46 reachable.

The delineation layers are mined and unwired — this is category A at volume:

| Layer | Cells | State |
|---|---|---|
| Bhāveśa-in-bhāva (BPHS a15) | 132 of 144 | transcribed, partially wired |
| Graha-in-rāśi (Sāravalī) | 82 | mined, **not wired** |
| Graha-in-rāśi (Bṛhajjātaka) | 72 | mined, **not wired** |
| Graha-in-bhāva, second witness (Sāravalī a30) | 84 | mined, **not wired** |
| Graha-in-rāśi modified by aspecting graha (Sāravalī) | 296 | mined, **not wired**, needs no new computation |
| Moon-in-navāṃśa (Sāravalī a24) | 40 | mined, **not wired** |
| Daśā delineation (Sāravalī a40, BPHS a36) | — | mined, **not wired** |

Also outstanding:

- **The dṛṣṭi conflict, which is doctrinal and not code.** Three schemes are in
  play: the engine's flat special-aspect rule, adhyāya 4's quarter-grading, and
  uttara 2's continuous six-case arc function. The engine's is *the only one this
  recension does not teach anywhere*. One must be labelled `configured_method`.
  **This needs an owner decision, not more work.**
- **Six vargas unmined, not blocked** (D16, D20, D24, D27, D40, D45) — their
  ślokas sit in legible stretches of a scan already on disk. Reading them
  completes the daśavarga and ṣoḍaśavarga viṃśopaka schemes.
- **Recension collation** (category E): the saptavargaja series, the required
  minima, the Moon's pakṣa-bala and ayana-bala's placement all disagree with the
  modern handbooks. Until collated, no reading may say "BPHS says a graha is
  strong above N" — the current report is careful to name its recension, and that
  care must survive.

---

## 6. Phase 3 — the tracks with rules and no engine

351 rules. Ordered by reading-value per unit of work.

| Track | Rules | Kind | Note |
|---|---|---|---|
| **Vietnamese (Tử Vi)** | 54 | A+B, cheap | A Zi Wei variant. `ziwei_stars` already computes the fourteen; this is largely a different palace/star naming layer over machinery that exists. **Best value in the project right now.** |
| **Latin/Lilly** | 34 | B | Overlaps the live Western engine; Lilly's tables are already encoded in `reference_data.py`. Mostly a report, not a computation |
| **Byzantine (Rhetorius)** | 31 | B | Hellenistic-adjacent; can reuse sect/dignity/lot machinery |
| **Qizheng** | 27 | B | Shares the sexagenary and lunisolar kernels |
| **Egyptian** | 40 | B | Decans + civil calendar; the calendar manifest already computes |
| **Tibetan** | 15 | B | Phugpa calendar computes; White Beryl judgment layer thin |
| **Medieval Jewish** | 5 | B | Thin; a solar-return module exists |
| **Nahua / Maya** | 39 | B+D | Day-signs. **Correlation-dependent** — the Nahua correlation has a known one-day discrepancy already recorded. Needs the same invariance-gate treatment as Zi Wei's calendar |
| **Babylonian** | 106 | — | **Not a natal tradition.** Omen corpus, state-directed. It should NOT be forced into a natal report shape; it needs its own artifact (an omen-application demonstration). Categorising it as "a missing natal engine" would be a category error |

---

## 7. Phase 4 — the nine tracks with zero rules

Burmese, Khmer, Korean, Mon, Mongolian, Onmyōdō, pre-Islamic Arabian, Sinhalese,
Thai. Each has a `source_audit.md` and no `defensibility_spec.md`.

**These are category D and they are the owner's move, not mine.** The standing
project rule ([never-declare-source-ceilings]) is that no ceiling may be claimed
without a documented hunt — so the first deliverable here is a *search trail per
track*, not a verdict. Several of these are likely findable: Thai and Burmese
astrology have printed manuals; Onmyōdō overlaps Sukuyōdō sources already held.

Ordering: run the search pass, produce an acquisition list, hand it over, then
mine what arrives.

---

## 8. Sequence and rationale

```
Phase 0  wiring (category A)               ~1 session   biggest value/hour
Phase 1  BaZi + Zi Wei to depth            ~2 sessions  fixes the weakest reports
Phase 2  Jyotisha delineation at volume    ~2 sessions  largest corpus, closest to bar
Phase 3  Vietnamese, Latin, Byzantine,     ~4 sessions  new engines over shared machinery
         Qizheng, Egyptian, Tibetan,
         Jewish, Nahua/Maya
Phase 3b Babylonian as its own artifact    ~1 session   NOT a natal report
Phase 4  search pass on the nine empties   ~1 session   produces an acquisition list
```

Phase 0 first is not arbitrary: every session of mining before it increases the
unwired backlog, and the backlog is already 587 rules.

---

## 9. What this plan will not deliver, and should not

Three things stay out no matter how much work is done, and calling them "gaps"
would be wrong:

1. **Refused content.** Kadkhudāh years, longevity, the socially harsh clauses.
   The sources state them; the publication policy withholds them. That is a
   decision, not an incompleteness.
2. **Genuinely undecided doctrine.** Jaimini's seven-vs-eight kāraka scheme
   (*saptānāṃ aṣṭānāṃ vā*), the chara daśā length conventions, the Varṇada
   derivation its own transmitter cannot explain. A practitioner declares a
   school; the engine asks the caller to.
3. **Verification against worked examples.** Renderings are graded
   `engine_translation_unreviewed` and that grade is honest, but it is not a
   queue for a reviewer who does not exist. There is no specialist. The
   project's own standard (`DEFENSIBILITY.md`) settled this: translation is not
   a gate for quotation, because showing the original, the rendering and the
   citation together lets any future reader check the rendering — which is
   strictly more auditable than paraphrasing someone's copyrighted English.

   What upgrades confidence is criterion 4 of that standard: **reproduce the
   tradition's own worked examples.** That is a thing I can do and have been
   doing, and it is the strongest proof available:

   - Murakami Tennō's recorded birth mansion — reproduced exactly
   - al-Qabīsī's own worked figures — 6 of 6
   - BPHS's printed Ṣaḍbala arithmetic — uccha 38|04 through piṇḍa 9|41|14
   - Abhyankar's Patel chart, which discriminates the Rahu convention
   - the Tử Vi placement tables — 148 of 150, with the two exceptions being
     the defect the pack already documents
   - Zi Wei's five printed grids — every cell, plus all ten stated anchors

   Where a track has no worked example, say so — that is the real gap, and it
   is a mining target, not a hiring one.

A tradition can pass all five gates and still carry all three of these. That is
what a careful practitioner's reading looks like too.

---

## Appendix — reproducing the measurements

Every figure in this document comes from one command:

```bash
python scripts/audit_engine_coverage.py --charts 12
```

It exercises each report engine over varied nativities — spread across date,
clock, hemisphere and latitude, because sect, retrogradation and combustion all
gate rules and a single birth exercises one value of each — and reports which
mined rules ever reach a page.

A rule counts as REACHED if it renders on at least one chart. Calculation
manifests are listed separately, because a zero there is correct rather than a
finding.

The numbers move as work lands. Re-run rather than trusting the tables above.
