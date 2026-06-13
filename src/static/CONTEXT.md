---
project: static
status: active
updated: 2026-06-12
---

# Static Assets (Traditional Astrology Site)

## Current Product Shape
- Two readings, one funnel:
  - **Free reading** — single-pass LLM traditional natal reading. Guest-first: no account, email, or login required. Unlimited.
  - **Complete Astrological Analysis ($69, one-time)** — six-pass deep report (20+ pages), bought via guest Stripe Checkout (no account), rendered in-browser and delivered as a PDF to the checkout email.
- **No subscriptions, ever.** Every payment is a one-off fulfilled same-day, so the site can be shut down at any time without owing anyone anything (owner decision, 2026-06-12).
- Delivery guarantee shown on-site: if anything goes wrong with delivery, the buyer keeps the reading and gets their money back.
- Optional one-time tips remain after the free reading. The monthly supporter option was removed (it's a subscription).
- The rendered report has simple sharing controls: native Share where supported, plus a Copy Link fallback.
- Retired public offer pages redirect back to the main funnel before static serving.

## Latest Changes (2026-06-12)
- Relaunched paid funnel: `js/reading-app.js` adds the $69 upsell after the free reading, starts guest checkout (`POST /api/v1/guest/checkout?tier=premium_audit`), and handles the `/?paid=true&session_id=...` return → `POST /api/v1/guest/generate-paid` → polls `GET /api/v1/guest/task-status/{id}` → renders the paid reading with a "PDF emailed" banner.
- Free tier flipped from giving away `premium_audit` to `free_llm_chart` (1 LLM pass) in `src/api/v1/endpoints/premium.py`.
- Paid-order safety net in `src/services/premium_generator.py` + `admin_notifier.notify_paid_order_issue`: Discord alert on paid generation failure, missing customer email, or PDF/email delivery failure; paid orders can never run with fewer LLM passes than their tier promises.
- `index.html` copy updated: free reading is the hook, $69 Complete Analysis is the upgrade, "no subscription" stated everywhere, money-back delivery guarantee in FAQ.
- `sw.js` cache is `astro-v28-premium-checkout`; script cache bust is `rev20260612premium1` (also in `natal-charts.html`, `pt/`, `sr/`).

## Key Files
- `index.html` - Main landing page, birth form, free reading + paid upgrade positioning, methodology, and FAQ.
- `natal-charts.html` - SEO entry page for natal chart intent, using the same report form.
- `traditional-birth-chart-calculator.html` - SEO entry page for traditional calculator intent.
- `free-natal-chart-pdf.html` - SEO entry page for PDF/report intent.
- `astrology-reading-for-clients.html` - SEO entry page for written reading intent.
- `style.css` - Site design system and report-flow UI styling.
- `js/reading-app.js` - Report request, polling, rendering, paid checkout/return flow, feedback, and tip UI.
- `js/api.js` and `js/config.js` - API helpers, base URL handling, purchase analytics (`trackPurchase`).
- `geomancy.html` / `js/geomancy-app.js` - Public classical geomancy explainer/tool.

## Backend Routes Used By Static Site
- `POST /api/v1/premium/guest/request` - Starts an unlimited free reading request (single LLM pass).
- `GET /api/v1/premium/guest/status/{task_id}` - Polls free reading completion.
- `POST /api/v1/guest/checkout?tier=premium_audit&...` - Creates the $69 guest Stripe Checkout session (no account, CSRF-exempt).
- `POST /api/v1/guest/generate-paid?session_id=...` - Verifies payment and starts paid generation (idempotent per Stripe session).
- `GET /api/v1/guest/task-status/{task_id}` - Polls paid reading completion.
- `POST /api/v1/reading_feedback` - Sends reading accuracy feedback.
- `POST /api/v1/guest/tip` - Optional one-time tip Checkout page after the free reading.
- `POST /api/v1/geomancy/cast` - Casts a classical geomancy shield chart.

## Operating Rules
- **Never add a subscription product or anything that creates a standing liability (credits, balances, annual plans).** One-off purchases only.
- Do not add login/signup requirements to report generation — free or paid.
- The free reading must stay genuinely free and useful; the paid tier must never silently degrade (paid iteration floor is enforced server-side).
- Keep "Historical Use Only" and no medical/legal/financial advice language on report and policy surfaces.
- Keep the page copy oriented around traditional astrology method: sect, dignities, houses, lots, profections, and time-lord context.
- Keep static code vanilla HTML/CSS/JavaScript unless the repository is intentionally migrated.

## Verification
- Open through FastAPI with `python -m uvicorn src.app:app --reload`.
- Test the main flow with Date `1996-08-13`, Time `07:18`, City `Fairfield`, State `CA`.
- Paid flow gate: a REAL $69 self-purchase on the live site (then self-refund) before announcing — code tests are not sufficient (see project rule: verify on live site).
- Before deploy, run focused Python tests for chart-event tracking and SEO pages, plus `node --check src/static/js/reading-app.js`.
