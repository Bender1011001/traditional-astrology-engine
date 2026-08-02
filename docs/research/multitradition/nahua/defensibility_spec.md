# Nahua defensibility spec

Status: governing spec for the Nahua section  
Updated: 2026-08-01  
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

This tradition has an unusual shape: the **interpretation is better sourced than
the date arithmetic**. Sahagun's informants recorded day-sign auguries in detail
in Florentine Codex Book 4, and that text is public and passage-addressable. What
is missing is the correlation that would tell us which day sign a modern birth
falls on.

That inversion decides the whole design.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | 13-by-20 cycle arithmetic | validated tonalpohualli pack | `implemented` |
| 2 | Trecena identification and heads | validated pack (20 heads verified) | `implemented` |
| 3 | Civil-date correlation | — | `refused` — no approved epoch exists |
| 4 | Day-sign auguries | **Florentine Codex Book 4, passage-addressable, public** | `computable` — the strongest interpretive material in any non-Western track |
| 5 | Trecena-level auguries and patron deities | Florentine Codex Book 4 chapters | `computable` |
| 6 | Day/night lords, volatiles (birds) | Codex Borbonicus, Tonalamatl Aubin | `source_gated` |
| 7 | Xiuhpohualli (365-day) position | requires the same missing correlation | `source_gated` |
| 8 | 52-year Calendar Round position | requires correlation | `source_gated` |

## The design consequence

Because item 3 is refused and item 4 is available, the honest product is **not**
"here is your day sign." It is:

> Here is what the Florentine Codex says about each of the twenty day signs, in
> Sahagun's informants' own words with folio citations — and here is why we
> cannot tell you which one is yours.

That is a genuinely defendable, genuinely interesting section, and it is more
honest than every "Aztec astrology" product in existence, all of which silently
invent a correlation.

If a correlation is ever approved, item 4 is already built and the section
upgrades in place.

## Judgment hierarchy

1. State the correlation problem first, before any cycle position.
2. Present cycle arithmetic as arithmetic (fixture-labeled).
3. Present the day-sign augury corpus as source quotation, per sign, cited to
   folio.
4. Never join 2 and 3 into a personal claim.

## Worked-example inventory

| Source | Contains | Usable now |
|---|---|---|
| Getty Florentine Codex Book 4 | Nahuatl + Spanish + English, stable folio and text-record IDs | **yes** — already used to anchor the validated pack; four text-record IDs cited on folio 1r alone |
| INAH Anales tonalamatl table | complete 20-trecena order | yes, already encoded |
| Codex Borbonicus (Assemblee) | pictorial trecena pages | needs codicological reading |
| Tonalamatl Aubin (INAH) | pictorial | needs codicological reading |

The Getty edition's stable text-record IDs are the key asset: they make
passage-cited quotation mechanically reliable.

## Refusal list

- **No day sign assigned to a birth.** No approved correlation exists, and the
  validated pack explicitly forbids reusing a Maya correlation because both
  traditions run 260-day counts.
- **No twenty-sign personality lookup.** The source audit is explicit that real
  tonalamatl reading requires patrons, day/night lords, volatiles, imagery, and
  manuscript-specific evidence — a bare sign-to-trait table erases material
  conditions the source itself preserves.
- **No flattening of conditional language.** Book 4's auguries are frequently
  conditional on conduct ("if he did penance..."), and that conditionality is
  the doctrine, not decoration.
- **No modern neo-Aztec content.** Only what the cited witnesses say.

## Conventions requiring disclosure

| Convention | Chosen | Note |
|---|---|---|
| Cycle anchor for demonstration | JDN 2451545 fixture | explicitly non-historical; must be labeled at every render |
| Orthography | source labels retained (Cuautli, Olin, etc.) | not regularized into interpretation keys |

## Current implementation gap

Item 1-2 ship; item 3 is permanently refused pending scholarship. **Item 4 is the
M4 task** and is the highest-value interpretive work available anywhere in the
non-Western tracks, because the source is public, passage-addressable, and
already anchored in a validated pack.
