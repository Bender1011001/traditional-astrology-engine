# Multi-tradition panel — Andrew

Historical and cultural interpretation of astrological doctrine. Not medical, financial, legal, psychological, or safety advice.

**Birth**: 1996-08-13 07:18 (UTC-7) — Fairfield, California, United States (38.2494, -122.0397)
**UTC**: 1996-08-13T14:18:00  ·  **JDN**: 2450309
**Local mean time**: 06:09:50  ·  **True solar time**: 06:05:05 (equation of time -4.7 min)

Panel version 0.1.0. Sections: 12.

---

## Western traditional (Hellenistic/medieval)

*Evidence: live engine*

Tropical Swiss Ephemeris positions from the shipping engine, the same core that produces the live premium report.

**Disclosures**

- **Source — Engine provenance.** Positions produced by the live calculator. The shipping premium report carries the full judgment layer with per-claim evidence notes; this panel section reports the calculation basis only.
- **Configured — Houses.** Whole-sign houses are used for topical judgment, with the quadrant Midheaven reported separately, following the live report's convention. *Alternatives: Placidus, Regiomontanus, Alcabitius, Porphyry.*

**Calculation**

- **ascendant**:
  - **sign**: Virgo
  - **degree in sign**: 1.5017
- **midheaven**:
  - **sign**: Taurus
  - **degree in sign**: 27.0459
- **sect**: day
- **sun altitude degrees**: 9.8747
- **placements**:
  - body Sun, sign Leo, degree in sign 21.0966, whole sign house 12, retrograde False
  - body Moon, sign Leo, degree in sign 13.2464, whole sign house 12, retrograde False
  - body Mercury, sign Virgo, degree in sign 17.1826, whole sign house 1, retrograde False
  - body Venus, sign Cancer, degree in sign 5.5396, whole sign house 11, retrograde False
  - body Mars, sign Cancer, degree in sign 12.5197, whole sign house 11, retrograde False
  - body Jupiter, sign Capricorn, degree in sign 8.5084, whole sign house 5, retrograde True
  - body Saturn, sign Aries, degree in sign 6.8529, whole sign house 8, retrograde True

---

## Islamicate / Persian

*Evidence: validated research pack*

Shares the Western calculation core. Distinctive layer computed here: al-Biruni's sect, halb, hayyiz and firdaria structure from the validated Kitab al-Tafhim reference-condition pack, with the Abu Ma'shar / al-Qabisi variant concordance shown alongside.

**Disclosures**

- **Source — Pack provenance.** Sect and gender classifications, halb/hayyiz and their one-way implication, the firdaria ordering and the equal-seventh subperiod structure are computed from the validated al-Biruni reference-condition pack (15 rules, edition wright_1934_halle_facing_scan), built from facing-page Arabic/English evidence in the Halle institutional scan. Every claim below is al-Biruni's unless another author is named.
- **Configured — Horizon test.** Above/below the horizon is taken from the planet's zodiacal degree against the Ascendant-Descendant axis, ignoring celestial latitude - the traditional treatment. The Sun's result is cross-checked against the ephemeris altitude that set the sect. *Alternatives: true altitude from the ephemeris, quadrant house cusps.*
- **Configured — Mercury association test.** al-Biruni conditions Mercury on association without defining it in the inspected passage. Co-presence in the same sign is used here; where the sign and an associated planet point opposite ways, the pack states no priority and this section leaves Mercury unresolved. *Alternatives: bodily conjunction within orb, any aspect, sign ruler only.*
- **Refused — Firdaria periods and ages.** The al-Biruni pack refuses node periods and age/date firdaria arithmetic because section 395 supplies neither node periods nor a major-duration table. The ordering and the equal sevenths below are therefore a sequence without a clock: no years, no ages, no dates.
- **Refused — Judgment from halb or hayyiz.** Section 498 lists halb or hayyiz among several conditions of a planet's joy. This section does not infer a complete judgment from them, cancel a debility, or change a planet's benefic or malefic nature - the pack forbids all three.
- **Source — Variant concordance.** Seven Wurzburg TEI witnesses are hash-pinned in this repository, covering separate Arabic, Hermann of Carinthia, John of Seville and Adelard of Bath lineages; 30 candidate passages and 8 preserved variants are catalogued. The Arabic originals are ninth- to eleventh-century and public domain, so the disagreements are shown rather than deferred.
- **Refused — Abu Ma'shar and al-Qabisi doctrine.** The variants below are published as evidence, not promoted to rules: no Latin lineage overrides the Arabic or another Latin lineage, the Great Introduction and the Abbreviation stay different works, and al-Biruni is never backfilled from either author. Rule promotion waits on the critical apparatus and Arabic specialist review.
- **Refused — Prediction.** The pack marks itself interpretation-ineligible and historical-use only. The reading below reports classification, structure and attribution; it derives no life prediction, no timing, and no advice.

**Calculation**

- **shared calculation core**: western_traditional
- **source pack**:
  - **pack id**: islamicate_al_biruni_tafhim_reference_conditions_v1
  - **author**: al-Biruni
  - **work**: Kitab al-Tafhim
  - **edition id**: wright_1934_halle_facing_scan
  - **rules loaded**: 15
  - **implementation status**: research_verified
  - **publication status**: research_only
- **sect**:
  - **nativity sect**: diurnal
  - **western sect label**: day
  - **sun altitude degrees**: 9.8747
  - **ascendant longitude**: 151.5017
  - **horizon test**: zodiacal arc against the Ascendant-Descendant axis
  - **sun arc test agrees with altitude**: True
- **classifications**:
  - **male signs**: aries, gemini, leo, libra, sagittarius, aquarius
  - **female signs**: taurus, cancer, virgo, scorpio, capricorn, pisces
  - **male planets**: saturn, jupiter, mars, sun
  - **female planets**: venus, moon
  - **diurnal planets**: saturn, jupiter, sun
  - **nocturnal planets**: mars, venus, moon
  - **mercury gender**: conditional_on_association; male when alone
  - **mercury sect**: conditional_on_sign_or_associated_planet; the inspected passage gives no conflict priority
- **planetary conditions**:
  - body Sun, sign Leo, sign gender male, above horizon True, planet sect diurnal, planet gender male, halb True, hayyiz True, resolution resolved
  - body Moon, sign Leo, sign gender male, above horizon True, planet sect nocturnal, planet gender female, halb False, hayyiz False, resolution resolved
  - body Mercury, sign Virgo, sign gender female, above horizon False, planet sect nocturnal, planet gender male, halb True, hayyiz False, resolution resolved
  - body Venus, sign Cancer, sign gender female, above horizon True, planet sect nocturnal, planet gender female, halb False, hayyiz False, resolution resolved
  - body Mars, sign Cancer, sign gender female, above horizon True, planet sect nocturnal, planet gender male, halb False, hayyiz False, resolution resolved
  - body Jupiter, sign Capricorn, sign gender female, above horizon False, planet sect diurnal, planet gender male, halb False, hayyiz False, resolution resolved
  - body Saturn, sign Aries, sign gender male, above horizon True, planet sect diurnal, planet gender male, halb True, hayyiz True, resolution resolved
- **condition summary**:
  - **halb definition**: true when a diurnal planet is above the horizon by day or below it by night, or a nocturnal planet is above by night or below by day
  - **hayyiz definition**: halb plus agreement between planet gender and sign gender
  - **implication**: every hayyiz is halb; not every halb is hayyiz
  - **in halb**: Sun, Mercury, Saturn
  - **in hayyiz**: Sun, Saturn
  - **halb without hayyiz**: Mercury
  - **one way implication holds**: True
  - **joy boundary**: Section 498 lists halb or hayyiz among several joy conditions. This pack does not infer a complete judgment, cancel debility, or change benefic/malefic nature.
- **mercury resolution**:
  - **basis**: alone_in_sign
  - **associates**: 
  - **gender**: male
  - **gender basis**: al-Biruni: Mercury is male when alone
  - **sect**: nocturnal
  - **sect basis**: al-Biruni: conditional on the sign; the sign's gender carries its day/night classification
  - **conflict**: False
  - **sign**: Virgo
  - **al qabisi difference**: The inspected al-Qabisi chapter II, Arabic and John of Seville's Latin, describes Mercury as male and diurnal outright. al-Biruni is the controlling author here, so al-Qabisi's classification is recorded as a cross-author difference and not substituted.
- **mars case**:
  - **rule id**: islamicate.al_biruni.condition.mars_hayyiz
  - **pack note**: Mars is male and nocturnal, so it requires the nocturnal horizon condition and a male sign
  - **planet gender**: male
  - **planet sect**: nocturnal
  - **required horizon**: above the horizon by night, or below it by day
  - **required sign gender**: male
  - **sign**: Cancer
  - **sign gender**: female
  - **horizon requirement met**: False
  - **sign requirement met**: False
  - **halb**: False
  - **hayyiz**: False
- **firdaria**:
  - **nativity sect**: diurnal
  - **rule id**: islamicate.al_biruni.firdaria.major_order.diurnal
  - **source section**: 395, Firdaria of planets (printed p. 239)
  - **major order**: sun, venus, mercury, moon, saturn, jupiter, mars
  - **descending cycle**: saturn, jupiter, mars, sun, venus, mercury, moon
  - **subperiods per major period**: 7
  - **subperiod rule**: The first seventh belongs to the major chronocrator alone; each later seventh joins it with the next planet below in the descending cycle.
  - **first major period**:
    - **major ruler**: sun
    - **subperiods**:
      - index 1, fraction start 0/7, fraction end 1/7, rulers ['sun']
      - index 2, fraction start 1/7, fraction end 2/7, rulers ['sun', 'venus']
      - index 3, fraction start 2/7, fraction end 3/7, rulers ['sun', 'mercury']
      - index 4, fraction start 3/7, fraction end 4/7, rulers ['sun', 'moon']
      - index 5, fraction start 4/7, fraction end 5/7, rulers ['sun', 'saturn']
      - index 6, fraction start 5/7, fraction end 6/7, rulers ['sun', 'jupiter']
      - index 7, fraction start 6/7, fraction end 7/7, rulers ['sun', 'mars']
  - **subperiod series**:
    - sequence 1, major ruler sun, sevenths ['sun', 'sun+venus', 'sun+mercury', 'sun+moon', 'sun+saturn', 'sun+jupiter', 'sun+mars']
    - sequence 2, major ruler venus, sevenths ['venus', 'venus+mercury', 'venus+moon', 'venus+saturn', 'venus+jupiter', 'venus+mars', 'venus+sun']
    - sequence 3, major ruler mercury, sevenths ['mercury', 'mercury+moon', 'mercury+saturn', 'mercury+jupiter', 'mercury+mars', 'mercury+sun', 'mercury+venus']
    - sequence 4, major ruler moon, sevenths ['moon', 'moon+saturn', 'moon+jupiter', 'moon+mars', 'moon+sun', 'moon+venus', 'moon+mercury']
    - sequence 5, major ruler saturn, sevenths ['saturn', 'saturn+jupiter', 'saturn+mars', 'saturn+sun', 'saturn+venus', 'saturn+mercury', 'saturn+moon']
    - sequence 6, major ruler jupiter, sevenths ['jupiter', 'jupiter+mars', 'jupiter+sun', 'jupiter+venus', 'jupiter+mercury', 'jupiter+moon', 'jupiter+saturn']
    - sequence 7, major ruler mars, sevenths ['mars', 'mars+sun', 'mars+venus', 'mars+mercury', 'mars+moon', 'mars+saturn', 'mars+jupiter']
  - **durations emitted**: False
  - **node periods emitted**: False
  - **duration refusal rule id**: islamicate.al_biruni.firdaria.duration.unresolved
  - **duration refusal**: al-Biruni, Kitab al-Tafhim section 395 states neither node periods nor a table of major-period durations. This section therefore emits the ordering and the equal-seventh structure and refuses every age, year count, and calendar date derived from them.
