---
project: astrology
status: complete
updated: 2026-05-02
---

# Astrology Project

## Resume
- **Free-chart/revenue emergency fix (2026-05-01)**: Root cause found in production logs: after Cloud SQL persistence was fixed, every `/api/v1/premium/guest/request` was being keyed as Cloud Run's internal link-local client `169.254.169.126`, so the "3 free readings per IP" gate became a global service-wide lockout and returned 402 after three tests. Added `src/api/v1/client_ip.py` to prefer `X-Forwarded-For`/real visitor headers, changed free-reading quota to a rolling visitor window, record `GuestRequest` only after successful chart generation, and skip quota enforcement for non-rate-limitable fallback proxy addresses. Live smoke test on `https://traditional-astrology.com/api/v1/premium/guest/request` returned `200 completed`, `instant=True`, ~13k chars HTML, and Cloud Logging now shows a public visitor IP instead of `169.254.169.126`.
- **Revenue/checkout evidence (2026-05-01)**: Cloud Run logs since 2026-04-01 show only two successful `/api/v1/guest/checkout` session-creation requests and no paid generation calls. Stripe live API check for the last 45 days showed 100 recent Checkout Sessions returned by the API page, 0 paid sessions, 0 PaymentIntents, 0 succeeded payments, and $0.00 received. This means the technical checkout endpoint can create sessions, but no one has completed payment.
- **Conversion cleanup (2026-05-01)**: Landing page now removes Sign In/Create Account nav/modal cues from the main B2C path because current model is guest-only checkout, not accounts. Prices are aligned to `$25` full reading and `$69` complete analysis. `reading-app.js` now emits GA4 funnel events: `free_chart_submit`, `free_chart_success`, `free_chart_paywall`, `free_chart_error`, `checkout_click`, `checkout_redirect`, `checkout_error`, `paid_return`, `paid_generation_started`, and `paid_generation_error`. A top-of-result conversion bar was added above every successful free chart so the paid CTA appears immediately after chart generation, not only at the bottom of a long reading. Static asset query strings were bumped to `rev20260501funnel2` because JS/CSS cache for 86400 seconds. Global CSS hides legacy `navLoginBtn`/`navAccountBtn` on older SEO pages until those pages are rebuilt; live `natal-charts.html` still contains old login markup but CSS hides it. Live checkout smoke test created a Stripe Checkout Session through `/api/v1/guest/checkout` and then expired the test session successfully.
- **Latest investigation and fix (2026-05-01)**: GA4 and GSC mismatch is expected because GSC reports Google Search clicks/impressions while GA4 reports JS-tracked page activity. Cloud Run logs showed real scanner/prober noise (`wp-login.php`, `.env`, `.git/config`, `xmlrpc.php`) returning mostly 404/405. `/dashboard.html` and `/login.html` traffic in the Apr 3-Apr 30 GA window was not owner usage; available Cloud Run request logs show crawler/prober user agents including YandexBot, Bingbot, Amazonbot, AhrefsBot, Bytespider, Meta external agent, ClaudeBot, Stripebot, OpenAI search bot, GoogleOther, BuiltWith, and PowerShell checks. GA/GTM is now removed from `src/static/dashboard.html`; private/API surfaces emit `X-Robots-Tag: noindex, nofollow`; `/dashboard.html` is now included in the legacy auth-page 301 redirects to `/#get-reading` so it cannot continue serving as a tracked/private page.
- **Analytics cleanup/reporting (2026-05-01)**: Removed duplicate Google Tag Manager from static HTML and kept direct GA4 `G-RCNDWN4XVN` so frontend `gtag("event", ...)` funnel events still work without possible GTM double-counting. Live checks on `/`, `/natal-charts.html`, and `/sect-in-astrology.html` confirmed `hasGtag=True` and `hasGTM=False`; `/dashboard.html` and `/login.html` confirmed `301 /#get-reading`, `hasGtag=False`, `hasGTM=False`. Added `scripts/daily_funnel_report.py` to report production funnel health from Cloud Run logs plus Stripe live API instead of noisy GA snapshots. Command used: `python scripts\daily_funnel_report.py --date 2026-05-01 --days 1 --limit 2000`. Latest output: 38 browser-like page views, 4 unique browser-like IPs, 6 free chart successes, 11 free chart failures, 1 checkout session created, 0 paid sessions, $0.00 gross. GA Admin API attempt to mark key events for property `522626788` failed with `403 ACCESS_TOKEN_SCOPE_INSUFFICIENT`; key events still need Analytics Admin UI access or a token with `analytics.edit`.
- **Acquisition/SEO sprint (2026-05-02 UTC)**: Added three buyer-intent static pages targeting free chart and conversion searches: `free-natal-chart-pdf.html`, `astrology-reading-for-clients.html`, and `sect-astrology-calculator.html`. Each page is indexable, direct-GA4-only, contains Historical Use / no medical/legal/financial advice language, and links above the fold to `/#get-reading`. Homepage now has a "Popular Free Calculators" internal-link section pointing to the new PDF preview, sect calculator, and annual profections page; footer links now emphasize those free acquisition paths rather than old B2B pages. `reading-app.js` now tracks `print_save_pdf` and uses a real `printReading()` handler; the free result conversion bar includes a `Print / Save Preview PDF` action to support the "free natal chart PDF" search intent truthfully. Static asset query strings bumped to `rev20260501seo1`. Added `src/tests/test_seo_acquisition_pages.py` plus a `.gitignore` exception so new `src/tests/test_*.py` regression tests are trackable.
- **Chart event persistence and feedback (2026-05-02)**: Added durable `chart_events` and `reading_feedback_events` SQLAlchemy tables so future free chart generations save the submitted birth inputs, request context, generated chart summary, full returned reading HTML, reading hash, remaining free count, and generation timing. The free chart API now returns `chart_event_id`/`reading_hash`; the B2C result UI sends a real Good/Bad vote tied to that chart event and the backend persists it, while preserving older up/down feedback compatibility. Owner-only inspection is available at `/api/v1/owner/chart-events?limit=50` with the configured `X-Owner-Key`; pass `include_reading_html=true` only when the full HTML is needed. Static asset query strings bumped to `rev20260502chartvotes1`. Regression added in `src/tests/test_chart_event_tracking.py`. Live smoke produced chart event `f58c84dd-f21e-4d13-b249-2a7dc4b9de90` with London 1990-01-01 12:00, `sect=DAY`, 13,069 chars of HTML, and one persisted `good` feedback vote.
- **Auth/account evidence (2026-05-01)**: Google Cloud SQL exists as `astrology-487423:us-central1:astrology-db`. Direct SQL counts after production redeploy showed zero `users`, zero `user_subscriptions`, zero `invoices`, zero `api_keys`, zero `usage_records`, zero `guest_requests`, zero `async_report_tasks`, zero `horary_rate_limits`, zero `leads`, zero `outreach_targets`, zero `outreach_attempts`, and zero user-created chart/delineation rows; only the four seeded `subscription_plans` rows exist. Cloud logs available back to 2026-04-01 showed zero successful `POST /api/v1/auth/register`, zero successful `POST /api/v1/auth/login`, zero `/api/v1/auth/me`, and only the investigation owner API check returning 401. Public chart-like usage did occur before the fix: 87 successful POST 200 requests across `/api/v1/premium/guest/request`, `/api/v1/horary`, and `/api/v1/charts/daily-briefing` in the available log window.
- **Last deployment (2026-05-03 UTC)**: Live Cloud Run service `astrology-engine` in `astrology-engine-prod/us-central1` is deployed at revision `astrology-engine-00045-xw4`, serving 100% traffic, with `DATABASE_URL` present, `OWNER_BOOTSTRAP_KEY` configured, and Cloud SQL annotation `astrology-487423:us-central1:astrology-db`. Startup creates new tables via `Base.metadata.create_all`. Live checks confirmed `/` returns `200`, uses `rev20260502chartvotes1`, no longer references `rev20260501seo1`, has `gtag=True`, and `GTM=False`. Owner readback through `/api/v1/owner/chart-events` confirmed the live smoke chart event and Good vote persisted. The production service account has `roles/cloudsql.client` on the DB project, and `sqladmin.googleapis.com` is enabled in the production project. `scripts/deploy_cloudrun.py` includes the Cloud SQL attachment, `--quiet`, and disables local gcloud file logging so env values are not written to SDK logs.
- **Secret hygiene note (2026-05-01)**: Local gcloud log files from this and older deploy work contained parsed env var values because `gcloud run deploy --env-vars-file` logs arguments. Matching local gcloud logs were removed, a follow-up scan found no remaining env markers, and `core/disable_file_logging` was set for gcloud. Rotate the live DB/API/SMTP/Stripe secrets if this machine or transcript is considered exposed.
- **Pick up at**: Site fully **LIVE and SECURE** on Google Cloud Run (`https://traditional-astrology.com`). DNS records successfully point to Google's IPs and Google trust certificates are verified. Targeted tests green for visitor-IP extraction/rate limiting.
- **Last session**: Validated DNS propagation and SSL certificate issuance. Deployed Phase 2 Continuous Improvements:
  1. **Static Asset Edge Caching**: Added `CacheControlMiddleware` (`max-age=86400` for assets, `300` for HTML) to improve Lighthouse/Web Vitals.
  2. **Graceful Error Parsing**: Updated `reading-app.js` and `script.js` to map and join FastAPI 422 array responses instead of displaying `[object Object]` alerts.
  3. **Cloud Logging Observability**: Upgraded `ActivityLogger` to auto-detect `K_SERVICE` env var and swap to `JSONFormatter` on `sys.stdout` for native ingestion into Google Cloud Logging.
  4. **UI Loading Feedback**: Fixed `submitBtn` so `.btn-loading` span automatically toggles visibility and hides `.btn-text` when calling the API, fixing stagnant button UI.
