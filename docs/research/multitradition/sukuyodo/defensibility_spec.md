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
| 1 | Birth mansion 本命宿 from a real birth date | T1299 卷下 T21.0394c28-0395a03 and T21.0395b01-b06 give the full procedure and its abbreviated cross-check; Kotyk 2018 names the regime | `source_gated` — **the gate moved on 2026-08-04 and did not open.** The regime is now named, dated and authored: the 符天暦 Futian li of Cao Shiwei (780-783, updated c. 806, epoch 660), "used by the Sukuyōshi through the Heian and Kamakura periods", with the 宣明暦 Senmyō reki (adopted 862) as the state calendar alongside. What is still absent is the Futian li's tables — it is a lost calendar reconstructed from citation and from the elapsed-day counts in two surviving horoscopes. Named regime, unretrieved parameters |
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
| 13 | The Japanese practice layer as distinct from the Chinese text | Kotyk 2018, hash-pinned and read; 13 rules extracted | `source_gated` — **partially lifted 2026-08-04.** The layer is no longer empty: the calendar regimes, the 961 arbitration, the emergence window, and the shape of a real Japanese horoscope are now encoded. It stays gated because every one of those rests on a single secondary reading; the primary Japanese documents (宿曜占文抄, the *Ono ruihi shō* and *Asaba shō* reports, a dated kanmon) are still unretrieved |
| 14 | Psychological or narrative natal reading | — | `refused` — the corpus contains no such genre |
| 15 | Lifespan, illness, appearance and kin-harm claims | T1299 states several 短命, 醜陋 and 妨親害族 clauses | `refused` for customer output; recorded as source text only |
| 16 | Ritual and apotropaic prescriptions as instruction | T1299 prescribes 灌頂 護摩 真言 道場 | `refused` — recorded as liturgical content of an initiatory tradition, never issued as advice |
| 17 | Resolution of the text's internal contradictions | T1299 contradicts itself on the 業 day and on marriage on a 危 day | `refused` — both readings are emitted or neither is; the pack will not choose |
| 18 | Merger with Onmyōdō, with T1308, or with T1311 | three different schemes | `refused` — see the two boundary rules in the manifest |
| 19 | The observational birth mansion, from the Moon's actual position at birth | Kotyk 2018 on the 961 arbitration; the 759 recension's statement, quoted there, that the corresponding mansion is always the one the Moon occupies | `source_gated` — this is the branch the tradition's own arbitration **upheld** over the table, and which Kotyk reports became standard. It needs a lunar longitude plus a named 27-mansion boundary scheme, and T1299 explicitly declines to tabulate the boundaries, saying only that the mansions are wide and narrow |
| 20 | The twelve-place layer of an actual Japanese horoscope | the 1113 *Sukuyō unmei kanroku* and the c. 1312 *Sukuyō go unroku*, via Kotyk 2018 | `source_gated` — the twelve place names are recorded; not one delineation attached to a place has been read, because neither document was retrieved |
| 21 | Reading the Japanese recension rather than the Taishō mainland recension | Yano 2013 via Kotyk 2018; *Sukuyōkyō shukusatsu*, ed. Wakita Bunshō, 1897 | `source_gated` — the 1897 typeset edition is named and not acquired. Until it is collated against T1299, no rule here may be called "what sukuyōshi used" |

### Why nothing is `computable`

`computable` means "the inputs exist and the remaining work is ours." That is not the
situation here, and saying it would be false in a way that matters:

The whole apparatus is anchored on the birth mansion, and **the birth mansion cannot be
computed for any real person from this corpus.** T1299 derives it from the lunar day of
an Indian-style lunar month whose full-moon mansion names the month. It gives that
procedure twice, in a primary and an abbreviated form that this pack proved algebraically
identical across all 810 month-day cases. What it never gives is a way to get from a
civil date to that lunar day. Rows 1, 6, 7 and 8 all sit behind that, and rows 2 to 5 are
behind the review gate the standard itself imposes on rule promotion.

**Updated 2026-08-04, because the previous version of this paragraph overstated the
block.** It read: *Japanese sukuyōshi got it from the calendar the court issued; that
calendar regime is not in the retrieved corpus and is not in this repository.* The second
clause is still true. The first was vague in a way that hid an answerable question, and
the answer had been sitting in the same pass's own list of leads.

The regime has a name. Japanese *sukuyōshi* did **not** work in the court's calendar for
this purpose — they worked in the **符天暦 Futian li**, Cao Shiwei's calendar of 780–783
updated around 806, epoch 660, which Kotyk states was "used by the Sukuyōshi through the
Heian and Kamakura periods" and which was in Japan by 891. The court's own calendar, the
**宣明暦 Senmyō reki** (adopted 862), is a second named regime, and the two were in
contact rather than sealed apart: *sukuyōshi* sat in state calendar production from 995
to 1038. The Futian li epoch is confirmed by arithmetic recomputed here, not asserted:
two horoscopes two centuries apart, stating 165,428 and 222,245 elapsed days, resolve to
the same day in February 660.

