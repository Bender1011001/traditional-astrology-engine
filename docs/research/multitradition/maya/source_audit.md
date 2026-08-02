# Maya calendars, codical almanacs, and living daykeeping audit

Status: calendar pilot research-verified; codex and interpretation pilots incomplete; not production approval  
Updated: 2026-08-01

## Result of this pass

There is no source basis for a single universal “Mayan astrology birth sign” engine. The evidence supports at least three distinct products:

1. **calendar conversion** — Long Count, Tzolk'in/Chol Q'ij, Haab, and Calendar Round under a named correlation;
2. **codex almanac/astronomical reader** — page-specific reconstruction of Postclassic almanacs and tables;
3. **living community daykeeping** — contemporary K'iche', Yucatec, or other community practice taught by named day keepers with permission.

Ancient codex interpretation and living practice may illuminate one another, but neither may impersonate the other. Regional language, community, time period, manuscript, epigraphic reading, and correlation constant must be visible in every result.

## Ancient codex evidence

### Dresden Codex

INAH and the holding library SLUB independently describe a manuscript containing 260-day divinatory almanacs plus astronomical, calendrical, meteorological, and ritual tables. The source is sufficiently structured for a page-addressable research engine.

The inspected institutional page map includes:

- miscellaneous and lunar-goddess almanacs;
- Venus pages 24 and 46–50, built around a 584-day cycle;
- eclipse pages 51–58;
- multiples of 78 and possible Mars material;
- K'atun prophecy;
- seasonal/rain tables;
- New Year ceremonies;
- farmer's almanacs;
- page-level scribal groupings proposed by current scholarship.

SLUB emphasizes that almanacs addressed favorable/unfavorable timing for concrete activities such as planting, harvesting, trade, hunting, warfare, marriage, birth, and health. This does not authorize a generic personality description for everyone born on a Tzolk'in day.

Sources:

- [INAH Dresden Codex project](https://www.codicededresde.inah.gob.mx/bienvenida/)
- [SLUB content map](https://www.slub-dresden.de/en/explore/manuscripts/the-dresden-maya-codex/content)
- [SLUB manuscript overview and provenance](https://www.slub-dresden.de/en/explore/manuscripts/the-dresden-maya-codex)

### Other surviving codices

The Maya Codex of Mexico has a dedicated INAH research portal and is essential for an independent Venus-almanac comparison. Madrid and Paris require equivalent holding-institution manifests. None should inherit Dresden page meanings merely because cycles or iconography overlap.

Source: [Codice Maya de Mexico](https://www.codicemayademexico.inah.gob.mx/)

## Living-practice evidence

The Smithsonian's Living Maya Time project identifies contemporary K'iche' day keepers by name and explains current highland Guatemalan Chol Q'ij practice. It also distinguishes Yucatec printed Tzolk'in contexts. The calendar is used as a symbolic value system within communities, not as detached commercial content.

The Smithsonian calendar converter demonstrates Long Count, Haab, and Tzolk'in outputs and links to day meanings. The inspected interface does not expose its correlation constant or implementation, so it is an external reference tool—not a source to copy.

Sources:

- [Smithsonian calendar system](https://maya.nmai.si.edu/calendar/calendar-system)
- [Smithsonian calendar converter](https://maya.nmai.si.edu/calendar/maya-calendar-converter)
- [Corn and calendar traditions with named contributors](https://maya.nmai.si.edu/corn-and-maya-time/corn-and-calendar-traditions)

## Calendar correlation is configuration, not fact

Mapping a Long Count to Julian/Gregorian dates requires a correlation constant. The Goodman–Martinez–Thompson family is widely used, but inspected peer-reviewed scholarship discusses 584,283, 584,285, 584,286, and region-specific alternatives such as an 18–20-day displacement for Isthmian texts. The choice can change every birth-date conversion and astronomical match.

The canonical engine field must therefore be:

```json
{
  "correlation_id": "gmt_584283",
  "correlation_constant": 584283,
  "scope": "lowland_maya_default_reconstruction",
  "authority": "specific publication and pages",
  "alternatives": [],
  "confidence": "declared",
  "notes": "not silently generalized to Isthmian or other systems"
}
```

Sources:

- [Cambridge, Mayan Calendars](https://www.cambridge.org/core/books/abs/calendrical-calculations/mayan-calendars/A520E2C29F19D15134A38C5D931EB1BF)
- [peer-reviewed discussion of correlation variants](https://www.cambridge.org/core/journals/latin-american-antiquity/article/role-of-solar-observations-in-developing-the-preclassic-maya-calendar/CE9899861546A50ACE1819A6796D8694)

## Calendar kernel

The first implementation must compute, with exact modular arithmetic:

- Long Count components and total-day value;
- Tzolk'in number and day name;
- Haab month/day including Wayeb;
- Calendar Round pair and 18,980-day recurrence;
- supplementary/lunar series only under a source-specific module;
- correlation-specific Julian Day and civil-calendar conversions;
- BCE astronomical year-number handling;
- alternative outputs for each enabled correlation.

All cycles need direction and zero-point tests. Never infer a day meaning before the calendar result is independently validated.

## Codex rule model

A codical almanac rule is not just a date keyword.

```json
{
  "codex": "dresden",
  "page": "19b",
  "section": "page register used by edition",
  "scribe_hypothesis": "named scholarly attribution",
  "cycle_length_days": 260,
  "anchor_dates": [],
  "interval_sequence": [],
  "day_name_positions": [],
  "glyph_transcription": [],
  "glyph_reading_version": "epigraphic publication",
  "actors_or_deities": [],
  "activity_domain": [],
  "augury": "direct reading or null",
  "ritual_context": [],
  "damaged_or_uncertain": [],
  "interpretation_status": "direct|scholarly_inference|disputed"
}
```

Images, numerals, glyphs, and intervals must be linked. A modern prose summary cannot be the sole authority for an omen.

## Product boundaries

### Calendar converter

Safe initial product if it exposes correlation and sources. It can show stable cyclic facts and alternate civil dates.

### Ancient almanac explorer

Accept a codex/page/cycle or a converted day, then show relevant passages/images with uncertainty and scholarship. It is historical education, not a personal destiny report.

### Birth-date historical reconstruction

May show which calendar expressions and codical cycles coincide with a birth date under a named correlation. It must not claim that the codex was designed to provide a complete individual natal reading unless a source demonstrates that exact use.

### Living community reading

Requires a named community/teacher source, permission, language and regional identity, training context, and review. A day meaning cannot be blended across K'iche', Yucatec, and ancient hieroglyphic sources.

## Translation and epigraphy workflow

1. Build a complete page-image manifest from holding institutions.
2. Select current scholarly facsimile, transcription, and epigraphic commentary.
3. Record each glyph reading with publication/version and uncertainty.
4. Separate numeric/calendar decoding from iconographic and divinatory interpretation.
5. Have a Maya epigrapher review codex encodings.
6. Have relevant community contributors review living-practice material and consent to public use.
7. Preserve original Mayan-language terms and regional variants.

## Validation gates

- Calendar arithmetic must match Smithsonian reference vectors and an independent scholarly implementation.
- Every supported correlation must have round-trip Long Count ↔ Julian Day tests.
- Dates near civil calendar reforms and BCE boundaries must use the shared historical-time contract.
- Dresden cycle tables must reproduce their recorded interval totals before any interpretation is attached.
- Venus/eclipse calculations must compare ancient tabular structure, modern astronomy, and correlation/Delta-T uncertainty without silently “correcting” the manuscript.
- Every codical claim must cite a page and current epigraphic reading.
- Living meanings need named-contributor permission and community-specific review.

## Cultural and safety policy

- Do not market a “Mayan zodiac.”
- Do not present ancient warfare, sacrifice, illness, death, flood, eclipse, or famine imagery as a current literal prediction.
- Do not publish ritual instructions or community knowledge without permission.
- Do not conflate Maya, Mexica/Nahua, Zapotec, Mixe-Zoque, or other Mesoamerican calendars because they share a 260-day structure.
- Respect holding-institution image rights and colonial provenance.
- Clearly label historical reconstruction versus living practice.

## First bounded pilots

### Pilot 1: calendar conformance

Implement Long Count, Tzolk'in, Haab, and Calendar Round under `gmt_584283` plus at least one alternate GMT variant. Test against Smithsonian and scholarly vectors, with correlation shown in every result.

Pilot 1 is now complete as a research artifact, not as a live engine:

- `calendar_kernel_spec.json` records the five Long Count weights and radices,
  Tzolk'in and Haab zero points, Yucatec and K'iche' label profiles, the
  18,980-day Calendar Round, explicit `gmt_584283` and `gmt_584285` profiles,
  proleptic-Gregorian/astronomical-year semantics, and publication limits.
- `calendar_rule_manifest.json` contains eight calendar-only rules. Birth data
  may select calendar facts, but every rule is interpretation-ineligible and
  has `customer_prediction: false`.
- `calendar_validation_vectors.json` supplies twelve reference, boundary,
  mutation, correlation-sensitivity, naming-profile, and safety vectors.
- `validate_maya_calendar.py` independently reproduces the Smithsonian cycle
  origin (`4 Ajaw 8 Kumk'u`), the December 21, 2012 anchor (`4 Ajaw 3
  K'ank'in`), and FAMSI's July 24, 2026 result (`13.0.13.14.3`, `1 Ak'b'al 16
  Xul`) under 584283. It also validates Long Count and Wayeb rollovers, the
  full Calendar Round recurrence, correlation sensitivity, and fail-closed
  invalid inputs.

The Smithsonian PDF used for the arithmetic/name concordance was hash-locked
as SHA-256
`a12c9e4d8716abdb1e06c05f93778b5ae7e6658614f94a47a157179a76f6e5fa`
(6,851,033 bytes, 10 pages); all text and representative rendered pages were
inspected. The open PNAS radiocarbon study independently confirms the additive
584,283 coefficient. The alternate 584,285 profile is retained for sensitivity
testing, not silently selected.

Important notation boundary: the linear arithmetic origin is
`0.0.0.0.0`, while the Smithsonian source presents the mythic creation-cycle
boundary as `13.0.0.0.0`. The validator preserves both contexts instead of
collapsing them.

### Pilot 2: one Dresden almanac

Select one bounded, well-studied almanac such as page 19b. Encode images, numerals, intervals, glyph readings, and auguries from page-level scholarship. Have a Maya epigrapher reproduce the result before expanding.

No personal reading generator should be built until both pilots pass and a living-practice partnership defines what, if anything, may responsibly be offered beyond historical reconstruction.
