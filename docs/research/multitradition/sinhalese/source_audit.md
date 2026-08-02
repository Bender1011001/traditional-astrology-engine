# Sinhalese and Sri Lankan Astrology Source Audit

Status: bounded pilot is research-feasible; no customer engine is authorized  
Audit date: 2026-07-31  
Product status: `research_verified` for corpus mapping, `not_implemented` for calculations and readings

## Decision

Sri Lanka has enough source depth to support a serious, source-scoped research
program, but not a single undifferentiated "Sri Lankan astrology" engine. The
first implementation must keep at least three layers separate:

1. the Sanskrit astral compilation associated with Anomadassi in medieval Sri
   Lanka;
2. later Sinhala horoscopy, almanac, matching and auspicious-time practice; and
3. Sri Lankan Tamil jyotisha manuscripts and living practice.

The current evidence justifies a source map and calculation concordance. It
does not yet justify publishing comprehensive readings, assuming that every
rule in a Sanskrit compilation was distinctively Sinhalese, or treating Sinhala
and Sri Lankan Tamil practice as interchangeable.

## Controlling historical witness candidate

### Daivajnakamadhenu

The strongest technical starting point found in this pass is the 1905 Benares
Sanskrit Series edition available through Jain eLibrary:

- catalog and scan: <https://jainqq.org/explore/009874/9>
- repository romanized OCR:
  <https://jainqq.org/booktext/Daivagna_Kamdhenu_Romanized/009874>
- print identity: Chaukhamba Sanskrit Series Office, Benares, 1905, 318 pages;
- title-page attribution: a work by Anomadassi Sangharaja Mahasthavira of
  Hastavanagalya Parivena in Ceylon, edited by C. A. Seelakkhandha Sthavira of
  Sailabimbarama, Dodanduwa, Ceylon, and Seetarama Upadhyaya of Sanskrit
  College, Benares;
- inspected OCR size: 434,945 UTF-8 bytes;
- inspected OCR SHA-256:
  `017833cb89b7eda054003c9da3a0375ee9921a6756824b59f53100e9ead8355c`.

The inspected contents list thirty chapters and 198 indexed sections. The
technical scope includes:

| Layer | Material exposed by the contents and inspected OCR |
|---|---|
| Astronomical/calendrical | planetary motion, years, Sun, Moon, planets, nakshatra, tithi, yoga, karana, visibility and eclipses |
| Omen and environmental | celestial and terrestrial phenomena, dreams, bodily signs and animal behavior |
| Natal | birth judgment, longevity, planetary periods, ashtakavarga and yogas |
| Interrogational | journeys, victory, captivity, missing persons, pregnancy, water and treasure questions |
| Electional | muhurta, kala hora, lunar states, defects, exceptions and life-cycle rites |
| Compatibility | marriage questions and comparison categories including gana, mahendra, stri-dirgha, yoni, rasi, sign lord, vashya and rajju |
| Applied branches | architecture, travel, agriculture, trade, rites, toxicology and medical material |

This breadth is valuable but also dangerous. The work is a compilation. Each
procedure needs a source-stratum and citation graph before the product can call
it Sri Lankan, medieval, natal, electional or living practice. OCR is noisy and
may not be used as the sole basis of an atomic rule. Every encoded passage must
be checked against the scan and reviewed in Sanskrit.

## Historical and ethnographic boundary evidence

Alastair Gornall's full study, "Conceptualising the World in Pali Literature,"
places Anomadassi in the thirteenth-century Sri Lankan Mahavihara environment
and describes the Sanskrit astronomical anthology in the wider history of Pali
and Sanskrit astral knowledge:
<https://hasp.ub.uni-heidelberg.de/journals/jpts/article/download/28261/27652/57506>.
It is a source-discovery and intellectual-history authority, not a source for
atomic judgments.

Steven E. G. Kemper's 1979 study of Sinhalese astrology provides a different
kind of evidence:
<https://www.cambridge.org/core/journals/journal-of-asian-studies/article/abs/sinhalese-astrology-south-asian-caste-systems-and-the-notion-of-individuality/92F0E2F27BB41283BB3B0846B81C6867>.
Its accessible article material and notes document person-specific horoscopy,
counterclockwise chart layout, the importance of the birth `nakat`, and a local
description of the eight-category, thirty-six-point marriage comparison. These
observations are not enough to encode calculation rules or assume a universal
acceptance threshold. They identify exactly what needs primary-text and worked-
example verification.

## Modern technical transmission leads

Institutional curricula are useful bibliography and reviewer maps:

- University of Peradeniya Sanskrit courses teach horoscope construction,
  auspicious time, planetary periods, signs, planets, lunar mansions and
  selected chapters of Brhajjataka:
  <https://arts.pdn.ac.lk/classical/sanskrit-ug.htm>.
