# CLI Guide: Omnibus Tool

The `omnibus.py` script is the primary administrative interface for the Codex Caelestis environment. It unifies auditing, database management, and maintenance tasks.

## Usage

```bash
python -m src.scripts.omnibus [COMMAND] [OPTIONS]
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
python -m src.scripts.omnibus audit --name "Alexander Hamilton" --date "1755-01-11" --time "14:00" --city "Charlestown"
```

### `rehydrate`
**WARNING:** This is a destructive operation.
Resets the `users.db` database (removing all user data) and re-seeds it with default `SubscriptionPlan` data.

**Usage:**
```bash
python -m src.scripts.omnibus rehydrate
```
*   Use `--yes` to bypass the confirmation prompt in automated environments.

### `version`
Displays the current version of the Engine and Database schema.

```bash
python -m src.scripts.omnibus version
```
