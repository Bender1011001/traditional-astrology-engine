# Astrological Engine

## Status
- Core calculation and synthesis logic verified.
- **Implemented**: Mundane Hierarchy (Eclipses to Ingresses), Horary Physics (Translation, Collection, etc.), Medical Astrology (Surgery & Crisis), Stellar Analysis (Parans), and Nodal Metabolic Phases.
- **Advanced Aspects**: Antiscia and Contra-antiscia integrated.

## Key Files
- `chart_calculator.py`: Handles ephemeris calls and geocoding.
- `logic.py`: Implements synthesis (Jones patterns, Sect, Audits, Universal Overrides).
- `dignities.py`: Tables for Domicile, Exaltation, Triplicity, Terms, Faces.
- `mundane.py`: Solar/Lunar eclipse calculators and World Hierarchy.
- `horary.py`: Dynamics of aspect application and light movement.
- `medical.py`: Traditional Iatromathematics protocol.
- `electional.py`: Kairos engine for perfect timing (Electional Astrology).

## Anti-Patterns
- Do NOT use modern psychological labels alone; always provide the traditional deterministic grounding (Dignity score).
- Do NOT ignore the Sect of the chart; it's the primary filter for Malefic/Benefic weighting.
- Do NOT perform surgery on Critical Days or during Eclipses.
