# Zi Wei Dou Shu Source and Rule-Family Audit

Status: a source-scoped calculation pilot is feasible; comprehensive reading remains source-limited  
Audit date: 2026-07-31  
Product status: `source_limited`; no customer Zi Wei reading is authorized

## Decision

`Zi Wei Dou Shu` is not one stable table set or one interpretation school. The
first implementation must be a named-edition chart calculator, not a generic
"Chinese astrology" reading. It must keep at least these lineages separate:

1. the later natal system represented by `紫微斗數全書` (*Complete Book of Zi
   Wei Dou Shu*) and related `全集` and `捷覽` witnesses;
2. later Sanhe, Feixing, Zhongzhou and other school packs, only after their own
   sources are established;
3. Vietnamese Tử Vi transmissions; and
4. the different Daoist-canon work also titled `紫微斗數`.

The shared title in item 4 is a dangerous false friend. Catalog and text-project
evidence says its star names and construction method differ from the system in
modern circulation. It must never be used to fill a gap in the later natal
system.

## Primary transcription inspected

Chinese Wikisource transcribes the three-juan Qing work `紫微斗數全書`:
<https://zh.wikisource.org/wiki/%E7%B4%AB%E5%BE%AE%E6%96%97%E6%95%B8%E5%85%A8%E6%9B%B8>.
The table of contents separates:

- juan 1: theoretical poems, star question-and-answer material, combinations,
  favorable/unfavorable configurations and rank judgments;
- juan 2: chart construction followed by the twelve palaces; and
- juan 3: interpretive method, exact-time concerns, ten-year and annual limits,
  and specialized judgments.

Juan 2 was inspected at
<https://zh.wikisource.org/wiki/%E7%B4%AB%E5%BE%AE%E6%96%97%E6%95%B8%E5%85%A8%E6%9B%B8/%E5%8D%B7%E4%BA%8C>.
It contains directly computable material, including:

- life and body palace placement from lunar birth month and double-hour;
- an explicit rule treating an intercalary month as the following month for
  this construction;
- reverse ordering of the twelve topical palaces;
- year-stem rules used to establish the five-phase bureau;
- placement sequences for the Purple Star and Northern/Southern Dipper stars;
- auxiliary stars placed from birth hour, month, day, year stem or year branch;
- Four Transformations keyed by birth-year stem;
- direction rules depending on yin/yang year and historical sex category;
- twelve-stage cycle placement; and
- annual and decade-related placements.

This is a machine-readable public-domain transcription, not yet a controlling
edition. Its base scan, collation history, transcription accuracy and relation
to `全集` or other printings are not established on the page. Every promoted
table must be checked character by character against a dated facsimile.

## Homonymous Daoist-canon text

The Chinese Text Project catalog record at
<https://ctext.org/library.pl?if=en&remap=gb&res=85160> maps a three-juan
`紫微斗數` in the *Zhengtong Daozang* facsimile, volumes 1114-1115. Its separate
wiki description at
<https://ctext.org/wiki.pl?if=gb&remap=gb&res=979714> explicitly warns that
this text differs from the modern Zi Wei Dou Shu system in its star names and
chart construction.

The CTCW transcription endpoint for the Daoist work's second juan timed out
during this audit. Even after access succeeds, it belongs under a separately
named Daoist star-astrology track. Similar title does not authorize a cross-text
rule merge.

## Required calculation configuration

Every result must carry a configuration fingerprint containing:

- source work, edition, printing and table revision;
- civil-to-lunisolar calendar version and location/timezone basis;
- lunar leap-month convention;
- day boundary and double-hour boundary;
- treatment of births near New Moon, solar-term and midnight boundaries;
- life/body palace algorithm;
- five-phase bureau and Na Yin table version;
- main-star and every enabled auxiliary-star placement table;
- Four Transformations table;
- temple/exaltation/prosperity/fallen brightness table;
- historical sex/gender direction convention and safe modern input mapping;
- decade, annual, monthly and finer timing methods; and
- interpretation school and precedence version.

No `ziwei_default` configuration is allowed. If a source does not specify a
table or boundary, the output is `unknown`, not an imported modern convention.

## Rule architecture

