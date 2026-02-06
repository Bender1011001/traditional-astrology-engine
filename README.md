# Judicial Astrology Engine: The Sovereign Release

Judicial Astrology Engine is a high-precision, practitioner-grade astrological engine built for the reconstruction and analysis of traditional nativity and mundane data. It implements 135 core rules derived from Hellenistic and Medieval sources (Valens, Ptolemy, Dorotheus, Bonatti, and Ibn Ezra).

Live site: [traditional-astrology.com](https://traditional-astrology.com)

## What's New: The Sovereign Release (v1.0)
The Sovereign Release marks the graduation of the engine from a research project to a production tool for practitioners.

- **Hardened Synthesis**: Fully aligned with traditional binder specifications, featuring the **Amplification/Greed Node Model** and narrative-driven geometric aspect interpretation.
- **Advanced Mechanics**: Integrated **Almuten Figuris** (Ibn Ezra 12-point house scoring) and the **Panaretos Lot Protocol** (full Forensic Audits for the 7 Hermetic Lots).
- **Professional CLI**: A new entry point for high-precision report generation (`src/scripts/generate_practitioner_report.py`).
- **Audit-Grade Logic**: Every calculation now includes a **Kakosis (Maltreatment)** audit, checking for besiegement, combustion, and malefic intervention.

## Core Features

### 1. Forensic Nativity Analysis
- **Soul Guardian (Almuten Figuris)**: Detailed scoring based on Ibn Ezra's traditional protocols.
- **Hermetic Lots**: Full implementation of the 7 Hermetic Lots with sect-based vector reversal.
- **Constitutional Fitness**: Complete Sect, Hayz, and Halb filtering.
- **Accidental Strength**: Combustion/Cazimi, Besiegement, Speed, and House Placement (Whole Sign/Placidus/Regiomontanus).
- **Shadow Physics**: Implementation of Antiscia and Contra-antiscia reflection.

### 2. Temporal Audits (Predictive)
- **Chronocrators**: Firdaria periods, Profections (Annual/Monthly), and Zodiacal Releasing (Level 3).
- **Time Lord Auditing**: Integrated historical timeline generation.

### 3. Mundane Hierarchy (Universal Causation)
- **Eclipse Sophistication**: Quadrant-based timing of intensification and chorography (geographic impact).
- **Great Conjunctions**: Historical tracking of Jupiter-Saturn cycles.
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
1. Clone the repository and initialize a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Professional CLI
Generate technical JSON data and a narrative Markdown report:
```bash
python src/scripts/generate_practitioner_report.py --name "Alexander Hamilton" --date "1755-01-11" --time "12:00" --city "Charlestown" --house_system "P"
```

### Running the Web API
The API is self-documenting via FastAPI:
```bash
python src/api.py
```
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Architecture
- `src/engine/`: Core algorithmic logic.
- `src/database/data/`: Ingested codex delineations (JSON).
- `src/static/`: Premium Glassmorphic UI.

## License
MIT License. See [LICENSE](LICENSE) for details.

### Medical Disclaimer
Portions of this software deal with historical medical astrology (Iatromathematics). This content is provided for **historical and educational research purposes only**. It is **NOT medical advice**. Under no circumstances should any information provided by this software be used to make health decisions or schedule medical procedures. Always consult a qualified medical professional for health concerns.

