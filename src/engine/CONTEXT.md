# Astrological Engine

## Status
- Core calculation and synthesis logic verified.
- **Implemented**: Mundane Hierarchy (Eclipses to Ingresses), Horary Physics (Translation, Collection, etc.), Medical Astrology (Surgery & Crisis), Stellar Analysis (Parans), and Nodal Metabolic Phases.
- **Temperament**: Full William Lilly calculation (Asc, Moon, Season, Phase).
- **Lunar Mansions**: 28 Tropical Mansions (Picatrix) for electional intent.
- **Vitality**: Hyleg & Alcocoden assessment (Bonatti) for lifespan analysis.
- **Planetary Hours**: Traditional temporal hour calculation (Sunrise convention) with Chaldean ordering.
- **Primary Directions**: Placidus Semi-Arc method specifically for directions to Angles.
- **Reception Logic**: Computational framework for Unilateral and Mutual Reception with Strict/Standard modes.
- **Prediction**: Added Active Transits (Outer Planet impacts), fully historical Zodiacal Releasing, and Time Lord auditing for past/future dates.
- **Advanced Aspects**: Antiscia and Contra-antiscia integrated.

- **Advanced Mechanics**: Hermetic Lots (Fortune/Spirit + 5 Planets) with **Kakosis Status** (Maltreatment checks for Lot & Ruler), Almuten Figuris (Ibn Ezra scoring), Monomoiria (Zoidion & Trigonal), Doryphory (Spear-Bearer), and Dodecatemoria (Valens/Paul methods).
- **Hardened Synthesis**: Research-aligned Node model (Amplification/Greed), narrative-driven geometric aspect interpretations, and icon-driven planetary protocols.
- **Improved Horary**: Added Frustration, strict Moiety orbs, and enhanced Perfection/Denial logic.
- **Rectification**: Added Pauline Trigonal Monomoiria rectification protocol.

## Key Files
- `chart_calculator.py`: Handles ephemeris calls and geocoding, now integrates Advanced Mechanics.
- `advanced_mechanics.py`: **New**. Hermetic Lots, Almuten, Doryphory, Monomoiria engines.
- `horary.py`: Dynamics of aspect application, light movement (Translation, Collection), and Perfection/Denial (Prohibition, Frustration).
- `logic.py`: Implements synthesis (Jones patterns, Sect, Audits, Universal Overrides).
- `dignities.py`: Tables for Domicile, Exaltation, Triplicity, Terms, Faces.
- `temperament.py`: Lilly's Temperament/Humoral calculation engine.
- `mansions.py`: 28 Lunar Mansions calculator and electional database.
- `hyleg.py`: Vitality and Longevity (Alcocoden) engine.
- `planetary_hours.py`: Temporal hours and planetary ruler calculation.
- `primary_directions.py`: Placidus proportional semi-arc calculations.
- `reception.py`: Reception and Mutual Reception algorithm (Bonatti/Lilly).
- `mundane.py`: Solar/Lunar eclipse calculators and World Hierarchy.
- `medical.py`: Traditional Iatromathematics protocol.
- `electional.py`: Kairos engine for perfect timing (Electional Astrology).
- `src/scripts/generate_premium_report.py`: **Main Entry**. Premium forensic report generator (LLM synthesis over engine JSON).

## Trap Diary
| Issue | Cause | Fix |
|-------|-------|-----|
| Crash in `azalt` calculation | `swisseph` constant mismatch (`SE_ECL2HOR` vs `ECL2HOR`) | Updated constant to `swe.ECL2HOR` in `chart_calculator.py` |

## Anti-Patterns
- Do NOT use modern psychological labels alone; always provide the traditional deterministic grounding (Dignity score).
- Do NOT ignore the Sect of the chart; it's the primary filter for Malefic/Benefic weighting.
- Do NOT perform surgery on Critical Days or during Eclipses.
