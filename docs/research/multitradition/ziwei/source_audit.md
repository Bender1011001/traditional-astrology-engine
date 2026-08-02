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
