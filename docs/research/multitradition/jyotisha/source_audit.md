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

## Verified 2026-08-02: the Sun bhava gap is a real scan gap, not an assumption

`delineation_rule_manifest.json` records `houses_not_recovered: [1,2,3,4,5,7,8]`
for the Sun's planet-in-bhava rule. That claim has now been checked directly
rather than trusted, because this corpus has repeatedly recorded blockers that
turned out to be false.

It holds. Adhyaya VIII begins at line 5690 of
`delineation_phaladeepika_6945_djvu.txt`, and the text there opens mid-sentence
("...he will be wandering without a wife and suffer humiliation. If the Sun
should be in the 6th house..."). The printed page numbers on either side of the
break run 61 then 84, so a physical page is missing from the scan itself. The
Sun's earlier bhava results were on it.

Everything after that point is present and legible: Moon, Mars, Mercury,
Jupiter, Venus and Saturn each have all twelve houses, and Rahu continues past
line 6120. Those are encoded at 12/12.

Two consequences worth stating:

1. The gap is NOT closable from this witness. It needs a different scan of
   Phaladeepika, not a different author. Substituting Saravali's or
   Brihat Jataka's Sun-in-bhava results would be a merge across authors and is
   refused.
2. The delineations themselves are genuinely terse - roughly ten words per
   house-cell in the original - so a complete planet-in-bhava block yields only
   about 800 words total. A full-length report cannot be built from this
   technique alone; it needs the other blocks (graha in rasi, bhava-lord in
   bhava, nakshatra results, dasa/antardasa pairs), which remain unmined.

Measured this pass: 2,341 words of Jyotisha delineation encoded against roughly
440,000 words of fetched source across BPHS, both Saravali witnesses,
Brihat Jataka and the untouched remainder of Phaladeepika.


## CORRECTION 2026-08-02: BPHS is legible. The earlier verdict was false.

The 2026-08-02 entry above and the registry entry
`jyotisha_bphs_subodhini_1899_archive` both record the 1899 Subodhini BPHS scan
as unusable - "OCR is severely corrupted and cannot control wording", and in the
defensibility spec's worked-example table, "almost total failure (near-all `?`
characters)". **That is wrong, and it was wrong when it was written.**

Measured directly on the local mirror at
`jyotisha/sources/bphs_subodhini_1899_djvu.txt`
(sha256 `edf836323aed641925dea689e0248a582b66238835ac55d8381c372b98ef1684`):

| Measure | Value |
|---|---|
| Characters | 1,106,274 |
| Devanagari codepoints | 807,038 (73%) |
| `?` characters in the entire file | 100 |
| Lines | 37,266 |
| Lines carrying an adhyaya marker | 463 |

A file with 100 question marks in 1.1 million characters is not "near-all `?`".
The earlier finding appears to have been produced from an impression of the
file rather than from reading it, and it cost the corpus a root text for two
audit passes. This is the fifth blocker of this exact shape in this corpus - a
Nahuatl text, Arabic/Latin TEI, the Tibetan White Beryl, and BPHS twice - and
the pattern is worth naming: **an "unreadable source" finding is a claim about
the source, and the only evidence that can support it is quoted illegible
lines.**

### What the OCR is actually like

Ordinary noisy Devanagari book OCR. Ligatures garble in places
(`ग्रहप्राइभोवाध्यायः` for `ग्रहप्रादुर्भावाध्यायः`); printed sloka numerals are
occasionally misread (adhyaya 15 prints its slokas 84-86 as `८७`, `८८`, `८६`);
and library stamps ("Nepal Sanskrit University, Balmeeki Campus, Kathmandu"),
eGangotri public-domain notices and page furniture are interleaved with verse.
Against that, continuous verse text is readable throughout the purva-khanda,
and every one of the 107 rules now in `bphs_rule_manifest.json` was transcribed
from it by eye.

### Where it genuinely does degrade, with evidence

