# Vietnamese Calendrical and Astrological Source Audit

Status: modern calendar kernel is research-verifiable; comprehensive natal reading remains source-limited  
Audit date: 2026-07-31  
Product status: `source_limited`; no customer Vietnamese reading is authorized

## Decision

There is no defensible single "Vietnamese astrology" engine. The evidence
already requires separate modules for:

1. historical Kinh/Viet royal calendrical astronomy;
2. the modern Vietnamese lunisolar calendar;
3. Vietnamese `Tử Vi` lineages;
4. Vietnamese transmissions of `Tử Bình`/Four Pillars, Hà Lạc, Thái Ất,
   Độn Giáp, Lục Nhâm and date selection;
5. Mường calendrical practice; and
6. Cham and other community traditions.

The modern lunisolar calculation can become a bounded, independently tested
kernel. It cannot by itself generate a natal judgment. Chinese calculations or
interpretations may be comparative witnesses, but may not be silently labeled
Vietnamese.

## Historical Vietnamese calendar evidence

Phạm Vũ Lộc and Lê Thành Lân's 2021 chapter, "A Brief History of Vietnamese
Astronomy and Calendars During the Reign of the Royal Dynasties," was inspected
in full through its author-uploaded copy:
<https://www.researchgate.net/publication/352896678_A_Brief_History_of_Vietnamese_Astronomy_and_Calendars_During_the_Reign_of_the_Royal_Dynasties>.
It is a scholarly synthesis and source map, not a primary rulebook.

The chapter documents that Vietnamese dynasties maintained an Office of
Astronomy whose responsibilities included calendars, eclipses, hemerology,
astrology, and propitious days and places. It also rejects a simple-copy model:
royal Vietnamese calendars could differ from contemporary Chinese calendars,
and the governing calendar changed across dynasties and regions. The chapter
maps `Bách Trúng Kinh` manuscript witnesses covering long runs of dated
calendars and distinguishes Tonkin and Cochinchina evidence and the adoption of
named calendar systems.

That history creates two mandatory fields for every historical conversion:

- `calendar_regime_id`, including dynasty, region, named calendar and date
  range; and
- `conversion_evidence_id`, identifying a dated almanac or a reconstruction
  validated against one.

Proleptically applying today's Vietnamese calendar to an eighteenth-century
birth is not acceptable merely because the place is within modern Vietnam.

## Modern Vietnamese lunisolar kernel

The inspected calculation page at
<https://www.xemamlich.uhm.vn/calrules_en.html> gives an explicit modern
procedure and worked 1984-1985 tables:

1. a lunar month begins on the local civil day containing the astronomical New
   Moon;
2. the winter solstice belongs to month 11;
3. a normal year has twelve lunar months;
4. if thirteen lunar months occur between the relevant month-11 anchors, the
   first following month without a principal solar term is intercalary and
   repeats the previous month number; and
5. Vietnam's local civil day, conventionally referenced to 105 degrees east on
   the page, can place a New Moon or solstice on a different date than Beijing.

The worked example is especially valuable because it demonstrates rather than
merely asserts divergence: in 1985 the Vietnamese and Chinese month numbering
separates around a solstice/New-Moon boundary and later reunites after an
intercalary month.

This page is a modern technical explanation, not a historical statute or
critical edition. Before promotion, its event times and month labels must be
recomputed using a named ephemeris and compared with Vietnamese published
almanacs. The longitude reference, civil-time law and valid date range must be
configuration, not hidden constants.

## Additional calendar acquisition leads

Kazuhiko Okazaki's "Old-time Luni-solar Calendars in Vietnam" is indexed by
Gunma University at <https://gunma-u.repo.nii.ac.jp/records/4360>. The record
exposes a PDF filename, but direct retrieval failed during this audit. No rule
from search snippets is accepted.

The VJOL record for "Hai cha con họ Đặng và lịch học Việt Nam xưa" at
<https://vjol.info.vn/index.php/ncpt-hue/article/view/4569> is another useful
history lead, but robots access failed. Its indexed description is not rule
evidence. Both works remain acquisition tasks.

## Vietnamese Tử Vi evidence

