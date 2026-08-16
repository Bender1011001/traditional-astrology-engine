# *Ghāyat al-Ḥakīm* (Picatrix), Ritter's critical edition — Arabic

Acquired 2026-08-11. 438 PDF pages. Warburg Institute Digital Collection scan.

## Verified: this is Ritter, not a reprint

The archive.org listing gives only "Picatrix Arabic", 2021, no editor, sitting in a mixed
upload beside a prize-bond leaflet and a pendulum manual. **Rendering a page settles it**:
the Arabic carries Ritter's full critical apparatus with his sigla — `LCVW`, `om. C`,
`Mon.` (the Hebrew witness, in Hebrew type), `Pic.` (the Latin *Picatrix*). That is the
critical edition, not a popular reprint.

Sample content at PDF ~120: **استجلاب قوة القمر في برج الثور** — drawing down the Moon's
power in Taurus — i.e. the astral-magic operations by sign.

## Pagination — SOLVED, and it runs BACKWARDS

**No usable text layer.** The only extractable text is the Warburg watermark; the Arabic
does not OCR at all, so every page must be read visually.

**The mapping, verified at two widely separated points:**

| composite page | folio read |
|---|---|
| 101 | **٣١٧ = 317** |
| 251 | **١٦٩ = 169** |

As the PDF advances, the folio **descends**. The scan is in physical page order, but the
Arabic binds right-to-left, so PDF page 1 is the *last* page of the text.

> **folio ≈ 418 − composite_page**

Measured slope −0.9867 folio per page over a 150-page span, i.e. ~2 pages of drift from
unnumbered plates. Good enough to land within a page or two of any target; confirm the
folio on arrival.

### A retraction of a retraction

An early pass read folios **٢٩٧/٢٩٨** around PDF 120. A later note in this file called that
"most likely a misreading of ١١٩/١٢٠", on the strength of a strip-crop experiment that
seemed to show PDF 20 = folio 20.

**The original reading was correct.** 418 − 120 = 298. The *retraction* was the error.

Two lessons, both cheap to state and expensive to relearn:
- The strip crop that produced "PDF 20 = folio 20" was landing on **something that was not a
  folio number** — a line number or apparatus marker. A number in roughly the right place on
  the page is not the same as the number you are looking for.
- Automated folio extraction failed three times here: fixed-fraction crops at two different
  bands (blank — the text block floats), and ink-detection (which locked onto the **Warburg
  watermark**, a grey wash across the whole page, and reported the page bottom). **Render the
  full page and read it.** Two full-page renders settled what six heuristic attempts could not.

## The rule this blocks

`picatrix_lunar_mansions_electional_scope` — the 28 lunar mansions and their electional
uses. Not located in the volume yet. Status stays `translation_inspected_partial_boundaries`;
acquiring the Arabic does not upgrade it.

---

## Mansions 2–5 read in Ritter's Arabic — boundaries exact, contents divergent (2026-08-11)

Pages 404–405 (folios 15–16). Each entry gives its span **to the arc-second**, then its uses.

### The boundaries are exactly right

Ritter prints mansion 2 as **12°51′26″ Aries → 25°42′52″ Aries**. One twenty-eighth of the zodiac is **12°51′26″**. Checked against `LunarMansionEngine.MANSION_WIDTH = 12.8571428571`:

| mansion | our start | Ritter | |
|---|---|---|---|
| 2 al-Buṭayn | 12.857143 | 12°51′26″ | exact |
| 3 al-Thurayyā | 25.714286 | 25°42′52″ | exact (1″ rounding) |
| 4 al-Dabarān | 38.571429 | 8°34′17″ Tau | exact |
| 5 al-Haqʿa | 51.428572 | 21°25′43″ Tau | exact |

The arithmetic is equal 1/28 tropical division, and it matches to the arc-second.

### ⚠ The intents do not match the Arabic

**Mansion 2, al-Buṭayn.** Ritter: *يصنع فيها طلسمات **لحفر الآبار والانهار** واستخراج المطالب والكنوز المدفونة وطلسمات **لنمو الزرع*** — talismans for the **digging of wells and rivers**, the extraction of buried objects and treasures, and the **growth of crops**.

Ours reads **"polluting rivers and waters"**. حفر is *digging/excavating*, not polluting. Treasure and crops match; the first item does not.