- **Blocked on**: GA4 key-event marking still needs Analytics Admin UI access or OAuth scope `https://www.googleapis.com/auth/analytics.edit`; local gcloud auth currently lacks that scope. The B2C pipeline, deployment, custom domains, monitoring, and PWA systems are operational.

## Status
- **Working**: Astrological engine core, B2C consumer reading site, guest checkout (Stripe one-time payments), Computation Trace ("Show Our Work") integrated.
- **Broken**: None known.
- **Business Model (B2C)**: Direct-to-consumer natal chart readings. No accounts, no subscriptions.
- **Free**: 3 instant template-based readings per visitor per rolling window (no LLM, ~3-5s)
  - **$25**: Full natal chart reading (LLM-generated, one-time Stripe payment)
  - **$69**: Premium in-depth analysis (LLM-generated, one-time Stripe payment)
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
- `src/services/free_reading_generator.py` — **Instant free reading**: Template-based, zero-LLM reading generator. Extracts Sun/Moon/Rising, sect, dignity scorecard, profections from `Auditor` data and renders consumer-friendly HTML.
- `src/services/premium_generator.py` — Background task for LLM-generated premium reports (paid tiers only); includes computation trace generation (step 3).
- `src/api/v1/endpoints/premium.py` — Free guest reading endpoint (instant) + paid reading polling endpoint.
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
| Azure DB Auth Failure (legacy, migrated to Cloud Run) | Used `astrology_admin` instead of `astroadmin` | Migrated to Google Cloud Run — no longer applicable |
| ACR ImagePullFailure (legacy, migrated to Cloud Run) | Truncated Registry Password used in App Settings | Migrated to Google Cloud Run — no longer applicable |
| Plan Not Found (Reg) | Database not seeded with standard plans | Added `seed_plans()` to app startup event |
| Decennials | Apheta / Sequence | Confirmed correct. Zodiacal sequence (`(p.lon - asc) % 360`) correctly computes post-ascendant alignment. |
| Stars | Parans & Hour Angles | Confirmed correct. Uses proper spherical astronomy (RA/Dec and Hour Angle offsets) for Asc/Desc/MC/IC intersection logic. |
| Zodiacal Releasing | L4 Duration Drift | `prediction.py` L4 duration hardcoded to `0.208`. Replaced with `(2.5 / 12.0)` to eliminate mathematical drift across extensive calculations. |
| Decumbiture | Critical Day Lunar Math | Confirmed correct. The Newton-Raphson implementation uses safely wrapped modulos handling up to 270 degrees perfectly without anti-particle trapping. |
| Solar Return | Muntha Exact Degree | Confirmed correct. Muntha accurately maps to `(Sign * 30) + (Asc % 30)` for high-precision overlays. |
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
| Cloud Run logs show as text | Standard python `logging` writes text lines to `sys.stdout` which Cloud Logging doesn't parse | Check for `os.environ.get("K_SERVICE")` and inject a custom `JSONFormatter` into `StreamHandler` |
| `[object Object]` on validation error | FastAPI 422 errors return `err.detail` as a list of dicts (`[{"loc": ..., "msg": ...}]`) which crashes `alert(err)` | Map the array to extract `{d.loc[x]}: {d.msg}` into a unified string |
| Array indexing `IndexError` at exactly 360.0 degree boundary | `int(lon / 30)` evaluates to `12` at exactly 360 | Wrapped mathematics with bounds `int((lon % 360.0) / 30.0) % 12` |
| Silent Combustion Check Failures in Electional.py | Engine checked for `"COMBUST"` but calculations.py explicitly maps Moon combustion to `"DARK_MOON"` | Corrected the strings in `electional.py` to match Lunar phase strings |
| Horary Semantic Perfection Physics Bugs | `horary.py` contained hardcoded positive offsets preventing retrograde/sinister interference detection and backwards logic for collection/translation weight validation | Re-wrote condition boundaries using the relative `dist = get_aspect_distance()` instead of basic algebra, and corrected logical `and`/`or` boundaries for weight checks |
| Essential Dignity Peregrine Exclusivity Bug | `dignities.py` lacked Peregrine scoring in the core calculator and improperly protected planets in Fall/Detriment from Peregrine compounding in the variant calculator | Implemented independent Peregrine stacking (-5) whenever `domicile==exaltation==triplicity==term==face==0` to match historic point values |
| Aspect Application Reversal Vector | `aspects.py` `is_applying` falsely flagged separated aspects as applying and applying aspects as separating due to mathematically inverted sign checks against the relative velocity derivative `d(p2-p1)/dt`. | Restructured distance-to-velocity gradient checks: logic now successfully demands that `rel_speed > 0` when `dist > 0`, and `rel_speed < 0` when `dist < 0`. |
| Primary Directions Placidus Pole Proxy Bug | `primary_directions.py` improperly hardcoded the geographic latitude (the Ascendant's pole) as the proxy Pole for all planet-to-planet Promittor projections. | Intercepted the calculation sequence to derive each Significator's exact proportioned Pole and Hemispheric quadrant via `_get_pole_and_hemisphere()`, enabling true "Under the Pole" Oblique progression. |
| Hyleg Baseline Disqualification Bug | `hyleg.py` disqualified any planet in the 1st House via a hardcoded `altitude > 0` filter, contradicting the Ascendant's status as a primary Hylegical place. | Bypassed the altitude filter specifically for House 1, acknowledging that the 1st house spans below the horizon natively. |
| Medical Astrology Missing Hostile Aspects | `medical.py` solely checked Conjunctions for Malefic/Luminary interference in the remediation window calculator, silently ignoring the classical Square/Opposition strictures. | Injected explicit mathematical geometric constraint validations for 90° (Square) and 180° (Opposition) with appropriate severity point scaling. |
| Equatorial Sect Math Corruption | `mundane.py` and `phasis.py` illegally passed Ecliptic planetary longitude coordinates to `swe.azalt` while using the `swe.EQU2HOR` or `swe.FLG_SWIEPH` projection flags. This grossly corrupted the apparent Solar altitude and caused fatal day/night sect inversions. | Re-mapped the projection matrices universally to `swe.ECL2HOR` to accurately parse physical ecliptic coordinates. |
| Void of Course Kinematic Intersection Bug | `calculations.py` `is_void_of_course` falsely flagged the Moon as VoC when the target planet was moving backwards or very fast, because it used a static sign boundary separator `dist_to_target < dist_to_end` rather than projecting the intersection dynamically over time `v = d/t`. | Rewrote the intersection condition to explicitly solve for the dynamic offset (`time = dist / closing_speed`, then `moon_travel = time * moon_speed`), ensuring bounds-checking occurs at the exact mathematical point of perfection. |
| Hermetic Lot Polarity Inversion | `lots.py` accidentally inverted the `a_lon` and `b_lon` arguments for the Lots of Necessity, Courage, and Nemesis during daytime calculations, calculating them backwards (e.g. `Asc + Mercury - Fortune` instead of `Asc + Fortune - Mercury`), contradicting Hellenistic physics because they relate to the Lot of Fortune rather than Spirit. | Mathematically swapped the arguments for the day/night polarity branching to faithfully reconstruct the Paulus Alexandrinus physics framework. |
| Dodecatemoria Harmonic Offset Corruption | `advanced_mechanics.py` superimposed its calculation arc against the planet's longitude (`longitude + arc`) rather than the start of the sign boundary (`sign_start + arc`), inadvertently boosting the formula by an entire N-harmonic factor (calculating x13 instead of Valens x12, and x14 instead of Paulus x13). | Repointed the mathematical projection vector to hinge entirely off `sign_start`, securing the intended classical geometric mapping to the micro-zodiac. |
| Humoral Temperament Tally Dilution | `temperament.py` indiscriminately added the inherent nature of *all* 7 traditional planets to the humor tally instead of just the *significant* planets (Asc ruler, Moon, and planets aspecting the Moon/Asc), creating a homogeneous 'blob' temperament for all nativities. It was also missing 60° (Sextile) and 120° (Trine) aspects in its aspect detectors. | Restructured the routine to first compile a `significant_planets` set, added checking for Sextile/Trine/Ascendant aspects, and restricted the inherent nature tally to only iterate over the authorized set matching Lilly's specific workflow. |
| Abscission False Collision & Hellenistic VoC Bug | `horary.py` `check_abscission` wrongly assumed that any physical interposition resulted in a collision cut, because it used `abs()` on the closing speed, failing to gate for when the interposing planet is moving away faster than the pursuer. Additionally, `check_void_of_course_hellenistic` judged the 30-degree boundary using static aspect distance rather than kinematic moon travel distance. | Swapped absolute speed comparison in Abscission to dynamic directional vector `closing_speed`, verifying true convergence over time. Implemented `v=d/t` kinematic time projection into the Hellenistic VoC checks. |
| Cloudflare analytics wildly different from GSC | Cloudflare is DNS-only (grey cloud), not proxying. DNS resolves to Google IPs (216.239.x.x), `server: Google Frontend`. CF dashboard shows DNS query counts (bots, resolvers), not page views. | Confirmed architecture is correct as Google Cloud Run direct. GA4 + GSC is the real analytics stack. Removed orphaned `cloudflared_config.yml` and `.cloudflared/`. |
| `www.traditional-astrology.com` times out | No DNS record configured for `www` subdomain in Cloudflare | Need to add CNAME record: `www` → `traditional-astrology.com` in Cloudflare DNS dashboard |

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
