# Multi-Tradition Astrology Engine Research

Status: active research foundation  
Started: 2026-07-31  
Product objective: one birth-data intake that produces independently calculated,
source-attributed readings from every supported tradition without silently mixing
their doctrines.

This directory is the evidence and design workspace for the new tradition
engines. It does not declare a tradition production-ready. A tradition becomes
production-ready only after its source, calculation, rule, validation, rights,
and cultural-review gates are all satisfied.

## Non-negotiable interpretation rule

No prose generator decides an astrological result. The engine must first emit a
deterministic trace containing:

1. normalized birth inputs and uncertainty;
2. tradition and explicitly selected school or recension;
3. calculated calendar or astronomical state;
4. every matched rule and its precise source location;
5. precedence, exceptions, and conflicting authorities;
6. the resulting judgment and its confidence/coverage status; and
7. publication limits, including the project's Historical Use Only restriction.

The prose layer may organize and explain that trace. It may not introduce a
placement, rule, prediction, remedy, or conclusion absent from the trace.

## Scope

The attached culture inventory is a discovery map, not an authority. Research
tracks are intentionally narrower than cultural labels:

| Track | First engines or corpora | Critical separation |
|---|---|---|
| Indian Jyotisha | Parashari-style natal, classical jataka, varga, yoga, dasha, transit, compatibility | Text/recension, ayanamsha, regional and school choices |
| Chinese | Ziping BaZi, then Zi Wei Dou Shu | BaZi is not Zi Wei; calculation conventions and reading schools must be versioned |
| Mesopotamian | Enuma Anu Enlil omen families, scholarly reports, late Babylonian horoscopes | State omen astrology is not late natal horoscopy |
| Islamicate/Persian | al-Biruni reference layer; author-scoped natal, interrogational, electional, mundane, conjunctional methods | Never collapse Mashallah, Abu Mashar, al-Qabisi, al-Kindi, Sahl, and later Latin transmissions |
| Tibetan | Phugpa and Tsurphu calendar kernels; Kar-tsi and Nak-tsi reading layers | Calendar version, lineage, and living-practice review |
| Maya | Tzolk'in/Chol Q'ij, Haab, Calendar Round, Long Count, codical almanacs | Ancient codices, colonial evidence, and living Maya daykeeping are distinct evidence layers |
| Nahua/Central Mexican | tonalpohualli, trecena, day/night lords, year-bearer traditions | Codex, region, language, and colonial-period variants |
| Pharaonic Egyptian | lucky/unlucky-day calendars, decans, star tables | Do not manufacture a native twelve-house natal system |
| Japanese | period-specific Onmyodo calendrics and divination | Imported Chinese structures and Japanese court/ritual adaptations must remain identifiable |
| Southeast Asian | Burmese, Thai/Lanna/Lue, Khmer, Sinhalese, Mon and related regional tracks | No generic Southeast Asian engine |
| Related regional descendants | Mongolian, Korean Saju, Vietnamese, medieval Jewish, pre-Islamic Arabian star calendars | Each is a separate research/implementation decision, not a cosmetic locale |

## What "every possible reading" means operationally

The application will maintain a coverage manifest. A technique is either:

- `production_verified`: calculations and rules pass all gates;
- `research_verified`: sources are inspected but implementation/validation is incomplete;
- `experimental`: available only with prominent limitations;
- `source_limited`: the surviving or accessible corpus cannot justify a complete reading;
- `not_implemented`: visible in the coverage manifest but never simulated.

"Every" means every enumerated, supported technique in the manifest is run. It
does not permit filling historical gaps with modern generic symbolism.

`engine_coverage_manifest.json` is now the authoritative fail-closed inventory,
validated by `engine_coverage_manifest.schema.json` and
`validate_engine_coverage.py`. Its first complete pass enumerates 20 tracks and
74 modules from the original culture map. Fifty-four modules can legitimately
accept birth data, but that does not mean they have reading engines. Current
module status is:

| Status | Modules | Meaning now |
|---|---:|---|
| `production_verified` | 0 | No non-Western module has passed every production gate. |
| `research_verified` | 18 | Sources and the stated bounded artifact/design are reproducible. |
| `experimental` | 0 | No unsupported prototype is being exposed as coverage. |
| `source_limited` | 53 | The accessible corpus does not yet justify the complete module. |
| `not_implemented` | 3 | The module is visible and deliberately not simulated. |

Only 11 of the 74 modules currently point to validated machine-readable
research artifacts. The remainder are source/design or discovery records. The
validator also proves that every rule manifest is represented in this coverage
map and that all 20 source-audit directories have a corresponding track.

## Shared research questions for every engine

### Identity and boundaries

- What is the exact tradition, period, region, school, lineage, text, recension,
  commentary, and modern practice being implemented?
- Is the technique natal, calendrical, omen-based, mundane, electional,
  interrogational, ritual, medical, agricultural, or political?
- Can it validly be driven by birth data, or does it require an observed omen,
  question time, present location, ruler/state context, or ritual initiation?

### Calculation

- Calendar: civil, lunar, lunisolar, ritual, era, leap-month/day, day-boundary,
  and year-boundary rules.
- Time: historical timezone, local mean/apparent solar time, longitude
  correction, daylight-saving history, sunrise/sunset boundary, and uncertain
  birth time.
- Astronomy: tropical/sidereal frame, ayanamsha, epoch, precession, Delta-T,
  visibility/phasis assumptions, planetary model, node convention, and
  ephemeris validity range.
- Coordinate semantics: geocentric/topocentric, ecliptic/equatorial/horizon,
  apparent/mean positions, and location dependency.
- Required tables, constants, cycles, and traditional approximations.

### Rules

- Atomic conditions and conclusions.
- Scope and exclusions.
- Rule ordering and precedence.
- Required combinations rather than isolated keyword meanings.
- Cancellation, mitigation, repetition, and contradiction.
- Timing activation.
- Textual variants and later commentary.
- Whether a rule is descriptive, predictive, ritual, or prescriptive.

### Validation

- Worked examples from the same source or school.
- Independent almanac, published chart, tablet, or practitioner calculation.
- Boundary fixtures immediately before/at/after calendar and astronomical
  transitions.
- Cross-implementation checks where independent software exists.
- Bilingual review of every customer-facing rule derived from a non-English
  primary text.
- False-friend checks preventing a familiar Western term from overwriting the
  source tradition's actual concept.

## Evidence grades

| Grade | Meaning | Customer use |
|---|---|---|
| A | Facsimile/critical text and translation inspected; precise passage; calculation independently reproduced | May be source-attributed within stated limits |
| B | Reliable edition/translation inspected; precise passage; original language not independently reviewed | May be attributed to the inspected translation |
| C | Scholarly secondary synthesis with explicit primary citations | Background or disclosed reconstruction only |
| D | Institutional overview, catalog metadata, or practitioner teaching | Discovery/validation lead, not sole authority for a classical rule |
| E | Commercial page, unsourced summary, social post, or AI-generated text | Never a rule authority |

## Production gates

A tradition cannot be labeled complete until all are true:

- [ ] scope and school/version manifest is frozen;
- [ ] source registry has rights and access status for every edition;
- [ ] source passages have stable IDs and precise locations;
- [ ] all computable rules use a versioned machine schema;
- [ ] calendar/astronomy kernel has golden and boundary vectors;
- [ ] precedence/conflict behavior is explicit and tested;
- [ ] at least two independent validation routes cover core calculations;
- [ ] sample readings retain full deterministic traces;
- [ ] bilingual/philological review is complete where required;
- [ ] living-tradition and cultural-context review is complete where required;
- [ ] medical, financial, fatalistic, coercive, and ritual outputs obey safety and Historical Use Only limits;
- [ ] coverage report lists omissions rather than hiding them;
- [ ] adversarial tests show that the prose layer cannot invent unsupported rules.

## Initial feasibility findings

