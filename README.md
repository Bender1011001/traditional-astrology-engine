# Codex Caelestis: Traditional Forensic Astrology Engine

Codex Caelestis is a high-precision astrological engine built for the reconstruction and analysis of traditional nativity and mundane data. It implements 135 core rules derived from Hellenistic and Medieval sources (Valens, Ptolemy, Dorotheus, Bonatti, and Lilly).

## Features

### 1. Forensic Nativity Analysis
- **Constitutional Fitness**: Complete Sect, Hayz, and Halb filtering.
- **Essential Dignity**: Full weighting for Domicile, Exaltation, Triplicity (Dorothean), Terms (Egyptian/Valens), and Face (Chaldean).
- **Accidental Strength**: Combustion/Cazimi, Besiegement, Speed, and House Placement (Whole Sign).
- **Shadow Physics**: Implementation of Antiscia and Contra-antiscia reflection.

### 2. Temporal Audits (Predictive)
- **Profections**: Annual, Monthly (Continuous/Saltatory), and Daily profections.
- **Zodiacal Releasing**: High-precision ZR up to Level 3, including 'Loosing of the Bond' logic.
- **Chronocrators**: Firdaria periods with sub-period shifts.

### 3. Mundane Hierarchy (Universal Causation)
- **Eclipse Sophistication**: Quadrant-based timing of intensification and chorography (geographic impact).
- **Great Conjunctions**: Historical tracking of Jupiter-Saturn cycles.
- **Comet Logic**: Classification by color and tail direction for mundane disruption.
- **Ingress Overrides**: Aries Ingress (Rank 4) logic overriding natal promises.

### 4. Iatromathematics (Medical)
- **Surgery Advisory**: Real-time safety auditing avoiding Eclipses, Critical Days, and Lunar sign conflicts.
- **Crisis Timing**: 7, 14, and 21-day "Crisis in Consciousness" progression.

## Getting Started

### Prerequisites
- Python 3.10+
- `pyswisseph` (Swiss Ephemeris Python bindings)
- `fastapi` & `uvicorn`

### Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install fastapi uvicorn pyswisseph pydantic
   ```
3. Run the application:
   ```bash
   python src/api.py
   ```
4. Open your browser at `http://127.0.0.1:8000`.

## Architecture
- `src/engine/`: Core algorithmic logic.
- `src/database/data/`: Ingested codex delineations (JSON).
- `src/static/`: Premium Glassmorphic UI.

## License
Educational Use Only. Forensic outcomes based on historical tradition.