**Mansion 4, al-Dabarān — this one is close to inverted.** Ritter: *طلسم **لفساد حال مدينة** … **لبناء لا يرجى بقاؤه** … **لفساد الزرع** … لحفظ الرقيق لمالكه … **لافساد ما بين الزوجين** والقاء القطيعة … **وعقد الحيات والعقارب*** — for **ruining a city's condition**, for **a building not expected to last**, for **corrupting crops**, keeping a slave for his owner, **corrupting what is between spouses**, and **binding snakes and scorpions**. فساد (ruin, corruption) recurs throughout.

Ours reads: *"employing others, building and construction, investing capital, obtaining offices and positions"* — constructive where the Arabic is destructive.

**Mansions 3 and 5 partially match.** Sea travel, love, education, marriage and journeys are all present in both. But ours adds items I did not find in the Arabic (*"making medicine", "favor from kings and officials", "divinatory dreams"*) and omits ones that are there (corrupting partnership, alchemy, land hunting, releasing **and** binding prisoners).

### Where the divergence probably comes from

Each entry carries `"source_refs": ["Picatrix Bk I, Ch 4", "Medieval Astrology Guide"]`. **The second reference is not a primary source.** The content that disagrees with Ritter is most likely from there, cited alongside Picatrix as though both were equal authorities.

This is the same failure the project already records for fixed stars — modern popularisation shipping under a primary-source citation.

### What was NOT done, and why

**The table was not rewritten.** Four of twenty-eight mansions have been read. Correcting a few entries from a partial reading would leave the table half in one tradition and half in another — the exact blend the project's own rule forbids. All 28 need reading in one pass before any rewrite.

### A doctrinal condition worth capturing when that happens

Mansion 5 carries an explicit gate: the marital-harmony talisman works *اذا كان القمر والطالع في **برج صور بني آدم** صالحا بريئا من النحوس والاحتراق* — **if the Moon and Ascendant are in a sign of human form**, sound and free of malefics and combustion. Ritter names them: **الجوزاء والسنبلة والميزان والدلو والقوس** — Gemini, Virgo, Libra, Aquarius, Sagittarius. The engine has no human-form-sign concept.

---

## Mansions 6–12 read — the divergence is systematic (2026-08-11)

Folios 17–18 (pages 402–403). With 2–5 already read, **11 of 28 mansions** are now compared against Ritter. The pattern is not random error.

| # | name | Ritter's Arabic | ours |
|---|---|---|---|
| 6 | al-Hanʿa | **corrupting cities and besieging them**, vengeance against kings, **destroying crops**, trusts and deposits, improving partners, land hunting, **corrupting the working of medicines when taken** | war, seeking justice, pursuing enemies, travel, forming partnership |
| 7 | al-Dhirāʿ | **growth of trade and its blessing**, growth of crops, traveller's safety **in water**, improving what is between friends and partners, **binding flies**, attaining a wish **from the sultan**, the runaway slave | agriculture, **washing or purifying the body**, reconciliation with enemies |
| 8 | al-Nathra | love and friendship **between those who hate each other**, traveller's welfare, **prolonging the binding of prisoners**, **driving away mice and bedbugs** | love and friendship, safe travel, friendship **between allies** |
| 9 | al-Ṭarf | **corrupting farms**, tearing travellers' veils, **severing partners**, imprisoning the adversary | capturing individuals, **fortifying gates and defences** |
| 10 | al-Jabha | marital harmony, **harming an enemy**, **binding the prisoner**, stability of what is built, partners' agreement | **healing of illness**, **ease of childbirth**, marriage, building |
| 11 | al-Zubra | **releasing prisoners and captives**, **besieging cities**, growth of trade, stability of buildings | building, **renting lands**, agriculture, marriage, **putting on new garments** |

### The bias has a direction

Two consistent movements, across every mansion checked:

**Omitted from ours** — the political and destructive: besieging cities, vengeance against kings, corrupting crops, severing partners, binding and releasing prisoners, corrupting medicines. Mansion 11's *releasing prisoners* is Ritter's **first** listed use and is absent from ours entirely.

**Added to ours** — benign domestic material with no counterpart in the Arabic: healing illness, ease of childbirth, washing the body, putting on new garments, fortifying defences, seeking justice.

One inversion of sense worth noting on its own: mansion 8 in Ritter makes friendship **between those who hate each other** (المتباغضين) — reconciling enemies. Ours reads *"creation of friendship between allies"*, which is close to the opposite claim and much weaker.

**This reads as a sanitised, domesticated recension** — a talismanic magic text with the coercive and political operations filed off. That is a coherent editorial choice by whoever compiled the "Medieval Astrology Guide" our `source_refs` names second, but it is **not Picatrix**, and it currently ships cited as Picatrix.

