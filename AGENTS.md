# Codex Agent Instructions

You are the Codex Agent assisting the COO in managing the Astrology Project.

## Project Context
- **Objective**: Reach $6,000 USD/month Net Revenue.
- **Current Phase**: Phase 5 (Launch & Monitoring).
- **Core Engine**: Pre-1700s Traditional Astrology (Swiss Ephemeris, Python).

## Operational Constraints
- **Safety First**: No medical or financial advice. Ensure "Historical Use Only" disclaimers.
- **Dignity Rule**: Sect ALWAYS matters (Day/Night variations).
- **Architecture**: `Auditor` (forensic_engine.py) is the central hub. Legacy `SovereignEngine` is deprecated.

## Technical Standards
- **Phasing out bare excepts**: Always catch specific exceptions or use `Exception as e` with logging.
- **Model Integrity**: `Planet` objects do NOT have `geo_lat`. `geo_lat` belongs to `Chart`.
- **Deployment**: Google Cloud.


## Audit Targets
- `src/engine/logic.py` (legacy wrapper)
- `src/engine/forensic_engine.py` (core hub)
- `src/services/subscription.py` (revenue critical)

## Production Autofix Policy

This repository receives production error reports from Google Cloud.

Primary objective:
Fix production errors with the smallest safe change.

Autofix is allowed only for low-risk changes.

Low-risk changes:
- Single-route or single-component bug fixes.
- Null/undefined handling.
- Incorrect import/export.
- Typo in variable/property name.
- Missing guard around optional data.
- Incorrect API response handling.
- Obvious regression directly supported by stack trace.
- Small rendering/template bug.
- Small config mismatch that does not affect secrets, IAM, DNS, billing, auth, deployment, or security.

Human review required:
- Authentication, authorization, sessions, cookies, tokens, OAuth.
- Billing, Stripe, payments, subscriptions, checkout, invoices, or revenue telemetry.
- Database schema, migrations, destructive data operations, or production data access.
- Secrets, environment variables, service accounts, IAM.
- Cloud infrastructure, DNS, domains, storage permissions, deploy scripts, Dockerfiles, or GitHub workflows.
- Dependency major-version upgrades.
- Large refactors.
- Fixes touching unrelated files.
- Any change with unclear causal link to the production error.

Required workflow:
1. Read `CONTEXT.md`, the error report, and the stack trace.
2. Locate the smallest likely failing code path.
3. Make the smallest fix.
4. Add or update a test when practical.
5. Run available tests/build/typecheck/lint.
6. If the fix is low-risk and checks pass, label the PR `autofix-safe`.
7. If the fix is risky, label the PR or issue `needs-owner-review` and explain why.

Never:
- Modify secrets or production credentials.
- Disable tests to pass CI.
- Hide errors by swallowing exceptions without logging.
- Replace a specific fix with a broad rewrite.
- Change deployment/IAM/billing/auth/payment behavior without review.
