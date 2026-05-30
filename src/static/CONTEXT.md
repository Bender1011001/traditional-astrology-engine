---
project: static
status: active
updated: 2026-05-26
---

# Static Assets (Traditional Astrology Site)

## Current Product Shape
- The public site offers one reading: the free full 20+ page traditional natal report.
- Visitors can generate as many full natal reports as they want.
- The form stays guest-first: no account, email, or login is required to create the report.
- The rendered report includes a reader-support ask, preset one-time tip buttons, a custom tip form, and a $5/month supporter option. The report remains free either way.
- The rendered report has simple sharing controls: native Share where supported, plus a Copy Link fallback.
- Retired public offer pages, including the old compatibility, daily, horary, and policy-offer routes, redirect back to the main free-report funnel before static serving.

## Latest Changes
- `index.html`, `traditional-birth-chart-calculator.html`, `free-natal-chart-pdf.html`, `natal-charts.html`, `faq.html`, `contact.html`, `terms.html`, and `astrology-reading-for-clients.html` now describe the single free full-report offer.
- `js/reading-app.js` starts the complete report flow, polls the result, renders feedback controls, shows simple Share Reading / Copy Link actions, and then shows preset tip, custom tip, and monthly supporter controls.
- `sw.js` cache is `astro-v27-support-tips`.
- Public script cache bust for `reading-app.js` is `rev20260526support1`.
- `robots.txt` disallows retired pages, and `sitemap.xml` lists the current public acquisition pages only.
- Current support/tip changes are local and not deployed yet because they touch payment/subscription behavior. The prior share-control release was deployed to Cloud Run after local tests and live custom-domain smoke checks passed.

## Key Files
- `index.html` - Main landing page, birth form, free full-report positioning, methodology, and FAQ.
- `natal-charts.html` - SEO entry page for natal chart intent, using the same report form.
- `traditional-birth-chart-calculator.html` - SEO entry page for traditional calculator intent.
- `free-natal-chart-pdf.html` - SEO entry page for PDF/report intent.
- `astrology-reading-for-clients.html` - SEO entry page for written reading intent.
- `style.css` - Site design system and report-flow UI styling.
- `js/reading-app.js` - Main report request, polling, rendering, feedback, and tip UI.
- `js/api.js` and `js/config.js` - API helpers and base URL handling.
- `geomancy.html` / `js/geomancy-app.js` - Public classical geomancy explainer/tool, still separate from the natal-report product.

## Backend Routes Used By Static Site
- `POST /api/v1/premium/guest/request` - Starts an unlimited free full-report request.
- `GET /api/v1/premium/guest/status/{task_id}` - Polls report completion.
- `POST /api/v1/reading_feedback` - Sends reading accuracy feedback.
- `POST /api/v1/guest/tip` - Opens an optional one-time tip Checkout page after the full report renders.
- `POST /api/v1/guest/monthly-support` - Opens an optional monthly supporter Checkout page. This does not unlock report content.
- `POST /api/v1/geomancy/cast` - Casts a classical geomancy shield chart.

## Operating Rules
- Do not add locked report access or paid report tiers to the natal reading funnel. Tips/supporter checkout must stay optional and must not unlock content.
- Do not add login/signup requirements to report generation.
- Keep "Historical Use Only" and no medical/legal/financial advice language on report and policy surfaces.
- Keep the page copy oriented around traditional astrology method: sect, dignities, houses, lots, profections, and time-lord context.
- Keep static code vanilla HTML/CSS/JavaScript unless the repository is intentionally migrated.

## Verification
- Open through FastAPI with `python -m uvicorn src.app:app --reload`.
- Test the main flow with Date `1996-08-13`, Time `07:18`, City `Fairfield`, State `CA`.
- Before deploy, run focused Python tests for chart-event tracking and SEO pages, plus `node --check src/static/js/reading-app.js`.