Chart construction and judgment are separate stages:

1. **Calendar facts**: source calendar date, leap status, stem-branch year and
   double-hour.
2. **Palace facts**: branch positions of life, body and the twelve topics.
3. **Bureau facts**: five-phase bureau and associated cycle information.
4. **Star facts**: each placement with its input dependency and source passage.
5. **Transformation/brightness facts**: table lookup with version identity.
6. **Relational facts**: same palace, opposition, trines and named combinations.
7. **Timing facts**: decade/annual/other activated palaces and stars.
8. **Judgments**: source-scoped conditional rules with precedence, mitigation
   and contradiction traces.

This prevents a prose model from moving a star, choosing a transformation
table, or combining two schools. It also makes disagreement testable: two
configurations can share the same birth fact and produce explicitly different
charts without either overwriting the other.

## Variant register opened by the sources

The current evidence already exposes issues requiring adjudication:

- leap months may be treated differently across later schools;
- the complete auxiliary-star set is not fixed;
- Four Transformation tables vary in later transmission;
- brightness/dignity tables vary;
- annual, monthly and finer-limit methods are not uniform;
- exact birth-hour rectification claims are interpretive rather than a license
  to alter reported input; and
- Vietnamese construction and timing cannot be assumed identical to a Chinese
  source.

Each disagreement becomes a versioned table or rule pack with evidence. A
popularity vote among websites is not adjudication.

## Birth-input capability map

| Technique family | Can one birth record drive it? | Current disposition |
|---|---|---|
| Source-scoped natal chart construction | Yes | Feasible pilot after facsimile collation |
| Main and auxiliary star placement | Yes, when each table is identified | Partial transcription evidence; not production-ready |
| Palace/star/combinational interpretation | Yes | `source_limited` pending rule extraction and Chinese review |
| Decade and annual timing | Birth plus target date | Source-scoped; boundary and direction tests required |
| Rectification | Needs independent life evidence and consent | Never silently changes reported birth data |
| Vietnamese Tử Vi | Yes in principle | Separate Vietnamese audit and source pack |
| Daoist-canon homonym | Not assumed to be the same natal method | Separate research track |

## First valid pilot

1. Acquire a dated facsimile of the same `全書` lineage and identify its
   title page, preface, colophon, printer and juan order.
2. Collate the entire construction section against the Wikisource text.
3. Encode only chart-construction tables; interpretation remains disabled.
4. Hand-calculate at least ten published charts from the same edition or
   lineage.
5. Include leap-month births, every double-hour boundary, New Moon boundaries,
   all five bureaus and all ten birth-year stems.
6. Independently implement the calculator twice or compare against a fully
   documented manual calculation.
7. Emit a complete fact trace showing the passage and table cell responsible
   for every palace, star and transformation.
8. Only then begin atomic interpretation-rule extraction from juan 1-3.

## Interpretation extraction requirements

Each atomic rule must identify:

- exact Chinese text and normalized transcription;
- source work, edition, juan, section and page/folio;
- translator and independent Chinese review;
- required palace, star, brightness, combination and timing conditions;
- whether the statement is natal, time-activated or limited to a historical
  social category;
- mitigation, cancellation and conflicting passages; and
- a customer-safe rendering or an explicit suppression reason.

Star keywords without configuration and relational context are insufficient.
The engine must not turn a list of isolated star meanings into a reading.

## Safety and dignity limits

The transcribed work includes severe judgments about death, illness, poverty,
children, marriage and historically gendered status. These are retained only
as cited historical evidence. They cannot become medical diagnosis, lifespan
prediction, reproductive prediction, financial advice, misogynistic output or
claims about a third party's private life. Historical sex-direction tables must
be documented without forcing a modern user into an unsupported identity
claim; ambiguous mappings must be disclosed or the affected timing layer
omitted.

The seven current grade-D construction candidates now have eleven vectors.
The added cases expand the complete Five Tigers year-stem lookup and the full
reverse twelve-topic-palace order from a Zi life palace, while explicitly
keeping implementation disabled until facsimile and Chinese-character
collation. These are transcription tests, not accepted golden charts.

## Failure conditions

The track remains `source_limited` if:

