# The condition rule: six independent attestations, zero implementation

**Written 2026-08-11**, consolidating findings scattered across `ptolemy_greek_book1.md` and `firmicus_notes.md`.

---

## The pattern

Across two authors, two languages and two independent transmission lines, the same architecture appears six times:

> **A malefic verdict is never final. It is a first reading, tested against whether a benefic overcomes it — and the outcome is graded, not binary.**

The inverse holds too, and is stated as explicitly: **a benefic promise is not final either.** The full good requires the significator well placed, of its own sect, *and* supported. Malefic absence alone is never sufficient.

---

## The six

| # | source | topic | malefic alone | benefic overcoming |
|---|---|---|---|---|
| 1 | **Ptolemy III.11** | the anaretic degree | kills | **hindered** — a benefic's bound, or Jupiter within **12°** / Venus within **8°** by square or trine, forward of the killing degree |
| 2 | **Ptolemy III.13** | bodily afflictions | *ἀνίατα καὶ ἐπαχθῆ* — incurable, grievous | *εὐσχήμονα … μέτρια καὶ εὐπαρηγόρητα* — **seemly, moderate, easily relieved**; *εὐαπάλλακτα*, easily got rid of, if the benefics are also oriental |
| 3 | **Ptolemy III.15** | diseases of the soul | incurable, unrelenting, notorious | *ἰάσιμα* — **curable**, though still conspicuous |
| 4 | **Firmicus III.25** | the planetary years | fewer years, or the number in months instead of years | *integer annorum numerus* — **the full number**, especially with Jupiter by day or Venus by night supporting |
| 5 | **Firmicus IV.19** | the lord of the nativity | *omnis eius efficacia debilitata languescit* — all his efficacy weakens | decrees all goods **and the full number of years** |
| 6 | **Firmicus IV.21** | the lord of action | cadent, in signs where he does not rejoice → the contrary | arms, glory, the licence of the sword, or noble arts of fire and iron |

**Ptolemy read in the Greek, Firmicus in the Latin, this session.** Neither depends on the other; Firmicus is not translating Ptolemy.

---

## The three conditions, as they are actually stated

Firmicus IV.19 gives the fullest form:

> *qui si **bene fuerit collocatus** in his, in quibus **gaudet** signis vel in quibus **exaltatur**, vel in **domiciliis suis**, et **conditionis suae** genitura fuerit, nec **malivolarum nociva radiatione pulsatus** nec **benivolarum stellarum praesidio destitutus***

1. **Well placed** — in signs of joy, exaltation, or own domicile
2. **Of its own sect** — *conditionis suae*
3. **Neither struck by malefics NOR deserted by benefics** — a double requirement, not a single test

Point 3 is the one an implementation would most easily get wrong. *Non destitutus* — **not deserted** — means benefic support must be **present**, not merely that malefic affliction is **absent**.

---

## What the engine does instead

`DignityCalculator` produces a **score**. Scores blend: a malefic affliction subtracts, a benefic aspect adds, and the result is a number somewhere in the middle.

**That is not what either author describes.** They describe a **gate**, not a sum. The question is not "how much dignity, net?" but "**does a benefic overcome the malefic — yes or no?**" — and the answer selects between named, opposite outcomes.

Ptolemy makes the same point structurally at III.14, where every planet's soul-delineation is a **binary**: *ἐπὶ μὲν ἐνδόξου διαθέσεως* versus *ἐπὶ δὲ τῆς ἐναντίας*, the dignified condition against the contrary. Venus dignified is *"gentle, good, merciful, altogether charming"*; Venus contrary is *"lazy, erotic, timid, lecherous."* **He does not give Venus a fixed meaning that gets nudged by score. He gives two opposite meanings selected by condition.**

An engine that blends toward the middle produces neither pole — and the reading reads hedged where the sources are decisive.

---

## Why this is the session's most actionable finding

- It is **not a delineation** to bolt on, nor a table to correct. It is a **missing step in how every malefic judgment is reached.**
- It is **attested six times in two languages**, which is far past the evidentiary bar the project normally requires.
- Three of the six carry **explicit, stated parameters** — Ptolemy's 12°/8° orbs, the bound alternative, the oriental clause — so implementing them requires no invention.
- It bears directly on the output customers care about most: **longevity, health, and whether a difficult chart is being read as a sentence or as a difficulty.**

## What it is not

It is **not** licence to soften hard readings. The condition cuts both ways: where no benefic overcomes, all three authors are blunter than the engine currently is — *incurable*, *grievous*, *all his efficacy languishes*. Implementing the rule faithfully would make some readings **harder**, not softer.

That is the point. The tradition grades; it does not average.

---

## Status

**Nothing implemented.** Ptolemy III.11's rescue has a full build plan recorded in `ptolemy_greek_book1.md`, including the data the payload currently lacks (the anaretic degree's longitude) and a warning about anchoring the orb window on the killing degree rather than the hyleg. The other five are documented but unplanned.

This is a decision for the owner, not a defect to patch: it changes published longevity figures and the tone of every difficult chart.
