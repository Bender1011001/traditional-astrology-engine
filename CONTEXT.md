# Astrology Project

## Status

- **Working**: Natal Forensic Engine (Dignities, Receptions, Kakosis), Mundane Speculum (Placidian Semi-Arc), Solar Return Determination (Morin), Secondary Progressions (Mercury Stations), Iatromathematics (Decumbiture/Crisis Days), Horary Physics (Denial of Perfection).
- **Broken**: None.
- **UI/UX**: Phase 2 Complete (Tooltips, FAQ, Comparison Table, Annual Plans, Analytics, Enhanced Paywall, New Landing Page Design).
- **Database**: Comprehensive pre-1700s traditional astrology—Managed via `AstrologicalDelineation` database table (SQLAlchemy).
- **Release Ready**: Version 1.3 (User Accounts).
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


## Deployment (Azure)

- **Platform**: Microsoft Azure (Web App for Containers)
- **Orchestration**: `setup_azure.ps1` (initial) and `fix_azure_recommendations.ps1` (production upgrades)
- **High Availability**: 
  - **App Service**: Zone-redundant (S1 SKU)
  - **Database**: PostgreSQL Flexible Server with Zone Redundant HA (General Purpose SKU)
  - **Registry**: ACR Premium with Geo-replication (Central US <-> East US 2)
- **Resilience**: Geo-redundant backups enabled for PostgreSQL.
- **Monitoring**: Azure Service Health alerts configured for infrastructure events.
- **Entry Point**: `uvicorn src.app:app` (defined in `Dockerfile`)
- **Static Files**: Served by FastAPI via `src/app.py` mount (Single Service Architecture)

## AI Configuration
- **Model**: Google Gemini Flash (via OpenRouter)
- **Reproducibility**: Enforced via `temperature=0.2` and `top_p=0.85` for plain readings.
- **System Prompts**: Strict adherence to chart data and deterministic output structure.



## Database Inventory (SQLAlchemy: `astrological_delineations` table)

The core delineations are now stored in the database to allow for manual fixes and persistent overrides. The `src/database/data/legacy/` directory contains the original JSON files.

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
- `src/app.py` — Entry point for the web server (Documentation at /docs).
- `src/static/basic.js` — Frontend logic including Paywall & Checkout.
- `src/static/success.html` — Payment success redirection handler.
- `LICENSE` — MIT License.

- `CHANGELOG.md` — Project history and rule updates.
- `src/database/data/glossary.json` — Astrological definitions.
- `src/engine/chart_calculator.py` — Core astronomical logic.
- `src/engine/logic.py` — Forensic audit and synthesis engine.
- `src/engine/classical_mechanics.py` — Antiscia, Dodecatemoria, Planetary Hours engine.
- `src/engine/dignities.py` — Essential dignity engine based on "Missing Codex".
- `src/engine/pdf_generator.py` — PDF report generation engine.
- `src/database/db_manager.py` — Loader for Codex delineations.
- `src/engine/chat_oracle.py` — RAG interface for chart Q&A.
- `src/engine/user_auth.py` — User authentication & accounts module.
- `scripts/extract_all_traditional_data.py` — Comprehensive data extraction.
- `scripts/migrate_json_to_db.py` — Migrates JSON data to the SQLAlchemy database.

## Data Sources
- `Binder1.txt` — Combined traditional source material (Valens, Firmicus, Lilly, Dorotheus).
- `docs/research/` — Lunar Mansions, Hyleg/Alcocoden, Placidus methods, Planetary Hours.

## Architecture Quirks
- Uses a custom "Egyptian Terms" system found in the binder which includes Sun and Moon.
- Implements "Universal Overdrive" logic where mundane events (eclipses) prioritize over natal placements.
- All planet-in-sign delineations have Day/Night sect variations.
- **User Authentication**: Uses PBKDF2 password hashing (100k iterations), JWT tokens for sessions, and **SQLAlchemy** (SQLite local / PostgreSQL prod).
- **Total Logging Architecture**: 
  - **Backend**: `RequestLoggingMiddleware` captures all requests/responses/timings.
  - **Frontend**: Telemetry system captures clicks/errors and sends them to `/api/log/telemetry`.
  - **Storage**: JSON-structured logs with rotation in `logs/astrology_engine.jsonl`.
