# Sukuyōdō extraction notes

Status: working notes for the T1299 rule pack
Updated: 2026-08-02
Translation grade for everything below: **`engine_translation_unreviewed`**

Every rendering on this page is a single unreviewed engine translation from the Classical
Chinese. The Chinese is quoted verbatim beside it precisely so that a specialist can check
the rendering against the original rather than against a paraphrase of someone else's
copyrighted English. No modern translation was consulted, and none was needed.

**Text and addressing.** All quotations are from CBETA's TEI P5 transcription of Taishō
volume 21, hash-pinned in `sources/`. Citations use the Taishō address printed by CBETA
and SAT alike: `T21.0391b06` is volume 21, page 391, column b, line 6. The corresponding
key in `sources/T21n1299_lines.txt` is `T21n1299_p0391b06`.

**Rights.** CBETA's header states the condition: *Available for non-commercial use when
distributed with this header intact.* Quotation here is research use with full passage
addresses. Customer-facing reproduction needs rights review.

---

## 1. The 27-versus-28 mansion question

Both schemes exist in the Buddhist astral corpus, they are not interchangeable, and
T1299 uses 27. This section documents the evidence rather than asserting the conclusion.

### 1.1 The text states 27, four times

**T21.0387b11-b13** — the cosmological preface

> 日月諸曜，眾生業置於空中，乘風而止，當須彌之半，踰健陀羅之上，運行於**二十七宿**十二宮焉。

*The sun, moon and the luminaries are set in space by the karma of beings; borne on the
wind they come to rest, at the midpoint of Sumeru, above Khadiraka, moving through the
**twenty-seven mansions** and the twelve signs.*

**T21.0388b24-b26** — the ṛṣi's question, opening the conjunction-class passage

> 仙人問言：凡天道**二十七宿**有闊有狹，皆以四足均分別，月行或在前後，驗天與說差互不同，宿直之宜如何定得？

*The ṛṣi asked: the **twenty-seven mansions** of the heavenly way are wide and narrow,
yet all are evenly divided into four pādas; the moon's motion is sometimes ahead and
sometimes behind, and checking the sky against the teaching they do not agree — how then
is the mansion on duty to be fixed?*

Note what the ṛṣi concedes: the mansions are *unequal in width* but are *treated as
equal quarters*. The text knows its own scheme is schematic. It does not tabulate the
real widths anywhere, which is one reason row 12 of the checklist is gated.

**T21.0391b10-b11** — closing the three-nine chapter

> 三九之法而周**二十七宿**，眾為祕密。

*The method of the three nines thus circuits the **twenty-seven mansions**; the whole of
it is secret.*

**T21.0397c19** — closing the second statement of the same table

> 此則是**二十七宿**，周而復始，是為三九之法。

*These then are the **twenty-seven mansions**, ending and beginning again; this is the
method of the three nines.*

And the fascicle-2 election almanac is headed 二十七宿所為吉凶曆.

### 1.2 Three arithmetic checks, all recomputed

None of these is taken on the text's word; each was evaluated from the text's own numbers.

**The pāda allotment closes only on 27.** Chapter 1 gives each of the twelve signs as
three mansion fragments in 足 (pāda). Example, T21.0387b14-b15:

> 第一、星四足，張四足，翼一足，大陽位焉。

*First: 星 four pādas, 張 four pādas, 翼 one pāda; the Sun is positioned here.*

Summing all twelve paragraphs: every sign totals **9**; the grand total is **108**; every
one of the 27 mansions totals exactly **4**; and 牛 receives **0**. 12 × 9 = 108 = 27 × 4.
A 28-mansion cycle cannot divide 108 pādas into whole quarters.
(Vector `sukuyo.v.pada_allotment_closes`.)

**The three-nine structure requires 27.** Three groups of nine. A 28th mansion leaves the
third group short or the triad open. (Vector `sukuyo.v.sanku_triad_heads`.)

**The conjunction classes partition 27.** 6 + 12 + 9, disjoint and exhaustive, 牛 in none.
(Vector `sukuyo.v.conjunction_classes_partition`.)

### 1.3 What 牛 is doing in the text

Chapter 2's figure catalogue has **28** entries. The 牛 entry, in full —
**T21.0390a14-a16**:

> 牛圖。牛宿吉，甚吉祥。其宿三星，形如牛頭，風梵摩神也，姓奢拏耶那，食乳粥香花藥。此宿生人，法合福德所作不求。

*Figure of 牛. The 牛 mansion is auspicious, greatly auspicious. Its mansion has three
stars, shaped like an ox's head; its deity is 風梵摩; its clan-name is 奢拏耶那; its food
is milk-gruel, fragrant flowers and medicine. A person born under this mansion accords
with merit, and what he does he does not have to seek.*

Compare a normal entry — **T21.0388c08-c13**, the first in the catalogue:

> 昴圖。昴六星，形如剃刀，火神也，姓某尼裴苦，食乳酪。**此宿直日**，宜火作煎煮、計算畜生、合和酥藥、作牛羊坊舍、種蒔、入宅、伐逆除暴、剃頭並吉。若用裁衣必被火燒。**此宿直生人**，法合念善、多男女、勤學問、有容儀。性合慳澁、足詞辯。

