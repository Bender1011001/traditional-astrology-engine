# Static Assets (B2C Readings Site)

## Status
- **Working**: Main landing/readings page (index.html), guest checkout flow, premium reading generation, Stripe one-time payments.
- **Legacy/Deprecated**: Most old B2B pages (gig-economy, developer, documentation, etc) are still present but no longer linked from the main page.
- **In-Progress**: Polishing reading output rendering, mobile optimizations.

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
