# Medieval Jewish defensibility spec

Status: governing spec for the Ibn Ezra section  
Updated: 2026-08-01  
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

The adversary is a historian of medieval Hebrew science. This tradition is the
best-positioned non-Western track in the repository, for a reason that is easy to
miss: **its validated pack already drives the live Western report's solar-return
layer.** The doctrine is shipping; it simply is not labeled as Ibn Ezra's.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Annual revolution (solar return) computed | Book of Revolution, validated pack | `implemented` — live in the premium report |
| 2 | Return-Ascendant ruler as annual witness | Book of Revolution s.1 | `implemented` |
| 3 | Comparison of return placements against natal whole-sign places | Book of Revolution s.4, s.15, s.21 | `implemented` |
| 4 | Sect-light triplicity ruler compared natal vs revolution | Book of Revolution s.4 | `implemented` |
| 5 | Ibn Ezra's three relative life phases from sect-light triplicity rulers | Book of Nativities, referenced in Revolution s.4 | `implemented` — and correctly kept distinct from Dorotheus's different first/second fortune rule |
| 6 | Natal doctrine from the Book of Nativities proper | Book of Nativities | `source_gated` — rule and precedence extraction incomplete |
| 7 | Hebrew terminology preserved alongside translation | parallel Hebrew-English critical edition | `computable` |
| 8 | World-astrology / conjunctional doctrine | separate module | `source_gated` |
| 9 | Elections and interrogations | separate module | `source_gated` |

## Judgment hierarchy

1. Natal figure first; the revolution qualifies the nativity and never replaces
   it — the pack's own evidence note states the revolution is *shorter-lived
   testimony that must be compared with the nativity*.
2. Return-Ascendant ruler and its condition.
3. Return/natal place overlays.
4. Sect-light triplicity ruler comparison across both figures.
5. Relative life phases, kept explicitly separate from Dorotheus's rule.

That last separation is a real defensibility point: the live report already
prints both and labels which is Ibn Ezra and which is Dorotheus. A specialist
would check exactly that.

## Worked-example inventory

| Source | Contains | Usable now |
|---|---|---|
| Ibn Ezra, *Book of Revolution* — parallel Hebrew-English critical edition | facing text, sections 1, 4, 15, 21 already inspected | yes; worked examples not yet located within it |
| Ibn Ezra, *Book of Nativities* — same edition | natal doctrine | needs inspection |

The critical edition is the controlling text and is already in use. The M3 task
is to inspect it for worked charts specifically.

## Refusal list

- **No Book of Nativities natal doctrine** until extraction completes.
- **No conflation of Ibn Ezra with Dorotheus or with Arabic sources**, even where
  he is transmitting them.
- **No return-location guessing.** The live report already discloses that natal
  coordinates are used as a proxy when return-location coordinates are not
  supplied; that disclosure must survive into this section.
- **No Hebrew-calendar date claim** without its own sourced conversion.

## Conventions requiring disclosure

| Convention | Chosen | Note |
|---|---|---|
| Return location | natal coordinates as proxy | disclosed; return houses depend on location |
| Shared calculation core | Western tropical engine | same positions as the Western section |

## Current implementation gap

Items 1-5 are effectively done and shipping inside the Western report. The work
here is **attribution rather than computation**: surface the Ibn Ezra layer as
its own labeled section so the tradition gets named credit, and add item 7's
Hebrew terminology. That is a small, high-yield task.