- **SEO & Search Visibility**:
  - **Canonical Domains**: All variants (www, http) are redirected to `https://traditional-astrology.com` via `CanonicalDomainMiddleware` to prevent indexing fragmentation.
  - **Crawlability**: `robots.txt` explicitly allows public pages but protects `/api`, dashboard files, and auth flow files.
  - **Internal Network**: Guide pages include "Related Guides" sections to ensure deep crawlability for search agents.

## Trap Diary
| Issue | Cause | Fix |
|-------|-------|-----|
| Syntax Error in Logic | Improper use of multi_replace_file_content range | Full re-write of logic module |
| Missing South Node | Only North Node calculated by default | Added derived South Node calculation |
| 500 Server Error in Chart Calc | `swisseph` constant mismatch | Updated constant to `swe.ECL2HOR` |
| Negative Vitality Score | Hyleg calculation without floor | Added safety clamp (min 5 years) |
| Placeholder Delineations | Moon Pisces had "NOT FOUND" text | Enhanced via enhance_delineations.py |
| Cache Manager Crash | `datetime.timedelta` undefined (wrong import) | Fixed import to `from datetime import datetime, timedelta` |
| Double Rate Limit | Free users counted twice per request | Removed duplicate check before cache lookup |
| Email Fake Success | Dev mode returned `True` without sending | Returns `False` + logs warning when not configured |
| Hardcoded URLs | Base URL was hardcoded in email links | Added `SITE_BASE_URL` env var |
| CORS Inflexibility | Hardcoded CORS origins | Added `CORS_ORIGINS` env var with sensible defaults |
| Console.error in Prod | JS errors visible to users | Silenced non-critical console outputs |
| Bare `except:` clauses | Catches all exceptions including system exits | Changed to `except Exception:` for safer handling |
| Stub Login/Register | Pages showed "coming soon" | Implemented full auth system with user_auth.py |
| Missing Function NameError | `_log_event` called but not defined in `api.py` | Restored missing helper function |
| Azure DB Auth Failure | Used `astrology_admin` instead of `astroadmin` | Use `astroadmin` as defined in `setup_azure.ps1` |
| ACR ImagePullFailure | Truncated Registry Password used in App Settings | Copy THE FULL 80+ CHAR password from ACR credentials |
| Plan Not Found (Reg) | Database not seeded with standard plans | Added `seed_plans()` to app startup event |
| Indexing Blind Spot | Lack of canonicalization & authority signals | Added `CanonicalDomainMiddleware` and tuned `robots.txt` |

## Anti-Patterns (DO NOT)
- Do not edit planets_in_signs.json manually without running enhance_delineations.py
- Do not use Day/Night delineations interchangeably—sect matters
- Do not ignore sect when calculating triplicities or Firdaria
- Do not hardcode URLs—use `SITE_BASE_URL` environment variable
- Do not use bare `except:` clauses—always catch specific exceptions

## Environment Variables (Production)
| Variable | Required | Description |
|----------|----------|-------------|
| `STRIPE_SECRET_KEY` | Yes | Stripe live secret key |
| `STRIPE_WEBHOOK_SECRET` | Yes | Stripe webhook signing secret |
| `JWT_SECRET` | Yes | Secret for signing JWT tokens (auto-generated on Render) |
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key for AI readings |
| `SENDGRID_API_KEY` | Yes* | SendGrid API key for email (*or configure SMTP) |
| `SENDER_EMAIL` | Yes | From address for outgoing emails |
| `SITE_BASE_URL` | No | Base URL for links in emails (default: https://traditional-astrology.com) |
| `CORS_ORIGINS` | No | Comma-separated allowed origins (default: production + localhost) |

## Build / Verify
```bash
python src/tests/test_audit.py
uvicorn src.api:app --reload
python scripts/extract_all_traditional_data.py  # Regenerate data to JSON
python scripts/migrate_json_to_db.py           # Sync JSON data to Database
python scripts/enhance_delineations.py         # Refresh delineation quality
```
