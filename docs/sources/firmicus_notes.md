# Firmicus Maternus, *Matheseos libri VIII* (Kroll–Skutsch, Teubner 1897)

Latin. Vol. 1 = 300 PDF pages. Pagination: `printed = pdf_page − 15` (verified against the running heads, e.g. pdf 94 carries `II 29,2—7` and prints 79).

---

## II.29 — antiscia. Printed pp. 77–84, PDF 92–99.

### The construction (II.29,3)

> *Initium antisciorum aut a Geminis et Cancro est aut a Sagittario et Capricorno … Gemini in Cancrum antiscium mittunt et Cancer in Geminos, Leo in Taurum et in Leonem Taurus, Virgo in Arietem et Aries in Virginem, Pisces in Libram et Libra in Pisces, Aquarius in Scorpium et Scorpius in Aquarium, Sagittarius in Capricornum et Capricornus in Sagittarium.*

The solstitial axis, six mutual pairs. **All six verified against `calculate_antiscia_points`.**

### The degree table (II.29,5–6)

Firmicus prints the whole Gemini/Cancer table degree by degree — I→XXIX, II→XXVIII, … XV→XV, … XXIX→I — and says it applies to every pair: *"Hoc itaque exemplum … ad omnium signorum antiscia pertinebit."*

**All 29 degree mappings verified exactly** against our formula `antiscia = (180 − λ) % 360`, reading his degree numbers as exact degree *points* (Gemini 1° → Cancer 29°, and 15° → 15° as the fixed point).

He also states the reciprocity explicitly: *"nam pars, a qua exceperit antiscium, ad eam a se rursus mittit antiscium"* — the degree it receives from, it sends back to.

### The 30th-degree exclusion (II.29,4)

> *in XXX. partem signi nulla pars mittat et quod XXX. in nullam partem mittat antiscium*

No degree sends its antiscion to the 30th, and the 30th sends to none. Under our continuous formula the 30th degree of a sign is the sign boundary itself (Gemini 30° = 90° = Cancer 0°), i.e. **degenerate rather than wrong** — it maps onto the boundary it sits on. Our implementation does not special-case it, and does not need to; recorded so that anyone comparing our output to Firmicus's printed table at that one degree knows why it looks different.

---

## ⚠ Source history: Firmicus points away from himself

> *[Ptolemy] quasi per speculum quidem antisciorum rationem attigit; **Dorotheus vero Sidonius**, vir prudentissimus et qui apotelesmata verissimis et disertissimis versibus scripsit, **antisciorum rationem manifestis sententiis explicavit, in libro scilicet quarto**.* (II.29,2)

