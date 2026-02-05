# COO Operations Manual (The "Brain")

**Objective**: Reach **$6,000 USD/month** Net Revenue.
**Current Phase**: Phase 5 (Launch & Monitoring) - STATUS: LAUNCHED.

## 1. The Strategy (North Star)
We are building a "Forensic Astrology" SaaS.
-   **Product**: Automated PDF Reports ($9.99 / $99.00).
-   **USPs**: "Forensic Accuracy", "Sect-Corrected Algorithms", "Medieval Techniques".
-   **Economics**: 94% Margin. Volume game. Target: 22 sales/day.

## 2. Prime Directives (The "Red Lines")
1.  **DO NOT GET USER SUED**: All claims must be defensible "entertainment" or "historical calculation". No medical/financial advice.
2.  **DO NOT GET USER ARRESTED**: Zero tolerance for fraud, dark patterns, or illegal content.
3.  **Priorities**: Safety > Revenue.

## 3. Key Metrics (KPIs)
-   **Traffic**: Monitor Google Search Console for indexation of landing pages.
-   **Conversion**: Track "Checkout Success" vs. "Landing Page Views".
-   **Revenue**: Check Stripe Balance explicitly.

## 3. The Tech Stack (Business Critical)
-   **Payment**: Stripe (Live Mode). Keys in `.env`.
-   **Hosting**: Render (Starter Plan).
-   **Security**: CSP Headers hardened (GTM/GA Allowed).
-   **SEO**: `sitemap.xml` indexes `/`, `/almuten-figuris.html`, `/lot-of-fortune.html`, `/hyleg-calculator.html`.
-   **Retention**: Automated PDF Emailer (Stickiness Loop) Active.

## 4. Operational Protocols
### A. Start of Session (The Check-in)
1.  **Read this file (`OPS_MANUAL.md`)**.
2.  **Read `task.md`** for immediate tactical blockers.
3.  **Check Stripe** (if user asks for status): Use `stripe` MCP or ask user.
4.  **Check Sitemap**: Ensure new pages are added.

### B. "Don't Break The Money" Rules
-   **Never** deploy code that breaks the checkout flow (`billing.py` / `basic.js`).
-   **Always** verify the `action=regenerate` logic in `basic.js` after editing that file.
-   **Disclaimer**: Always maintain the "Historical Use Only" legal shield.

## 5. Current Task List (Snapshot)
See `task.md` for live status.
-   [x] Phase 4 (SEO) Complete.
-   [ ] Phase 5 (Launch/Monitoring) In Progress.
    -   Active: Monitoring First Sale.
    -   Active: Verifying SEO Indexing.
