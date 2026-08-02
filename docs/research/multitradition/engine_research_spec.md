# Multi-Tradition Engine Research Specification

This specification defines what research must deliver before implementation.
It deliberately stops short of prescribing one universal astrological model.

The current global implementation boundary is machine-readable in
`engine_coverage_manifest.json`. That file, rather than directory counts or a
green aggregate validator alone, controls claims about which traditions and
techniques exist. Its schema and validator require every named module to expose
its input kind, birth-input eligibility, evidence state, current coverage
status, concrete artifacts, and remaining gates. Missing techniques must remain
visible as `source_limited` or `not_implemented`; they may not be inferred from
an adjacent tradition or a shared calculation kernel.

## 1. Canonical birth input

The shared intake must preserve the user's statement and the normalized values:

```text
name (optional)
recorded local date
recorded local time (optional)
time precision: exact | rounded | approximate | unknown
calendar as recorded
place name as recorded
latitude/longitude and confidence
IANA timezone and historical UTC offset
timezone ambiguity/nonexistent-time resolution
UTC instant or interval
local mean solar time
local apparent solar time (when an engine requires it)
Julian Day variants used by each engine
calendar-conversion provenance
```

Never overwrite the recorded value with a normalized value. An uncertain time
is an interval propagated through every technique, not a fake noon chart.

## 2. Tradition configuration

Every engine invocation must carry a versioned configuration:

```json
{
  "tradition_id": "string",
  "engine_version": "semver",
  "school_id": "string",
  "source_pack_id": "string",
  "calendar_profile_id": "string",
  "astronomy_profile_id": "string",
  "rule_pack_ids": ["string"],
  "language_profile_id": "string"
}
```

Defaults are product decisions and must be visible in the reading. No silent
"standard Vedic" or "standard Chinese" profile is allowed.

## 3. Calculation trace

Each kernel returns typed facts only. Minimum fact fields:

```json
{
  "fact_id": "stable-id",
  "kind": "placement-or-calendar-state",
  "value": {},
  "input_dependencies": ["birth.utc_interval"],
  "algorithm_id": "versioned-id",
  "source_ids": ["source-id"],
  "uncertainty": {},
  "warnings": []
}
```

## 4. Rule representation

The research corpus must be representable without prose matching:

```json
{
  "rule_id": "tradition.work.location.rule",
  "tradition_id": "string",
  "school_id": "string-or-null",
  "period": "string",
  "domain": "natal|timing|omen|calendar|compatibility|other",
  "scope": {},
  "conditions": {},
  "conclusion": {},
  "priority": null,
  "exceptions": [],
  "conflicts_with": [],
  "source_passages": [],
  "evidence_grade": "A|B|C|D|E",
  "publication_limit": "string",
  "review_status": "string"
}
```

The schema must support conjunctive conditions, nested alternatives, thresholds,
cycles, intervals, directionality, repetition, cancellation, and source
variants. Numeric weights are prohibited unless the source specifies them or a
clearly labeled project policy derives them.

## 5. Judgment trace

A judgment contains:

- admitted and rejected rules;
- why each rule matched or failed;
- precedence and conflict resolution;
- conclusions supported by multiple independent rules;
- conclusions weakened by uncertainty or missing birth time;
- source coverage percentage by technique family;
- explicit unsupported questions;
- safe publication rendering.

## 6. Initial technique inventory

The lists below are research checklists, not claims that all techniques are
already sufficiently documented.

### Indian Jyotisha

- astronomical/calendar profile and ayanamsha;
- graha, rashi, bhava, lagna, nakshatra and pada;
- dignity/relationship/condition systems;
- divisional charts and exact varga boundary conventions;
- house/sign lordship and functional role conventions;
- yogas with full conditions, cancellations, and strength requirements;
- Vimshottari and other explicitly selected dasha systems;
- transits (gochara), Ashtakavarga, and timing synthesis;
- annual methods, including separately sourced Tajika material;
- compatibility systems and their regional variants;
- Jaimini techniques only as a separately versioned source pack;
- prashna, muhurta, samhita, and medical material outside the birth-only product.

Research blockers: BPHS recension history; translation rights; ayanamsha and
node defaults; house model; varga and dasha school variants; access to worked
examples from authoritative editions; Sanskrit review.

### Chinese BaZi / Ziping