*Figure of 昴. 昴 has six stars, shaped like a razor; its deity is the fire deity; its
clan-name is 某尼裴苦; its food is milk-curd. **On the day this mansion is on duty**, it is
fit for fire-work and boiling, reckoning livestock, compounding butter-medicines, building
byres for oxen and sheep, sowing, entering a dwelling, punishing rebellion and removing
violence, and shaving the head — all auspicious. If cloth is cut on it, it will surely be
burnt by fire. **A person born on this mansion's duty-day** accords with mindfulness of
the good, many sons and daughters, diligence in study, and a dignified bearing; his nature
accords with stinginess, and he is full of argument.*

Every one of the other 27 entries has that **此宿直日** clause. 牛 has none. The text
catalogues it as an asterism and marks its exclusion from the operative cycle by
withholding its duty-day.

牛 is also absent from the fascicle-2 election almanac and from the printed worked
example of the three nines (§2.2 below).

### 1.4 The one unresolved conflict

**T21.0387a20-a22**

> 取張、翼、軫、角、亢、氐、房、心、尾、箕、斗、**牛**、女等一十三宿，迄至于虛宿之半，恰當子地之中，分為六宮也。

*Taking the thirteen mansions 張, 翼, 軫, 角, 亢, 氐, 房, 心, 尾, 箕, 斗, **牛**, 女, up to
half of the 虛 mansion, exactly at the middle of the 子 earth-branch, they are divided into
six signs.*

This includes 牛 and cannot be reconciled with the pāda allotment printed nine lines later,
which gives 牛 nothing and which begins the solar half at 星 rather than 張. Recorded as an
observed internal discrepancy. **Not emended.** Encoded in
`sukuyo.mansion.niu_is_catalogued_not_operative` under `conclusion.unresolved`.

### 1.5 The contrast witnesses go the other way

**T1308, T21.0426c03-c05**

> 今西國婆羅門僧金俱吒，命得**二十八宿**神下，問其吉凶、畫其形狀，辨七曜所至攘災法如後。

*Now the brahmin monk 金俱吒 of the Western Country summoned down the deities of the
**twenty-eight mansions**, asked them about fortune and misfortune, drew their forms, and
distinguished the methods for averting calamity when the seven luminaries arrive, as
follows.*

And T1308 defines the life mansion differently — **T21.0426b26-b27**:

> 其宿四世界眾生所生之日時，日月行所在為之**命宿**。

*The mansion in which the sun and moon are travelling at the day and hour of a being's
birth in the four worlds is its **life mansion**.*

That is a **different derivation** from T1299's, which takes the mansion of the lunar
birth day counted from the month's full-moon mansion. Fed the same person the two will
disagree. Merging them is forbidden by `sukuyo.boundary.t1308_is_a_28_mansion_system`.

**T1311, T21.0459b05** opens 二十八宿在天左轉 — a third scheme again, running a
nine-luminary cycle indexed by year of life rather than by mansion.

**Conclusion.** T1299 = 27, operative, with 牛 catalogued but excluded. T1308 and T1311 =
28, and structurally different besides. The pack encodes only T1299 and registers the
other two as contrast witnesses.

---

## 2. The mansion-relationship system

### 2.1 The table, stated twice

**T21.0391a29-b11** — 三九祕宿品第三, first statement

> 一九之法：命宿、榮宿、衰宿、安宿、危宿、成宿、壞宿、友宿、親宿。
> 二九之法：業宿、榮宿、衰宿、安宿、危宿、成宿、壞宿、友宿、親宿。
> 三九之法：胎宿、榮宿、衰宿、安宿、危宿、成宿、壞宿、友宿、親宿。
> 此法以定人所生日為宿直、為命宿、為第一，次以榮宿，又次衰宿，及安宿、危宿、成宿、壞宿、友宿、親宿，如是九宿為一九之法。其次則以業宿為首，以下九准前，為二九之法。次則以胎宿為首，以下九准前。三九之法而周二十七宿，眾為祕密。

*Method of the first nine: 命 mansion, 榮 mansion, 衰 mansion, 安 mansion, 危 mansion,
成 mansion, 壞 mansion, 友 mansion, 親 mansion. Method of the second nine: 業 mansion,
then the same eight. Method of the third nine: 胎 mansion, then the same eight.*
*This method takes the mansion on duty on the day of a person's birth as the 命 mansion
and as the first; next the 榮 mansion, next again the 衰 mansion, then 安, 危, 成, 壞, 友,
親 — these nine mansions constitute the method of the first nine. Next, taking the 業
mansion as head, the nine below follow as before, constituting the method of the second
nine. Next, taking the 胎 mansion as head, the nine below follow as before. The method of
the three nines thus circuits the twenty-seven mansions; the whole of it is secret.*

**T21.0397c07-c19** — 三必祕要法, second statement, with explicit ordinals

> 三九法者，皆從本所屬宿為初九，第一命宿，依次第二為榮宿，第三衰宿，第四安宿，第五危宿，第六成宿，第七壞宿，第八友宿，第九親宿。次第十宿，為二九行頭為業宿，第十一復為榮宿，第十二衰宿，第十三安宿，第十四危宿，第十五成宿，第十六壞宿，第十七友宿，第十八親宿。次第十九宿，即為三九行頭為胎宿，第二十為榮宿，第二十一衰宿，第二十二安宿，第二十三危宿，第二十四成宿，第二十五壞宿，第二十六友宿，第二十七親宿。此則是二十七宿，周而復始，是為三九之法。

