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


---

## Cross-check: which other rules are genuinely blocked

Having got the Dorotheus availability wrong, the same question was re-asked for every
remaining rule by listing the actual scan collection rather than probing text layers.

**Genuinely absent from `tmp/acquire/pdfs/` — these rules really are blocked on acquisition:**

| rule | source needed | present? |
|---|---|---|
| `al_biruni_firdaria_seven_planet_core` | al-Bīrūnī, *Book of Instruction*, Arabic | no |
| `al_biruni_hayz_halb` | same | no |
| `ptolemy_doryphory_rank` | Tetrabiblos, Boll–Boer Greek | no |
| `ptolemy_perseus_algol` | same | no |
| `ptolemy_prorogation_distributor` | same | no |
| `lilly_reception` | *Christian Astrology* 1647 facsimile | no |
| `lilly_planetary_conditions` | same | no |
| `ibn_ezra_triplicity_life_thirds` | Ibn Ezra, Hebrew | no |
| `ibn_ezra_annual_revolution_core` | same | no |
| `firmicus_antiscia_major_configurations` | Firmicus, *Mathesis*, Latin | no — **but see below** |
| `picatrix_lunar_mansions_electional_scope` | *Ghāyat al-Ḥakīm*, Arabic | no |

So the al-Bīrūnī claim stands: those two are blocked. The Ptolemy claim also stands — the
three Ptolemy rules cite chapters that WERE read in the Greek earlier, but no Ptolemy scan is
in the collection now, so they cannot be re-checked or transcribed without re-acquiring it.

**One lead worth following:** Dorotheus Appendix I (printed ~427) is
*Fragmentum e Firmici Materni Mathesios libro II 29,2* — a Firmicus fragment, in this volume,
concerning **antiscia**. `firmicus_antiscia_major_configurations` is exactly an antiscia rule.
That appendix will not carry the whole of Mathesis II.29, but it is a primary witness to the
antiscia material and is on disk. Not yet read.

**Also on disk and unread**, bearing on no currently-registered rule but relevant to the
tradition: Hephaistio (Greek, 2 vols), Olympiodorus on Paulus (Greek), Abū Maʿshar's
*Mudkhal al-Kabīr* (Arabic), Sahl ibn Bishr, Bonatti (Latin 1550), Morin (1661),
Māshāʾallāh, Lydus, and three CCAG volumes.

---

## I.1 read in the Arabic (2026-08-11)

Located at Arabic printed pp. 3–4 (PDF pp. 10–11), rubric **⟨١⟩ باب. معرفة السبعة بالطول والعرض ومثلثات البروج وأربابها** — "knowledge of the seven in longitude and latitude, and the triplicities of the signs and their lords." The chapter numeral is Pingree's supplement in ⟨ ⟩; باب itself is in the manuscripts.

### The table as the Arabic gives it

| triplicity | day (بالنهار) | night (بالليل) |
|---|---|---|
| مثلثة الحمل — fire | Sun, Jupiter, Saturn | Jupiter, Sun, Saturn |
| مثلثة الثور — earth | Venus, Moon, Mars | Moon, Venus, Mars |
| مثلثة الجوزاء — air | Saturn, Mercury, Jupiter | Mercury, Saturn, Jupiter |
| مثلثة السرطان — water | Venus, Mars, Moon | Mars, Venus, Moon |

**Checked systematically against `DOROTHEAN_TRIPLICITY`: all four consistent.** Our tuple is stored `(day, night, participating)`, and Dorotheus's two orderings compress onto it exactly — the day-first lord fills the day slot, the night-first lord the night slot, and the third, which is the same in both orderings, the participating slot. The table is right.

Note the element names (نارية / ترابية / هوائية / مائية) are **not** in the text; the apparatus records them as `add. B`, present only in the Berlin manuscript. Our keys are element names, which is a convenience, not Dorotheus's own vocabulary.

### ⚠ The clause with no slot

> **وفي السنبلة أيضاً حظٌّ لعطارد** — *"and in Virgo, Mercury too has a share."*

This sits inside the earth-triplicity entry and is **sign-specific**: a fourth participant belonging to Virgo alone, not to Taurus or Capricorn. `DOROTHEAN_TRIPLICITY` is keyed by *element*, so there is no place to put it and no Virgo chart can express it.

**Deliberately not patched.** حظّ ("share", "portion") does not state a weight, and triplicity feeds dignity scoring — inventing a value would move every Virgo chart's totals on a guess. Recorded as a real, sourced gap for a decision, not silently filled.

### A narrow text/translation mismatch

Pingree's English at printed p. 161 prints the earth-triplicity night third as **"[then Mars]"**, and his own sigla mark `[]` as an editorial supplement. The Arabic at p. 4 line 2 prints **ثم المريخ** plainly — unbracketed, no ⟨ ⟩, no apparatus note. So the constituted Arabic presents as transmitted what the translation presents as supplied. Which side is inconsistent could not be settled from these pages; flagged rather than resolved.

### Still English-only

Chapters 5 and 22–24 (printed pp. 183–189), which this rule also cites for fortune and elevation, have **not** been read in the Arabic. The rule's status is therefore `arabic_text_read_directly_partial`, not a clean pass.