- exact year, month, day, and hour pillar algorithms;
- solar-term boundaries and timezone/longitude/apparent-time conventions;
- hidden stems, Ten Gods, Five Phase relations, season/month command;
- strength and root/support assessment without invented percentage scoring;
- structures/patterns, useful/favorable/unfavorable influences, and climate
  adjustment as school-scoped doctrines;
- combinations, clashes, harms, punishments, destructions, transformations and
  their enabling/blocking conditions;
- Twelve Life Stages, Na Yin, and symbolic stars as separately toggleable layers;
- luck-pillar direction, start age, decade, annual, monthly, and shorter timing;
- relationship/family/vocation interpretations with exact source scope;
- compatibility and uncertainty around the hour pillar.

Research blockers: Chinese critical editions; translation; competing day
boundary and true-solar-time conventions; different pattern/useful-god schools;
worked-example corpus.

### Zi Wei Dou Shu

- lunar-calendar conversion and leap-month treatment;
- life/body palaces and twelve-palace layout;
- placement algorithms for the principal and auxiliary stars;
- Four Transformations by stem and school;
- brightness/temple status tables and variant schools;
- palace, star, combination, opposite/trine-axis, decade and annual rules;
- Southern/Northern or other documented school variants.

This engine must not reuse BaZi meanings merely because both are Chinese.

### Mesopotamian/Babylonian

- Enuma Anu Enlil subcorpora: first crescent, lunar eclipse, solar phenomena,
  weather, earthquakes, and planetary/fixed-star omens;
- protasis/apodosis normalization, geographic mappings, substitutions,
  cancellations, repetitions, observation reliability, and ritual response;
- scholarly reports and letters as evidence for applied interpretation;
- MUL.APIN and computational/visibility background where relevant;
- Astronomical Diaries and Goal-Year material only for their documented roles;
- late Babylonian natal horoscope corpus as a separate engine with explicit
  limits on surviving interpretations.

Birth data alone cannot drive the state-omen engine. It requires a historical or
current observed/calculated phenomenon and relevant mundane context.

### Islamicate/Persian

- one author/work/source pack at a time;
- natal foundations, interrogations, elections, annual revolutions, mundane
  ingress/conjunction methods, lots, firdaria, and other time-lord systems;
- Sasanian/Indian/Greek transmissions identified where sources do so;
- lunar mansions, astrometeorology, talismanic material and city/foundation
  charts kept in their actual domains;
- Arabic, Persian, Hebrew, and Latin recensions compared rather than silently
  merged.

The existing al-Biruni and Ibn Ezra entries are inspected anchors, not complete
Islamicate or Jewish engines.

### Tibetan

- Phugpa, Tsurphu, Bhutanese, Mongolian and other calendar profiles;
- skipped/repeated days and months;
- lunar day, mansion, yoga, karana, solar/lunar longitude and planetary tables;
- Kar-tsi and Nak-tsi layers kept distinct;
- animal/element, mewa, parkha, life-force/body/power/luck/vitality and annual
  cycles only after Tibetan-language or lineage-qualified verification;
- compatibility, obstacle years, death/funeral, medical, ritual and remedial
  material subject to strong safety and practitioner-review limits.

### Maya

- selected correlation constant and conversion uncertainty;
- Long Count, Tzolk'in/Chol Q'ij, Haab and Calendar Round;
- Lords of the Night, Year Bearers and regional variants;
- codex-specific almanacs and astronomical tables;
- Venus, eclipse, lunar, rain, agricultural and katun material in source scope;
- contemporary K'iche' and other living daykeeping as community-specific packs,
  never represented as a single timeless pan-Maya doctrine.

### Nahua/Central Mexican

- tonalpohualli arithmetic and correlation;
- day sign, coefficient, trecena ruler, day/night lords and directional layers;
- year signs/bearers, xiuhpohualli/veintena relations and 52-year cycle;
- Codex Borbonicus, Borgia group, Telleriano-Remensis, Vaticanus A, Aubin and
  colonial textual witnesses as identified source packs;
- Nahuatl vocabulary and regional/period variants;
- modern community review before presenting identity or destiny claims.

### Pharaonic Egyptian

