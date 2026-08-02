# Mesopotamian / Babylonian astral-divination source audit

Status: research foundation, not production approval  
Updated: 2026-08-01

## Result of this pass

There is enough surviving material to build several historically bounded tools, but not one undifferentiated “Babylonian natal astrology” engine. The source record requires at least four separate products or modes:

1. **Neo-Assyrian state celestial reports** — observations/predictions and selected omen clauses sent to a king;
2. **`Enuma Anu Enlil` omen-series research mode** — a much larger canonical omen tradition organized by celestial/weather phenomena and primarily institutional portents;
3. **Late Babylonian natal horoscope reconstruction** — documents recording astronomical data on or near a birth, sometimes with short auspicious/inauspicious implications;
4. **astronomical-compendium mode** — `MUL.APIN` and later procedure/ephemeris texts that establish historical celestial schemes but are not themselves interchangeable with natal judgment texts.

Chronology, genre, audience, and method must be visible in every output. A late zodiacal horoscope cannot be projected backward into a second-millennium omen, and an omen addressed to a king or country cannot be silently rewritten as an individual's personality trait.

## Corpus map

| Corpus | Period/scope | What it can support | What it cannot support by itself |
|---|---|---|---|
| `Enuma Anu Enlil` | long first/second-millennium textual tradition; standardized celestial omen series | protasis/apodosis omen logic, phenomenon categories, regional/state portent mappings | a modern natal chart or generic personal reading |
| SAA 8 reports | Neo-Assyrian royal scholarly reports | real observation/report practice; citation of omens; uncertainty, variants, timing, regional mappings, remedial context | universal rules detached from royal/institutional setting |
| Late Babylonian horoscopes | fifth through first centuries BCE in the currently known corpus | birth-date astronomical data, zodiacal positions, select natal implications and technical schemes | twelve-house, ascendant, aspect, or personality systems unless a tablet/edition explicitly attests them |
| `MUL.APIN` | first-millennium astronomical compendium with older material | star lists, ideal calendar schemes, simultaneous risings/settings, Moon-path constellations | a natal judgment manual |
| Astronomical Diaries / procedure texts / ephemerides | first-millennium observed and computed astronomy | independent reconstruction of historical celestial data and scribal computational context | automatic astrological judgment |

## Evidence inspected

### ORACC overview of `Enuma Anu Enlil`

The ORACC Ancient Knowledge Networks overview divides the standard series into lunar-crescent material, lunar eclipses, solar phenomena/eclipses, weather/earthquakes, then planetary and fixed-star signs. It states that the portents overwhelmingly concern institutions: king, army, country, enemies, flood, crops, pestilence, and disease.

