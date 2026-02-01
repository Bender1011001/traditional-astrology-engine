# Master Roadmap: Astrology SaaS Launch

This roadmap synthesizes the technical stability needs and business requirements to transition the project into a commercially viable product.

## Phase 1: Technical Stabilization (Immediate)
**Goal:** Ensure the engine is bug-free and tests pass reliably.

### 1. Fix Critical Bugs (Identified via Audit)
- [ ] **Fix Electional Engine Crash:**
    - **Issue:** `KeyError: <Sign.ARIES: 'Aries'>` in `src/engine/electional.py`.
    - **Fix:** Convert Enum to string before accessing `DignityCalculator.DOMICILES`.
- [ ] **Fix API Integration Tests:**
    - **Issue:** `test_calculate_endpoint_free` fails with 422.
    - **Fix:** Update test payload to use `date`/`time` keys instead of `birth_date`/`birth_time` to match `ChartRequest` schema.
- [ ] **Fix Test Configuration:**
    - **Issue:** `ModuleNotFoundError: No module named 'src'` when running pytest.
    - **Fix:** Create `pytest.ini` or `conftest.py` to correctly set the python path.

### 2. Code Health & Maintenance
- [ ] **Resolve Deprecation Warnings:**
    - Replace `datetime.utcnow()` with `datetime.now(datetime.UTC)` across the codebase (`src/engine/user_auth.py`, `src/services/subscription.py`, etc.).
    - Address SQLAlchemy `declarative_base` warning.
    - Address Pytest asyncio loop scope warning.

## Phase 2: Business Readiness (Pre-Launch)
**Goal:** Enable payments, user management, and legal compliance.

### 1. Payments & Subscriptions (Stripe)
- [ ] **Verify Stripe Products:**
    - Run `scripts/setup_stripe_products.py` to ensure products/prices exist in the connected Stripe account.
    - Verify Webhook handling in `src/api/v1/endpoints/billing.py`.
- [ ] **Frontend Checkout Flow:**
    - Test the full flow: Register -> Select Plan -> Stripe Checkout -> Success -> Dashboard.
    - Ensure "Upgrade" buttons correctly trigger the session creation.

### 2. User Management & Security
- [ ] **Email Service:**
    - Configure SendGrid (or SMTP) for password resets and welcome emails.
    - Verify `SENDER_EMAIL` env var.
- [ ] **Production Security:**
    - Rotate `JWT_SECRET` and `STRIPE_SECRET_KEY` for production.
    - Ensure `CORS_ORIGINS` is set correctly for the production domain.

### 3. Legal & Compliance
- [ ] **Review Legal Documents:**
    - Finalize `src/static/terms.html` and `src/static/privacy.html`.
    - Ensure Cookie Consent banner is present (if required).

## Phase 3: UX & Performance (Launch Window)
**Goal:** Optimize user experience and system reliability.

### 1. User Experience
- [ ] **Loading States:** Implement progress bars for chart calculation (as per `technical-stability-plan.md`).
- [ ] **Mobile Responsiveness:** Audit chart rendering on mobile devices.
- [ ] **Onboarding:** Add a "First Chart" wizard.

### 2. Infrastructure
- [ ] **Error Monitoring:** Integrate Sentry for backend/frontend error tracking.
- [ ] **Database Backups:** Configure automated PostgreSQL backups on Render.
- [ ] **Load Testing:** Run `locust` tests to verify stability under load (50+ concurrent users).

## Execution Order
1. **Phase 1** must be completed immediately to have a working baseline.
2. **Phase 2** runs in parallel with Phase 1 fixes where possible, but is required for "Open for Business".
3. **Phase 3** can be rolled out during the Beta/Soft Launch period.