### Recommendation, now that the sample is large enough

11 of 28 is enough to say the table's *contents* are not from the cited source, while its *boundaries* are exactly right. Three options, in order of how well they hold the project's own source-fidelity rule:

1. **Read all 28 and rewrite from Ritter.** Correct, and the remaining 17 are on disk. Roughly one more focused pass.
2. **Suppress mansion intents from customer output** until (1) is done, keeping the boundaries, which are sound. Stops shipping unsourced electional advice today.
3. **Relabel** `source_refs` honestly as a modern compilation and drop the Picatrix citation. Cheapest, but leaves the content in.

Doing nothing is the one option inconsistent with the rest of the project: every other rule in the registry now states exactly which edition it was read from.

---

## Mansions 26–28, and the rule that governs the whole system (2026-08-11)

Folios 23–24 (pages 396–397). **26** al-Fargh al-Muqaddam (21°25′44″ Aqu → 4°17′10″ Pis): *talismans of good in its entirety*, joining souls in affection, stability of buildings, **safety of travellers in ships**, and corrupting what is between partners. **27** al-Fargh al-Muʾakhkhar (→ 17°8′36″ Pis): growth of trade, **speed of recovery from illness**, destroying the wealth of whom you wish, **harm to those riding ships**, prolonging confinement. **28** al-Rishāʾ (→ end of Pisces): growth of trade and crops, healing, **reconciliation between spouses**, binding prisoners, harm to ship-riders.

Note 27 and 28 are near-mirrors on the sea: one harms ship-riders, the other keeps the traveller safe.

### ⚠ Two findings in the closing passage that govern everything above

**1. Picatrix attributes the whole 28-mansion system to India.**

> *وهذه الصور الثماني والعشرون **معوّل اهل الهند** عليها في محاولاتهم **واختياراتهم**، هكذا وجدنا فيما طالعناه من كتبهم في هذا الشأن*

"These twenty-eight figures are what **the people of India** rely upon in their operations and their **elections** — thus we found in what we have perused of their books on this matter."

The author is reporting a foreign system, not asserting his own. And he names its use outright: **اختيارات, elections.**

**2. There is a governing Moon condition on every mansion election, and we implement none of it.**

> *والعمدة فيما قدّمناه ان يكون **القمر** فيما تحاوله من **اعمال الخير نقيًّا من النحوس والاحتراق متصلًا بالسعود**، وفي ابتدآت الاعمال تجعله **منصرفًا عن سعد متصلًا بسعد**، وفي **اعمال الشرّ بعكس هذا***

"**The cardinal rule** (al-ʿumda) in what we have presented is that the Moon, in what you attempt of **works of good**, be **pure of the malefics and of combustion, applying to the benefics**; and at the beginnings of works, make it **separating from a benefic and applying to a benefic**; and in **works of evil, the reverse of this.**"

This is a hard gate on the entire chapter. A mansion does not simply "mean" its uses — the operation requires the Moon to be unafflicted, uncombust, and applying to a benefic. The engine reports mansion intents with **no Moon condition at all**.

It also states plainly that the system covers **اعمال الشرّ, works of evil**, with the conditions deliberately reversed. That is the strongest possible confirmation that our sanitised table (see the previous two entries) is not this text: the source is explicit that half its operations are malefic, and says how to time them.

### Status: all 28 mansions now located, 2–12 and 26–28 read in detail

Enough to act on. The recommendation stands and hardens: the boundaries are exact and should be kept; the intents are from a modern compilation and should either be rewritten from Ritter or suppressed from customer output. Any rewrite must carry the ʿumda condition above, or it will publish talismanic operations without the gate their own source puts on them.

---

## Mansions 16–22 read — a direct inversion, and a missing signature clause (2026-08-11)

Folios 20–21. **22 of 28 mansions are now compared at full depth** (1–12, 16–22, 26–28); 13–15 and 23–25 are read at name-and-span level only.

