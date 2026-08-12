# Dorotheus of Sidon, *Carmen Astrologicum* (Pingree, Teubner 1976)

**Scope:** 234 PDF pages, each a two-page spread. Printed pagination runs to at least p. 431.
Formula derived from the scan: `printed_left = pdf_page * 2 - 18` (verified at pdf 221 → printed 424/425).

---

## What this volume actually contains

Dorotheus's Greek original is lost. The text survives through a Pahlavi intermediary into ʿUmar al-Ṭabarī's Arabic, with Greek fragments preserved by later authors. This edition carries **all three layers**, and all three are in the scan:

| layer | where | status |
|---|---|---|
| **Arabic** (ʿUmar's translation — the earliest continuous witness) | PDF ~10–88, printed ~1–160, right-to-left with apparatus | **present** |
| **English** (Pingree's translation) | printed 161 onward | present |
| **Greek fragments** (Hephaistio, Firmicus) | Appendices I–II, printed ~424–431 | **present** |

Also present at printed ~431: a table of **Ὅρια κατὰ Δωρόθεον** — Dorotheus's bounds.

---

## ⚠ A methodological correction worth keeping

I twice concluded this source was unavailable in its original language, and was twice wrong, for the same reason.

**The probe was:** extract the PDF text layer and count Arabic (U+0600–U+06FF) and Greek (U+0370–U+03FF) codepoints. It returned **zero of both** across five sampled pages.

**The reality:** the volume is dense with Arabic *and* Greek. The scan's OCR simply fails on non-Latin script and emits garbage Latin characters instead — so a codepoint count of zero is exactly what a page *full* of Arabic produces.

**The rule:** a text-layer probe can prove a script is PRESENT; it can never prove one is ABSENT. To establish absence, render the page and look at it. This is the same trap as declaring a source missing without searching — the negative result feels like evidence and isn't.

---

## The rule that rests on this source

`dorotheus_sect_light_triplicity_fortune` — cites "Chapters 1, 5, and 22–24; Teubner pp. 161–162 and 183–189".

**Printed p. 161 located and read (PDF p. 89).** It is Pingree's *English*, and it carries the triplicity doctrine directly:

> *Know the lords of the triplicities of the signs: the lords of the triplicity of Aries by day are the Sun, then Jupiter, then Saturn, by night Jupiter, then the Sun, then Saturn; the lords of the triplicity of Taurus by day are Venus, then the Moon, then Mars, by night the Moon, then Venus…* (I.1, printed p. 161)

So the citation is accurate, but **pp. 161–162 are the translation, not the original**. Verifying this rule against the original means reading the corresponding Arabic in the first ~160 printed pages, which is now known to be available.

**Status:** `translation_inspected` remains correct and honest. It is NOT upgraded on the strength of having found the Arabic — finding a source is not reading it.
