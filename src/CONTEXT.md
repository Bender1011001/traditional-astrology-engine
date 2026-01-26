# [Engine/Logic]

## Status
- **Working**: Basic planet models, simple dignity calculations (Dignity score), basic sect logic.
- **Broken**: No Lots, No Fixed Stars, No Nodal Physics, No Profection Muntha logic.

## Tech Stack
- Python 3.9+ 
- No external dependencies (pure math).

## Key Files
- `models.py` — Core data structures (Planet, Chart, Sect).
- `logic.py` — The "Brain" of the forensic audit.
- `calculations.py` — Math utils for dignity.
- `main.py` — Entry point CLI.

## Architecture Quirks
- The system must adhere to **Forensic Astrology** principles (Valens/Bonatti).
- **Sect is King**: All formulas for Lots must reverse based on Day/Night.
- **Nodes are Metabolic**: Not psychological. NN = Intake, SN = Excretion.
- **Stars Override Planets**: Parans > Ecliptic.

## Trap Diary
| Issue | Cause | Fix |
|-------|-------|-----|
| Inaccurate Dignity | Using Ptyolemaic Terms | Use Egyptian Terms (Valens) as per Binder 1. |
| Lots Calculation | Ignoring Sect Reversal | Implement strict `if sect == NIGHT: swap(A, B)` logic. |

## Anti-Patterns
- Do NOT use modern psychological interpretations (e.g., "Soul Growth" for Nodes).
- Do NOT use Placidus or quadrant houses for Topics; use Whole Sign.