1. **Indian Jyotisha is calculable but not a single configuration.** A
   machine-readable Sanskrit `Brhajjataka` exists at GRETIL, while the current
   project/Swiss Ephemeris path can support explicitly selected sidereal modes.
   BPHS must be edition/recension scoped rather than treated as an uncontested
   monolith. The first two `Brhajjataka` packs now preserve twenty-two
   passage-located calculation and condition rules, including mutually
   exclusive Hora/Drekkana variants, without manufacturing a single consensus
   setting or importing modern numerical shadbala.
2. **BaZi has a strong calendar kernel starting point.** The Hong Kong
   Observatory publishes the stem-branch cycle and precise solar-term data.
   Classical interpretation texts remain primarily Chinese-language and need
   edition plus translation review.
3. **Babylonian omen work has unusually strong digital philology, but natal
   rules are not simple placement meanings.** ORACC can provide transliterations
   and translations, but the omen series is fragmentary and variant. The first
   passage-level late-horoscope pack preserves four judgments from Rochberg Text
   10 and one record/computation target. Three judgments depend on unresolved
   planetary `KI` (`qaqqaru`, “place”), so they are explicitly barred from being
   generalized into planet-in-sign or conjunction meanings.
   A version-locked astronomy validator now reproduces all 58 non-lunar table
   positions in Texts 2-10 within 0.2151 degrees and identifies three lunar
   discrepancies without hiding them. One is a probable printed-date/prose-date
   conflict in Text 6(b); the others require time and Delta-T sensitivity work.
   A separate NASA/JPL Horizons request/parser path checks all 192 published
   positions. The original 67 have a same-TT maximum difference of 0.0008223
   degrees. The 125-position extension has a same-TT maximum of 0.0008398
   degrees; its same-UT maximum is 0.0148495 degrees for the Moon while
   Horizons-minus-Swiss Delta-T ranges from -41.945 to +90.342 seconds. These
   time-scale results are retained rather than hidden as implementation noise.
   Text 1 is now separately modeled as twelve surrounding astronomical and
   calendar events, not a natal chart. Its 15 longitude and 12 rise/set
   comparisons pass the exploratory reproduction gates, while a 24.484-day
    Saturn-station calendar conflict, the restored lunar datum, the damaged
    Mercury sign, and every atmospheric visibility verdict remain unresolved.
   A separate Neo-Assyrian state-omen branch now has a bounded SAA 8 pilot from
   reports 316 and 535: 24 passage units, 33 atomic rules, and 12 validation
   vectors preserve selector combinations, textual variants, damage,
   unresolved predicates, geographic assignments, and scholarly rhetoric.
   Every rule rejects birth input and customer prediction; this corpus cannot
   be folded into the natal product.
   A second bounded pilot compares the Late Babylonian IM 124485 witness of
   `Enuma Anu Enlil` Tablet 20 with the Neo-Assyrian VAT 9419 + VAT 11310
   fragment: 13 passage units, 17 witness-scoped rules, and 11 vectors. The
   editions demonstrate transposed directions, changed dates, unstable clause
   boundaries, and directly conflicting outcomes, so the engine must require a
   named witness/recension and abstain rather than synthesize them.
4. **The al-Biruni reference layer now has a bounded, passing research pack.**
   The complete Halle Arabic/English facing edition was located after visual
   inspection proved the local file was only an English astrology extract.
   Six facing-page pairs support 15 author/work-scoped rules and 13 compound
   vectors for structural firdaria order, sign/planet classifications, `halb`,
   and `hayyiz`; 288 fixed-planet condition combinations pass. Major firdaria
   durations, node periods, generic Islamicate inheritance, Arabic linguistic
   verification, customer interpretation, and live-engine use remain disabled.
5. **Tibetan calendar math is implementable only with version selection.** The
   available mathematical literature explicitly documents Phugpa/Tsurphu and
   other divergences, including days or months that can differ. An
   exact-rational Phugpa research pack now reproduces 31 published Losar dates,
   the 2000-2020 leap-month table, the full 2012 skipped/repeated-date table,
   three epoch profiles, and named formula-variant divergences. It remains a
   secondary reconstruction: institutional conformance, interpretation, and
   live-engine status are false pending almanac and Tibetan review.
