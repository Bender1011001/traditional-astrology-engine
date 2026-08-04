# Japanese Sukuyōdō (宿曜道) source audit

Status: source foundation established; bounded T1299 rule pack complete; Japanese
reception layer acquired; not production approval
Updated: 2026-08-04

## Correction, 2026-08-04: the calendar block was overstated

The 2026-08-02 pass closed with this sentence: *the text supplies no way to convert a
civil date into the lunar day its birth-mansion procedure requires*, and it called that
an access problem whose missing document was "a calendar." That much is still true. What
was wrong was the next step, taken in the defensibility spec and in the manifest rule
`sukuyo.natal.birth_mansion_requires_lunar_calendar`: that **no named regime was
available**, and that the Japanese-side calendar question was open.

It is not open. It has a name, an author, a date, and an epoch that two surviving
documents independently confirm.

| | |
|---|---|
| Regime | **符天暦 Futian li / Futenreki** |
| Author | 曹士蒍 Cao Shiwei |
| Produced | 780–783 CE, updated around 806 |
| Epoch | 660 CE |
| In Japan by | 891, catalogued as 唐七曜符天暦 in the *Nihonkoku genzai sho mokuroku* |
| Used by | *sukuyōshi*, "through the Heian and Kamakura periods" |

And the state calendar alongside it was the **宣明暦 Senmyō reki**, brought to Japan in
859 and adopted from 862 — the calendar whose staleness Kamo no Yasunori complained of in
the mid-tenth century, prompting the mission that brought a Futian li recension back in
957. *Sukuyōshi* were not sealed off from it: they officially participated in state
calendar production between 995 and 1038, and argued with court calendrical experts about
eclipse prediction into the thirteenth century.

**The epoch is checkable and it checks.** The 1113 horoscope *Sukuyō unmei kanroku* states
that 165,428 days had elapsed since its calendar's epoch. Its subject was born 15 January
1113. Under Julian reckoning that birth is JDN 2127596; less 165,428 days is JDN 1962168,
which is **15 February 660**. The second horoscope, *Sukuyō go unroku*, gives 222,245
days for a subject born in 1268; measured from that same epoch day it lands on 6 August
1268, and a person born then is 44 turning 45 in 1312, which is what that document says.
Two separately transmitted manuscripts, two centuries apart, reckon from one day. That
arithmetic was recomputed here rather than taken on the source's word.

**What is still missing, stated precisely.** The Futian li's own tables. It is a lost
calendar, reconstructed from later citation and from exactly the elapsed-day counts
above. So the block moves from

> no named lunisolar regime exists for this tradition

to

> the regime is named, dated and authored, and its parameters are not retrieved.

The checklist row stays `source_gated`. It does **not** become `computable`, and saying
otherwise would be the opposite error to the one being corrected here.

**Why this is written up rather than quietly patched.** This is the sixth false ceiling
this corpus has retired. The governing rule is that a ceiling is never asserted without a
documented hunt, and the 2026-08-02 statement asserted one — it declared the Japanese
calendar question unanswerable on the strength of a search that had returned catalogue
metadata and stopped. The article that answers it, Kotyk 2018, was **already named in
that pass's own list of recorded-not-used leads**. The lead was written down and not
followed.

## Correction, 2026-08-04: the encoded text is not the text Japanese practice used

Acquired in the same pass and more uncomfortable. Yano 2013 has demonstrated that the
"mainland recension" of the *Xiuyao jing* preserved in the Taishō canon differs
considerably from the "Japanese recension," which traces to the ninth century, which
Kotyk judges best represents the original, and which **was exclusively used in the
medieval period.**

Every one of the 32 rules in `sukuyo_rule_manifest.json` is extracted from the mainland
recension. They are a faithful reading of a text that Japanese *sukuyōshi* did not use in
the form encoded. This is not fatal — the two are recensions of one work, and the single
point where they can be compared here agrees, on which see the worked example below — but
until they are collated, **no rule in this repository may be described as "what Japanese
sukuyōshi used."** The acquisition target is named and is old enough to be tractable:
*Sukuyōkyō shukusatsu* 宿曜経縮刷, 2 vols, the typeset Japanese recension edited by
Wakita Bunshō 脇田文紹, 1897.

## The worked example the track did not have

