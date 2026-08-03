# Jyotisha defensibility spec

Status: governing spec for the Vedic reading section  
Updated: 2026-08-02  
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

This spec governs the Parasari (BPHS-descended) track. It is deliberately
distinct from the sign-based Jaimini track at `../jaimini/`, which has its own
defensibility spec and is not merged with this one.

The adversary here is a working Jyotishi. That reader will check for divisional
charts and dasha before anything else, and will notice immediately if the section
reasons like a Western chart wearing sidereal longitudes.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Sidereal longitudes under a named ayanamsa | India Calendar Reform Committee 1956 (registry: `jyotisha_india_calendar_reform_committee_1956`) fixes Lahiri as the civil standard | `implemented` (Lahiri, disclosed) |
| 2 | Lagna, its lord, and the lord's placement | Brhajjataka I; BPHS lagna chapters | `implemented` |
| 3 | Rasi (D1) placements with dignity | Brhajjataka II (encoded in `brhajjataka_planetary_rule_manifest.json`) | `implemented` |
| 4 | Nakshatra and pada for Moon, lagna, and each graha | Brhajjataka I.4-14 passages already passage-aligned | `implemented` |
| 5 | Whole-sign bhava assignment | classical default; Sripati is the live alternative | `implemented` (disclosed) |
| 6 | **Navamsha (D9)** | universally treated as mandatory; BPHS varga chapters | `implemented` (all grahas, nodes, lagna; vargottama flagged; D9 dignity separate) |
| 7 | Vimshottari mahadasha from janma nakshatra | BPHS dasha chapters; standard 120-year scheme | `implemented` |
| 8 | Vimshottari antardasha (bhukti) | same | `implemented` |
| 9 | Graha dignity: exaltation, debilitation, own sign, moolatrikona | Brhajjataka II | `implemented` (moolatrikona pending) |
| 10 | Friendship/enmity (naisargika and tatkalika) | BPHS relationship chapters | `implemented` (naisargika; tatkalika/panchadha not computed and disclosed) |
| 11 | Graha drishti (special aspects for Mars, Jupiter, Saturn) | BPHS aspect chapters | `implemented` |
| 12 | Yogas: Raja, Dhana, and yogakaraka identification | BPHS yoga chapters; Phaladeepika | `implemented` (with constituent facts, evaluated only after items 1-6) |
| 13 | Combustion (astangata) | BPHS | `implemented` |
| 14 | Shadbala | BPHS bala chapters | `source_gated` — recension-dependent weights |
| 15 | Ashtakavarga | BPHS | `source_gated` |
| 16 | Other vargas (D10 career, D7 children, etc.) | BPHS varga chapters | `source_gated` — which vargas are mandatory varies by school |
| 17 | Planet-in-bhava classical delineation text (as opposed to structural condition alone) | Phaladeepika Adhyaya VIII (`delineation_rule_manifest.json`) | `source_gated` — sourced and paraphrased for 8 of 9 grahas across all 12 houses (Saturn 11/12, Sun 5/12); translation rights unresolved, independent Sanskrit review pending, no composer wiring written |
| 18 | Named-yoga delineation text (Pancha Mahapurusha, Kesari/Sakata, Mahabhagya, Adhama/Sama/Varishtha, Sunapha/Anapha/Durudhara/Kemadruma, Vesi/Vaasi/Kartari, 4 Rajayogas, Neechabhanga Rajayoga) | Phaladeepika Adhyayas V-VII (`delineation_rule_manifest.json`) | `source_gated` — same translation-rights/review hold as #17; several sub-yogas additionally need house-from-Moon or house-from-Sun computation the engine does not yet perform |
| 19 | Vimshottari mahadasha classical significations (general, per graha) | Phaladeepika Adhyaya XIX (`delineation_rule_manifest.json`) | `source_gated` — same translation-rights/review hold as #17; antardasha-level significations not yet sourced |
| 20 | **Bhavesha-in-bhava delineation from the root text itself** (lord of each bhava, in each bhava) | BPHS Subodhini 1899 purva-khanda adhyaya 15 (`bphs_rule_manifest.json`) | `source_gated` — 132 of 144 cells transcribed from the Sanskrit and rendered; independent Sanskrit review outstanding before promotion, and no composer wiring written |
| 21 | Functional benefic/malefic/yogakaraka/maraka by lagna | BPHS Subodhini 1899 adhyaya 13 (`bphs_rule_manifest.json`) | `source_gated` — all 12 lagnas transcribed (Aries partial, page-image gap); this recension's assignments diverge from the modern handbooks and the divergence is unresolved |
| 22 | Graded drishti (pada/dvipada/tripada/purna per graha per house-offset) | BPHS Subodhini 1899 adhyaya 4, slokas 23-29 (`bphs_rule_manifest.json`) | `source_gated` — the root text grades every aspect on a four-step scale rather than the flat special-aspect rule item 11 implements; the two are in open conflict and the conflict is recorded, not resolved |
| 23 | Rasi drishti (sign-to-sign aspect) taught inside the Parasari root text | BPHS Subodhini 1899 adhyaya 4, slokas 2-18 (`bphs_rule_manifest.json`) | `source_gated` — the recension teaches it in the main chapter sequence, which weakens the corpus's own Parasari/Jaimini partition; needs a doctrinal decision, not code |
| 24 | Vimshottari mahadasha delineation from the root text, conditioned on the dasha lord's dignity | BPHS Subodhini 1899 adhyaya 36 (`bphs_rule_manifest.json`) | `source_gated` — utkrsta/papa couplets for all 9 grahas plus placement-conditioned expansions for 8 (Ketu absent); column-interleave in the scan limits clause order |
| 25 | Antardasha quality from divisional placement (drekkana, dvadasamsa, trimsamsa) | BPHS Subodhini 1899 adhyaya 37, slokas 2-7 (`bphs_rule_manifest.json`) | `source_gated` — five of the six tests need vargas the engine does not compute (item 16) |