6. **Maya calendar arithmetic now has a bounded, passing research pack.** The
   eight-rule, twelve-vector kernel reproduces Smithsonian and FAMSI anchors,
   Long Count/Wayeb boundaries, the 18,980-day Calendar Round, language-profile
   label alignment, and explicit 584283/584285 correlation sensitivity. It is
   calendar-only: `live_engine`, interpretation eligibility, and customer
   prediction all remain false. INAH and SLUB codex work and any living Chol
   Q'ij meanings still require page-level scholarship, permission, and review.
7. **Native Egyptian scope must remain constrained.** Museum and scholarly
   databases support hemerologies, decans, and astronomical tables; they do not
   justify a fabricated pharaonic natal horoscope.
8. **Thai, Burmese, and Khmer materials already disprove a generic Southeast
   Asian engine.** Thai/Lanna/Lue `Suriyayatra` formula families, Burmese and
   Arakanese calendar procedures, and Khmer integer ephemerides have related
   transmission histories but materially different constants, intercalation,
   epochs, day boundaries, and textual witnesses. Each must be versioned as a
   separate calculation and interpretation track.
9. **Sri Lankan material supports bounded, lineage-specific pilots.** The
   inspected 1905 `Daivajnakamadhenu` edition supplies a large technical map
   associated with a medieval Sri Lankan author, while university curricula,
   manuscript repositories, ethnography, and official New Year practice map
   later Sinhala transmission. A Sanskrit compilation is not automatically a
   complete account of living Sinhala practice, and Sri Lankan Tamil jyotisha
   is a separate language and source track.
10. **Mon astrology is presently source-limited.** Mon-associated collections
    demonstrably contain astrology, divination and horoscopology, but no
    complete Mon-language birth-reading procedure was verified in this pass.
    Language, script, repository location and ethnicity must be cataloged
    separately; Burmese or Thai procedures cannot be relabeled Mon.
11. **Korean Saju requires a Korean profile, not only translated Ziping.**
    Joseon calendar and Myeonggwahak witnesses, Korean Saju terminology and
    worked charts, `Tojeong Bigyeol`, marriage documents, and modern Korean
    school choices form distinct modules. Historical Korean civil-time changes
    are capable of changing the hour pillar and must be validated explicitly.
12. **Mongolian zurkhai is a family of calendar and divination lineages, not a
    generic natal chart.** A Mongolian-language seasonal electional manuscript,
    a major scholarly manual, Tibetan-language manuscripts used in Mongolia,
    and living Kalmyk evidence are now mapped. Calendar school, textual
    language, provenance and regional lineage must remain separate; no verified
    comprehensive birth-reading procedure has yet been established.
13. **Regional-language review remains a production gate.** The inspected Thai,
    Burmese, Khmer, Japanese and Sri Lankan material is sufficient to define
    bounded pilots, not to publish comprehensive customer rules. Mon,
    Mongolian, Vietnamese, and additional primary-text work remain open.
14. **Vietnamese calendrical calculation cannot be reduced to a Chinese date
    lookup.** Historical royal calendars varied by regime and region, while a
    modern worked calculation shows that local civil-day placement of New Moon
    and winter solstice can change month numbering. Vietnamese Tử Vi also
    reports school and transmission variants; it needs its own editions and
    validation charts.
15. **Zi Wei Dou Shu must be edition- and lineage-scoped.** The inspected
    `Quanshu` transcription exposes a substantial deterministic construction
    layer, but still requires facsimile collation. A different Daoist-canon
    work bears the same title and uses different stars and construction; it is
    permanently isolated from the later natal system.
16. **Medieval Jewish astrology is best entered through a named Ibn Ezra
    corpus, not a generic Jewish zodiac.** Critical editions preserve multiple
    Hebrew versions and distinct books for nativities, revolutions, elections,
    questions, critical days and world astrology. Arabic source ancestry,
    Ibn Ezra's own position and later French/Latin transmission must remain
    visible in every rule trace.