*As for the three-nine method: in every case one takes the mansion one belongs to as the
first nine. The first is the 命 mansion; in order, the second is the 榮 mansion, the third
衰, the fourth 安, the fifth 危, the sixth 成, the seventh 壞, the eighth 友, the ninth 親.
The tenth mansion next is the head of the second nine's row, the 業 mansion; the eleventh
is again 榮, the twelfth 衰, the thirteenth 安, the fourteenth 危, the fifteenth 成, the
sixteenth 壞, the seventeenth 友, the eighteenth 親. The nineteenth mansion next is the
head of the third nine's row, the 胎 mansion; the twentieth is 榮, the twenty-first 衰,
the twenty-second 安, the twenty-third 危, the twenty-fourth 成, the twenty-fifth 壞, the
twenty-sixth 友, the twenty-seventh 親. These then are the twenty-seven mansions, ending
and beginning again; this is the method of the three nines.*

**Extracted predicate.** With `offset = (index(target) − index(subject's 命宿)) mod 27`
over the canonical order:

- `offset ∈ {0, 9, 18}` → the triad head: `命`, `業`, `胎` respectively;
- otherwise → `[榮, 衰, 安, 危, 成, 壞, 友, 親][(offset mod 9) − 1]`.

Encoded as `sukuyo.sanku.triad_heads` and `sukuyo.sanku.category_by_offset`.

### 2.2 The text's own worked example, and it passes

**T21.0397c02-c06** prints the three nines in full for a subject born under 畢:

> 初九：畢、觜、參、井、鬼、柳、星、張、翼。
> 二九：軫、角、亢、氐、房、心、尾、箕、斗。
> 三九：女、虛、危、室、壁、奎、婁、胃、昴。

Rotating the canonical order (昴 畢 觜 參 井 鬼 柳 星 張 翼 軫 角 亢 氐 房 心 尾 箕 斗 女
虛 危 室 壁 奎 婁 胃) by index(畢) = 1 reproduces **all twenty-seven mansions in the
printed order**, group for group. 牛 does not appear. This is the tradition's own worked
example of its own central technique, and the encoded table matches it character for
character. Vector `sukuyo.v.sanku_worked_example_from_bi`.

### 2.3 The compatibility test is asymmetric

**T21.0391b14-b17** — marked 和上云, i.e. the master's oral instruction recorded by the
annotator Yang Jingfeng, not translated scripture

> 和上云：凡與人初結交者，先須看彼人命宿押我何宿，又看我命宿押彼人何宿，大抵以榮、安、成、友、親為善，堪結交；自餘並惡，不可與相知。以為祕法耳。

*The master said: whenever first forming an association with a person, one must first see
which of my mansions that person's 命 mansion falls upon, and also see which of his
mansions my 命 mansion falls upon. Broadly speaking, 榮, 安, 成, 友 and 親 are good and fit
for forming an association; all the rest are bad, and one should not become acquainted.
This is held as a secret method.*

Three things must survive into any implementation:

1. **Both directions.** 押 ("falls upon", "presses on") is directional. If B sits at
   offset *k* from A, then A sits at offset (27 − *k*) from B. Worked case: A = 昴,
   B = 井. B seen from A is offset 4 → **危**. A seen from B is offset 23 → **成**. One is
   in the favourable set and the other is not. A single compatibility verdict for a pair
   answers half the question the source asks.
   (Vector `sukuyo.v.sanku_relation_is_asymmetric`.)
2. **The hedge.** 大抵, "broadly speaking." The source qualifies its own rule.
3. **The scope.** The favourable set is stated for 結交 specifically. It is not a general
   ranking of the nine categories, and it is contradicted for 危 by the election passages
   in §3.

---

## 3. Election by the personal three-nine category

Two statements, which agree in parts and contradict each other in others. Both are
encoded; neither is preferred.

### 3.1 Chapter 3, T21.0391b19-b25

> 凡命、胎宿直日，不宜舉動百事。業宿直日，所作皆吉祥。衰、危、壞宿日，並不宜遠行，出入遷移、買賣裁衣、剃頭剪甲並不吉。壞日，又宜壓鎮降伏怨讎及討伐暴惡。安日，移動遠行、修園宅臥具、作壇場並吉。危日，宜結交婚姻、歡會宴聚吉。成日，修學問道、合藥求仙吉。友、親日，宜結交朋友大吉。

*On the duty-days of the 命 and 胎 mansions, it is not fit to undertake the hundred
affairs. On the duty-day of the 業 mansion, everything done is auspicious. On the 衰, 危
and 壞 mansion days, distant travel is unfit; going out and moving house, buying and
selling, cutting cloth, shaving the head and paring the nails are all inauspicious. On the
壞 day, however, it is fit to suppress and subdue enemies and to punish the violent and
evil. On the 安 day, moving, distant travel, repairing gardens, houses and bedding, and
constructing a ritual platform are all auspicious. On the 危 day, it is fit to form
associations and marriages; joyous gatherings and banquets are auspicious. On the 成 day,
cultivating study and inquiring into the Way, compounding medicines and seeking
transcendence are auspicious. On the 友 and 親 days, it is fit to make friends and form
associations — greatly auspicious.*