Three specific losses were located. None of them is general corruption.

1. **A page-image gap inside adhyaya 13 (Aries lagna).** At djvu lines
   6135-6147 the only surviving content is:

   ```
   6137 'छ '
   6138 '® Nepal SanskritUniversity, Balmeeki Campus, Kathmandu '
   6142 '८८-0. In Public Domain. Digitization by eGangotri '
   6145 '0. बृहत्पाराशरहोरासारांशः । '
   ```

   Verse text is clean on both sides of it (line 6134 ends
   `परतंत्रेण जीवस्य पापकः`, line 6148 resumes `…मोपि निश्चितम्`). The list of
   Aries's functional benefics and malefics falls inside the gap. That rule is
   marked `recovery: "partial"` and is not reconstructed.

2. **Two-column interleave in adhyaya 36.** Each graha's `utkrsta` and `papa`
   dasha results are the two halves of one long sragdhara verse printed in
   facing columns, and the OCR reads across them. The graha names, the verse
   numbers and the good/bad split survive unambiguously; the clause ORDER
   inside each half is reconstructed. Both affected rules carry
   `reading_confidence: "medium"` and say so in their exceptions.

3. **An out-of-sequence block of ~1,300 lines.** Djvu lines 15871-17180 sit in
   the middle of adhyaya 37 but carry running headers numbering their chapters
   18 and 19 (`प्रश्नाध्यायः १८`, `अध्यायानुक्रमवर्णनाध्यायः १९`). Adhyaya 37's
   own header resumes at line 17189. Something is bound or scanned out of order
   here; it was not investigated further this pass because nothing was mined
   from it.

### What the recension actually is

Not the BPHS a modern reader knows, and the pack says so everywhere. The
running headers and colophons of the first half call it
**`बृहत्पाराशरहोरासारांश`** - the *saramsa*, the essence or abridgement, of the
Brhatparasarahora. The publisher's preface (djvu lines 260-340) claims the work
runs to a hundred adhyayas in two khandas, states that it had *never before been
printed*, and quotes the closing sloka `एवं होराशताध्याया सर्वपापप्रणाशिनी`. The
purva-khanda's chapter order is Jaimini-inflected in a way the modern
recensions are not: rasi-drsti at adhyaya 4, karakamsa-phala at 9, arudha at 11,
upapada at 12. The uttara-khanda restarts its numbering at 1 and runs
ashtakavarga, sadbala, ista-kasta, rasmi, lokayatra, ayurdaya, kalamsa and
abdacharya.

Practical consequence, and it is not a small one: **this pack's gaps are not
necessarily BPHS's gaps.** Adhyaya 15 gives 132 of the 144 bhavesa-in-bhava
cells; the missing twelve are missing from *this recension's printed text*, and
the modern Sharma and Santhanam recensions do carry results for several of them.
Nothing was imported to fill them.

### What was extracted

| Block | Adhyaya | Cells / rules |
|---|---|---|
| Bhavesa in bhava (lord of each bhava, in each bhava) | 15 | **132 of 144 cells** in 12 rules |
| Governing proportionality qualifiers | 15, 36 | 3 rules |
| Graded graha drsti (pada scale) | 4 | 4 rules, 28 offset cells |
| Rasi drsti | 4 | 1 rule |
| Functional nature by lagna | 13 | 12 rules (Aries partial) |
| Maraka doctrine and its exemption | 13 | 1 rule |
| Dhana yogas | 30 | 13 rules |
| Daridra and bandhana yogas | 31 | 20 rules |
| Raja yogas (varga ladder, kendra-kona, karaka-based) | 28, 29 | 6 rules |
| Vimsottari mahadasa results, 4 conditions x 9 grahas | 36 | 4 rules, 34 graha cells |
| Dasa of the lord of each bhava | 36 | 1 rule, 12 cells |
| Dasa combinations and reckoning-from-a-bhava | 36 | 22 rules |
| Named dasa quality grades (Sampurna...Adhama) | 36 | 1 rule, 6 grades |
| Antardasa arithmetic and bhukti quality | 37 | 7 rules |

