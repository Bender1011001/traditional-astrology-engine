# CLI Guide: Omnibus Tool

This project intentionally keeps `src/scripts/` minimal. The supported CLI entrypoint is the premium report generator.

## Usage

```bash
python src/scripts/generate_premium_report.py --help
```

## Commands

### `audit`
Runs a forensic audit on a specific nativity.

**Arguments:**
*   `--name`: (Required) Name of the subject.
*   `--date`: (Required) Birth date (YYYY-MM-DD).
*   `--time`: (Required) Birth time (HH:MM).
*   `--city`: (Required) Birth city.
*   `--state`: (Optional) Birth state/region.

**Example:**
```bash
python src/scripts/generate_premium_report.py --name "Alexander Hamilton" --date "1755-01-11" --time "14:00" --city "Charlestown" --state "MA"
```

### `rehydrate`
**WARNING:** This is a destructive operation.
Resets the `users.db` database (removing all user data) and re-seeds it with default `SubscriptionPlan` data.

**Usage:**
```bash
Administrative maintenance commands were moved into service modules (not scripts) to avoid a large scripts folder.
```
*   Use `--yes` to bypass the confirmation prompt in automated environments.

### `version`
Displays the current version of the Engine and Database schema.

```bash
See `src/services/db_seed.py` and `src/services/db_patch.py` for DB maintenance helpers.
```