### 3.2 三必祕要法, T21.0397c25-0398a17

> 若榮宿日，即宜入官拜職、對見大人、上書表進獻君王、興營買賣、裁著新衣、沐浴及諸吉事並大吉。出家人剃髮、割爪甲、沐浴、承事師主、啟請法要並吉。
> 若安宿日，移徙吉，遠行人入宅、造作園宅、安坐臥床帳、作壇場並吉。
> 若危宿日，宜結交、定婚姻，歡宴聚會並吉。
> 若成宿日，宜修道學問、合和長年藥法，作諸成就法並吉。
> 若友宿日、親宿日，宜結交、定婚姻，歡宴聚會並吉。
> 若命宿日、胎宿日，不宜舉動百事。值業宿日，所作善惡亦不成就，甚衰。
> 若危壞日，並不宜遠行出、入移徙、買賣、婚姻、裁衣、剃頭、沐浴並凶。
> 若衰日，唯宜解除諸惡、療病。
> 若壞日，宜作鎮壓、降伏怨讎及討伐阻壞姦惡之謀，餘並不堪。
> 此所用三九法，於長行曆縱不是吉相，己身三九若吉，但用無妨。
> 又一說云：命宿、胎宿、危宿、壞宿，此宿日不得進路，及剃髮、裁衣、除爪甲並凶。

*On the 榮 mansion day it is fit to enter office and receive rank, to have audience with
great persons, to submit memorials and present them to the sovereign, to raise up trade,
to cut and wear new clothes, to bathe, and all auspicious matters — greatly auspicious.
For renunciants, shaving the head, paring the nails, bathing, serving the preceptor and
requesting the essentials of the Dharma are auspicious.*
*On the 安 mansion day, moving house is auspicious; for the traveller, entering a
dwelling, building gardens and houses, setting up seats, beds and curtains, and
constructing a ritual platform are all auspicious.*
*On the 危 mansion day, it is fit to form associations and to settle a marriage; joyous
banquets and gatherings are auspicious.*
*On the 成 mansion day, it is fit to cultivate the Way and study, to compound
longevity-medicine methods, and to perform rites of accomplishment.*
*On the 友 and 親 mansion days, it is fit to form associations and settle a marriage;
joyous banquets and gatherings are auspicious.*
*On the 命 and 胎 mansion days it is not fit to undertake the hundred affairs. Falling on
the 業 mansion day, what is done — good or evil — likewise does not come to fruition;
greatly declining.*
*On the 危 and 壞 days, distant travel, going out and in, moving house, trade, marriage,
cutting cloth, shaving the head and bathing are all inauspicious.*
*On the 衰 day, only dispelling evils and treating illness are fit.*
*On the 壞 day it is fit to perform suppression, to subdue enemies, and to punish and
thwart the schemes of the wicked; the rest are all unfit.*
*In using this three-nine method, even if the general almanac shows no auspicious aspect,
if one's own three-nine is auspicious, one may use it without harm.*
*Another account says: the 命, 胎, 危 and 壞 mansion days — on these days one may not set
out on a journey, nor shave the head, cut cloth or pare the nails; all inauspicious.*

### 3.3 The four disagreements, encoded as forks

| # | Point | Chapter 3 | 三必祕要法 |
|---|---|---|---|
| 1 | the 業 day | 所作皆吉祥 — all auspicious | 所作善惡亦不成就，甚衰 — nothing comes to fruition |
| 2 | the 衰 day | blocked together with 危 and 壞 | split out; 唯宜解除諸惡、療病 |
| 3 | marriage on a 危 day | 宜結交婚姻 | recommended at T21.0398a02, called 凶 at T21.0398a09 — **the section contradicts itself** |
| 4 | the four-mansion travel ban | absent | present but labelled 又一說云 |

Disagreement 1 is the serious one: 業 is a triad head, so a third of the cycle's structure
hangs on a term the text does not settle. `sukuyo.election.gou_day_contradiction` records
both readings with `conclusion.resolution = none`, and the vector asserts that a
single-polarity output is not permitted.

### 3.4 The precedence rule

**T21.0398a14-a15** is the tradition's own statement of its judgment hierarchy:

> 此所用三九法，於長行曆縱不是吉相，己身三九若吉，但用無妨。

*In using this three-nine method, even if the general almanac (長行曆) shows no auspicious
aspect, if one's own three-nine is auspicious, one may use it without harm.*

The personal, birth-mansion-relative layer **outranks** the impersonal calendrical layer.
This is exactly the kind of ordering the defensibility standard's requirement 2 says a
composer must execute rather than flatten. Encoded as
`sukuyo.election.sanku_overrides_general_almanac`.

---

## 4. Planetary affliction, and its inversion

**T21.0391b26-c03**

> 凡日月直，星沒。犯逼守命、胎之宿，此人是厄會之時也，宜修功德、持真言念誦、立道場以禳之。
> 若犯業宿及榮、安、成、友、親等宿，並所求不遂、百事迍邅，亦宜修福念善。
> 若犯衰、危、壞等宿者，則所求稱意、百事通達。

