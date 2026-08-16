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
