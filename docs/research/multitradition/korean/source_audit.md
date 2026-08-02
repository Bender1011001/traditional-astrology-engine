# Korean Saju, Myeongri and Related Divination Source Audit

Status: bounded calculation research is feasible; interpretation remains source- and school-limited  
Audit date: 2026-07-31  
Product status: `research_verified` for taxonomy and source routing, `not_implemented` for customer readings

## Decision

Korean birth divination cannot be represented by a single "Korean astrology"
switch. At minimum, the product must separate:

1. Korean transmission and practice of Ziping/Sammyeong Four Pillars, commonly
   called Saju-Myeongri;
2. Korean court calendrics and Myeonggwahak date-selection literature;
3. *Tojeong Bigyeol*, an annual divination system with its own casting and text
   history;
4. *Dang Saju*, which requires a separate source audit;
5. marriage exchange, compatibility (`gunghap`) and date selection; and
6. modern Korean schools and counseling practice.

Saju shares major textual ancestors with Chinese Ziping. That does not make a
Chinese engine a sufficient Korean engine. Korean editions, terminology,
calendar tables, historical civil time, school conventions, worked examples
and cultural-review expectations all require explicit versioning.

## Historical transmission map

Kim Mantae's 2010 study provides the most useful inspected scholarly route into
the early corpus:
<https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART001512374>.
The accessible abstract argues for stages of transmission from Tang-period
forms through the Yuan-era spread of the Ziping system, identifies a Korean
work titled *Ohaengchonggwal* in 1458, and records
*Japyeongsammyeongtongbyeonyeonwon* as a Joseon Myeonggwahak textbook. These are
historical claims and source leads, not rules that can be encoded from the
abstract.

Kim's 2013 article focuses on Seo Geo-jeong's *Ohaengchonggwal* and
*Pirwonjapgi*:
<https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART001782319>.
Its accessible abstracts describe the former as the earliest known Saju-
Myeongri book written in Korea and the latter as the earliest Korean document
using the term `Saju`. It also records a Neo-Confucian intellectual frame and
Seo's criticism of practitioners using disorderly theories to deceive clients.

The first source-acquisition priority is therefore not another modern summary.
It is surviving *Ohaengchonggwal* material, the exact *Pirwonjapgi* passages,
and the Joseon editions or records of the Myeonggwahak teaching corpus.

## Korean Saju technical taxonomy

The Academy of Korean Studies' encyclopedia entry supplies a modern Korean
technical map and worked tables:
<https://encykorea.aks.ac.kr/Article/E0025957>. The inspected page describes:

- year, month, day and hour pillars;
- the day stem as the central reference;
- hidden stems and relationships among stems and branches;
- yin-yang and five-phase generation and control;
- six-kin/relational categories;
- combinations, clashes, punishments, breaking, harms and related structures;
- twelve life stages and spirit-star families;
- pattern (`gyeokguk`) and useful-god (`yongshin`) judgment; and
- ten-year major cycles, annual cycles and finer time layers.

This is enough to inventory entities and independently recompute the presented
chart. It is not enough to choose one balancing method, useful-god hierarchy,
major-cycle start formula, spirit-star set or interpretive school. The article
must remain a taxonomy and validation lead until every procedure is tied to a
named edition and Korean reviewer.

A 2026 abstract on algorithmic formalization is unusually relevant to system
design:
<https://db.koreascholar.com/Article/Detail/451431>. It classifies solar-term,
five-phase and major-cycle calculations as fully formalizable; some
combinations, voids, stages and spirit-star rules as partly formalizable; and
useful-god selection as dependent on expert tacit judgment. The full article
and program were not accessible. Its conclusion is a hypothesis to test, not a
reason to place untraceable practitioner intuition inside production code. A
claim of "non-formalizable" may instead indicate unstated school selection,
conflicting authorities or missing precedence rules.

## Calendar and historical time

The Four Pillars are only as sound as their calendar and time normalization.
Digital Jangseogak's *Manyeonlyeok* record describes a royal Korean witness
dated across 1710-1776, based on the Qing Shixian system and used for new moons,
month ends and solar terms:
<https://jsg.aks.ac.kr/dir/view?catePath=%EC%88%98%EC%A7%91%EB%B6%84%EB%A5%98&dataId=JSG_K3-390>.
The institution describes it as a basis for later Joseon long-range calendar
production. This is evidence for an edition-specific Joseon calendar kernel,
not an automatic license to apply modern astronomical solar-term instants to
every historical Korean chart.

The implementation must version:

- Gregorian, Julian, lunisolar and recorded almanac input;
- true astronomical versus traditional tabular solar-term calculation;
- year and month pillar boundaries;
- day rollover convention;
- hour-branch boundaries and any true-solar-time correction;
- location and longitude; and
- every Korean civil-time and daylight-saving transition.

The Korea Astronomy and Space Science Institute paper found for historical
standard-time changes timed out on direct access:
<https://harg.kasi.re.kr/pro_plus/down/200307/200307_067-084.pdf>. Its search
snippet is not evidence. The paper, contemporaneous legal enactments and IANA
transition data must be reconciled before an hour pillar is calculated for a
twentieth-century Korean birth. A thirty- or sixty-minute historical error can
change the hour pillar and all downstream rules.