The 2026-08-02 worked-example inventory recorded, correctly, that no dated Sukuyōdō
consultation with a named subject was in the retrieved corpus, and that this was the
track's real gap. It is no longer.

In **961**, the *sukuyōshi* Hōzō 法蔵 (905–969) and the *onmyōji* Kamo no Yasunori
(917–977) disputed the natal mansion (本命宿) and personal ritual day (本命日) of
**Murakami Tennō** (926–967), born on the **second day of the sixth lunar month** of
Enchō 4. Kamo no Yasunori applied the *Xiuyao jing* table — the schematic procedure this
repository already encoded on 2026-08-02 — and got **柳** (Āśleṣā).

The encoded rules reproduce it exactly. Month 6's full-moon mansion is 女, index 20 in the
canonical order; (20 + (2 − 15)) mod 27 = 7; index 7 is 柳. A wrong entry in either the
month table or the mansion order would have given a different mansion.

Three things make it worth more than a passing check:

1. It is the defensibility standard's requirement 4 satisfied for this track — a dated
   historical consultation, a named subject, a stated result, reproduced.
2. It is a cross-recension check. Kotyk's value comes from the *Japanese* recension
   (*Sukuyōkyō shukusatsu* 1: 13–15); the engine's comes from the Taishō mainland
   recension. They agree at the one point currently comparable.
3. **It reproduces the position that lost.** A third party, Yoshino Nichizō, ruled for
   Hōzō on the mansion — determined from *the nakṣatra in which the Moon was actually
   lodged at birth*, not from the table — and for Kamo no Yasunori on the ritual day.
   Hōzō's basis was the *first*, 759 version of the *Xiuyao jing*, which says the
   corresponding mansion is always the one the Moon occupies. So the tradition's own
   arbitration set the schematic table aside for the natal question, and Kotyk reports
   that the observational method evidently became standard: the 1113 horoscope's lunar
   position is not taken from the table.

That is a method fork of the first order and it is now encoded as one. An implementation
that emitted only the schematic mansion would be emitting the answer this tradition
rejected. It is also, quietly, a warning about the split verdict: the mansion question
went to the Buddhist astrologer and the day question to the yin-yang office, which is
evidence that the two remained distinct competing offices — the boundary rule
`sukuyo.boundary.sukuyodo_is_not_onmyodo` is unaffected, and no Onmyōdō source is admitted
on the strength of it.

## What a Sukuyōdō reading actually looks like — corrected

The 2026-08-02 audit set expectations as *mansion-relational and calendrical*, "close to
the opposite of a Western psychological chart reading," with no houses. That description
is accurate for **T1299**. It is wrong for **Japanese practice**.

The *Sukuyō unmei kanroku* is a concentric horoscope: earthly branches as the twelve
Jupiter stations, the twelve zodiac signs with planetary rulers, nine planets (including
Rāhu and Ketu-as-lunar-apogee) placed against the lunar stations, and an outer ring of
**twelve places** — 壽命 lifespan, 財庫 wealth, 兄弟 brothers, 田宅 estate, 男女 children,
奴僕 slaves, 夫妻 marriage, 疾病 illness, 遷移 travel, 官祿 career, 福德 fortune, 禍害
disaster. Kotyk notes these themes are largely consistent with Hellenistic doctrine,
reaching East Asia through Iranian intermediaries. The planetary values carry fractions
and are more precise than the *Qiyao rangzai jue* ephemerides.

So the tradition Japanese *sukuyōshi* practised had a place doctrine after all, and it is
a distant descendant of the same Hellenistic apparatus the Western report already runs.
No delineation attached to any place has been read, and none is encoded; the correction is
structural only.

## What was added in the 2026-08-04 pass

- one hash-pinned scholarly witness (Kotyk 2018, 50pp PDF and a page-addressed extraction);
- a separate `japanese_reception_rule_manifest.json` with **13 rules** — kept separate
  from the T1299 pack precisely because the Chinese text and the Japanese practice are
  different evidence;
- **16 vectors**, four of them recomputed arithmetic rather than reported claims;
- one new registry source;
- the three corrections above.

## Disambiguation, stated first because everything depends on it

