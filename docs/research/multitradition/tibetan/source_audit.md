# Tibetan astro-science source, lineage, and implementation audit

Status: secondary-source Phugpa arithmetic pilot complete; White Beryl access/rights blocker dissolved, extraction blocked on legibility not rights; institutional concordance and interpretation incomplete; not production approval  
Updated: 2026-08-02

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

## White Beryl and Vaidurya g.ya' sel access investigation (2026-08-02)

### What was actually tested

The engine module (`src/engine/multitradition/tibetan.py`) refuses sMewa (nine
numeric squares) and sPar-kha (eight trigrams) with the stated reason "no
sourced anchor," and this audit's own "Engine/module boundaries" section above
says their "exact formulas and judgments remain blocked until the controlling
Tibetan texts and instruction are licensed and reviewed." This pass tested that
claim the same way an earlier pass in this repository tested — and dissolved —
an assumed copyright blocker on the 16th-century Nahuatl Florentine Codex and
on CC-BY-SA Arabic/Latin texts: by actually going and fetching the primary
source, rather than reasoning from its presumed unavailability.

The controlling primary source for sMewa and sPar-kha is the *nag-rtsis*
("black calculation") half of the **White Beryl** (*bai DUr dkar po*, Vaidurya
dkar po) by sde srid Sangs rgyas rgya mtsho (Desi Sangye Gyatso, 1653-1705),
the same author and the same treatise whose *skar-rtsis* (calendrical/
astronomical) half Janson's paper already reconstructs for the Phugpa
calendar pack above.

### Finding 1: the rights/access blocker is FALSE

Both the White Beryl itself and Sangye Gyatso's own companion treatise
clarifying disputed points in it are public domain, fully identified, and were
retrieved in full during this pass:

| Work | BDRC item | Edition | Pages | Rights statement | Access restriction |
|---|---|---|---|---|---|
| *bai DUr dkar po* (White Beryl), vol. 1 | `bdrc-W30116` | New Delhi: T. Tsepal Taikhang, 1972; reproduced from a print from the Lhasa blocks of Burmiok Athing | 650 | **Public Domain** | `restrictedInChina` |
| *bai DUr dkar po* (White Beryl), vol. 2 | `bdrc-W30116` | same | 646 | **Public Domain** | `restrictedInChina` |
| *bai DUr g.ya' sel* ("Removing the Tarnish of the Beryl"), vol. 1 | `bdrc-W1KG12689` | 18th-century sde-dge redaction, 1976 facsimile | 628 | **Public Domain** | `openAccess` (no restriction at all) |
| *bai DUr g.ya' sel*, vol. 2 | `bdrc-W1KG12689` | same | 634 | **Public Domain** | `openAccess` |

`restrictedInChina` is a PRC-only distribution geoblock BDRC applies to
Tibet-related material, stated on the item's own metadata — it is not a
copyright restriction, and it did not block retrieval from outside China. The
companion text carries no restriction of any kind. All four volumes were
downloaded in full as PDFs (SHA-256 hash-pinned in
`sources/access_manifest.json`) with no login, paywall, or takedown
encountered.

This directly falsifies the "no sourced anchor" / licensing framing this track
previously carried for sMewa and sPar-kha, in the same pattern the project has
now seen twice before. **The correct statement is: the source exists, is
named, is public domain, and is retrievable in full. It was not previously
retrieved because no one had gone and fetched it.**

### Finding 2: the elemental-astrology content is real and locatable