## Myeonggwahak and electional practice

Jangseogak's *Yeoksamyeongwon* record is a strong bounded witness:
<https://jsg.aks.ac.kr/dir/view?dataId=JSG_K3-402>. The five-volume Joseon
edition has a 1799 royal preface and is described as a reference for Gwansanggam
Myeonggwahak officials judging ordinary auspiciousness and selecting dates. Its
books cover year/month construction, auspicious and inauspicious monthly
spirits, mixed yin-yang doctrine and selection, with quoted authorities and the
compiler's commentary.

This belongs in a Korean court-transmission electional pack. It does not belong
in a natal report merely because the customer supplied a birth date. An
election requires a proposed activity, location and time window.

## Tojeong Bigyeol is a separate engine

The Academy of Korean Studies overview states that *Tojeong Bigyeol* uses year
ruler, month construction and day-cycle arithmetic for annual fortune,
constructs three figures from birth year, month and day without birth hour,
uses forty-eight of the sixty-four hexagrams, and supplies twelve monthly
verses:
<https://encykorea.aks.ac.kr/Article/E0059207>. The same article questions the
traditional attribution to Yi Ji-ham and places its widespread seasonal use
later than his lifetime.

Jangseogak holds an undated one-volume Classical Chinese witness with 732
microfilm images:
<https://jsg.aks.ac.kr/dir/view?dataId=ARC_kh2_je_a_vsu_C9A%5E9A_000>. The item
record was inspected, but its folios were not. No casting formula or verse may
be encoded until this witness is compared with dated copies and modern printed
traditions. Attribution, available hexagrams, remainder handling, age counting
and text variants all require a versioned stemma.

## Marriage evidence and privacy

Jangseogak's digitized `Saju Danja` is a direct social-history witness:
<https://jsg.aks.ac.kr/dir/view?catePath=%EC%88%98%EC%A7%91%EB%B6%84%EB%A5%98&dataId=ANC_G002%2BAKS%2BKSM-XF.0000.0000-20101008.B002a_002_00596_XXX>.
It records a groom's birth year, lunar month, day and double-hour sent to the
bride's family. It demonstrates exchange of the four birth components in a
marriage process, but contains no visible compatibility verdict.

A modern compatibility feature therefore needs two-person consent, separate
retention controls, a Korean source for the actual comparison, and a clear
statement that it is historical/cultural interpretation rather than a measure
of relationship fitness. Gendered formulas, fertility claims or social-status
judgments cannot be silently normalized or published as facts.

## Birth-input capability map

| Technique family | Input beyond one person's birth data | Current disposition |
|---|---|---|
| Korean Saju-Myeongri natal | Exact location, civil-time history and selected school | Bounded calculation pilot after source and convention freeze |
| Major/annual fortune cycles | Evaluation date and a versioned start/direction method | Recompute worked examples before interpretation |
| Tojeong Bigyeol | Birth year/month/day plus target year; no birth hour in the inspected overview | Separate annual engine after manuscript comparison |
| Marriage `gunghap` | A second person's consented birth data | Separate privacy-sensitive workflow; rules not yet verified |
| Myeonggwahak election | Proposed activity, place and candidate time window | Separate electional workflow |
| Dang Saju | Likely birth-derived, but no controlling source inspected | `source_limited` and separate audit required |

## First implementation pilots

### Pilot A: Korean Four-Pillars calculation profile

1. Acquire full Korean scholarship and exact source editions identified above.
2. Freeze a named modern Korean school for the pilot.
3. Implement only calendar conversion, four pillars, hidden stems, ten-god
   relationships and one explicitly sourced major-cycle method.
4. Recompute the Academy of Korean Studies worked chart without copying its
   conclusion.
5. Compare the same birth through the shared Chinese Ziping kernel and emit
   every difference caused by Korean source/configuration choices.
6. Test immediately before, at and after solar terms, midnight/day rollover,
   hour boundaries, historical offset changes and daylight-saving changes.
7. Obtain Korean-language expert review of the calculation trace before adding
   interpretive rules.

### Pilot B: Tojeong Bigyeol edition concordance

1. Acquire the Jangseogak images and at least two dated comparison witnesses.
2. Record every formula, table, hexagram omission, remainder rule and verse by
   folio.
3. Reproduce documented historical examples or almanac outputs.
4. Publish no annual prediction until the selected recension and translation
   pass independent review.

## Failure conditions

The Korean track remains non-production if:

- Chinese Ziping results are merely translated into Korean and labeled Saju;
- a Korean edition or practice is treated as indigenous when it is an
  identifiable imported Chinese witness without local modification;
- calendar and civil-time choices are hidden;
- major-cycle direction or first-cycle timing lacks a named source and worked
  example;
- useful-god or pattern selection is delegated to free-form model intuition;
- *Tojeong Bigyeol*, *Dang Saju*, Saju and electional methods are blended;
- marriage material is calculated without the second person's informed
  consent;
- health, death, disaster, fertility, gender-role, legal, financial or ritual
  claims become factual advice; or
- the interface implies this researched track is live when only the Western
  system is currently implemented.

