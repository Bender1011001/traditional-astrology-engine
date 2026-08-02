# Japanese Sukuyōdō defensibility spec

Status: governing spec for the Sukuyōdō section — research stage, nothing shipped
Updated: 2026-08-02
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

**Sukuyōdō (宿曜道) is not Onmyōdō.** The repository's separate [`onmyodo/`](../onmyodo/source_audit.md)
track covers the yin-yang and five-phase court tradition of the Onmyōryō — sexagenary
reckoning, the shikiban board, directional taboos. Sukuyōdō is the Buddhist astral
tradition transmitted through Chinese Buddhist translation from Indian and Iranian
material: 27 lunar mansions, 12 zodiacal signs, 7 planetary weekdays. The core text
documents its own transmission in its own words — it tells the reader that if he forgets
which weekday it is, he should ask a Sogdian, a Persian, or a person of the Five Indias,
and it prints the Sogdian, Persian and Sanskrit names for each planet. In Japan the two
were separate offices with separate practitioners who competed for calendrical authority.
The two tracks share no source, no rule and no vector, and this spec refuses any reading
that presents them as one system.

## What this tradition actually does

A Sukuyōdō reading is **mansion-relational and calendrical**. It is not psychological.

The subject's birth mansion (本命宿) is the anchor, and almost everything else is a
*relation* to it: the three-nine table (三九之法) sorts all 27 mansions into nine
categories relative to the birth mansion, and those categories then answer two kinds of
question — *is this person fit to associate with*, and *is today a day to act*. A planet
striking a mansion is judged by which category that mansion holds for you, which is why
the same transit is good news for one person and bad news for another.

The reading the sources support therefore looks like this:

> Your birth mansion is X. Here is where every other mansion stands relative to it.
> Here is what the text says to do and not do on each of those days, in its own words,
> with its contradictions left in. Here is why we cannot yet tell you which mansion is
> yours for a modern birth date.

Forcing this into a Western shape — twelve houses, a personality narrative, a
psychological arc — would be a category error. The text's own natal clauses are
status- and office-shaped (*fit to hold the office of the treasury*, *fit to hold the
office of the stables*), not character-shaped.

## Core-technique checklist

Statuses are as the standard defines them. **Nothing here is `implemented`**: no engine
module exists for this tradition, and this pass created the source foundation only.
Nothing is `computable` either, and that is not a formality — see "Why nothing is
`computable`" below.

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Birth mansion 本命宿 from a real birth date | T1299 卷下 T21.0394c28-0395a03 and T21.0395b01-b06 give the full procedure and its abbreviated cross-check | `source_gated` — the procedure needs a lunar month and day in the source's own scheme and the text supplies no conversion from any civil calendar |
| 2 | The 27-mansion operative cycle and its canonical order | four independent statements in T1299 plus the pāda arithmetic and the printed worked example | `source_gated` — extracted and internally cross-checked four ways; promotion needs an independent Classical Chinese reader and CBETA rights clearance |
| 3 | Three-nine relationship table 命 業 胎 plus 栄 衰 安 危 成 壊 友 親 | T1299 卷上 三九祕宿品第三 and 卷下 三必祕要法, two independent statements of the same table | `source_gated` — the table is complete and reproduces the text's own worked example; same review gate as row 2 |
| 4 | Bidirectional evaluation of a pair of birth mansions | T1299 T21.0391b14-b16 requires both directions | `source_gated` — same review gate; the asymmetry is proven by vector |
| 5 | Association judgment 結交 from the favourable set | T1299 T21.0391b16-b17 名 榮 安 成 友 親 as 善 | `source_gated` — same review gate; the text's own hedge 大抵 must survive |
| 6 | Day election by the subject's personal three-nine category | T1299 T21.0391b19-b25 and T21.0397c25-0398a13 | `source_gated` — every day judgment is relative to the birth mansion, so this inherits row 1's calendar block |
| 7 | Precedence of the personal three-nine over the general almanac | T1299 T21.0398a14-a15 states the hierarchy explicitly | `source_gated` — inherits rows 1 and 6 |
| 8 | Planetary affliction of the natal mansion with category inversion | T1299 T21.0391b26-c03 and T21.0398a18-a25 | `source_gated` — the text outsources planetary positions 當須問知司天者 and the companion ephemeris T1308 is transcribed as unusable grid text |
| 9 | Seven weekday luminaries and the natal clause attached to each | T1299 卷上 七曜直日品第四 | `source_gated` — the text gives the cycle but no epoch; a weekday for a historical date needs a named calendar authority |
| 10 | Weekday-mansion combination classes 甘露日 金剛峯日 羅剎日 | T1299 T21.0398b21-c07 | `source_gated` — two of the twenty-one printed pairs read 冒 and 底, which are not mansion names; a facsimile or second witness is needed |
| 11 | Twelve 宮 placement and the natal clause attached to each | T1299 卷上 T21.0387b14-0388a04 with the pāda allotment | `source_gated` — placing a birth in a sign needs a solar position and a named zodiac frame that the text never states |
| 12 | Mansion on duty from an observed lunar position | T1299 T21.0388b24-c06 and T21.0395b09-b21 give the three conjunction classes | `source_gated` — the text says the mansions are unequal in width and instructs the reader to verify against the sky, but tabulates neither the widths nor an ephemeris |
| 13 | The Japanese practice layer as distinct from the Chinese text | none retrieved | `source_gated` — needs 宿曜占文抄 or a dated Sukuyōdō kanmon; see the access manifest for the named targets |
| 14 | Psychological or narrative natal reading | — | `refused` — the corpus contains no such genre |
| 15 | Lifespan, illness, appearance and kin-harm claims | T1299 states several 短命, 醜陋 and 妨親害族 clauses | `refused` for customer output; recorded as source text only |
| 16 | Ritual and apotropaic prescriptions as instruction | T1299 prescribes 灌頂 護摩 真言 道場 | `refused` — recorded as liturgical content of an initiatory tradition, never issued as advice |
| 17 | Resolution of the text's internal contradictions | T1299 contradicts itself on the 業 day and on marriage on a 危 day | `refused` — both readings are emitted or neither is; the pack will not choose |
| 18 | Merger with Onmyōdō, with T1308, or with T1311 | three different schemes | `refused` — see the two boundary rules in the manifest |

