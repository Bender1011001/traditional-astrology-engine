# Security Documentation

This document outlines the security architecture and remediation efforts for Codex Caelestis.

## Security Model Overview

Codex Caelestis follows an "API-first, Security-First" design, utilizing multi-layered authentication and strict role-based access control (RBAC).

### 1. Authentication

The system supports two primary authentication methods:

- **JWT (JSON Web Tokens)**: Used for user sessions. Tokens are issued upon successful login or after a successful Stripe payment session. They contain the `chart_hash` and `tier` information to authorize premium report generation.
- **Static API Keys**: Used for B2B (Business-to-Business) integrations. These are long-lived keys (`sk_live_...`) managed in the Developer Dashboard. These are stored as SHA-256 hashes in the database.

### 2. Authorization (RBAC)

Access levels are defined as follows:

- **Guest**: Access to basic public pages and the `/calculate` endpoint (limited by IP rate limiting and "free" tier restrictions).
- **User**: Authenticated individuals who can save charts, download PDFs, and access premium reports based on their subscription tier.
- **Developer/B2B**: Authenticated via API key. Access is metered against a monthly quota defined in their subscription plan.
- **Admin**: Access to internal maintenance tools (e.g., `/patch_db`). Requires a separate `ADMIN_SECRET_KEY`.
- **Owner**: Access to the Owner's Dashboard for user management and subscription overrides. Requires specific email verification or a `OWNER_BOOTSTRAP_KEY` for setup.

### 3. Rate Limiting

- **Public API**: IP-based rate limiting to prevent abuse of the free tier.
- **Authenticated API**: Account-based rate limiting based on subscription plan tiers.
- **Admin API**: Strict IP-based lockouts after 5 failed attempts per hour.

## Vulnerability Remediation

### 1. City-Suffix Backdoor (Resolved 2026-02-07)

**Issue**: A development bypass allowed users to access "paid" tier features (LLM-synthesized reports) for free by appending ` -d` to the city name in a chart request.

**Remediation**: 
- Removed the parsing logic in `src/api/v1/endpoints/charts.py` that checked for the `-d` suffix.
- Standardized the tier verification logic to strictly use JWT claims or API key metadata.

---
*Last Updated: 2026-02-07*
