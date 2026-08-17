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

---

# ⭐ Firmicus IV.17, *De loco et de efficacia Fortunae* — the sect question settled (2026-08-11)

PDF 252–253.

> *In omni genitura **nocturna** computa **a Luna usque ad Solem**, in **diurna** genitura **a Sole** computa rursus **ad Lunam**, et quantuscumque signorum fuerit numerus, tanta **ab horoscopo** incipiens signa numera*

**In every nocturnal nativity count from the Moon to the Sun; in a diurnal nativity from the Sun to the Moon** — then that many from the ascendant.

## Firmicus reverses by sect. That makes Ptolemy the outlier, confirmed.

Earlier this session, Ptolemy IV.2 was read insisting the arc runs Sun→Moon *πάντοτε*, **always**, *"both for those born by day and for those born by night"* — and `lots.py` was noted as diverging from him.

**A third independent witness, read in its own original language, now sides with the engine:**

| author | day | night | read in |
|---|---|---|---|
| **Ptolemy** (IV.2) | Sun→Moon | **Sun→Moon** | Greek |
| **Dorotheus** | Sun→Moon | Moon→Sun | Arabic |
| **Paulus** (ch. 23) | Sun→Moon | Moon→Sun | Greek |
| **Firmicus** (IV.17) | Sun→Moon | **Moon→Sun** | Latin |
| **our `lots.py`** | Sun→Moon | Moon→Sun | — |

Three of four majority authors reverse; Ptolemy alone does not. **The engine follows the majority, and that is now demonstrated from three originals rather than assumed.** The earlier note calling this "the highest-impact divergence found in the session" stands as a *doctrinal* fact about Ptolemy, but it is no longer a reason to doubt our implementation — he is the minority view and knowingly so.

## And a methodological instruction we already satisfy

> *Sed haec **platica** computatio est, quam ideo posuimus, ne quid a nobis praetermissum esse videatur; **partiliter** vero locus Fortunae ista ratione colligitur, **quam tu sequi in omni disputatione debebis***

"But this is the **platic** [whole-sign] computation, which we set down lest anything seem omitted; the place of Fortune is properly gathered **partilely** [by exact degree], **which you ought to follow in every discussion**."

Firmicus records the whole-sign shortcut and then tells the reader **not to use it**. `calculate_lot` works in absolute longitudes throughout, so the engine already does what he instructs — verification confirming existing practice.

## A topical lot system, listed

> *Sic **vitam**, sic **spem**, sic **fratres**, sic **parentes**, sic **filios**, sic **valitudines**, sic **coniugem**, sic **mortem**, sic **actus**, sic **amicos**, sic **inimicos**, sic cetera omnia*

Life, hope, brothers, parents, children, health, spouse, death, actions, friends, enemies — each with its own partile lot, *"and all the rest that are required in the substance of the human race."*

`LotName` already carries Life, Siblings, Father, Mother, Children, Sickness, Marriage, Death, Friends and Enemies. **Ten of Firmicus's eleven are present.** The one absent is ***spes*, hope** — which is interesting, because the 11th place in the Hellenistic scheme is *Ἀγαθὸς Δαίμων* and carries hopes; a Lot of Hope would be its degree-precise counterpart. Recorded as a gap, not built: Firmicus names it here without giving its formula, and the formula would have to come from elsewhere.

---

# ⭐ Firmicus IV.19, *De domino geniturae* — four methods for the chart lord, and his own is none of ours (2026-08-11)

PDF 258–259.

> *geniturae dominum, quem Graeci **oecodespoten** vocant … ipse enim **totius geniturae possidet summam** et ab ipso **stellae singulae decreti licentiam sortiuntur***

The lord of the nativity, whom the Greeks call *oikodespotes* — **he possesses the sum of the whole nativity, and from him the individual stars receive the licence of their decree.** That is a stronger claim than "chart ruler": the other planets' verdicts are *licensed* by him.

## The condition test, and its link to the planetary years

> *qui si **bene fuerit collocatus** in his, in quibus **gaudet** signis vel in quibus **exaltatur**, vel in **domiciliis suis** … nec **malivolarum nociva radiatione pulsatus** nec **benivolarum stellarum praesidio destitutus**, omnia bona … decernit **et integrum annorum numerum**. Si vero **impeditus a malivolis vel a benivolis desertus** fuerit, **omnis eius efficacia debilitata languescit***

Well placed — in signs of **joy**, **exaltation**, or **own domicile** — of his own sect, **neither struck by malefic radiation nor deserted by benefic protection** — he decrees all goods **and the full number of years**. Impeded by malefics *or* **deserted by benefics**, **all his efficacy weakens and languishes**.

That is the **same rule as III.25** stated a second time, and it settles what "*bene collocatus*" meant there. Note the **double condition**: malefic absence is not sufficient; **benefic protection must be present**. Fifth instance today of that architecture — Ptolemy's three rescues, Firmicus's years, and now this.

## Four historical methods, recorded as such

