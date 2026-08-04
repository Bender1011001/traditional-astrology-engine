# Egyptian defensibility spec

Status: governing spec for the pharaonic Egyptian section
Updated: 2026-08-04
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

The adversary is an Egyptologist. There are two fast ways to fail in front of one:
produce a "pharaonic birth chart", which the surviving pharaonic material does not
contain; or state a modern calendar date for an ancient civil day without saying
which epoch you assumed, in a calendar that has no intercalation and therefore
drifts a day every four years.

## What the corpus actually is

Before 2026-08-04 this track carried a validated 365-day civil-calendar kernel and
a hash-pinned facsimile of Papyrus Sallier IV whose hieratic nobody here could
read. The registry's own `next_action` for that papyrus asked for "a complete
transcription and modern critical translation".

That translation has existed since 1870 and is public domain. Chabas' *Le
calendrier des jours fastes et nefastes de l'annee egyptienne* is a complete
French translation of Sallier IV, digitised by the Bayerische Staatsbibliothek
with an open OCR endpoint. It carries, day by day from the mutilated opening of
Thoth to 11 Pachons: the day number, a Gregorian equivalent, the manuscript's
three-part mark reproduced in hieroglyphs, and the legend.

And the legends contain a natal layer. Eighteen days carry an explicit birth
prognosis of the form *Quiconque est ne ce jour-la ...*.

**Every one of the eighteen predicts the native's death.** They name the manner
(a crocodile, a serpent, wounds, drunkenness, intercourse, the annual contagion,
blindness, the river, the stone), the timing (does not live; lives and dies the
same day; dies of old age; dies after a long life in opulence), or the honour
(dies revered by the citizens of Memphis; dies revered by his fellow citizens).

That is the finding, and it is more interesting than a reading would have been.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | 365-day civil year, 12x30 + 5, no intercalation | validated civil-calendar pack | `implemented` |
| 2 | Season and month position, epagomenal handling | validated pack | `implemented` |
| 3 | Fail-closed chronology: no civil date without a declared epoch | validated pack | `implemented` |
| 4 | Sallier IV day legends, day by day | **Chabas 1870, public domain, hash-pinned; 32 days geometry-verified** | `implemented` (day corpus, 1,932 words of quoted French plus rendering) |
| 5 | The three-part day mark system and its colour semantics | Chabas' own French prose, pp. 21-22 | `implemented` (system encoded; see item 6) |
| 6 | Per-day mark *values* | Chabas reproduces the marks in hieroglyphs, not in words | `source_gated` — not machine-legible from the OCR layer; needs plate collation against the Budge 1923 facsimile already pinned here |
| 7 | Birth prognoses keyed to the civil day | Sallier IV legends via Chabas | `implemented` (18 clauses, each day-fixed by column geometry) — and all 18 refused for customer output |
| 8 | Civil-to-modern conversion convention of the edition | Chabas p. 23: the Coptic anchor, 1 Thoth = 29 August Julian = 11 September Gregorian | `implemented` as a disclosed `configured_method` |
| 9 | Days outside the preserved span | the papyrus is mutilated at the opening and stops at 11 Pachons | `refused` — the engine must decline, and must not read silence as absence |
| 10 | The Cairo Calendar (pCairo 86637) and pLeiden I 346 | Bakir 1966 and successors | `source_gated` — no open edition located; see the search trail in `source_audit.md` |
| 11 | Decanal, astral or planetary natal judgment | — | `refused` — this witness is a hemerology; no celestial datum enters it |

## Judgment hierarchy

1. Declare the epoch. A Sallier day has no modern date until an epoch profile is
   named, and the wandering year means the correspondence moves.
2. Report the day's legend, in Chabas' French with the rendering beside it.
3. Report the day class as the legend states it, never as inferred from the
   hieroglyphic mark, which this edition does not translate.
4. Where mark and legend disagree — 23 Thoth is the attested case — show both and
   show the editor's emendation as an emendation.
5. State the birth clause as a historical record, refused for application.

## Worked-example inventory

| Source | Contains | Usable now |
|---|---|---|
| Chabas' own Gregorian column | a Coptic-anchored equivalent for every printed day | **strong**: the anchor was re-derived independently from the column and reproduced every printed month heading across 17 geometry-verified pages |
| Chabas' discussion of 23 Thoth (p. 22) | an explicit mark/legend conflict, diagnosed by the editor | usable: the pack reproduces the conflict rather than resolving it |
| Budge 1923 facsimile, 41 plates (already pinned) | the hieratic itself | usable for collation of the marks; the outstanding item 6 work |

## Refusal list

- **No pharaonic birth chart.** The natal layer here is keyed to the civil day
  alone. No planet, decan, star or hour enters any of the eighteen clauses.
- **No customer birth prognosis.** All eighteen predicate death. The section
  states the finding and declines to apply any clause to a person.
- **No civil date without a declared epoch.** The 365-day year has no
  intercalation; the correspondence to a Julian or Gregorian day requires the
  manuscript's own date, which Chabas himself says he did not determine.
- **No verdict for a day outside the preserved span.** The papyrus opens mutilated
  and stops at 11 Pachons. Silence there is loss, not evidence.
- **No per-day mark value asserted from OCR.** The marks are hieroglyphs; the OCR
  renders them as noise, and guessing them would be inventing the source's own
  primary datum.

## Conventions requiring disclosure

| Convention | Chosen | Alternatives |
|---|---|---|
| Modern-date column | Chabas' Coptic anchor, 1 Thoth = 11 September Gregorian | any epoch derived from an actual dating of the papyrus; Chabas offered his "par simple curiosite" and disclaimed it |
| Day class | read from the legend text | reading it from the hieroglyphic mark, which would require plate collation |
| Mark/legend conflict at 23 Thoth | both reported | the editor's emendation, which we show but do not adopt |
| Quotation orthography | unaccented, as the OCR layer supplies it | the printed page, cited by scan and printed page for every entry |

## Current implementation gap

Item 6 is the one piece of real outstanding work and it is a collation task, not
a research task: the Budge facsimile plates are already in this repository, and
reading the three-part mark off them would complete the day-verdict layer. Item
10 is a genuine access gate. Everything else on this checklist either ships or is
refused on the source's own terms.