*[opening clause obscure: 凡日月直，星沒。] When [a luminary] offends, presses upon or
remains in the 命 or 胎 mansion, this person is in a time of calamity; he should cultivate
merit, hold and recite mantras, and establish a ritual site to avert it.*
*If it offends the 業 mansion, or the 榮, 安, 成, 友 or 親 mansions, then what is sought is
not obtained and the hundred affairs are beset; he should likewise cultivate blessings and
be mindful of the good.*
*If it offends the 衰, 危 or 壞 mansions, then what is sought accords with his wish and the
hundred affairs pass through.*

Restated at **T21.0398a18-a25** with the agent named and an operational instruction:

> 夫五星及日月陵犯守逼命、胎之宿，即於身大凶，宜修功德造善以禳之。若陵逼業宿者及榮、安、成、友、親之宿，即所求不遂，諸途迍坎，亦宜修福。福者，謂入灌頂及護摩，并修諸功德。如五星陵犯守逼衰、危、壞等宿，即身事並遂、所作稱心，官宦遷轉求者皆遂。如此當須問知司天者，乃知此年此月熒惑、鎮歲、辰星、太白及日月等在何宿。

*When the five planets and the sun and moon overrun, offend, remain in or press upon the
命 or 胎 mansion, it is greatly inauspicious for the person; he should cultivate merit and
do good to avert it. If they overrun or press upon the 業 mansion, or the 榮, 安, 成, 友
or 親 mansions, then what is sought is not obtained and every road is obstructed; he
should likewise cultivate blessings. By blessings is meant entering abhiṣeka and homa, and
cultivating all merits. If the five planets overrun, offend, remain in or press upon the
衰, 危 or 壞 mansions, then his affairs are all accomplished and what he does accords with
his heart, and those seeking office and promotion all obtain it. For this one must ask
someone who knows the office of heaven, so as to know in which mansion Mars, Saturn,
Jupiter, Mercury, Venus and the sun and moon stand this year and this month.*

**Two findings that constrain any implementation.**

First, **affliction is signed by category, not scalar.** A planet striking a 衰, 危 or 壞
mansion is *good news* for that subject. An engine that scores transits as uniformly
negative contradicts this text directly. Encoded as
`sukuyo.transit.affliction_inverts_by_category`, with a vector asserting the inversion.

Second, **the text outsources the ephemeris.** 當須問知司天者 — go ask the astronomical
official. T1299 supplies no planetary positions at all, which is what T1308 was compiled
to supply and why the two texts travel together despite being different systems.

**Recorded as unresolved:** the opening clause 凡日月直，星沒。 The construction is unclear
in the received text — plausibly "when the sun and moon are on duty, and a star sets" or a
section header on occultation. It is quoted verbatim in the rule's `exceptions` and is
**not** used to condition the rule.

**Refused for output:** the remedial prescriptions. Abhiṣeka, homa, mantra recitation and
the establishment of a ritual site are the liturgy of an initiatory tradition. They are
recorded as what the text says and are never issued as instructions.

---

## 5. Birth-mansion derivation, and why it cannot run

### 5.1 The months are named by their full-moon mansion

**T21.0394c20-c28**

> 西國皆以十五日望宿，為一月之名。故二月為角月。三月名氐月，四月名心月，五月名箕月，六月名女月，七月名室月，八月名婁月，九月為昴月，十月名觜月，十一月名鬼月，十二月名星月，正月名翼月。

*In the Western Country they all take the mansion of the fifteenth-day full moon as the
name of the month. Thus the second month is the 角 month. The third is named the 氐 month,
the fourth the 心 month, the fifth the 箕 month, the sixth the 女 month, the seventh the 室
month, the eighth the 婁 month, the ninth the 昴 month, the tenth the 觜 month, the
eleventh the 鬼 month, the twelfth the 星 month, and the first month the 翼 month.*

**Check.** Taken in the canonical 27-order, the twelve steps between successive months are
[2, 2, 2, 2, 2, 3, 3, 2, 2, 3, 2, 2] and sum to exactly **27**. The table closes.
(Vector `sukuyo.v.month_full_moon_table_closes`.)

**External cross-check.** These are the Indian month-naming nakṣatras, and all twelve
match: 角 = Citrā (Caitra), 氐 = Viśākhā (Vaiśākha), 心 = Jyeṣṭhā (Jyaiṣṭha), 箕 =
Pūrvāṣāḍhā (Āṣāḍha), 女 = Śravaṇa (Śrāvaṇa), 室 = Pūrvabhādrapadā (Bhādrapada), 婁 =
Aśvinī (Āśvina), 昴 = Kṛttikā (Kārttika), 觜 = Mṛgaśiras (Mārgaśīrṣa), 鬼 = Puṣya (Pauṣa),
星 = Maghā (Māgha), 翼 = Uttaraphalgunī (Phālguna). **This identification is engine-supplied
and is informational only.** T1299 does not print Sanskrit nakṣatra names here — it prints
transliterated deity names in chapter 2, which is a different matter. No rule in the pack
depends on the Sanskrit equivalences.

### 5.2 The primary procedure

**T21.0394c28-0395a03**

> 夫欲知二十七宿日者，先須知月望宿日。欲數一日至十五日已前白月日者，即從十五日下宿逆數之可知。欲知十六日已後至三十日，即從十五日下宿順數即得。但依此即定。

