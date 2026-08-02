# Qizheng Siyu (七政四餘) defensibility spec

Status: governing spec for the Qizheng Siyu section — research stage, nothing shipped
Updated: 2026-08-02
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

**This is the first pass on a tradition that had zero files in this repository
before it.** The adversary is a practitioner of 七政四餘 specifically — someone
who will ask, before anything else, "which recension of Guo Lao are you
quoting, and does your Rahu/Ketu convention match what a working
fate-calculator actually uses?" This spec is built so that question has an
honest answer even where the honest answer is "not yet confirmed."

## What this tradition actually does

A Qizheng Siyu reading casts the seven visible classical bodies (Sun, Moon,
Mercury, Venus, Mars, Jupiter, Saturn) at their real ecliptic positions,
together with four calculated invisible points — 羅睺 (Rahu), 計都 (Ketu),
紫氣 (Ziqi), 月孛 (Yuebei) — into a twelve-sign zodiac and a Western-style
twelve-house chart. It is the one Chinese tradition in this repository that
uses a zodiac-and-houses structure at all, reflecting a real, textually
demonstrable transmission of Hellenistic- and Indian-derived astronomy along
Tang-dynasty trade and Buddhist-translation routes — not a modern gloss
imposed on Chinese material. This pass proves that transmission from the
primary text itself (see the T1308 rules below) rather than asserting it.

The four surplus bodies are **not epistemically uniform**, and a defensible
reading must say so: Rahu is a real geometric point (a lunar node), Yuebei is
a real physical point (the lunar apogee), and Ziqi has, per the best evidence
located in this pass, **no identified real astronomical referent at all** —
it appears to be a calendrical bookkeeping construct given a planetary
personality. Collapsing these three into "four planets" without disclosure
would misrepresent the tradition's own material.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Rahu's identity, names, and eclipse function | T1308 (Taishō T21 no. 1308), juan 2, T21.0442b-d, read directly and hash-verified | `implemented` in research corpus — names, eclipse-trigger conditions, and the text's own Indian-vs-Han eclipse-theory comparison are encoded |
| 2 | Rahu's motion rate and cycle arithmetic | T1308, T21.0442d-0443b | `implemented` in research corpus — every stated rate is encoded and independently recomputed; a small (~1/3 degree) internal inconsistency in the source's own 18-year figure is recorded rather than smoothed |
| 3 | Ketu's identity, names, and motion direction | T1308, T21.0446b-c | `implemented` in research corpus — names including the Yuebei-cognate 月勃力, and the explicit prograde-vs-Rahu's-retrograde contrast |
| 4 | Ketu's motion rate and cycle arithmetic | T1308, T21.0446c-d | `implemented` in research corpus — both the 9-year and 62-year/7-revolution figures close exactly against the stated annual rate, with zero rounding slack |
| 5 | Whether T1308's Ketu is the mature system's Yuebei or its Ketu | encoder's inference from rows 3-4, T1308 | `implemented` in research corpus as a labeled inference, not asserted as a source claim — see the boundary rule and its `conflicts_with` discipline |
| 6 | Rahu/Ketu's later paired-node redefinition (Tang-Song, then Qing) | zh.wikipedia synthesis citing 陳于柱 2009; no primary Song or Qing text retrieved | `source_gated` — the claim is real and named, but the underlying academic and primary sources were not independently retrieved in this pass |
| 7 | Ziqi's period and its no-real-referent status | zh.wikipedia synthesis; 28-vs-29-year disagreement recorded, not resolved | `source_gated` — same access gap as row 6 |
| 8 | The twelve-palace scheme's earliest attested form | T1308, T21.0427c-0428a | `implemented` in research corpus — twelve palace names, nine centuries before the mature system, with the one drifted name (palace 12) flagged rather than silently reconciled |
| 9 | The mature system's twelve-palace names and select named patterns (格) | ctext.org transcription of 張果星宗, juan 2 table of contents and one worked pattern | `implemented` in research corpus for the one pattern encoded (身命合格); the fifty-plus-entry pattern catalogue is not exhaustively extracted |
| 10 | Judgment hierarchy: seven governors outrank four surplus as a class | ctext.org transcription | `implemented` in research corpus |
| 11 | Judgment hierarchy: directional asymmetry of affliction between the two classes | ctext.org transcription | `implemented` in research corpus |
| 12 | Four surplus bodies' solitary-versus-mixed delineation preference | ctext.org transcription, independently corroborated in 星命溯源 juan 1 | `implemented` in research corpus, cross-witness corroborated |
| 13 | Four surplus bodies' elemental-affinity naming scheme | ctext.org transcription | `implemented` in research corpus, explicitly labeled as mnemonic/didactic, not computational |
| 14 | Twelve-branch planetary rulership (domicile) scheme | modern web secondary sources only; matches the Hellenistic domicile table exactly under the standard branch-zodiac correlation | `source_gated` — the highest-value unconfirmed finding in this pass; no primary Qizheng Siyu text located stating it directly |
| 15 | Worked-example charts (命例) for real historical figures | ctext.org transcription (4 figures) and 星命溯源 (2 of the 4, cross-corroborated) | `source_gated` — the delineation fragments and, for two figures, their claimed historical outcomes are located and encoded; structured birth data (year/month/day/double-hour) for none of the four figures was located in this pass, so none is machine-checkable yet |
| 16 | Sign and house placement rules for the seven governors from computed ecliptic longitude | not located in any source read in this pass | `source_gated` — this is likely present in the fuller ctext.org or 星命溯源 text this pass did not exhaustively read, not absent from the tradition |
| 17 | Limit-period / directed-year timing technique (限運) | referenced in worked-example fragments (酉限, 五十二歲酉限昴日) but its computation rule not located | `source_gated` |
| 18 | 命主/度主 (palace-lord versus degree-lord) distinction referenced in 星命溯源 juan 2 | 星命溯源 juan 2 names the distinction as operative but this pass did not extract its computation rule | `source_gated` |
| 19 | A reproducible worked chart computed from real birth data and checked against the source's own stated judgment | none of the four located worked examples currently has structured birth data | `source_gated` — see the worked-example inventory below; this is the track's single most consequential gap |
| 20 | Personality/character delineation from a surplus body in isolation | ctext.org transcription (row 12/13) | `refused` for any living customer; retained as historical/documentary quotation of what the source says a solitary Yuebei, Rahu, or Ziqi placement signifies |
| 21 | Death, lifespan, or violent-outcome prediction for a living person | the two worked examples that check against real historical deaths (張巡, 安祿山) are retrospective, about named historical figures already dead for over 1,200 years | `refused` for any living customer; the historical retrospective delineations are retained and labeled as such |
| 22 | Any claim about a person's rank, fortune, or nobility from a named pattern (格) | ctext.org transcription, row 9 | `refused` as customer output; retained as historical quotation of the pattern's stated meaning |
| 23 | Merger with BaZi or Zi Wei Dou Shu material | structurally distinct systems, see the boundary rule | `refused` — no rule, table, or worked example crosses between qizheng/, bazi/, and ziwei/ |
| 24 | Merger of the two identified Guo Lao Xing Zong print traditions (1593 Ming vs. later compiled edition) | both survive as unusable OCR in this pass | `refused` — neither is used as a controlling edition for any rule, and neither's content is backfilled into the other |