- Egyptian civil-calendar conversion profiles and uncertainty;
- Papyrus Sallier IV and Cairo Calendar good/bad subdivisions with passages;
- decan lists and diagonal star-table variants;
- Ramesside/transit star clocks and temple/tomb astronomical diagrams;
- later demotic/Greco-Roman material separated from pharaonic corpora.

The honest product may be a day-quality/decan tool, not a full natal reading.

### Onmyodo

- period and institution (ritsuryo/Heian and later developments);
- calendar bureau algorithms, sexagenary dates, seasonal nodes and eclipse/comet
  omen practice;
- directional taboos, nine-star and related imported methods only where the
  selected Japanese sources document them;
- Senji Ryakketsu and other primary texts with Japanese specialist review;
- ritual/purification content treated as historical description, not automated
  instruction.

### Southeast Asian and related regional systems

Create separate manifests for:

- Burmese calendar, Mahabote and eight-day planetary practice;
- Thai/Lanna/Lue Suriyayatra and Thai horoscopy;
- Khmer ephemerides and documented divination traditions;
- Sinhalese/Sri Lankan Jyotisha and regional timing/marriage practices;
- Mon and other local corpora;
- Mongolian calendar/astrology;
- Korean Saju and its textual/practice differences from Chinese BaZi;
- Vietnamese systems and their Chinese/local layers;
- pre-Islamic Arabian anwa and lunar-station weather calendars;
- medieval Jewish author-specific astrology, beginning with already-inspected
  Ibn Ezra material.

## 7. Validation corpus specification

Each engine needs:

1. **Source vectors:** every worked calculation/example in the controlling text.
2. **Almanac vectors:** dates around year, month, day, hour, leap, and solar-term
   boundaries.
3. **Astronomy vectors:** positions checked against an independent ephemeris or
   published table using the same coordinate/time conventions.
4. **Historical vectors:** published tablets/charts/calendars reconstructed from
   their recorded data.
5. **Practitioner vectors:** blinded calculations and rule traces reviewed by at
   least two qualified practitioners of the selected school, where feasible.
6. **Uncertainty vectors:** unknown time, rounded time, ambiguous timezone,
   calendar reform, polar day/night, and dates outside ephemeris range.
7. **Adversarial vectors:** attempts to induce cross-tradition leakage,
   unsupported remedies, medical/financial advice, or fatalistic certainty.

## 8. Research deliverables per tradition

```text
README.md                 boundaries and status
sources.json              edition/corpus registry and rights
passages/                 permissible extracts and exact locations
calculation_spec.md       formulas, epochs, constants, conventions
rules.json                atomic versioned rules
conflicts.md              textual/school disagreements
golden_vectors.json       worked examples and expected outputs
validation.md             independent checks and practitioner review
coverage.json             supported/unsupported technique inventory
publication_policy.md     customer language and safety limits
```

## 9. Immediate research order

1. Shared time/calendar/uncertainty contract.
2. Jyotisha classical-natal source and convention audit.
3. BaZi calendar kernel and Ziping source audit.
4. Babylonian lunar-eclipse corpus expansion (bounded SAA 8 reports 316/535 and
   a two-witness `Enuma Anu Enlil` Tablet 20 latter-half pilot complete; the
   controlling 1988 edition and three later update articles inventoried; two
   ancient commentaries on Tablets 16-21 encoded separately; full Tablets
   15-22 base-text coverage, further witnesses, and collation remain open).
5. Maya calendar/codex pilot (the calendar arithmetic half now passes twelve
   bounded vectors under explicit 584283/584285 profiles; one page-addressed
   Dresden almanac, specialist review, rights review, and any living-practice
   partnership remain open; no reading engine exists).
6. Tibetan Phugpa calendar kernel (Janson's secondary reconstruction now
   passes exact-rational tests against Tables 1, 7, 8, and 9; Men-Tsee-Khang
   almanac concordance, Tibetan-language review, institutional permission, and
   all interpretation remain open).
7. Islamicate author-scoped expansion (the al-Biruni reference/condition pilot
   now passes 13 vectors and 288 exhaustive condition combinations against six
   visually inspected Arabic/English facing-page pairs; independent Arabic
   translation review, major firdaria durations, a complete natal procedure,
   and separate Abu Ma'shar/al-Qabisi comparison packs remain open).
8. Egyptian hemerology/decan feasibility pilot.
9. Language-partner discovery for Zi Wei, Onmyodo, Nahua, and regional Asian
   systems.