1. ***Quidam*** — the planet in the **principal places (angles)** found in **its own signs or its own terms**.
2. ***Alii*** — the planet **in whose terms the Sun by day, or the Moon by night, is found** — *"et habet rationem,"* and it has reason.
3. ***Alii*** — the lord of the **Moon's exaltation**.
4. ***Alii*** — the lord of **the sign the Moon enters next** after birth, leaving the one she is in.

> *Sed et nos **hanc rationem sequimur**; haec enim est **verissima et ab omnibus comprobata***

**"And we too follow THIS method; for it is the truest and approved by all"** — referring to the immediately preceding, **the fourth**: the ruler of the sign the Moon next enters.

## ⚠ This is a fork on the most central determination in the chart

Our `AlmutenEngine` computes the chart lord by **summing five essential dignities in points** — the Ibn Ezra / Arabic-Latin method. Firmicus's preferred method is **not that, and not any of his other three either as we implement them**: it is a single, purely lunar criterion requiring no scoring at all.

**Not a defect.** Ours is a legitimate and later-standard method, and the engine's almuten is correctly attributed. But it is worth knowing that:

- **the chart ruler is not a settled question in the tradition** — Firmicus lists four live methods in the fourth century and picks the simplest;
- **his second method is close to something we already compute** — the term-lord of the sect light — which appears in the engine's dignity chain without being elevated to chart lord;
- and his verdict *"verissima et ab omnibus comprobata"*, truest and approved by all, is **exactly the kind of claim the project's own standards treat with suspicion**, since three rival methods are listed on the same page.

Recorded as a sourced fork on a determination the report presents as settled. **The honest surface would be one line noting that the chart lord is method-dependent and naming which method we run** — the same treatment the dignity tables already get in "Where the Sources Differ."

---

# ⭐ Firmicus IV.21, *De actibus* — independent confirmation of Ptolemy's three (2026-08-11)

PDF 275–276.

> *Sunt autem, qui **actus decernunt hominibus, Mars Venus et Mercurius***

**"There are those who decree actions for men: Mars, Venus, and Mercury."**

That is **exactly** Ptolemy IV.4's restriction, arrived at independently — a different author, a different language, a different transmission line, naming the **same three planets and no others** as significators of profession.

Two originals agreeing on a restriction this specific is much stronger evidence than either alone. Ptolemy read in Greek, Firmicus in Latin, both excluding Jupiter, Saturn, the Sun and the Moon from ever *taking* the lordship of action.

## The selection rule differs, and the difference is small

| | how the one of the three is chosen |
|---|---|
| **Ptolemy** IV.4 | *"two ways: from the **Sun** (the planet rising before it) and from the **culminating place**"* |
| **Firmicus** IV.21 | the one found *"either **in the MC**, or in the **right trine of the MC**, or in the **left**, or in the **other angles**"* |

Both anchor on the **Midheaven**. Ptolemy adds the pre-solar riser; Firmicus adds the MC's trines and the remaining angles. **Same doctrine, slightly different reach.**

## And the same conditional architecture, a sixth time

> *Si ergo Mars actus decreverit et **bene fuerit collocatus** et **benivolis stellis oportuna fuerit radiatione coniunctus** et sit **nocturna genitura**, dat **arma ducatus ac gloriam, licentiam gladii** … aut certe **claras artes et nobiles ex igni et ex ferro***

Mars as lord of action, **well placed**, **joined by benefics with timely radiation**, and **in a nocturnal nativity** — his own sect — gives **arms, generalships and glory, the licence of the sword**, or **bright and noble arts from fire and iron**.

> *In **pigris autem et deiectis locis** constitutus et in his signis, **in quibus non gaudet** …*

But set in the **sluggish and cast-down places** — the cadent houses — and in signs **where he does not rejoice**, the contrary follows.

**Three conditions again: good placement, benefic support, own sect.** Sixth instance today of the architecture found in Ptolemy III.11, III.13, III.15, and Firmicus III.25 and IV.19. It is not a stylistic tic of one author; it is how this tradition reasons about malefics.

Note also *"ex igni et ex ferro"* — **from fire and iron** — matching Ptolemy's Mars professions exactly: armourers, surgeons, statue-makers, all trades of forge and blade.

## What this does to the earlier finding

When only Ptolemy restricted action to three planets, that was one author's system against our almuten-plus-10th-ruler chain — a fork, and I over-claimed it as a defect before retracting.

**With Firmicus independently agreeing, the position changes.** Two of the tradition's major sources, in two languages, exclude Jupiter and Saturn from *ever* signifying profession. Our engine can and does hand career to either. That is now a **majority position we depart from**, not one author's idiosyncrasy — the mirror image of the Lot of Fortune case, where Ptolemy was the outlier and we followed the majority.

Recorded as such. Still not a defect — the Paulus-derived chain is a real tradition — but the weight of evidence on this specific point has moved, and it is worth knowing which side of it the engine sits on.

---

# Firmicus II.6, *De finibus* — the Egyptian terms confirmed, and a dignity claim we do not follow (2026-08-11)

PDF 61–62.

> *hos fines Graeci **oria** vocant*

