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
