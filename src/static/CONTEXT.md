---
project: static
status: complete
updated: 2026-05-11
---

# Static Assets (B2C Readings Site)

## Resume
- **Production deploy verified (2026-05-11 UTC)**: Static geomancy education/tool and horary subscription assets are live on `https://traditional-astrology.com` via Cloud Run revision `astrology-engine-00096-564` at 100% traffic. Live smoke passed for `/horary.html`, `/geomancy.html`, `/sw.js`, `/js/horary-app.js`, `/api/v1/horary/access`, a valid unauthenticated horary cast blocking with `401`, `/api/v1/geomancy/cast`, and live Stripe horary subscription checkout creation for a throwaway account; the smoke Checkout Session was expired immediately in Stripe. New-revision Cloud Logging `severity>=ERROR` returned `[]`.
- **Geomancy education + horary subscription pivot (2026-05-11 UTC)**: `geomancy.html` now acts as both explainer and free shield-chart tool: it leads with "What Is Geomancy?", explains why rule-based geomancy fits the Traditional Astrology brand, documents odd/even lines, daughters, parity combination, judge validity, shield positions, and how geomancy differs from horary. Horary moved from the temporary one-question Stripe test SKU to an account-based `$5/month` unlimited subscription. `js/horary-app.js` checks `/api/v1/horary/access`, starts `/api/v1/horary/subscription/checkout`, verifies return through billing checkout verification, then casts via `/api/v1/horary/subscriber-answer`. `dashboard.html` now exposes subscription renewal status and a cancel-renewal button backed by the existing billing cancellation endpoint. `terms.html`, `refunds.html`, homepage pricing/teasers, sitemap dates, and `sw.js` were updated for the new product model.
- **Geomancy page and $1 horary copy (2026-05-10 UTC)**: Added `geomancy.html` and `js/geomancy-app.js` as a public shield-chart tool backed by `POST /api/v1/geomancy/cast`; it renders judge, outcome, witnesses, all 16 shield positions, source-basis caveat, and Historical Use Only safety copy. `style.css` now includes geomancy result/dot/shield styling, `sw.js` is `astro-v21-geomancy-horary-dollar` and precaches `/geomancy.html` plus `/js/geomancy-app.js`, and `index.html` / `horary.html` navigation links include Geomancy. Horary public copy moved from `$5` to `$1`, with `terms.html` and `refunds.html` updated. `config.js` now makes FastAPI-served localhost pages call their own origin instead of always forcing `127.0.0.1:8000`; separate Vite/static local ports still use the default API port. Verification: focused tests passed (`25 passed`), JS syntax checks passed for `config.js`, `js/geomancy-app.js`, and `js/horary-app.js`; Playwright desktop/mobile smoke on `http://127.0.0.1:8765/geomancy.html` rendered 16 shield cards, no console errors, and no horizontal overflow.
- **Superseded paid horary Stripe test flow (2026-05-09 UTC)**: The first horary monetization pass used a one-question Stripe checkout only as a cheap payment-system test surface. This was removed from the public product on 2026-05-11 because there were no real customer sales to preserve; current horary monetization is the `$5/month` account subscription above.
- **Mobile optimization pass (2026-05-08 UTC)**: Fixed the current mobile website surface around the public conversion path. `style.css` now improves the sticky mobile header, hamburger menu sizing, tiny-screen brand/CTA fit, form/input/button touch targets, hero text wrapping, trust-item stacking, Daily Navigator target-date controls, compatibility secondary CTAs, and compact disclaimer copy. `consent.js` now owns a real capture-phase mobile nav controller for pages with inconsistent inline handlers; verified bug before the patch: `/compatibility.html` set the hamburger `aria-expanded` state but did not reveal `.nav-links`. Static CSS references were bumped to `rev20260508mobile1`; `sw.js` is now `astro-v15` / `astro-runtime-v15` and caches `consent.js`. Static HTML pages now also include an inline `mobile-nav-fallback` style, because the in-app browser reproduced a stale service-worker cache where fresh HTML loaded but old external CSS still kept `.nav-links` hidden.
- **Pick up at**: Monitor production funnel events and Stripe checkout starts for the new horary subscription.
- **Blocked on**: Nothing known in the deployed static horary/geomancy surfaces.

