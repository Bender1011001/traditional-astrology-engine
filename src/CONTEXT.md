# [Engine/Logic]

## Status
- **Working**: Planet models, dignity calculations, sect logic, Lots, Fixed Stars, Nodal Physics, Profections, Email Capture Service, API V1 (Forensic Engine), Token-based Rate Limiting (Agency/Master).
- **Broken**: Rectification event-based logic (placeholder).
- **In-Progress**: API V2 structure established.

## Tech Stack
- Python 3.9+ 
- No external dependencies (pure math).
- SendGrid / SMTP for emails.
- File-based Caching (/tmp for serverless capability).

## Key Files
- `models.py` — Core data structures (Planet, Chart, Sect).
- `logic.py` — The "Brain" of the forensic audit.
- `app.py` — FastAPI entry point (V1/V2 routing).
- `api/v1/schemas/forensic_v1.py` — Public contract for V1 output.
- `api/v1/middleware/rate_limiting.py` — Token-bucket logic.
- `engine/email_service.py` — Email notification handler.

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
| Rate Limit Localhost | Internal calls from email capture | Whitelist 127.0.0.1 in RateLimiter logic. |
| Rate Limit Collisions | Multi-user IP sharing | Switched to `api_key_id` as primary key for B2B. |

## Anti-Patterns
- Do NOT use modern psychological interpretations (e.g., "Soul Growth" for Nodes).
- Do NOT use Placidus or quadrant houses for Topics; use Whole Sign.
