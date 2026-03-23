---
project: astrology
status: complete
updated: 2026-03-23
---

# Astrology Project

## Resume
- **Pick up at**: Site LIVE on Google Cloud Run (`astrology-engine-jknswoor2a-uc.a.run.app`). Custom domain mapping created — **DNS records need to be updated at Cloudflare** to point `traditional-astrology.com` to Google's IPs (4x A + 4x AAAA records, DNS-only/gray cloud). 516 tests green.
- **Last session**: Deployed to Google Cloud Run. Fixed CSP trailing-space bug, StaticFiles route shadowing for healthz, CanonicalDomainMiddleware .run.app skip. Added custom 404 page (celestial theme, auto-served by Starlette). Enabled kaniko Docker layer caching (72hr TTL). Cleaned up all Azure artifacts. Updated deploy script to use env.yaml. PWA install banner working.
- **Blocked on**: DNS update at Cloudflare — still resolving to old Azure IP `40.122.36.65`.

## Status
- **Working**: Astrological engine core, B2C consumer reading site, guest checkout (Stripe one-time payments), Computation Trace ("Show Our Work") integrated.
- **Broken**: None known.
- **Business Model (B2C)**: Direct-to-consumer natal chart readings. No accounts, no subscriptions.
  - **Free**: 3 premium readings per IP
  - **$7**: Full natal chart reading (one-time Stripe payment)
  - **$29**: Premium in-depth analysis (one-time Stripe payment)
- **Database**: Comprehensive pre-1700s traditional astrology—Managed via `AstrologicalDelineation` database table (SQLAlchemy).
- **Release Ready**: Version 2.0 (B2C Consumer Readings).
- **SEO**: Content pages (natal-charts, houses, aspects, etc.) kept for organic traffic with CTA banners → reading form.


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


## Deployment (Google Cloud Run)

- **Platform**: Google Cloud Run (managed, serverless containers)
- **Project**: `astrology-engine-prod`
- **Region**: `us-central1`
- **Service URL**: `https://astrology-engine-jknswoor2a-uc.a.run.app`
- **Custom Domain**: `traditional-astrology.com` (mapped, pending DNS)
- **Resources**: 512Mi memory, 1 CPU, 0-3 instances, 300s timeout
- **Build**: `gcloud builds submit` with kaniko caching (72hr TTL)
- **Deploy**: `python scripts/deploy_cloudrun.py` or manual `gcloud run deploy --env-vars-file env.yaml`
- **Entry Point**: `uvicorn src.app:app` (defined in `Dockerfile`)
- **Static Files**: Served by FastAPI via `src/app.py` mount (Single Service Architecture)
- **Health Check**: `GET /api/healthz` → `{"status": "healthy", "version": "2.0.0"}`
- **Custom 404**: `src/static/404.html` (auto-served by Starlette StaticFiles)

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

### Outreach & Leads
- `Lead` — Inbound marketing lead capture from website.
- `OutreachTarget` — Curated list of people/shops for outbound contact.
- `OutreachAttempt` — Logs of what was sent/attempted and when.

### Other
- `house_topoi.json` — House significations
- `example_charts.json` — Historical charts (Lilly, Newton, Napoleon, etc.)
- `glossary.json` — Traditional astrological terms

## Security & Audit Status
- **Verified**: '-d' city suffix backdoor removed from `charts.py` (2026-02-07).
- **Verified**: Admin and Owner endpoints require environment-based secret keys.
- **Verified**: Stripe webhook signature verification active.

## Documentation Reference
- `docs/SYSTEM_ARCHITECTURE.md` — High-level system overview.
- `docs/SECURITY_DOCUMENTATION.md` — Security model and remediation history.
- `docs/API_GUIDE.md` — v1 Endpoints and payloads.
- `docs/engine/architecture.md` — Deep dive into the Auditor and Service layer.
- `docs/engine/auditor.md` — Rules for the forensic audit.
- `docs/DEPLOYMENT.md` — VPS setup, env vars, and updates.
- `docs/FRONTEND.md` — Client-side architecture.
- `docs/TESTING.md` — Test suite guide.