**CORRECTION (made after cross-checking Pingree's fuller quotation of this passage).** The page read in the Firmicus volume begins mid-sentence, and the "as if through a mirror" clause was first attributed here to Ptolemy. It belongs to **Antiochus**. Firmicus's full sentence names three men: *Ptolemy* follows no principle but antiscia; *Antiochus*, saying Libra does not see Aries because of the earth between, touched the doctrine only "as if through a mirror"; and **Dorotheus of Sidon set it out plainly in his FOURTH BOOK**.

Our rule `firmicus_antiscia_major_configurations` cites Firmicus as its authority. Firmicus himself names Dorotheus IV as the clear source. **We now hold Dorotheus** (Pingree 1976, Arabic + English + Greek fragments), so that attribution is checkable — and the Dorotheus volume's own Appendix I is *Fragmentum e Firmici Materni Mathesios libro II 29,2*, i.e. Pingree prints this very passage as a witness to Dorotheus. The two volumes point at each other.

**Not yet done:** reading Dorotheus IV on antiscia to see whether his version agrees with Firmicus's table.

---

## The loop closes: Firmicus IS the surviving witness

Pingree prints this exact Firmicus passage in the *Carmen Astrologicum* as:

> **Appendix I: Fragmentum e Firmici Materni *Mathēseos* libro II 29,2 (II 29,2–9 = fr. 61 Stegemann) haustum**

He classifies it as a **fragment of Dorotheus**, with a canonical number — *fr. 61 Stegemann*.

An editor prints a *testimonium* in an appendix when the primary text is lost. **The antiscia chapter of Dorotheus IV does not survive in the Arabic Carmen.** Firmicus preserves it.

So `firmicus_antiscia_major_configurations` citing Firmicus is **correct and not second-best**. He is the surviving witness, and Pingree's own edition of Dorotheus says so. The earlier note here — that Firmicus "points away from himself" and the attribution was therefore unchecked — is resolved: it was checkable, it has been checked, and the answer is that there is nothing behind Firmicus to check against.

**This also closes the "read Dorotheus IV on antiscia" item.** There is no Dorotheus IV antiscia text to read.

---

# Book III located and sampled in the Latin (2026-08-11)

**The text layer is usable.** Unlike the Greek and Arabic scans, Firmicus's Teubner OCRs into legible Latin — running heads, apparatus and all. That makes this the **cheapest source in the collection to read at volume**: no page rendering, no image tokens, direct text extraction.

Mapping: PDF page ≈ printed − 15 (pdf 146 = printed 131). Running heads carry book and chapter, e.g. `III 5, 8–13`.

## What Book III is

**The planets in the twelve houses**, one chapter per planet, each running through all twelve places with sub-cases for aspects from benefics and malefics. Sampled III.5, the Sun:

> *Si vero nocte Sol in horoscopi signo fuerit inventus, **sordidiore genere facit procreari***

Sun in the 1st by night — **causes birth into a lowlier family**. With Saturn or Mars square, opposed or conjunct: *maiores fratres perimit* — **destroys the elder brothers**, and the patrimony with them. In any angle, the Sun *maiores fratres omnes debilitabit* — weakens all elder brothers — **or makes the native the firstborn**.

> *In secundo loco Sol ab horoscopo constitutus faciet **per semetipsos patrimonia quaerentes** … Sed hos eosdem **languidos** facit et **parvae vitae***

Sun in the 2nd — **self-made in acquiring patrimony**, pleasant and good throughout life; but **sickly and short-lived**, impeded by adversities, *semper in vita sua varia terroris trepidatione solliciti* — always anxious with a shifting trepidation of terror.

With Venus and Jupiter in trine, sextile or conjunction: *iacentes homines et abiectos ad rem publicam faciet incremento dignitatis adduci* — **raises men who are prostrate and abject to public dignity** — but *cum maximo impedimento … et cum patrimonii iactura voluntaria*, with the greatest impediment and voluntary loss of patrimony.

## Two things worth knowing before anyone mines this

**1. The volume is large and entirely unused.** Only `firmicus_antiscia_major_configurations` cites Firmicus, and only for II.29. Books III–VI are essentially all delineation — planets in houses, planets in aspect, the *sphaera barbarica*. That is hundreds of pages of specific, vivid material the engine does not draw on at all.

**2. The register is markedly more fatalistic than Ptolemy's, and it gives direct advice.** The Sun-in-2nd passage ends:

> *Unde quicumque sic Solem habuerit constitutum, **nihil adpetat, ad nullam rem audeat***

*"Whoever has the Sun so placed, let him **attempt nothing, dare nothing**."*

That is second-person directive counsel, and `_PROTECTED_DIRECTIVE` in the publication contract would block it on sight — correctly, since it is the engine telling a reader how to live. Anyone importing Firmicus delineations will hit this repeatedly: he does not merely describe, he instructs.

Compare Ptolemy at I.2–3, who insists the art is *conjectural, not affirmative*. **The two authors differ in kind, not just in table.** Firmicus asserts outcomes and prescribes conduct where Ptolemy hedges the whole enterprise. Recorded because that difference is an editorial decision for whoever mines this material, not a technical one — and because the contract will enforce Ptolemy's register whether or not the choice is made deliberately.

---

# ⭐ Firmicus III.25, *Quis deorum quot annos decernat* — the planetary years (2026-08-11)

PDF 88–90. Read from the text layer.

### He gives a METHOD before any number

> *Cum **datorem vitae** diligenter inspexeris, id est **dominum geniturae**, et videris, **quo sit in loco positus et in quali signo et in qualibus partibus**, sed et **dominus signi ipsius, in quo est vitae dator** constitutus, simili ratione perspexeris, **Solem quoque et Lunam** quatenus dator vitae et benivolae stellae respiciant, facile totius vitae poteris definire substantiam*

Inspect the **giver of life** — that is the **lord of the nativity** — its place, sign and degrees; then the **lord of the sign the giver occupies**, likewise; then how **the Sun, the Moon and the benefics** regard it. Only then is the number read.

> *Nam si et ipse dator vitae **bono in loco** sit positus et in bono signo et in bonis partibus, **integer annorum decernitur numerus**, praesertim si datorem vitae **Iuppiter in diurna genitura, Venus in nocturna** prospera radiatione sustentent*

**The full number is decreed only when the giver of life is well placed** — and especially when **Jupiter by day, or Venus by night**, supports it.

That is a **sect-conditional benefic support** on the years, structurally the same shape as Ptolemy's three rescues (III.11, III.13, III.15): the number is not a property of the planet but of the planet *in condition*.

### Three tiers, not two

Firmicus grades **bene / medie / male** — well, middlingly, badly:

| planet | *bene* | *medie* | *male* |
|---|---|---|---|
| Saturn | **57** | — | — |
| Jupiter | **79** | — | 12 (or 12 months) |
| Mars | **63** | — | 15 (or 15 months) |
| Sun | **120** | **45** | 18 |
| Venus | **84** | — | 8 yrs 8 days 12 hrs |
| Mercury | **108** | **79** | 20 (or 20 months) |
| Moon | **84** | — | 25 |

Note the *male* values are given with alternate units — *"XII annos aut menses XII et dies…"*, twelve **years or twelve months**. The badly-placed giver may yield the number in a smaller unit entirely.

### ⚠ Four of seven greatest-years disagree with `hyleg.PLANETARY_YEARS`

| planet | Firmicus | ours (`major`) | |
|---|---|---|---|
| Saturn | 57 | 57 | ✅ |
| Jupiter | 79 | 79 | ✅ |
| Sun | 120 | 120 | ✅ |
| **Mars** | **63** | **66** | ❌ |
| **Venus** | **84** | **82** | ❌ |
| **Mercury** | **108** | **76** | ❌ |
| **Moon** | **84** | **108** | ❌ |

The *minor* years all agree (30/12/15/19-18/8/20/25), so this is not a wholesale different tradition — the **least** years are the common inheritance and the **greatest** diverge.

**Mercury 108 and Moon 84 look transposed** against the standard set, where Mercury is 76 and the Moon 108. That may be Firmicus's tradition, a manuscript corruption, or my misreading of the Roman numerals — **I am not asserting which.** Today has already produced one numeral misreading caught only by a failing total, and this chapter prints no summation to check against.

**Not changed.** Our table is the standard Arabic-Latin set and is internally consistent; Firmicus is one witness among several and the divergence needs a second source before anyone touches numbers that feed published longevity figures. Recorded as a sourced discrepancy for a decision.

### What is worth taking regardless of the numbers

**The three-tier structure and its condition.** Our `PLANETARY_YEARS` carries `minor`/`mean`/`major`, and `hyleg.py` selects among them — but Firmicus states the *criterion* explicitly: the full number requires the giver of life well placed **by place, sign and degree**, with its dispositor examined, and benefic support **by sect**. That is a checkable rule, and it is the same architecture as the Ptolemaic rescues found earlier today.