### Why nothing is `computable`

`computable` means "the inputs exist and the remaining work is ours." That is not the
situation here, and saying it would be false in a way that matters:

The whole apparatus is anchored on the birth mansion, and **the birth mansion cannot be
computed for any real person from this corpus.** T1299 derives it from the lunar day of
an Indian-style lunar month whose full-moon mansion names the month. It gives that
procedure twice, in a primary and an abbreviated form that this pack proved algebraically
identical across all 810 month-day cases. What it never gives is a way to get from a
civil date to that lunar day. Japanese sukuyōshi got it from the calendar the court
issued; that calendar regime is not in the retrieved corpus and is not in this
repository. Rows 1, 6, 7 and 8 all sit behind that one missing document, and rows 2 to 5
are behind the review gate the standard itself imposes on rule promotion.

**Read the ceiling report for this track carefully.** "At ceiling" here means *no work on
this checklist is currently unblocked*. It does not mean the reading is complete — the
reading does not exist yet.

## Judgment hierarchy

The text states its own precedence, which is unusual and worth taking literally.

1. **Establish the birth mansion first.** Everything else is defined relative to it.
   Until it is fixed, nothing downstream may be emitted at all.
2. **Compute the three-nine category** of whatever is being judged — the other person's
   mansion, today's mansion, the mansion a planet occupies. The category, not the
   mansion, is what carries the judgment.
3. **The personal three-nine outranks the general almanac.** T21.0398a14-a15:
   *even if the general almanac shows no auspicious aspect, if one's own three-nine is
   auspicious, one may act without harm.* A composer that lists the personal reading and
   the almanac reading as parallel bullets has flattened a hierarchy the source orders.
4. **Apply the day-election clauses** for that category, preserving the fork between the
   chapter 3 and 三必祕要法 statements wherever they disagree.
5. **Only then the planetary layer**, and only with its inversion intact: affliction of a
   favourable-category mansion obstructs, affliction of an unfavourable-category mansion
   helps.
6. **The weekday layer is independent** and combines with the mansion only where the text
   pairs them explicitly, in the three combination classes.

The 12-sign layer is a separate frame in chapter 1 and does not feed the three-nine
system at all. Do not blend them.

## Worked-example inventory

| Source | Contains | Usable now |
|---|---|---|
| T1299 卷下 三必祕要法, T21.0397c02-c06 | the three nines printed in full for a subject whose birth mansion is 畢 — 27 named mansions in three groups of nine | **yes, and it passes.** Rotating the canonical order by index(畢) reproduces all 27 entries in the printed sequence exactly. Vector `sukuyo.v.sanku_worked_example_from_bi` |
| T1299 卷上 T21.0387b14-0388a04 | the twelve signs with their pāda allotments | **yes.** The arithmetic closes at 12 × 9 = 108 = 27 × 4 with zero pāda to 牛. Vector `sukuyo.v.pada_allotment_closes` |
| T1299 卷下 T21.0394c20-c28 | the twelve months named by their full-moon mansion | **yes.** The twelve steps sum to exactly 27. Vector `sukuyo.v.month_full_moon_table_closes` |
| T1299 卷下 T21.0394c28-0395b06 | the primary and abbreviated birth-mansion procedures | **yes as a self-consistency proof** — exhaustively identical over 810 cases. Not usable as a real-birth example, because no dated worked nativity survives in the text |
| T1299 卷上 T21.0388b26-c03 | the three lunar-conjunction classes | **yes.** 6 + 12 + 9 = 27, disjoint and exhaustive, 牛 in none |
| A dated Sukuyōdō consultation with a named subject | — | **no such example is in the retrieved corpus.** This is the tradition's real worked-example gap and it lives in the Japanese kanmon record, not the Chinese text |

