# Pharaonic Egyptian hemerology and decan source audit

Status: research foundation, not production approval  
Updated: 2026-08-01

## Result of this pass

Ancient Egyptian evidence supports at least two valuable but separate products:

1. a witness-specific **calendar of lucky and unlucky days** (`hemerology`) explorer; and
2. a scholarly **decan and diagonal-star-table** explorer.

It does **not** presently authorize a native pharaonic twelve-sign, twelve-house,
planetary-aspect, or personality-style natal engine. A modern birth date must not
be relabeled with an invented "Egyptian zodiac." Even a daily hemerological
judgment cannot automatically become a statement about the character or fate of
a person born that day: the actual source passage must say that.

This pass now includes a machine-readable **civil-calendar arithmetic artifact
only**. It exhaustively validates all 365 internal positions, ordinary-month and
additional-day boundaries, negative offsets, a deliberately synthetic chronology
fixture, missing-profile rejection, later Alexandrian/Coptic-model rejection, and
the absence of prognosis or birth-reading output. It has no default historical
anchor and is neither live nor customer-eligible.

It also includes a hash-pinned, machine-validated access manifest for the full
317-page Cleveland Public Library scan of Budge's 1923 second series. The Sallier
IV section contains 41 facsimile plates (LXXXVIII-CXXVIII). Relevant description
pages, the first two calendar plates, and the final reverse plate were rendered
and visually inspected. This acquisition improves witness access but does not
make the hemerology rule-extraction-ready.

## Hemerological corpus inspected

### Papyrus Cairo 86637

Bakir's 1966 edition is the first controlling acquisition. The inspected
bibliographic record describes a 142-page publication containing photographic
reproduction, hieroglyphic transcription, and a briefly annotated translation.
The full edition was not accessible in this pass, so no individual rule from it
is production-authorized yet.