*If you wish to know the day of the twenty-seven mansions, you must first know the mansion
of the full-moon day. To count the bright-fortnight days from the first up to before the
fifteenth, count backwards from the mansion under the fifteenth. To know from the
sixteenth up to the thirtieth, count forwards from the mansion under the fifteenth. Follow
this and it is fixed.*

**T21.0395b01-b03**

> 夫欲求人所屬宿者，即於圖上，取彼生月十五日下宿，從此望宿逆順數之，至彼生日止，則求得彼人所屬宿也。

*If you wish to find the mansion a person belongs to, then on the chart take the mansion
under the fifteenth day of his birth month, and from that full-moon mansion count
backwards or forwards to his birth day and stop; this yields the mansion that person
belongs to.*

Predicate: `mansion = order[(index(full_moon_mansion_of_birth_month) + (lunar_day − 15)) mod 27]`.

### 5.3 The abbreviated procedure, and the text's own redundancy check

**T21.0395b04-b06**

> 又法略算求人本命宿，先下生日數，又虛加十三訖，即從彼生月望宿，用上位數順除，數盡則止，即得彼人所屬命宿。

*Another method, an abbreviated reckoning for finding a person's 本命宿: first set down the
number of the birth day, then notionally add thirteen; then from the full-moon mansion of
his birth month, count off forward by the number in the upper position, stopping when the
count is exhausted; this yields the 命宿 that person belongs to.*

Predicate: `mansion = order[(index(full_moon_mansion) + (lunar_day + 13 − 1)) mod 27]`.

Since `(d + 12) = (d − 15) + 27`, the abbreviated reckoning **is** the primary reckoning.
Evaluated exhaustively over all 12 months × 30 lunar days: **810 cases, 0 mismatches**.
(Vector `sukuyo.v.abbreviated_equals_primary_exhaustive`.) The text supplies its own
cross-check, which is a gift for validation: an implementation that disagrees with only
one of the two formulas is provably wrong.

### 5.4 The blocker

**Nothing here converts a civil date into 生月 and 生日.** The procedure presupposes a
lunar month and day already expressed in the source's own scheme. Japanese sukuyōshi took
them from the calendar the court issued. That calendar regime is not in the retrieved
corpus and is not in this repository.

Under the standard's translation-policy table, this is the third row: *original not
retrievable → this is the real blocker, an access problem*. Except that the missing
document is a **calendar**, not a translation. The Chinese was read directly and presented
no difficulty.

Encoded as `sukuyo.natal.birth_mansion_requires_lunar_calendar`, which fails closed and
explicitly forbids the three tempting substitutions: a Gregorian day-of-year modulo 27, a
modern almanac, and a Jyotisha nakṣatra from a modern ephemeris. The last is wrong twice
over — different derivation, and it would silently reintroduce the 28th mansion.

### 5.5 The observational route, which the text keeps separate

**T21.0388b26-c06**

> 菩薩曰：凡月宿有三種合法，一者前合、二者隨合、三者並合，知此三則宿直可知也。云何前合？奎、婁、胃、昴、畢、觜六宿為前合也。云何為並合？參、井、鬼、柳、星、張、翼、軫、角、亢、氐、房十二宿為並合。云何為隨合？心、尾、箕、斗、女、虛、危、室、壁九宿為隨合。凡宿在月前、月居宿後為前合。月在宿前、宿在月後，如犢隨母為隨合。宿月並行，為並合也。
> 頌曰：六宿未到名前合，十二宿月左右合，九宿如犢隨從母，奎宿直應當知耳。

*The Bodhisattva said: there are three modes of the moon's conjunction with a mansion —
first, forward conjunction; second, following conjunction; third, alongside conjunction.
Know these three and the mansion on duty can be known. What is forward conjunction? The
six mansions 奎, 婁, 胃, 昴, 畢, 觜 are forward conjunction. What is alongside conjunction?
The twelve mansions 參, 井, 鬼, 柳, 星, 張, 翼, 軫, 角, 亢, 氐, 房 are alongside conjunction.
What is following conjunction? The nine mansions 心, 尾, 箕, 斗, 女, 虛, 危, 室, 壁 are
following conjunction. When the mansion is ahead of the moon and the moon behind it, this
is forward conjunction. When the moon is ahead of the mansion and the mansion behind it,
as a calf follows its mother, this is following conjunction. When mansion and moon travel
together, this is alongside conjunction.*
*Verse: six mansions not yet reached are named forward conjunction; with twelve mansions
the moon conjoins left or right; nine follow like a calf after its mother; from the 奎
mansion the duty should be known.*

6 + 12 + 9 = 27, disjoint, exhaustive, 牛 in none.

And at **T21.0395b20** the text instructs: 當以此頌復驗之於天 — *one should verify this
verse again against the sky.* The tradition treats its own schematic rule as an
approximation to observation, not a replacement for it. Worth quoting in any product
prose; it is a better epistemic posture than most modern astrology software's.

**Variant recorded, not emended:** the verse's final line reads 奎宿直應當知耳 at
T21.0388c06 and 從奎宿數應當知 at T21.0395b13.

---

## 6. The twelve signs