| # | Ritter's Arabic | ours |
|---|---|---|
| 16 al-Zubānā | **فساد المتاجر — corrupting trade**, corrupting plantings and farms, severing friends and spouses, punishing a wife if her husband wishes, **freeing the prisoner from his bonds** | **"making money through buying and selling"**, prosperity, favour from authorities |
| 17 al-Iklīl | improving livestock, besieging cities, stability of building, traveller's safety in water — **and the friendship clause below** | placement of armies, strong buildings, safety of sailors |
| 18 al-Qalb | **binding banners for kings** for victory over their enemies, **preservation of kings**, stability of buildings, growth of plantings, discord among partners; *whoever marries while the Moon is here **with Mars**, she will be thayyib* | building, renting and purchasing land, getting promoted, eastward journeys |
| 19 al-Shawla | besieging cities, victory over enemies, destroying wealth, **the slave's escape from his master**, **wrecking and breaking ships**, **escape of the prisoner and captive** | sieges, litigation, land journeys, planting trees, **hurrying the menses of women** |
| 20 al-Naʿāʾim | taming a difficult beast, speed of travel, **drawing whom you desire** and affection, **constricting prisoners**, corrupting partners | **"hunting on land"** — one item against Ritter's five |
| 21 al-Balda | stability of buildings, growth of crops, preserving wealth and livestock for their owners, travellers' safety, and **a talisman for a woman divorced from her husband so that she never marries after him** | strengthening buildings, planting, big purchases |

### Mansion 16 is a straight inversion

Ritter opens it with **فساد المتاجر**, *the corruption of trade*. Ours opens with *"making money through buying and selling"*. Not a softening — the opposite claim, in the first listed use.

### Mansion 17 drops the clause that defines the mansion

> *واجمعوا انّ من صادق صديقًا والقمر في هذه المنزلة فان **صداقته لا تنقطع** فلأجل ذلك **يختارونها لطلسمات المصادقة***

"**They agreed** that whoever befriends a friend while the Moon is in this mansion, **his friendship will not be severed** — and for that reason **they elect it for talismans of friendship**."

Ritter states outright that this is *why* the mansion is chosen. Ours omits friendship from mansion 17 entirely.

### The suppressed material is consistently the coercive material

Mansions 16, 19 and 21 each carry an operation aimed at a person against their will — punishing a wife at her husband's request, a slave's escape, wrecking ships, and a divorce-curse ensuring a woman never remarries. **None of these appear in our table.** Nor do the royal operations of 18 (binding banners for kings, preserving kings), nor the erotic compulsion of 20 (*drawing whom you desire*).

This is now beyond doubt about its direction. The table is a **deliberately sanitised recension** of a talismanic magic text — a defensible editorial choice by whoever made it, and not a defensible citation of Picatrix.

### Final verdict on this rule

- **Boundaries: verified exact.** Keep them.
- **Chapter citation: correct.** Book I ch. 4, Arabic *fasl (4)*.
- **Intents: not Picatrix.** 22 of 28 checked; divergence is systematic, directional, and includes at least two outright inversions of sense (16 trade, 8 friendship).
- **Two source conditions unimplemented:** the *ʿumda* Moon gate, and the attribution to India.

Registry status `arabic_text_read_directly_boundaries_only` reflects exactly this and should not be rounded up.

---

## All 28 read — correcting my own verdict, and one concrete data bug (2026-08-11)

Mansions 13–15 and 23–25 read at depth. **The audit now covers 28 of 28**, and it forces a correction to what I wrote two entries ago.

### I overstated "systematic sanitisation". The divergence is not uniform.

Several mansions match Ritter closely:

| # | Ritter | ours | |
|---|---|---|---|
| 13 al-ʿAwwāʾ | growth of trade, growth of crops, **releasing the prisoner**, connection with kings | increasing trade and money, increase of harvests, **liberation** | good |
| 14 al-Simāk | marital harmony, **completing recovery through treatment**, ship-riders' welfare | causing marital love, **curing the sick**, helping sailors | good |
| 15 al-Ghafr | **حفر الآبار والكنوز — digging wells and treasures**, obstructing the traveller, separating spouses, ruining dwellings | **"digging wells and canals"**, healing, employment, moving house | opening matches |

So the table is a genuine transmission with real fidelity in places, not a wholesale substitution. My earlier "deliberately sanitised recension" was too strong a claim from a partial sample, and I am withdrawing it as a blanket characterisation. What is true is narrower: **specific entries diverge, several badly, and the coercive material is disproportionately among the missing.**

### Mansion 2's "polluting" is an internal contradiction, not a translation policy

Mansion 15 in **our own table** renders حفر الآبار as **"digging wells and canals"** — correctly. Mansion 2 renders the same phrase حفر الآبار والانهار as **"polluting rivers and waters"**. The table gets the word right in one entry and wrong in another, which proves the mansion 2 reading is **an error in that entry**, not a consistent editorial stance. That is a one-line fix.

