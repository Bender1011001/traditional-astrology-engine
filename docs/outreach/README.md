# Outreach Automation

This repo includes a minimal outbound automation runner for **email-only** outreach.

Safety/Compliance:
- Keep messages about software/workflows only. No medical or financial advice.
- Provide a valid postal address in the footer.
- Do not blast: defaults are throttled and **dry-run** unless you opt in.

## 1) Build/Import Targets

Targets come from `docs/research/Gig Economy Astrologer Contact Research.txt`.

```powershell
python scripts/extract_outreach_targets.py
python scripts/import_outreach_targets.py --reset
```

This writes `docs/outreach/outreach_targets.csv` and imports it into the DB (`users.db` by default).

## 2) Dry Run (Recommended)

```powershell
python scripts/outreach_run.py --limit 10
```

This creates `outreach_attempts` DB rows as `skipped` with `dry_run` marker.

## 3) Send (Explicit)

Requires:
- `SENDER_EMAIL`, `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS` configured
- `--postal-address` provided (or `OUTREACH_POSTAL_ADDRESS` env var set)

```powershell
$env:OUTREACH_POSTAL_ADDRESS = "Your Company, 123 Main St, City, ST ZIP"
python scripts/outreach_run.py --send --limit 5 --min-gap-sec 35 --segment teacher
```

## 4) Monitoring

Owner UI:
- `owner.html` has an Outreach tab for targets
- KPIs + Leads tabs are also available

