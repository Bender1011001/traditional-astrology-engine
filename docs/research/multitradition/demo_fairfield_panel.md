# Multi-tradition panel — Andrew

Historical and cultural interpretation of astrological doctrine. Not medical, financial, legal, psychological, or safety advice.

**Birth**: 1996-08-13 07:18 (UTC-7) — Fairfield, California, United States (38.2494, -122.0397)
**UTC**: 1996-08-13T14:18:00  ·  **JDN**: 2450309
**Local mean time**: 06:09:50  ·  **True solar time**: 06:05:05 (equation of time -4.7 min)

Panel version 0.1.0. Sections: 8.

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

Shares the Western calculation core. Distinctive layer: al-Biruni's reference conditions from the validated al-Biruni pack.

**Disclosures**

- **Source — Pack provenance.** Firdaria ordering, equal-seventh subperiod structure, sect and gender classifications, halb/hayyiz and their one-way implication come from the validated al-Biruni reference-condition pack, built from facing-page Arabic/English evidence.
- **Refused — Firdaria periods and ages.** The al-Biruni pack refuses node periods and age/date firdaria arithmetic because section 395 supplies neither node periods nor a major-duration table. Those values are therefore not emitted from this pack.
- **Refused — Abu Ma'shar and al-Qabisi doctrine.** Seven TEI witnesses are hash-pinned and 30 passage candidates are catalogued, including a Mars firdaria disagreement (Arabic 7 years vs Hermann 8) and an apparent al-Qabisi/al-Biruni Mercury difference. None is promoted to a rule pending controlling-edition collation.

**Calculation**

- **sect**: day
- **shared calculation core**: western_traditional
- **distinctive layers available**: al-Biruni reference conditions (validated), halb / hayyiz classification (validated), firdaria ordering, diurnal and nocturnal (validated)
- **distinctive layers gated**: firdaria period durations and dates, Abu Ma'shar Great Introduction doctrine, al-Qabisi Introduction doctrine, lunar mansions

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

Swiss Ephemeris sidereal positions; whole-sign houses; Vimshottari dasha keyed to the Moon's nakshatra.

**Disclosures**

- **Configured — Ayanamsa.** Lahiri (Chitrapaksha) selected. The engine supports eight ayanamsas and no validated research pack selects one; a different choice shifts every sidereal longitude and can move a placement across a sign boundary. *Alternatives: Fagan-Bradley, Krishnamurti, Raman, True Citra, True Revati, Surya Siddhanta, Hipparchos.*
- **Configured — House system.** Whole-sign houses, the dominant classical Jyotisha convention. Sripati and equal-house variants exist and would move cusp-adjacent placements. *Alternatives: Sripati, Equal house from the lagna degree.*
- **Configured — Nodes.** Mean nodes used for Rahu/Ketu. True-node calculation differs by up to about 1.5 degrees and is a live disagreement between schools. *Alternatives: True node.*
- **Source — Navamsha.** D9 is computed for every graha and the lagna, with vargottama flagged. Jyotisha treats the navamsha as mandatory rather than optional: a D1 verdict that D9 contradicts is not a finished judgment.
- **Refused — Interpretation depth.** This section reports calculation and structural condition only. Divisional charts beyond D1 and D9, Shadbala, and Ashtakavarga are not computed, so no strength claim depending on them is made.

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
  - graha Sun, rasi Cancer, degree in sign 27.2855, house 12, nakshatra Ashlesha, pada 4, nakshatra lord Mercury, dignity neutral placement, navamsha Pisces, navamsha division 9, navamsha dignity neutral placement, vargottama False, retrograde False
  - graha Moon, rasi Cancer, degree in sign 19.4353, house 12, nakshatra Ashlesha, pada 1, nakshatra lord Mercury, dignity own sign, navamsha Sagittarius, navamsha division 6, navamsha dignity neutral placement, vargottama False, retrograde False
  - graha Mercury, rasi Leo, degree in sign 23.3715, house 1, nakshatra Purva Phalguni, pada 4, nakshatra lord Venus, dignity neutral placement, navamsha Scorpio, navamsha division 8, navamsha dignity neutral placement, vargottama False, retrograde False
  - graha Venus, rasi Gemini, degree in sign 11.7285, house 11, nakshatra Ardra, pada 2, nakshatra lord Rahu, dignity neutral placement, navamsha Capricorn, navamsha division 4, navamsha dignity neutral placement, vargottama False, retrograde False
  - graha Mars, rasi Gemini, degree in sign 18.7086, house 11, nakshatra Ardra, pada 4, nakshatra lord Rahu, dignity neutral placement, navamsha Pisces, navamsha division 6, navamsha dignity neutral placement, vargottama False, retrograde False
  - graha Jupiter, rasi Sagittarius, degree in sign 14.6973, house 5, nakshatra Purva Ashadha, pada 1, nakshatra lord Venus, dignity own sign, navamsha Leo, navamsha division 5, navamsha dignity neutral placement, vargottama False, retrograde True
  - graha Saturn, rasi Pisces, degree in sign 13.0418, house 8, nakshatra Uttara Bhadrapada, pada 3, nakshatra lord Saturn, dignity neutral placement, navamsha Libra, navamsha division 4, navamsha dignity exalted, vargottama False, retrograde True
  - graha Rahu, rasi Virgo, degree in sign 16.6805, house 2, nakshatra Hasta, pada 3, nakshatra lord Moon, dignity not assessed for nodes, navamsha Gemini, navamsha division 6, navamsha dignity not assessed for nodes, vargottama False, retrograde True
  - graha Ketu, rasi Pisces, degree in sign 16.6805, house 8, nakshatra Revati, pada 1, nakshatra lord Mercury, dignity not assessed for nodes, navamsha Sagittarius, navamsha division 6, navamsha dignity not assessed for nodes, vargottama False, retrograde True
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
- **Refused — Strength and pattern.** Day-master strength class, pattern eligibility, and useful-element selection are school-specific and are not asserted here. The Ziping hierarchy requires month command before any such judgment.
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

## How to read the labels

- **validated research pack** — arithmetic from a fail-closed pack whose standalone validator passes in this repository.
- **live engine** — produced by the shipping Western calculator.
- **configured method** — the product chose a convention the research pack deliberately refuses to default. Alternatives are named inline.
- **Refused** — the tradition, or the surviving sources for it, cannot support the claim. This is a finding, not an omission.