The 畢-rooted enumeration is the strongest asset this track has. It is the tradition's
own worked example of its own central technique, and the engine's table reproduces it
character for character. That is not a coincidence that can be waved away: a wrong
mansion order or a wrong triad offset would break it immediately.

## Refusal list

- **No birth mansion for a modern date.** T1299 supplies the procedure and no calendar
  conversion. Substituting a Gregorian day-of-year modulo 27, a modern almanac, or a
  Jyotisha nakṣatra computed from a modern ephemeris is forbidden. The Jyotisha
  substitution is the specifically tempting one and it is wrong twice over: it is a
  different derivation and it would silently reintroduce the 28th mansion.
- **No merger with Onmyōdō.** Different corpus, different units, different institution,
  different practitioners. This is the disambiguation the whole track exists to hold.
- **No merger with the 28-mansion texts.** T1308 summons twenty-eight mansion deities and
  defines 命宿 as where the Sun and Moon stand at birth; T1311 runs a nine-luminary age
  cycle. Both are registered as contrast witnesses. Neither may supply a mansion count,
  a birth mansion, or a delineation to the T1299 pack.
- **No resolution of the text's contradictions.** Chapter 3 says everything done on a 業
  day is auspicious; 三必祕要法 says nothing done on it comes to fruition. 三必祕要法
  recommends marriage on a 危 day and, seven lines later, calls marriage on a 危 day
  inauspicious. Both readings ship with their locations, or neither does.
- **No lifespan, illness, appearance or kin-harm output.** The text states 短命 for
  people born under the Sun's day, under Venus's day, and in 蟹宮; 醜陋惡性、妨親害族 for
  Mars's day. These are recorded as what the source says and are never rendered as a
  claim about a reader.
- **No ritual instruction.** The remedial prescriptions — abhiṣeka, homa, mantra
  recitation, establishing a ritual site — belong to an initiatory Buddhist tradition.
  They are quoted as source content in historical context and are never issued as
  something to do.
- **No psychological narrative.** The tradition does not have one. A section that
  invented one would fail the standard's third test on the first sentence.

## Conventions requiring disclosure

| Convention | Chosen | Note |
|---|---|---|
| Mansion count | 27, per T1299's own four statements | the 28-fold list exists in the same text's figure catalogue and is disclosed, not hidden |
| Mansion order origin | 昴 first, per chapter 2 and the almanac | this is the Indian nakṣatra order, not the Chinese lodge order beginning 角; the choice is the text's, not ours |
| 牛 handling | catalogued, never operative | its natal clause is quotable; it is unreachable by any computation |
| Text and edition | CBETA TEI P5 of Taishō vol. 21, hash-pinned | not a facsimile; character-level doubts at the 羅剎日 rows are unresolved |
| Translation status | single unreviewed engine rendering | Chinese quoted verbatim beside every rendering in `extraction_notes.md`, so a specialist can check the rendering against the original |
| Rights | CBETA non-commercial condition, header retained | **not** assumed public domain; customer-facing reproduction needs rights review |
| Sanskrit nakṣatra equivalences | engine-supplied, cross-checked against the month table | informational only in `extraction_notes.md`; **no rule depends on them** |
| Western sign labels | engine-supplied gloss | T1299 names signs by figure (獅子, 秤, 蝎, 磨竭, 瓶, 魚); no rule depends on the Western label |
| Calendar regime | **none chosen** | deliberately absent; the pack fails closed rather than pick one |

## Current implementation gap

The gap is total and should be stated plainly: **there is no Sukuyōdō engine module, no
composer section, and no rendered output.** This pass built the source foundation —
three hash-pinned Taishō witnesses, 32 rules, 42 vectors, and the boundary rules that
keep the track separate from Onmyōdō and from the 28-mansion texts.

What would move it, in order of leverage:

1. **A named lunisolar calendar regime.** This single acquisition unblocks rows 1, 6, 7
   and 8 — most of the reading. Until it lands, the honest product is the relational
   table and the refusal, in the shape the Nahua track already ships: *here is the whole
   system, in the text's words, and here is why we cannot place you in it.*
2. **Independent Classical Chinese review** of the 32 encoded passages, plus a second
   encoder reproducing the extraction without seeing this pack. That lifts rows 2 to 5,
   which are the mansion-relational core and the most immediately implementable material
   in the tradition.
3. **A Taishō facsimile** for the two corrupt 羅剎日 characters and for T1308's grid
   tables.
4. **The Japanese layer** — 宿曜占文抄 or a dated kanmon — which is what would let this
   track claim to be Sukuyōdō rather than a careful reading of the Chinese text that
   Sukuyōdō read.

Note that item 1 is a document problem and item 2 is a review problem. Neither is a
composer problem, which is why the checklist carries no `computable` row.