Nothing on this checklist is `computable`. Every remaining gap is blocked on a
named document (rows 6, 7, 14-19), a named access-quality problem (the two
Internet Archive print editions), or is a standing product refusal (rows
20-24) — never on unclaimed engine work.

## Judgment hierarchy

The clearest hierarchy statement located in this pass is a **class-level**
one, not a step-by-step protocol like the byzantine track's seven
inspections. The composer, when this track eventually has one, executes in
this order:

1. **Class before individual body.** The seven governors are judged first and
   rank as the chart's primary dignities ("gentlemen," 君子); the four
   surplus bodies are secondary, auxiliary factors ("mere surplus qi,"
   餘氣耳) — never co-equal chart rulers with the seven governors.
2. **Direction of affliction between classes matters more than which body is
   "stronger."** A governor afflicting a surplus body is the tradition's own
   tolerable case; a surplus body afflicting a governor is its own stated
   worst case ("will certainly bring great misfortune and harm"). A composer
   that treats both directions as symmetric has missed a source-stated rule.
3. **Solitary versus combined placement of the surplus bodies changes their
   reading.** The tradition states this explicitly and independently in two
   witnesses (ctext.org's transcription and the Siku Quanshu's 星命溯源):
   the four surplus class is "best taken singly; it fears being mixed
   together." A composer must check for this before delineating a
   surplus-body combination the same way it would a single placement.
4. **Named patterns (格) are judged as configured wholes**, not accumulated
   point-by-point — the one pattern encoded in this pass (身命合格) states a
   compound condition (lord stars harmonious, mutually generating, and
   dignified) yielding one compound judgment (wealth or nobility), not three
   separate additive facts.
5. **A worked example's own claimed historical check outranks a generic
   delineation.** Where the source itself states that a chart matches a real,
   named historical outcome (as with 張巡 and 安祿山), that check is the
   strongest available evidence for the technique and should be surfaced
   ahead of an unchecked generic reading, once the birth data gap is closed.