**107 rules, 342 validation vectors** (every rule referenced by at least one),
`customer_prediction: false` throughout, publication status `research_only`.

### What is NOT in this recension

The 9x12 **graha-in-bhava** grid that the priority order expected. It is not
there. Adhyaya 14 is titled for the twelve bhavas but its content is compound
conditional judgment (lord plus aspect plus co-tenant), not a clean
graha-by-house grid, and no chapter in either khanda supplies one. The
Phaladeepika Sun gap at houses 1-5, 7 and 8 therefore **cannot** be filled from
BPHS in this edition, and no attempt was made to fill it. That is a negative
result and it is worth as much as the positive ones: it means the corpus's
graha-in-bhava coverage still depends on a single damaged Phaladeepika scan.

### Volume

8,607 words of English delineation rendering encoded this pass, against
1,106,274 characters of BPHS source read or scanned. For comparison, the whole
prior Jyotisha delineation layer stood at 2,341 words. The bhavesa block alone
is roughly seven words of Sanskrit per cell and about twenty of rendering, which
is denser than Phaladeepika's graha-in-bhava block and covers a technique
(judging a house by where its lord went) that the engine can already compute for
every chart it casts.

---

## Saravali (Nirnaya Sagar 1907) and Brihat Jataka (Aiyar 1905) — delineation mining, 2026-08-02

The previous pass flagged `delineation_saravali_nirnayasagara_1907_djvu.txt` as
"legible, not yet mined, next highest-value task." This pass mined it.

### Why this witness could be read directly

366,411 characters, of which 291,940 are proper Devanagari code points and nine
are OCR `?` failure markers. The sloka numbering runs continuously inside each
adhyaya and the chapter colophons (`iti kalyanavarmaviracitayam saravalyam ...`)
survive, so a passage can be located by chapter, by sloka and by line. That is
good enough to read the Sanskrit and translate it, so that is what was done:
every cell carries the Sanskrit it renders, the encoder's own rendering graded
`engine_translation_unreviewed`, the adhyaya and sloka number, and a line range
into the text. No modern copyrighted translation was consulted, quoted or
paraphrased. The point is not that the rendering is authoritative; it is that a
specialist can check it against the original in the same file.

### What was extracted from Saravali

| Block | Adhyaya | Cells |
|---|---|---|
| Sun in the twelve rasis, + 7 signs x 6 drsti variants, + svakshetra/uccha | 22 | 55 |
| Moon in the twelve rasis, + all 12 signs x 6 drsti variants | 23 | 84 |
| Moon in Taurus by half-sign (degree-conditioned) | 23 | 2 |
| Gate on when a rasi result is realised in full | 23 | 1 |
| Moon in each graha's navamsa x 6 aspecting grahas | 24 | 40 |
| Vargottama / navamsa-strength gate; navamsa lord overrides the rasi result | 24 | 2 |
| Yavana attribution of the whole drsti method | 24 | 1 |
| Mars in the rasis (Aries-Cancer only; see gap) + 6 owner-groups x drsti | 25 | 37 |
| Mercury in the twelve rasis + 7 owner-groups x 6 drsti | 26 | 54 |
| Jupiter in the twelve rasis + 7 owner-groups x 6 drsti | 27 | 54 |
| Venus in the twelve rasis + 7 owner-groups x 6 drsti | 28 | 54 |
| Saturn in the twelve rasis + 7 owner-groups x 6 drsti | 29 | 54 |
| **Graha in bhava, seven grahas x twelve bhavas, complete** | **30** | **84** |
| Benefic/malefic bhava polarity with the 6/8/12 inversion | 30 | 1 |
| What overrides a bhava result (yoga, drsti, uccha) | 30 | 1 |
| Vimsottari mahadasa results, favourable and unfavourable halves | 40 | 14 |
| What makes a dasa good or bad (dignity, bhava, combustion, retrogression) | 40 | 8 |
| Where inside a dasa the result falls (sirsodaya / prsthodaya) | 40 | 1 |
| Moon's mula dasa by rasi, attributed to the Yavanas | 40 | 15 |

