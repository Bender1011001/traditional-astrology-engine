# BaZi / Four Pillars source and convention audit

Status: research foundation, not production approval  
Updated: 2026-08-01

## Sexagenary kernel pack (added 2026-08-01)

The first machine-readable BaZi artifact now exists:
`sexagenary_kernel_spec.json`, `sexagenary_rule_manifest.json` (10 rules),
`sexagenary_validation_vectors.json` (20 vectors), and
`validate_sexagenary_kernel.py`.

Encoded, strictly within the inspected Hong Kong Observatory scope:

- ten-stem and twelve-branch orders and their modular cycles;
- the sixty-pair joint cycle from Jia-Zi with the same-parity invariant
  (all 60 valid pairs and all 60 cross-parity rejections enumerated);
- the twelve two-hour shichen with Zi spanning 23:00-01:00 (all 1,440
  minutes partition-checked);
- the year-stem-to-month-stem and day-stem-to-hour-stem lookup tables
  (all ten rows of each verified against the closed-form advance);
- solar terms as 24 ecliptic-longitude moments, twelve major and twelve
  minor, with per-term longitudes deliberately not encoded.

Refused, fail-closed:

- any default day-count anchor (the inspected pages supply no day
  concordance; civil-date conversion requires a named anchor profile and
  test-fixture anchors are labeled non-historical);
- any year/month/day/hour boundary convention (the convention matrix
  below remains unresolved; boundary-dependent pillar requests are
  rejected without a named school profile);
- any five-element tally, Ten-God relation, hidden-stem output, luck
  pillar, or interpretation (separate source-controlled packs required).

This closes the "machine-readable calculation manifest" gate in the
engine coverage manifest. The named-concordance, school-convention,
solar-time-lineage, and almanac-conformance gates remain open.

## Result of this pass

A historically defensible BaZi engine is feasible, but the current source set is not yet sufficient for production. The astronomy/calendar kernel has authoritative independent references. The interpretation layer now has two substantial Classical Chinese discovery texts, but neither web transcription can serve as a controlling edition without page-image alignment, bibliographic work, and specialist review.

The first architectural conclusion is firm: do not implement BaZi as a generic Five-Phase percentage score. The inspected `Yuanhai Ziping` transcription gives a hierarchy of conditional judgments:

1. establish the day stem as the subject;
2. determine month command, seasonal depth, and whether the subject has timely support;
3. determine rootedness and relative strength;
4. identify eligible relations and pattern candidates;
5. test whether each candidate completes, is damaged, competes, transforms, follows, or fails;
6. apply luck and annual periods to the already-qualified natal structure;
7. render a judgment with all supporting and defeating predicates exposed.

That hierarchy should become a deterministic rule graph. Numerical measures may assist a documented rule, but an undocumented weighted element total must never substitute for the source's categorical and conditional logic.

## Calculation kernel evidence

### Hong Kong Observatory

The Hong Kong Observatory supplies an independent government reference for:

- the ten heavenly stems and twelve earthly branches;
- the full sexagenary cycle beginning with Jia-Zi;
- the use of year, month, day, and hour stem-branch pairs as the Eight Characters;
- the twelve two-hour `shichen`, including Zi from 23:00 through 01:00;
- year-stem-to-month-stem and day-stem-to-hour-stem lookup tables;
- solar terms as moments when the Sun reaches 24 predefined ecliptic-longitude positions, divided into twelve major and twelve minor terms.

This evidence validates reference tables and astronomical test vectors. It does **not** select a BaZi school, a year/day boundary, true-solar-time policy, luck-cycle formula, or interpretation rule.

Sources:

- [Heavenly Stems and Earthly Branches](https://www.hko.gov.hk/en/gts/time/stemsandbranches.htm)
- [24 Solar Terms in 2027](https://www.hko.gov.hk/en/gts/astron2027/files/2027SolarTerms24.pdf)

## Interpretation witnesses inspected

### `Yuanhai Ziping` on Chinese Wikisource

The transcription is rich enough for technique discovery. Its table of contents includes the day as subject, month command, annual influence, major luck periods, hidden stems, strength, and the Ten-God relation families. Inspected passages include:

- `看命入式`: the day stem is the subject; year, month, day, and hour have distinct roles; month-season depth and obtaining the command matter; wealth/officer indications require the subject's strength; the reader is warned against rigid application.
- `神趣八法`: classification, following, transformation, reflection, reversal, and related patterns are conditional. Roots, competing combinations, season, and later periods can complete or break a candidate.
- `杂论口诀`: month, wealth/officer relations, and strength receive priority, followed by many terse judgments.
- `会要命书说`: the presented corpus describes itself as a combined and abridged collection of two earlier works.

Provenance limitations are serious. The page is categorized as a work without a cited source. Authorship and compilation layers are not established. The transcription is therefore a searchable discovery witness, not an edition-level authority.

Source: [Yuanhai Ziping transcription](https://zh.wikisource.org/wiki/%E6%B7%B5%E6%B5%B7%E5%AD%90%E5%B9%B3)

### `Sanming Tonghui` on Chinese Wikisource

The work page attributes the text to Wan Minying and links volumes one through nine; volumes ten through twelve are explicitly absent. Its bibliographic note is unusually valuable because it warns that later commercial printings inserted charts of late-Ming officials and describes doctrinal preferences and weaknesses in the received text. Volume one exposes foundational Five-Phase, stem-branch, Na Yin, and sixty-Jiazi material.

This witness can drive a passage inventory, but cannot control production rules until it is aligned to a complete dated scan and suspected interpolations are marked by edition.

Sources:

- [Sanming Tonghui work page](https://zh.wikisource.org/zh-hant/%E4%B8%89%E5%91%BD%E9%80%9A%E6%9C%83)
- [Sanming Tonghui, volume one](https://zh.wikisource.org/wiki/%E4%B8%89%E5%91%BD%E9%80%9A%E6%9C%83/%E5%8D%B7%E4%B8%80)

### `Mingli Jicheng`, volume-one page-image lead

The 98-page PDF opens successfully, but the web layer exposes no OCR or bibliographic text. Its filename identifies it as volume one of `Mingli Jicheng`; it does not yet prove which component work or edition is present. Title page, colophon, holding institution, publication date, and contents must be visually transcribed before promotion.

Source: [NLC/Wikimedia page-image PDF](https://upload.wikimedia.org/wikipedia/commons/d/d3/NLC511-04101394-70574_%E5%91%BD%E7%90%86%E9%9B%86%E6%88%90_%E5%8D%B7%E4%B8%80.pdf)

## Rule families to extract

Each family needs a source pack, convention identifier, passage manifest, translator review, worked examples, and counterexamples.

| Family | Required facts and predicates |
|---|---|
| Pillar construction | year, month, day, hour stem/branch; hidden stems; solar-term instant; civil and candidate solar times |
| Seasonal command | month branch, solar-term segment, seasonal depth, commanded/supporting/draining/controlling relationships |
| Day-master state | roots, visible/hidden support, generation/control, combinations, clashes, season, candidate strength class |
| Ten Gods | relation from each stem/hidden stem to day stem, polarity, location, visibility, eligibility, damage |
| Pattern eligibility | candidate pattern, required relation, month priority, purity/mixing, supporting conditions, defeating conditions |
| Transformations | combination present, season permits, root permits or blocks, competing combination, transformed state |
| Following structures | absence of usable root/support, dominant configuration, purity, later-period completion or breakage |
| Branch relations | combinations, directional/seasonal frames, clashes, harms, punishments, destruction, activation conditions |
| Useful/avoidant influences | school-specific derivation only; preserve disagreements rather than averaging them |
| Luck pillars | direction, sequence, commencement age/time, boundary convention, interaction with natal qualified structure |
| Annual/monthly timing | sexagenary period facts, natal-luck-period interactions, source-qualified event domains |
| Auxiliary markers | each spirit/star enabled only in a named source/school pack; never allowed to override core structure silently |

## Unresolved convention matrix

These choices can change the chart. No default may be hidden from the report or cache key.

| Convention | Known variants requiring proof | Production requirement |
|---|---|---|
| Year boundary | beginning of spring (`Li Chun`) versus lunar/civil new-year usage in some contexts | named school/source; boundary test vectors on both sides |
| Month boundary | minor solar terms (`jie`) versus other calendrical month mappings | exact longitude/term mapping and time standard |
| Day boundary | civil midnight versus early/late Zi-hour rollover variants | explicit versioned option; two-hour boundary vectors |
| Hour clock | standard civil time, local mean solar time, or apparent/true solar time | preserve civil time and all derived candidates; never silently replace |
| Longitude correction | zone-meridian correction; equation-of-time inclusion or exclusion | formula, ephemeris/time-scale source, and lineage attribution |
| Historical time | modern IANA zone where applicable versus reconstructed local time/offset | uncertainty interval and provenance; no false precision |
| Luck direction | sex/polarity and year-stem rules vary in presentation and school | source-specific predicate table |
| Luck commencement | days-to-nearest-term conversion; preceding/following term; conversion ratio and rounding | exact algorithm plus published worked examples |
| Hidden-stem weights | qualitative presence versus numerical proportions | forbid numerical weights unless the controlling source states them |
| Strength scoring | qualitative categories versus modern point systems | source-specific; no universal score |

## Proposed deterministic trace

```text
birth input
  -> civil-time and place resolution
  -> selected historical-time policy
  -> solar-longitude / solar-term facts
  -> pillar candidates under named boundary conventions
  -> hidden-stem and relation facts
  -> seasonal-command facts
  -> day-master support/root predicates
  -> pattern candidates
  -> completion / defeat / transformation tests
  -> natal qualified structure
  -> luck-period facts and interactions
  -> source-bounded judgments
```

Every output claim must state:

- the tradition and school pack;
- source edition and passage location;
- translation/reviewer version;
- calculation convention IDs;
- supporting facts and successful predicates;
- defeating predicates checked and their results;
- whether the judgment is direct, synthesized from named rules, disputed, or suppressed.

## Translation and edition workflow

1. Acquire complete dated page-image editions and record holding institution, catalog ID, edition, scan identity, rights, and hashes.
2. Build a diplomatic Chinese transcription aligned by page and section.
3. Collate Wikisource/Chinese Text Project text only as OCR or search aids.
4. Commission independent Classical Chinese translation and domain review.
5. Record terminology choices such as `yongshen`, `geju`, `de ling`, and `cong` without flattening them into one modern school definition.
6. Extract candidate rules as explicit predicates with passage locations.
7. Create positive, negative, boundary, and ambiguity examples.
8. Have a second specialist reproduce the classification from the source pack without seeing engine output.

## Safety and publication policy

The inspected classical text includes categorical claims about death, disease, disability, sexuality, gender, fertility, poverty, and moral character. These are historical artifacts, not acceptable direct consumer predictions.

Production behavior must:

- label the material as historical/cultural interpretation;
- suppress diagnosis, lifespan/death prediction, pregnancy/fertility certainty, criminality, sexual morality, and demeaning class/gender claims;
- retain the source passage and suppression reason in the internal audit trace;
- render non-deterministic, dignity-preserving themes only when a safe transformation is faithful to the rule;
- state when no safe consumer judgment can be produced.

## Production gates

BaZi remains blocked from release until all of the following pass:

- a controlling source pack has complete edition identity, page hashes, and passage locations;
- a named school/convention pack resolves every chart-changing boundary above;
- pillar calculations match independent observatory/calendar vectors and at least one separately implemented reference calculation;
- a bilingual specialist approves translations and rule encodings;
- worked examples reproduce both qualifying and defeating conditions;
- mutation tests prove that removing a condition changes or invalidates the expected judgment;
- time uncertainty is propagated into alternate-chart outputs rather than hidden;
- safety review approves all renderable judgment families;
- rights review approves commercial use of every published text fragment and translation.

## Next research actions

1. Identify and inspect a complete twelve-volume dated `Sanming Tonghui` scan.
2. Establish a bibliographic stemma for `Yuanhai Ziping` and select one or more controlling editions.
3. Locate primary or lineage-authoritative statements for every boundary in the convention matrix.
4. Acquire published worked charts from the selected source packs and encode them as golden cases.
5. Build the first narrow pilot: pillar calculation plus provenance trace only, with no consumer interpretation.