**Sukuyōdō is not Onmyōdō.** The repository already carries an [`onmyodo/`](../onmyodo/source_audit.md)
track. That is the yin-yang and five-phase court tradition administered by the Onmyōryō:
sexagenary reckoning, the `shikiban` divination board, directional deities and travel
taboos, the Kamo and Abe lineages, `Hoki Naiden`, `Ozassho`.

Sukuyōdō is a different tradition with a different corpus, different units, different
practitioners and a different institutional history. It is the Buddhist astral science
that entered Japan through Chinese Buddhist translation of Indian material, with
demonstrable Iranian and Sogdian intermediation. Its units are:

- the **27 lunar mansions** (宿, from the Indian nakṣatra);
- the **12 zodiacal signs** (宮, from the Indian rāśi);
- the **7 planetary weekdays** (七曜);
- and the relations *between* mansions, which is where the tradition's distinctive
  technique lives.

Not one of those is a yin-yang or five-phase unit. The core text carries no sexagenary
stem-and-branch reckoning, no divination board, no directional deity taboo, and no
five-phase generation or conquest sequence. Its remedies are Buddhist tantric ones.

The strongest single piece of evidence is the text's own account of its transmission. In
its weekday chapter it tells the reader that if he cannot remember which day it is, he
should simply ask a Sogdian, a Persian, or a person of the Five Indias, because they all
know — and it then prints a three-column table of Sogdian, Persian and Sanskrit names for
each of the seven planets, and notes that Nirgranthas and Manichaeans keep a fast on
Sunday. A text that documents its own foreign transmission this explicitly is not a
branch of the Japanese yin-yang bureau.

Practical consequence for this repository: **the two tracks share no source, no rule and
no vector.** No Sukuyōdō rule may cite an Onmyōdō source and no Onmyōdō rule may cite a
Sukuyōdō source. This is enforced by the boundary rule
`sukuyo.boundary.sukuyodo_is_not_onmyodo` and its vector.

## Result of this pass

The tradition had nothing in the repository before this pass. It now has:

- three hash-pinned Taishō witnesses, retrieved and read in Classical Chinese;
- a line-addressed rendering of each, keyed to Taishō page, column and line;
- 32 rules with passage citations, all from T1299;
- 42 validation vectors covering every rule, with values computed rather than asserted;
- a governing defensibility spec and this audit;
- five new registry sources including two honest negative results.

The central finding is that **the mansion-relationship system is completely specified in
the text and completely encodable.** It is stated twice, independently, in different
chapters, and the second statement carries a printed worked example that the encoded
table reproduces exactly. That is the highest-value directly implementable material in
the tradition and it is now extracted.

The central blocker is equally clear and is not a language or rights problem: **the text
supplies no way to convert a civil date into the lunar day its birth-mansion procedure
requires.** Under the standard's own table this is an access problem — the missing
document is a calendar, not a translation.

## Source map

| Work | Taishō | Branch supported | Current evidentiary value | Main limitation |
|---|---|---|---|---|
| 宿曜經 *Xiuyao jing / Sukuyōkyō* | T21 no. 1299 | the whole tradition: mansions, signs, weekdays, relations, election | complete text retrieved, hash-pinned, read directly; 32 rules extracted with page/column/line citations; three internal arithmetic checks and one printed worked example all pass | single unreviewed reader; CBETA transcription not collated against a facsimile; no calendar conversion in the text |
| 七曜攘災決 *Qiyao rangzai jue* | T21 no. 1308 | planetary positions and apotropaic procedure | complete text retrieved and hash-pinned; structure and opening read | **28-mansion system with a different 命宿 definition**; its tables are printed as grids and CBETA's linearization of them is unusable as data; nothing encoded |
| 梵天火羅九曜 *Bontenkara kuyō* | T21 no. 1311 | nine-luminary age cycle | complete text retrieved and hash-pinned; opening read | a third scheme again (28 mansions, 九曜 by year of life); registered as a contrast witness only; nothing encoded |
| Japanese practice manuals (宿曜占文抄 etc.) | — | what Japanese sukuyōshi actually did | catalogue metadata only | not retrievable as text; still the Japanese-side manuscript gap |
| Kotyk, "Japanese Buddhist Astrology and Astral Magic," *JJRS* 45/1 (2018) | — | the Japanese reception layer: calendar regimes, the 961 birth-mansion debate, two dated horoscopes, the recension question | retrieved 2026-08-03, hash-pinned, read; 13 rules and 16 vectors extracted; two of its numerical claims recomputed and closing | **secondary scholarship, not a primary Japanese document** — everything from it is grade B, and the primary chain it cites (Momo 1969/1990, Yano 2013, *Ono ruihi shō*, *Asaba shō*) has not been opened |
| *Sukuyōkyō shukusatsu* 宿曜経縮刷, ed. Wakita Bunshō, 1897 | — | the **Japanese recension** of the *Xiuyao jing*, i.e. the text medieval practice actually used | not acquired | named acquisition target; until it is collated against T1299 no rule here may be called "what sukuyōshi used" |

