# Islamicate / Persian astrological source audit

Status: bounded al-Biruni validator complete; not production approval  
Updated: 2026-08-01

## Result of this pass

The project can eventually support several high-quality Islamicate astrological engines, but it must not ship a single anonymous “Arabic” or “Persian” method. The surviving corpus is multilingual and highly transmitted: authors synthesized Greek, Persian, Indian, and local materials; works moved through Arabic, Persian, Hebrew, Greek, and Latin; translations sometimes altered content; and the same author wrote for different branches.

The production unit must therefore be an **author + work + textual lineage + branch + convention pack**, not a civilization label.

Recommended initial packs:

1. `al_biruni_tafhim_wright_1934_reference`
2. `abu_mashar_great_introduction_2019_arabic`
3. `al_qabisi_introduction_2004_arabic`
4. `mashallah_astrological_history_1971`
5. `sahl_interrogations_arabic_witness`
6. `abu_mashar_religions_dynasties_2000_mundane`
7. `al_kindi_weather_transmission_2000`

These packs may share audited astronomical facts, but they may not silently share judgments.

## Source map

| Author/work | Branch supported | Current evidentiary value | Main limitation |
|---|---|---|---|
| al-Biruni, `Tafhim` / `Book of Instruction` | reference definitions, astronomical and astrological elements | institutional Halle scan of the complete facing Arabic/English edition plus a locally hashed English astrology extract; six relevant facing-page pairs inspected and 15 bounded rules validated | Arabic pages are visually aligned but not independently translated; major firdaria durations and a complete natal procedure are not authorized |
| Abu Ma'shar, `Great Introduction` | foundational doctrine and classifications | 2019 critical Arabic with facing English, Latin variants, Greek fragment | copyrighted; full volumes not yet locally inspected |
| al-Qabisi, `Introduction` | concise introductory doctrine | 2004 Arabic/Latin/English critical edition and extensive manuscript record | Arabic and Latin transmissions require separate manifests |
| Masha'allah, `Astrological History` corpus | historical astrology plus separately preserved natal works/horoscopes | scholarly text, translation, astronomical chronology, commentary | works in appendices must not be collapsed into the main historical text |
| Sahl ibn Bishr | planetary conditions, interrogations, elections, times | Arabic manuscript leads plus large Latin transmission | no selected controlling Arabic edition; popular modern translations are not sufficient authority |
| Abu Ma'shar, `Religions and Dynasties` | great conjunctions and collective history | critical Arabic/Latin/English edition | attribution may include Ibn al-Bazyar; not natal |
| al-Kindi weather letters | weather/mundane astrology | edited Hebrew and Latin witnesses with English translation/commentary | Arabic original is lost; not natal or horary |

## Evidence already present in the repository

The existing local Wright scan has SHA-256 `b5b15d3a25842072d680dd6e6d341c992bff0c2a43141d36b47e6a7e2cc761d2`. Visual inspection corrected its earlier registry description: it is a 128-page English extract covering sections 347-530, not a file containing the facing source-language pages. The complete facing Arabic/English edition was therefore located at the Universitaets- und Landesbibliothek Sachsen-Anhalt. Its METS and 718-canvas IIIF structure were inspected, and the relevant English/Arabic page pairs were acquired and hash-locked for the pilot.

Two useful examples demonstrate the required passage-level discipline:

- Section 395 verifies a seven-planet firdaria sequence with day births beginning from the Sun, night births from the Moon, and equal subdivision of a major period among seven rulers. It does **not** authorize node periods; those must be attributed to a later source if enabled.
- Section 496 distinguishes `halb` and `hayyiz`; Mercury remains conditional, and the conditions modify a planet rather than magically canceling every debility or changing malefic nature into benefic nature.

This is the correct rule-record model for all further extraction: exact passage, direct scope, explicit non-claims, and no later accretion attributed backward.

Sources:

- [al-Biruni research scan](https://www.skyscript.co.uk/pdf/pubs/texts/albiruni/docs/albiruni.pdf)
- [Halle institutional facing edition](https://doi.org/10.25673/99914)
- [Halle IIIF manifest](https://opendata.uni-halle.de/json/iiif/1981185920/101870/3d85daea-887c-4aa5-abf1-562d6add6731/manifest)
- Local registry: `src/database/data/doctrine_sources.json`

## Critical-edition leads

### Abu Ma'shar's `Great Introduction`

Brill describes the 2019 edition as a critical Arabic text with facing English translation, variants from John of Seville and Hermann of Carinthia's Latin translations, unique Latin passages in appendices, a Greek fragment, and multilingual glossaries. This is strong enough to become a controlling doctrinal source after lawful acquisition and full inspection.

Source: [Brill Scholarly Editions](https://scholarlyeditions.brill.com/library/urn%3Acts%3AarabicLit%3A0988AbuMashar/)

### al-Qabisi's `Introduction`

The Warburg co-publisher states that the work survives in at least twenty-five Arabic manuscripts and more than two hundred Latin manuscripts, and that the 2004 edition includes Arabic, English, and Latin versions. The scale of transmission makes a generic “Alcabitius says” rule unsafe unless its textual lineage is recorded.

Source: [critical-edition description](https://www.ninoaragnoeditore.it/opera/al-qabisi-the-introduction-to-astrology)

### Masha'allah's corpus

The Harvard edition separates text, translation, chronology/astronomy, and commentary. Its appendices separately include a natal work and additional horoscopes. Each component must become a distinct work record with its own rules and chart recomputation.

Source: [Harvard edition record](https://www.degruyterbrill.com/document/doi/10.4159/harvard.9780674863965/html)

### Sahl ibn Bishr

The Qatar Digital Library overview identifies Arabic manuscript witnesses at the British Library and Yale and describes an introductory section on zodiacal signs/houses and sixteen planetary conditions followed by interrogations. It also notes extensive Latin transmission. This is a strong manuscript-discovery path, not yet a controlling edition.

Source: [Qatar Digital Library overview](https://qdl.qa/en/sahl-ibn-bishr-and-rise-astrology-abbasid-times)

### Branch-specific non-natal works

Abu Ma'shar's `Book of Religions and Dynasties` treats conjunctions and other factors in collective historical prediction and carries an explicit attribution issue. Al-Kindi's weather letters survive through Hebrew and Latin rather than a found Arabic original. Both require branch-specific engines and prominent transmission labels.

Sources:

- [Abu Ma'shar on historical astrology](https://brill.com/downloadpdf/edcollbook/title/17142.pdf)
- [al-Kindi weather edition](https://www.routledge.com/Scientific-Weather-Forecasting-In-The-Middle-Ages-The-Writings-of-Al-K/Bos-Burnett/p/book/9780710305763)

## Engine/module boundaries

### Reference/doctrine layer

Candidate facts and definitions include signs, houses, planetary attributes, aspects, lots, dignities/conditions, sect-related states, cycles, and calendrical/astronomical terminology. A reference text may define a concept without prescribing a complete judgment procedure; `definition` and `executable_rule` must be different record types.

### Natal layer

Required source families include:

- nativity chart construction and house convention;
- planetary condition and relevance hierarchy;
- luminaries, Ascendant, rulers, lots, and significators;
- longevity/vitality material, which must remain research-only or suppressed;
- profession, status, relationships, family, travel, and other topics only when a work supplies a complete procedure;
- annual revolutions and time-lord methods only from their own works/passages.

### Interrogations/questions layer

This is not a birth-input product. It needs question time/place, radicality or validity conditions where attested, house/significator assignment, application/separation, reception, prohibition, translation/collection, planetary impediments, outcome, and timing. Sahl and later authors must remain separately configurable.

### Elections layer

Election rules require a requested action, time window, location, target houses/significators, Moon conditions, relevant prohibitions, and source-specific priorities. A natal engine cannot generate an election merely by reusing benefic scores.

### Revolutions and historical/mundane layer

Solar ingress, annual revolution, conjunction, comet, weather, dynasty, ruler, and collective-event materials are independent branches. They require event charts and historical context, not a person's birth alone.

## Rule schema additions

```json
{
  "author": "canonical author ID",
  "work": "canonical work ID",
  "branch": "natal|question|election|revolution|mundane|weather|reference",
  "source_language": "Arabic|Persian|Hebrew|Greek|Latin",
  "textual_lineage": "manuscript/translation family",
  "passage": "book/chapter/section/page/folio",
  "rule_kind": "definition|calculation|eligibility|priority|judgment|exception",
  "predicates": [],
  "result": {},
  "exceptions": [],
  "translation_status": "direct|reviewed|legacy|lost_original_transmission",
  "publication_limits": [],
  "non_claims": []
}
```

## Unresolved calculation/convention matrix

Every work pack must explicitly resolve or declare irrelevant:

- tropical or other zodiac frame and precession assumptions;
- house division and exact cusp use;
- apparent versus mean positions;
- planetary latitude and visibility;
- lots formula and day/night reversal;
- aspect doctrine, orb/body/ray distinction, application, and dexter/sinister handling;
- terms, triplicity, decans/faces, joys, sect, `hayyiz`, `halb`, and other condition tables;
- planetary years and time-period constants;
- calendar/era, local time, and historical astronomical table (`zij`) assumed by worked charts;
- whether modern ephemeris recomputation is a reconstruction or a replacement for the author's numerical framework.

The engine must preserve both `source_recorded_value` and `modern_recomputed_value` when they differ.

## Transmission and translation workflow

1. Acquire the critical edition and all legitimately accessible source-language witnesses.
2. Record work identity; reject titles that conflate distinct Arabic works under one Latin title.
3. Align Arabic/Persian text, critical apparatus, English translation, and relevant Latin/Hebrew/Greek witnesses.
4. Mark lacunae, editorial supplements, mistranslations alleged by editors, and content unique to a translation.
5. Have an Arabic/Persian history-of-science specialist review terminology and rule extraction.
6. Encode direct rules and exceptions; separate editor reconstruction and modern-practitioner synthesis.
7. Recompute every worked horoscope with both source-era and modern astronomical profiles where possible.

## Validation gates

- Each rule must reproduce at least one worked or textually explicit positive case.
- Each condition/exception must have a negative or mutation case.
- Two independent readers must agree on the passage-to-predicate encoding.
- Arabic and translated passages must be cited together when available.
- Author packs must be tested against one another to prove that disabling cross-pack inheritance changes the result.
- The engine must refuse a “generic Islamicate” mode unless it is explicitly a comparative view that labels every claim by author.
- Rights review must approve every displayed quotation and translation.

## Safety and dignity policy

Historical texts may make deterministic statements about death, illness, disability, pregnancy, sexuality, enslavement, religion, ethnicity, class, rulers, war, and disasters. The consumer layer must suppress medical diagnosis, lifespan/death prediction, criminal accusations, reproductive certainty, demeaning status claims, and real-world political/disaster forecasts.

Magical, talismanic, ritual, or religious instructions require a separate cultural/safety/permissions review and are outside the first astrology engine. They must not be generated by improvising from correspondence tables.

## First bounded pilot

Build an **al-Biruni reference and condition validator**, not a full reading:

1. ingest the locally hashed Wright witness as a page-addressable source;
2. encode only passages visually aligned to their facing source-language page, while keeping linguistic verification false until specialist review;
3. start with firdaria section 395 and `hayyiz`/`halb` section 496;
4. add condition tables only after full passage review;
5. create counterexamples for node-period attribution, Mercury conditionality, and false cancellation of debility;
6. obtain Arabic/Persian specialist review;
7. then compare the same concepts in Abu Ma'shar and al-Qabisi without merging them.

The first production reading should wait until at least one complete author/work natal procedure—not merely a collection of definitions—passes these gates.

## Bounded pilot result

The first pilot is now implemented as research infrastructure:

- `al_biruni_reference_condition_spec.json` records the author/work/edition identity, two source artifacts, six English/Arabic facing-page pairs, exact page-image hashes, the structural formulas, and publication gates.
- `al_biruni_reference_condition_rule_manifest.json` contains 15 author-scoped rules for diurnal and nocturnal firdaria order, equal-seventh subperiod structure, node and duration exclusions, sign and planet classifications, Mercury's explicit-resolution requirement, `halb`, `hayyiz`, the Mars case, the limited joy statement, and the publication boundary.
- `al_biruni_reference_condition_validation_vectors.json` contains 13 compound vectors covering every rule.
- `validate_al_biruni_reference_conditions.py` passes all 13 vectors and exhaustively checks the implication `hayyiz -> halb` across 288 fixed-planet/sect/horizon/sign combinations.

The validator deliberately cannot calculate age/date firdaria boundaries because section 395 does not supply the major-period duration table. It also refuses to default Mercury when its contextual basis is missing, excludes node periods from this author/work pack, and never turns `halb` or `hayyiz` into a complete favorable judgment. `live_engine`, customer eligibility, interpretation eligibility, and full-reading eligibility remain false.

The next gate is independent Arabic review of the six encoded passage pairs. After that, the same concepts should be extracted separately from Abu Ma'shar and al-Qabisi so cross-author differences can be tested rather than blended.

## Abu Ma'shar and al-Qabisi access gate

The comparison-source gate found a lawful, structured source layer that is more
useful than publisher metadata but still short of rule-extraction authority.
Version 0.4.0 of the University of Wurzburg Arabic and Latin Corpus exposes
downloadable, passage-addressable TEI under CC BY-SA 4.0 for:

- Abu Ma'shar's *Great Introduction*: the Arabic text derived from the 2019
  critical edition plus separate Hermann of Carinthia and John of Seville Latin
  lineages;
- al-Qabisi's *Introduction*: Arabic and John of Seville Latin derived from the
  2004 critical edition; and
- Abu Ma'shar's *Abbreviation of the Introduction*: Arabic and Adelard of Bath
  Latin derived from the 1994 critical edition.

All seven response bodies were retrieved, byte-counted, SHA-256 pinned, and
structurally inspected. Together they contain edition-page markers and explicit
work divisions, so they can support a passage concordance. They do **not**
expose the modern English translations or the complete critical apparatus.
Consequently, no doctrine was encoded from them in this pass.

`abu_mashar_al_qabisi_access_matrix.json` records the exact artifacts, hashes,
division and page-marker profiles, controlling editions, rights boundary, and
work/translation separation rules. The companion
`validate_abu_mashar_al_qabisi_access.py` checks all local invariants and can
re-download the seven TEI files with `--verify-remote`; that remote verification
passed on 2026-08-01.

The central negative finding is operationally important: the *Great
Introduction* and its seven-chapter *Abbreviation* are different works, while
Hermann and John are separate Latin translation lineages. Similar titles,
shared authorship, or agreement among Latin witnesses cannot authorize rule
inheritance. The next rule pass therefore remains gated on lawful access to the
English translations and apparatus, Arabic specialist review, and a second
independent passage-to-predicate reader.

## Candidate concordance result

`al_biruni_abu_mashar_al_qabisi_candidate_concordance.json` now provides a
structural comparison layer for five concepts: sign/planet gender and sect,
`halb`/`hayyiz`, planetary house joys, firdaria year values, and firdaria
sequence/subperiod procedure. It contains 30 candidate passage records across
the seven TEI artifacts plus the existing al-Biruni baseline. It stores passage
addresses and short search tokens, not source quotations or inferred rules.

The comparison produced eight explicit variant observations:

- Abu Ma'shar's Great Introduction Arabic p. 800 gives Mars seven firdaria
  years. Hermann p. 143 gives eight. John p. 310 gives Mars seven but a
  bracketed Moon value of eight; John's displayed values sum to 74 while its
  stated total is 75.
- The Arabic Abbreviation p. 80 gives values summing to and explicitly totaling
  75. Adelard p. 136 preserves the same listed values but states 77.
- Al-Qabisi Arabic p. 60 uses separate `halb` and `hayyiz` forms in a staged
  definition, whereas John p. 266 uses `alhaiz` and `aiz`. The apparatus and an
  Arabic specialist must determine whether this is terminological collapse,
  orthographic variation, or another editorial issue.
- The Great Introduction p. 786 and Abbreviation p. 52 contain a surface
  `halb`-form immediately glossed through dignities and joys, unlike the
  horizon-condition use in al-Qabisi and the al-Biruni baseline. Surface-form
  matching is therefore explicitly unsafe.
- Adelard renders the Abbreviation's named `hayyiz` condition as *competentia*,
  demonstrating that Latin discovery cannot rely only on transliterations.
- Al-Qabisi's inspected planet chapter describes Mercury as male and diurnal,
  while the al-Biruni pilot keeps Mercury conditional. This is retained as an
  author-scoped difference candidate, never a shared default.
- Al-Biruni section 395's omission of node periods and duration values remains
  a passage-scope boundary. Values found in al-Qabisi or Abu Ma'shar are not
  backfilled into al-Biruni.

These are not editorial corrections. The validator recomputes the listed
firdaria totals, proves that the disagreements remain present, and fails if any
candidate is promoted to rule-ready, live, or customer-eligible status.

## al-Qabisi direct extraction result (2026-08-02)

The blocking gate recorded above ("no doctrine was encoded from them in this
pass", "remains gated on lawful access to the English translations") was a
conflation this corpus has since corrected. Per
[../DEFENSIBILITY.md](../DEFENSIBILITY.md), "Translation is not a gate for
quotation": al-Qabisi's *Introduction* is a 9th-10th-century (composed
mid-10th century, dedicated to Sayf al-Dawla of Aleppo) public-domain Arabic
text. Independent specialist review is required before any rule is *promoted
into a validated, live pack* - it was never required before the engine could
*read the public-domain original and quote it directly*. That distinction had
not yet been acted on for al-Qabisi specifically; it now has.

**Provenance, precisely.** The Arabic text used is
`wurzburg_tei/al_qabisi_introduction_arabic_tei.xml`, fetched via
`fetch_wurzburg_tei.py` and verified against the hash already recorded in
`abu_mashar_al_qabisi_access_matrix.json`
(`sha256 3267ff80d6b10dbecf3a2eed7a51495db0842dd20d711a5952cbcbfa05657add`).
Per its own TEI header: transcribed by Kaddour Alkassem and Azzam Hasan;
series "Arabic and Latin Corpus", edited by Dag Nikolaus Hasse together with
Jon Bornholdt, Andreas Büttner, and Irina Galynina; published by the
Institute of Philosophy, University of Würzburg (Residenz, Südflügel, 97070
Würzburg, Germany); corpus version 0.4.0, compiled 2026-06-30; licence
**Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**;
source edition cited in the TEI `sourceDesc`: al-Qabīṣī (Alcabitius), *The
Introduction to Astrology*, ed. and transl. Charles Burnett, Keiji Yamamoto
and Michio Yano (London/Turin, 2004). The companion John of Seville Latin TEI
witness for the same work (`al_qabisi_introduction_john_latin_tei.xml`,
`sha256 0766e56b232809e763e8ae1f1cbcbd131ce3649df811ef319e2c1d6803de74b8`) was
also fetched and hash-verified in this pass via the same script, for future
Arabic/Latin variant-concordance work; it was not used as a source for any
rule in this pass.

**What survives and in what shape.** The TEI is a flat, page-addressable
transcription: one `<div type="book">` containing five `<div type="chapter"
n="I".."V">` elements (matching al-Qabisi's own stated five-differentia
structure, given in his own preface: I - the essential and accidental states
of the zodiacal sphere; II - the natures of the seven planets; III - what
happens to the seven planets in themselves and to each other; IV -
interpretation of the astrologers' technical terms; V - the compendium of the
lots), 206 paragraphs total, with `<pb n=/>` markers reproducing the 2004
edition's own pagination (18-154) and four `<table>` elements (the Egyptian
bounds table, the face/decan table, a masculine/feminine-degree table, and a
"wells"-degree table) using Arabic abjad numerals. No lacunae or editorial
brackets were encountered in the transcription; the text reads as continuous.

**What was done.** All five chapters were parsed and read directly in Arabic.
54 rules and 14 validation vectors were extracted into
`al_qabisi_rule_manifest.json` and `al_qabisi_validation_vectors.json`, each
citing chapter, paragraph, and edition page, quoting the Arabic, and grading
every rendering `engine_translation_unreviewed` with `customer_prediction:
false` throughout - the same discipline already used for the Rhetorius
(Byzantine) pack in this corpus. Five of al-Qabisi's own dignity tables
(domicile, exaltation-degree, Dorothean-style triplicity, Egyptian bounds, and
Chaldean face order) were additionally cross-checked programmatically against
this repository's existing `src/engine/reference_data.py` and
`src/engine/multitradition/hellenistic.py` during this pass; all five matched
exactly, with zero mismatches, across every sign. A sixth finding - al-Qabisi's
own explicit numerical essential-dignity scoring table (domicile +5,
exaltation +4, triplicity +3, bound +2, face +1) - is textually identical to
the scoring table `hellenistic.py` currently documents as "a later Latin
development" attributed to William Lilly (1647); al-Qabisi states it in
10th-century Arabic roughly seven centuries earlier. This is reported as a
research finding for the pack owner's attention; no engine code was changed as
part of this pass.

Chapter IV turned out to be the single most load-bearing chapter for a natal
reading: it carries the full hyleg (prorogator) candidate-place algorithm, the
kadkhudah (alcocoden) selection algorithm (with an explicit, named
disagreement from Dorotheus on priority order), al-wali (a third,
less-discussed significator), a fully-worked numeric example of whole-sign
annual profection (independently reproduced and confirmed correct during this
pass), a second worked example for world-year profection citing al-Kindi's
chronology, primary/ascensional directions with a mean-solar-motion rate
(59'8"/day, correct to about a third of an arcsecond against the modern
value), a bound-based direction system (al-jarbakhtar) with an internally
self-consistent rate conversion, and several minor named techniques
(duodecatemoria, the ninth-parts/nawbahr - structurally the same construction
as Jyotisha's navamsha, noted as an observation only - the Ascendant-specific
darijan, and an hour-lord annual rotation, sahib al-dawr). Chapter II
independently supplied the full nine-body firdaria major-period duration
table, including both nodes, summing to 75 years - the exact gap flagged as
absent from the existing al-Biruni pilot (checklist item 7). Chapter V's lot
compendium (jumal al-sihaam) lists on the order of 50 individually-formulated
lots across all 12 houses plus mundane/commodity-price lots, several
explicitly attributed by name (Hermes, Valens, al-Andarzaghar, Dorotheus), and
closes with al-Qabisi's own admission that the final, weakest tier (commodity
price divination) is included "even though the doctrine concerning it is
weak" - a source-internal caveat, not one invented for this pass.

**Rights status, confirmed.** CC BY-SA 4.0 for the TEI transcription itself,
exactly as already recorded in `abu_mashar_al_qabisi_access_matrix.json`; the
2004 critical edition's translation and apparatus remain separately
copyrighted and were neither consulted nor reproduced. Every Arabic quotation
in the new rule manifest is of the medieval public-domain text.

**What remains gated.** Rule *promotion* into a validated/live pack still
requires independent Arabic specialist review and a second independent
passage-to-predicate reader (per the corpus-wide validation gates above); none
of the 54 rules is `live_engine`, customer-eligible, or interpretation-eligible
today. The same direct-extraction method should next be applied to the Abu
Ma'shar Great Introduction and Abbreviation Arabic TEI (already downloaded and
hash-verified) without merging their doctrine into al-Qabisi's or vice versa.