The Vietnamese Open Educational Resources overview at
<https://voer.edu.vn/m/tu-vi/eab16554> is a Creative Commons discovery and
terminology source. It says the history is uncertain, describes a twelve-palace
chart driven by lunar birth year, month, day, double-hour and sex, inventories
star-placement inputs, and explicitly reports Vietnamese/Chinese and
Vietnamese-school differences. Examples include a claimed different starting
palace, variable annual-limit methods, star totals, placement of Hỏa/Linh and
competing monthly timing procedures.

Those statements are valuable as a list of disagreements to test. They are not
accepted atomic rules because the page identifies its author as Wikipedia,
mixes traditional attribution with legend, sometimes corrects its own
bibliography, and does not provide passage-level editions for most claims.

A Vietnamese Tử Vi pack therefore needs:

- a named Vietnamese work, edition, date and lineage;
- a complete construction table for all included stars;
- the exact lunar-calendar and leap-month convention;
- the day and double-hour boundary;
- sex/gender direction rules represented historically and safely;
- palace, five-phase bureau, main/body palace and transformation tables;
- decade, annual, monthly and finer timing methods, each school-scoped;
- at least ten published worked charts reproduced exactly; and
- Vietnamese-language review of both rule extraction and customer prose.

The Chinese `紫微斗數全書` audit supplies a comparative source lineage. It does
not automatically govern Vietnamese construction, star sets or timing.

## Birth-input capability map

| Technique family | Can one birth record drive it? | Current disposition |
|---|---|---|
| Modern Vietnamese lunar date | Yes, with exact instant/place and configured civil-day rules | `research_verified` after independent almanac tests |
| Historical royal-calendar date | Sometimes, after regime selection | `source_limited` pending dated almanac concordances |
| Vietnamese Tử Vi chart construction | Yes in principle | `source_limited` pending controlling editions and worked charts |
| Vietnamese Four Pillars/Tử Bình | Yes in principle | Separate source pack; never relabel Chinese BaZi output |
| Date selection and hemerology | Requires candidate activity/date, not only birth data | Separate workflow |
| Mường or Cham calendars | Community- and lineage-specific | Separate audits; no output |

## First valid pilots

### Pilot A: modern calendar boundary suite

1. Recompute all New Moons, principal terms and month labels in the published
   1984-1985 worked tables.
2. Compare Vietnam and China at every event whose local civil dates differ.
3. Add one-second-before, exact-event and one-second-after vectors.
4. Validate against at least two independent Vietnamese almanac series.
5. Test every Vietnamese civil-time transition within the supported period.
6. Return ambiguity rather than choosing a month when input uncertainty crosses
   a boundary.

### Pilot B: one named Vietnamese Tử Vi school

1. Acquire a legally usable Vietnamese edition with full construction tables.
2. Establish its relationship to Chinese `Toàn Thư`, `Toàn Tập` or another
   lineage without assuming identity.
3. Encode chart construction separately from interpretation.
4. Reproduce ten worked charts, including a leap-month birth and every double-
   hour boundary.
5. Have a Vietnamese specialist adjudicate disagreements.
6. Publish the school name and omissions in the coverage manifest.

## Safety and cultural limits

Historical sources may make severe claims about illness, death, fertility,
children, wealth, caste or gender. Such passages may be preserved in the
forensic trace for Historical Use Only research, but cannot become diagnosis,
financial advice, reproductive prediction, literal death prediction, or
discriminatory treatment. A reading may discuss symbolic or historical themes
only within the selected source's verified limits.

## Failure conditions

The track remains `source_limited` if:

- modern calendar rules are projected backward across historical regimes;
- Beijing dates or Chinese chart rules are silently reused for Vietnam;
- one modern overview decides a disputed Vietnamese-school rule;
- Tử Vi, Tử Bình, Hà Lạc, Thái Ất or date selection are blended;
- Kinh, Mường and Cham materials are merged;
- leap-month, local-day, double-hour or sex/gender direction conventions are
  hidden;
- no Vietnamese-language reviewer approves the rule trace; or
- the interface implies a live Vietnamese engine while only Western is live.

