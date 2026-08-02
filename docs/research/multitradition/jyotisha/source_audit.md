# Indian Jyotisha Source Audit

Status: Chapters I-II calculation/condition pilots encoded; Phaladeepika delineation layer (planet-in-bhava, named yogas, Vimshottari mahadasha significations) extracted 2026-08-02; not ready for implementation or publication  
Date: 2026-08-02 (originally 2026-07-31)

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

## 2026-08-02 pass: Phaladeepika delineation extraction; BPHS OCR confirmed unusable; a legible Saravali witness found

Scope: build the Parasari (BPHS-descended) delineation layer distinct from the
sign-based Jaimini track (`docs/research/multitradition/jaimini/`). Per
`defensibility_spec.md`'s core-technique checklist, the calculation/structural
items (1-13) were already `implemented`; the open items (14-16: Shadbala,
Ashtakavarga, other vargas) remain untouched by this pass - nothing found here
sources numeric strength weights or divisional-chart precedence, so those three
rows are unchanged. This pass instead opened a dimension the checklist did not
yet name: classical delineation TEXT keyed to facts the engine already computes
(planet-in-house, named yogas, Vimshottari mahadasha significations), as
opposed to the calculation and structural-detection material already encoded.

### Mantreswara, Phaladeepika - now mined for delineation content

