---
project: scripts
status: working
updated: 2026-03-14
---

# Scripts Directory

## Resume
- **Pick up at**: [Review and update]
- **Last session**: [Auto-migrated to CONTEXT v2]
- **Blocked on**: Nothing

## Status
- **Working**: Outreach runner, data extraction, delineation enhancement, migration scripts.
- **New**: `outreach_run.py` (v1.0) with throttling and cooldown.

## Tech Stack
- Python 3.10+
- SQLAlchemy (Core/Models)
- `smtplib` (Email)

## Key Files
- `outreach_run.py` — Automated outreach runner (email-only) with throttling.
- `extract_all_traditional_data.py` — High-precision extraction of traditional source material into JSON.
- `enhance_delineations.py` — LLM-driven quality enhancement for raw delineations.
- `migrate_json_to_db.py` — Syncs JSON delineations to the production/local DB.
- `seed_fresh_db.py` — Seeds a new database with default plans and system data.

## Operational Guidance (Outreach)
- **Dry-run**: Always run without `--send` first to verify targets.
- **Throttling**: Defaulted to 40 emails/hour to maintain IP reputation.
- **Compliance**: Requires `OUTREACH_POSTAL_ADDRESS` environment variable for the mandatory footer.

## Anti-Patterns
- Do not bypass the `--min-gap-sec` sleep (prevents SMTP rejection).
- Do not run `--send` without verifying the `--limit` first.
