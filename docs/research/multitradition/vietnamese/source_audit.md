# Vietnamese Calendrical and Astrological Source Audit

Status: modern calendar kernel is research-verifiable; a Vietnamese-language Tử Vi
delineation pack now exists; chart construction remains source-limited  
Audit dates: 2026-07-31, extended 2026-08-04  
Product status: `source_limited`; no customer Vietnamese reading is authorized

## 2026-08-04 addition: the track is no longer calendar-only

The 2026-07-31 audit was right about the shape of the problem and wrong about what could
be done about it now. It listed `Tử Vi` chart construction as `source_limited` "pending
controlling editions and worked charts" and then stopped — the track carried a calendar
and no astrology, in a country where **Tử Vi Đẩu Số is what an ordinary person means by
having their chart read**. Pilot B, "one named Vietnamese Tử Vi school," was written down
and not attempted.

It has now been attempted. The result splits cleanly in two, and the split is the finding.

### What was acquired

**A Vietnamese-language delineation source covering all twelve palaces.** *Phú Tử Vi Lê
Quí Đôn* — a `lục bát` verse phú traditionally attributed to Lê Quý Đôn (1726-1784),
transmitted through Lương Quới Nhơn's *Tử Vi Đẩu Số Thực Hành* (1968) and transcribed in
2017 with an explicit collation note. Retrieved from the Internet Archive, hash-pinned,
flattened to a 778-line addressed rendering, and read in full. It yielded
`tuvi_rule_manifest.json`: **19 rules, 21 vectors, 49 delineation cells** across the
Mệnh, Điền Trạch, Quan Lộc, Nô Bộc and Tài Bạch palaces, each carrying the Vietnamese
verbatim as the OCR reads it, a normalised reading, and an English engine rendering.

**One openly licensed modern book with no technique in it.** *Tử Vi Đông A* (2026, CC0)
was read and searched: `an sao` 0, `lập thành` 0, `đại hạn` 0, `tiểu hạn` 0, `giờ Tý` 0.
It is an essay on Tử Vi as Trần-dynasty statecraft. Registered as reception evidence with
a rule forbidding any construction or delineation rule from citing it.

**The named edition the 2026-07-31 audit asked for** — Vân Đằng Thái Thứ Lang, *Tử Vi Đẩu
Số Tân Biên*, Tín Đức Thư Xã, 1957, 352pp, in three parts: `Lập thành`, `Luận đoán 12
cung`, `Luận đoán Vận hạn`. Named, dated, structurally described, **and not held.**

### The three findings that answer "Vietnamese or reprinted Chinese?"

This was the question the 2026-07-31 audit posed and could not test. It is now testable
against a held text.

1. **The palace enumeration is the exact reverse of the Chinese order.** The phú numbers
   its own sections aloud: Mệnh, Phụ Mẫu, Phúc Đức, Điền Trạch, Quan Lộc, Nô Bộc, Thiên
   Di, Tật Ách, Tài Bạch, Tử Tức, Phu Thê, Huynh Đệ. The Quanshu enumeration runs 命,
   兄弟, 夫妻, 子女, 財帛, 疾厄, 遷移, 奴僕, 官祿, 田宅, 福德, 父母. Position *k* of one
   is position 14−*k* of the other, at every position, with no counterexample. The second
   palace this tradition reaches for is *parents*; the Chinese order reaches for
   *siblings*.

2. **The Phúc Đức palace carries ancestral-tomb geomancy.** Roughly 104 of its 133 lines
   — the longest block in the phú by a wide margin — read the natal chart's Phúc Đức
   palace as a reading of the ancestral graves: Trường Sinh as `khởi tổ`, Thanh Long as
   the dragon water attending on the left, Bạch Hổ as the tiger water on the right,
   `phân kim` set from the branch characters, `dương mộ` and `âm mộ`, and an
   eighteen-entry table mapping Tử Vi stars onto five-phase categories and landforms —
   Thiên Cơ as the wood-star form, Vũ Khúc as metal, Văn Khúc as the watercourse, Linh
   Tinh as a brush peak, Long Trì as a well, Thiên Quan and Thiên Phúc as ground near a
   shrine. This is Tử Vi fused with `âm trạch` practice, conducted entirely with Tử Vi
   stars rather than a compass school's own apparatus. It is not in the Chinese work's
   福德 palace.

3. **Tuần and Triệt operate as named agents** on palaces, which is one of the very
   differences the VOER overview flagged in the 2026-07-31 pass as a claim to test.

Two caveats are carried in the rules themselves and are repeated here because they matter:
findings 1 and 2 compare against **general knowledge of the Quanshu, not a held edition**,
and one witness is not a tradition. Pinning a Quanshu edition is the cheapest available
improvement to this track and would convert both from asserted to shown.

### The blocker, stated exactly