- the Daoist-canon homonym is merged with the later natal system;
- Wikisource is treated as a verified facsimile edition;
- `全書`, `全集`, `捷覽` or later schools are blended;
- Chinese rules are relabeled Vietnamese;
- star count, leap-month, brightness, transformation or timing variants are
  hidden;
- interpretation begins before deterministic chart construction passes golden
  vectors;
- no Chinese-language reviewer approves the passage table; or
- the interface implies a live Zi Wei reading while only Western is live.


---

# Addendum, 2026-08-04: the rest of the Quanshu

Status change: still `source_limited` for reading, but the construction ceiling asserted
above was **wrong**, and the error was one of scope rather than of judgment.

## What the earlier audit missed

The 2026-07-31 audit inspected one Wikisource page — juan 2 — and correctly listed what it
saw, including "year-stem rules used to establish the five-phase bureau" and "placement
sequences for the Purple Star and Northern/Southern Dipper stars". Seven rules were then
extracted, and the engine built on them described its own output as "an empty board": no
bureau, no Zi Wei, no main stars, no brightness.

Both statements cannot be true, and the audit's was the accurate one. The tables were on
the page the whole time. They are not printed as prose — the bureau day-tables and the
brightness table are ASCII-art grids inside `<nowiki>` blocks, and the Tian Fu rule is a
captioned diagram — so a prose-oriented pass over the same URL reads straight past them.

Every juan has now been retrieved as raw wikitext, hash-pinned with its revision id, and
recorded in `sources/access_manifest.json`.

| Juan | Bytes | Revision | What it carries |
|---|---|---|---|
| toc | 3,091 | 850736 | Three-juan arrangement and section list |
| 1 | 67,683 | 2665454 | Rhapsodies; the 37-star question-and-answer chapter; the two marrow rhapsodies; well-placed and broken configuration verses; named wealth/rank/poverty configurations |
| 2 | 106,736 | 1963110 | The whole construction chapter, then the twelve topic-palace delineation chapters |
| 3 | 36,720 | 2268626 | Order of judgment; limit precedence; Dipper split of a limit's halves; birth-hour caution; hidden-merit cancellation |

## The bureau gate, opened

The five-phase bureau is not a printed 10x12 grid anywhere. It is a **composition of two
tables that are printed**, and the chapter performs the composition itself, once, in its
opening paragraph:

> 如甲生人安命在寅却起甲己之年丙为首，是丙寅丁卯炉中火，却去火局寻某日生期起紫微帝王

A Jia-year birth with the life palace at Yin: the Five Tigers couplet 甲己之岁起丙寅 puts
丙 at Yin, so the palace is 丙寅; the sixty-jiazi nayin song gives 丙寅丁卯炉中火, furnace
fire; fire is the six bureau; and the birth day is then looked up in the fire table to
place Zi Wei. The nayin song is printed in full immediately after the Five Tigers couplets
— sixty pairs in thirty couplets, with no gap.

The earlier pack held the Five Tigers table and forbade its use "until Chinese characters
and pairings are collated". The characters are now recorded, and the chapter's own worked
example exercises the Jia/Ji row end to end **inside the source**. The prohibition is
narrowed rather than lifted: the table computes, and must always be shown with its
derivation.

## The Zi Wei day tables, and a rule recovered from them

Five verses and five twelve-palace day grids are printed, one per bureau. They are not
restatements of a formula the text supplies — the text supplies no formula. A closed form
was therefore derived from them:

> Let n be the bureau number and d the lunar day. Take k = ceil(d/n) and c = n·k − d.
> Begin at Yin advanced by (k−1) palaces. If c is odd, retreat c palaces; if c is even,
> advance c.

Machine collation of that expression against all sixty printed cells, and against the ten
day-one and day-two anchors the five verses state in words:

| Bureau | Printed cells reproduced | Verse anchors reproduced |
|---|---|---|
| 水二局 | 12 / 12 | 2 / 2 |
| 木三局 | 11 / 12 | 2 / 2 |
| 金四局 | 11 / 12 | 2 / 2 |
| 土五局 | 12 / 12 | 2 / 2 |
| 火六局 | 12 / 12 | 2 / 2 |