The Latin *fines* renders the Greek **ὅρια** — terminology confirmed across both languages.

### ✅ Third independent witness for the Egyptian set

Firmicus gives Aries as: **Jupiter 1–6, Venus 7–12, Mercury 13–20, Mars 21–25, Saturn 26–30**; Taurus opening **Venus 1–8**.

| | Aries |
|---|---|
| **Firmicus** (Latin) | Jupiter 6 · Venus 12 · Mercury 20 · Mars 25 · Saturn 30 |
| **our `EGYPTIAN_TERMS`** | Jupiter 6 · Venus 12 · Mercury 20 · Mars 25 · Saturn 30 |

**Exact match**, and Taurus agrees on its opening boundary too.

That makes **three independent confirmations of the Egyptian table this session** — Ptolemy printing it at I.21 with his own per-planet totals (57/79/66/82/76 = 360, all five matching ours), Valens using it throughout, and now Firmicus setting it out sign by sign in Latin. The table the engine runs is as well attested as anything in the tradition.

Note also that Firmicus gives the **Egyptian** set as *the* terms, without presenting alternatives. Ptolemy at I.21 knew of two systems and built a third; Firmicus, writing later, simply transmits the Egyptian. That is itself evidence about which set had won by the fourth century.

### ⚠ But a dignity claim the engine does not follow

> *nam cum **in finibus suis stella fuerit inventa, sic est tamquam in suo domicilio constituta***

**"For when a planet is found in its own terms, it is as if placed in its own domicile."**

Our `DignityCalculator` — following Lilly, verified from the 1647 earlier today — scores **domicile 5** and **term 2**. Firmicus makes term **equivalent to domicile in effect**.

That is a real divergence on dignity weighting, and it is not a small one: a planet in its own term but otherwise peregrine would move from a weak +2 to something like domicile strength. It would change almuten outcomes wherever a term-lord placement is decisive.

**Not changed, and not proposed.** Lilly's table is verified from the facsimile, internally consistent, and the engine's numbers match it exactly. Firmicus is one witness and his phrasing is *tamquam* — "as if", a comparison rather than a scoring instruction. It may be rhetorical emphasis on the term's importance rather than a claim of numerical parity.

Recorded because the distinction matters for anyone reading Firmicus's delineations: when he says a planet is strong in its own terms, he means considerably more by it than a +2 in our scheme.

---

# Firmicus III.1, *Thema Mundi* — the world's own nativity (2026-08-11)

PDF 106–107. Attributed to **Aesculapius and Hanubius**, *"to whom the most powerful divinity of Mercury entrusted the secrets of this science."*

| body | position |
|---|---|
| **Sun** | Leo 15° |
| **Moon** | Cancer 15° |
| **Saturn** | Capricorn 15° |
| **Jupiter** | Sagittarius 15° |
| **Mars** | Scorpio 15° |
| **Venus** | Libra 15° |
| **Mercury** | Virgo 15° |
| **Ascendant** (*hora*) | Cancer 15° |

**Every planet in its own domicile, all at the fifteenth degree, with Cancer rising** — and the Moon exactly on the Ascendant.

> *secundum istas rationes etiam **hominum volunt fata disponi**, sicut in illo libro continetur **Aesculapii, qui Myriogenesis appellatur**, prorsus ut **nihil ab ista mundi genitura in singulis hominum genituris alienum esse videatur***

*"…they hold that the fates of men too are arranged accordingly — as is contained in that book of Aesculapius called the **Myriogenesis** — so that **nothing in individual human nativities should appear alien to this nativity of the world**."*

## The same table, two incompatible justifications

This is the doctrinal foundation of the domicile system — and it is **not** the one Ptolemy gives.

| | why Saturn rules Capricorn |
|---|---|
| **Ptolemy I.18** | **Physical.** Cancer and Leo are nearest our zenith and hottest, so they go to the lights. Saturn, cold and opposed in nature to their heat, takes the signs **diametrically opposite** theirs, *"because the diametrical configuration is unfavourable."* |
| **Firmicus III.1** | **Archetypal.** Saturn *was in Capricorn* when the world was born, and every human chart is a variation on that founding figure. |

**Identical assignments, entirely different grounds** — one causal and physical, the other mythological and precedent-based. Neither author acknowledges the other's reasoning.

That pairing is worth having, because it answers the "why" question two ways for the same fact. A reader who finds the physical argument unpersuasive may find the archetypal one compelling, and vice versa. **The engine currently offers neither.**

## A note on the attribution

Firmicus credits **Aesculapius**, **Hanubius** (Anubis), and — in the apparatus — **Nechepso and Petosiris**, the standard pseudepigraphic authorities of the Hellenistic tradition. Ptolemy, by contrast, cites no divine authorities anywhere in Book I; he argues from the solar year.

The two authors differ in **kind of authority as well as kind of argument**: Firmicus transmits what was revealed to sages, Ptolemy derives what follows from the seasons. Recorded alongside the earlier note that Firmicus *instructs* where Ptolemy *hedges* — the same divide, showing up in the foundations rather than the delineations.