Source: [ORACC technical terms](https://oracc.museum.upenn.edu/cams/akno/technicalterms/index.html)

### State Archives of Assyria 8

The open SAA 8 corpus supplies tablet-level metadata, Akkadian transliteration, English translation, sender/recipient, genre, period, and edition lineage. Inspected records demonstrate the actual predicate structure needed for a rule engine:

- phenomenon observed or predicted;
- celestial body and event class;
- month and day;
- eclipse watch;
- start/end direction or affected portion;
- color, wind, halo, or accompanying planet;
- region, ruler, army, crop, or other target;
- quoted omen and sometimes variant;
- possible protective/remedial action or substitute target;
- damage/restoration status of the tablet text.

For example, SAA 8 316 explains that an eclipse's evil is assigned using month, day, watch, and where it begins and clears. SAA 8 535 combines month, date, watch, direction/region, wind, and Jupiter. These are not single-key lookup rules.

#### Bounded lunar-eclipse pilot

The first executable research extraction is intentionally narrow: official
ORACC TEI for SAA 8 reports 316 (`P238143`) and 535 (`P236933`). The retrieved
witnesses are locked by SHA-256 in
`saa8_lunar_eclipse_pilot_corpus.json`; their transliteration, English
translation, line alignment, damage, and editorial restoration markup were
inspected together. The pilot contains 24 passage units, 33 atomic rules across
two manifests, and 12 direct, mutation, abstention, boundary, and safety
vectors with complete rule coverage.

The extraction keeps month, day, watch, beginning direction, clearing
direction, eclipsed portion, wind, cloud, lightning, darkness, accompanying
planet, and geographic target as distinct selectors. It also retains variants,
unknown observations, broken text, restorations, and the reports' political
rhetoric. Restored or damaged predicates fail closed. Descriptions of royal
substitution, exorcistic action, death, famine, flood, revolt, or territorial
harm are historical evidence only and cannot produce advice or customer
predictions.

This branch is a Neo-Assyrian institutional/state-omen model. Every pilot rule
has `birth_input_eligible: false` and every conclusion has
`customer_prediction: false`. A person's birth date, time, or place therefore
cannot activate it, and it must not be merged into the late Babylonian natal
horoscope branch.

The next bounded pass inspected Al-Rawi and George's full critical edition of
Late Babylonian IM 124485, covering Tablet 20 sections VII-XIII, and Heessel's
KAL 13 text 21, the Neo-Assyrian VAT 9419 + VAT 11310 fragment covering parts
of sections X-XIII. The PDFs are locked in the corpus manifest by SHA-256 as
`5bab54e...79c7d72e` (35 pages) and `d15921dc...71589e` (279 pages). The
comparison yields 13 passage units, 17 rules, and 11 vectors.

This is evidence against a flattened textus receptus. The witnesses and the
editions' cited manuscripts transpose eclipse directions, change dates and
selectors, divide clauses differently, and sometimes give incompatible
outcomes such as peace versus plunder or destruction versus prosperity. The
rules therefore require explicit witness and recension identity. Supplements
about Venus, fixed stars, or Papsukkal remain separate from the lunar-eclipse
protasis; impossible schematic eclipse dates and unstable clause boundaries
fail closed. Every rule remains ineligible for birth input and customer
prediction. Full Tablets 15-22 coverage, additional witnesses, Assyriological
collation, rights review, a larger applied-report sample, and a separate
astronomical/calendar layer remain open.

Sources:

- [SAA 8 corpus](https://oracc.museum.upenn.edu/saao/saa08/)
- [SAA 8 316: lunar eclipse and Jupiter](https://oracc.museum.upenn.edu/saao/saa08/P238143/html)
- [SAA 8 535: eclipse on Sivan 15](https://oracc.museum.upenn.edu/saao/saa08/P236933)
- [SAA 8 046: predicted non-occurrence of eclipse](https://oracc.museum.upenn.edu/saao/saa08/P336575/)
- [Al-Rawi and George, EAE Tablet 20 critical edition](https://www.cambridge.org/core/journals/iraq/article/tablets-from-the-sippar-library-xiii-enuma-anu-ellil-xx/280BDD368D6222B88EAFDC70CFC49E15)
- [Heessel, KAL 13 text 21](https://doi.org/10.11588/diglit.69509#0070)

Files:

- `eae20_canonical_witness_pilot_corpus.json`
- `eae20_witness_rule_manifest.json`
- `eae20_witness_validation_vectors.json`

#### Tablets 15-22 edition map and ancient commentary layer

The edition inventory now identifies the controlling full edition as
Rochberg-Halton's 296-page 1988 AfO Beiheft 22 and records three necessary
updates: Fincke 2016 for Tablets 15-19, Fincke 2017 for Tablet 20, and Fincke
2019 for Tablets 21-22. Institutional catalogs, publisher records, CDLI, and
the author's bibliography verify their identity and scope. They do not provide
openly inspectable full text, so none of those four publications has been
misrepresented as passage-inspected and no rules were extracted from snippets.

Two complete open Yale CCP/ORACC editions do provide a bounded ancient-
commentary layer. BM 47447 (`P461229`) is a 71-line Achaemenid commentary mainly
on EAE 16 with final EAE 19 entries. Sm.683 (`P425538`) is a Neo-Assyrian
fragment explaining EAE 21 sections II, IV, and VI. Their complete
transliterations, translations, introductions, notes, and collations were
inspected and their ORACC HTML artifacts hash-locked.

The resulting corpus has 21 passage units, 22 rules, and 14 vectors. It records
ancient scope restrictions (for example, an eclipse-with-lightning entry is
restricted to summer), alternative astronomical readings, lexical equations,
regional mappings, damaged dependencies, and the Sm.683 commentator's
rationalization of what modern editors identify as a sign error in one base
manuscript. Commentary is always labeled as commentary; a quoted base omen is
not promoted to controlling base text until collated against the 1988 edition
and relevant Fincke update. Alternatives are not combined, broken dependencies
fail closed, and every rule rejects birth input and customer prediction.

Sources:

- [Rochberg-Halton 1988 bibliographic record](https://cdli.earth/publications/75398)
- [Fincke 2016, Tablets 15-19](https://doi.org/10.1400/251413)
- [Fincke 2017, Tablet 20](https://doi.org/10.1400/257666)
- [Fincke 2019, Tablets 21-22](https://doi.org/10.1400/278198)
- [Yale CCP P461229, commentary on EAE 16-19](https://ccp.yale.edu/P461229)
- [Yale CCP P425538, commentary on EAE 21](https://ccp.yale.edu/P425538)

Files:

- `eae15_22_edition_inventory.json`
- `eae16_21_commentary_corpus.json`
- `eae16_21_commentary_rule_manifest.json`
- `eae16_21_commentary_validation_vectors.json`

### Rochberg's `Babylonian Horoscopes`

The 1998 American Philosophical Society volume is the controlling corpus lead. The publisher describes it as the first complete edition of the extant cuneiform horoscopes, with transcription plus philological and astronomical commentary. Its structure explicitly separates cultural context, edition method, elements of a horoscope, the texts, glossary, and index. NYU's Ancient World Digital Library exposes a 184-page searchable scan under noncommercial research/education terms with APS permission.

The publisher distinguishes these horoscopes from single-event omens: they assemble the Moon, Sun, and five planet positions at birth and presuppose the ecliptic plus methods for obtaining unobservable positions. This does not imply a later Greek-style chart; features must be admitted only when attested in the corpus.

Sources:

- [AWDL searchable scan and rights statement](https://sites.dlib.nyu.edu/viewer/books/isaw_aphs000011/1)
- [Publisher description and table of contents](https://www.degruyterbrill.com/document/doi/10.70249/9798893983043/html)

#### First passage-level pilot: Text 10 (MLC 2190)

Text 10, the horoscope of Aristocrates (YPM BC 002136 / CDLI P507395), and its
duplicate Text 11 were inspected on book pages 83-87. The source records a
Seleucid-era date, the Moon, Sun and five visible planets, a lunar-latitude
statement, and short judgments associated with Jupiter, Venus and Mercury.
Rochberg's published astronomical table was first preserved as a recomputation
target. It has since been reproduced through the locked Swiss Ephemeris profile
and independently cross-checked against NASA/JPL Horizons, without treating
either modern ephemeris or the editor's correction value as verification of the
tablet reading. The editor also says that the birth-time expression is difficult
and that the lunar longitude does not resolve it.

The decisive rule-engine finding is that the three planetary judgments are
introduced through planetary `KI` (`qaqqaru`, “place”). Rochberg parallels that
usage with nativity omens, but Text 10 alone does not establish the executable
`KI` scheme. Therefore none of the judgments may be encoded as “Jupiter in
Sagittarius,” “Venus in Taurus,” “Mercury in Gemini,” or “Mercury with the Sun.”
They remain record-specific historical judgments with a null algorithmic
trigger until the terminology and parallel corpus are resolved.

The pilot contributes four grade-B, research-only rules and one record-level
validation vector. Longevity, fertility/offspring, rank and inheritance language
is retained for historical fidelity but is ineligible for personal prediction.
The acquired 184-page low-resolution scan has SHA-256
`dd233eb1593135dacf280224288fb16cf3697df48fc9ec0347cc522959dff285`;
AWDL's noncommercial research/education terms do not establish commercial
publication rights.

Files:

- `rochberg_text10_rule_manifest.json`
- `rochberg_text10_validation_vectors.json`

#### Texts 1-10 corpus-format pass

The first ten numbered tablets were then inspected across book pages 51-85.
They contain eleven natal records because Text 6 places two births on one
tablet. This is a discovery and fixture-selection corpus, not yet ten accepted
golden charts: Text 3 and Text 6(a) are too fragmentary for the primary golden
set, while several other records require restoration-sensitive tests.

The pass establishes at least these distinct record structures:

- Text 1 records synodic phenomena around the birth; Rochberg explicitly says
  none of its astronomical data refer to the birth date.
- Texts 2, 4, 6(b), 7, and 8 use normal-star lunar positions, sometimes at a
  time different from the preserved birth time.
- Text 7 contains both a conception record and a birth record; its 273-day
  interval is a record fact, not a universal gestation rule.
- Texts 5, 9, and 10 contain personal judgments, but Text 5's possible house
  scheme is damaged, Text 9 includes restored/damaged triggers, and Text 10's
  planetary judgments depend on unresolved `KI`.
- Text 4 records Mercury and Saturn at their synodic-event dates rather than as
  ordinary birth-time positions.
- Text 8 preserves a Mars reading that conflicts with Rochberg's computation;
  the engine must retain the discrepancy instead of silently correcting it.

`rochberg_texts1_10_corpus_manifest.json` records all eleven births, sixteen
explicit judgment clauses, textual/restoration status, date and time limits,
editorial-computation status, and pilot eligibility. Its dedicated JSON Schema
requires every customer-prediction flag to remain false. The corpus-wide CDLI
audit now provides exact identifier/reference joins for 30 of 32 numbered
tablets; Texts 11 and 16 and all image-level collation remain explicit gates.

Files:

- `horoscope_corpus.schema.json`
- `rochberg_texts1_10_corpus_manifest.json`

#### Judgment-clause completion for Texts 2, 5, and 9

The actual rendered edition pages for Text 2 (pp. 56-57), Text 5 (pp. 65-67)
and Text 9 (pp. 79-81) were re-inspected against their transcription,
translation, apparatus, commentary and astronomical tables. This completes a
machine-readable rule entry for every one of the sixteen explicit judgment
clauses in Texts 1-10:

- Text 2 contributes one uncertain propitious clause whose subject and relation
  to the reverse chronology are unresolved;
- Text 5 contributes eight property, deprivation, age-36, longevity,
  relationship, profit and travel clauses, but the possible house material is
  damaged and no clause can be attached securely to a planet, sign,
  conjunction or house;
- Text 9 contributes three same-line judgment candidates. The Moon/long-life
  line is preserved, Jupiter is restored, and the Venus premise is damaged.
  Same-line adjacency in one record is not yet a complete reusable protasis.

The twelve new rules range from grade B to D and are record-specific,
research-only evidence. Their twelve vectors test restoration removal,
placement non-equivalence, age-36 ambiguity, incomplete predication and the
required suppression of lifespan, fertility, deprivation, relationship,
status and financial predictions. Combined with Text 10, the Babylonian pilot
now has sixteen clause rules and thirteen vectors, but still no modern-input
judgment engine.

Files:

- `rochberg_texts2_5_9_judgment_rule_manifest.json`
- `rochberg_texts2_5_9_judgment_validation_vectors.json`

#### First independent astronomical-table reproduction

Rochberg's longitude tables for Texts 2-10 were recomputed with pyswisseph
20230604 / Swiss Ephemeris 2.10.03, the official compressed DE431 planetary and
lunar files for 601 BCE-2 BCE, proleptic Julian dates, astronomical year
numbering, and each correction printed by Rochberg. A second calculation used
the built-in Moshier semi-analytical model. This is independent of Rochberg's
numeric output, but it is a cross-model check through one library rather than a
fully separate implementation.

The executable validator checks 67 published positions:

- all 58 non-lunar positions reproduce within 0.2151 degrees;
- 6 of 9 lunar positions reproduce within the exploratory 0.35-degree
  threshold;
- the largest DE431-versus-Moshier longitude difference is 0.0242 degrees;
- Text 5's Moon differs by -0.5785 degrees and would match after a diagnostic
  shift of about +1.09 hours;
- Text 9's Moon differs by +0.7683 degrees and would match after a diagnostic
  shift of about -1.53 hours;
- Text 6(b)'s printed May 4 table label misses by -12.1770 degrees, while the
  May 5 date stated in the adjoining prose misses by only -0.2695 degrees.

Those time shifts are diagnostics, not rectifications. Texts 5 and 9 require a
bounded birth-time/UT1/Delta-T sensitivity analysis rather than selecting the
best-fitting time. The Text 6(b) label conflict must remain visible pending
calendar and edition review.

The validator also caught a software-level reproducibility hazard: Swiss
Ephemeris automatic tidal acceleration can become call-order dependent when
SWIEPH and MOSEPH calls are interleaved. The research profile now locks
`TIDAL_DE431` (-25.8 arcseconds per century squared) before any calculation and
verifies the return flags so a missing file cannot silently fall back to
Moshier.

The 0.25-degree planetary and 0.35-degree lunar thresholds were selected during
this exploratory pass. They are explicitly not preregistered final golden-set
tolerances. A Delta-T/UT1 interval study, source-specific calendar review, and
frozen prospective thresholds are still required.

#### Text 1 event-sequence reproduction

Text 1 (AO 17649, book pp. 51-55 / PDF pp. 67-71) cannot be validated as a
birth chart. Rochberg explicitly states that none of its astronomical data
refer to the date of birth. The research fixture therefore represents twelve
separate records: five visibility reports, two stations, a fixed-scheme
solstice date, an editorially restored lunar-visibility datum, an ideal Saturn
visibility alternate, an acronychal rising, and the intercalary-Addaru notice.

Using the same version- and hash-locked DE431 profile, an explicit approximate
Babylon coordinate, disc-center rise/set events, and no refraction, the new
validator reproduces:

- 15 published modern-longitude comparisons within 0.5673 degrees;
- 12 published rise/set-time comparisons within 0.0574 hour;
- Jupiter's second station inside Rochberg's October 12-16 interval and direct
  motion by October 17;
- the Saturn acronychal elongation within 0.3716 degrees; and
- the tropical winter-solstice crossing at -410 December 26, 03.1685 UT,
  separately from the text's schematic Tebetu day 9.

The first Mercury discussion contains a source-layer inconsistency worth
preserving: its printed 241.84-degree summary minus Rochberg's stated
8.73-degree correction is exactly the later 233.11-degree uncorrected value.
The validator compares like with like rather than treating both as modern
tropical longitudes.

Two calendar/editorial issues remain unresolved. Independently solving
Saturn's first station gives -410 November 2, 12.3844 UT, about 24.484 days
before the date obtained by strict same-month arithmetic from the edition's
Kislimu day-15 Mercury mapping. The lunar phenomenon on Tebetu day 26 is
supplied in angle brackets; nearby January 13-16 lunar diagnostics are retained
without choosing a Julian date or claiming visibility. The same no-verdict
policy applies to every first/last visibility entry because geometry alone is
not an ancient atmospheric visibility criterion.

Files:

- `rochberg_text1_event_spec.json`
- `validate_rochberg_text1_events.py`

Reproduction command:

```powershell
python docs/research/multitradition/babylonian/validate_rochberg_text1_events.py `
  --ephe-dir tmp/text1_ephe `
  --fetch-missing
```

#### Independent NASA/JPL Horizons cross-check

All 192 published positions were also submitted to the documented NASA/JPL Horizons API
from an independently written request/parser path, using Earth geocenter
`500@399` and apparent Earth-ecliptic-of-date longitude (quantity 31). The
comparison deliberately asks two different questions:

- **Texts 2-10, 67 positions:** at the same UT labels, the maximum absolute
  difference is 0.0306521 degrees for all bodies and 0.0031827 degrees for
  non-lunar bodies. Horizons' quantity-30 Delta-T values exceed the locked
  Swiss values by 95.059-224.735 seconds at the eleven tested instants. At the
  same TT instants, all differences are at most 0.0008223 degrees, with a mean
  absolute difference of 0.000813 degrees;
- **Texts 12-27, 125 positions:** at the same UT labels, the maximum absolute
  difference is 0.0148495 degrees for the Moon and 0.001646 degrees for
  non-lunar bodies. Horizons-minus-Swiss Delta-T ranges from -41.945 to
  +90.342 seconds across eighteen instants. At the same TT instants, all
  differences are at most 0.0008398 degrees, with a mean absolute difference
  of 0.000829 degrees.

The TT instants use the locked Swiss Delta-T only to construct a common
dynamical-time comparison. That does not select Swiss Delta-T as historically
true. The near-constant residual is consistent with the documented Horizons
IAU76/80 Earth-ecliptic-of-date output and the libraries' differing reference-
frame realizations; it is retained, not subtracted.

Horizons planet-center trajectories do not cover every ancient date in this
sample, so Mars, Jupiter, and Saturn use barycenter targets 4, 5, and 6. The
target mapping is therefore a visible limitation, not interchangeable with a
final offline planet-center oracle. The API results are a reproducible live
snapshot with post-hoc drift gates; they are not immutable golden vectors.

Sources: [Horizons API documentation](https://ssd-api.jpl.nasa.gov/doc/horizons.html)
and [Horizons manual](https://ssd.jpl.nasa.gov/horizons/manual.html).

Files:

- `rochberg_texts1_10_astronomy_spec.json`
- `rochberg_texts11_27_astronomy_spec.json`
- `validate_rochberg_astronomy.py`
- `jpl_horizons_crosscheck_spec.json`
- `jpl_horizons_texts11_27_crosscheck_spec.json`
- `validate_horizons_crosscheck.py`

Reproduction command from the repository root (the explicit fetch flag verifies
the official byte counts and hashes before calculation):

```powershell
python docs/research/multitradition/babylonian/validate_rochberg_astronomy.py `
  --ephe-dir tmp/babylonian_ephe `
  --fetch-missing

python docs/research/multitradition/babylonian/validate_horizons_crosscheck.py `
  --ephe-dir tmp/horizons_crosscheck_ephe `
  --fetch-missing

python docs/research/multitradition/babylonian/validate_horizons_crosscheck.py `
  --spec docs/research/multitradition/babylonian/jpl_horizons_texts11_27_crosscheck_spec.json `
  --rochberg-spec docs/research/multitradition/babylonian/rochberg_texts11_27_astronomy_spec.json `
  --ephe-dir tmp/horizons_texts11_27_ephe `
  --fetch-missing
```

### CDLI object records

Exact-designation searches of CDLI's current catalog now match 30 of Rochberg's
32 numbered tablets. Every accepted artifact page both preserves the edition's
museum designation and explicitly cites the same *Babylonian Horoscopes*
number. Examples include P493454 / AO 17649 (no. 1), P364217 / BM 33382
(no. 4), P507395 / MLC 2190 (no. 10), P565177 / BM 41054 (no. 17), and
P364227 / BM 42025 + BM 42164 (the joined pieces of no. 25). The birth-note
tablets are also joined: P565183 (no. 29), P565152 (no. 30), P364221 (no. 31),
and P364225 (no. 32).

The two unresolved entries are Uruk excavation numbers W 20030/143 (no. 11,
the copy of no. 10) and W 20030/10 (no. 16). CDLI's exact-designation search
returned no record for either on 2026-08-01. No identifier was inferred from
nearby catalog sequences. The machine-readable concordance locks all 30
positive joins and both negative results.

Of the 30 matched pages, 29 displayed CDLI's no-image asset and none supplied
an in-page transliteration or translation. Only P364229 / Text 27 exposed a
photo thumbnail; the downloaded thumbnail was SHA-256 verified and visually
inspected as a montage of the tablet surfaces and damaged edges, then removed.
No sign reading was asserted from it. This demonstrates why a
production manifest must still join catalog record, object image, edition,
transliteration, translation, and recomputation rather than treating any single
web record as complete. Identifier concordance is not sign-level collation.

Sources:

- [CDLI horoscope of Aristocrates](https://cdli.earth/cdli-tablet/746)
- [CDLI P565177 / horoscope no. 17](https://cdli.earth/artifacts/565177)
- [CDLI P364229 / horoscope no. 27](https://cdli.earth/artifacts/364229)
- [CDLI collection search](https://cdli.earth/search)

File: `rochberg_cdli_concordance.json`

### `MUL.APIN` tablet 1

The British Museum identifies tablet 86378 as a nearly complete Late Babylonian witness of `MUL.APIN` tablet 1. The catalog lists three divisions of heaven, dates in an ideal 360-day year, simultaneous risings/settings, and Moon-path constellations, and points to Hunger and Pingree's critical edition. This is essential astronomy-history evidence but must not be misrepresented as a natal delineation source.

Source: [British Museum tablet 86378](https://www.britishmuseum.org/collection/object/W_1899-0610-108)

## Product boundaries

### A. Historical birth-horoscope reconstruction

Input may use modern birth information, but the output must be framed as a reconstruction of facts of the kinds attested in late Babylonian horoscope documents. Candidate fact families include:

- Babylonian calendar date and intercalation state;
- location and historical time uncertainty;
- Sun, Moon, and five visible planet positions;
- zodiacal sign and degree/fraction only where the selected text class supports it;
- lunar phase/date relationships;
- visibility phenomena and relevant synodic state;
- any attested named technical scheme, versioned by scholarly interpretation;
- direct implications only when a rule is tied to an edited text.

The engine must not add twelve topical houses, a modern Ascendant, modern aspects, outer planets, psychological sign descriptions, or medieval dignities merely because the existing Western engine can compute them.

### B. Celestial-omen research reader

This is event-driven, not birth-driven. It should accept an observed or reconstructed phenomenon and expose matching omen passages with their full qualifiers, variants, target, date range, and source condition. Because most portents are political/collective and many are violent, this mode should be scholarly and non-predictive for consumers.

### C. Royal-report simulator/explorer

This should reproduce the structure of a report—observation, cited series, variants, uncertainty, and historical response—without pretending to advise a present-day ruler or forecast real disasters. It is a textual-education product, not a personal reading.

## Required data model

```text
artifact
  museum/CDLI/ORACC identifiers
  provenance, period, language, script, dimensions
  image rights and image checksum

edition witness
  publication, editor, year, pages/text number
  transliteration, translation, signs damaged/restored/uncertain

astronomical event
  body/bodies, phenomenon, observation versus prediction
  Babylonian date, proposed Julian date interval, location
  sign/degree or stellar reference as actually attested
  direction, watch, color, visibility, wind, halo, companion body

omen rule
  protasis predicates
  apodosis target and outcome
  geographic/royal context
  variants and commentary
  source text and confidence

natal record
  birth date/place information as preserved
  recorded celestial data
  recomputed celestial data and residuals
  explicit ancient judgments
  inferred/scholarly reconstructed schemes, separately labelled
```

## Validation design

1. Complete the two unresolved institutional joins for W 20030/143 and W 20030/10, then add image availability, rights, checksums, transliteration, translation, and sign-level collation to the 30 exact CDLI joins already locked in `rochberg_cdli_concordance.json`.
2. Freeze or independently reproduce the 192-position NASA/JPL Horizons snapshot and set prospective tolerances; calendar and Delta-T uncertainty intervals remain required even though both modern ephemeris paths agree closely at identical TT instants.
3. Compare recorded versus recomputed positions and preserve discrepancies; do not “correct” the ancient text silently.
4. Reproduce ancient calendar conversion independently with a second implementation and published chronology tables.
5. For omen rules, parse protasis and apodosis separately and retain every qualifier.
6. Test damaged/restored text by removing restorations; outputs depending on them must downgrade or disappear.

## Complete edition passage audit (2026-08-01)

The edition catalogue on book pages 25-27 / PDF pages 41-43 contains 28
numbered horoscope texts and four birth-note tablets. Three shared-tablet entries
(Texts 6, 16, and 22) have `a` and `b` records, producing 31 horoscope record
entries. Text 11 explicitly duplicates Text 10; collapsing only that documented
duplicate yields 30 catalogued horoscope entries after collapse. This is not a
proven unique-nativity count: Text 28 is so fragmentary that Rochberg says it
ought to have contained more than one horoscope. The four birth-note tablets
preserve six births, including three separate birth notices in Text 32. These
distinctions are locked in `rochberg_full_corpus_catalog.json`.

Every page covering Texts 11-20 (book pp. 86-115 / PDF pp. 102-131) was visually
inspected alongside the transcription, translation, apparatus, commentary, and
tables. The range adds eleven records but only three judgment candidates, all in
Text 16: a damaged good-fortune clause, an uncertain favorable qualifier on a
Venus first-visibility event, and a favorable lunar-progress fragment whose
conditional premise is incomplete. None supplies a generalizable or executable
birth-chart trigger. Text 11 supplies duplicate evidence, not independent rules.

Negative evidence remains first-class: Text 14 is extensively restored and has
an eclipse-sequence mismatch; Text 15 contains Jupiter and Mercury evidence-layer
discrepancies; Text 16 contains Venus, Moon-longitude, and lunar-latitude
conflicts; Text 17's date is provisional; Text 19's expected Moon sign does not
fit the surviving trace; and Text 20's lunar-eclipse date has no corresponding
eclipse.

Every page covering Texts 21-28 and Birth Notes 29-32 (book pp. 116-147 / PDF
pp. 132-163) was also visually inspected. Texts 21-28 add nine horoscope records
on eight tablets. Text 27 alone adds two personal-judgment fragments: “That child
good fortune ...” and “(his) good fortune will diminish.” Their upper-edge
location supplies no protasis or demonstrated link to any placement, seasonal
hour, eclipse, or visibility datum, so both remain non-executable. Text 28 has no
secure date, record boundary, or planetary reconstruction. The birth notes have
no planetary data or judgment rules; later dates in Texts 29 and 31 are retained
as annotations rather than miscounted as births.

The entire 32-text edition has now received passage-level inspection. The 125
published longitude values across 18 tables for Texts 12-27 were independently
recomputed under the locked DE431/Moshier profile. Of these, 112 fall inside the
inherited exploratory body tolerances; all thirteen failures remain explicit.
The largest planetary residual is Text 18 Saturn at 2.1036 degrees. Text 23's
printed January 6 table produces a 14.2624-degree Moon discrepancy and coherent
one-day discrepancies for faster bodies; a named January 5 diagnostic reduces
the Moon residual to 0.8514 degrees without replacing the printed label.

JPL cross-checking for this extension, object concordance, calendar uncertainty,
visibility/eclipses, and Assyriological review remain required before
implementation readiness can be assessed.
7. Mutation-test qualifiers such as month, day, watch, direction, and companion planet.
8. Have an Assyriologist review transliteration, translation, genre classification, and whether an executable rule overstates the text.

## Scholarly disagreement policy

New work can revise the schemes inferred from terse horoscope terminology. Alessia Pilloni's 2024 open-access study explicitly proposes new interpretations for `bit nisirtu` and `KI`. Such reconstructions belong in named hypothesis packs (`rochberg_1998`, `pilloni_2024`, etc.), never in an unlabeled “Babylonian” default. A result should show when packs disagree.

Source: [Pilloni 2024 repository record](https://refubium.fu-berlin.de/handle/fub188/43685?locale-attribute=en)

## Safety and historical-use policy

The corpora contain predictions of royal death, war, revolt, famine, disease, crop failure, and other catastrophe. Production must not present these as current factual forecasts or personal destiny.

- Keep state-omen outputs in an educational, source-reader context.
- Label all outputs historical reconstruction and cultural interpretation.
- Do not issue medical, legal, financial, geopolitical, or disaster advice.
- Suppress direct death, disease, or catastrophe predictions in consumer readings.
- Preserve the original apodosis internally with provenance and a suppression reason.
- Do not invent a reassuring opposite when a rule is suppressed.

## Production gates

The first Babylonian release remains blocked until:

- the complete horoscope corpus is licensed/inspected and concorded to objects;
- an Assyriologist has reviewed the corpus manifest and initial rule encodings;
- calendar and astronomy recomputation passes the full corpus with documented residuals;
- every feature is tagged `recorded`, `direct_rule`, `editor_restoration`, `scholarly_inference`, or `modern_reconstruction`;
- no later Hellenistic, medieval, or modern Western technique enters without explicit evidence;
- the public experience clearly distinguishes natal reconstruction from state omen research;
- rights and safety reviews pass.

## First bounded pilot

Build a non-consumer corpus validator before any reading generator:

1. ten well-preserved late horoscope records;
2. tablet/edition/CDLI concordance;
3. calendar conversion with uncertainty;
4. recomputed Sun, Moon, and visible planets;
5. recorded-versus-computed comparison report;
6. extraction of only the explicit judgments on those tablets;
7. independent Assyriological and astronomical review.

Only after that gate passes should the project decide whether the surviving rules support a meaningful personal reading, or only a historically faithful horoscope reconstruction.
