---
project: static
status: complete
updated: 2026-05-08
---

# Static Assets (B2C Readings Site)

## Resume
- **Paid horary Stripe test flow (2026-05-09 UTC)**: The Horary Oracle page is now the cheap Stripe test surface. `horary.html` changed from a free-form answer flow to a `$5` one-time Stripe checkout CTA; `js/horary-app.js` posts the question/city/state to `POST /api/v1/horary/checkout`, redirects to Stripe, then on return from `?horary_paid=success&session_id=...` calls `POST /api/v1/horary/paid-answer` and renders the verified paid answer. `sw.js` is now `astro-v17-paid-horary` so cached `/js/horary-app.js` is refreshed. Terms/refunds mention the `$5` Horary Oracle question as a one-time digital purchase. Local browser smoke on `http://127.0.0.1:8765/horary.html` showed the `$5` CTA and no console warnings; production deploy/live Stripe smoke remain if needed.
- **Mobile optimization pass (2026-05-08 UTC)**: Fixed the current mobile website surface around the public conversion path. `style.css` now improves the sticky mobile header, hamburger menu sizing, tiny-screen brand/CTA fit, form/input/button touch targets, hero text wrapping, trust-item stacking, Daily Navigator target-date controls, compatibility secondary CTAs, and compact disclaimer copy. `consent.js` now owns a real capture-phase mobile nav controller for pages with inconsistent inline handlers; verified bug before the patch: `/compatibility.html` set the hamburger `aria-expanded` state but did not reveal `.nav-links`. Static CSS references were bumped to `rev20260508mobile1`; `sw.js` is now `astro-v15` / `astro-runtime-v15` and caches `consent.js`. Static HTML pages now also include an inline `mobile-nav-fallback` style, because the in-app browser reproduced a stale service-worker cache where fresh HTML loaded but old external CSS still kept `.nav-links` hidden.
- **Pick up at**: Production deploy and live mobile smoke if these local static changes should go public.
- **Blocked on**: Nothing known locally; live deployment still needs a normal Cloud Run deploy if these static changes should go public.

## Status
- **Working**: Main landing/readings page (index.html), guest checkout flow, premium reading generation, Stripe one-time payments.
- **Legacy/Deprecated**: Most old B2B pages (gig-economy, developer, documentation, etc) are still present but no longer linked from the main page.
- **In-Progress**: Mobile polish is implemented and locally verified; production deployment and live smoke remain if requested.

## Tech Stack
- HTML5, CSS3 (Vanilla — dark mystical theme)
- Vanilla JavaScript (ES6 Modules)
- Google Fonts (Cormorant Garamond, Inter)
- Stripe Checkout (guest, no-auth one-time payments)

## Key Files
- `index.html` — **The entire product**. Hero + birth form + reading output + pricing + FAQ. No separate pages needed.
- `style.css` — Complete dark theme with cosmic background, gold accents, glassmorphism cards.
- `js/reading-app.js` — **Main application logic**. Handles form submission, free reading via premium guest API, paywall, Stripe checkout redirect, post-payment generation, polling, markdown rendering, and feedback.
- `js/api.js` — API fetch helpers with fallback.
- `js/config.js` — API base URL configuration.
- `config.js` — Global config with API URL and subdomain redirect.
- `og-card.png` — Open Graph preview image.

## Architecture Quirks
- **The Form IS the Product**: No separate demo page. The birth form is in the hero section of index.html.
- **No Auth Required**: Everything works without login/signup/accounts. Guest flow only.
- **Free → Paywall → Paid**: 3 free premium readings per IP → paywall → Stripe checkout → generate reading.
- **CSS uses `:root` token system**: Dark theme (`--bg-deep`, `--gold`, etc). Cosmic star background via CSS `radial-gradient` patterns.
- **Backend Routes**:
  - `POST /api/v1/premium/guest/request` — Free reading (IP-limited to 3)
  - `GET /api/v1/premium/guest/status/{task_id}` — Poll for reading completion
  - `POST /api/v1/guest/checkout` — Create Stripe checkout session (no auth)
  - `POST /api/v1/guest/generate-paid` — Verify payment + start generation
  - `GET /api/v1/guest/task-status/{task_id}` — Poll paid reading status
  - `POST /api/v1/reading_feedback` — Accuracy feedback

## Revenue Model
- **$7** — Full Reading (one-time, Stripe)
- **$29** — Premium Forensic Audit (one-time, Stripe)
- No subscriptions. No accounts. No monthly fees.

## Trap Diary
| Issue | Cause | Fix |
|-------|-------|-----|
| Old site bounced visitors | B2B SaaS pitch vs B2C search intent | Complete redesign to consumer readings |
| Accounts killed conversion | Signup friction | Eliminated all auth; guest-only flow |
| $20-29/mo pricing failed | Too high for casual visitors | Dropped to $7 one-time |

## Anti-Patterns (DO NOT)
- Do NOT add login/signup requirements to the reading flow.
- Do NOT use TailwindCSS; stick to the custom Vanilla CSS system.
- Do NOT use technical jargon on the landing page (no "forensic audit", "Swiss Ephemeris", "CSV upload" in consumer-facing copy).
- Do NOT add subscription/monthly pricing. One-time only.
- Do NOT add external JS dependencies if a vanilla solution is possible.

## Build / Verify
- Open `index.html` via FastAPI (`python -m uvicorn src.app:app --reload`) or static server.
- Test the full reading flow with: Date=1996-08-13, Time=07:18, City=Fairfield, State=CA.
