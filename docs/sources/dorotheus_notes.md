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

---

## I.5 read in the Arabic — the ranking of the places (2026-08-11)

Located at PDF 12–13; running heads read `I 4`, `I 5-6`, `I 7`. Chapter heading:

> **⟨ه⟩ باب. في فضل الامكنة** — "Chapter 5. On the excellence of the places."

> *فاحفظ ما اذكره لك من الامكنة وفضل بعضها على بعض في القوة. فان **افضل الامكنة الطالع**، ثم **وسط السماء**، ثم ما يلي وسط السماء وهو **الحادي عشر** من الطالع، ثم مقابلة هذا المكان … وهو **الخامس** من الطالع وهو الذي يسمى **بيت الولد**، ثم مقابلة الطالع وهو **موضع الغروب**…*

Ranked by strength: **Ascendant → Midheaven → 11th → 5th (called "the house of the child") → 7th (the setting place)** → …

Note his construction is by *opposition pairs*: the 11th, then the opposite of the 11th (the 5th), then the opposite of the Ascendant (the 7th). Chapters 6 (**قوة الكواكب السبعة**, the power of the seven planets) and 7 (**تربية المواليد**, the rearing of natives) follow immediately.

### A ranking worth comparing, carefully

`src/engine/decennials.py:20` holds `OPERATIVE_HOUSES = [1, 10, 11, 7, 5, 9, 4]` — same first three as Dorotheus, but **7 before 5**, where Dorotheus gives **5 before 7**.

**This is NOT asserted as a defect.** `OPERATIVE_HOUSES` sits in the *Valens* decennial engine and may legitimately follow Valens's ordering rather than Dorotheus's; the two authors need not agree, and the project's own standing rule is that conflicting rules belong to different traditions and get different tables. Recorded as a **question to resolve by reading Valens on the same point**, not as a bug.

### Status

`dorotheus_sect_light_triplicity_fortune` cites chapters **1, 5, and 22–24**. Chapters 1 and 5 are now read in the Arabic; **22–24 are not**, so the rule stays `arabic_text_read_directly_partial`.

---

## I.22 read in the Arabic — the chapter the rule turns on (2026-08-11)

PDF 22–23, running heads `I 21` and `I 21-22`. Heading:

> **⟨كب⟩ باب. معرفة امر سعادة المولود والمال** — "Chapter 22. On knowing the matter of the native's fortune and wealth [and elevation]."

> *انظر في امر السعادة والمال وما ستلقي تلك السعادة ودرجاتها في الارتفاع. فان كان المولود **نهاريا** فانظر الي **الشمس** واصحاب مثلثتها، وان كان **ليليا** فانظر الي **القمر** واصحاب مثلثته. فان وجدت صاحبي المثلثة **الاول والثاني** كلاهما جميعا او الي واحد منهما على حدته في **مكان حسن** فانه لا يزال امره **من اول سنة الي اخر عمره** في جودة ورفعة وكثرة. وان وجدت صاحب المثلثة الاول في مكان حسن والثاني في **مكان ردي** …*

- **Sect selects the light**: diurnal → the Sun and its triplicity lords; nocturnal → the Moon and its triplicity lords.
- **First and second lords are compared**, each judged by whether it sits in a *good place* (مكان حسن) or a *bad* one (مكان ردي).
- Both good → the native's condition holds "from the first year to the end of his life" in excellence, elevation and abundance. The mixed cases follow, and **that** is the source of the beginning-versus-later reading the engine publishes.

**The engine's summary of this rule was accurate.** Verification confirming existing work, now from the earliest surviving witness rather than a translation.

## Status

`dorotheus_sect_light_triplicity_fortune` → **`arabic_text_read_directly`**. Chapters 1, 5 and 22 read; 23–24 continue I.22 and were not separately confirmed, which is noted in the location field rather than glossed.