**58 of 60, and 10 of 10.** The two failures are isolated and both are self-revealing,
because a bureau grid must partition the thirty days exactly once:

- 木三局 at Yin prints 初三 初九. But 初九 already stands in the Chen cell and 初五 stands
  nowhere at all. The printed 九 is a graphic slip for 五.
- 金四局 at Hai prints only 初一, leaving the grid at 29 days. The missing day is 三十.

Two further defects were found and repaired the same way, in the nayin song: 甲戊乙亥 for
甲戌乙亥 (戊 is a stem and can never be a branch) and 戊戌已亥 for 戊戌己亥 (已 is not a
stem). Both repairs are forced by the closed sexagenary cycle, not chosen.

This is why the construction rules in the new pack carry evidence grade **C** rather than
the earlier uniform D. C here means something narrow and checkable: *the transcription
checks itself, so a transcription error in these tables is detectable rather than silent*.
It does not mean collated, and it does not mean reviewed.

## All fourteen main stars

`安南北斗诸星诀` is two couplets. The first counts six stars backward from Zi Wei; the
second counts eight forward from Tian Fu; and Tian Fu itself is fixed by the captioned
`安天府图` as the reflection of Zi Wei in the Yin–Shen axis, with the caption's own worked
case 如紫居丑则府居卯. Six plus eight is fourteen. The first couplet also closes its own
circle — 空三复见紫微郎, and the skips do sum to twelve — which is what fixes 隔 and 空 as
exclusive skips rather than inclusive counts.

## The brightness table

`廟旺得地利益平和不得地落陷`, seven columns against twelve branches, printed as a grid.
Machine parse: **twelve rows, twenty stars in each, 240 cells, no repetition.** The single
star absent from each row is always the one that structurally cannot occupy it — Lu Cun
never in the four tomb branches, Qing Yang never in Yin/Si/Shen/Hai, Tuo Luo never in
Zi/Mao/Wu/You — which matches this same chapter's placement rules for those three stars
exactly. The table is complete, and its completeness is checkable without any outside
witness.

## A dated facsimile now exists

The earlier audit's first pilot step was "acquire a dated facsimile of the same lineage".
One has been located and hash-pinned:

**新鋟希夷陳先生紫微斗數全書**, seven juan; 宋·陳摶撰, 明·潘希尹補, 楊一宇恭閲,
書林葆和堂葉梓行; **明代南陽堂刊本**, catalogued 1600. Internet Archive item
`20260506_20260506_1217`, 266 leaves at 300 ppi.

Three consequences:

1. The blanket statement "base facsimile unidentified" no longer holds. A named, dated,
   publicly retrievable printing of this lineage exists.
2. Its Tesseract `chi_sim` OCR layer is unusable — vertical woodblock Chinese defeats it
   the way blackletter tables defeated both Lilly OCR layers. The remedy is the same one
   that worked there: **page photographs**, retrievable individually at
   `https://archive.org/download/20260506_20260506_1217/page/n{leaf}_w1200.jpg`. One page
   was fetched and confirmed legible; locating the construction chapter among 266 leaves
   is the outstanding work.
3. The Ming printing is in **seven** juan; the Wikisource text is in three. The two
   witnesses are differently divided, not merely differently printed, and any collation
   must map sections rather than juan numbers.

## Searches run, and what they returned

| Query | Route | Result |
|---|---|---|
| 紫微斗數全書 page tree | `zh.wikisource.org` `action=raw` on the title and all three juan | All four pages retrieved, revisions pinned |
| 紫微斗數全書 明刊本 / 善本 / 掃描 | WebSearch | Led to 書格 and to the Internet Archive items |
| 紫微斗数全书 續道藏 / 古本 / 故宮珍本叢刊 | WebSearch | Identified the Nanyangtang printing and the 1607 萬曆續道藏 witness of the *homonym* |
| shuge.org Nanyangtang record | Direct HTTPS | **403 Forbidden**, both via fetch tool and via curl with a browser user agent |
| `紫微斗数全书`, `紫微斗數全書`, `紫微斗数`, `title:(紫微)` | Internet Archive advancedsearch API | Four searches; the Nanyangtang facsimile surfaced only on the fourth, catalogued under a Vietnamese romanised title |
| Item file list and derivatives | Internet Archive metadata API | 853 MB image PDF, 432 MB JP2 zip, 143 KB DjVu text, hOCR, page index — the text derivatives were taken, the images were not |