The 1950 Subrahmanya Sastri translation (already registered, previously only
metadata-inspected) was read directly, chapter by chapter, rather than sampled.
Adhyaya VIII ("the effects of the Sun and other planets in the several bhavas
from the Lagna") supplies planet-in-bhava results for all 12 houses for Moon,
Mars, Mercury, Jupiter, Venus, Rahu and Ketu, for 11 of 12 houses for Saturn
(house 1 is explicitly dignity-conditioned - exalted/own sign versus any other
sign - the source's own asymmetry, not smoothed over here), and for 5 of 12
houses for the Sun (6, 9, 10, 11, 12; houses 1-5, 7 and 8 fall in a stretch of
the scan where the Devanagari survived but the English translation did not,
between the end of the Neechabhanga passage and the legible resumption - a
genuine OCR gap, not an invented completion). Adhyayas V-VII supply eight named
yoga clusters: the five Pancha Mahapurusha yogas (Ruchaka/Bhadra/Hamsa/
Malavya/Sasa - a planet in its own sign or exaltation in a kendra), Kesari and
Sakata yoga (the Moon in kendra, or in 6th/8th/12th, counted from Jupiter -
popularly "Gajakesari"), Mahabhagya yoga, the Adhama/Sama/Varishtha grading
(Moon's house counted from the Sun, notable because it inverts the usual
kendra-is-strongest convention and is preserved as printed), Sunapha/Anapha/
Durudhara/Kemadruma (planets in the 2nd/12th from the Moon, with a named
dissenting view on Kemadruma cancellation explicitly preserved rather than
resolved), the Vesi/Vaasi/Kartari benefic-malefic-flanking cluster, a
"4 Rajayogas" catalog, and the Neechabhanga Rajayoga (debilitation-cancellation)
sequence. Adhyaya XIX supplies general Vimshottari mahadasha significations for
all nine grahas (only the Sun's is explicitly conditioned on natal placement
quality in this passage). All of the above is now encoded, paraphrased (not
quoted at length, for the same rights-uncertain-translation reason Aiyar's
Brhajjataka translation is only paraphrased), cited by Adhyaya and sloka
number, in `delineation_rule_manifest.json` (18 rules).

Deliberately NOT mined: Adhyayas XI-XII ("horoscope of women", "issue/
children") were located but skipped. Their content is yoga-style rules about
progeny and marriage outcome for the native, which sits inside this pack's own
safety limits on fertility/health claims; nothing from those chapters is in the
delineation manifest. Progeny/children clauses that appear incidentally inside
the encoded planet-in-bhava and yoga material (e.g. several houses' results for
Jupiter, Saturn, Rahu, Ketu, and the Malavya and Papakartari yoga results) are
retained as historical testimony with an explicit suppression note, the same
treatment this corpus already gives varna/caste material.

No worked natal chart - real or stated birth data, computed positions, and an
author-given verdict - was found in Adhyayas V-VIII or XIX. Those chapters are
rule catalogs, not worked-example collections. Adhyayas IX-XVIII and XX-XXVIII
were not inspected in this pass and remain open leads for a worked example
(see `worked_examples.json`'s updated `jyotisha.phaladeepika.chapter_inventory`
entry for the exact negative finding and what remains unchecked).

### Brihat Parashara Hora Shastra, 1899 witness - OCR confirmed unusable

The archive text file (already registered from a prior pass, with a recorded
sha256) was actually fetched to a local mirror this time
(`jyotisha/sources/bphs_subodhini_1899_djvu.txt`, hash confirmed identical to
the registry's recorded value) and inspected directly rather than by metadata
alone. The OCR is confirmed - not merely suspected - to be almost total
failure: a 2,000-character spot sample contained effectively no recoverable
Devanagari or Hindi, rendering overwhelmingly as literal `?` replacement
characters. This is a worse failure mode than the Saravali 1914 witness's
"mixed scripts, many misrecognitions". Per `DEFENSIBILITY.md`'s four-row table,
this is squarely row 3 ("original not retrievable [as usable text] - an access
problem, not a language or rights problem"): the digitized pages themselves
carry a CC0/public-domain notice, so there is no rights blocker, only a
digitization-quality one. No BPHS content is encoded anywhere in this pass;
BPHS remains the only one of the four controlling witnesses that has produced
zero usable text across two inspection passes.

### Kalyanavarma, Saravali - a legible Sanskrit witness found

Two additional Saravali witnesses were located and inspected this pass, one of
which resolves what had been a genuine OCR-quality blocker rather than a rights
question:

- **Nirnaya Sagar Press, 1907 (ed. V. Subrahmanya Sastri), archive item
  `saravalisubrahmanyasastryv.nirnayasagarpress1907_202003_345_b`.** CC0-licensed
  digitization. Downloaded, hashed, and mirrored to
  `jyotisha/sources/delineation_saravali_nirnayasagara_1907_djvu.txt`. Unlike
  every previously catalogued Saravali witness, this OCR is measurably legible
  Devanagari: of 366,411 characters, 291,940 are proper Devanagari code points
  and only 9 are `?` failure markers. The front matter (a Nirnaya Sagar Press
  book-list) was read to confirm press/edition identity; the Saravali text
  proper has not yet been read for chapters, slokas, or a worked example - that
  is the single highest-value next step on this branch, now that legibility is
  no longer the blocker.
- **Digital Library of India, 1928 "third edition", archive item `dli.csl.7888`.**
  Inspected and found NOT usable for content: its ~200-line English preface (by
  the same editor, discussing manuscript collation - a Kankanhalli manuscript
  of 54-56 chapters, two missing) is legible and useful edition-history context,
  but the ~25,000-line Devanagari body is almost entirely OCR noise. Registered
  as a lower-priority third witness, useful only for corroborating the editor's
  own preface claims.

A prior local file at `jyotisha/sources/delineation_saravali_nirnayasagara_1907_djvu.txt`
(present before this pass, undocumented in the registry) was superseded by a
freshly downloaded, hash-verified copy of the confirmed 1907 archive item
above, since its provenance could not otherwise be established with confidence.

### Checklist and coverage-manifest consequences

No row on `defensibility_spec.md`'s core-technique checklist changed status as
a direct result of this pass (items 14-16 remain genuinely `source_gated`; this
pass did not source Shadbala, Ashtakavarga, or other-varga material). Three new
checklist rows were added for the delineation-content dimension this pass
opened (planet-in-bhava text, named-yoga delineation text, Vimshottari
mahadasha significations), each marked `source_gated` rather than `computable`
or `implemented`: the rules are sourced and structured, but (a) the
translation's rights are unresolved, (b) independent Sanskrit/practitioner
review is pending since the scan's own embedded Devanagari is OCR-corrupted,
and (c) no composer or engine code was written this pass to consume them - all
three are genuine holds, not merely undone composer effort, so `source_gated`
is the honest label rather than the disallowed `computable`.
`engine_coverage_manifest.json`'s `phaladeepika_natal` module was upgraded from
`source_limited`/`source_discovery_only` to `research_verified`/
`validated_research_artifact` (matching the existing `brhajjataka_classical_
jataka` module's posture, which carries comparable translation-rights and
review caveats) now that `delineation_rule_manifest.json` exists as its
artifact.

## Next source work

1. Read the Saravali text proper in the newly-found 1907 Nirnaya Sagar Press
   witness for chapter structure, bhava/yoga content, and any worked example;
   per `DEFENSIBILITY.md`'s "translation is not a gate for quotation" section,
   a direct rendering graded `engine_translation_unreviewed` is now the correct
   move rather than waiting on a modern English translation.
2. Recover Phaladeepika Adhyaya VIII's Sun houses 1-5, 7 and 8 from a page-image
   check rather than the OCR text, which does not carry a legible English
   translation for that stretch.
3. BPHS: attempt page-IMAGE-level inspection (not OCR text) of the 1899
   witness, or locate a second, better-digitized Sanskrit recension; OCR-text
   extraction from this specific scan is now a closed lead, confirmed unusable
   rather than merely suspected.
4. Facsimile-check and independently review the Sanskrit for the encoded
   `Brhajjataka` Chapters I-II pilots, then continue chapter-by-chapter while
   keeping translator additions in a separate evidence layer.
5. Resolve `Phaladeepika` 1950 translation rights (the title page says
   "copyright registered"; the Archive item's rights field is empty) before any
   rule in `delineation_rule_manifest.json` can move past `research_only`.
6. Add house-from-the-Moon and house-from-the-Sun relative-house computation to
   `src/engine/multitradition/vedic.py` (out of scope for this research pass):
   several of the newly-sourced yogas (Sunapha/Anapha/Durudhara/Kemadruma,
   Kesari/Sakata, Adhama/Sama/Varishtha, the Sun-relative Vesi/Vaasi cluster,
   and the kendra-from-Moon branch of Neechabhanga Rajayoga) are sourced and
   structured but not yet checkable against the live engine's current facts,
   which compute house only from the Lagna.
7. Create the first golden calculation vectors from worked examples in the same
   editions, not from modern web calculators, once one is located.
