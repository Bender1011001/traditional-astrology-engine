# Tibetan astro-science source, lineage, and implementation audit

Status: secondary-source Phugpa arithmetic pilot complete; institutional concordance and interpretation incomplete; not production approval  
Updated: 2026-08-01

## Result of this pass

Tibetan astro-science is a living, institutionally taught composite tradition. “Composite” does not mean freely blendable: Men-Tsee-Khang explicitly distinguishes indigenous Ancient Tibetan material, Chinese-derived elemental systems, Indian-derived Kalacakra astronomy, arising-vowels practice, and major Phugpa/Tsurphu lineages. Men-Tsee-Khang identifies its own lineage as Phugpa.

The correct first implementation is therefore a **Men-Tsee-Khang/Phugpa calendar and elemental-calculation research profile**, developed with institutional or lineage-qualified review. A generic “Tibetan astrology” engine assembled from English popular books would be unacceptable.

## Institutional taxonomy

Men-Tsee-Khang's overview distinguishes:

- Ancient Tibetan astro-science and observation;
- old Chinese-derived elemental astrology (`rGya-rTsis rNying-Ma`, also `Byung-rTsis`/`Nag-rTsis`);
- new Chinese-derived almanac/astronomical material (`rGya-rTsis gSar-Ma`);
- Indian-derived Kalacakra astro-science (`dKar-rTsis` / `Dus-'Khor sKar-rTsis`);
- arising-vowels practice (`dByangs-'Char`);
- Tsurphu (`Tsurlug`) and Phugpa (`Phuglug`) calendar/astronomical lineages;
- additional historical systems that must not be silently normalized to Phugpa.

It lists natal, compatibility, obstacle-year, deceased, geomancy, weather/collective, and calendrical applications. Those are separate output domains with different safety and permission requirements.