Items 17-19 are new as of 2026-08-02 and were added rather than folded into
items 7, 8 or 12, because those items are about calculation (mahadasha/
antardasha arithmetic) or structural detection (yoga conditions, with no
catalogue or phala attached, by design - see `vedic.py`'s own docstring), while
17-19 are about the classical delineation TEXT for those same facts. None of
items 1-16 changed status: this pass's sourcing did not touch Shadbala,
Ashtakavarga, or other-varga material, so 14-16 remain exactly as they were.
Items 20-25 are new as of 2026-08-02 and come from the root text itself rather
than from Mantresvara. They are kept as separate rows, and in a separate
manifest (`bphs_rule_manifest.json`), because BPHS and Phaladeepika are
different authors of different dates: item 20's bhavesha grid and item 17's
graha-in-bhava grid answer different questions and are never merged into one
delineation. Items 22 and 23 are the uncomfortable ones - the root text
contradicts what this engine currently implements (item 11) and what this
corpus's own tradition partition assumes - and they are recorded as conflicts
rather than quietly dropped.

17-25 are marked `source_gated`, not `computable`, because a real hold remains
on each (translation rights, independent review) and because this pass wrote
no composer or engine code to consume them; `computable` is reserved for gaps
that are ours alone and immediately actionable, which per
`ceiling_report.py` this corpus's own tooling refuses to let stand unresolved.

**Item 6 is done** (2026-08-01), verified by four structural properties the
classical rule guarantees and now covered by a runnable worked example. It
immediately earned its place: in the Fairfield chart Saturn is neutral in D1
Pisces but **exalted in D9 Libra** — a D1-only verdict on Saturn would have been
wrong.

## Judgment hierarchy

The composer must execute in this order. Later steps may qualify earlier ones;
they may not silently replace them.

1. Lagna and lagna lord: sign, degree, nakshatra, placement, condition.
2. Moon: janma rasi and janma nakshatra — in Jyotisha the Moon outranks the Sun
   for personal significations.
3. Graha dignity and placement in D1, with retrogradation and combustion.
4. Bhava rulership: which graha owns which house, and where that owner sits.
5. Drishti: who aspects what, including the special aspects.
6. Navamsha cross-check: does D9 confirm or undercut the D1 verdict on each graha.
7. Yogas, evaluated only after 1-6 and only where their constituent conditions
   have actually been verified.
8. Dasha: current mahadasha and antardasha, read against the qualified natal
   structure — never as free-floating themes.

The root text's own statement of this order, now that it is readable, agrees
with step 4 and adds a qualifier the composer must carry: BPHS Subodhini 1899
adhyaya 15 sloka 100 - *balabalavivekena sarvesam phalam adiset*, "the result of
every one of them is to be declared by discrimination of strength and weakness"
- and adhyaya 36 sloka 92 restates it for dasha. Neither bhavesha grid may be
rendered unconditionally. This is the text making proportionality part of the
rule, not a commentator softening it, and a reading that quotes a bhavesha cell
flat has already departed from the source.

## Worked-example inventory

| Source | Location | Contains | Usable now |
|---|---|---|---|
| Brhajjataka, Aiyar 1905 translation | registry `jyotisha_varahamihira_brhajjataka_aiyar_1905_archive` | worked illustrations in the commentary | **inspected 2026-08-02**: keyword search of the full OCR found only abstract calculation walkthroughs ("suppose the Sun's longitude to be..."), no natal chart with real birth data and a stated verdict. Page-image (non-OCR) inspection still not attempted. |
| Saravali, Subrahmanya 1914 | registry `jyotisha_kalyanavarma_saravali_subrahmanya_1914_archive` | example applications | still needs page inspection; OCR remains too corrupted to read (mixed scripts, many misrecognitions) |
| Saravali, Nirnaya Sagar Press 1907 | registry `jyotisha_kalyanavarma_saravali_nirnayasagar_1907_archive` (new 2026-08-02) | full Sanskrit text, chapter structure, any worked example | **discovered 2026-08-02**: first Saravali witness with legible Devanagari OCR (291,940/366,411 characters proper Devanagari, 9 failure marks); text proper not yet read for content - this is now the priority Saravali lead, ahead of the 1914 witness |
| Phaladeepika, Subrahmanya 1950 | registry `jyotisha_mantreswara_phaladeepika_subrahmanya_1950_archive` | worked yoga examples | **inspected 2026-08-02**: Adhyayas V-VIII and XIX read directly; all are rule catalogs (now in `delineation_rule_manifest.json`), no worked chart found. Adhyayas IX-XVIII and XX-XXVIII not yet inspected. |
| BPHS Subodhini 1899 | registry `jyotisha_parasara_bphs_subodhini_1899_egangotri` (new 2026-08-02) | dasha and varga worked cases | **CORRECTED 2026-08-02**: the earlier "almost total `?` failure" verdict was wrong — the file has 100 question marks in 1,106,274 characters and 807,038 Devanagari codepoints, and reads. Worked material actually found: (a) adhyaya 37 sloka 1 gives the antardasha formula AND works it (Sun mahadasha 6 years, Sun antardasha within it 3 months 18 days) - directly checkable against the engine today, and the one BPHS claim in the pack needing no translation judgment; (b) adhyaya 36 slokas 8-10 work a Vimshottari balance from a stated Moon longitude; (c) adhyaya 28 slokas 44-48 name *natives* for the varga-dignity raja-yogas - Harishchandra, Bali, Yudhishthira, Shalivahana, Nagarjuna, "the Manus" - legendary and dynastic figures with no recoverable birth data, so inventory rather than test charts. |

Brhajjataka, Phaladeepika and BPHS have now each had at least one direct,
non-metadata inspection pass for worked-example content specifically. Brhajjataka
and Phaladeepika came back negative in the chapters inspected. BPHS came back
POSITIVE on the second pass, after the first pass's legibility verdict was found
to be false - which is the more useful lesson of the two: a "the scan is
unreadable" finding is a claim about the scan, and it has to be produced by
reading the scan, not by a character-frequency impression of it. The Saravali branch is the one where
this pass changed the picture from "corrupted" to "legible but unread" - that
reading pass is the next highest-value M3 task for this tradition.

## Refusal list

- **No lifespan claim.** Ayurdaya methods exist and are recension-dependent; the
  live Western report already demonstrates how badly length-of-life arithmetic
  behaves when branches disagree. Jyotisha ayurdaya is not asserted.
- **No muhurta or remedial prescription.** Gemstone, mantra, and ritual remedies
  are prescriptive advice, not historical delineation.
- **No caste, varna, or social-rank delineation** rendered as a claim about the
  reader, even where the sources state it. Retain in the audit trace with the
  suppression reason.
- **No marriage-compatibility verdict** (kuta/guna milan) in a natal reading; it
  requires a second chart and its own source treatment.
- **No claim depending on Shadbala or Ashtakavarga** until those are implemented
  with sourced weights.
- **No progeny, fertility, or childlessness claim** rendered about a living
  reader. Phaladeepika's planet-in-bhava and yoga material (Adhyayas V-VIII)
  routinely states progeny counts or "childless" outcomes as part of a house or
  yoga result; those clauses are retained in `delineation_rule_manifest.json`
  as historical testimony with an explicit suppression note, the same
  treatment this spec already gives varna/caste material, and are never
  rendered as a claim about the reader's own fertility.
- **No maraka, killing-agency, or timing-of-death claim.** BPHS Subodhini 1899
  adhyaya 13 assigns a killing graha to every lagna and adhyaya 23 is an entire
  chapter of maraka distinctions. All of it is transcribed in
  `bphs_rule_manifest.json` with `output_policy: "refused"`; none of it is
  rendered, in any form, including as a softened "difficult period". The text's
  own sloka 40 is a *restriction* - a graha does not kill in its own dasha and
  bhukti - and it is encoded alongside the killing clauses, because a pack that
  records only the accusations and drops the exemptions misrepresents the
  doctrine it claims to be preserving.
- **No destitution or imprisonment verdict.** BPHS adhyaya 31's daridra-yogas
  and bandhana-yogas are encoded and refused for the same reason as the death
  material. They are kept in the manifest rather than skipped so that adhyaya
  30's dhana-yogas are not published as if the text only ever promised wealth.
- **No third-party defamation.** The bhavesha grid of adhyaya 15 repeatedly
  states that the native's wife is a courtesan or unchaste, that his mother is
  an adulteress, that his father is a great thief, or that his wife or child
  will not live. Every such clause is transcribed in full under
  `restricted_by_house` with its reason and is never rendered. The publishable
  remainder of the same verse is rendered; the verse is not discarded whole.
- **No `mleccha`, `jati`, impotence (`kliba`) or bodily-incapacity clause**
  rendered about a reader - extending the caste refusal above to the specific
  vocabulary this recension actually uses.
- **No "you will be a king" predicate.** The varga-dignity raja-yoga ladder of
  adhyaya 28 grades a chart into Parijata / Uttama / Gopura / Simhasana /
  Airavata / Paravata; the tier NAME would be a defensible thing to report if
  the vargas were ever computed, and the emperor predicate attached to it is
  not.
- **No horoscope-of-women-chapter or issue-chapter material.** Phaladeepika
  Adhyayas XI-XII were located and deliberately not mined for rules; their
  subject matter is marriage/progeny outcome for the native and falls under
  the two refusals immediately above and below.

## Conventions requiring disclosure

| Convention | Chosen | Alternatives |
|---|---|---|
| Ayanamsa | Lahiri (Chitrapaksha) | Fagan-Bradley, Krishnamurti, Raman, True Citra, True Revati |
| Houses | Whole sign | Sripati, equal-from-degree |
| Nodes | Mean | True |
| Dasha year length | 365.2425 days | 360-day savana year; sidereal year |
| Moolatrikona boundaries | pending | vary slightly by text |
| BPHS recension | 1899 Subodhini (Mumbai), purva-khanda, self-titled *Brhatparasarahorasaramsa* | Sharma and Santhanam recensions differ substantially in chapter count, order and content; the 1899 preface itself claims 100 adhyayas in two khandas and claims first printing. Any BPHS quotation must name which recension it came from |
| Graha drishti weighting | flat special aspects (Mars 4/7/8, Jupiter 5/7/9, Saturn 3/7/10) | BPHS adhyaya 4 grades every graha's glance on all seven of the 3rd, 4th, 5th, 7th, 8th, 9th and 10th, in quarters. The engine implements the flat rule; the root text does not teach it |
| Node dignities | engine's current scheme | BPHS adhyaya 36 slokas 35-36 give Rahu exalted in Taurus, moolatrikona Cancer, owning Gemini, Sagittarius, Virgo and Pisces (Ketu exalted in Scorpio). Recorded, not adopted |
| Relative-house reckoning | house from the Lagna only | house from the Moon (chandra lagna) and house from the Sun are both classically used (Sunapha/Anapha/Durudhara/Kemadruma, Kesari/Sakata, Adhama/Sama/Varishtha, the Sun-relative Vesi/Vaasi cluster, and the kendra-from-Moon branch of Neechabhanga Rajayoga all require one or the other) but neither is computed by `vedic.py` today |

## Current implementation gap

The shipped panel section covers items 1-5, 7, and 9 (partially). To reach a
defendable reading it needs, in order: **navamsha (6)**, antardasha (8), drishti
(11), then yogas (12) gated on 10 and 13.

As of 2026-08-02, a delineation-content layer for items 17-19 exists in
`delineation_rule_manifest.json` (18 rules, sourced from Phaladeepika), and a
second, larger layer for items 20-25 exists in `bphs_rule_manifest.json` (107
rules, 342 validation vectors, sourced from BPHS itself). Neither is wired into
`vedic.py` or the composer.

The single largest change this pass makes is not a rule count. It is that
`src/engine/traditions/vedic_report.py` currently tells the reader, in its own
method notes, that *"Brhat Parasara Hora Sastra - the root text this system is
named for - is NOT the source of any delineation here. Its available scan is
unusable."* **The second half of that sentence is now false.** The scan is
usable; 107 rules were read out of it. The sentence must be rewritten before the
next reading ships, because as it stands it tells a Jyotishi something untrue
about why the root text is absent. The honest replacement is narrower: BPHS is
readable and encoded, but nothing from it is rendered yet, pending independent
Sanskrit review of the renderings and a composer wiring pass.

The remaining blockers, in order of how much they cost:

1. **Independent Sanskrit review.** Every one of the 107 renderings is graded
   `engine_translation_unreviewed`. Under `../DEFENSIBILITY.md` that is enough
   to *quote* from - original, rendering and citation are all published
   together - and not enough to *promote into a validated pack*. This is the
   gate, and it is a real one rather than a placeholder.
2. **Recension collation.** This recension is missing 12 of adhyaya 15's 144
   cells, and its adhyaya 13 lagna assignments disagree with the modern
   handbooks. Until it is collated verse-by-verse against the Sharma and
   Santhanam recensions, no reading may claim "BPHS says" without naming the
   recension - and this pack refuses to fill its own gaps from the others.
3. **Divisional charts (item 16).** Adhyaya 37's antardasha quality test and
   adhyaya 28's raja-yoga ladder both run on vargas beyond D9. Five of six
   bhukti tests and the entire raja-yoga ladder are unevaluable today.
4. **The drishti conflict (item 22).** The engine's flat special-aspect rule and
   the root text's graded scale cannot both be presented as Parasari. One of
   them has to be labelled a `configured_method` with the other named as its
   alternative.

Nothing in this pass changed the rendered panel. `customer_prediction` is false
on all 107 conclusions and no engine code reads the new manifest.