## Key Files
- `src/app.py` — Entry point for the web server (Documentation at /docs).
- `src/static/js/reading-app.js` — B2C reading flow (form → free/paid → poll → render). Includes `buildTraceSection()` for rendering computation trace.
- `src/engine/trace_generator.py` — Reusable trace module: generates JSON dict of all computation steps for any chart.
- `src/services/premium_generator.py` — Background task for premium reports; includes computation trace generation (step 3).
- `src/api/v1/endpoints/guest_checkout.py` — Guest Stripe checkout (no auth, $7/$29).
- `LICENSE` — MIT License.
- `CHANGELOG.md` — Project history and rule updates.
- `src/database/data/glossary.json` — Astrological definitions.
- `src/engine/chart_calculator.py` — Core astronomical logic.
- `src/engine/calculate_advanced_mechanics.py` — Core math for electional/horary logic
- `src/engine/forensic_engine.py` — Forensic audit hub (replaced logic.py).
- `src/engine/classical_mechanics.py` — Antiscia, Dodecatemoria, Planetary Hours engine.
- `src/engine/dignities.py` — Essential dignity engine based on "Missing Codex".
- `src/engine/pdf_generator.py` — PDF report generation engine.
- `src/database/db_manager.py` — Loader for Codex delineations.
- `src/engine/chat_oracle.py` — RAG interface for chart Q&A.
- `src/engine/user_auth.py` — User authentication & accounts module.
- `scripts/outreach_run.py` — Automated outreach runner (email-only).
- `scripts/extract_all_traditional_data.py` — Comprehensive data extraction.
- `scripts/migrate_json_to_db.py` — Migrates JSON data to the SQLAlchemy database.
- `src/engine/daily_navigator.py` — Daily Navigator engine: synthesizes all timing layers into one briefing.
- `src/api/v1/endpoints/daily.py` — API endpoint for daily prediction briefings.
- `src/static/daily.html` — Frontend page for the Daily Navigator.

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
| Crash on startup | SyntaxError in `forensic.py` | Removed duplicate argument |
| CSP Violations on `/docs` | `SecurityHeadersMiddleware` blocking CDNs | Added `jsdelivr` and `tiangolo` to allow-list |
| SyntaxError: duplicate argument | Repeated `house_system` in method signature/calls | Cleansed signature and corrected API calls |
| High bounce rate | B2B SaaS pitch vs B2C search intent mismatch | Complete site redesign to consumer readings |
| Zero conversions | Account signup friction | Removed all auth; guest-only checkout flow |
| SEO CTR penalty | JS DOM mutation left B2B traces for Googlebot | Baked consumer CTA UI directly into HTML and deleted seo-bridge.js |
| Stripe CSP blocked | Checkout domain not in Content-Security-Policy | Added checkout.stripe.com + js.stripe.com to CSP |
| All free readings fail | `premium_generator.py` passed `house_system=` to `generate_chart_data()` which doesn't accept it | Removed the unsupported kwarg from the lambda call |
| Glossary tooltip text rendered inline, garbling all reading text | `basic.js` creates `.glossary-tooltip-popup` elements but `style.css` had NO CSS rules for them — popups showed as visible text | Added 56 lines of tooltip CSS: `display:none` by default, shown on hover/active |
| New static pages always redirect to index | `app.py` has `_LEGACY_REDIRECTS` list that 301-redirects listed pages BEFORE static file handler sees them | Remove the page from `_LEGACY_REDIRECTS` before it can be served as a static file |
| Primary directions trace silently empty | `raw["meta"]` uses `lat` not `latitude` for geographic latitude | Use `.get("lat")` not `.get("latitude")` |
| 31 pages not indexed in GSC, 5 indexed | `robots.txt` blocked `about.html` and `faq.html` despite them being in `sitemap.xml`, and correctly blocked B2B/auth pages | Removed `about.html` and `faq.html` from `robots.txt` disallow list |
| UnicodeEncodeError crashes pytest on Windows | Pytest captures `sys.stdout` but Windows default `cp1252` encoding crashes on emojis (🦅) output by `logger.py` | Added fallback `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` to console handler in `logger.py` |
| Silent cache failures for charts | `json.dumps()` in `CacheManager` crashed on `PlanetName` Enum objects | Added `default=str` kwargs to `json.dumps()` |
| API integration tests failing on /calculate | Endpoint transitioned from returning legacy `astronomical` key to `astronomy` via `ForensicEngine` | Updated `test_api_integration.py` assertions to expect `astronomy` |
| Daily Navigator crashes on dict planets/houses | `calculate_chart_data` returns planets as `{name: data}` dict and houses as `{int: cusp}` dict, but `_rebuild_chart_model` assumed list format | Added dict-handling branches for both planets and houses in `_rebuild_chart_model` |
| Planet constructor rejects `sign` kwarg | `Planet.sign` is a computed `@property` from longitude, not a dataclass field | Removed `sign=` from `Planet()` constructor calls |
| Chart constructor rejects `house_cusps` kwarg | `Chart` model uses `houses: Optional[Dict[int, float]]`, not `house_cusps: List[float]` | Changed to pass `houses=` dict instead |
| CSP trailing space crashes h11 on Cloud Run | CSP header ending with `; ` (space after semicolon) causes `h11.LocalProtocolError: Illegal header value` on every request | Remove trailing space/semicolon from last CSP directive |
| Root-level routes shadowed by StaticFiles mount | `app.mount("/", StaticFiles(html=True))` catches ALL paths before `@app.get("/healthz")` — returns 404 for HTML file not found | Use `/api/healthz` prefix so API router handles it before static mount |
| `.gcloudignore` `scripts/` excludes `src/scripts/` | `scripts/` glob matches both root `scripts/` and `src/scripts/` — latter is needed by `premium_generator.py` import chain | Use `/scripts/` (root-only) in `.gcloudignore` |
## Anti-Patterns (DO NOT)
- Do not edit planets_in_signs.json manually without running enhance_delineations.py
- Do not use Day/Night delineations interchangeably—sect matters
- Do not ignore sect when calculating triplicities or Firdaria
- Do not hardcode URLs—use `SITE_BASE_URL` environment variable
- Do not use bare `except:` clauses—always catch specific exceptions
- Do NOT add login/signup/account requirements to the reading flow — it kills conversions
- Do NOT add subscription/monthly pricing — one-time only for B2C
- Do NOT use technical jargon ("forensic audit", "Swiss Ephemeris") in consumer-facing copy

## Environment Variables (Production)
| Variable | Required | Description |
|----------|----------|-------------|
| `STRIPE_SECRET_KEY` | Yes | Stripe live secret key |
| `STRIPE_WEBHOOK_SECRET` | Yes | Stripe webhook signing secret |
| `JWT_SECRET` | Yes | Secret for signing JWT tokens (auto-generated on Render) |
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key for AI readings |
| `SENDGRID_API_KEY` | Yes* | SendGrid API key for email (*or configure SMTP) |
| `SMTP_HOST` | Yes* | SMTP server host (*if not using SendGrid direct) |
| `SMTP_PORT` | No | SMTP server port (default: 587) |
| `SMTP_USER` | Yes* | SMTP username |
| `SMTP_PASS` | Yes* | SMTP password |
| `SENDER_EMAIL` | Yes | From address for outgoing emails |
| `OUTREACH_POSTAL_ADDRESS` | Yes* | Postal address for CAN-SPAM compliance footer (*required for sends) |
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