**This track now has delineation without construction.** The phú judges a chart it assumes
is already built. It never states how to find cung Mệnh from lunar month and hour, how to
find cung Thân, how to determine the ngũ hành cục, where Tử Vi is placed, where the
northern and southern series begin, or — pointedly — where Tuần and Triệt fall.

So the pack holds 49 cells of judgement and cannot produce one chart to apply them to.

The temptation is specific and is refused in writing. This repository has a working
`ziwei/` module. Running it and labelling the output Vietnamese would produce something
that looked right and was wrong, because the Vietnamese schools are reported to disagree
with the Chinese **and with each other** on exactly the construction questions — the
starting palace, star totals, the placement of Hỏa and Linh, annual-limit method. Every
one is decided during construction. Borrowing picks a side in a live dispute and stamps it
Vietnamese. `vietnam.tuvi.no_chart_construction_in_this_witness` makes the pack fail
closed instead.

Under the DEFENSIBILITY standard's own table this is the third row: **public-domain-or-not,
the original is not retrievable.** An access problem, not a language or rights problem —
except that here the missing document is named, dated and in copyright, so the path is
licensing rather than searching.

### Documented negative results

Recorded because an untested absence is not a finding.

| Target | Method | Result |
|---|---|---|
| Vietnamese construction manuals in retrievable full text | six archive.org advancedsearch queries: `Van Dang Thai Thu Lang` (224 hits), `Tu Vi Ham So` (564), `Tu Vi Nghiem Ly` (722), `tu vi dau so toan thu` (904), `Nguyen Phat Loc tu vi` (120), and the Vietnamese string `"tử vi" AND "đẩu số"` (128) | none relevant. The four Tử Vi items found were all followed up; two were downloaded, one is the phú, one is the reception book |
| Nôm-script Vietnamese Tử Vi manuscripts | Hán Nôm institute CONTENTdm search API, three queries (`紫微`, `tu vi`, `tuvi`) | HTTP 200 each time, `totalResults` **0** each time |
| the same | Vietnamese Nôm Preservation Foundation text collections page, inspected | collections are Thắng Nghiêm and Phổ Nhân temple texts, the Digital Library of Hán-Nôm, Kiều, Lục Vân Tiên, Chinh Phụ Ngâm Khúc, Hồ Xuân Hương, History of Greater Vietnam. **No divination, astrology, almanac or tử vi collection listed** |
| the full text of *Tử Vi Đẩu Số Tân Biên* | an aggregator site carrying it by chapter was fetched; the page is an index of per-palace articles and carries no construction rules | not pursued further: crawling an in-copyright 1957 book from an aggregator is not an acquisition path this repository will use |

The open lead: the Institute of Hán-Nôm Studies' own catalogue at hannom.org.vn, searched
under its subject headings rather than by title string.

### Safety posture for the material actually acquired

The phú is a pre-modern divinatory text and it says pre-modern things. Nine checklist rows
are `refused` — lifespan spans of 60, 70 and 80-to-90 years; two death-on-the-road
clauses; a `Đoán sinh tử` section whose stated purpose is to warn a person of the year
they may not survive; a Tật Ách palace that is a star-to-ailment table including blindness
and madness; prediction of the sex and number of children; `dâm dục` clauses about the
reader and their siblings; a class judgement about servants; and an appended separate
procedure for women premised on a woman of rank owing her position to her husband.

All of it is kept verbatim in the trace with line addresses, and none of it reaches a
reader. Refusal is applied **per cell** where the surrounding palace is otherwise sound —
the Tham Lang cell in Mệnh and the servants couplet in Nô Bộc are refused inside palaces
whose other cells are not — and **per section** where the whole block is unsafe. Deleting
these clauses instead of refusing them would misrepresent the source, which is a different
failure from the one being avoided.

The governing spec for all of this is [`defensibility_spec.md`](defensibility_spec.md),
new in this pass.

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

**2026-08-04 status of this list.** The first, second, seventh and eighth items below are
now partially or wholly answered by the *Phú Tử Vi Lê Quí Đôn* pack; the rest are not. See
the addition at the head of this document for what was acquired and what the remaining
blocker is.

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
| Vietnamese Tử Vi chart construction | Yes in principle | `source_limited` — as of 2026-08-04 the missing document is **named**: the `Lập thành` section of Vân Đằng Thái Thứ Lang, *Tử Vi Đẩu Số Tân Biên* (1957). In copyright; licensing, not searching |
| Vietnamese Tử Vi palace and star delineation | Not from a birth alone — it needs a chart first | `source_limited` but **evidenced**: 19 rules, 21 vectors, 49 cells from the *Phú Tử Vi Lê Quí Đôn*. Orphaned until construction lands |
| Vietnamese Tử Vi tomb geomancy in Phúc Đức | Would need a chart, and is refused as advice regardless | `source_limited`; recorded as a technique, never issued |
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

