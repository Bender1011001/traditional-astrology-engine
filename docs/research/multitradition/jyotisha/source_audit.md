# Indian Jyotisha Source Audit

Status: Chapters I-II calculation/condition pilots encoded; not ready for implementation or publication  
Date: 2026-07-31

## Outcome

There is enough accessible material to begin a serious classical-natal engine,
but not enough evidence to call any single modern configuration "the Vedic
system." The first production pack must name its texts, editions, astronomical
profile, and interpretive school.

This pass inspected four downloadable OCR objects and one machine-readable
Sanskrit text. Exact identifiers and hashes are in `../source_registry.json`.

## Inspected witnesses

### Varahamihira, Brhajjataka

1. GRETIL provides machine-readable Sanskrit with stable chapter/verse markers,
   based on a named 1979 reprint edition. Its usage notice restricts it to
   reference under the source terms.
2. Internet Archive item `brihatjataka00varaiala` is N. Chidambaram Aiyar's
   1905 second revised and enlarged English edition. The OCR is readable enough
   for search and structural comparison, but page images must control exact
   wording.

The inspected 1905 contents identify these technique families:

- zodiac/sign and planetary definitions;
- conception and birth-time topics;
- early-death and lifespan doctrines;
- dasha and antardasha periods;
- Ashtakavarga;
- vocation;
- raja, nabhasa, lunar, two-planet, ascetic, miscellaneous and adverse yogas;
- nakshatras;
- planets in signs, houses and vargas;
- aspects;
- death, lost-horoscope/rectification material, and drekkanas.

Research implication: `Brhajjataka` is a compact classical backbone and a good
verse-ID pilot, but Aiyar's notes and supplementary framing must be tagged as
translator/editor material rather than silently attributed to Varahamihira.

### Chapter I passage-alignment pilot

`brhajjataka_calculation_rule_manifest.json` now records eleven atomic,
research-only rules aligned between GRETIL Sanskrit verse IDs and Aiyar's 1905
translation. They cover the sign/nakshatra-quarter partition, classical sign
rulers, navamsa and trimsamsa assignment, two explicitly conflicting
Hora/Drekkana variants, exaltation/depression, vargottama navamsas, and
moolatrikona signs. The pack deliberately does **not** encode a modern
ayanamsha, moolatrikona degree spans, or an invented exaltation-strength curve.

The conflict in the source is preserved. `BJ_01.11` gives the Solar/Lunar Hora
and sign/fifth/ninth Drekkana construction. `BJ_01.12` marks another view with
`ke cit` (some); Aiyar identifies it in his NOTES with Garga's school. The
manifest therefore treats the second construction as a reported selectable
variant and treats the Garga identification as Aiyar's commentarial
attribution, not as an unqualified statement by Varahamihira.

`brhajjataka_validation_vectors.json` supplies 36 direct-example and derived
boundary targets. Half-open intervals are an explicit deterministic test
convention, not a claim about the verse's exact boundary wording. A source
specialist must review objects exactly on a division boundary before any code
is promoted. The added coverage preserves the 108-quarter structural partition
without inventing an ayanamsha and tests all seven moolatrikona signs while
requiring degree ranges to remain null.

`brhajjataka_planetary_rule_manifest.json` adds eleven Chapter II rules for
conditional benefic/malefic status, fractional and special aspects, the
Satyacharya natural-relationship table, temporary relationships and their
reported exaltation-sign variant, positional/directional/motional/temporal
strength qualifiers, and natural-strength order. Its 39 vectors expand direct
tables and negative controls, including an affirmative test that positional
strength membership produces no numeric shadbala weight.

This second pack intentionally refuses several tempting shortcuts. Aiyar's
15-degree aspect extension, directional-triplicity reading, greatest-
brilliance elongations, and gloss of `samagama` are commentary or require
Sanskrit review, so they are not promoted as Varahamihira's computation. The
text supplies several strength qualifiers and an ordinal natural-strength
order, not permission to import modern numerical shadbala points. Mercury's
status when unjoined or joined to both benefic and malefic categories is
explicitly unresolved and must fan out or abstain.

Rights also remain gated. Internet Archive metadata leaves the rights field
empty, while the scanned 1905 title page says `Registered Copyright.` The
translation is therefore used only for internal alignment and paraphrase
research pending a jurisdictional rights decision.

### Kalyanavarma, Saravali

Internet Archive item `in.ernet.dli.2015.313760` traces to a 1914 Digital
Library of India/Banasthali University scan. The Sanskrit page images appear
substantial and the OCR exposes a chapter list, but the OCR mixes scripts and
misrecognizes many characters. Automated rule extraction from that OCR would be
unsafe.

Research implication: this witness needs image-based Sanskrit re-keying/OCR,
verse alignment, and specialist correction before it can contribute exact
rules. It is useful now for edition discovery and coverage inventory only.

### Mantreswara, Phaladeepika