## The controlling text

`T21n1299` is titled in full 文殊師利菩薩及諸仙所說吉凶時日善惡宿曜經 — *The Sūtra on
Mansions and Luminaries, on Auspicious and Inauspicious Times, Days, Good and Evil,
Spoken by the Bodhisattva Mañjuśrī and the Various Ṛṣis*. Two fascicles.

Its own colophon material, at the head of fascicle 1, records an unusually explicit
textual history:

- 不空 (Amoghavajra) translated it in 乾元二年 (759 CE);
- 史瑤, Assistant Magistrate of Duanzhou, took down and compiled the first version, and
  the text says of that version that it *could not order the chapters, and made the
  sense cumbersome and confused, so that students would find it hard to use*;
- the lay disciple 楊景風 (Yang Jingfeng) therefore re-annotated it under the master's
  direction, finishing in 廣德二年 (764 CE), *and every disciple keeps a copy*.

Three things follow, and all three matter for rule extraction.

First, **the received text is the 764 recension, not the 759 one.** The text says so.

Second, **not everything in it is sūtra.** Yang Jingfeng's annotations are woven into the
body, and several of the most operationally useful passages are marked 和上云 — "the
master says" — i.e. they are Amoghavajra's oral instruction recorded by the annotator,
not translated scripture. The bidirectional compatibility test is one of these. Rules
extracted from those passages carry the attribution; collapsing annotation into scripture
would overstate their authority.

Third, **the text admits it is a repair of a confused text**, which is the most likely
explanation for the internal contradictions catalogued below. Those contradictions are
data about the transmission, not defects to be edited out.

## The 27-versus-28 question

Both schemes exist in the Buddhist astral corpus and the difference is operational, not
cosmetic. T1299 uses **27**. Four independent statements say so:

| Location | Statement |
|---|---|
| T21.0387b12 | the luminaries move 於二十七宿十二宮 — through the 27 mansions and 12 signs |
| T21.0388b24 | the ṛṣi's question opens 凡天道二十七宿有闊有狹 — the 27 mansions of the heavenly way are wide and narrow |
| T21.0391b10 | 三九之法而周二十七宿 — the three-nine method circuits the 27 mansions |
| T21.0397c19 | 此則是二十七宿，周而復始 — these are the 27 mansions, ending and beginning again |

Plus the fascicle-2 election almanac is titled 二十七宿所為吉凶曆.

Three independent arithmetic checks confirm it, and all three were recomputed rather than
taken on the text's word:

1. **The pāda allotment.** Chapter 1 gives each of the twelve signs as three mansion
   fragments measured in 足 (pāda). Every sign totals 9; the grand total is 108; every
   mansion totals exactly 4; **牛 receives none**. A 28-mansion cycle cannot divide 108
   pāda into whole quarters.
2. **The three-nine structure.** 3 groups × 9 positions = 27 exactly. A 28th mansion
   would leave the third nine short or the triad open.
3. **The conjunction classes.** 6 + 12 + 9 = 27, disjoint and exhaustive, 牛 in none.

And 牛 is absent from the fascicle-2 election almanac, and from the printed worked
example of the three nines.

So what is 牛 doing in the text at all? Chapter 2's figure catalogue has **28** entries,
including one for 牛 between 斗 and 女. But that entry is structurally anomalous: it gives
the star count, the shape, the presiding deity, the gotra and the offering, and then a
natal clause — and it **omits the 此宿直日 day-election clause that every one of the other
27 entries carries.** 牛 is catalogued as an asterism and excluded from the operative
cycle, and the text marks the exclusion by withholding its duty-day.

