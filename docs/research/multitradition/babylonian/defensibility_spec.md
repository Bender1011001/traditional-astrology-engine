# Babylonian defensibility spec

Status: governing spec for the Mesopotamian section  
Updated: 2026-08-01  
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

This is the tradition where **requirement 5 (refusal) carries most of the weight**.
The adversary is an Assyriologist, and the fastest way to fail is to produce a
Babylonian personality reading — a genre the surviving corpus does not contain.

## What the corpus actually is

The encoded material divides into two kinds, and they answer different questions:

1. **Celestial omens** (Enuma Anu Enlil, the Neo-Assyrian royal reports) — the
   overwhelming majority. Protasis/apodosis pairs about **the king, the land, the
   harvest, the army**. These are state omens. They are not about the reader.
2. **Late Babylonian horoscopes** (Rochberg's 32 numbered texts) — genuinely
   natal, genuinely rare, and mostly *positional records* rather than judgments.
   Across Texts 1-28 the encoded corpus yields only **21 explicit judgment
   clauses**, and the validator asserts none of them is customer-eligible.

A defendable section states this division first. The honest headline is that this
is the oldest documented tradition and that its natal branch is thin, late, and
laconic — which is itself the most interesting true thing to say about it.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Positions recomputed for the birth date | 192 positions recomputed and JPL-Horizons cross-checked | `implemented` in corpus |
| 2 | Babylonian-style position reporting (zodiacal sign + degree) | Rochberg astronomy specs | `computable` |
| 3 | Lunar phase / eclipse proximity | SAA8 eclipse pilot (33 rules, 12 vectors) | `computable` |
| 4 | Applicable EAE omen protases for the sky at birth | EAE 20 witness pack (17 rules), EAE 16-21 commentary (22 rules) | `computable` — the section's real content |
| 5 | Horoscope-format presentation matching Rochberg's text structure | corpus manifests, 31 horoscope records | `computable` |
| 6 | The 21 explicit judgment clauses, quoted as historical artifacts | Texts 1-28 judgment manifests | `computable`, quotation only |
| 7 | Natal judgment synthesis | — | `refused`, see below |

## Judgment hierarchy

1. State what kind of document this is: an omen corpus plus a small late
   horoscope corpus, not a natal interpretive system.
2. Report positions in the tradition's own idiom.
3. Report lunar/eclipse condition.
4. Surface omen protases whose celestial condition the birth sky actually
   matches — each with its apodosis quoted and attributed, and each labeled as a
   claim about kings and lands.
5. Where a Rochberg text carries an explicit judgment clause in comparable
   circumstances, quote it as a historical parallel, never as a prediction.
6. Stop. Do not synthesize.

## Worked-example inventory

| Source | Contains | Usable now |
|---|---|---|
| Rochberg 1998, Texts 1-32 | 31 horoscope records, 4 birth notes, 6 birth records | catalogued and CDLI-concordanced (30/32 exact matches); these ARE the worked examples — each is a real ancient chart with its recorded content |
| SAA8 royal reports | applied omen citations by named scholars to dated events | strongest worked-example material in the whole corpus: a named ancient astrologer applying a named omen to a dated sky |
| EAE 20 / 16-21 commentary | ancient commentary rationalizing omen text | shows how ancient practitioners resolved ambiguity |

This tradition has the **best worked-example situation of any non-Western track**:
the SAA8 reports are ancient practitioners showing their work on dated skies, and
the astronomy has already been recomputed and Horizons-cross-checked. A worked
example here can be validated end to end.

## Refusal list

- **No personality, character, or temperament claim.** The corpus does not
  contain the genre. This is the defining refusal.
- **No modern natal synthesis** built by analogy from state omens.
- **No prediction of any kind** to a reader. Apodoses concern kings, lands,
  armies, and harvests, and are quoted as historical text.
- **No blending of witnesses.** The EAE 20 pack preserves recension conflicts;
  the section must not merge them.
- **No commentary overwriting base omen text.** Commentary restrictions,
  alternatives, and wordplay qualify; they never replace.
- **No claim from the two CDLI-unresolved tablets** without saying they are
  unresolved.

## Conventions requiring disclosure

| Convention | Chosen | Note |
|---|---|---|
| Ephemeris | Swiss Ephemeris, Horizons cross-checked | 192 positions verified |
| Zodiac | tropical positions reported; Babylonian sidereal schemes differ | must be stated when reporting "sign" |
| Omen matching orb | to be fixed | must be disclosed once chosen; no silent default |

## Current implementation gap

Nothing of this section is in the shipped panel yet — it is M5. The design above
is what M5 builds: a positions block, an eclipse/lunar block, matched omen
protases with quoted apodoses, and an explicit statement of the genre boundary.