An embedded-text-layer keyword search for the Tibetan strings *sme* (of
*sme ba*, སྨེ) and *spar kha* (སྤར་ཁ) across both White Beryl volumes found 20
hits out of 646 pages in volume 2, clustering at file-pages 308-348 and
recurring at 443-611, against only 7 scattered hits out of 650 pages in
volume 1. This is consistent with volume 1 being predominantly *skar-rtsis*
(the astronomical/calendrical material Janson reconstructs) and volume 2
carrying a substantial, plausibly dedicated *byung-rtsis*/*nag-rtsis*
(elemental astrology) chapter block — exactly the content this track needs.

One candidate page (volume 2, file-page 318) was rendered directly from the
retrieved PDF at 6x and then 14x zoom (PyMuPDF, no OCR involved) and read
visually. It shows genuine, continuous Tibetan dbu-can prose with the printed
running folio number **308** clearly legible in the margin — real primary-source
text, not a blank, missing, or corrupted page. The rendered images are
hash-pinned at `sources/page_images/w30116_v2_p318_folio308_full.png` and
`..._detail.png`.

### Finding 3: the real remaining blocker is legibility, not rights — and it is a different kind of blocker

Two independent paths to machine-readable text were checked and both failed
for different, informative reasons:

1. **Automated OCR.** Internet Archive's generated `djvu.txt`/hOCR layer for
   both works was inspected directly and is unusable: English and decorative
   front matter is transliterated into pseudo-Tibetan Unicode noise, and body
   text interleaves short legible runs with long garbled strings. No content
   in this pack rests on this OCR text, and none should be, by anyone.
2. **Direct visual reading of the scan.** This is the technique that already
   worked for this repository's Byzantine Greek track (nine CCAG page images
   read directly). It was attempted here at the same zoom levels. The White
   Beryl's 1972 print is genuinely legible as Tibetan script — individual
   syllables and the folio number were confirmed — but sentence-level
   transcription of technical procedural content could not be carried to
   defensibility-grade confidence in a single pass. The companion *g.ya' sel*
   text (sde-dge redaction) was checked as a possible easier alternative and is
   **not**: at the same 14x zoom it is printed in a markedly more cursive,
   lower-contrast style and was less legible, not more.

This is a **different blocker class** from the one this track previously
recorded. Under `../DEFENSIBILITY.md`'s own table, "original not retrievable"
is the row for a genuine access problem — and that row does not apply here,
because the original **is** retrievable. What remains is closer to that
standard's other carve-out, "rule promotion into a validated pack... wants
independent review," combined with the access-quality problem this repository
has already named twice elsewhere: the Byzantine track's OCR-corruption of a
rule-bearing verb, and Sukuyodo's "CBETA's linearization of \[grid\] tables is
unusable as data." A legible-in-principle woodblock print that a single
unreviewed pass cannot confidently transcribe is an evidentiary-quality gate,
not a rights gate, and it is recorded as such.

### What this finding does NOT license

Two secondary, English-language pages (`tibastro.be/Parkha/ParkhaGeneral` and
`kunjung.org/general-4`) were found during this investigation and do state
specific numeric procedures — a mother's-age-based *parkha* formula with three
counting-method variants, and a stated *mewa* descent sequence
1, 9, 8, 7, 6, 5, 4, 3, 2. **Neither cites the White Beryl, or any other named
primary or scholarly source, for any of it.** They are not used here and
should not be used in a future pass either: promoting them would be exactly
the "generic 'Tibetan astrology' engine assembled from English popular books"
this audit's own opening section already calls unacceptable. Dissolving a
false rights blocker does not create license to substitute an unsourced
convenience; it only obligates going back to the primary source until it
yields, or naming a qualified second source (a peer-reviewed monograph, a
named Tibetan-reading collaborator) that actually engages with it.

### Updated "what blocks what"

| Item | Old framing | Corrected framing |
|---|---|---|
| sMewa construction | "no sourced anchor" (implies unavailable) | **Source identified, public domain, retrieved in full.** Blocked on legible transcription of a specific woodblock print, not on rights. |
| sPar-kha construction | "no sourced anchor" | Same as above. |
| Life-force squares (srog/lus/dbang-thang/rlung-rta), compatibility/elemental judgment tables | "depend on conventions the research pack has not fixed" | Presumed to live in the same White Beryl chapter block (not independently folio-located this pass); same legibility gate applies once located. |
| Institutional Men-Tsee-Khang almanac conformance for the calendar pack | acquisition/licensing pending | Unchanged by this pass — a separate document (living-institution almanac series), not the White Beryl. |

### First bounded next pilot for this sub-track

1. Either (a) obtain a genuinely expert Classical-Tibetan paleographic pass
   over White Beryl vol. 2 file-pages 308-348 and 443-611 (the located
   chapter block), or (b) locate a modern computer-typeset edition of the same
   chapter (a `krung go'i bod rig pa dpe skrun khang` / `mi rigs dpe skrun
   khang`-style reprint would OCR and read far more reliably than a 1972
   photostat of a xylograph) — neither requires any new rights clearance.
2. Once legible, extract sMewa cycle construction, sPar-kha assignment, and
   the life-force/compatibility tables the same way this repository's other
   tracks extract rules: exact passage citation, `engine_translation_unreviewed`
   grade, evidence grade A/B, independent Tibetan-reading review before any
   rule is promoted.
3. Do not, at any point, substitute the unsourced popular-web arithmetic named
   above for this work.
4. See `whitebeyl_rule_manifest.json`, `whitebeyl_validation_vectors.json`, and
   `sources/access_manifest.json` for exactly what was hash-pinned and verified
   this pass, and `defensibility_spec.md` in this directory for how this
   reclassifies the core-technique checklist.
