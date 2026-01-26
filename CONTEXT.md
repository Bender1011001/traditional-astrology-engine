
# Astrology Project

## Status
- **Working**: High-precision chart calculation, essential dignities, mundane events (Rank 1-4), textual delineations (Codex), complex forensic audit, Horary Physics, Medical Iatromathematics, Antiscia, Forensic 5-Day Forecast (Epitasis), and premium UI.
- **Release Ready**: Version 1.1 (The Chronocrator Upgrade).

## Tech Stack
- Python 3.10+
- FastAPI, Uvicorn
- Swiss Ephemeris (`pyswisseph`)
- Vanilla JS, CSS (Glassmorphism)

## Key Files
- `src/api.py` — Entry point for the web server.
- `src/engine/chart_calculator.py` — Core astronomical logic.
- `src/engine/logic.py` — Forensic audit and synthesis engine.
- `src/engine/dignities.py` — Essential dignity engine based on "Missing Codex".
- `src/database/db_manager.py` — Loader for Codex delineations.

## Architecture Quirks
- Uses a custom "Egyptian Terms" system found in the binder which includes Sun and Moon, deviating from standard Hellenistic practice.
- Implements "Universal Overdrive" logic where mundane events (eclipses) prioritize over natal placements.

## Trap Diary
| Issue | Cause | Fix |
|-------|-------|-----|
| Syntax Error in Logic | Improper use of multi_replace_file_content range | Full re-write of logic module |
| Missing South Node | Only North Node calculated by default | Added derived South Node calculation |

## Build / Verify
`python src/tests/test_audit.py`
`uvicorn src.api:app --reload`
