
# Astrology Project

## Status
- **Working**: High-precision chart calculation, essential dignities, mundane events (Rank 1-4), textual delineations (Codex), complex forensic audit, Horary Physics, Medical Iatromathematics, Antiscia, Forensic 5-Day Forecast (Epitasis), Generative AI Oracle, and premium UI.
- **Release Ready**: Version 1.1 (The Chronocrator Upgrade).

## Tech Stack
- Python 3.10+
- FastAPI, Uvicorn
- Swiss Ephemeris (`pyswisseph`)
- Vanilla JS, CSS (Glassmorphism)
- Google Gemini Flash (Generative AI)

## Key Files
- `src/api.py` — Entry point for the web server.
- `src/engine/chart_calculator.py` — Core astronomical logic.
- `src/engine/logic.py` — Forensic audit and synthesis engine.
- `src/engine/dignities.py` — Essential dignity engine based on "Missing Codex".
- `src/database/db_manager.py` — Loader for Codex delineations.
- `src/engine/chat_oracle.py` — RAG interface for chart Q&A.

## Architecture Quirks
- Uses a custom "Egyptian Terms" system found in the binder which includes Sun and Moon, deviating from standard Hellenistic practice.
- Implements "Universal Overdrive" logic where mundane events (eclipses) prioritize over natal placements.

## Trap Diary
| Issue | Cause | Fix |
|-------|-------|-----|
| Syntax Error in Logic | Improper use of multi_replace_file_content range | Full re-write of logic module |
| Missing South Node | Only North Node calculated by default | Added derived South Node calculation |
| 500 Server Error in Chart Calc | `swisseph` constant mismatch (`SE_ECL2HOR` vs `ECL2HOR`) | Updated constant to `swe.ECL2HOR` in `chart_calculator.py` |
| Negative Vitality Score | Hyleg calculation simply subtracted malefic years without floor | Added safety clamp (min 5 years) and vitality rating |

## Build / Verify
`python src/tests/test_audit.py`
`uvicorn src.api:app --reload`