## Status
- **Working**: Main landing/readings page (index.html), guest checkout flow, premium reading generation, $5/month Horary Oracle Unlimited subscription, public geomancy explainer/shield chart, Stripe one-time payments for natal reports, Stripe subscription billing for horary.
- **Legacy/Deprecated**: Most old B2B pages (gig-economy, developer, documentation, etc) are still present but no longer linked from the main page.
- **In-Progress**: Production monitoring for horary subscription interest and geomancy engagement.

## Tech Stack
- HTML5, CSS3 (Vanilla — dark mystical theme)
- Vanilla JavaScript (ES6 Modules)
- Google Fonts (Cormorant Garamond, Inter)
- Stripe Checkout (guest one-time payments and account-based horary subscription)

## Key Files
- `index.html` — **The entire product**. Hero + birth form + reading output + pricing + FAQ. No separate pages needed.
- `style.css` — Complete dark theme with cosmic background, gold accents, glassmorphism cards.
- `js/reading-app.js` — **Main application logic**. Handles form submission, free reading via premium guest API, paywall, Stripe checkout redirect, post-payment generation, polling, markdown rendering, and feedback.
- `js/api.js` — API fetch helpers with fallback.
- `js/config.js` — API base URL configuration.
- `config.js` — Global config with API URL and subdomain redirect.
- `geomancy.html` / `js/geomancy-app.js` — Public classical geomancy explainer and shield chart UI backed by `/api/v1/geomancy/cast`.
- `horary.html` / `js/horary-app.js` — $5/month Horary Oracle Unlimited subscription checkout and subscriber answer flow.
- `og-card.png` — Open Graph preview image.

## Architecture Quirks
- **The Form IS the Product**: No separate demo page. The birth form is in the hero section of index.html.
- **Guest-first readings**: Free preview and natal report purchases work without forcing account creation. Horary subscription requires an account because recurring access must be tied to a customer.
- **Free → Paywall → Paid**: 3 free premium readings per IP → paywall → Stripe checkout → generate reading.
- **CSS uses `:root` token system**: Dark theme (`--bg-deep`, `--gold`, etc). Cosmic star background via CSS `radial-gradient` patterns.
- **Backend Routes**:
  - `POST /api/v1/premium/guest/request` — Free reading (IP-limited to 3)
  - `GET /api/v1/premium/guest/status/{task_id}` — Poll for reading completion
  - `POST /api/v1/guest/checkout` — Create Stripe checkout session (no auth)
  - `POST /api/v1/guest/generate-paid` — Verify payment + start generation
  - `GET /api/v1/guest/task-status/{task_id}` — Poll paid reading status
  - `POST /api/v1/reading_feedback` — Accuracy feedback
  - `GET /api/v1/horary/access` — Report current account horary subscription access
  - `POST /api/v1/horary/subscription/checkout` — Create $5/month horary subscription checkout
  - `POST /api/v1/horary/subscriber-answer` — Cast horary for an active subscriber
  - `POST /api/v1/geomancy/cast` — Cast a classical geomancy shield chart

## Revenue Model
- **Free** — Instant natal chart preview plus one free Complete Analysis LLM report per real visitor IP.
- **$5/month** — Horary Oracle Unlimited subscription (deterministic code engine, Stripe subscription)
- **$25** — Full Reading (one-time, Stripe)
- **$69** — Complete Analysis (one-time, Stripe)
- Natal reports stay one-time. Horary is the low-cost subscription tool because each question is deterministic code rather than LLM generation.

## Trap Diary
| Issue | Cause | Fix |
|-------|-------|-----|
| Old site bounced visitors | B2B SaaS pitch vs B2C search intent | Complete redesign to consumer readings |
| Accounts killed chart conversion | Signup friction | Keep the natal reading funnel guest-first; require accounts only where recurring horary access needs billing identity |
| $20-29/mo pricing failed | Too high for casual visitors | Dropped to $7 one-time |

## Anti-Patterns (DO NOT)
- Do NOT add login/signup requirements to the reading flow.
- Do NOT use TailwindCSS; stick to the custom Vanilla CSS system.
- Do NOT use technical jargon on the landing page (no "forensic audit", "Swiss Ephemeris", "CSV upload" in consumer-facing copy).
- Do NOT add subscriptions to the natal reading funnel. The exception is Horary Oracle Unlimited, which is account-based at $5/month because the cost is deterministic and recurring access needs billing identity.
- Do NOT add external JS dependencies if a vanilla solution is possible.

## Build / Verify
- Open `index.html` via FastAPI (`python -m uvicorn src.app:app --reload`) or static server.
- Test the full reading flow with: Date=1996-08-13, Time=07:18, City=Fairfield, State=CA.