Two things are explicitly **not yet part of this hierarchy** because they are
not yet located: a step-by-step natal inspection protocol comparable to the
byzantine track's seven inspections, and the precise placement/dignity rules
(廟旺陷弱) that would let sign and house placement itself be judged in a
stated order. Their absence from this section is an honest gap, not a claim
that the tradition lacks such a protocol — the byzantine track's own
experience is that such protocols exist and are simply not yet retrieved.

## Worked-example inventory

| Source | Contains | Usable now |
|---|---|---|
| ctext.org 張果星宗 transcription | four delineation fragments for real Tang figures: 王勃, 楊國忠, 張巡, 安祿山 | **partially.** Delineation text and, for two figures, a claimed historical outcome are located and encoded. No structured birth data (year/month/day/double-hour) was located for any of the four |
| 星命溯源 (Siku Quanshu), juan 2 | independently corroborates the 王勃 and 楊國忠 fragments, with matching chart details | **partially**, same limitation — corroboration strengthens confidence the fragments are genuine rather than transcription artifacts, but does not itself supply birth data |
| 張巡's delineation | claims he "did indeed die at [An] Lushan's soldiers' hands" | the claimed outcome **is independently checkable against real history**: Zhang Xun died in 757 CE defending Suiyang during the An Lushan rebellion, matching the claim exactly. This is the strongest circumstantial evidence in this pass that the tradition's worked examples are not free invention |
| 安祿山's delineation | claims that "at age 52... he did indeed that year scheme to depose and enthrone [himself]" | likewise independently checkable: An Lushan proclaimed the Yan dynasty and declared himself emperor in 755 CE, matching the claim |
| A dated nativity with full structured birth data reproduced end-to-end from the source | — | **no such example was located in this pass.** This is the track's real, honest worked-example gap |

