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