17. **Anwāʾ does not currently support a birth reading.** The evidence supports
    rain-star, seasonal, pastoral and agricultural reconstruction. Direct
    inscriptions, later philological compilations and the systematic
    twenty-eight lunar stations are different evidence layers; the later grid
    cannot be projected backward or turned into personality signs.

## Files

- `source_registry.json`: machine-readable discovery and verification ledger.
- `rule_manifest.schema.json`: JSON Schema for passage-located atomic rule
  manifests, including conditions, conclusions, conflicts, exceptions,
  evidence grade, publication limits and review status.
- `validation_vectors.schema.json`: shared schema for direct, derived,
  boundary, mutation, abstention and safety vectors.
- `validate_research_corpus.py`: fail-closed graph validator for source IDs,
  source packs, rule/vector schemas, global ID uniqueness, complete rule-vector
  coverage, the Babylonian corpus fixture and astronomy-count invariants, and
  the Maya, Nahua, BaZi, Phugpa, and al-Biruni pack-specific
  provenance/publication gates.
- `maya/calendar_kernel_spec.json`, `maya/calendar_rule_manifest.json`,
  `maya/calendar_validation_vectors.json`, and `maya/validate_maya_calendar.py`:
  bounded Maya calendar arithmetic, provenance, and validation with no
  divinatory interpretation or live routing.
- `tibetan/phugpa_calendar_spec.json`,
  `tibetan/phugpa_calendar_rule_manifest.json`,
  `tibetan/phugpa_calendar_validation_vectors.json`, and
  `tibetan/validate_phugpa_calendar.py`: exact-rational secondary Phugpa
  reconstruction with explicit lineage/variant boundaries and no
  institutional or interpretive claim.
- `islamicate/al_biruni_reference_condition_spec.json`,
  `islamicate/al_biruni_reference_condition_rule_manifest.json`,
  `islamicate/al_biruni_reference_condition_validation_vectors.json`, and
  `islamicate/validate_al_biruni_reference_conditions.py`: author/work/edition-
  scoped firdaria and condition facts, facing-page provenance, exhaustive
  logical invariants, and fail-closed translation/publication boundaries.
- `nahua/tonalpohualli_cycle_spec.json`, `nahua/calendar_rule_manifest.json`,
  `nahua/calendar_validation_vectors.json`, and
  `nahua/validate_tonalpohualli_cycle.py`: a research-only 13-by-20 cycle
  kernel with all 260 pairs and twenty trecena heads validated. It has no
  default civil-date epoch, rejects cross-tradition correlations, and emits no
  divinatory or customer-facing output.
- `bazi/sexagenary_kernel_spec.json`, `bazi/sexagenary_rule_manifest.json`,
  `bazi/sexagenary_validation_vectors.json`, and
  `bazi/validate_sexagenary_kernel.py`: a research-only stem/branch kernel with
  the observatory-attested sixty-pair cycle, shichen partition, and month/hour
  stem lookup tables validated exhaustively. It has no day-count anchor, no
  year/month/day/hour boundary convention, and emits no five-element tally,
  Ten-God relation, luck pillar, or reading; every boundary-dependent request
  fails closed pending named concordance and school-convention profiles.
- `egyptian/civil_calendar_spec.json`,
  `egyptian/civil_calendar_rule_manifest.json`,
  `egyptian/civil_calendar_validation_vectors.json`, and
  `egyptian/validate_civil_calendar.py`: a research-only 365-position civil-year
  bijection for three four-month seasons plus five `heriu-renpet` days. It has
  no default chronology, rejects later Coptic/Alexandrian leap profiles, and
  emits neither hemerology nor birth-reading output.