One loose end is recorded and not resolved: T21.0387a20 lists 牛 inside a thirteen-mansion
enumeration of the solar half of the zodiac. That enumeration cannot be reconciled with
the pāda allotment printed nine lines later, which gives 牛 nothing. It is left standing
as an observed internal discrepancy.

The contrast witnesses go the other way, which is exactly why they were acquired. T1308
opens by summoning 二十八宿 deities and carries a 宿度法 in which 牛 receives a degree
entry. T1311 opens 二十八宿在天左轉. **Neither may be merged into the T1299 pack**, and
T1308's divergence is deeper than the count: it defines 命宿 as the mansion where the Sun
and Moon stand at the time of birth, where T1299 defines it as the mansion of the lunar
birth day. Fed the same person, the two definitions will disagree.

## The mansion-relationship system

This is the tradition's distinctive technique and the reason the track is worth building.

The **三九之法** (method of the three nines) takes the subject's own birth mansion as
position 1 and reads the remaining 26 in canonical order, assigning a category to each
position:

| Positions | Head | Then |
|---|---|---|
| 1-9 | 命 (life) | 榮 衰 安 危 成 壞 友 親 |
| 10-18 | 業 (karma) | 榮 衰 安 危 成 壞 友 親 |
| 19-27 | 胎 (womb) | 榮 衰 安 危 成 壞 友 親 |

Two people's birth mansions therefore determine a category with no interpretive latitude.
The text states the table in chapter 3 and again in 三必祕要法 with explicit ordinals
(第一命宿 … 第二十七親宿), and the second statement prints a full worked example for a
subject born under 畢. Rotating the canonical order by the index of 畢 reproduces all 27
printed mansions exactly, in all three groups.

Two properties make this genuinely testable rather than merely tabulated:

**It is asymmetric.** The text requires both directions — *see which of my mansions his
life-mansion falls upon, and which of his mine falls upon.* If B sits at offset *k* from
A, A sits at offset 27 − *k* from B, and the two categories almost never match. For
A = 昴 and B = 井 the pair is 危 one way and 成 the other: one is in the favourable set
and the other is not. A product that reports a single compatibility score for a couple
has answered half the question the source asks.

**Its favourable set is scoped.** 榮, 安, 成, 友, 親 are called good — but explicitly for
結交, forming an association, and explicitly under the hedge 大抵, "broadly speaking." The
text does not offer this as a general ranking, and it immediately complicates it: 危 is
excluded from the favourable set here, yet both election passages recommend a 危 day for
結交 and marriage. The same term is a bad relationship *category* and a good relationship
*day*. That is preserved, not averaged.

## Internal contradictions, recorded not resolved

The text repairs a confused predecessor and it shows. Four disagreements are encoded as
forks:

1. **The 業 day.** Chapter 3: 業宿直日，所作皆吉祥 — everything done is auspicious.
   三必祕要法: 值業宿日，所作善惡亦不成就，甚衰 — nothing done, good or bad, comes to
   fruition; greatly declining. Opposite verdicts on a triad head, from the same text.
2. **The 衰 day.** Chapter 3 blocks 衰 with 危 and 壞. 三必祕要法 blocks only 危 and 壞 and
   gives 衰 a narrow positive use — dispelling evils and treating illness.
3. **Marriage on a 危 day.** 三必祕要法 recommends it at T21.0398a02 and calls it
   inauspicious at T21.0398a09, seven lines later, in the same section.
4. **The 羅剎日 table.** Two of its seven rows print 冒 and 底, which are not mansion
   names. 昴 and 氐 are the obvious candidates, but 昴 already fills a row in the
   金剛峯日 table, so the emendation is not free. Both are left unemended and both rows
   are marked unusable.

The pack's position on all four is the same: emit both readings with their locations, or
emit neither. This is the `conflicts_with` machinery in the manifest doing real work.

## What the reading would actually look like

Set expectations correctly. A defensible Sukuyōdō report is **mansion-relational and
calendrical**, and it is close to the opposite of a Western psychological chart reading:

- it opens with the birth mansion, because everything is defined relative to it;
- its body is a *relation table* — where every other mansion stands to yours, and
  therefore how each person and each day stands to you;
- its natal statements are the text's own, which are status- and office-shaped
  (*fit to hold the office of the treasury*), not character-shaped;
- its planetary layer is inverted by category, so the same transit is favourable for one
  subject and unfavourable for another;
