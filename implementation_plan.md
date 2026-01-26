# Technical Specification: Classical Astrology Engine Expansion

## 1. Overview
This specification details the implementation of 135 missing rules (36 structural logic, 99 interpretive) to achieve full classical fidelity in the astrology engine.

## 2. Structural Logic Rules (36 Rules)

### 2.1 Almuten Figuris (Ibn Ezra System)
- **Hylegical Points**: Calculate dignity for Sun, Moon, Ascendant, Lot of Fortune, and Pre-natal Syzygy (Sanctum Sanctorum).
- **Weighted Scoring**:
    - Domicile: +5
    - Exaltation: +4
    - Triplicity: +3
    - Term: +2
    - Face: +1
- **Accidental Modifiers**:
    - House Placement: 1st/10th (+12), 7th/4th/11th (+10), 5th (+7), 2nd (+6), 9th (+5), 3rd (+4), 8th (+3), 6th/12th (+2).
    - Day/Night Ruler bonus.
- **Output**: Identification of the "Captain of the Soul" (Almuten Figuris).

### 2.2 Mundane Hierarchy & Eclipses
- **Universal Precedence**: Implementation of the "Suspension Mechanism" where Mundane events override Natal promises.
- **Ptolemaic Duration**:
    - Solar: 1 hour obscuration = 1 year influence.
    - Lunar: 1 hour obscuration = 1 month influence.
- **Spatial Timing (Quadrants)**:
    - Ascendant: Months 1-4.
    - Midheaven: Months 5-8.
    - Descendant: Months 9-12.
- **Chorography**: Filtering eclipse impact based on geographic visibility and sign-region affiliation.
- **Comet Logic**: Classification by color (Martial/Saturnian) and tail direction.

### 2.3 Horary Physics (Aspect Logic)
- **Translation of Light**: A faster planet transfers light from a slower one it has separated from to another it is approaching.
- **Collection of Light**: Two planets approaching a third slower planet.
- **Prohibition**: A third planet intercedes an aspect before perfection.
- **Refrenation**: A planet turns retrograde before completing an aspect.
- **Void of Course**: Definition as the Moon making no further Ptolemaic aspects before leaving her sign.

### 2.4 Time-Lord Systems & Revolutions
- **Firdaria**: Complete 75-year sequence for Day (Sun-first) and Night (Moon-first) births.
- **Solar Return (Morin System)**:
    - **Muntha**: Locate the profected Ascendant in the SR chart.
    - **Superimposition**: Mapping SR house cusps onto Natal houses.
    - **Lord of the Year**: Conditional audit (is it angular/dignified in the SR?).
- **Lunar Phases**: 8-fold Soli-Lunar cycle (0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°).

### 2.5 Medical Astrology (Melothesia)
- **Anatomical Mapping**: Aries (Head) to Pisces (Feet).
- **Surgery Rules**:
    - Prohibit surgery when Moon is in the sign ruling the body part.
    - Avoid surgery on "Critical Days" (Moon square/opposite decumbiture Moon).
    - Avoid surgery during Eclipses.

## 3. Interpretive Data Rules (99 Rules)

### 3.1 Missing Planets in Signs (Ingestion List)
The following 99 delineations must be extracted from `binder_chunks/` and populated in `src/database/data/planets_in_signs.json` and `planets_in_houses.json`:

#### Sign Delineations (Partial list - for full ingestion):
- **Saturn**: Gemini (Ref: Part 026, 025), Sagittarius, Scorpio (Natal).
- **Jupiter**: Taurus (Ref: Part 002), Gemini (Sect-specific), Libra.
- **Mars**: Gemini, Virgo, Aquarius.
- **Sun**: Sagittarius (Ref: Part 002), Gemini, Aquarius.
- **Venus**: Gemini, Aries (Night), Scorpio (Night).
- **Mercury**: Gemini (Full Domicile), Leo, Sagittarius.
- **Moon**: Gemini, Leo, Aquarius.

#### House Delineations (Missing/Placeholders):
- **Sun**: 2nd, 3rd, 4th, 7th, 8th, 9th, 11th, 12th.
- **Moon**: 2nd, 3rd (Full), 5th, 6th (Full), 8th, 9th, 11th, 12th.
- **Jupiter**: 3rd, 4th, 5th, 6th, 8th, 9th, 11th, 12th.
- **Mars**: 3rd, 4th, 5th, 8th, 9th, 10th, 11th.

## 4. Implementation Targets
- `src/engine/calculations.py`: Almuten points, Eclipse timing.
- `src/engine/dignities.py`: Accidental dignity scores.
- `src/engine/prediction.py`: Firdaria sequences, Solar Return Muntha.
- `src/engine/mundane.py`: Universal suspension logic, Chorography.
- `src/database/data/*.json`: Textual delineations.

## 5. Validation Criteria
- Almuten Figuris matches Ibn Ezra's manual examples.
- Solar Return superimposition correctly identifies natal house overlaps.
- Firdaria period transitions occur at 75-year intervals with correct sub-periods.
- Interpretive JSONs contain zero "NOT" or "NOT FOUND" entries.