**Result: two of four located worked examples check against real,
independently documented history; zero of four are currently machine-
checkable end-to-end.** This is a genuinely better starting position than
several other tracks in this repository (compare the byzantine track's "zero
worked examples reproducible today"), and it is stated with equal honesty:
having the right delineation-to-history match without the birth data that
would let an engine reproduce it independently is real evidence, not a
finished vector. The route to a real worked example runs through a fuller
read of the same two texts already identified, not through new source
discovery.

## Refusal list

- **No death, lifespan, or violent-outcome prediction for a living person.**
  The two worked examples with real historical checks (張巡, 安祿山) concern
  named historical figures who have been dead for over 1,200 years; their
  retrospective delineations are retained and labeled as historical
  quotation, never repurposed as a template for predicting a living person's
  death or downfall.
- **No character/personality claim rendered to a customer from a solitary
  surplus-body placement.** The source's own statements ("Yuebei alone makes
  a person stingy," "Rahu alone confers a greedy disposition") are quoted as
  historical source content with their citations and are not applied to a
  person.
- **No rank, wealth, or nobility claim from a named pattern (格).** The one
  pattern encoded (身命合格, "if not wealthy then noble") is preserved as a
  quotation of the source's own stated judgment for that configuration, never
  rendered as a claim about a customer.
- **No silent choice of Rahu/Ketu convention.** Given the documented
  three-era redefinition history (even though not yet primary-verified),
  this pack refuses to let an implementation silently apply the modern
  Western/Jyotisha node convention to a Qizheng Siyu chart. Any Rahu/Ketu
  assignment must be a disclosed `configured_method` naming its alternative.
- **No presentation of the four surplus bodies as epistemically uniform.**
  Rahu (a real node), Yuebei (the real lunar apogee), and Ziqi (no identified
  real referent) are not interchangeable "four planets," and a reading must
  disclose this difference rather than flatten it.
- **No merger of T1308's Ketu with the mature system's Ketu.** T1308's Ketu is
  treated, by this pack's own labeled inference, as the ancestor of the
  mature system's *Yuebei* — not of the mature system's own Ketu, which later
  sources describe as a nodal point paired with Rahu. The two are kept in
  separate `school_id` spaces and never cross-cited as if identical.
- **No merger of the two identified Guo Lao Xing Zong print traditions.** The
  1593 Ming Nanjing Dawentang print and the later compiled edition (with its
  1926-era 量天尺 apparatus) are different witnesses separated by roughly
  330 years; neither is used to fill a gap in the other.
- **No merger with BaZi or Zi Wei Dou Shu.** Qizheng Siyu is the only one of
  the three Chinese traditions in this repository that casts real or
  astronomically-derived celestial positions into a zodiac-and-houses
  structure; BaZi uses no celestial positions at all and Zi Wei uses a star
  catalogue with no real celestial positions. No rule, table, or worked
  example is shared across the three tracks.
- **No presentation of the twelve-branch planetary rulership scheme as
  source-confirmed.** It is currently sourced from modern web secondary
  material only, however exact its structural match to the Hellenistic
  domicile table. It is disclosed as unconfirmed-in-primary-text pending the
  next pass, not asserted as established doctrine.

## Conventions requiring disclosure

| Convention | Chosen | Note |
|---|---|---|
| Rahu/Ketu node assignment | not chosen in this pack — recorded as an open, disclosed question | the tradition's own history (as reported by secondary synthesis) has changed this assignment at least twice; the modern practicing convention is reported to be the mirror image of the Western/Jyotisha convention, but this is not yet primary-verified |
| Ziqi's period | not chosen — 28 years and 29 years are both reported, disagreeing, in modern sources | no primary-text figure was located in this pass to adjudicate between them |
| T1308-Ketu-to-mature-Yuebei identity | treated as the same referent across two names, as a labeled encoder inference | never presented as a claim the sources make about themselves |
| Twelve-branch planetary rulership | not asserted as confirmed doctrine | matches the Hellenistic domicile table exactly under the standard branch-zodiac correlation, but rests on secondary web sources only in this pass |
| Text of record for the mature system | the ctext.org wiki transcription | base facsimile and collation history unidentified, exactly the situation the ziwei/ track already documents for its own comparable transcription; graded D accordingly |
| Translation | engine's own, from the Classical Chinese | graded `engine_translation_unreviewed` throughout; Chinese is shown beside every rendering so a specialist can check it |
| Twelve-palace name for position 12 | not resolved between 困窮 (T1308, 9th c.) and 相貌 (mature system) | recorded as a documented drift, not silently reconciled |
| Rights: T1308 | CBETA non-commercial condition, inherited unchanged from the sukuyodo/ track's own hash-pinned copy of the identical file | not assumed public domain for customer-facing reuse |
| Rights: the 1593 Ming print | HathiTrust public-domain determination, printed on the scan itself | among the cleanest public-domain determinations in this project |
| Rights: 星命溯源 (Siku Quanshu) | public domain (1781 imperial compilation) | Wikisource-marked; no facsimile page image independently retrieved in this pass |

## Current implementation gap

There is no Qizheng Siyu engine module and no Qizheng Siyu code — this pass
built the source foundation only. It produced 27 rules and 32 validation
vectors across a nine-luminary primary Buddhist-astronomical text (already
hash-pinned in this repository under a different tradition's folder and
independently re-verified here), an anonymous mature-system transcription, a
named 1593 Ming print edition (access-blocked by OCR quality, not by rights),
a separate later compiled print edition, the Siku Quanshu's own imperial
redaction of the tradition, and secondary scholarly synthesis on two
still-unconfirmed points.

What that buys, concretely: Rahu and Ketu's earliest attested identities and
motion arithmetic are not reconstructions, they are direct readings of a
hash-verified primary text, with the arithmetic independently recomputed and
its internal inconsistencies disclosed rather than smoothed; the tradition's
own class-level judgment hierarchy (seven governors over four surplus,
directional affliction asymmetry, solitary-versus-mixed delineation) is
encoded from its own stated language and cross-witness corroborated in one
case; the twelve-palace scheme is shown to predate the mature system by
centuries, with continuity and drift both documented; and two of four
located worked examples check against real, independently verifiable
Tang-dynasty history.

What it does not buy: any sign/house placement computation from a real
ecliptic longitude, any limit-period (限運) timing computation, any
machine-checkable worked chart, and confirmation in a primary text of either
the later Rahu/Ketu redefinition history or the twelve-branch planetary
rulership scheme — the last of which, if confirmed, would be one of the
strongest single findings in this entire multi-tradition project.

The next four moves, in order of value:

1. **A full read-through of the ctext.org 張果星宗 transcription's remaining
   juan (3-6) and 星命溯源's juan 3-5.** This pass performed targeted passage
   searches, not an exhaustive read; the twelve-branch rulership scheme and
   the four worked examples' birth data are the two highest-value things a
   full read-through would plausibly surface.
2. **Page-image reading of the 1593 Ming print's JP2 scans**, at minimum for
   the four-surplus definitional chapter and the worked-example chapter, to
   convert a bibliographically-confirmed-but-textually-inert source into a
   citable one — the same move the byzantine track used to unlock CCAG
   material behind poor OCR.
3. **Direct retrieval of 陳于柱 (2009) and 譚冰 (2013)**, the two named
   academic sources behind the Rahu/Ketu three-era redefinition claim, to
   convert it from secondary-sourced to independently verified.
4. **Independent Classical Chinese review** of all 27 encoded rules, plus a
   second passage-to-predicate encoder, before anything here reaches
   `research_verified`. Until that review and the birth-data gap above are
   both closed, `publication_status` stays `research_only`.
