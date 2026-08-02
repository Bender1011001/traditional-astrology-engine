# Jyotisha defensibility spec

Status: governing spec for the Vedic reading section  
Updated: 2026-08-01  
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

The adversary here is a working Jyotishi. That reader will check for divisional
charts and dasha before anything else, and will notice immediately if the section
reasons like a Western chart wearing sidereal longitudes.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Sidereal longitudes under a named ayanamsa | India Calendar Reform Committee 1956 (registry: `jyotisha_india_calendar_reform_committee_1956`) fixes Lahiri as the civil standard | `implemented` (Lahiri, disclosed) |
| 2 | Lagna, its lord, and the lord's placement | Brhajjataka I; BPHS lagna chapters | `implemented` |
| 3 | Rasi (D1) placements with dignity | Brhajjataka II (encoded in `brhajjataka_planetary_rule_manifest.json`) | `implemented` |
| 4 | Nakshatra and pada for Moon, lagna, and each graha | Brhajjataka I.4-14 passages already passage-aligned | `implemented` |
| 5 | Whole-sign bhava assignment | classical default; Sripati is the live alternative | `implemented` (disclosed) |
| 6 | **Navamsha (D9)** | universally treated as mandatory; BPHS varga chapters | `implemented` (all grahas, nodes, lagna; vargottama flagged; D9 dignity separate) |
| 7 | Vimshottari mahadasha from janma nakshatra | BPHS dasha chapters; standard 120-year scheme | `implemented` |
| 8 | Vimshottari antardasha (bhukti) | same | `computable` |
| 9 | Graha dignity: exaltation, debilitation, own sign, moolatrikona | Brhajjataka II | `implemented` (moolatrikona pending) |
| 10 | Friendship/enmity (naisargika and tatkalika) | BPHS relationship chapters | `computable` |
| 11 | Graha drishti (special aspects for Mars, Jupiter, Saturn) | BPHS aspect chapters | `computable` |
| 12 | Yogas: Raja, Dhana, and yogakaraka identification | BPHS yoga chapters; Phaladeepika | `computable` |
| 13 | Combustion (astangata) | BPHS | `computable` |
| 14 | Shadbala | BPHS bala chapters | `source_gated` — recension-dependent weights |
| 15 | Ashtakavarga | BPHS | `source_gated` |
| 16 | Other vargas (D10 career, D7 children, etc.) | BPHS varga chapters | `source_gated` — which vargas are mandatory varies by school |

**Item 6 is done** (2026-08-01), verified by four structural properties the
classical rule guarantees and now covered by a runnable worked example. It
immediately earned its place: in the Fairfield chart Saturn is neutral in D1
Pisces but **exalted in D9 Libra** — a D1-only verdict on Saturn would have been
wrong.

## Judgment hierarchy

The composer must execute in this order. Later steps may qualify earlier ones;
they may not silently replace them.

1. Lagna and lagna lord: sign, degree, nakshatra, placement, condition.
2. Moon: janma rasi and janma nakshatra — in Jyotisha the Moon outranks the Sun
   for personal significations.
3. Graha dignity and placement in D1, with retrogradation and combustion.
4. Bhava rulership: which graha owns which house, and where that owner sits.
5. Drishti: who aspects what, including the special aspects.
6. Navamsha cross-check: does D9 confirm or undercut the D1 verdict on each graha.
7. Yogas, evaluated only after 1-6 and only where their constituent conditions
   have actually been verified.
8. Dasha: current mahadasha and antardasha, read against the qualified natal
   structure — never as free-floating themes.

## Worked-example inventory

| Source | Location | Contains | Usable now |
|---|---|---|---|
| Brhajjataka, Aiyar 1905 translation | registry `jyotisha_varahamihira_brhajjataka_aiyar_1905_archive` | worked illustrations in the commentary | needs page inspection |
| Saravali, Subrahmanya 1914 | registry `jyotisha_kalyanavarma_saravali_subrahmanya_1914_archive` | example applications | needs page inspection |
| Phaladeepika, Subrahmanya 1950 | registry `jyotisha_mantreswara_phaladeepika_subrahmanya_1950_archive` | worked yoga examples | needs page inspection |
| BPHS Subodhini 1899 | registry `jyotisha_bphs_subodhini_1899_archive` | dasha and varga worked cases | needs page inspection; recension audit already flags variance |

All four are already in the source registry with archive access. None has yet been
inspected for worked charts specifically. That inspection is the M3 task for this
tradition.

## Refusal list

- **No lifespan claim.** Ayurdaya methods exist and are recension-dependent; the
  live Western report already demonstrates how badly length-of-life arithmetic
  behaves when branches disagree. Jyotisha ayurdaya is not asserted.
- **No muhurta or remedial prescription.** Gemstone, mantra, and ritual remedies
  are prescriptive advice, not historical delineation.
- **No caste, varna, or social-rank delineation** rendered as a claim about the
  reader, even where the sources state it. Retain in the audit trace with the
  suppression reason.
- **No marriage-compatibility verdict** (kuta/guna milan) in a natal reading; it
  requires a second chart and its own source treatment.
- **No claim depending on Shadbala or Ashtakavarga** until those are implemented
  with sourced weights.

## Conventions requiring disclosure

| Convention | Chosen | Alternatives |
|---|---|---|
| Ayanamsa | Lahiri (Chitrapaksha) | Fagan-Bradley, Krishnamurti, Raman, True Citra, True Revati |
| Houses | Whole sign | Sripati, equal-from-degree |
| Nodes | Mean | True |
| Dasha year length | 365.2425 days | 360-day savana year; sidereal year |
| Moolatrikona boundaries | pending | vary slightly by text |

## Current implementation gap

The shipped panel section covers items 1-5, 7, and 9 (partially). To reach a
defendable reading it needs, in order: **navamsha (6)**, antardasha (8), drishti
(11), then yogas (12) gated on 10 and 13.