### ⚠ A concrete data bug: mansions 24 and 25 are duplicates in our table

Ours reads, for both:

> 24 Saʿd al-Suʿūd — *sieges, seeking fights, taking revenge on enemies*
> 25 Saʿd al-Akhbiyah — *sieges, seeking fights, taking revenge on enemies*, safety in travel

Ritter's two are **entirely different from each other**:

- **24 Saʿd al-Suʿūd** — *improving trade*, improving the spouses' arrangement, **victory of armies and raiding parties**, corrupting partners, **freeing the bound**; and *whoever attempts a craft in it, what he attempts is spoiled and not completed*.
- **25 Saʿd al-Akhbiya** — **besieging cities**, harming enemies and victory over them, **talismans for sending messengers and spies**, severing spouses, corrupting crops, **عقد الزوج وجميع الاعضاء — binding the husband and all his members** (impotence magic), binding the prisoner, founding buildings.

Our 25 is a fair match for Ritter's 25. **Our 24 is a copy of our 25** and bears no relation to Ritter's 24, which is largely benefic. This is not a translation dispute — it is a duplicated entry, and it means every chart with the Moon in Saʿd al-Suʿūd currently receives the wrong mansion's electional advice.

### Revised final verdict

- **Boundaries: exact.** Verified to the arc-second across all 28.
- **Chapter citation: correct.**
- **Intents: mixed fidelity.** Some entries good (13, 14, 15, 25), some diverging, at least two inverted in sense (16 trade, 8 friendship), one internally contradictory (2 vs 15), and **one duplicated (24 = 25)**.
- **Two source conditions unimplemented:** the *ʿumda* Moon gate; the attribution to India.

The duplicate at 24 is worth fixing on its own merits regardless of the larger rewrite decision — it is a plain bug with a known correct value.

---

## ⚠ RETRACTION: several "missing" claims above were my own truncation artifact (2026-08-11)

**Three of the absence claims in the entries above are wrong, and the error is mine.**

When comparing our table against Ritter I printed our `intents_good` truncated to ~86 characters. Several mansions have lists longer than that, so material I reported as *absent* was simply past the cut. Checked against the full lists:

| mansion | what I claimed | reality |
|---|---|---|
| 6 al-Hanʿa | "MISSES besieging cities" | **present** — *"besieging cities and castles"*, and *"exact revenge on enemies"*, and *"excellent hunting"* (171-char list; I saw 88) |
| 11 al-Zubra | "*releasing prisoners* is Ritter's **first** listed use and is **absent from ours entirely**" | **present** — *"redemption of captives"*, plus *"voyages and maritime trade"* and *"gaining by merchandise"* for Ritter's growth of trade (164-char list) |
| 17 al-Iklīl | "omits friendship from mansion 17 entirely" | the entry ends *"ordinary durability **loves**"* — garbled, but the friendship material is evidently there, not omitted |

**This is the same error as the text-layer probe earlier in the day**: concluding *absence* from an incomplete view. A truncated list can prove something is PRESENT; it can never prove something is ABSENT. I drew the stronger conclusion from the weaker evidence twice in one session.

### What survives the correction

Claims made from lists short enough to be shown in full, or verified by dumping the whole entry:

- **Mansion 16 is still an inversion.** Its full list is 75 chars — *"making money through buying and selling, prosperity, favour from authorities"* — against Ritter's **فساد المتاجر**, the corruption of trade. Nothing was cut.
- **Mansion 20 is still thin.** Its entire list is 15 characters: *"hunting on land"*, against Ritter's five operations.
- **Mansion 21 still lacks the divorce-curse.** Full list is 70 chars.
- **Mansion 2 "polluting" vs mansion 15 "digging"** — both short lists, the internal contradiction stands.
- **The 12/24 duplicates** — verified by dumping complete entries as JSON, not by truncated print. Those fixes stand.

### What does NOT survive

**The characterisation that the coercive and political operations are systematically absent.** Mansions 6 and 11 carry besieging cities, revenge on enemies, and redemption of captives. The table is closer to Ritter than my earlier entries claim, and I have now overstated the divergence twice — first as "deliberately sanitised", then again after partially withdrawing that.

**Revised position, stated conservatively:** the boundaries are exact; two entries were duplicated and are fixed; at least one entry (16) inverts its source and one (20) is severely thin; the rest require a careful full-list comparison that has NOT yet been done properly. The earlier per-mansion tables in this file should be re-derived against untruncated data before any rewrite decision rests on them.