**T21.0387b14-0388a04.** Each of the twelve paragraphs has the same five-part shape.
Example, T21.0387b22-b24:

> 第三、角二足，亢四足，氐三足，太白位焉。其神如秤，故名秤宮。主寶庫之事。若人生屬此宮者，法合心直平政、信敬多財，合掌庫藏之任。

*Third: 角 two pādas, 亢 four pādas, 氐 three pādas; Venus is positioned here. Its deity is
like a balance, hence it is named the Balance sign. It governs matters of treasure-houses.
If a person is born belonging to this sign, he accords with an upright heart and even
governance, with trust and reverence and much wealth; he is fit to hold the office of the
storehouses.*

Note the **form of the natal clause**: 法合 X, 合掌 Y 之任 — "accords with X, fit to hold
the office of Y." These are status and office statements, not personality traits. Rendering
師子宮 as "you are a natural leader" would be a modernization the source does not license;
the source says *fit to hold command of the armies*.

**The domicile pattern.** 大陽 in 師子宮, 太陰 in 蟹宮, and the five planets each holding
two signs arranged symmetrically outward — Mercury in 女宮 and 婬宮, Venus in 秤宮 and 牛宮,
Mars in 蝎宮 and 羊宮, Jupiter in 弓宮 and 魚宮, Saturn in 磨竭宮 and 瓶宮. This is the
classical domicile arrangement. T1299 states it and does not derive it, and it supplies **no**
exaltation, triplicity, term or face material anywhere. Importing Hellenistic or Jyotisha
dignity apparatus on the strength of the agreement is forbidden by
`sukuyo.rasi.resident_luminary`.

**Orthographic note.** The text writes 大陽 at T21.0387b14 and 太陽 at T21.0387c08; 大陰
and 太陰 alternate similarly. Names are recorded as printed at each location and are not
normalized.

**Refused content.** T21.0388a01-a04, 蟹宮: 法合惡性欺誑、聰明而短命 — *accords with an evil
nature and deceit; clever but short-lived.* Recorded as source text; refused for customer
output.

---

## 7. The seven weekdays, and the transmission evidence

**T21.0391c07-c10**

> 夫七曜，日、月、五星也。其精上曜于天，其神下直于人，所以司善惡而主理吉凶也。其行一日一易，七日一周，周而復始。

*The seven luminaries are the sun, the moon and the five planets. Their essences shine
above in heaven and their spirits preside below over people, and so they govern good and
evil and rule over fortune and misfortune. In their course they change once a day and
complete one revolution in seven days, ending and beginning again.*

A continuous seven-day week, stated plainly. **The text gives no epoch for it**, which is
why the weekday row of the checklist is gated.

**T21.0398b01-b18** is the passage that settles the Onmyōdō question:

> 忽不記得，但當問胡及波斯并五天竺人總知。尼乾子末摩尼，常以密日持齋，亦事此日為大日。此等事持不忘，故今列諸國人呼七曜如後。
> 日曜，太陽，胡名蜜，波斯名曜森勿，天竺名阿儞底耶。
> 月曜，太陰，胡名莫，波斯名婁禍森勿，天竺名蘇上摩。
> 火曜，熒惑，胡名雲漢，波斯名勢森勿，天竺名糞盎聲哦囉迦盎。
> 水曜，辰星，胡名咥，波斯名掣森勿，天竺名部陀。
> 木曜，歲星，胡名鶻勿，波斯名本森勿，天竺名勿哩訶娑跛底。
> 金曜，太白，胡名那歇，波斯名數森勿，天竺名戌羯羅。
> 土曜，鎮星，胡名枳院，波斯名翕森勿，天竺名賒乃以室折囉。

*If you suddenly cannot remember, simply ask a Sogdian, or a Persian, or a person of the
Five Indias — they all know. The Nirgranthas and the Manichaeans always keep a fast on the
密 day and serve that day as the great day. These matters they hold and do not forget;
therefore the names by which the people of the various countries call the seven luminaries
are listed below.* [seven rows follow, each giving the Chinese planet name, the Sogdian
name, the Persian name and the Sanskrit name]

The Sanskrit names are transparent — 阿儞底耶 = Āditya, 蘇[上]摩 = Soma, 部陀 = Budha,
勿哩訶娑跛底 = Bṛhaspati, 戌羯羅 = Śukra, 賒乃以室折囉 = Śanaiścara — and the Sogdian 蜜
(Mīr, Sunday) is the day the text says Manichaeans keep.

**Two rows carry interlinear phonetic notation and are quoted with it intact.** The Moon
row prints 蘇上摩, where 上 is a tone gloss on 蘇 (上聲) rather than a syllable of the name.
The Mars row prints 糞盎聲哦囉迦盎, in which 聲 is likewise a phonetic marker; the intended
name is evidently Aṅgāraka, but the surrounding graphs 糞 and the two 盎 are not
straightforwardly resolvable from this transcription alone and are **not emended here**.
This is one of the passages where a Taishō facsimile or a second witness is needed.

A text that names its own Sogdian, Persian and Indian transmitters, in three languages,
in a table, is not a branch of the Japanese yin-yang bureau. This is the primary evidence
for `sukuyo.boundary.sukuyodo_is_not_onmyodo`.