**87 rules, 563 validation vectors, 563 delineation cells, ~29,000 words**
(Sanskrit plus rendering) in `saravali_rule_manifest.json` and
`saravali_validation_vectors.json`. `customer_prediction: false` on every
conclusion; publication status `research_only`.

### The finding that matters most

**Adhyaya 30 is a complete seven-graha by twelve-bhava table with no scan gap.**
The BPHS audit immediately above concluded that the graha-in-bhava grid "is not
there" in that recension and that "the corpus's graha-in-bhava coverage still
depends on a single damaged Phaladeepika scan." It no longer does. Saravali 30
gives all 84 cells, and gives them with sub-conditions the engine already
computes: the Sun's 1st-house cell is refined by rasi (Cancer/Aries, Leo and
Libra each get their own clause), the Moon's 1st-house cell splits on
Cancer/Taurus/Aries versus the rest, the Moon's 6th and 8th split on full versus
waned, and Saturn's 1st-house cell splits on exaltation-or-own-rasi versus
everything else.

This does **not** repair the Phaladipika Sun gap. That gap is a fact about that
witness and stays recorded as one. Saravali is a second author, not a patch.
Where Saravali 30 and Phaladipika VIII differ, that is a difference between
Kalyanavarma and Mantreswara and must be rendered as two voices.

### The Saravali gap, stated precisely

Adhyaya 25 (Angarakacara) jumps from sloka 7 at txt line 3897 to sloka 34 at
line 3911. That is a lost leaf, not a lost line. What is gone: Mars's plain
results in Leo through Pisces, and the drsti set for Mars's own rasis (Aries and
Scorpio). Those cells are recorded as `rasis_not_recovered` and were **not**
filled in from Brihat Jataka, from Phaladipika, or from anywhere else.

### Structural note: two different drsti schemes inside one book

Adhyaya 23 (the Moon) gives drsti variants **sign by sign** — all twelve rasis
get six aspecting-graha cells each, 72 cells. Adhyayas 22 and 25-29 give them
**grouped by the owner of the rasi**: Mars in "a rasi of Venus" gets one cell
covering both Taurus and Libra. This is not an encoding convenience, it is how
Kalyanavarma organises the chapters, and it is flagged in the exceptions of
every owner-grouped rule so that no one later mistakes the grouping for
carelessness.

### The second Saravali witness cannot carry a collation

`delineation_saravali_2015313760_djvu.txt` was searched for ten distinctive
strings drawn from passages encoded this pass (nighnanti, bhavan,
sangramotkata, kulire, vikalanayana, rasiphalam, muladasa and others). Nine of
the ten return zero hits and the tenth returns a mangled context. Its Devanagari
OCR is corrupt at the aksara level and much of the file is a verse index rather
than the text. **No genuine cross-witness disagreement could be established, in
either direction, and none is claimed.** That is a limitation of the second
witness, not evidence that the two witnesses agree.

What the 1907 edition does supply is its own printed variant apparatus
(pathabheda) at the foot of each page — for example at txt line 3302, the
variant `budhena drste krsatanuh syat` against Adhyaya 22 sloka 22. Where such a
variant bears on an encoded cell it is carried in that cell rather than
discarded. This is a within-edition apparatus and is not the same thing as a
collation of two witnesses; the corpus should not pretend otherwise.

### What was extracted from Brihat Jataka

