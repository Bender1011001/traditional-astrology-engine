# Etsy Build-First Plan

Objective: win the Etsy PDF-seller segment by shipping workflow utility before paid conversion pressure.

## Policy

- Sales mode is controlled by `SALES_MODE` in environment:
  - `pilot`: paid checkout disabled globally.
  - `live`: paid checkout enabled.
- During `pilot`, we collect lead intent and run product interviews, but do not push paid checkout.

## Current Product Surface (Shipped)

- Lead capture page for gig-economy segment: `src/static/gig-economy.html`.
- Seller batch workflow in dashboard:
  - Upload CSV.
  - Generate ZIP PDF pack via `/api/v1/charts/bulk/pdf`.
  - Supports standard + Etsy-style column aliases.

## Etsy MVP Definition

- Input:
  - CSV headers:
    - Canonical: `name,date,time,city,state`
    - Etsy aliases: `client_name,birth_date,birth_time,birth_place`
- Output:
  - ZIP with one PDF per client row.
- Constraints:
  - Historical Use Only disclaimer present.
  - No medical/legal/financial advice output claims.

## Go/No-Go to move `SALES_MODE=live`

1. Generate 100+ successful PDFs from batch workflow without manual intervention.
2. Complete at least 10 seller interviews from waitlist.
3. Confirm one repeat usage cohort (same sellers using tool weekly).
4. Confirm support burden is manageable (no critical unresolved blockers).

## Activation

- Set env var on deployed API:
  - `SALES_MODE=live`
- Verify:
  - `GET /api/v1/billing/plans` returns `checkout_globally_enabled=true`.
  - Pricing CTAs no longer show pilot-gated messaging.
