# Astrologer Validation Packet (Template)

Purpose
Provide a clear, practitioner-friendly way to verify the math behind chart calculations without reviewing code.

What you will receive
- A CSV export for each test chart with planetary positions, house cusps, lots, aspects, and dignity scores.
- A one-page summary of inputs (date/time/place, house system, zodiac system, ayanamsa).

What we need from you
- Confirm that the math matches your software within the tolerance targets below.
- Note any mismatches and the exact values you get in your tools.
- A short statement of verification results (1-2 paragraphs).

Inputs for each chart
- Birth date (YYYY-MM-DD)
- Birth time (HH:MM) with time zone resolution handled by the engine
- City, State/Country
- House system (Whole Sign, Placidus, Regiomontanus, etc.)
- Zodiac system (Tropical or Sidereal) and ayanamsa if sidereal

Outputs to verify (priority order)
1) Planetary longitudes
2) House cusps and angles (Asc, MC)
3) Lots (Fortune, Spirit, etc.)
4) Aspects (type, orb, applying/separating)
5) Dignity scoring components (domicile, exaltation, triplicity, term, face)

Tolerance targets
- Planetary longitudes: <= 0.01 degrees
- House cusps: <= 0.10 degrees
- Lots: <= 0.10 degrees
- Aspects: orb matches within 0.10 degrees
- Dignity: categorical match (ruler assignments) and score match

Suggested workflow
1) Enter the exact chart inputs into your software.
2) Compare against the CSV export row by row.
3) Mark each category as Pass/Fail and note any discrepancies.

Deliverable format (example)
- Chart: [Name / Date / Place]
  - Planets: Pass (all within tolerance)
  - Houses: Pass (all within tolerance)
  - Lots: Fail (Fortune off by 0.2 deg in my tool)
  - Aspects: Pass
  - Dignity: Pass
- Summary: Overall Pass/Fail and short notes.

Notes
- The goal is to validate math, not interpretive delineations.
- If your software uses different default orbs or lot formulas, please note that.