- `egyptian/budge_sallier_iv_access_manifest.json` and
  `egyptian/validate_budge_sallier_access.py`: a hash-pinned institutional scan
  of Budge's 1923 second series with 41 Sallier IV facsimile plates
  (LXXXVIII-CXXVIII). It records the opening/final losses and corrects the
  epagomenal boundary: the likely section is lost, so non-preservation must not
  be presented as proof that the historical calendar had no prognosis. This is
  source access only; rule extraction, readings, and customer output remain off.

Run the integrity gate from the repository root:

```powershell
python docs/research/multitradition/validate_research_corpus.py
```
- `engine_research_spec.md`: shared data contract, research outputs, tests, and
  per-tradition technique inventory.
- `historical_time_contract.md`: shared civil-time, historical-calendar,
  astronomical-timescale, uncertainty, and cache-identity contract.
- `babylonian/saa8_lunar_eclipse_pilot_corpus.json`, the two associated rule
  manifests, and `saa8_lunar_eclipse_validation_vectors.json`: a hash-locked,
  passage-located state-omen pilot that is explicitly ineligible for birth
  readings and customer prediction.
- `babylonian/eae20_canonical_witness_pilot_corpus.json`,
  `eae20_witness_rule_manifest.json`, and
  `eae20_witness_validation_vectors.json`: a hash-locked comparison of two
  Tablet 20 witnesses that preserves recension conflicts and forbids both
  witness blending and natal/customer use.
- `babylonian/eae15_22_edition_inventory.json` maps the controlling 1988
  edition, the three later Fincke update articles, their actual access status,
  and two open ancient commentaries. `eae16_21_commentary_corpus.json`,
  `eae16_21_commentary_rule_manifest.json`, and
  `eae16_21_commentary_validation_vectors.json` encode 21 passage units, 22
  commentary-specific rules, and 14 vectors. Commentary restrictions,
  alternatives, wordplay, and manuscript-error rationalizations never
  overwrite the base omen text.
- Current source audits: `jyotisha/`, `bazi/`, `babylonian/`, `islamicate/`,
  `tibetan/`, `maya/`, `nahua/`, `egyptian/`, `onmyodo/`, `thai/`, `burmese/`,
  `khmer/`, `sinhalese/`, `mon/`, `korean/`, `mongolian/`, `vietnamese/`,
  `ziwei/`, `medieval_jewish/`, and `pre_islamic_arabian/`.
- Each tradition directory will grow from its audit into source manifests,
  passage extracts, calculation specifications, rule tables, golden vectors,
  and unresolved questions.
- `medieval_jewish/rule_manifest.json` is the first schema-validated extraction
  pack. Its five Ibn Ezra annual-revolution rules now have eight dependency,
  boundary and precedence vectors in `medieval_jewish/validation_vectors.json`;
  they are research evidence, not a claim that the engine or full corpus is
  complete.
- `ziwei/calculation_rule_manifest.json` contains seven lower-grade,
  facsimile-pending construction candidates; `ziwei/validation_vectors.json`
  preserves eleven explicit and derived examples without promoting the transcription to a
  controlling edition.
- `vietnamese/calendar_rule_manifest.json` formalizes five modern calendar
  candidates, and `vietnamese/calendar_validation_vectors.json` ties five
  published examples to them as recomputation targets, not accepted golden
  truth.
- `jyotisha/brhajjataka_calculation_rule_manifest.json` and
  `jyotisha/brhajjataka_planetary_rule_manifest.json` contain twenty-two
  grade-B, research-only Chapters I-II rules aligned between stable GRETIL
  Sanskrit verse IDs and Aiyar's 1905 English translation. Their 75 validation
  targets include explicit examples, exact division boundaries, complete
  lookup rows and negative controls. The half-open boundary convention,
  Sanskrit review, facsimile collation, unresolved Mercury and `samagama`
  semantics, astronomy dependencies, and translation rights remain gates;
  these are not an implemented or customer-eligible Jyotisha engine.