Internet Archive item `in.gov.ignca.6945` is V. Subrahmanya Sastri's 1950 second
revised and enlarged English edition from a Central Archaeological Library/IGNCA
scan. The OCR is searchable. The inspected prefaces explicitly say:

- earlier publications were incomplete or had misplaced verses;
- the editor attempted to supply missing material, including a twenty-eighth
  chapter;
- the treatment differs from other authors in places;
- the title page says copyright registered.

The OCR exposes material on bhavas, shadvarga/saptavarga, extensive yoga
families, transits and other natal/timing topics.

Research implication: the edition is useful for internal study and comparison,
but it is a reconstructed practitioner edition, not a neutral critical text.
Its copyright must be resolved before excerpts or derived translation text are
used commercially.

### Brhat Parashara Hora Shastra, 1899 witness

Internet Archive item
`xpnh_brihat-parashara-hora-shastra-purva-uttara-khanda-subodhini-shridhar-jatash`
is identified as a Mumbai 1899 Sanskrit-Hindi Purva/Uttara Khanda edition, with
a Sanskrit `Subodhini` commentary associated with Sridhara and an Uttara Khanda
edited by Govinda Sharma Shastri. The Nepal Sanskrit University/Balmeeki Campus
digitization pages display a CC0/public-domain notice. The Archive metadata
rights field is empty.

The OCR is very poor, but portions of the contents are recoverable, including
house results, varga material, arudha/karakamsha material, Vimshottari and
Kalachakra dasha calculations, subperiods, and dasha results.

Research implication: this is an important early printed witness precisely
because BPHS recension structure is disputed. It must be compared chapter by
chapter with other Sanskrit editions. Its existence does not make every rule in
later English BPHS editions ancient, uniform, or textually settled.

## Controlling research decisions still required

### Text/source packs

Proposed initial packs, each independently switchable:

1. `varahamihira_brhajjataka`
2. `kalyanavarma_saravali`
3. `mantreswara_phaladeepika`
4. `parashara_1899_witness`
5. later BPHS recensions only after explicit comparison
6. Jaimini, Tajika, prasna, muhurta and regional packs as separate projects

No "consensus" rule may be created by averaging these texts. A synthesis layer
may report agreement or conflict while retaining every source rule.

### Astronomy/calendar profile

The engine must make these choices explicit and testable:

- tropical versus named sidereal reference;
- exact ayanamsha mode and epoch;
- mean versus true node;
- geocentric/topocentric positions;
- apparent versus mean positions where relevant;
- civil, local mean, or local apparent time;
- sunrise boundary and weekday/vara convention;
- house/bhava model;
- nakshatra and pada boundaries;
- ephemeris version and valid date range.

The current `ChartRequest` already exposes `zodiac_system`, `ayanamsa`,
`node_type`, coordinates and unknown-time fields, but a Jyotisha profile must
prevent an arbitrary mixture of options that no selected school uses.

### Interpretation hierarchy

Research must determine, per pack:

1. chart viability and birth-time sensitivity;
2. lagna, its ruler, luminaries and relevant foundational condition;
3. sign/house/varga strength and relationships;
4. yoga qualification, cancellation, activation and repetition;
5. topic-specific significators and lords;
6. dasha activation;
7. transit/Ashtakavarga or selected timing modifiers;
8. contradictions and source precedence.

This ordering is only a research hypothesis until supported passage by passage.
It must not be copied from the Western `judgment_planner` scoring model.

## Rule-extraction schema additions needed for Sanskrit texts

Each passage needs:

```text
work
edition/witness
chapter and verse
Sanskrit text
normalized transliteration
word segmentation
literal translation
published translation(s)
commentary/editor additions
condition AST
conclusion AST
cross-references
variant readings
philological reviewer
practice reviewer
publication paraphrase
```

## Safety and publication limits

The inspected contents include early death, lifespan, disease-adjacent,
gendered, fertility, social-rank and adverse-fate doctrines. They may be
researched and represented historically, but customer output must not:

- state a death age or survival deadline;
- diagnose health, fertility, pregnancy or mental condition;
- give medical or financial instructions;
- present caste, sex/gender hierarchy or inherited status as fact;
- turn a translation uncertainty into a confident personal judgment.

The deterministic trace should preserve the historical testimony and then apply
a documented publication policy, as the Western engine already does for severe
longevity material.

## Next source work

1. Acquire and hash controlling PDFs/page images for the four witnesses.
2. Facsimile-check and independently review the Sanskrit for the encoded
   `Brhajjataka` Chapters I-II pilots, then continue chapter-by-chapter while keeping
   translator additions in a separate evidence layer.
3. Locate at least two more Sanskrit BPHS recensions and construct a chapter/
   verse concordance against the 1899 witness.
4. Locate a legally usable Sanskrit `Saravali` edition or re-key the inspected
   page images with specialist review.
5. Resolve `Phaladeepika` translation rights and compare its reconstructed
   passages against Sanskrit witnesses.
6. Create the first golden calculation vectors from worked examples in the same
   editions, not from modern web calculators.