So the honest statement of the block is now narrower and harder: **the regime is named,
dated and authored; its tables are lost.** That is still `source_gated` and still not
`computable`, because "the inputs exist and the remaining work is ours" is false — a
reconstruction of a lost Tang calendar is not composer work. But the shape of the
acquisition has changed from "find out what they used" to "implement and test a named
calendar," which is a different and much more tractable task.

And one thing did get worse. Rows 1, 6, 7 and 8 were previously understood to be gated on
one document. They are gated on two, because row 19 records that the tradition's own
arbitration preferred the *observational* mansion over the tabulated one. A perfect
implementation of the Futian li would deliver the branch that lost.

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
| The 961 debate over Murakami Tennō's natal mansion, via Kotyk 2018 (journal p. 56, citing *Sukuyōkyō shukusatsu* 1: 13-15) | a dated consultation, a named subject — born 926, lunar 6/2 — and a stated result, 柳 Āśleṣā | **yes, and it passes.** Month 6's full-moon mansion is 女 at index 20; (20 + (2 − 15)) mod 27 = 7; index 7 is 柳. Vector `sukuyo.jp.v.murakami_tenno_natal_mansion`. It is also a cross-recension check: the reported value comes from the Japanese recension, the engine's from the Taishō mainland recension, and they agree |
| The Futian li epoch, from two dated horoscopes | 165,428 elapsed days stated in the 1113 *Sukuyō unmei kanroku*; 222,245 in the c. 1312 *Sukuyō go unroku* | **yes, and it closes.** Both resolve to 15 February 660 Julian, and the difference between the counts carries the first birth date exactly onto the second. Vectors `sukuyo.jp.v.epoch_from_the_1113_horoscope`, `..._1268_horoscope`, `..._daycount_difference_closes` |
| A dated Sukuyōdō consultation whose *full judgement* survives with the chart | — | **still not in the retrieved corpus.** The Murakami case supplies one determination, not a reading. The full documents — the 1113 and 1312 horoscopes — are known only through description |

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
| Calendar regime | **none chosen; two now named** | still deliberately unchosen and still failing closed. The candidate set is 符天暦 Futian li (the sukuyōshi's calendar) and 宣明暦 Senmyō reki (the state calendar). If either is ever implemented, the engine must compute under **both** and refuse on disagreement — `sukuyo.jp.regime_gate_requires_agreement`, labelled `configured_method`, following the `CALENDAR_REGIMES` pattern in `src/engine/multitradition/ziwei.py`. The alternative it rejects, silently picking one, is named |
| Birth-mansion derivation | **fork preserved, unresolved** | schematic table versus the Moon's observed position. The tradition's own 961 arbitration chose observational; this repository has only the schematic branch encoded, and must say so |
| Recension | Taishō mainland recension | **not** the Japanese recension that medieval practice used. Disclosed since 2026-08-04; previously undisclosed because unknown |
| Reading shape | mansion-relational | true of T1299 and **false of Japanese practice**, which used a twelve-place horoscope. Both must be described; neither may be presented as the whole tradition |

## Current implementation gap

The gap is total and should be stated plainly: **there is no Sukuyōdō engine module, no
composer section, and no rendered output.** This pass built the source foundation —
three hash-pinned Taishō witnesses, 32 rules, 42 vectors, and the boundary rules that
keep the track separate from Onmyōdō and from the 28-mansion texts.

The 2026-08-04 pass added a second manifest, `japanese_reception_rule_manifest.json`, with
13 rules and 16 vectors covering the Japanese layer. It is kept separate from the T1299
pack on purpose: one is a Chinese scripture read directly, the other is a modern
specialist's report of Japanese documents nobody here has opened, and collapsing them
would launder grade B into grade A.

What would move it, in order of leverage:

1. ~~**A named lunisolar calendar regime.**~~ **Done — and it was never the acquisition it
   was described as.** The regime is the 符天暦 Futian li, and the replacement task is to
   implement and test a reconstruction of it, alongside the 宣明暦 Senmyō reki, behind the
   agreement gate. Rows 1, 6, 7 and 8 remain gated on that implementation *and* on row 19,
   because the tradition's own arbitration preferred the observational mansion. Until both
   land, the honest product is the relational table and the refusal, in the shape the
   Nahua track already ships: *here is the whole system, in the text's words, and here is
   why we cannot place you in it.*
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