- and its precedence rule is stated by the text: your personal three-nine outranks the
  general almanac.

There is no natal narrative genre in this corpus to reproduce, so there is nothing to
reproduce badly. The temptation to fill the space with Western material is the main
defensibility risk this track carries.

## Rights

**Not public domain by assumption.** The CBETA TEI header states: *Available for
non-commercial use when distributed with this header intact.* The stored XML retains that
header unmodified so the condition travels with the file. The underlying Taishō edition
carries its own publisher terms, which were not independently cleared in this pass.

Research use inside the repository is within the stated condition. Reproducing the
transcription as customer-facing product content is a separate question and requires
rights review. This is recorded in every source's `rights_note` and in the access
manifest, and it is one of the two gates on the mansion-relational rows of the checklist.

## Access log

**Retrieved.** CBETA's TEI P5 corpus on GitHub served all three Taishō texts on
2026-08-02, with the canonical page/column/line markers intact:

| File | Bytes | SHA-256 |
|---|---|---|
| `T21n1299.xml` | 386,505 | `259172d5f220aaa041617c35f62fced97fd2f64353ea700fd63684d27f29899b` |
| `T21n1308.xml` | 280,824 | `464d38d06fb926a7060866d275058802244bef5f4602bfd0b58dc97f59594df8` |
| `T21n1311.xml` | 91,994 | `15cca1e14d418ee607ce4ef2b446950783ce5ce33636b2027eb95cc35cc45fc2` |

Each was flattened to a line-addressed rendering, also hashed, which is the surface every
rule citation resolves against. `fetch_sukuyo_sources.py --verify` re-checks all six.

**Failed.** SAT Daizōkyō. A request to
`https://21dzk.l.u-tokyo.ac.jp/SAT/ddb-sat2.php?mode=detail&nonum=1299&vol=21` returned
HTTP 200 with a 57-byte body containing an unsubstituted SQL fragment — the guessed
parameter names are wrong for that endpoint and the service leaked its query template
rather than erroring. No SAT text was retrieved and none is cited. This is not a blocker:
CBETA serves the same text with the same addresses. It would become useful as an
independent second transcription for collating the doubtful characters, which is what the
retry should target.

**Metadata only.** NDL Search returned twenty records for 宿曜. None was opened and none
is cited. They are recorded because they name the documents and the specialists that
would lift this pack's gates — Akazawa's study of the Insei and Kamakura Sukuyōdō
institution, Mizuguchi on the separate establishment of Onmyōdō and Sukuyōdō, Shigeta on
the rivalry between onmyōji and sukuyōshi over calendar authority, Udai on the Kōzan-ji
宿曜占文抄, and Kotyk on the Xiuyao jing's transmission.

## Validation gates before anything ships

1. An independent Classical Chinese reader reproduces the 32 passage-to-predicate
   encodings without seeing this pack.
2. A specialist in Buddhist astral science reviews the technical vocabulary — 宿直,
   三九, 命宿 versus 本命宿, 押, 犯逼守, 甘露/金剛峯/羅剎.
3. The CBETA transcription is collated against a Taishō facsimile at every doubtful
   character, minimally the 羅剎日 rows.
4. A named lunisolar calendar regime is selected, dated, and validated against an
   independent implementation before any birth mansion is emitted.
5. Rights review clears or restricts quotation under CBETA's non-commercial condition.
6. The Japanese reception layer is acquired, or the section states plainly that it
   reports the Chinese text Japanese practitioners read rather than their own practice.
7. Every fork stays a fork. A regression test should fail if any of the four
   contradictions is silently resolved.

## First bounded pilot

Build a **mansion-relationship validator**, not a reading:

1. ingest the canonical 27-order and the three-nine table;
2. reproduce the 畢-rooted worked example (already passing);
3. prove asymmetry exhaustively over all 27 × 27 mansion pairs;
4. prove the pāda, month-step and conjunction-class arithmetic closes (already passing);
5. emit compatibility only as *both directions plus both categories*, never as a score;
6. refuse to emit a birth mansion for any real date until the calendar regime lands.

That pilot is defensible today on everything except the birth mansion itself, which is
precisely the shape the Nahua track already ships: the system in full, in the text's own
words, plus an honest statement of why the reader cannot yet be placed inside it.
