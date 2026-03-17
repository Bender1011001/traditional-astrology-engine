---
project: engine
status: audited
updated: 2026-03-16
---

# Astrological Engine

## Resume
- **Pick up at**: All 6 audit fixes applied and verified. Next: Horary Abscission of Light, Hyleg aspect-based Anareta.
- **Last session**: Full 46-file audit completed (2026-03-16). 5 Critical (2 real), 10 Moderate, 8 Minor issues found. 6 fixes applied.
- **Blocked on**: Nothing

## Status
- **AUDIT STATUS**: ✅ Comprehensive audit completed 2026-03-16. See `engine_audit_report.md` in artifacts.
- Core calculation and synthesis logic verified against source material (Ptolemy, Valens, Dorotheus, Bonatti, Lilly, Al-Biruni, Paulus Alexandrinus).
- **Implemented**: 40+ traditional techniques spanning the full canon: Essential/Accidental Dignities, Sect, Hayz/Halb, Aspects, Reception (Bonatti/Lilly), Hermetic & Forensic Lots (40+), Kakosis (7 Conditions), Horary Physics, Profections, Zodiacal Releasing, Firdaria, Decennials, Primary Directions (Placidus), Distributor, Hyleg/Alcocoden, Almuten Figuris, Lord of Geniture, Monomoiria, Dodecatemoria, Doryphory, Antiscia, Fixed Stars (Parans), Lunar Mansions (Picatrix), Temperament (Lilly), Medical/Decumbiture, Mundane Hierarchy, Eclipses, Electional (Kairos), Planetary Hours, Solar Return, Solar Arcs, Phasis/Visibility, Synodic Phases, Prenatal Syzygy, Al-Mubtazz, Nodal Metabolic model.

### Audit Fixes Applied (2026-03-16)
1. **temperament.py** — Added inherent planetary natures (PLANET_NATURES dict) per Lilly CA pp.57-83
2. **reception.py** — Fixed Bonatti strict threshold from `>= 2` to `>= 3` (Term alone insufficient)
3. **electional.py** — Added Via Combusta, early Ascendant degree (0-3°), late degree (27-30°) checks
4. **phasis.py** — Implemented `check_chariot()` using DignityCalculator (was returning False always)
5. **calculations.py** — Made VoC check speed-aware (application requires closing gap via relative speed)
6. **dignities.py** — Participating triplicity ruler already scored at +1 (confirmed correct, no change needed)

## Key Files
- `forensic_engine.py`: Central hub/Auditor. Orchestrates all engines, produces bifurcated JSON output.
- `dignities.py`: 5-tier essential dignities + accidental dignities, Hayz/Halb, Monomoiria.
- `advanced_mechanics.py`: Hermetic Lots, Almuten Figuris, Doryphory, Dodecatemoria.
- `horary.py`: Horary physics (Translation, Collection, Prohibition, Frustration, Refranation).
- `aspects.py`: Ptolemaic 5 aspects with applying/separating and sect-qualified interpretations.
- `reception.py`: Bonatti Strict / Lilly Standard reception with mutual reception detection.
- `temperament.py`: Lilly's humoral calculation (now includes inherent planetary natures).
- `lots.py`: Hermetic + Forensic Lots (40+) with kakosis checks.
- `kakosis.py`: 7 Conditions of Maltreatment (Hellenistic).
- `prediction.py`: Profections, Zodiacal Releasing, Firdaria, Solar Arc, Muntha, Transits.
- `decennials.py`: Valens Decennials with reset logic.
- `primary_directions.py`: Placidus semi-arc + zodiacal directions to angles/points.
- `hyleg.py`: Hyleg/Alcocoden vitality assessment.
- `phasis.py`: Planetary visibility (Arcus Visionis), synodic phases, Chariot condition.
- `stars.py`: 21 fixed stars + conjunctions + parans.
- `mansions.py`: 28 Lunar Mansions (tropical, Picatrix).
- `mundane.py`: Eclipse sophistication, Great Conjunctions, seasonal ingresses.
- `electional.py`: Kairos engine (Bonatti considerations).
- `medical.py`: Iatromathematics with disclaimer.
- `decumbiture.py`: Critical days, humoral analysis.
- `geniture.py`: Lord of Geniture (Lilly net fortitudes/debilities).
- `classical_mechanics.py`: Antiscia, Dodecatemoria, Planetary Hours.
- `nodes.py`: Digestive Model of Lunar Nodes.
- `solar_return.py`: Solar Return chart calculations.
- `calculations.py`: Core utilities (VoC, combustion, Via Combusta, besiegement, syzygy).
- `synthesis.py`: Human-readable report generation.
- `calculator/main.py`: Entry point for Swiss Ephemeris chart calculations.

## Trap Diary
| Issue | Cause | Fix |
|-------|-------|-----|
| Crash in `azalt` calculation | `swisseph` constant mismatch (`SE_ECL2HOR` vs `ECL2HOR`) | Updated constant to `swe.ECL2HOR` in `chart_calculator.py` |
| VoC false negatives | Only checked geometry, not application (speed) | Made VoC speed-aware in `calculations.py` |
| Bonatti reception too permissive | Threshold `>= 2` admitted bare Term reception | Changed to `>= 3` in `reception.py` |
| Chariot always False | `check_chariot()` was a stub | Implemented using DignityCalculator in `phasis.py` |
| Incomplete temperament | Missing inherent planetary natures in tally | Added `PLANET_NATURES` dict in `temperament.py` |

## Anti-Patterns
- Do NOT use modern psychological labels alone; always provide the traditional deterministic grounding (Dignity score).
- Do NOT ignore the Sect of the chart; it's the primary filter for Malefic/Benefic weighting.
- Do NOT perform surgery on Critical Days or during Eclipses.
- Do NOT admit bare Term reception (score 2) as valid in Bonatti Strict mode.
- Do NOT check VoC without verifying application (relative speed must show Moon closing gap).
