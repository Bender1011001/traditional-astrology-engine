# API Guide

This guide provides a comprehensive reference for the Codex Caelestis v1 API.

## Base URL

`https://traditional-astrology.com/api/v1`

## Authentication

### User/Session Authentication

Most endpoints require a Bearer token in the `Authorization` header.
`Authorization: Bearer <your_jwt_token>`

### B2B API Key Authentication

For high-throughput generation, use an API key in the `X-API-Key` header.
`X-API-Key: sk_live_...`

## Endpoint Reference

### 1. Authentication & Users

- `POST /auth/register`: Create a new account.
- `POST /auth/login`: Authenticate and receive a JWT.
- `GET /auth/me`: Get current user profile and usage stats.
- `POST /auth/forgot-password`: Trigger password reset email.
- `POST /auth/reset-password`: Reset password with token.

### 2. Chart Calculation

- `POST /charts/calculate`: Generate 2full natal chart, forensic audit, and 5-day forecast.
- `POST /charts/generate`: B2B optimized endpoint for high-throughput chart data.
- `POST /charts/calculate-full`: Single endpoint for the full forensic nativity dossier.

### 3. Saved Charts

- `GET /charts/saved`: List all saved charts for the current user.
- `GET /charts/saved/{index}`: Get specific saved chart metadata.
- `GET /charts/saved/{index}/pdf`: Download a generated PDF report.
- `DELETE /charts/saved/{index}`: Remove a chart from saved list.

### 4. Billing & Subscriptions

- `POST /billing/create-checkout-session`: Start Stripe Checkout for a tier upgrade.
- `GET /billing/verify-checkout-session`: Verify payment success and upgrade account.
- `POST /billing/cancel-subscription`: Turn off auto-renewal.

### 5. Administration

- `POST /admin/patch_db`: Emergency database schema patching. Requires `X-Admin-Key`.

## Error Handling

The API uses standard HTTP status codes:

- `400 Bad Request`: Invalid input or logic error.
- `401 Unauthorized`: Missing or invalid authentication.
- `403 Forbidden`: Insufficient permissions (e.g., owner check failed).
- `429 Too Many Requests`: Rate limit or quota exceeded.
- `500 Internal Server Error`: Engine or database failure.

### Note on Response Formats

All calculated responses return a JSON object containing `technical_data` and potentially `plain_reading`.