- Peradeniya course documents additionally name Panchanga, Shadvarga, naming
  and marriage matching in Sri Lankan social practice:
  <https://arts.pdn.ac.lk/classical/content/SKT-curriculum-since-2019.pdf> and
  <https://cdce.pdn.ac.lk/dload/BA_Common/SupplementaryCourcesAll.pdf>.
- The University of Colombo Institute of Indigenous Medicine curriculum names
  Sinhala references including *Lagna Chandrikava* and *Nakshatra
  Nighantuva*:
  <https://fim.cmb.ac.lk/wp-content/uploads/2010/08/BAMS-CURRICULUM-2011.pdf>.

These pages do not establish rules. They provide exact texts to acquire and
qualified institutions from which to seek bilingual review and worked
examples.

The Sri Lankan Department of Cultural Affairs also documents an official,
living consensus process among astrologers and almanac writers for annual New
Year auspicious times:
<https://culturaldept.gov.lk/index.php?Itemid=248&catid=13&id=262%3Athe-2026-new-year-s-amulets-set&lang=en&option=com_content&view=article>.
That establishes public practice, not the unpublished calculation by which the
committee reached the listed instants.

## Manuscript acquisition routes

- University of Sri Jayewardenepura describes astrology manuscripts in its
  Pali, Sinhala and Sanskrit palm-leaf holdings, mostly eighteenth and
  nineteenth century, with supervised access:
  <https://lib.sjp.ac.lk/palm-leaf-manuscript-reading-service/>.
- The British Library catalog exposes a separate set of Sri Lankan Tamil
  palm-leaf astrology records:
  <https://searcharchives.bl.uk/?f%5Bmaterial_type_si%5D%5B%5D=Archives+and+Manuscripts&f%5Bproject_collections_ssim%5D%5B%5D=Sri+Lankan+Tamil+Palm-Leaf+Manuscripts&f%5Brelated_subjects_ssim%5D%5B%5D=Astrology&f%5Burl_stub_si%5D%5B%5D=eap.bl.uk&per_page=50&sort=date>.
- The American Institute for Sri Lankan Studies Paramaththa archive lists
  astrology among manuscript subjects: <https://www.aisls.org/paramaththa/>.
- The University of Manchester describes Sinhala palm-leaf holdings in its
  South Asian collections:
  <https://www.digitalcollections.manchester.ac.uk/collections/pali>.

The Tamil collection must become its own source and review track. Country of
origin is not a license to merge languages, textual lineages or practitioner
communities.

## Birth-input capability map

| Technique family | Can birth data drive it? | Current disposition |
|---|---|---|
| Natal horoscope | Yes, with exact calendar, time, location and school conventions | Research source acquisition and worked examples required |
| Birth nakat | Yes | Calculation convention and historical calendar boundary tests required |
| Dasha and longevity | Yes in historical texts | Historical Use Only; longevity/death claims must not be rendered as literal outcomes |
| Marriage matching | Requires two persons' birth data | Separate consented two-person workflow; category formulas and thresholds require Sinhala-source verification |
| Auspicious times | No; it requires a proposed activity and time/location window | Separate electional workflow, not an automatic natal result |
| Prashna | No; it requires a sincere question and question moment | Separate interrogational workflow |
| Omens and dreams | No; an observed event is the input | Event-specific historical module only |
| Medical, ritual and fetal-sex material | Historically present | Suppressed from predictive customer output; research metadata only unless a safe educational treatment is approved |

## First implementation pilot

The first pilot is deliberately narrow:

1. produce a page/section concordance for the 1905 edition;
2. select one calculation family whose inputs and outputs are unambiguous;
3. align each rule to a scan page, Sanskrit transcription and reviewed
   translation;
4. reproduce at least two worked examples from the same school or an identified
   almanac;
5. test calendar, sunrise/day-boundary and birth-time uncertainty transitions;
6. have a Sanskrit philologist and a Sinhala astrology-domain reviewer approve
   the source classification; and
7. expose only the deterministic trace until the evidence and cultural-review
   gates pass.

A modern Sinhala natal or compatibility pilot follows only after the named
Sinhala texts are acquired. A Sri Lankan Tamil pilot follows through its own
Tamil sources and reviewers.

## Failure conditions

The track remains non-production if any of the following is true:

- a rule exists only in noisy OCR or an unsourced commercial explanation;
- the source edition, chapter and page cannot be emitted in the trace;
- an Indian rule is labeled Sinhalese solely because it was copied in Sri
  Lanka;
- a modern practitioner convention is projected backward into Anomadassi;
- a Sinhala convention is applied to the Tamil collection, or vice versa;
- an eight-category compatibility total or threshold lacks a school-specific
  worked example;
- the prose layer converts historical longevity, health, death, sex/gender or
  ritual claims into factual advice or deterministic predictions; or
- customer output obscures that only the Western system is currently live.