Source: [Open Library bibliographic record](https://openlibrary.org/books/OL270374M/The_Cairo_calendar_no._86637)

### Papyrus Sallier IV, British Museum EA10184

The British Museum identifies this late Nineteenth Dynasty papyrus, around 1225
BCE, as one of the most extensive surviving calendars of lucky and unlucky days.
Each day is prefaced by three good/bad markers, allowing mixed judgments within
one day.

A complete institutional scan of Budge's 1923 second series is now acquired and
hash-pinned as
`084058ed3a69936bcc56e1d96e1be0541a1f18f4d645e16dd1b9fec1a980f419`.
Budge's description identifies twenty-three surviving columns and the loss of
Thoth 1-17. Its more specific closing note preserves selected material for early
Pachons but says Pachons 11 through Mesore 30 are wanting. It also says the
portion probably containing the Five Epagomenal Days is lost. Plates
LXXXVIII-CXXVIII occupy PDF pages 231-311. Budge provides selected summaries,
not a complete modern critical translation, so no hemerological rules are
promoted from this acquisition.

Sources: [British Museum EA10184](https://www.britishmuseum.org/collection/object/Y_EA10184-5), [Cleveland Public Library scan](https://cplorg.contentdm.oclc.org/digital/collection/p4014coll9/id/5301/)

### Papyrus BM EA10474

The British Museum record identifies the recto as the Teaching of Amenemope and
the verso as a calendar of lucky and unlucky days. The calendar side requires a
facsimile and edition-level collation; the more famous recto must not be mistaken
for the source of the calendar rules.

Source: [British Museum EA10474](https://www.britishmuseum.org/collection/object/Y_EA10474-1)

### Leitz's comparative corpus

Christian Leitz's two-volume 1994 *Tagewahlerei* is identified in the inspected
scholarship as the most comprehensive study and main reference work. It must be
acquired before a source pack can be considered complete. Bakir alone is not an
adequate critical basis.

Source: [bibliographic record](https://openlibrary.org/works/OL3085197W/Tagewa%CC%88hlerei)

### Modern periodicity study

Porceddu and coauthors report nine full or partial hemerological witnesses. Their
13-page paper is now pinned as SHA-256
`b6c15ade0035169fbfb697645bd3cac902aad47bbb123e05013207a3d68c3f52`;
the relevant pages were text-extracted, rendered, and visually checked. The paper
documents the shared civil-calendar structure, normally three prognosis units for
a day, and exact tabulations from Cairo 86637, BM 10474, and Sallier IV.
It also reports statistical periodicities and possible astronomical associations.

Those associations are **modern analyses**, not ancient executable rules. They
may test an encoded corpus but must never add lunar or Algol meanings to a
reading unless an ancient passage independently supplies them.

Source: [full author-hosted paper](https://www.mv.helsinki.fi/home/jetsu/papers/egypt1.pdf)

## Calendar kernel

The hemerologies follow the Egyptian civil-calendar form:

- three seasons: Akhet, Peret, and Shemu;
- four numbered months in each season;
- thirty numbered days in each month;
- five additional `heriu-renpet` days completing a 365-day year; and
- normally three prognosis units within an ordinary day.

The inspected comparison contains no prognosis data for the five additional
days. The direct Budge witness evidence now makes the key distinction explicit:
Sallier IV's portion that probably contained those days is lost. Therefore the
system records “no preserved main-calendar prognosis in the inspected corpus”
and abstains; it does not claim that the historical source or tradition had no
prognosis. The comparison also warns that the civil year was not fixed to the
solar year. Therefore a conversion needs a named chronological model and
uncertainty, not merely `Gregorian month/day -> Egyptian month/day`.

The UCL institutional calendar table independently preserves the sequence of
four Akhet, four Peret, and four Shemu months followed by five additional days.
Its later Alexandrian/Coptic leap-day discussion is retained as a regime boundary,
not inherited by the pharaonic 365-day model.

```json
{
  "calendar_model_id": "named scholarly reconstruction",
  "historical_regime": "source period and place",
  "epoch_or_anchor": "citation",
  "civil_date_policy": "Julian/Gregorian conversion policy",
  "egyptian_date": {
    "season": "Akhet|Peret|Shemu|heriu-renpet",
    "month_in_season": 1,
    "day": 1
  },
  "conversion_uncertainty_days": 0,
  "applicability": "historical reconstruction|source-table lookup"
}
```

For a modern user's date of birth, the default honest state is
`source_limited`: an ancient recurring civil-calendar entry is not automatically
a historically authorized forecast for a twenty-first-century birth.

## Hemerology rule model

Every unit must preserve the actual witness instead of merging manuscripts into
one apparently unanimous calendar.

```json
{
  "witness_id": "p_cairo_86637",
  "edition_id": "bakir_1966_collated_leitz_1994",
  "source_locator": "recto/verso, column and line",
  "egyptian_date": {"season": "Akhet", "month": 1, "day": 15},
  "prognosis_units": [
    {
      "ordinal": 1,
      "source_label": "transliterated term",
      "normalized_valence": "good|bad|damaged|missing|uncertain",
      "time_mapping": "source-stated|scholarly-inference|unknown"
    }
  ],
  "narrative_basis": [],
  "recommended_or_forbidden_actions": [],
  "birth_specific_statement": null,
  "restorations": [],
  "translation_variants": [],
  "status": "direct|restored|disputed"
}
```

The three units must not be hard-coded as modern clock thirds until the selected
edition justifies that mapping. "Morning, midday, evening" is a useful scholarly
interpretation but not yet a verified time algorithm in this project.

## Decans and diagonal star tables

McMaster's Ancient Egyptian Astronomy Database is a current scholarly companion
to Neugebauer and Parker's *Egyptian Astronomical Texts*. It catalogs decans,
decan lists, diagonal star tables, astronomical representations, sundials, and
water clocks.

The database deliberately prefers **diagonal star tables** over labels such as
"star clocks" or "star calendars," because those names presume a function. It
also distinguishes T and K textual families, damaged or reconstructed lists,
and a modern ideal organization that no surviving object matches exactly.

Sources: [database](https://aea.mcmaster.ca/index.php/en/database), [diagonal star tables](https://aea.mcmaster.ca/index.php/en/database/diagonal-star-tables), [decan lists](https://aea.mcmaster.ca/index.php/en/database/decan-lists)

Consequences for implementation:

- store every object and sequence separately;
- distinguish visible signs, restorations, and editor-supplied ideal positions;
- preserve funerary/object context;
- do not map decans to modern tropical zodiac degrees without an explicit
  historical reconstruction and uncertainty;
- do not infer personality meanings from a decan's name or image; and
- do not merge later Hellenistic Egyptian astrology into a pharaonic source pack.

## Product boundaries

### Hemerology source explorer

Permitted after collation. Shows the selected Egyptian date, all surviving
prognosis units, narrative bases, actions, damage, translations, and witness
disagreements.

### Historical-date reconstruction

Permitted under a named chronological model. It must show the reconstructed date
and uncertainty. Competing anchors produce parallel results, not a hidden winner.

### Birth-day reading

Only a passage explicitly discussing birth can support a birth-specific result.
Otherwise the product may say what a selected calendar records for a reconstructed
day, but it must not turn that entry into personality, destiny, longevity,
relationship, medical, or vocational claims.

### Decan explorer

Permitted as a historical-astronomy/cultural feature after object data and image
rights are resolved. It is not presently a natal reader.

## Translation and provenance workflow

1. Acquire Bakir 1966 and both Leitz 1994 volumes legally.
2. Manifest every facsimile page and hash the controlling internal copies.
3. Align hieratic image, hieroglyphic transcription, transliteration, literal
   translation, and editorial translation by line.
4. Mark lacunae, restorations, uncertain signs, and later hands explicitly.
5. Collate Cairo 86637, Sallier IV, BM 10474, and the remaining witnesses without
   filling one witness's gap from another.
6. Obtain Egyptological review from specialists in Hieratic and Egyptian
   calendrics.
7. Resolve museum-image and modern-edition rights before public display.

## Validation gates

- The civil-calendar kernel must round-trip all 365 positions and reject day 31.
- The five additional days must not receive prognosis units without a source
  passage, and a lost section must remain unknown rather than becoming a
  historically negative rule.
- Every encoded value must reproduce the controlling edition's source locator.
- Independent double entry must agree on every visible prognosis sign.
- Damaged and missing units must remain non-results, not neutral values.
- A cross-witness view must expose disagreements and absent dates.
- Mutation tests must change the selected entry when season, month, day, witness,
  or chronological model changes.
- The modern statistical periodicity paper may audit the tabulation but cannot
  create ancient rules.
- An Egyptologist must blindly reproduce the pilot month from the source pack.

## Cultural and safety policy

- Never market an "Egyptian zodiac" from this corpus.
- Never conflate pharaonic, Ptolemaic/Hellenistic, Greco-Roman, Coptic, or modern
  revival systems.
- Do not transform dangerous, violent, medical, fertility, death, or ritual
  prescriptions into advice.
- Original prognosis language may be shown with historical-use-only context;
  the public reading must avoid deterministic harm claims.
- Identify object custody, acquisition history, and image rights where known.

## First bounded pilot

Build a **one-month, three-witness hemerology concordance**:

1. select one complete thirty-day month present in Cairo 86637, Sallier IV, and
   BM 10474;
2. collate all ninety prognosis positions per witness from facsimile and edition;
3. align narrative explanations and actions without synthesizing disagreements;
4. encode damage and restoration confidence;
5. run civil-calendar and witness-selection mutation tests;
6. have a second encoder and an Egyptologist independently reproduce the month;
7. publish only the source explorer until birth-specific passages and a defensible
   date-conversion use case are separately authorized.

The preliminary calendar-only prerequisite is complete; the one-month
hemerology concordance is not. Current artifacts are:

- `civil_calendar_spec.json`: 365-day model, chronology contract, hemerology
  boundary, source hashes, and product gates;
- `civil_calendar_rule_manifest.json`: eleven atomic calendar and abstention
  rules;
- `civil_calendar_validation_vectors.json`: seventeen boundary, wraparound,
  rejection, synthetic-conversion, and output-isolation fixtures;
- `validate_civil_calendar.py`: exhaustive 365-position bijection, recurrence,
  source-identity, rule-coverage, and product-boundary validation.
- `budge_sallier_iv_access_manifest.json`: acquired scan identity, preservation
  facts, plate map, inspected-page record, and interpretation boundaries;
- `validate_budge_sallier_access.py`: source hash, plate-span, preservation, and
  nonlive product-boundary validation.