Source: [Men-Tsee-Khang introduction](https://mentseekhang.org/introduction-to-tibetan-astrology/)

## Calendar/astronomy layer

The institutional overview names five calendrical components:

1. weekday (`gZa'` / vara);
2. lunar day (`Tshes` / tithi);
3. constellation (`sKar` / nakshatra);
4. conjunction (`sByor-Ba` / yoga);
5. practical half-tithi component (`Byed-Pa` / karana).

It also distinguishes solar, lunar, and zodiacal day systems; treats five visible planets, lunar nodes/eclipses, planetary positions relative to birth, and an Ascendant-like `Dus-'Byor`. These terms authorize research modules, not yet exact formulas.

Svante Janson's 86-page mathematical paper provides a modern algorithmic description and explicitly supports comparison among variants, skipped/repeated dates, lunar mansions, yoga, karana, and planetary calculations. It remains a secondary mathematical reconstruction and must be checked against Tibetan-language sources and institutional almanacs.

Sources:

- [Tibetan calendar mathematics](https://arxiv.org/abs/1401.6285)
- [Men-Tsee-Khang calendar publications](https://mentseekhang.org/calendar/)

## Official curriculum evidence

The inspected first-professional curriculum is stronger than a commercial table of contents because it identifies expected competencies and named teaching texts. It requires students to calculate and interpret:

- preliminary Kalacakra astronomy;
- foundational Elemental Astrology;
- constitutional types;
- twelve year signs;
- nine numeric squares (`sMewa`);
- eight trigrams (`sPar-kha`);
- elemental months;
- dates and hours;
- additional calendrical/material categories;
- a medical-horoscope unit.

The curriculum is a completeness checklist, not a substitute for the teaching texts or oral instruction. The presence of calculation, interpretation, and practical exercises shows that a lookup-table-only engine would be incomplete.

Source: [Men-Tsee-Khang first-professional curriculum](https://bcollege.mentseekhang.org/wp-content/uploads/2023/11/9-SRUG-KT.pdf)

## Engine/module boundaries

### A. Phugpa calendar profile

Required outputs include Tibetan year/month/day identity, Rabjung cycle, intercalary month, skipped/doubled lunar date, weekday, lunar day, mansion, yoga, karana, and lineage/version. It must match purchased institutional almanacs before release.

### B. Kalacakra astronomical profile

This module computes the named traditional astronomical quantities under the selected lineage. Modern ephemeris values may be shown as comparison but cannot silently replace traditional arithmetic.

### C. Elemental natal profile

Candidate families from the official taxonomy/curriculum include year sign, element relationships, constitutional type, `sMewa`, `sPar-kha`, elemental month/date/hour, and their qualified interactions. Exact formulas and judgments remain blocked until the controlling Tibetan texts and instruction are licensed and reviewed.

### D. Compatibility and obstacle-year profiles

These consume the validated elemental natal facts but require their own source procedures. They cannot be inferred by comparing generic element labels.

### E. Geomancy, deceased, medical, arising-vowels, and ritual profiles

These are separate, sensitive modules. Medical and deceased readings are not appropriate for automated consumer prediction. Arising-vowels and ritual material may be esoteric/restricted and must not be implemented without explicit lineage permission.

## Required configuration identity

```json
{
  "institution_profile": "mentseekhang",
  "calendar_lineage": "phugpa",
  "lineage_version": "named text/almanac/reviewer version",
  "module": "calendar|kalacakra_astronomy|elemental_natal|compatibility|obstacle_year",
  "source_texts": [],
  "almanac_series": [],
  "tibetan_transliteration_standard": "EWTS version",
  "translation_review": "review record",
  "traditional_arithmetic_profile": "version",
  "modern_comparison_ephemeris": null
}
```

Phugpa and Tsurphu outputs must never share a cache key or be averaged.

## Source acquisition plan

1. Obtain Men-Tsee-Khang's complete multi-year astrology curriculum and bibliography in Tibetan.
2. Purchase or license the named foundational textbooks and several consecutive almanacs.
3. Build a Wylie/Tibetan title-author-work-ID manifest using BDRC and institutional catalogs.
4. Record folio/page, edition, lineage, restriction status, rights, and checksum.
5. Have two qualified Tibetan-language astro-science practitioners identify which materials are textual, oral, lineage-restricted, or suitable for public automation.
6. Align translated terminology without treating Sanskrit, Chinese, and Tibetan cognates as automatically identical methods.

BDRC is a discovery repository; no BDRC item becomes a source until a stable work record and rights status are captured.

Source: [Buddhist Digital Resource Center](https://www.bdrc.io/)

## Validation design

### Calendar golden set

- at least ten consecutive Men-Tsee-Khang almanacs;
- every Tibetan New Year in the interval;
- all intercalary months;
- all skipped and doubled dates;
- month/day boundary instants;
- weekday, mansion, yoga, and karana samples;
- independent output from Janson's formulas and another scholarly implementation;
- Phugpa-versus-Tsurphu divergence cases.

### Elemental calculation set

- official curriculum exercises or institution-approved worked cases;
- boundary years/months/dates/hours;
- complete `sMewa` and `sPar-kha` cycles;
- positive and defeating relationship cases;
- practitioner blind reproduction from source inputs;
- mutation tests for each input component.

### Interpretation set

Every claim needs Tibetan passage/lesson provenance, translation review, prerequisites, exceptions, and an institution-approved public rendering. Practitioner agreement must be measured separately from calculation agreement.

## Cultural and safety gates

- Establish a paid or otherwise mutually agreed relationship with qualified reviewers; do not extract living expertise without consent.
- Preserve Tibetan names, lineage, and institutional attribution.
- Do not market the output as replacing a trained practitioner.
- Do not automate medical diagnosis, treatment, death prediction, funeral guidance, spirit diagnosis, or claims about epidemics/disasters.
- Do not expose esoteric or restricted instructions.
- Do not flatten Buddhist religious claims into generic wellness language or strip them of context merely to commercialize them.
- Provide a historical/cultural-use disclaimer and show which safe modules are available.

## Production gates

Tibetan output remains blocked until:

- a named institution/lineage profile is selected and reviewed;
- the source bibliography and rights are complete;
- calendar output passes the multi-year almanac suite;
- traditional arithmetic remains distinguishable from modern ephemeris comparison;
- elemental rules reproduce approved worked exercises;
- translations and terminology pass two-person review;
- sensitive modules are excluded or explicitly approved;
- all source and reviewer licenses permit commercial use.

## First bounded pilot

Build a **Phugpa calendar concordance**, not a natal reading:

1. acquire three initial consecutive Men-Tsee-Khang almanacs, expanding to ten;
2. encode the calendar profile from Janson and the selected Tibetan source;
3. compare every date, skipped/doubled day, and intercalary month;
4. publish a discrepancy report rather than tuning constants invisibly;
5. obtain Men-Tsee-Khang/qualified-practitioner review;
6. only then add year sign, `sMewa`, and `sPar-kha` calculations from approved teaching material.

## Phugpa arithmetic pilot result (2026-08-01)

The secondary mathematical half of the pilot is now encoded and passing:

- `phugpa_calendar_spec.json` locks the complete Janson PDF and TeX source
  identities, three documented epoch profiles, exact rational constants,
  intercalation and true-date rules, and the standard-versus-Lochen `a2` fork.
- `phugpa_calendar_rule_manifest.json` contains ten calendar-only rules. Birth
  data may select calendar facts, but every rule rejects interpretation and
  customer prediction.
- `phugpa_calendar_validation_vectors.json` contains ten compound vectors
  covering 31 published Losar dates (2000-2030), all Phugpa leap months in
  Table 7 (2000-2020), the complete 2012 skipped/repeated-day inventory in
  Table 8, three epoch profiles, boundary behavior, the 2025 Phugpa/Tsurphu
  divergence, and the three modern `a2` divergence dates named by Janson.
- `validate_phugpa_calendar.py` uses exact `Fraction` arithmetic. It does not
  use floating-point rounding, a modern ephemeris, or silent variant selection.

The 86-page PDF is hash-locked at
`7cafc7df563a3020849c86f4e397daa18b7f7f5ff46244403180aca90b9d0f77`;
the complete TeX source is
`edf45d3a0978a92cd3eff2482bfd258a4168424f4cfd24f9ead5a24c733a4a4b`.
The full source and PDF text were inspected, and rendered pages covering the
scope, tables, core formulas, variant warning, and weekday rule were visually
checked.

This does **not** establish institutional conformance. Janson states that he
does not read Tibetan and relies on secondary sources, and Men-Tsee-Khang
almanacs have not yet been acquired or licensed for systematic comparison.
The pack therefore sets `institutional_conformance: false`,
`interpretation_eligible: false`, and `live_engine: false`. The next gate is a
discrepancy-preserving comparison against at least three consecutive
institutional almanacs, expanding to ten, with Tibetan-language review.