**Natal clauses, T21.0391c11-0392a27.** Six of the seven planets carry a 若人此曜直日生者
clause; **辰星 (Mercury) does not.** The gap is recorded and not filled by inference.
Refused for output: 短命 (Sun, Venus) and 醜陋惡性、妨親害族 (Mars). Also note that each
entry carries a 若五月五日得此曜者 annual omen and a 若有虧蝕地動者 eclipse/earthquake omen
— those are **mundane** omens about the year and the state and must not be folded into a
natal reading.

**Weekday-mansion classes, T21.0398b21-c07.** Three seven-row tables: 甘露日 (amṛta, 大吉祥),
金剛峯日 (vajra-peak, for wrathful rites), 羅剎日 (rākṣasa, 不宜舉百事，必有殃禍). Two rows of
the 羅剎日 table print 冒 (T21.0398c03) and 底 (T21.0398c05), neither of which is a mansion
name. 昴 and 氐 are the obvious candidates, but 昴 already fills a row in the 金剛峯日 table,
so the emendation is not free. **Left unemended; both rows marked unusable.** 19 of 21
pairs are clean.

---

## 8. Terminology to have a specialist check first

These carry doctrinal weight and a single unreviewed reading can distort them silently.

| Term | Working rendering | Why it needs review |
|---|---|---|
| 宿直 | "mansion on duty" | whether it is the mansion the moon occupies, the mansion assigned to the day, or both depending on context |
| 命宿 / 本命宿 | "life mansion" / "natal life mansion" | whether the two are strictly synonymous in T1299; T1308 uses 命宿 for something else entirely |
| 業宿 | "karma mansion" | 業 is doctrinally loaded; whether the technical sense here is karmic or merely positional |
| 胎宿 | "womb mansion" | likewise; whether it points to conception |
| 押 | "falls upon" / "presses on" | the operative verb of the compatibility test; the whole asymmetry rests on it |
| 犯 逼 守 陵 | "offend, press, remain in, overrun" | four distinct planetary-aspect verbs used together; whether they are graded or synonymous |
| 三九 | "the three nines" | whether 九 is "nine" or "row of nine" in 二九行頭 |
| 長行曆 | "the general almanac" | which almanac exactly, and whether it is the 二十七宿所為吉凶曆 in the same text |
| 和上 | "the master" | whether this is Amoghavajra specifically throughout |
| 甘露 / 金剛峯 / 羅剎 | amṛta / vajra-peak / rākṣasa | the Sanskrit behind each and whether they are established liturgical categories |

---

## 9. Missing work

Ordered by leverage.

1. **A named lunisolar calendar regime.** The single highest-value acquisition. It
   unblocks checklist rows 1, 6, 7 and 8 — most of the reading. Needs an explicit month
   numbering, leap-month policy, day boundary, locality, and a resolution of the
   bright/dark fortnight convention that chapter 6 (黑白月分品第六, T21.0392c29-0393a22)
   assumes. Historically the Japanese answer is the Senmyō calendar; the passage that
   would supply it is a calendar table, not a passage of T1299.
2. **Independent Classical Chinese review** of the 32 encoded passages, plus a second
   encoder reproducing the extraction blind. This is the gate the house standard itself
   imposes on rule promotion, and it is what lifts the mansion-relational core.
3. **A Taishō facsimile or an independent second transcription** for the two corrupt
   羅剎日 characters, and for collating any other doubtful graph. The SAT retry with the
   documented `satdb2018pre.php` permalink form is the cheapest route.
4. **T1308's tables in a layout-preserving form.** CBETA's linearization of the Taishō
   grids is unusable as data, and the transcribed quadrant totals (75 + 98 + 80 + 113)
   sum to 366 rather than 365.25. Needed before any degree apportionment, ephemeris or
   twelve-place material can be touched — and it must stay in a separate 28-mansion pack.
5. **The Japanese reception layer.** 宿曜占文抄 (Kōzan-ji) or a dated Sukuyōdō kanmon from
   the Insei/Kamakura corpus. Without it this track is *a careful reading of the Chinese
   text that Sukuyōdō read*, not Sukuyōdō practice. That distinction should be stated in
   any published prose until the gap closes.
6. **A dated worked nativity.** T1299 contains no worked chart for a named person. The
   畢-rooted three-nine enumeration is a worked example of the *technique*, which is
   valuable, but it is not a reproduced judgment about a person. If any survive they will
   be in the Japanese kanmon record, not the Chinese text.
7. **The unequal mansion widths.** The ṛṣi concedes at T21.0388b24 that the mansions are
   wide and narrow while treated as equal quarters. The text never tabulates the real
   widths. T1308's 宿度法 is the obvious place to look, but it is a 28-mansion text and
   its degrees cannot be back-fitted into T1299's 27-fold scheme.
8. **Chapters not yet extracted.** 祕密雜占品第五 (T21.0392b03-c28, a body-part and
   miscellaneous divination chapter), 黑白月分品第六, 日名善惡品第七, the fascicle-2
   擇日/擇時 sections, the full 二十七宿所為吉凶曆 almanac (149 lines), 行動禁閉法,
   裁縫衣裳服著用宿法, and 釋大白所在八方天上地下吉凶法. These are additional election
   material, not additional structure, and none of them changes the mansion count or the
   three-nine table.