Adhyaya XVIII (Rasisila) gives six grahas — Sun, Mars, Mercury, Jupiter, Venus,
Saturn — across the twelve rasis, 72 cells, plus the twelve-lagna extract that
Aiyar prints at the end of the chapter and explicitly attributes to
**Satyacharya**, not to Varahamihira. **8 rules, 85 vectors**, all graded **B**,
because the rendering that would drive judgment is Aiyar's 1905 English rather
than the encoder's own reading of the printed Devanagari: this OCR carries only
the English for these stanzas, so the delineation reaches the corpus through one
nineteenth-century translator's choices. The IAST mula quoted beside each cell
comes from the companion e-text `sources/brhajj_u.txt` and has **not** been
collated line by line against the 1905 printing, which is the second reason for
B and not A.

Brihat Jataka Chapter I (txt lines ~2020-2210) is sign-shape and naksatra-list
material and was deliberately not mined as delineation.

The Moon is absent from Adhyaya XVIII. Varahamihira gives the Moon's rasi
results through the aspect table of **Adhyaya XIX**, which states the same
technique as Saravali Adhyaya 23. Adhyaya XIX is not yet mined and is the single
highest-value remaining target in this corpus, because it is the first real
opportunity to collate one delineation table across two named authors.

### Refusals

Socially harsh cells — caste (`sudra`, `vadhaki`, low-caste handicraft), gender
(`stri-vapuh`, `stri-sattvam`), disability and impotence (`sanda`, `kliba`,
`vikala`, `kubja`, blindness, leprosy), servitude (`dasa`, `presya`,
`bhrtaka`), and the death of a parent or spouse — are encoded **verbatim**, with
`output_policy: "refused"` on the cell and a `publication_limit` on the rule
stating that they are never rendered as a claim about a living person. The whole
Satyacharya lagna rule is refused: every one of its twelve cells ends in a mode
of death. Saravali 40.11's Mars cell names sexual violence and homicide and is
refused outright. Nothing was softened in the encoding; the refusal sits at the
output boundary, which is where it belongs.

### Worked examples

Neither witness works an actual nativity in the chapters mined. Saravali 22-30
and 40 and Brihat Jataka XVIII are rule statements throughout; the only
concretely worked figure encountered anywhere in this pass is Brihat Jataka
XXII.2, which walks a *constructed* configuration (Cancer rising with the Moon
in it, Mars, Saturn, the Sun and Jupiter in their exaltations) to illustrate the
definition of karaka planets. That is an illustrative diagram, not a nativity
with a claimed native and a claimed outcome, and it is **not** a validation
vector under DEFENSIBILITY requirement 4. It is recorded here so the next pass
does not re-find it and mistake it for one.

### Volume

29,025 words of Sanskrit-plus-rendering encoded from Saravali and roughly 3,900
words of English rendering from Brihat Jataka, against 366,411 plus 564,451
characters of source read. Before this pass and the BPHS pass, the whole
Jyotisha delineation layer stood at 2,341 words.

## 2026-08-04: the Phaladipika Sun gap is CLOSED - it was a defective scan, not a lost page

The 2026-08-02 verification established that Adhyaya VIII opens mid-sentence in
`in.gov.ignca.6945` and that its printed page numbers jump 81 -> 84, and
concluded correctly that the gap "needs a different SCAN, not a different
author." A second witness has now supplied exactly that.

`dli.ernet.507316` pp. 82-84 carry the whole of what the primary scan omits:
p.82 the close of Adhyaya VII, the heading `|| astamo'dhyayah ||` and sloka 1
(Sun in the 1st); p.83 slokas 2-3 (Sun in the 2nd through 7th); p.84 the 8th.
All three were read directly from page images, not OCR.

The Sun's planet-in-bhava rule therefore now carries **12/12 houses**, and
`houses_not_recovered` is removed. This is a SCAN REPAIR: same work, same
translator, a different photograph of the same edition. It is emphatically not
the cross-author substitution the corpus forbids, and the rule records both the
recovering witness and the defect in the primary one.

Note on p.84: the 8th-house cell contains "he will not be long-lived". It is
stored verbatim, and the engine's clause-level publication policy redacts the
longevity clause at render time - which is where that judgment belongs.
