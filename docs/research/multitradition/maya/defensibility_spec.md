# Maya defensibility spec

Status: governing spec for the Maya section  
Updated: 2026-08-04  
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

Two distinct adversaries: an epigrapher/archaeoastronomer, who will check the
correlation handling and the Long Count arithmetic, and a contemporary K'iche'
daykeeper, whose tradition is living and whose day meanings are not the
epigrapher's to assign. Both must be satisfied, and they want different things.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Long Count from a named correlation | validated kernel; GMT 584283 + 584285 | `implemented`, both emitted |
| 2 | Tzolk'in number and day name | validated kernel formulae | `implemented` |
| 3 | Haab month and day | validated kernel formulae | `implemented` |
| 4 | Calendar Round position and its 18980-day period | validated kernel | `implemented` (period reported) |
| 5 | Lords of the Night (G1-G9) | not in the validated pack | `implemented` as `configured_method`, disclosed |
| 6 | Lunar series (glyphs C, D, E, X) | not encoded | `source_gated` |
| 7 | 819-day count | not encoded | `source_gated` |
| 8 | Venus cycle station | Dresden Codex Venus table (registry has INAH/SLUB/FAMSI facsimiles) | `source_gated` |
| 9 | Day-sign meanings | Dresden codical almanacs; NMAI living-K'iche' material; the colonial Yucatec day-augury lists (*u mutil chuenil kin sansamal*) in the Chilam Balam of Kaua and Ixil | `source_gated` — no open transcription located; see the search trail in `source_audit.md` and the refusals below |
| 10 | Year Bearer and its prognostic | **Landa, *Relacion de las cosas de Yucatan*, Brasseur 1864 edition, public domain, hash-pinned** | `implemented` — four letters, four Bacabs, four verdicts and their remedies encoded (11 rules, 10 vectors); harsh clauses refused for customer output |
| 11 | Katun prognostics (Buluc-Ahau, Bolon-Ahau) | Landa, same edition | `source_gated` — present in the witness, not yet encoded |

## Judgment hierarchy

1. Name the correlation before reporting any date. A Maya date without its
   correlation constant is meaningless.
2. Report Long Count, Tzolk'in, Haab, Calendar Round under each correlation
   emitted.
3. Report Lord of the Night, labeled configured.
4. Only then, if day meanings are ever enabled, attribute them to a specific
   witness — codical or living — and never blend the two.

## Worked-example inventory

| Source | Contains | Usable now |
|---|---|---|
| NMAI Living Maya Time converter | reference conversions | **strong**: an institutional converter to check our arithmetic against, date by date |
| FAMSI date converter | reference conversions | second independent check |
| Dresden Codex facsimiles (INAH, SLUB, FAMSI) | almanacs with real Tzolk'in sequences | usable for cycle verification; interpretation gated |
| PNAS 2013 radiocarbon correlation study | correlation evidence | supports 584283 as bounded default |

Two independent institutional converters is an unusually good position. The M3
worked-example task here is mechanical and high-value: sample dates across a wide
span, compare our output to both converters, publish the agreement rate.

## Refusal list

- **No silent correlation.** Every date carries its constant.
- **No day-sign personality reading.** Two separate reasons: the validated pack
  carries arithmetic only, and — more importantly — Tzolk'in day meanings belong
  to a **living tradition** with contemporary practitioners. Assigning them from
  a codex without that community's involvement is both unsourced and
  appropriative. This refusal should be stated to the reader plainly.
- **No 2012-style prophetic or era-ending claim.** The kernel's own notation
  policy retains 13.0.0.0.0 as source annotation without replacing the linear
  value.
- **No Long Count for dates requiring the Extended Long Count** (negative days);
  the five-place profile rejects them.
- **No conflation of Maya and Nahua 260-day counts.**
- **No personal application of a year-bearer verdict.** Landa's four verdicts are
  about the year's rain, maize, sickness, famine and political order. The witness
  attaches none of them to a person born in the year, and neither will we.
- **No Landa verdict without its remedy, and none without its framing.** Every
  prognostic in that source is paired with a prescribed observance, and the text
  says outright that when the miseries came anyway the blame was laid on the
  observance. Quoting the verdict alone converts a conditional ritual system into
  a fatalistic one. Landa is also a hostile witness who burned the books he
  describes; deleting that framing would present a colonial account as neutral
  ethnography.

## Conventions requiring disclosure

| Convention | Chosen | Alternatives |
|---|---|---|
| Correlation | both 584283 and 584285 emitted | 584285 is a sensitivity profile, not a default |
| Day-name profile | Yucatec, Smithsonian 2012 spellings | K'iche' and other regional name sets differ |
| Lords of the Night | G = (total_day + 1) mod 9 | configured; not in the validated pack |
| Day boundary | integer JDN of the civil date | the pack does not infer a birth-time instant |

## Current implementation gap

Items 1-5 ship today. The immediate high-value work is not new technique but
**verification**: the two-converter cross-check described above. Day meanings
stay refused pending a partnership route rather than a source route.