- `babylonian/rochberg_text10_rule_manifest.json` and
  `rochberg_texts2_5_9_judgment_rule_manifest.json` now encode all sixteen
  explicit judgment clauses found in Texts 1-10: four from Text 10 and twelve
  from Texts 2, 5 and 9. Their thirteen vectors preserve damaged/restored
  premises, unknown technical triggers, mutation behavior and consumer safety.
  Only the Text 10 lunar-latitude clause has a candidate computational premise;
  none is executable from a modern birth input. Assyriological review, full
  corpus parallels, `KI`/house-scheme reconstruction and commercial rights
  remain gates.
- `babylonian/rochberg_texts1_10_corpus_manifest.json`, validated by
  `horoscope_corpus.schema.json`, maps the first ten numbered tablets and all
  eleven births they contain. It distinguishes preserved text, damage,
  editorial restoration and inference; records sixteen explicit judgment
  clauses; and excludes fragmentary records from the primary golden set. This
  is an edition-level corpus fixture, not proof that the astronomy or judgment
  triggers are implemented.
- `babylonian/rochberg_texts1_10_astronomy_spec.json` and
  `validate_rochberg_astronomy.py` provide a version-, file-hash-, calendar-,
  Delta-T-, tidal-acceleration-, and return-flag-locked reproduction of 67
  edition-table positions. The exploratory thresholds are not final golden
  tolerances, and the Moshier comparison is cross-model evidence through the
  same library rather than a second implementation.
- `babylonian/rochberg_text1_event_spec.json` and
  `validate_rochberg_text1_events.py` reconstruct Text 1's twelve non-natal
  event records. They reproduce 15 longitude and 12 rise/set comparisons,
  independently solve the Jupiter and Saturn stations, separate the schematic
  solstice date from the tropical crossing, and generate no visibility or
  birth-chart verdict where the source and calendar do not justify one.
- `babylonian/jpl_horizons_crosscheck_spec.json`,
  `babylonian/jpl_horizons_texts11_27_crosscheck_spec.json`, and
  `validate_horizons_crosscheck.py` independently query and parse the official
  NASA/JPL Horizons API. They separate same-UT-label from same-TT-instant
  agreement, preserve the outer-planet barycenter limitation, and treat the
  two live results covering all 192 positions as versioned exploratory
  snapshots rather than golden oracles. The extension's tighter drift gates are
  labeled post-hoc and cannot serve as prospective production tolerances.
- `babylonian/rochberg_full_corpus_catalog.json` transcribes the complete edition
  catalogue: 28 numbered horoscope texts yielding 31 record entries because
  Texts 6, 16, and 22 each contain two records, plus four birth-note tablets
  preserving six births. Text 11 is the sole explicit duplicate link, leaving
  30 catalogued horoscope entries under that collapse. Text 28 may originally
  have contained more than one horoscope, so 30 is not a unique-nativity claim.
  Catalogue event-year and
  Seleucid-year index layers remain separate where they differ.
- `babylonian/rochberg_cdli_concordance.json` joins 30 of the 32 numbered
  tablets to exact current CDLI records. Every accepted page cites the matching
  Rochberg number; Texts 11 and 16 remain explicitly unresolved because searches
  for W 20030/143 and W 20030/10 returned no exact CDLI record. Identifier
  matching is not treated as image or sign-level collation. Of the 30 matched
  pages, 29 show no image and none supplies in-page text; only Text 27 exposes a
  photo thumbnail, which was hash-verified and visually inspected without
  asserting new sign readings.
- `babylonian/rochberg_texts11_20_corpus_manifest.json` adds eleven records from
  ten numbered texts after inspection of book pp. 86-115 / PDF pp. 102-131.
  `rochberg_text16_judgment_rule_manifest.json` encodes the only three candidate
  favorable/good-fortune clauses in this range. All have unresolved or damaged
  predicates, all six validation vectors fail closed, and none is eligible for
  customer output.
- `babylonian/rochberg_texts21_28_corpus_manifest.json` completes passage-level
  inspection of the horoscope section. Nine records on eight tablets preserve
  date intervals, restorations, almanac dependencies, and multiple explicit
  text/computation conflicts. Text 27 contributes two fortune fragments, but
  `rochberg_text27_judgment_rule_manifest.json` and five vectors prove that no
  astronomical protasis or customer-executable rule is recoverable.
