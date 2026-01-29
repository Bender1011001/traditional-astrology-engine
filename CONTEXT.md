
# Astrology Project

## Status
- **Working**: High-precision chart calculation, essential dignities, mundane events (Rank 1-4), textual delineations (Codex), complex forensic audit, Horary Physics, Medical Iatromathematics, Antiscia, Forensic 5-Day Forecast (Epitasis), Generative AI Oracle.
- **UI/UX**: Phase 2 Complete (Tooltips, FAQ, Comparison Table, Annual Plans, Analytics, Enhanced Paywall).
- **Database**: Comprehensive pre-1700s traditional astrology—20 JSON files, ~210KB total.
- **Release Ready**: Version 1.2 (The Aesthetic Upgrade).
- **Monetization**: Stripe (One-time + Annual/Monthly Subscriptions).


## Tech Stack
- Python 3.10+
- FastAPI, Uvicorn
- Swiss Ephemeris (`pyswisseph`)
- Vanilla JS, CSS (Glassmorphism)
- Google Gemini Flash (Generative AI)
- ReportLab (PDF Generation)
- Geopy, TimezoneFinder, pytz (Location & Time)
- Stripe (Payments)
- PyJWT (Authentication)


## Database Inventory (src/database/data/)

### Natal Chart Delineations
- `planets_in_signs.json` — 168 entries (7 planets × 12 signs × 2 sects)
- `planets_in_houses.json` — 84 entries (7 planets × 12 houses)
- `detailed_delineations.json` — General planet/sign descriptions

### Essential Dignities
- `terms_bounds.json` — Egyptian Terms for all 12 signs
- `faces_decans.json` — 36 Faces/Decans with Chaldean rulers
- `triplicities.json` — Fire/Earth/Air/Water Day/Night rulers

### Predictive Techniques
- `firdaria.json` — Firdaria planetary periods (Day/Night chart orders)
- `profections.json` — Annual Profection house meanings (ages 0-95)
- `solar_return_moon_houses.json` — SR Moon in natal houses

### Fixed Stars & Lunar Mansions
- `fixed_stars.json` — 16 major stars (4 Royals, Behenian, violent)
- `lunar_mansions.json` — 28 tropical mansions with electional properties

### Lots & Arabic Parts
- `lots_arabic_parts.json` — 16 Lots (Fortune, Spirit, Eros, Marriage, etc.)

### Longevity & Health
- `hyleg_alcocoden.json` — Vitality/longevity technique with planetary years
- `medical_astrology.json` — Iatromathematics (body parts, humors, critical days)

### Aspects & Eclipses
- `aspect_delineations.json` — 5 Ptolemaic aspects with sect variations
- `aspect_natures.json` — Basic aspect natures
- `eclipse_rules.json` — Solar/Lunar eclipse interpretation

### Electional Astrology
- `electional_considerations.json` — Moon conditions, planetary hours, Bonatti rules

### Other
- `house_topoi.json` — House significations
- `example_charts.json` — Historical charts (Lilly, Newton, Napoleon, etc.)
- `glossary.json` — Traditional astrological terms

## Key Files
- `src/api.py` — Entry point for the web server (Documentation at /docs).
- `src/static/basic.js` — Frontend logic including Paywall & Checkout.
- `src/static/success.html` — Payment success redirection handler.
- `LICENSE` — MIT License.

- `CHANGELOG.md` — Project history and rule updates.
- `src/database/data/glossary.json` — Astrological definitions.
- `src/engine/chart_calculator.py` — Core astronomical logic.
- `src/engine/logic.py` — Forensic audit and synthesis engine.
- `src/engine/dignities.py` — Essential dignity engine based on "Missing Codex".
- `src/engine/pdf_generator.py` — PDF report generation engine.
- `src/database/db_manager.py` — Loader for Codex delineations.
- `src/engine/chat_oracle.py` — RAG interface for chart Q&A.
- `scripts/extract_all_traditional_data.py` — Comprehensive data extraction.

## Data Sources
- `Binder1.txt` — Combined traditional source material (Valens, Firmicus, Lilly, Dorotheus).
- `docs/research/` — Lunar Mansions, Hyleg/Alcocoden, Placidus methods, Planetary Hours.

## Architecture Quirks
- Uses a custom "Egyptian Terms" system found in the binder which includes Sun and Moon.
- Implements "Universal Overdrive" logic where mundane events (eclipses) prioritize over natal placements.
- All planet-in-sign delineations have Day/Night sect variations.

## Trap Diary
| Issue | Cause | Fix |
|-------|-------|-----|
| Syntax Error in Logic | Improper use of multi_replace_file_content range | Full re-write of logic module |
| Missing South Node | Only North Node calculated by default | Added derived South Node calculation |
| 500 Server Error in Chart Calc | `swisseph` constant mismatch | Updated constant to `swe.ECL2HOR` |
| Negative Vitality Score | Hyleg calculation without floor | Added safety clamp (min 5 years) |
| Placeholder Delineations | Moon Pisces had "NOT FOUND" text | Enhanced via enhance_delineations.py |

## Anti-Patterns (DO NOT)
- Do not edit planets_in_signs.json manually without running enhance_delineations.py
- Do not use Day/Night delineations interchangeably—sect matters
- Do not ignore sect when calculating triplicities or Firdaria

## Build / Verify
```bash
python src/tests/test_audit.py
uvicorn src.api:app --reload
python scripts/extract_all_traditional_data.py  # Regenerate all data
python scripts/enhance_delineations.py  # Refresh delineation quality
```