Not obtained: the 書格 record (403); the 故宮珍本叢刊 reprint; any HathiTrust copy; and the
Daozang homonym's CTCW transcription, which is still not needed and still quarantined.

## What is now encoded

`quanshu_full_rule_manifest.json` and `quanshu_full_validation_vectors.json`, pack id
`ziwei_quanshu_full_three_juan_wikisource_v1`: **83 rules, 100 vectors**, 46 rules at grade
C and 37 at D, roughly **28,500 Han characters quoted verbatim**, and **193 delineation
cells refused** by per-cell policy.

The seven-rule `calculation_rule_manifest.json` is left untouched and unsuperseded. It is a
different, narrower pack and the two coexist; the new pack re-states the Five Tigers rule
under its own id with the characters recorded, and says so in the rule.

## What is still true from the original audit

Everything about lineage hygiene. The Daozang homonym is still a homonym. `全書`, `全集`
and `捷覽` are still separate witnesses. Vietnamese Tử Vi is still a separate track. No
school blend is authorised by anything above. And no customer Zi Wei reading is authorised:
the delineation cells are research evidence with per-cell output policy, not a product.

## Revised first pilot

Steps 1 and 2 of the original pilot are now partly done and partly redirected:

1. ~~Acquire a dated facsimile~~ — **done**; collate against its page images, starting with
   the two defective grid cells.
2. ~~Collate the construction section against Wikisource~~ — the transcription has been
   collated **against itself**; against the facsimile it has not.
3. Hand-calculate published charts from the same lineage — still open, and still the real
   worked-example gap: this work prints no dated nativity.
4. Independent Chinese review of all 83 rules — still open, and now much larger.
5. A declared historical sex convention — still the blocker on every limit rule, on the
   twelve-stage cycle, on the twelve gods, and on the decade and small limits.

## Facsimile spot collation, leaf n100

One page image was taken from the Nanyangtang scan and read directly, both to confirm the
route works and to test the transcription against the print.

**It works.** Leaf n100 renders as a fully legible two-page woodblock opening at 1400 px
width — column rules, the 歌 / 曰 / 又 verse headers, individual characters and even a later
hand's marginal annotations all read cleanly. The OCR layer for the same leaf is noise.
This is the Lilly remedy applied to a Chinese witness, and it holds.

The leaf carries the **太陰 entry of the life-palace chapter**: the tail of its palace
couplets, then all three of its verse blocks. That is a navigational finding in itself —
the construction chapter lies at a *lower* leaf number in this seven-juan arrangement, so
the next pass should search roughly leaves 1–100 of 266 for the bureau grids.

Five candidate variants against the Wikisource transcription came out of that one leaf:

| Passage | Facsimile | Wikisource | Assessment |
|---|---|---|---|
| 太陰 palace couplets, Wu/Wei/Shen | 丁庚甲生人財官格 | 丁庚甲**入**生人财官格 | Spurious 入 in the transcription |
| 入男命訣, verse 2 close | 列朝**紳** | 列朝**纲** | Real variant, both sensible |
| 入男命訣, verse 4 open | **太陽**陷地惡星**沖** | **太阴**陷地恶星**中** | Runs the other way: the verse is in the Tai Yin chapter, so the *print* looks wrong here |
| 入女命訣, verse 2 | 尅害夫君**壽又夭** | 克害夫君**又夭寿** | Word order |
| 入限訣, verse 2 open | **添進財產**福非輕 | **添屋进财**福非轻 | Real variant |

One leaf, five variants. The transcription is close to this printing and demonstrably not
identical to it. That is the whole argument for collation rather than trust — and it is why
the two defective bureau cells found by self-collation (木三局 at Yin, 金四局 at Hai) should
be *re-read from the print* rather than silently patched from the closed form.

These readings are candidates, not settled: they come from a single 1400-pixel render and
each should be re-checked at full JP2 resolution before it changes an encoded cell.