- `babylonian/rochberg_birth_notes29_32_manifest.json`, validated by its own
  schema, records six births on four tablets. Text 32 contains three distinct
  births; later dates in Texts 29 and 31 are not miscounted as births. The full
  graph now contains 160 sources, 18 rule manifests, 184 rules, 17 vector files,
  and 224 vectors with complete coverage. The totals include separate Maya,
  Nahua cycle-only, Egyptian civil-calendar-only, and Phugpa calendar packs plus
  an author-scoped al-Biruni reference-condition pack; none is a live reading
  engine.
- `islamicate/abu_mashar_al_qabisi_access_matrix.json` pins seven exact
  University of Wurzburg TEI witnesses for Abu Ma'shar's *Great Introduction*,
  his distinct *Abbreviation*, and al-Qabisi's *Introduction*. Arabic and each
  Latin translation lineage remain separate. The files are passage-addressable
  and CC BY-SA, but the inspected corpus does not include the modern English
  translations or full apparatus, so the access validator passes while rule
  extraction and customer output remain false.
- `islamicate/al_biruni_abu_mashar_al_qabisi_candidate_concordance.json`
  resolves 30 candidate passages across five comparison concepts and preserves
  eight translation, arithmetic, terminology, and scope variants. It detects
  conflicting firdaria numbers/totals, non-transliterating Latin terminology,
  and an author-scoped Mercury classification difference. These are apparatus
  review targets, not normalized rules; the validator fails if the concordance
  becomes rule-ready, live, or customer-eligible.
- `babylonian/rochberg_texts11_27_astronomy_spec.json` independently reproduces
  125 published longitude targets across 18 tables under the same hash- and
  version-locked DE431/Moshier profile as the earlier corpus. It passes with 112
  targets inside exploratory body tolerances and preserves all thirteen failures.
  The largest planetary residual is Text 18 Saturn at 2.1036 degrees. Text 23's
  printed January 6 table behaves like a one-day label conflict: its Moon is
  14.2624 degrees away at the printed instant, while the named January 5
  diagnostic reduces that residual to 0.8514 degrees. These are research
  findings, not reasons to rewrite the edition silently.

## Current limitations and failed access

The bundled Archive.org discovery script's `search` command returned the same
API rewrite error for focused and narrow searches on 2026-07-31:

`New and legacy rewrite both failed with errors: [REWRITE FAILED] Could not rewrite querystring (query is not valid so cannot be rewritten); unknown error`

No candidates from those failed responses were promoted. A direct request to
Archive.org's official advanced-search JSON endpoint subsequently succeeded;
the candidate identifiers were then passed through the skill's `details` and
`text` commands. The registry records the resulting metadata, OCR quality, and
rights uncertainty. The helper's discovery path remains defective, but its
item-level verification path is usable.

The indexed Haripunjaya chronology article at ThaiScience returned an HTML
analytics shell rather than the promised PDF. It remains an `access_failed`
lead; no claim from its search snippet was promoted. The EAP1432 methodology
report also remains `search_metadata_only` pending successful full-text access.
The KASI historical-standard-time PDF timed out as well; Korean offset and
daylight-saving boundary fixtures therefore remain gated on institutional and
legal-source acquisition.
The NLM Mongolian-manuscript article returned HTTP 429 on direct open, so its
curatorial description remains `search_metadata_only` pending repository
access.
The Gunma University Okazaki PDF could not be opened, the VJOL Dang-family
calendar article was blocked by unavailable robots metadata, and the CTCW
Daoist-canon transcription timed out. No snippet or failed-response claim was
promoted from those endpoints.
The University of Arizona anwāʾ dissertation handle did not open, the
Al-Qantara article timed out, and the Varisco volume publisher page returned
HTTP 403. Their metadata and abstracts remain discovery evidence only; no
unseen passage was promoted.