- **variant concordance**:
  - **corpus**: University of Wurzburg Arabic and Latin Corpus 0.4.0
  - **retrieved**: 2026-08-01
  - **witness lineages**: Arabic (al-Biruni, Abu Ma'shar, al-Qabisi), Latin - Hermann of Carinthia, Latin - John of Seville, Latin - Adelard of Bath
  - **candidate passages**: 30
  - **preserved variants**: 8
  - **firdaria year values by lineage**:
    - author Abu Ma'shar al-Balkhi, work Kitab al-Mudkhal al-Kabir (Great Introduction), lineage Arabic, passage VII.8 p. 800, mars years 7, moon years 9, recomputed total 75, stated total 75, totals agree True, listed values {'sun': 10, 'venus': 8, 'mercury': 13, 'moon': 9, 'saturn': 11, 'jupiter': 12, 'mars': 7, 'north_node': 3, 'south_node': 2}, status candidate_only
    - author Abu Ma'shar al-Balkhi, work Kitab al-Mudkhal al-Kabir (Great Introduction), lineage Latin - Hermann of Carinthia, passage chapter 8 p. 143, mars years 8, moon years 9, recomputed total 76, stated total None, totals agree None, listed values {'sun': 10, 'venus': 8, 'mercury': 13, 'moon': 9, 'saturn': 11, 'jupiter': 12, 'mars': 8, 'north_node': 3, 'south_node': 2}, status candidate_numeric_variant_apparatus_required
    - author Abu Ma'shar al-Balkhi, work Kitab al-Mudkhal al-Kabir (Great Introduction), lineage Latin - John of Seville, passage differentia VIII p. 310, mars years 7, moon years 8, recomputed total 74, stated total 75, totals agree False, listed values {'sun': 10, 'venus': 8, 'mercury': 13, 'jupiter': 12, 'mars': 7, 'moon': 8, 'saturn': 11, 'north_node': 3, 'south_node': 2}, status candidate_order_and_numeric_variant_apparatus_required
    - author al-Qabisi, work Kitab al-Mudkhal ila Sina'at Ahkam al-Nujum (Introduction), lineage Arabic, passage chapter II pp. 64-88, mars years 7, moon years 9, recomputed total 75, stated total None, totals agree None, listed values {'sun': 10, 'venus': 8, 'mercury': 13, 'moon': 9, 'saturn': 11, 'jupiter': 12, 'mars': 7, 'north_node': 3, 'south_node': 2}, status candidate_only
    - author al-Qabisi, work Kitab al-Mudkhal ila Sina'at Ahkam al-Nujum (Introduction), lineage Latin - John of Seville, passage chapter 2 pp. 270-293, mars years 7, moon years 9, recomputed total 75, stated total None, totals agree None, listed values {'sun': 10, 'venus': 8, 'mercury': 13, 'moon': 9, 'saturn': 11, 'jupiter': 12, 'mars': 7, 'north_node': 3, 'south_node': 2}, status candidate_translation_lineage
    - author Abu Ma'shar al-Balkhi, work Mukhtasar al-Mudkhal (Abbreviation), lineage Arabic, passage chapter 7 p. 80, mars years 7, moon years 9, recomputed total 75, stated total 75, totals agree True, listed values {'sun': 10, 'venus': 8, 'mercury': 13, 'moon': 9, 'saturn': 11, 'jupiter': 12, 'mars': 7, 'north_node': 3, 'south_node': 2}, status candidate_only_separate_work
    - author Abu Ma'shar al-Balkhi, work Mukhtasar al-Mudkhal (Abbreviation), lineage Latin - Adelard of Bath, passage chapter 7 p. 136, mars years 7, moon years 9, recomputed total 75, stated total 77, totals agree False, listed values {'sun': 10, 'venus': 8, 'mercury': 13, 'moon': 9, 'saturn': 11, 'jupiter': 12, 'mars': 7, 'north_node': 3, 'south_node': 2}, status candidate_total_variant_apparatus_required
  - **observations**:
    - observation id firdaria_great_introduction_mars_variant, type numeric_translation_lineage_variant, evidence The Arabic p. 800 and John p. 310 list Mars as 7; Hermann p. 143 lists Mars as 8., resolution unresolved_pending_2019_apparatus, engine action refuse_cross_lineage_value_selection
    - observation id firdaria_great_introduction_john_internal_total, type internal_arithmetic_and_order_conflict, evidence John p. 310 lists values summing to 74, including a bracketed Moon value of 8, but states a total of 75 and orders Jupiter and Mars before Moon and Saturn., resolution unresolved_pending_2019_apparatus, engine action refuse_unreviewed_rule_promotion
    - observation id firdaria_abbreviation_latin_total, type internal_arithmetic_conflict, evidence The Adelard Latin p. 136 values sum to 75 but the text states 77; the Arabic p. 80 values and stated total are both 75., resolution unresolved_pending_1994_apparatus, engine action preserve_both_recorded_and_recomputed_totals
    - observation id halb_hayyiz_qabisi_latin_terminology, type translation_terminology_boundary, evidence The Qabisi Arabic p. 60 uses separate halb and hayyiz tokens within the definition; Latin p. 266 uses alhaiz and aiz for the two stages., resolution unresolved_pending_arabic_and_apparatus_review, engine action do_not_normalize_terms_automatically
    - observation id halb_lexeme_semantic_anomaly, type cross_passage_lexical_anomaly, evidence Great Introduction Arabic p. 786 and Abbreviation Arabic p. 52 contain a halb-form token immediately glossed through dignities and joys, unlike the horizon use in Qabisi p. 60 and the al-Biruni baseline., resolution unresolved_pending_arabic_collation_and_apparatus, engine action do_not_equate_surface_forms_across_passages
    - observation id hayyiz_abbreviation_competentia, type translation_semantic_rendering, evidence The Abbreviation Arabic p. 40 names hayyiz; Adelard p. 110 renders the corresponding first planetary condition as competentia rather than a transliteration., resolution candidate_alignment_pending_apparatus, engine action retain_translation_specific_term
    - observation id mercury_author_scope_difference, type author_scoped_classification_difference, evidence The inspected Qabisi chapter II Arabic and Latin describe Mercury as male and diurnal, while the existing al-Biruni pack keeps Mercury conditional on context., resolution candidate_difference_pending_controlling_translation_review, engine action prohibit_cross_author_mercury_default
    - observation id firdaria_scope_not_contradiction, type passage_scope_difference, evidence Al-Biruni section 395 omits duration and node tables in the inspected passage; Qabisi chapters II and IV and Abu Ma'shar's year-value passages include them., resolution preserve_as_scope_difference, engine action do_not_backfill_al_biruni_from_other_authors
  - **hard invariants**: No candidate passage is a doctrinal rule., No Arabic token is translated by this concordance., No Latin translation lineage overrides the Arabic witness or another Latin lineage., The Great Introduction and the Abbreviation remain different works., Arithmetic disagreement is preserved as evidence and is never silently corrected., Absence from one inspected passage is not absence from an author's complete corpus., Only the Western engine is live; every item here remains research-only and customer-ineligible.
- **distinctive layers computed**: sect and its planetary consequences, halb and hayyiz for the seven classical planets, planetary and sign gender/sect classification, Mercury's conditional classification, firdaria ordering, diurnal and nocturnal, equal-seventh subperiod structure
- **distinctive layers gated**: firdaria period durations and dates, Abu Ma'shar Great Introduction doctrine, al-Qabisi Introduction doctrine, lunar mansions, tasyir / directions

**Reading**

Sect first, because every condition rule in this section is conditioned on it. The Sun stands above the horizon at birth, so this is a diurnal nativity. al-Biruni (Kitab al-Tafhim, sections 386 and 396-401, Wright 1934 facing edition) puts Saturn, Jupiter and the Sun in the diurnal sect and Mars, Venus and the Moon in the nocturnal sect, and leaves Mercury conditional.

Planetary condition, al-Biruni section 496: a planet is in halb when a diurnal planet stands above the horizon by day or below it by night, or a nocturnal planet above by night or below by day. It is in hayyiz when it is in halb and additionally occupies a sign of its own gender. The implication runs one way only - every hayyiz is a halb, and a halb is not thereby a hayyiz.

In this chart Sun, Mercury and Saturn hold halb, and Sun and Saturn hold hayyiz. Mercury holds halb without hayyiz, which is al-Biruni's one-way implication showing up in the chart itself.

Mars is the case al-Biruni singles out in section 496: male in gender but nocturnal in sect, so it needs the nocturnal horizon condition - above by night or below by day - and a male sign. Here Mars is in Cancer, a female sign, and it fails the horizon condition and fails the sign condition: halb False, hayyiz False.

Mercury is conditional in al-Biruni, not fixed: sections 385-386 make its gender depend on association and its sect on the sign or an associated planet, and give no priority when those bases disagree. It is alone in its sign here, so this section reads it as male and nocturnal, rather than defaulting. al-Qabisi, by contrast, describes Mercury as male and diurnal outright in the inspected chapter II, in both the Arabic and John of Seville's Latin. al-Biruni is the controlling author for this section, so al-Qabisi's classification is recorded as a cross-author difference and is not substituted.

Section 498 lists halb and hayyiz among several conditions of a planet's joy. al-Biruni does not there cancel a debility or change a planet's benefic or malefic nature, and neither does this section: the flags above are one condition, not a verdict.

Firdaria, as structure only. al-Biruni, section 395, calls the firdaria a Persian idea and gives the diurnal order as Sun, Venus, Mercury, Moon, Saturn, Jupiter, Mars. Each major period divides into seven equal parts: the first belongs to the major chronocrator alone and each later seventh joins it with the next planet below in the descending cycle Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon - so the opening Sun period runs Sun, Sun+Venus, Sun+Mercury, Sun+Moon, Sun+Saturn, Sun+Jupiter, Sun+Mars.

No firdaria ages or dates follow from that. The inspected section 395 supplies neither node periods nor a table of major-period durations, so what al-Biruni gives here is an ordering without a clock. Duration tables do exist in Abu Ma'shar and al-Qabisi - and they disagree with each other and with themselves, which is what the rest of this section records.

Variant, Mars firdaria years - Abu Ma'shar al-Balkhi, Great Introduction. The Arabic witness (VII.8, p. 800) gives Mars 7 years; Hermann of Carinthia's Latin (chapter 8, p. 143) gives 8. Neither lineage overrides the other, so both are recorded and neither is selected [firdaria_great_introduction_mars_variant].

Variant, internal arithmetic - John of Seville's Latin of the same Great Introduction (differentia VIII, p. 310) lists values that sum to 74, including a bracketed Moon of 8, while stating a total of 75, and it orders Jupiter and Mars ahead of the Moon and Saturn. The conflict is preserved as evidence and never silently corrected [firdaria_great_introduction_john_internal_total].

Variant, internal arithmetic - Adelard of Bath's Latin of Abu Ma'shar's Abbreviation, a separate work from the Great Introduction (chapter 7, p. 136), lists values summing to 75 but states 77; the Arabic of the same work (chapter 7, p. 80) lists 75 and states 75. Both the recorded and the recomputed totals are kept [firdaria_abbreviation_latin_total].

Variant, terminology - al-Qabisi's Arabic (chapter I, p. 60) carries distinct halb and hayyiz tokens inside one definition, while John of Seville's Latin of that chapter (chapter 1, p. 266) collapses the two stages into alhaiz and aiz; Adelard of Bath, translating the Abbreviation (chapter 3, p. 110), drops the transliteration entirely and writes competentia. This section does not normalise those terms onto one another [halb_hayyiz_qabisi_latin_terminology, hayyiz_abbreviation_competentia].

Variant, lexical - a halb-form token in the Great Introduction Arabic (p. 786) and the Abbreviation Arabic (p. 52) is glossed through dignities and joys rather than the horizon, unlike al-Qabisi p. 60 and the al-Biruni baseline. Surface forms are not equated across passages [halb_lexeme_semantic_anomaly].

Finally, a scope difference rather than a contradiction: al-Biruni's section 395 simply omits the duration and node tables that al-Qabisi (chapters II and IV) and Abu Ma'shar (the year-value passages) do carry. al-Biruni is not backfilled from them [firdaria_scope_not_contradiction].

---

## Medieval Jewish (Ibn Ezra)

*Evidence: validated research pack*

Shares the Western calculation core. Distinctive layer: Ibn Ezra's Book of Revolutions method from the validated pack.

**Disclosures**

- **Source — Pack provenance.** Ibn Ezra revolutions rules come from a validated pack built on the parallel Hebrew-English critical edition, and already drive the solar-return layer of the live premium report.
- **Refused — Nativities treatise.** The Book of Nativities module remains source-limited: its rule and precedence extraction is not complete, so no natal doctrine specific to it is asserted here.

**Calculation**

- **shared calculation core**: western_traditional
- **distinctive layers available**: Ibn Ezra annual revolution comparison (validated), sect-light triplicity ruler phases (validated)
- **distinctive layers gated**: Book of Nativities natal doctrine

---

## Vedic (Jyotisha)

*Evidence: configured method*

Swiss Ephemeris sidereal positions; whole-sign houses; Vimshottari mahadasha and antardasha keyed to the Moon's nakshatra; navamsha, drishti, combustion and naisargika relations computed.

**Disclosures**

- **Configured — Ayanamsa.** Lahiri (Chitrapaksha) selected. The engine supports eight ayanamsas and no validated research pack selects one; a different choice shifts every sidereal longitude and can move a placement across a sign boundary. *Alternatives: Fagan-Bradley, Krishnamurti, Raman, True Citra, True Revati, Surya Siddhanta, Hipparchos.*
- **Configured — House system.** Whole-sign houses, the dominant classical Jyotisha convention. Sripati and equal-house variants exist and would move cusp-adjacent placements. *Alternatives: Sripati, Equal house from the lagna degree.*
- **Configured — Nodes.** Mean nodes used for Rahu/Ketu. True-node calculation differs by up to about 1.5 degrees and is a live disagreement between schools. *Alternatives: True node.*
- **Source — Navamsha.** D9 is computed for every graha and the lagna, with vargottama flagged. Jyotisha treats the navamsha as mandatory rather than optional: a D1 verdict that D9 contradicts is not a finished judgment.
- **Configured — Combustion orbs (astangata).** Combustion is flagged from a configured orb table measured as ecliptic-longitude separation from the Sun: Moon 12, Mars 17, Mercury 14 (12 when retrograde), Jupiter 11, Venus 10 (8 when retrograde), Saturn 15 degrees. These are widely-cited traditional values, but texts and schools differ by several degrees and a different table moves grahas across the combustion boundary. *Alternatives: orb sets differing by several degrees between texts and schools, latitude-corrected (true) angular distance instead of longitude difference, no retrograde reduction for Mercury and Venus.*
- **Configured — Drishti scheme.** Graha drishti is computed whole-sign by house: the 7th from every graha, with Mars adding the 4th and 8th, Jupiter the 5th and 9th, and Saturn the 3rd and 10th. Rahu and Ketu receive the 7th only; the extended nodal aspects some schools grant them are not asserted, and no degree-based drishti strength (drishti bala) is computed. *Alternatives: Rahu/Ketu granted 5th and 9th aspects, Degree-proportional drishti strength.*
- **Configured — Graha friendship.** Only naisargika (natural, permanent) friendship is computed, from the standard BPHS table. Tatkalika (temporary, sign-distance) friendship and the panchadha compound relation it produces are NOT computed, so no compound-relation dignity claim is made. Rahu and Ketu carry no agreed naisargika row and are excluded. *Alternatives: Tatkalika friendship, Panchadha (compound) relation.*
- **Configured — Yoga scope.** Only three structurally verifiable classes are tested - yogakaraka, Raja Yoga, and Dhana Yoga - each reported with the constituent facts that made it true. No yoga catalogue is applied and no phala (result) is attached to any detected yoga.
- **Refused — Lifespan (ayurdaya).** No lifespan or longevity claim is made. Ayurdaya methods are recension-dependent and their branches disagree; length-of-life arithmetic is not asserted from this section.
- **Refused — Muhurta and remedies.** No electional (muhurta) timing and no remedial prescription - gemstone, mantra, ritual, donation - is given. Those are prescriptive advice rather than historical delineation.
- **Refused — Varna and social rank.** No caste, varna, or social-rank delineation is rendered as a claim about the reader, even where the classical sources state one. The material stays in the audit trace with its suppression reason.
- **Refused — Marriage compatibility.** No marriage-compatibility verdict (kuta / guna milan) is produced. It requires a second chart and its own source treatment, and is not a natal-reading output.
- **Refused — Shadbala and Ashtakavarga.** Shadbala and Ashtakavarga are not implemented - their weights are recension-dependent and unsourced here - so no strength claim, yoga, or period judgment depending on either is made anywhere in this section.
- **Refused — Interpretation depth.** This section reports calculation and structural condition only. Divisional charts beyond D1 and D9 are not computed, and moolatrikona boundaries are pending, so no claim resting on them is made.

**Calculation**

- **ayanamsa degrees**: 23.809826
- **lagna**:
  - **rasi**: Leo
  - **degree in sign**: 7.6918
  - **lord**: Sun
  - **nakshatra**: Magha
  - **pada**: 3
  - **nakshatra lord**: Ketu
  - **navamsha**: Gemini
  - **navamsha lord**: Mercury
  - **vargottama**: False
- **janma rasi**: Cancer
- **janma nakshatra**:
  - **name**: Ashlesha
  - **pada**: 1
  - **lord**: Mercury
- **grahas**:
  - graha Sun, rasi Cancer, degree in sign 27.2855, house 12, nakshatra Ashlesha, pada 4, nakshatra lord Mercury, dignity neutral placement, navamsha Pisces, navamsha division 9, navamsha dignity neutral placement, vargottama False, retrograde False, dispositor Moon, dispositor relation friend, combust False, solar separation degrees 0.0, combustion orb degrees None, drishti houses [6]
  - graha Moon, rasi Cancer, degree in sign 19.4353, house 12, nakshatra Ashlesha, pada 1, nakshatra lord Mercury, dignity own sign, navamsha Sagittarius, navamsha division 6, navamsha dignity neutral placement, vargottama False, retrograde False, dispositor Moon, dispositor relation own sign lord, combust True, solar separation degrees 7.8502, combustion orb degrees 12.0, drishti houses [6]
  - graha Mercury, rasi Leo, degree in sign 23.3715, house 1, nakshatra Purva Phalguni, pada 4, nakshatra lord Venus, dignity neutral placement, navamsha Scorpio, navamsha division 8, navamsha dignity neutral placement, vargottama False, retrograde False, dispositor Sun, dispositor relation friend, combust False, solar separation degrees 26.086, combustion orb degrees 14.0, drishti houses [7]
  - graha Venus, rasi Gemini, degree in sign 11.7285, house 11, nakshatra Ardra, pada 2, nakshatra lord Rahu, dignity neutral placement, navamsha Capricorn, navamsha division 4, navamsha dignity neutral placement, vargottama False, retrograde False, dispositor Mercury, dispositor relation friend, combust False, solar separation degrees 45.5571, combustion orb degrees 10.0, drishti houses [5]
  - graha Mars, rasi Gemini, degree in sign 18.7086, house 11, nakshatra Ardra, pada 4, nakshatra lord Rahu, dignity neutral placement, navamsha Pisces, navamsha division 6, navamsha dignity neutral placement, vargottama False, retrograde False, dispositor Mercury, dispositor relation enemy, combust False, solar separation degrees 38.5769, combustion orb degrees 17.0, drishti houses [2, 5, 6]
  - graha Jupiter, rasi Sagittarius, degree in sign 14.6973, house 5, nakshatra Purva Ashadha, pada 1, nakshatra lord Venus, dignity own sign, navamsha Leo, navamsha division 5, navamsha dignity neutral placement, vargottama False, retrograde True, dispositor Jupiter, dispositor relation own sign lord, combust False, solar separation degrees 137.4118, combustion orb degrees 11.0, drishti houses [1, 9, 11]
  - graha Saturn, rasi Pisces, degree in sign 13.0418, house 8, nakshatra Uttara Bhadrapada, pada 3, nakshatra lord Saturn, dignity neutral placement, navamsha Libra, navamsha division 4, navamsha dignity exalted, vargottama False, retrograde True, dispositor Jupiter, dispositor relation neutral, combust False, solar separation degrees 134.2437, combustion orb degrees 15.0, drishti houses [2, 5, 10]
  - graha Rahu, rasi Virgo, degree in sign 16.6805, house 2, nakshatra Hasta, pada 3, nakshatra lord Moon, dignity not assessed for nodes, navamsha Gemini, navamsha division 6, navamsha dignity not assessed for nodes, vargottama False, retrograde True, dispositor Mercury, dispositor relation not assessed for nodes, combust False, solar separation degrees 49.395, combustion orb degrees None, drishti houses [8]
  - graha Ketu, rasi Pisces, degree in sign 16.6805, house 8, nakshatra Revati, pada 1, nakshatra lord Mercury, dignity not assessed for nodes, navamsha Sagittarius, navamsha division 6, navamsha dignity not assessed for nodes, vargottama False, retrograde True, dispositor Jupiter, dispositor relation not assessed for nodes, combust False, solar separation degrees 130.605, combustion orb degrees None, drishti houses [2]
- **houses**:
  - house 1, rasi Leo, lord Sun
  - house 2, rasi Virgo, lord Mercury
  - house 3, rasi Libra, lord Venus
  - house 4, rasi Scorpio, lord Mars
  - house 5, rasi Sagittarius, lord Jupiter
  - house 6, rasi Capricorn, lord Saturn
  - house 7, rasi Aquarius, lord Saturn
  - house 8, rasi Pisces, lord Jupiter
  - house 9, rasi Aries, lord Mars
  - house 10, rasi Taurus, lord Venus
  - house 11, rasi Gemini, lord Mercury
  - house 12, rasi Cancer, lord Moon
- **house lordships**:
  - **Jupiter**: 5, 8
  - **Mars**: 4, 9
  - **Mercury**: 2, 11
  - **Moon**: 12
  - **Saturn**: 6, 7
  - **Sun**: 1
  - **Venus**: 3, 10
- **drishti**:
  - graha Sun, from house 12, from rasi Cancer, aspects ['7th aspect to house 6'], aspects houses [6], aspects grahas [], special drishti none
  - graha Moon, from house 12, from rasi Cancer, aspects ['7th aspect to house 6'], aspects houses [6], aspects grahas [], special drishti none
  - graha Mercury, from house 1, from rasi Leo, aspects ['7th aspect to house 7'], aspects houses [7], aspects grahas [], special drishti none
  - graha Venus, from house 11, from rasi Gemini, aspects ['7th aspect to house 5'], aspects houses [5], aspects grahas ['Jupiter'], special drishti none
  - graha Mars, from house 11, from rasi Gemini, aspects ['4th aspect to house 2', '7th aspect to house 5', '8th aspect to house 6'], aspects houses [2, 5, 6], aspects grahas ['Rahu', 'Jupiter'], special drishti 4th, 8th
  - graha Jupiter, from house 5, from rasi Sagittarius, aspects ['5th aspect to house 9', '7th aspect to house 11', '9th aspect to house 1'], aspects houses [1, 9, 11], aspects grahas ['Mercury', 'Venus', 'Mars'], special drishti 5th, 9th
  - graha Saturn, from house 8, from rasi Pisces, aspects ['3rd aspect to house 10', '7th aspect to house 2', '10th aspect to house 5'], aspects houses [2, 5, 10], aspects grahas ['Rahu', 'Jupiter'], special drishti 3rd, 10th
  - graha Rahu, from house 2, from rasi Virgo, aspects ['7th aspect to house 8'], aspects houses [8], aspects grahas ['Saturn', 'Ketu'], special drishti none
  - graha Ketu, from house 8, from rasi Pisces, aspects ['7th aspect to house 2'], aspects houses [2], aspects grahas ['Rahu'], special drishti none
- **naisargika relations**:
  - **Sun**:
    - **friends**: Moon, Mars, Jupiter
    - **neutral**: Mercury
    - **enemies**: Venus, Saturn
  - **Moon**:
    - **friends**: Sun, Mercury
    - **neutral**: Mars, Jupiter, Venus, Saturn
    - **enemies**: 
  - **Mars**:
    - **friends**: Sun, Moon, Jupiter
    - **neutral**: Venus, Saturn
    - **enemies**: Mercury
  - **Mercury**:
    - **friends**: Sun, Venus
    - **neutral**: Mars, Jupiter, Saturn
    - **enemies**: Moon
  - **Jupiter**:
    - **friends**: Sun, Moon, Mars
    - **neutral**: Saturn
    - **enemies**: Mercury, Venus
  - **Venus**:
    - **friends**: Mercury, Saturn
    - **neutral**: Mars, Jupiter
    - **enemies**: Sun, Moon
  - **Saturn**:
    - **friends**: Mercury, Venus
    - **neutral**: Jupiter
    - **enemies**: Sun, Moon, Mars
- **combustion orbs configured**:
  - **direct**:
    - **Moon**: 12.0
    - **Mars**: 17.0
    - **Mercury**: 14.0
    - **Jupiter**: 11.0
    - **Venus**: 10.0
    - **Saturn**: 15.0
  - **retrograde overrides**:
    - **Mercury**: 12.0
    - **Venus**: 8.0
- **navamsha cross check**:
  - graha Sun, rasi d1 Cancer, dignity d1 neutral placement, rasi d9 Pisces, dignity d9 neutral placement, vargottama False, verdict D9 matches the D1 dignity, diverges False
  - graha Moon, rasi d1 Cancer, dignity d1 own sign, rasi d9 Sagittarius, dignity d9 neutral placement, vargottama False, verdict D9 undercuts the D1 verdict, diverges True
  - graha Mercury, rasi d1 Leo, dignity d1 neutral placement, rasi d9 Scorpio, dignity d9 neutral placement, vargottama False, verdict D9 matches the D1 dignity, diverges False
  - graha Venus, rasi d1 Gemini, dignity d1 neutral placement, rasi d9 Capricorn, dignity d9 neutral placement, vargottama False, verdict D9 matches the D1 dignity, diverges False
  - graha Mars, rasi d1 Gemini, dignity d1 neutral placement, rasi d9 Pisces, dignity d9 neutral placement, vargottama False, verdict D9 matches the D1 dignity, diverges False
  - graha Jupiter, rasi d1 Sagittarius, dignity d1 own sign, rasi d9 Leo, dignity d9 neutral placement, vargottama False, verdict D9 undercuts the D1 verdict, diverges True
  - graha Saturn, rasi d1 Pisces, dignity d1 neutral placement, rasi d9 Libra, dignity d9 exalted, vargottama False, verdict D9 raises the D1 verdict, diverges True
  - graha Rahu, rasi d1 Virgo, dignity d1 not assessed for nodes, rasi d9 Gemini, dignity d9 not assessed for nodes, vargottama False, verdict not assessed for nodes, diverges False
  - graha Ketu, rasi d1 Pisces, dignity d1 not assessed for nodes, rasi d9 Sagittarius, dignity d9 not assessed for nodes, vargottama False, verdict not assessed for nodes, diverges False
- **yogas**:
  - yoga Yogakaraka, grahas ['Mars'], rule one graha ruling both a kendra (4, 7 or 10) and a trikona (5 or 9) from the lagna, summary Mars rules kendra house 4 and trikona house 9., constituent facts ['Mars owns house 4, a kendra.', 'Mars owns house 9, a trikona.', 'Mars itself stands in Gemini in house 11, neutral placement.', 'In D9 Mars falls in Pisces (neutral placement).']
  - yoga Raja Yoga, grahas ['Jupiter', 'Mars'], rule a kendra lord and a trikona lord conjunct or in mutual drishti, summary Jupiter and Mars are in mutual drishti as kendra and trikona lords., relation mutual drishti, constituent facts ['Mars owns kendra house 4.', 'Jupiter owns trikona house 5.', 'Jupiter stands in Sagittarius in house 5, own sign, retrograde.', 'Mars stands in Gemini in house 11, neutral placement.', 'Jupiter casts its 7th aspect from house 5 onto house 11, where Mars stands.', 'Mars casts its 7th aspect from house 11 onto house 5, where Jupiter stands.']
  - yoga Raja Yoga, grahas ['Jupiter', 'Venus'], rule a kendra lord and a trikona lord conjunct or in mutual drishti, summary Jupiter and Venus are in mutual drishti as kendra and trikona lords., relation mutual drishti, constituent facts ['Venus owns kendra house 10.', 'Jupiter owns trikona house 5.', 'Jupiter stands in Sagittarius in house 5, own sign, retrograde.', 'Venus stands in Gemini in house 11, neutral placement.', 'Jupiter casts its 7th aspect from house 5 onto house 11, where Venus stands.', 'Venus casts its 7th aspect from house 11 onto house 5, where Jupiter stands.']
  - yoga Raja Yoga, grahas ['Mars', 'Venus'], rule a kendra lord and a trikona lord conjunct or in mutual drishti, summary Mars and Venus are conjunct as kendra and trikona lords., relation conjunct, constituent facts ['Venus owns kendra house 10.', 'Mars owns trikona house 9.', 'Mars stands in Gemini in house 11, neutral placement.', 'Venus stands in Gemini in house 11, neutral placement.', 'Mars and Venus occupy the same house (11) - conjunction verified by whole-sign co-tenancy.']
  - yoga Dhana Yoga, grahas ['Mercury'], rule one graha ruling two or more of houses 1, 2, 5, 9, 11, summary Mercury rules dhana houses 2, 11., constituent facts ['Mercury owns houses 2, 11, all of them among the dhana houses 1, 2, 5, 9, 11.', 'Mercury stands in Leo in house 1, neutral placement.', 'In D9 Mercury falls in Scorpio (neutral placement).']
  - yoga Dhana Yoga, grahas ['Jupiter', 'Mars'], rule two lords of houses 1, 2, 5, 9, 11 conjunct or in mutual drishti, summary Jupiter and Mars are dhana lords, in mutual drishti., relation mutual drishti, constituent facts ['Jupiter owns dhana house 5.', 'Mars owns dhana house 9.', 'Jupiter stands in Sagittarius in house 5, own sign, retrograde.', 'Mars stands in Gemini in house 11, neutral placement.', 'The two are in mutual drishti.']
- **vimshottari mahadashas**:
  - lord Mercury, start 1996-08-13, end 2010-02-01, years 13.47, partial at birth True
  - lord Ketu, start 2010-02-01, end 2017-01-31, years 7, partial at birth False
  - lord Venus, start 2017-01-31, end 2037-01-31, years 20, partial at birth False
  - lord Sun, start 2037-01-31, end 2043-02-01, years 6, partial at birth False
  - lord Moon, start 2043-02-01, end 2053-01-31, years 10, partial at birth False
  - lord Mars, start 2053-01-31, end 2060-02-01, years 7, partial at birth False
  - lord Rahu, start 2060-02-01, end 2078-01-31, years 18, partial at birth False
  - lord Jupiter, start 2078-01-31, end 2094-01-31, years 16, partial at birth False
  - lord Saturn, start 2094-01-31, end 2113-02-01, years 19, partial at birth False
  - lord Mercury, start 2113-02-01, end 2130-02-01, years 17, partial at birth False
- **vimshottari antardashas**:
  - **mahadasha lord**: Venus
  - **mahadasha full years**: 20
  - **mahadasha partial at birth**: False
  - **notional start**: 2017-01-31
  - **subdivision rule**: antardasha_years = mahadasha_years * antardasha_lord_years / 120
  - **sum of antardasha years**: 20.0
  - **periods**:
    - mahadasha lord Venus, antardasha lord Venus, start 2017-01-31, end 2020-06-02, years 3.333333, before birth False
    - mahadasha lord Venus, antardasha lord Sun, start 2020-06-02, end 2021-06-02, years 1.0, before birth False
    - mahadasha lord Venus, antardasha lord Moon, start 2021-06-02, end 2023-02-01, years 1.666667, before birth False
    - mahadasha lord Venus, antardasha lord Mars, start 2023-02-01, end 2024-04-02, years 1.166667, before birth False
    - mahadasha lord Venus, antardasha lord Rahu, start 2024-04-02, end 2027-04-03, years 3.0, before birth False
    - mahadasha lord Venus, antardasha lord Jupiter, start 2027-04-03, end 2029-12-02, years 2.666667, before birth False
    - mahadasha lord Venus, antardasha lord Saturn, start 2029-12-02, end 2033-01-31, years 3.166667, before birth False
    - mahadasha lord Venus, antardasha lord Mercury, start 2033-01-31, end 2035-12-02, years 2.833333, before birth False
    - mahadasha lord Venus, antardasha lord Ketu, start 2035-12-02, end 2037-01-31, years 1.166667, before birth False
- **vimshottari current**:
  - **as of**: 2026-08-02
  - **status**: running
  - **mahadasha**:
    - **lord**: Venus
    - **start**: 2017-01-31
    - **end**: 2037-01-31
    - **years**: 20
    - **partial at birth**: False
  - **antardasha**:
    - **mahadasha lord**: Venus
    - **antardasha lord**: Rahu
    - **start**: 2024-04-02
    - **end**: 2027-04-03
    - **years**: 3.0
    - **before birth**: False

**Reading**

1. Lagna and lagna lord - Leo rises at 7.69 degrees, in Magha pada 3 (nakshatra lord Ketu). Its navamsha is Gemini, lord Mercury; the lagna is not vargottama.

1. Lagna lord - Sun rules Leo and sits in Cancer, house 12, neutral placement. It owns house 1. Everything below is qualified by this condition rather than read around it.

2. Moon, janma rasi and janma nakshatra - Cancer in house 12, Ashlesha pada 1 (lord Mercury); own sign, combust - 7.85 deg from the Sun against a configured 12 deg orb. In Jyotisha the Moon outranks the Sun for personal significations, so this stands above any solar statement in this section.

3. Graha dignity and placement in D1 - stated as condition first, with retrogradation and combustion, before anything is made of it.

3. Sun - Cancer 27.29, house 12, Ashlesha pada 4 (lord Mercury); neutral placement; sign lord Moon, whom Sun naturally regards as friend.

3. Moon - Cancer 19.44, house 12, Ashlesha pada 1 (lord Mercury); own sign, combust - 7.85 deg from the Sun against a configured 12 deg orb; sign lord Moon, whom Moon naturally regards as own sign lord.

3. Mercury - Leo 23.37, house 1, Purva Phalguni pada 4 (lord Venus); neutral placement; sign lord Sun, whom Mercury naturally regards as friend.

3. Venus - Gemini 11.73, house 11, Ardra pada 2 (lord Rahu); neutral placement; sign lord Mercury, whom Venus naturally regards as friend.

3. Mars - Gemini 18.71, house 11, Ardra pada 4 (lord Rahu); neutral placement; sign lord Mercury, whom Mars naturally regards as enemy.

3. Jupiter - Sagittarius 14.70, house 5, Purva Ashadha pada 1 (lord Venus); own sign, retrograde; sign lord Jupiter, whom Jupiter naturally regards as own sign lord.

3. Saturn - Pisces 13.04, house 8, Uttara Bhadrapada pada 3 (lord Saturn); neutral placement, retrograde; sign lord Jupiter, whom Saturn naturally regards as neutral.

3. Rahu - Virgo 16.68, house 2, Hasta pada 3 (lord Moon); not assessed for nodes, retrograde; sign lord Mercury; naisargika relation not assessed for nodes.

3. Ketu - Pisces 16.68, house 8, Revati pada 1 (lord Mercury); not assessed for nodes, retrograde; sign lord Jupiter; naisargika relation not assessed for nodes.

4. Bhava rulership - which graha owns which house, and where that owner actually sits. A house is judged through its lord's condition.

4. Sun owns house 1 - it sits in house 12 (Cancer), neutral placement.

4. Moon owns house 12 - it sits in house 12 (Cancer), own sign, combust - 7.85 deg from the Sun against a configured 12 deg orb.

4. Mercury owns houses 2, 11 - it sits in house 1 (Leo), neutral placement.

4. Venus owns houses 3, 10 - it sits in house 11 (Gemini), neutral placement.

4. Mars owns houses 4, 9 - it sits in house 11 (Gemini), neutral placement.

4. Jupiter owns houses 5, 8 - it sits in house 5 (Sagittarius), own sign, retrograde.

4. Saturn owns houses 6, 7 - it sits in house 8 (Pisces), neutral placement, retrograde.

5. Drishti - every graha aspects the 7th house from itself; Mars adds the 4th and 8th, Jupiter the 5th and 9th, Saturn the 3rd and 10th. Aspects are counted whole-sign by house, not by degree orb.

5. Sun from house 12 (Cancer) - 7th aspect to house 6. No graha stands in the aspected houses.

5. Moon from house 12 (Cancer) - 7th aspect to house 6. No graha stands in the aspected houses.

5. Mercury from house 1 (Leo) - 7th aspect to house 7. No graha stands in the aspected houses.

5. Venus from house 11 (Gemini) - 7th aspect to house 5. Grahas aspected: Jupiter.

5. Mars from house 11 (Gemini) - 4th aspect to house 2; 7th aspect to house 5; 8th aspect to house 6. Grahas aspected: Rahu, Jupiter.

5. Jupiter from house 5 (Sagittarius) - 5th aspect to house 9; 7th aspect to house 11; 9th aspect to house 1. Grahas aspected: Mercury, Venus, Mars.

5. Saturn from house 8 (Pisces) - 3rd aspect to house 10; 7th aspect to house 2; 10th aspect to house 5. Grahas aspected: Rahu, Jupiter.

5. Rahu from house 2 (Virgo) - 7th aspect to house 8. Grahas aspected: Saturn, Ketu.

5. Ketu from house 8 (Pisces) - 7th aspect to house 2. Grahas aspected: Rahu.

6. Navamsha cross-check - D9 either confirms the D1 verdict or undercuts it. A D1 judgment never tested against D9 is not a finished judgment in this tradition.

6. Moon - D1 Cancer (own sign) against D9 Sagittarius (neutral placement). D9 undercuts the D1 verdict; the two are read together, not averaged.

6. Jupiter - D1 Sagittarius (own sign) against D9 Leo (neutral placement). D9 undercuts the D1 verdict; the two are read together, not averaged.

6. Saturn - D1 Pisces (neutral placement) against D9 Libra (exalted). D9 raises the D1 verdict; the two are read together, not averaged.

7. Yogas - reached only after steps 1 to 6, and only for structures whose constituents were verified above. Yogas whose definition needs Shadbala or Ashtakavarga are not evaluated at all.

7. Yogakaraka (Mars) - Mars rules kendra house 4 and trikona house 9. Rule applied: one graha ruling both a kendra (4, 7 or 10) and a trikona (5 or 9) from the lagna. Constituent facts: Mars owns house 4, a kendra. Mars owns house 9, a trikona. Mars itself stands in Gemini in house 11, neutral placement. In D9 Mars falls in Pisces (neutral placement).

7. Raja Yoga (Jupiter, Mars) - Jupiter and Mars are in mutual drishti as kendra and trikona lords. Rule applied: a kendra lord and a trikona lord conjunct or in mutual drishti. Constituent facts: Mars owns kendra house 4. Jupiter owns trikona house 5. Jupiter stands in Sagittarius in house 5, own sign, retrograde. Mars stands in Gemini in house 11, neutral placement. Jupiter casts its 7th aspect from house 5 onto house 11, where Mars stands. Mars casts its 7th aspect from house 11 onto house 5, where Jupiter stands.

7. Raja Yoga (Jupiter, Venus) - Jupiter and Venus are in mutual drishti as kendra and trikona lords. Rule applied: a kendra lord and a trikona lord conjunct or in mutual drishti. Constituent facts: Venus owns kendra house 10. Jupiter owns trikona house 5. Jupiter stands in Sagittarius in house 5, own sign, retrograde. Venus stands in Gemini in house 11, neutral placement. Jupiter casts its 7th aspect from house 5 onto house 11, where Venus stands. Venus casts its 7th aspect from house 11 onto house 5, where Jupiter stands.

7. Raja Yoga (Mars, Venus) - Mars and Venus are conjunct as kendra and trikona lords. Rule applied: a kendra lord and a trikona lord conjunct or in mutual drishti. Constituent facts: Venus owns kendra house 10. Mars owns trikona house 9. Mars stands in Gemini in house 11, neutral placement. Venus stands in Gemini in house 11, neutral placement. Mars and Venus occupy the same house (11) - conjunction verified by whole-sign co-tenancy.

7. Dhana Yoga (Mercury) - Mercury rules dhana houses 2, 11. Rule applied: one graha ruling two or more of houses 1, 2, 5, 9, 11. Constituent facts: Mercury owns houses 2, 11, all of them among the dhana houses 1, 2, 5, 9, 11. Mercury stands in Leo in house 1, neutral placement. In D9 Mercury falls in Scorpio (neutral placement).

7. Dhana Yoga (Jupiter, Mars) - Jupiter and Mars are dhana lords, in mutual drishti. Rule applied: two lords of houses 1, 2, 5, 9, 11 conjunct or in mutual drishti. Constituent facts: Jupiter owns dhana house 5. Mars owns dhana house 9. Jupiter stands in Sagittarius in house 5, own sign, retrograde. Mars stands in Gemini in house 11, neutral placement. The two are in mutual drishti.

8. Dasha - as of 2026-08-02 the running mahadasha is Venus (2017-01-31 to 2037-01-31), and within it the Rahu antardasha (2024-04-02 to 2027-04-03, 3.00 years).

8. Mahadasha lord Venus in the natal structure - Gemini, house 11, neutral placement; it owns houses 3, 10; in D9 Capricorn (neutral placement). The period is read through that qualified condition, never as a free-floating theme.

8. Antardasha lord Rahu in the natal structure - Virgo, house 2, not assessed for nodes, retrograde; it owns no house in the whole-sign scheme; in D9 Gemini (not assessed for nodes). The period is read through that qualified condition, never as a free-floating theme.

8. Period boundaries are calendar arithmetic on a 365.2425-day year from the janma-nakshatra balance. They locate a period, not an event.

---

## Chinese BaZi (Four Pillars)

*Evidence: configured method*

Cycle arithmetic, shichen partition, and stem lookup tables from the validated sexagenary kernel; boundaries supplied as product conventions.

**Disclosures**

- **Source — Kernel provenance.** Stem/branch orders, the sixty-pair cycle, the shichen partition, and both the year-to-month and day-to-hour stem tables come from bazi_sexagenary_kernel_v1, whose standalone validator passes in this repo.
- **Configured — Year boundary.** Li Chun (solar longitude 315 degrees) begins the pillar year - the dominant Ziping convention. Some practice uses the lunar new year, which moves the year pillar for births between the two dates. *Alternatives: Lunar new year, Civil January 1.*
- **Configured — Month boundary.** Months change at the twelve jie (month-establishing solar terms), computed from Swiss Ephemeris solar longitude rather than a printed almanac. *Alternatives: Printed almanac tables, Mean-motion approximations.*
- **Configured — Day anchor.** Sexagenary day count anchored at JDN 2433191 (1949-10-01) = Jia-Zi, cross-checked against 2000-01-01 = Wu-Wu. The research pack registers no day-concordance source, so this anchor is a product choice.
- **Configured — Day rollover.** The civil day is used for the day pillar. Late-Zi schools roll the day pillar forward at 23:00, which changes the day pillar for births between 23:00 and midnight. *Alternatives: Late-Zi rollover at 23:00.*
- **Source — Hidden stems and Ten Gods.** The hidden-stem table and Ten-God relations follow the inspected Yuanhai Ziping / Sanming Tonghui transcriptions (transcription grade: the Wikisource witnesses cannot control wording). Only the undisputed MAIN qi of each branch - which always matches the branch's own element - is used for month-command and rooting judgments; middle and residual qi are reported but carry no judgment weight here.
- **Configured — Month command.** Seasonal command states (wang/xiang/xiu/qiu/si) computed from the month branch's season under the standard five-phase cycle, with Earth commanding the four transition months. The Ziping hierarchy makes this the first substantive judgment, before any strength or pattern claim.
- **Refused — Pattern and useful god.** Pattern (geju) eligibility and useful-element (yongshen) selection are school-specific and stay refused pending edition control. The support assessment below states seasonal state and roots - the facts every school agrees precede those judgments - and draws a summary conclusion only where the testimony is unanimous.
- **Fork — Hour pillar.** True solar time (06:05:05) and clock time (07:18:00) fall in different shichen, so the hour pillar differs: 癸 Gui 卯 Mao versus 甲 Jia 辰 Chen. True solar time is used as primary; both are shown because practice is genuinely divided. *Alternatives: Clock time, Local mean time.*

**Calculation**

- **pillar year used**: 1996
- **li chun boundary utc**: 1996-02-04T13:07:52Z
- **month term start utc**: 1996-08-07T05:48:46Z
- **pillars**:
  - **year**:
    - **stem**: bing
    - **branch**: zi
    - **label**: 丙 Bing 子 Zi
    - **animal**: Rat
    - **stem element**: Fire
    - **branch element**: Water
  - **month**:
    - **stem**: bing
    - **branch**: shen
    - **label**: 丙 Bing 申 Shen
    - **animal**: Monkey
    - **stem element**: Fire
    - **branch element**: Metal
  - **day**:
    - **stem**: ren
    - **branch**: wu_branch
    - **label**: 壬 Ren 午 Wu
    - **animal**: Horse
    - **stem element**: Water
    - **branch element**: Fire
  - **hour**:
    - **stem**: gui
    - **branch**: mao
    - **label**: 癸 Gui 卯 Mao
    - **animal**: Rabbit
    - **stem element**: Water
    - **branch element**: Wood
- **hour pillar candidates**:
  - **true solar time**:
    - **time**: 06:05:05
    - **stem**: gui
    - **branch**: mao
    - **label**: 癸 Gui 卯 Mao
  - **clock time**:
    - **time**: 07:18:00
    - **stem**: jia
    - **branch**: chen
    - **label**: 甲 Jia 辰 Chen
  - **local mean time**:
    - **time**: 06:09:50
    - **stem**: gui
    - **branch**: mao
    - **label**: 癸 Gui 卯 Mao
- **day master**:
  - **stem**: ren
  - **label**: 壬 Ren
  - **element**: Water
  - **polarity**: yang
- **month command**:
  - **season of month branch**: Metal
  - **day master state**: xiang 相 (assisting)
  - **root in month branch**: True
  - **root branches**: year, month
  - **support assessment**: supported: the day master is in seasonal command and rooted in the month branch itself
- **hidden stems**:
  - **year**:
    - stem gui, label 癸 Gui, element Water, qi main, ten god 劫財 Rob Wealth
  - **month**:
    - stem geng, label 庚 Geng, element Metal, qi main, ten god 偏印 Indirect Resource
    - stem ren, label 壬 Ren, element Water, qi middle, ten god 比肩 Friend
    - stem wu_stem, label 戊 Wu, element Earth, qi residual, ten god 七殺 Seven Killings
  - **day**:
    - stem ding, label 丁 Ding, element Fire, qi main, ten god 正財 Direct Wealth
    - stem ji, label 己 Ji, element Earth, qi middle, ten god 正官 Direct Officer
  - **hour**:
    - stem yi, label 乙 Yi, element Wood, qi main, ten god 傷官 Hurting Officer
- **visible stem ten gods**:
  - **year**: 偏財 Indirect Wealth
  - **month**: 偏財 Indirect Wealth
  - **hour**: 劫財 Rob Wealth
- **element tally**:
  - **Wood**: 1
  - **Fire**: 3
  - **Earth**: 0
  - **Metal**: 1
  - **Water**: 3
- **luck pillars**:
  - **start age**: 8.256
  - **direction rule**: Yang-stem year with male native, or yin-stem year with female native, runs forward; the complementary cases run reverse.
  - **year stem polarity**: yang
  - **sequences**:
    - **forward**:
      - age from 8.26, age to 18.26, start 2004-11-14, end 2014-11-15, label 丁 Ding 酉 You
      - age from 18.26, age to 28.26, start 2014-11-15, end 2024-11-14, label 戊 Wu 戌 Xu
      - age from 28.26, age to 38.26, start 2024-11-14, end 2034-11-14, label 己 Ji 亥 Hai
      - age from 38.26, age to 48.26, start 2034-11-14, end 2044-11-14, label 庚 Geng 子 Zi
      - age from 48.26, age to 58.26, start 2044-11-14, end 2054-11-14, label 辛 Xin 丑 Chou
      - age from 58.26, age to 68.26, start 2054-11-14, end 2064-11-14, label 壬 Ren 寅 Yin
      - age from 68.26, age to 78.26, start 2064-11-14, end 2074-11-14, label 癸 Gui 卯 Mao
      - age from 78.26, age to 88.26, start 2074-11-14, end 2084-11-14, label 甲 Jia 辰 Chen
    - **reverse**:
      - age from 8.26, age to 18.26, start 2004-11-14, end 2014-11-15, label 乙 Yi 未 Wei
      - age from 18.26, age to 28.26, start 2014-11-15, end 2024-11-14, label 甲 Jia 午 Wu
      - age from 28.26, age to 38.26, start 2024-11-14, end 2034-11-14, label 癸 Gui 巳 Si
      - age from 38.26, age to 48.26, start 2034-11-14, end 2044-11-14, label 壬 Ren 辰 Chen
      - age from 48.26, age to 58.26, start 2044-11-14, end 2054-11-14, label 辛 Xin 卯 Mao
      - age from 58.26, age to 68.26, start 2054-11-14, end 2064-11-14, label 庚 Geng 寅 Yin
      - age from 68.26, age to 78.26, start 2064-11-14, end 2074-11-14, label 己 Ji 丑 Chou
      - age from 78.26, age to 88.26, start 2074-11-14, end 2084-11-14, label 戊 Wu 子 Zi

**Reading**

Day master (the subject of the chart): 壬 Ren, yang Water. The Ziping hierarchy judges everything else relative to this stem.

Month command, the first judgment: the day master stands in state xiang 相 (assisting) for this month's season, with a root in the month branch; rooted also in year. Assessment: supported: the day master is in seasonal command and rooted in the month branch itself.

Visible stems relative to the day master - year: 偏財 Indirect Wealth, month: 偏財 Indirect Wealth, hour: 劫財 Rob Wealth.

Absent element(s) among visible stems and branch main qi: Earth. In Ziping terms the related Ten-God relations lack visible carriers; hidden-stem presence, if any, is listed in the calculation block and carries less force.

---

## Tibetan year character

*Evidence: configured method*

Year character derived from the sexagenary cycle encoded in the validated BaZi kernel, with Tibetan naming; rabjung position counted from 1027 CE.

**Disclosures**

- **Source — Cycle basis.** Tibetan and Chinese share one sexagenary cycle. The element/animal series here is verified at two independent anchors: 1027 CE = Female Fire Rabbit (first rabjung) and 1984 CE = Male Wood Mouse (Jia-Zi).
- **Configured — Year boundary.** The Tibetan year begins at Losar, whose date requires the full Phugpa month calculation. The BaZi Li Chun pillar year is used as a proxy; Losar typically falls weeks later, so a birth between the two boundaries may be assigned the previous year's character. *Alternatives: Phugpa Losar calculation, Civil year.*
- **Refused — Mewa and parkha.** Not computed. Their cycle anchors are not fixed by any source in the registry, and parkha is conventionally sex-dependent while sex is not part of the birth input contract. A plausible-looking value here would be indistinguishable from a wrong one.
- **Refused — Obstacle years, la, and compatibility.** Kag (obstacle-year) arithmetic, life-force calculations, and compatibility judgments depend on conventions the research pack has not fixed and are not asserted.
- **Refused — Calendar date.** The Phugpa pack can compute the Tibetan month and lunar day, but its own publication contract requires almanac conformance testing before dates are presented. This section therefore reports the year character only.

**Calculation**

- **pillar year used**: 1996
- **year character**: Male Fire Mouse
- **element**: Fire
- **animal**: Mouse
- **polarity**: male
- **sexagenary index**: 12
- **rabjung**:
  - **cycle number**: 17
  - **year in cycle**: 10

---

## Maya calendar

*Evidence: validated research pack*

Long Count, Tzolk'in, and Haab arithmetic from the validated Maya calendar kernel, emitted under both registered correlations.

**Disclosures**

- **Source — Kernel provenance.** Cycle weights, radices, and position formulae come from the validated maya_calendar_kernel pack; day-name and month-name profiles are the Smithsonian 2012 Yucatec spellings the pack registers.
- **Fork — Correlation constant.** The pack registers GMT 584283 as a bounded research default and GMT 584285 as an alternate sensitivity profile. Both are computed below; they shift every Maya date by two days. *Alternatives: GMT 584285.*
- **Configured — Lords of the Night.** The nine-fold G-series is not encoded in the validated pack. It is computed here as G = (total_day mod 9) + 1 with G9 at total_day 8, the standard modern convention, and labeled configured rather than validated.
- **Refused — Day meanings.** Tzolk'in day-sign meanings are not asserted. The pack carries calendar arithmetic only; codical almanacs and living K'iche' daykeeping practice are separate source-limited modules.
- **Configured — Day boundary.** The integer JDN of the civil date is used. The pack's own semantics compare integer date identities and do not infer a birth-time instant, so the birth clock time does not affect this section.

**Calculation**

- **correlation profiles**:
  - **gmt 584283**:
    - **correlation constant**: 584283
    - **status**: bounded_research_default
    - **integer jdn**: 2450309
    - **total day**: 1866026
    - **long count**: 12.19.3.7.6
    - **tzolkin**: 10 Kimi
    - **haab**: 9 Yaxk'in
    - **lord of night**: G4
    - **civil calendar**: proleptic_gregorian
  - **gmt 584285**:
    - **correlation constant**: 584285
    - **status**: alternate_sensitivity_profile_not_default
    - **integer jdn**: 2450309
    - **total day**: 1866024
    - **long count**: 12.19.3.7.4
    - **tzolkin**: 8 K'an
    - **haab**: 7 Yaxk'in
    - **lord of night**: G2
    - **civil calendar**: proleptic_gregorian
- **calendar round days**: 18980

---

## Nahua tonalpohualli

*Evidence: validated research pack*

13-by-20 cycle arithmetic from the validated tonalpohualli kernel. No historical civil-date correlation is available.

**Disclosures**

- **Refused — Civil-date correlation.** The validated pack registers NO approved correlation between the tonalpohualli and the civil calendar, and explicitly forbids reusing a Maya correlation merely because both traditions run 260-day counts. The cycle position below is therefore computed under a labeled non-historical fixture and must not be read as this person's day sign.
- **Source — Kernel provenance.** Day-sign order and the 260-position recurrence come from the validated nahua_tonalpohualli_cycle_v1 pack, anchored to Florentine Codex Book 4 folio 1r and the INAH-hosted trecena table.
- **Source — Reading corpus.** Quotations below come from Florentine Codex Book 4 via hash-pinned witness files fetched from the Getty backend, quoted in the public-domain Nahuatl with an independent English rendering graded engine_translation_unreviewed. Folio and text-record identifiers accompany every quotation.

**Calculation**

- **correlation status**: unresolved_no_approved_epoch
- **fixture anchor jdn**: 2451545
- **fixture anchor note**: Non-historical test fixture. Any day-sign claim derived from it is arithmetic demonstration only.
- **fixture cycle position**:
  - **coefficient**: 13
  - **day sign id**: coatl
  - **day sign label**: Coatl
  - **canonical cycle index**: 64
- **cycle dimensions**:
  - **coefficients**: 13
  - **day signs**: 20
  - **joint period days**: 260
- **augury pack**:
  - **pack id**: nahua_book4_augury_v1
  - **statements**: 4
  - **scope**: Pilot: Chapter 1 (Ce Cipactli) only, from pinned folios 1r-2r. The pack quotes the corpus; it never assigns a day sign to a birth, because no civil-date correlation is approved.

**Reading**

What the corpus itself teaches (Ce Cipactli chapter, quoted as demonstration - not assigned to your birth):

Folio 1r, chapter heading: “First chapter, which tells of the first sign, named One Cipactli, and of the good day-fortune that those born then merited, men and women alike: yet these same people could destroy it, could forfeit it by their own act, because of their laziness.” [Nahuatl: Injc ce capitulo, itechpa tlatoa, injc centetl machiotl: in jtoca ce cipactli, i…]

Folio 2r, the forfeiture clause: “And they also said: even though he was born on a good day sign, if he does not do penance well, if he does not take counsel with himself, if he does not accept and apply to himself the cold water and the nettle - the admonitions, the instruction, the words of the old men and the old women - if he merely turns corrupt, becomes wicked, follows no road at all: nothing comes of it; he destroys it entirely by his own doing.”

The doctrine: a day sign grants a potential that conduct completes or destroys. It is the structural opposite of a personality trait - which is why this section quotes the corpus and refuses the trait table.

---

## Mesopotamian (Babylonian omen corpus)

*Evidence: configured method*

Encoded Enuma Anu Enlil and SAA 8 omen protases matched against a reconstructed sky. The rules are hash-pinned research packs; the calendar projection and the matching orb are product choices and are disclosed as such.

**Disclosures**

- **Refused — Genre boundary.** The Mesopotamian corpus contains no personality genre. Enuma Anu Enlil and the Neo-Assyrian reports judge kings, lands, armies and harvests; no protasis in them takes a birth as input and no apodosis in them describes a person's character, temperament, or disposition. This section is therefore not a personality reading and cannot be turned into one - any Babylonian character delineation is an invention, however ancient the vocabulary it borrows.
- **Refused — Birth-input eligibility.** All 72 encoded omen protases are marked `birth_input_eligible: false` by their own packs, and the twelve the packs additionally mark non-executable are excluded from matching outright. A match therefore means only that the sky on this date satisfied an ancient protasis whose apodosis was addressed to a land or a king. It never means the omen applies to the native.
- **Refused — Prediction.** Apodoses are quoted as historical text about ancient states. Nothing here is a forecast of political, ecological, financial, medical, or personal events, and the packs' own publication limits (suppressing violence, death, disaster, and ritual as present-day prediction) are carried through with each quotation.
- **Refused — Natal synthesis.** The 21 explicit judgment clauses encoded from Rochberg's Texts 1-28 carry no resolved trigger: every one is marked `executable_from_birth_input: false` or `algorithmic_trigger: null`. They are listed as artifacts of specific tablets and are never applied to this or any other chart, and no judgment is built by analogy from the state omens.
- **Refused — Witness blending.** The EAE 20 pack preserves recension conflicts between IM 124485, VAT 9419, and manuscripts D, S, M, Y. Conflicting witnesses are reported separately with their `conflicts_with` links intact; they are never averaged into a single reading.
- **Refused — Commentary layer.** Ancient commentary restricts scope, equates words, and preserves alternatives. Commentary rules are keyed to a base omen rather than to a sky, so they are never matched independently and never overwrite the base omen text.
- **Refused — Unresolved tablets.** 2 of 32 numbered tablets are not exactly matched to a current CDLI record. No claim in this section rests on them, and their unresolved status is stated rather than smoothed over.
- **Source — Rule provenance.** 72 encoded omen protases are loaded from four hash-pinned witness packs - the EAE 20 witness comparison (Al-Rawi and George 2006 with Heessel 2021), the EAE 16-21 ancient commentaries (CCP/ORACC), and SAA 8 reports 316 and 535 (Hunger 1992 via ORACC) - plus 21 judgment clauses from Rochberg's Babylonian Horoscopes. Apodoses are quoted as the packs encode them: normalized clause identifiers with their edition citation, not prose lifted from a modern copyrighted translation, so a specialist can check each identifier against the cited location.
- **Configured — Zodiac.** Positions are the shipping engine's tropical Swiss Ephemeris longitudes. Babylonian sidereal schemes differ: System A and System B norms are anchored to fixed stars, and at a modern date the offset is close to a full sign, so a sign named here will frequently not be the sign a Babylonian scribe would have written. *Alternatives: Babylonian System A norm, Babylonian System B norm, a sidereal ayanamsa.*
- **Configured — Babylonian calendar projection.** The lunisolar calendar is run roughly two thousand years past its attested use, so the month and day below are a modern projection and not a historical date. Nisannu is taken as the first month whose day 1 begins on or after the vernal equinox; day 1 begins at the first sunset after conjunction at which the Moon sets at least 48 minutes after the Sun; days run sunset to sunset at the place of birth; a thirteenth month is labeled intercalary. *Alternatives: the Seleucid 19-year intercalation cycle projected forward, Schoch or Yallop arcus-visionis visibility criteria, sunset reckoned at Babylon rather than at the birthplace, the schematic 30-day month of the astrolabe texts.*
- **Configured — Omen matching orb.** The matching orb is zero on every axis and is stated rather than defaulted. An eclipse protasis is satisfied only if an umbral lunar eclipse is in progress at the birth instant - proximity in days never counts. Month and day selectors must match the projected date exactly, with no plus-or-minus-one-day widening even though the projected day boundary is itself uncertain. Watch selectors require a night birth. A protasis naming any condition the reconstruction cannot supply is counted unevaluable and never partially matched. *Alternatives: plus or minus one day on the projected calendar day, treating any eclipse in the same lunar month as satisfying the eclipse condition, scoring partial protasis satisfaction.*
- **Configured — Night watches.** The three watches are computed as equal thirds of the interval from sunset to sunrise at the place of birth. The corpus itself uses watch names without defining their boundaries arithmetically. *Alternatives: seasonal-hour watches, the schematic watch scheme of MUL.APIN.*
- **Source — Position reporting.** Bodies are listed in the order Rochberg's edition tabulates a horoscope - Moon, Sun, Jupiter, Venus, Mercury, Saturn, Mars - as sign and degree only. The corpus records no houses, no aspects, no rulerships, and no sect, and none is supplied here. The packs encode no Babylonian sign-name table either, so signs carry their standard modern names.

**Calculation**

- **corpus shape**:
  - **encoded omen protases**: 72
  - **omen packs**: 4
  - **rochberg numbered texts**: 32
  - **horoscope record entries**: 31
  - **explicit judgment clauses**: 21
  - **judgment clauses executable from a birth**: 0
  - **genre**: state divination; no natal personality genre survives
- **positions in edition order**:
  - body Moon, sign Leo, degree in sign 13.2464, zodiac tropical
  - body Sun, sign Leo, degree in sign 21.0966, zodiac tropical
  - body Jupiter, sign Capricorn, degree in sign 8.5084, zodiac tropical
  - body Venus, sign Cancer, degree in sign 5.5396, zodiac tropical
  - body Mercury, sign Virgo, degree in sign 17.1826, zodiac tropical
  - body Saturn, sign Aries, degree in sign 6.8529, zodiac tropical
  - body Mars, sign Cancer, degree in sign 12.5197, zodiac tropical
- **not recorded by this corpus**: houses, aspects, rulerships, sect, personality delineation
- **babylonian date projection**:
  - **status**: modern_projection_not_a_historical_date
  - **month index**: 5
  - **month**: abu
  - **month label**: Abu
  - **intercalary**: False
  - **day**: 27
  - **day one evening ut**: 1996-07-18T03:29 UT
  - **year began ut**: 1996-03-21T02:20 UT
  - **vernal equinox ut**: 1996-03-20T08:03 UT
- **lunar condition**:
  - **elongation from sun degrees**: 352.1498
  - **phase**: conjunction, moon invisible
  - **synodic age days**: 28.9188
  - **previous conjunction ut**: 1996-07-15T16:14 UT
- **night watch**:
  - **is night**: False
  - **watch**: None
  - **status**: daylight_birth
- **eclipse condition**:
  - **lunar eclipse in progress**: False
  - **umbral magnitude at birth**: 0.0
  - **penumbral magnitude at birth**: 0.0
  - **previous lunar eclipse**:
    - **maximum ut**: 1996-04-04T00:09 UT
    - **type**: total
    - **days from birth**: -131.589
  - **next lunar eclipse**:
    - **maximum ut**: 1996-09-27T02:54 UT
    - **type**: total
    - **days from birth**: 44.525
  - **next solar eclipse**:
    - **maximum ut**: 1996-10-12T14:01 UT
    - **type**: partial
    - **days from birth**: 59.989
- **omen matching**:
  - **rules evaluated**: 72
  - **matched**: 
  - **matched count**: 0
  - **non executable by pack**: 12
  - **not matched count**: 19
  - **unevaluable count**: 41
  - **unevaluable reasons**:
    - **eclipse-shape, quadrant, or phase-progress observation no modern reconstruction can supply**: 25
    - **fixed-star relation not reduced to a computable rule**: 1
    - **planet-in-Moon observation, not a longitude test**: 1
    - **commentary layer, keyed to a base omen rather than a sky**: 10
    - **commentary layer, keyed to a manuscript variant**: 1
    - **interpretive framework, not a protasis**: 1
    - **identifies an ancient record, not a sky condition**: 2
  - **calendar selector overlap**: 
  - **calendar selector overlap note**: Not matches. These protases name the projected month or day, but the lunar eclipse every one of them presupposes did not occur.
  - **configured orb**: zero: umbral eclipse in progress at the birth instant; exact month and day equality on the projected calendar; watch only for a night birth
  - **sky facts supplied**:
    - **phenomenon**: none
    - **babylonian month**: abu
    - **babylonian day**: 27
    - **watch**: None
    - **sets while eclipsed**: False
  - **no match reason**: no umbral lunar eclipse was in progress at the birth instant, and every encoded protasis in these packs presupposes one
- **horoscope judgment clauses**:
  - **encoded clause count**: 21
  - **executable from birth input**: 0
  - **with resolved trigger**: 0
  - **clauses**:
    - rule id babylonian.rochberg1998.text2.rev1.propitious_clause, text Text 2 (AB 251), clauses ['propitious_outcome'], attribution Babylonian Horoscopes, Text 2 (AB 251), pp. 56-57, rev. 1 and reverse commentary [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade C, customer prediction False, pack late_babylonian_horoscope_judgment_clauses_rochberg_1998
    - rule id babylonian.rochberg1998.text5.rev2.initial_property_lack_clause, text Text 5 (MLC 1870), clauses ['initial_property_lack'], attribution Babylonian Horoscopes, Text 5 (MLC 1870), p. 67, rev. 2; damaged possible house material pp. 66-67 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade C, customer prediction False, pack late_babylonian_horoscope_judgment_clauses_rochberg_1998
    - rule id babylonian.rochberg1998.text5.rev4.food_insufficiency_clause, text Text 5 (MLC 1870), clauses ['food_insufficiency_or_hunger'], attribution Babylonian Horoscopes, Text 5 (MLC 1870), p. 67, rev. 4; damaged possible house material pp. 66-67 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade D, customer prediction False, pack late_babylonian_horoscope_judgment_clauses_rochberg_1998
    - rule id babylonian.rochberg1998.text5.rev5.youth_property_does_not_last_clause, text Text 5 (MLC 1870), clauses ['property_acquired_in_youth_does_not_last'], attribution Babylonian Horoscopes, Text 5 (MLC 1870), p. 67, rev. 5; damaged possible house material pp. 66-67 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade C, customer prediction False, pack late_babylonian_horoscope_judgment_clauses_rochberg_1998
    - rule id babylonian.rochberg1998.text5.rev6.year36_property_clause, text Text 5 (MLC 1870), clauses ['property_in_year_or_age_36'], attribution Babylonian Horoscopes, Text 5 (MLC 1870), p. 67, rev. 6 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade B, customer prediction False, pack late_babylonian_horoscope_judgment_clauses_rochberg_1998
    - rule id babylonian.rochberg1998.text5.rev7.long_life_clause, text Text 5 (MLC 1870), clauses ['long_life'], attribution Babylonian Horoscopes, Text 5 (MLC 1870), p. 67, rev. 7 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade B, customer prediction False, pack late_babylonian_horoscope_judgment_clauses_rochberg_1998
    - rule id babylonian.rochberg1998.text5.rev8-9.wife_social_conflict_clause, text Text 5 (MLC 1870), clauses ['wife_and_social_conflict_or_coercion'], attribution Babylonian Horoscopes, Text 5 (MLC 1870), p. 67, rev. 8-9 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade D, customer prediction False, pack late_babylonian_horoscope_judgment_clauses_rochberg_1998
    - rule id babylonian.rochberg1998.text5.rev10.profit_clause, text Text 5 (MLC 1870), clauses ['profit'], attribution Babylonian Horoscopes, Text 5 (MLC 1870), p. 67, rev. 10 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade C, customer prediction False, pack late_babylonian_horoscope_judgment_clauses_rochberg_1998
    - rule id babylonian.rochberg1998.text5.rev11-12.property_travel_clause, text Text 5 (MLC 1870), clauses ['travel_concerning_property'], attribution Babylonian Horoscopes, Text 5 (MLC 1870), p. 67, rev. 11-12 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade D, customer prediction False, pack late_babylonian_horoscope_judgment_clauses_rochberg_1998
    - rule id babylonian.rochberg1998.text9.obv4.moon_aquarius_long_life_clause, text Text 9 (NCBT 1231), clauses ['long_life'], attribution Babylonian Horoscopes, Text 9 (NCBT 1231), pp. 79-80, obv. 4; astronomical table p. 81 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade B, customer prediction False, pack late_babylonian_horoscope_judgment_clauses_rochberg_1998
    - rule id babylonian.rochberg1998.text9.obv5.jupiter_prince_help_clause, text Text 9 (NCBT 1231), clauses ['someone_will_help_the_prince'], attribution Babylonian Horoscopes, Text 9 (NCBT 1231), pp. 79-80, obv. 5 and critical apparatus; astronomical table p. 81 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade C, customer prediction False, pack late_babylonian_horoscope_judgment_clauses_rochberg_1998
    - rule id babylonian.rochberg1998.text9.obv6.venus_sons_clause, text Text 9 (NCBT 1231), clauses ['male_offspring'], attribution Babylonian Horoscopes, Text 9 (NCBT 1231), pp. 79-80, obv. 6 and critical apparatus; astronomical table p. 81 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade D, customer prediction False, pack late_babylonian_horoscope_judgment_clauses_rochberg_1998
    - rule id babylonian.rochberg1998.text16b.obv10.good_fortune_clause, text Text 16b (W 20030/10 obverse), clauses ['good_fortune_or_propitious_days'], attribution Babylonian Horoscopes, Text 16b (W 20030/10 obverse), p. 101, obv. 10; commentary pp. 101-104 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade C, customer prediction False, pack late_babylonian_horoscope_text16_rochberg_1998
    - rule id babylonian.rochberg1998.text16a.rev5.venus_first_visibility_favorable_qualifier, text Text 16a (W 20030/10 reverse), clauses ['favorable_question_mark'], attribution Babylonian Horoscopes, Text 16a (W 20030/10 reverse), p. 101, rev. 5; apparatus and commentary pp. 101-104 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade D, customer prediction False, pack late_babylonian_horoscope_text16_rochberg_1998
    - rule id babylonian.rochberg1998.text16a.rev9.moon_progress_favorable_fragment, text Text 16a (W 20030/10 reverse), clauses ['favorable'], attribution Babylonian Horoscopes, Text 16a (W 20030/10 reverse), p. 101, rev. 9; commentary pp. 103-104 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade D, customer prediction False, pack late_babylonian_horoscope_text16_rochberg_1998
    - rule id babylonian.rochberg1998.text27.upper_edge1.good_fortune_fragment, text Text 27 (BM 38104), clauses ['good_fortune'], attribution Babylonian Horoscopes, Text 27 (BM 38104), p. 139, upper edge line 1 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade C, customer prediction False, pack late_babylonian_horoscope_text27_rochberg_1998
    - rule id babylonian.rochberg1998.text27.upper_edge2.good_fortune_diminishes, text Text 27 (BM 38104), clauses ['good_fortune_will_diminish'], attribution Babylonian Horoscopes, Text 27 (BM 38104), p. 139, upper edge line 2 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade C, customer prediction False, pack late_babylonian_horoscope_text27_rochberg_1998
    - rule id babylonian.rochberg1998.text10.obv4-6.moon_positive_latitude_omen, text Text 10 (MLC 2190), clauses ['prosperity', 'greatness'], attribution Babylonian Horoscopes, Text 10 (MLC 2190), pp. 83-84, obv. 4-6; commentary p. 84 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade B, customer prediction False, pack late_babylonian_horoscope_text10_rochberg_1998
    - rule id babylonian.rochberg1998.text10.obv7-8.jupiter_ki_place_judgment, text Text 10 (MLC 2190), clauses ['prosperity', 'peace_or_reconciliation_translation_uncertain', 'durable_wealth', 'long_life'], attribution Babylonian Horoscopes, Text 10 (MLC 2190), p. 84, obv. 7-8; KI and reading commentary p. 85 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade B, customer prediction False, pack late_babylonian_horoscope_text10_rochberg_1998
    - rule id babylonian.rochberg1998.text10.obv8-10.venus_ki_place_judgment, text Text 10 (MLC 2190), clauses ['favor_wherever_the_native_goes', 'male_and_female_offspring'], attribution Babylonian Horoscopes, Text 10 (MLC 2190), p. 84, obv. 8-10; KI commentary p. 85 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade B, customer prediction False, pack late_babylonian_horoscope_text10_rochberg_1998
    - rule id babylonian.rochberg1998.text10.rev1-3.mercury_ki_place_judgment, text Text 10 (MLC 2190), clauses ['bravery', 'first_in_rank', 'greater_importance_than_brothers', 'succession_to_fathers_house'], attribution Babylonian Horoscopes, Text 10 (MLC 2190), with duplicate Text 11 (W 20030/143), p. 84, rev. 1-3; critical apparatus p. 83 and duplicate pp. 86-87 [babylonian_rochberg_horoscopes_1998_awdl], algorithmic trigger None, executable from birth input False, evidence grade B, customer prediction False, pack late_babylonian_horoscope_text10_rochberg_1998

**Reading**

What this corpus is. Enuma Anu Enlil and the Neo-Assyrian celestial reports are state divination: 72 encoded protasis/apodosis pairs judging kings, lands, armies and harvests. The natal branch is thin, late and laconic - Rochberg's 32 numbered texts yield 31 horoscope records that are mostly positional, and only 21 explicit judgment clauses in all. The oldest documented tradition in this panel is also the one with the least to say about an individual life.

Positions, in the corpus's own idiom. A Late Babylonian horoscope records body, zodiacal sign and degree, in the order the edition tabulates them, and nothing else - no houses, no aspects, no rulerships, no sect: Moon in Leo 13.25°; Sun in Leo 21.10°; Jupiter in Capricorn 8.51°; Venus in Cancer 5.54°; Mercury in Virgo 17.18°; Saturn in Aries 6.85°; Mars in Cancer 12.52° (tropical longitudes; a Babylonian sidereal norm would shift these by close to a sign).

Calendar and lunar condition. Projected Babylonian date: Abu 27 - month 5 of the year that began 1996-03-21T02:20 UT, a modern projection and not a historical date. The Moon stood 352.1° east of the Sun and 28.9 days past conjunction - conjunction, moon invisible.

Eclipse condition. No umbral lunar eclipse was in progress at the birth instant. The nearest was 44.5 days away, on 1996-09-27T02:54 UT (total).

Omen protases matched: none. All 72 encoded protases were evaluated at the disclosed zero orb; 12 are marked non-executable by their own packs, and 41 cannot be evaluated from a modern ephemeris at all (eclipse-shape, quadrant, or phase-progress observation no modern reconstruction can supply (25), commentary layer, keyed to a base omen rather than a sky (10), identifies an ancient record, not a sky condition (2)). For the remainder, no umbral lunar eclipse was in progress at the birth instant, and every encoded protasis in these packs presupposes one.

The natal branch, quoted as artifact. 21 explicit judgment clauses survive across Texts 1-28, and 0 of them can be executed from a birth: every one is recorded with an unresolved trigger, so none reduces to a rule another chart could satisfy. Text 2 (AB 251), for instance, attaches “propitious_outcome” to its own ancient native (Babylonian Horoscopes, Text 2 (AB 251), pp. 56-57, rev. 1 and reverse commentary [babylonian_rochberg_horoscopes_1998_awdl]) - a record of what one tablet says, not a rule that travels.

Where this stops. The corpus records positions, a date, a lunar and eclipse condition, and the omens a sky satisfies. It contains no protasis that takes a birth as input and no apodosis about anyone's character, temperament, or disposition, so this section reports those four things and stops. Nothing above is a prediction, and nothing above can be turned into a personality reading without inventing a genre the sources do not contain.

---

## Pharaonic Egyptian civil calendar

*Evidence: validated research pack*

The 365-day civil-year structure and its position arithmetic from the validated Egyptian civil calendar pack. The pack registers no chronology profile, so this birth is not placed in the calendar.

**Disclosures**

- **Source — Pack provenance.** Year length, the three seasons of four thirty-day months, the five heriu-renpet days, the non-intercalating model and the position/date bijection come from egyptian_civil_calendar_365_v1, anchored to Porceddu et al. 2008 and the UCL civil-calendar table.
- **Refused — Placing this birth in the Egyptian year.** Refused. The pack's chronology contract sets default_profile to null: it requires a named profile carrying regime, authority, anchor civil date, anchor Egyptian date, calendar policy, locality, day boundary and uncertainty in days, and there is no approved profile for any regime. The 365-day year drifts a full day against the seasons every four years, so an unanchored conversion is not approximately right - it is wrong by an unbounded amount. The birth's civil day (JDN 2450309) is therefore reported as the withheld input, not converted.
- **Refused — Back-projected calendars.** The later Alexandrian/Coptic leap rule, a modern fixed month-and-day table, and any unnamed reign or locality are all rejected by the pack as chronology profiles. A profile whose model_id is not pharaonic_civil_365 fails closed rather than being coerced.
- **Refused — Hemerology and any birth reading.** Refused. The pack's output contract permits calendar position fields only and names prognosis, personality, fate, health, death, morality, compatibility and recommendation as forbidden fields. A calendar position is not a witness-specific judgment, and no lucky/unlucky verdict is produced here even where a date is otherwise well formed.
- **Refused — Sallier IV and the epagomenal days.** Refused, and for a reason worth stating precisely. The Sallier IV access manifest records rule_extraction_ready: false - the file is acquired but not fully read, with no complete transcription, no translation and no collation against Bakir 1966 or Leitz 1994. Budge further states that the portion probably containing the Five Epagomenal Days is LOST. Loss is unknown evidence, not proof that the original calendar assigned those days no prognosis, so this section neither supplies a prognosis nor asserts that none existed.
- **Configured — Date notation.** Dates are written in the Egyptological convention used by the pack's own source - Roman month number within the season, then season, then day, as in 'I Akhet 1'. The season names are the pack's source labels. *Alternatives: Greek month names (Thoth, Phaophi, ...), Plain 1-12 month numbering.*

**Calculation**

- **calendar model**:
  - **model id**: pharaonic_civil_365
  - **year length days**: 365
  - **ordinary months**: 12
  - **ordinary month length days**: 30
  - **ordinary days**: 360
  - **additional days**: 5
  - **intercalation**: False
  - **seasons**: Akhet (4 months), Peret (4 months), Shemu (4 months)
  - **additional period**: heriu-renpet
- **birth placement**:
  - **placed**: False
  - **chronology profile used**: None
  - **withheld input jdn**: 2450309
  - **withheld input civil date**: 1996-08-13
  - **reason**: no_approved_chronology_profile
- **chronology contract**:
  - **default profile**: None
  - **required fields**: profile_id, tradition_id, model_id, anchor_civil_date, calendar_policy, anchor_egyptian_date, historical_regime, authority, uncertainty_days, locality, day_start
  - **unsupported profiles**: Alexandrian or Coptic leap-year rules projected backward, A modern fixed month/day table treated as universal pharaonic chronology, An unnamed reign, epoch, locality, calendar policy or day boundary
- **cycle internal structure**:
  - **landmark positions**:
    - **I Akhet 1**: 0
    - **I Akhet 30**: 29
    - **II Akhet 1**: 30
    - **I Peret 1**: 120
    - **I Shemu 1**: 240
    - **IV Shemu 30**: 359
    - **heriu-renpet day 1**: 360
    - **heriu-renpet day 5**: 364
  - **position date round trip over 365 positions**: True
- **fail closed selfcheck**:
  - **note**: Contract reproduction from the pack's own vectors. None of these concerns this birth.
  - **no profile supplied**: missing_profile
  - **coptic model supplied**: wrong_calendar_model
  - **synthetic fixture profile**:
    - **profile id**: test_fixture_not_historical
    - **historical regime**: synthetic_test_only
    - **result**: heriu-renpet day 5
    - **year position**: 364
    - **not this birth**: True
- **hemerology boundary**:
  - **heriu renpet prognosis**: no prognosis survives in the currently inspected main-calendar data; Sallier IV's likely epagomenal portion is lost, so historical absence is not proven
  - **missing witness text creates negative rule**: False
  - **calendar position creates birth reading**: False
- **sallier iv witness**:
  - **witness id**: papyrus_sallier_iv_ea10184
  - **traditional name**: Sallier IV
  - **british museum number**: 10184
  - **surviving range**: I Akhet 18 through I Shemu 12
  - **lost ranges**: I Akhet 1-17 (Thoth 1-17), I Shemu 11 through IV Shemu 30 (Pachons 11 through Mesore 30), the portion probably containing the Five Epagomenal Days
  - **epagomenal status**: not_preserved_in_this_witness
  - **historical absence proven**: False
  - **rule extraction ready**: False
  - **complete translation present**: False
  - **modern critical edition collated**: False

**Reading**

What this tradition's surviving apparatus can and cannot do with a birth date, stated in its own terms:

The civil year is a fixed arithmetic object - 12 months of 30 days across Akhet, Peret and Shemu, then 5 heriu-renpet days upon the year, 365 days total, with no intercalation. Positions inside it convert both ways exactly, and that arithmetic is verified over all 365 positions above.

What is missing is the join between that object and a date on a modern calendar. Because the year never intercalates, it slides against the seasons by roughly one day in four years and a full year in about 1460 - so the join is not a detail, it is the whole conversion. The pack registers no approved anchor, and refuses to invent one.

The hemerological layer - the calendars of lucky and unlucky days that would be the closest Egyptian analogue to a birth judgment - is a separate, source-limited problem. Sallier IV survives in two portions with lacunae, has no complete critical transcription in hand, and its likely epagomenal section is lost. This section quotes no prognosis and invents none.

---

## Zi Wei Dou Shu (Purple Star)

*Evidence: transcription grade*

Grade-D construction candidates transcribed from Ziwei Doushu Quanshu juan 2 on Chinese Wikisource, base facsimile unidentified. Only the hour-keyed Wenchang/Wenqu placement has all of its inputs; the chart proper does not, and is refused.

**Disclosures**

- **Source — Pack provenance and grade.** All seven rules come from ziwei_quanshu_juan2_wikisource_candidate_v1, transcribed from Chinese Wikisource juan 2. The page identifies no base scan, collation history or relation to the Quanji or Jielan printings, so every rule carries evidence grade D and review status 'facsimile collation and Chinese review pending'. This is a transcription, not a controlling edition.
- **Refused — The chart itself.** Refused - and not for want of effort. Life and body palace placement begins from the LUNAR birth month; the pack registers no approved civil-to-lunisolar conversion, and its source audit forbids a ziwei_default configuration, requiring instead a declared calendar version, leap-month convention and day boundary. Without the chart month there is no life palace; without the life palace there are no twelve topic palaces; and Zuofu/Youbi are keyed to the month as well. The Vietnamese lunisolar kernel elsewhere in this panel is NOT a substitute: it is a modern Vietnamese profile referenced to 105 degrees east, and both audits forbid relabeling one tradition's calendar as another's.
- **Refused — Five Tigers and the Four Transformations.** Refused. The pack's own validation vector for the Five Tigers table sets implementation_allowed_before_facsimile_collation to false, so the table is not encoded here at all. The Four Transformations need the birth-year stem on the Zi Wei year boundary, which this pack does not fix, and the transcription's table is explicitly in conflict with later-school tables; keying it to this birth would assert a lineage the sources have not yet settled.
- **Refused — Star meanings and any reading.** Refused. Every rule in the pack carries a publication limit forbidding prose meaning before construction reproduces facsimile-backed worked charts, and the source audit warns that a list of isolated star keywords is not a reading. The placement below is a position, not a judgment.
- **Refused — The Daoist-canon homonym.** A different three-juan work in the Zhengtong Daozang shares the title Ziwei Doushu but differs in star names and construction. It is never used to fill a gap in this system, including the gaps named above.
- **Configured — Double-hour partition and boundary.** The twelve shichen are taken from the validated BaZi sexagenary kernel (Zi opening at 23:00), because the Zi Wei pack states its own double-hour boundary must be established from golden examples and declines to default it. Two of the twelve double-hours - Zi and Chou - have golden vectors in this pack; the other ten rest on the stated counting rule alone. *Alternatives: Zi centred on midnight (23:00-01:00 split across days), A printed almanac's shichen table.*
- **Fork — Double-hour basis.** True solar time (06:05:05) and clock time (07:18:00) fall in different shichen, so Wenchang and Wenqu land on different branches under each. Both are shown; neither is asserted, because the pack fixes no boundary. *Alternatives: Clock time, Local mean time.*

**Calculation**

- **source profile**:
  - **source pack id**: ziwei_quanshu_juan2_wikisource_candidate_v1
  - **source edition id**: ziwei_doushu_quanshu_juan2_wikisource
  - **implementation status**: not_implemented
  - **publication status**: research_only
  - **evidence grade of every rule**: D
  - **review status**: facsimile_collation_and_chinese_review_pending
- **chart construction**:
  - **status**: blocked_no_lunisolar_profile
  - **blocking input**: chart lunar month (regular or intercalary)
  - **blocked operations**: life palace placement, body palace placement, twelve topic palace assignment, Zuofu / Youbi placement (month-keyed), five-phase bureau and main-star sequences, Four Transformations by birth-year stem, Five Tigers palace-stem sequence, decade and annual limits
- **hour keyed placements**:
  - **true solar time**:
    - **time**: 06:05:05
    - **double hour branch**: mao
    - **double hour label**: 卯
    - **wenchang branch**: wei
    - **wenqu branch**: wei
  - **clock time**:
    - **time**: 07:18:00
    - **double hour branch**: chen
    - **double hour label**: 辰
    - **wenchang branch**: wu
    - **wenqu branch**: shen
  - **local mean time**:
    - **time**: 06:09:50
    - **double hour branch**: mao
    - **double hour label**: 卯
    - **wenchang branch**: wei
    - **wenqu branch**: wei
- **twelve topic palace order**: life, siblings, wife_and_concubines_historical_label, children, wealth, illness, travel, servants_historical_label, office_and_career, property, fortune_and_virtue, parents
- **vector selfcheck**:
  - **note**: Reproduction of the pack's own transcription vectors, to show the arithmetic matches the source examples. Not this birth's chart.
  - **ziwei.quanshu.wenchang wenqu.zi**:
    - **input double hour**: zi
    - **wenchang**: xu
    - **wenqu**: chen
    - **matches source example**: True
  - **ziwei.quanshu.wenchang wenqu.chou**:
    - **input double hour**: chou
    - **wenchang**: you
    - **wenqu**: si
    - **matches source example**: True
  - **ziwei.quanshu.topic palaces.reverse from zi**:
    - **input life palace**: zi
    - **matches source example**: True
    - **hypothetical only**: True
  - **five tigers table**: not_implemented_by_pack_instruction

---

## Vietnamese lunisolar calendar

*Evidence: configured method*

Month starts, the month-11 solstice anchor, month numbering and the no-principal-term intercalation rule from the validated modern Vietnamese calendar pack, computed on Vietnam's civil day with a product-supplied ephemeris the pack declines to name.

**Disclosures**

- **Source — Rule provenance and grade.** The five calculation rules come from vietnam_modern_lunisolar_rules_uhm_candidate_v1. The pack's own evidence grade is D: the inspected technical page is explicit and carries worked 1984-1985 tables, but its authorship and statutory authority are not established and independent recomputation, almanac comparison and Vietnamese review remain pending. All five of its published vectors are reproduced below.
- **Configured — Ephemeris and timescale.** New Moon instants are found where apparent geocentric Moon-Sun elongation reaches zero, and principal terms where apparent solar longitude reaches a multiple of 30 degrees, both from the Swiss Ephemeris in UT with civil dates on the proleptic Gregorian calendar. The pack names no ephemeris, timescale or numerical tolerance, so this is the product's choice. *Alternatives: JPL DE440 directly, VSOP87/ELP mean-element tables, Published Vietnamese almanac tables.*
- **Configured — Civil-day basis.** Every event is dated on UTC+7, from the 105-degrees-east reference longitude documented on the inspected page, applied uniformly across all years. The pack warns in terms that a reference longitude is not a substitute for statutory timezone history, and that the valid period and precise role of 105E require Vietnamese authority - so for any year outside the modern statutory profile this is an assumption, not a sourced fact. *Alternatives: Vietnamese statutory zone history, including UTC+8 periods, Beijing UTC+8 basis (rejected by the pack).*
- **Configured — Applying a Vietnamese calendar to a birth outside Vietnam.** The Vietnamese calendar is a civil calendar defined on Vietnam's own day, so the birth instant is converted to Vietnam's civil date rather than the birth place's. Where the two differ, both are shown. This is a projection of a place-specific calendar onto a foreign birth, and is reported as such. *Alternatives: Refuse the section for non-Vietnamese births, Date the events on the birth place's civil day (this would no longer be the Vietnamese calendar).*
- **Configured — Boundary tolerance.** Events falling within 5 minutes of Vietnamese local midnight are flagged, because ephemeris or civil-time uncertainty can push them across the day boundary and move a month label. The pack requires alternates rather than a silent choice in that case; the threshold itself is a product setting. *Alternatives: A tighter threshold tied to a stated ephemeris error budget, No tolerance check at all.*
- **Refused — Historical royal calendars.** Refused. This is the modern calculation profile. The pack states it cannot be applied proleptically to a historical royal calendar without a regime-specific source, and the Vietnamese audit requires a calendar_regime_id and a dated almanac concordance for any historical conversion, because Vietnamese dynastic calendars could and did differ from contemporary Chinese ones. For a birth predating the modern profile the date below is the modern rule run backward, not the calendar that was in force.
- **Refused — Any Vietnamese natal reading.** Refused. This is a calendar fact and nothing more. The surviving corpus cannot support a Vietnamese natal system: Tu Vi and Tu Binh each require their own named editions, construction tables and worked charts, none of which exist here, and the audit forbids relabeling a Chinese BaZi or Zi Wei result as Vietnamese. No sexagenary year name, no star chart and no personality claim is emitted here.

**Calculation**

- **calendar profile**:
  - **school id**: modern_vietnamese_lunisolar_uhm_candidate
  - **reference longitude**: 105E
  - **civil offset hours**: 7.0
  - **ephemeris**: Swiss Ephemeris (swisseph), apparent geocentric, UT
  - **civil calendar**: proleptic Gregorian
  - **implementation status in pack**: not_implemented
- **civil dates**:
  - **birth place civil date**: 1996-08-13
  - **vietnamese civil date**: 1996-08-13
  - **differs from birth place day**: False
  - **utc**: 1996-08-13T14:18:00
- **lunar date**:
  - **month number**: 6
  - **is intercalary**: False
  - **day**: 30
  - **label**: month 6, day 30
  - **month start civil date**: 1996-07-15
  - **month end civil date**: 1996-08-13
  - **month length days**: 30
- **month start new moon**:
  - **utc**: 1996-07-15T16:14:51Z
  - **hanoi civil date**: 1996-07-15
  - **beijing civil date**: 1996-07-16
  - **local day differs from beijing**: True
- **lunar year structure**:
  - **month11 anchor start**: 1995-12-22
  - **next month11 anchor start**: 1996-12-10
  - **month count**: 12
  - **is leap year**: False
  - **anchor solstice utc**: 1995-12-22T08:16:46Z
  - **anchor solstice hanoi date**: 1995-12-22
  - **anchor solstice beijing date**: 1995-12-22
  - **tet in this anchor span**: 1996-02-19
  - **birth precedes that tet**: False
- **intercalation evidence**:
  - **is leap year**: False
  - **months between month11 anchors**: 12
  - **rule**: twelve months between anchors: sequential 11, 12, 1..10
- **boundary trace**:
  - **tolerance minutes**: 5.0
  - **closest event**: the New Moon opening this lunar month
  - **closest margin minutes**: 45.15
  - **within tolerance**: False
  - **all margins minutes**:
    - **the New Moon opening this lunar month**: 45.15
    - **the New Moon opening the next lunar month**: 566.17
    - **the winter solstice anchoring month 11**: 523.23
    - **the winter solstice closing the span**: 174.13
- **worked example selfcheck**:
  - **new moon local day divergence 1984 05 30**:
    - **computed utc**: 1984-05-30T16:47:50Z
    - **computed**:
      - **hanoi civil date**: 1984-05-30
      - **beijing civil date**: 1984-05-31
    - **expected**:
      - **hanoi civil date**: 1984-05-30
      - **beijing civil date**: 1984-05-31
    - **matches**: True
  - **solstice local day divergence 1984 12 21**:
    - **computed utc**: 1984-12-21T16:22:47Z
    - **computed**:
      - **hanoi civil date**: 1984-12-21
      - **beijing civil date**: 1984-12-22
    - **expected**:
      - **hanoi civil date**: 1984-12-21
      - **beijing civil date**: 1984-12-22
    - **matches**: True
  - **month11 1984**:
    - **computed**:
      - **month number**: 11
      - **start civil date**: 1984-11-23
      - **end civil date**: 1984-12-21
    - **expected**:
      - **month number**: 11
      - **start civil date**: 1984-11-23
      - **end civil date**: 1984-12-21
    - **matches**: True
  - **new year divergence 1985**:
    - **computed**:
      - **vietnamese new year**: 1985-01-21
      - **chinese new year**: 1985-02-20
    - **expected**:
      - **vietnamese new year**: 1985-01-21
      - **chinese new year**: 1985-02-20
    - **matches**: True
    - **note**: The Chinese date is the same five rules evaluated on Beijing's civil day, which is how the pack's own vector states the contrast. It is not an authoritative Chinese calendar result.
  - **intercalary month 1985**:
    - **computed**:
      - **is leap year**: True
      - **intercalary month start**: 1985-03-21
      - **intercalary month end**: 1985-04-19
    - **expected**:
      - **is leap year**: True
      - **intercalary month start**: 1985-03-21
      - **intercalary month end**: 1985-04-19
    - **matches**: True
  - **all published vectors reproduced**: True

**Reading**

What this section is: a date, computed under a named set of modern rules, on Vietnam's civil day rather than anyone else's.

The Vietnamese civil day is doing real work here, not decoration. In the pack's own 1984-85 worked case a New Moon lands at 23:47 Hanoi time and a winter solstice at 23:22 - both a few minutes short of midnight - and those minutes are why Tet 1985 fell on 21 January in Vietnam while Chinese New Year fell on 20 February. The engine reproduces both dates above from the rules alone.

What this section is not: a reading. A Vietnamese natal system would need its own named edition and construction tables, which the corpus does not have, and a Chinese chart wearing a Vietnamese label would be worse than nothing.

---

## Across traditions

*Agreement is only meaningful between traditions that share no mathematics. Sections are grouped by calculation basis and a shared-basis group counts as ONE independent voice. Western, Islamicate, and medieval Jewish share one tropical chart; Western and Vedic whole-sign house numbers coincide by construction and are therefore never counted as independent agreement on placement.*

**Independent voices: 6** (from 9 sections sharing a calculation basis, plus any standing alone).

- *hellenistic core* — western_traditional, islamicate_persian, medieval_jewish share one calculation basis and count as a single voice.
- *sexagenary core* — chinese_bazi, tibetan, vietnamese, ziwei_doushu share one calculation basis and count as a single voice.
- *mesoamerican count* — maya, nahua_central_mexican share one calculation basis and count as a single voice.

**Where independent systems agree**

- **Timing systems present** (2 independent voices): Two or more traditions with no shared timing mathematics each supply a period structure for this birth: Vedic: Vimshottari Mercury mahadasha 1996-08-13 to 2010-02-01; BaZi: luck pillars begin at age 8.256, first pillar 丁 Ding 酉 You (2004-11-14)
  - *Caveat: Both systems produce periods, which is not the same as both flagging the same date. Period boundaries are reported separately and are NOT aligned or averaged here.*
- **Traditions that decline to personalize** (4 independent voices): These sections report structure but refuse a personal verdict, each for a source-specific reason stated in its own disclosures: mesopotamian_babylonian, nahua_central_mexican, pharaonic_egyptian, vietnamese, ziwei_doushu
  - *Caveat: Refusals are findings about the surviving corpora, not gaps in this engine.*

**Distinctions that must not be collapsed**

- **Day/night and polarity** — Hellenistic sect is day; the BaZi day master is yang Water. These are NOT equivalent concepts and must not be read as agreeing or disagreeing - sect is a chart-wide condition set by the Sun's position relative to the horizon, while polarity is an intrinsic property of one stem.
  - *Listed to prevent a false equivalence, not as a finding.*

---

## How to read the labels

- **validated research pack** — arithmetic from a fail-closed pack whose standalone validator passes in this repository.
- **live engine** — produced by the shipping Western calculator.
- **configured method** — the product chose a convention the research pack deliberately refuses to default. Alternatives are named inline.
- **Refused** — the tradition, or the surviving sources for it, cannot support the claim. This is a finding, not an omission.
