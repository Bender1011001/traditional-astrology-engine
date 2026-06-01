#!/usr/bin/env python3
"""
run_domain.py — CLI entry point for a single domain astrological correlation pipeline.

Historical Use Only — not financial, investment, medical, or legal advice.

Usage:
    python run_domain.py <domain_name>

Example:
    python run_domain.py sp500
    python run_domain.py earthquakes

Available domains: see domains.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Path setup: allow running as `python run_domain.py` from any directory
# ---------------------------------------------------------------------------

_HERE = Path(__file__).parent.resolve()
_PROJECT_ROOT = _HERE.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Module imports
# ---------------------------------------------------------------------------

from astrology_mapping_v5.domains import DOMAINS
from astrology_mapping_v5.fetch_data import fetch_domain
from astrology_mapping_v5.features import generate_features_for_dates, get_feature_cols
from astrology_mapping_v5.pipeline import run_domain_pipeline, detrend_target

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Directories
# ---------------------------------------------------------------------------

_DATA_DIR = _HERE / "data"
_RESULTS_DIR = _HERE / "results"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Target building logic (per-domain)
# ---------------------------------------------------------------------------

def build_target(domain_name: str, raw_df: pd.DataFrame, freq: str) -> pd.DataFrame | None:
    """
    Build the binary target column for a given domain from its raw data.
    Returns a DataFrame with 'date' + target column, or None on failure.
    """
    raw_df = raw_df.copy()
    raw_df["date"] = pd.to_datetime(raw_df["date"]).dt.normalize()
    raw_df = raw_df.sort_values("date").reset_index(drop=True)

    try:
        if domain_name == "sp500":
            raw_df["return"] = raw_df["close"].pct_change()
            abs_ret = raw_df["return"].abs()
            # Detrend: high vol day = |return| >= 2.5% AND above 3yr rolling median
            rows_per_year = 252
            rolling_med = abs_ret.rolling(3 * rows_per_year, min_periods=126).median()
            # Binary: |return| >= 2.5% AND above rolling median
            raw_df["high_vol_day"] = (
                (abs_ret >= 0.025) & (abs_ret > rolling_med)
            ).astype(int)
            return raw_df[["date", "high_vol_day"]].dropna()

        elif domain_name == "vix":
            raw_df["spike_gt30"] = (raw_df["close"] > 30).astype(int)
            return raw_df[["date", "spike_gt30"]].dropna()

        elif domain_name in ("gold", "bitcoin", "crude_oil"):
            thresholds = {"gold": 0.03, "bitcoin": 0.10, "crude_oil": 0.05}
            threshold = thresholds[domain_name]
            raw_df["weekly_return"] = raw_df["close"].pct_change()
            raw_df["big_move"] = (raw_df["weekly_return"].abs() >= threshold).astype(int)
            return raw_df[["date", "big_move"]].dropna()

        elif domain_name == "treasury_yield":
            raw_df["weekly_change"] = raw_df["close"].diff()
            raw_df["big_move"] = (raw_df["weekly_change"].abs() >= 0.20).astype(int)
            return raw_df[["date", "big_move"]].dropna()

        elif domain_name == "unemployment":
            raw_df["mom_change"] = raw_df["value"].diff()
            raw_df["increase_gt03pp"] = (raw_df["mom_change"] > 0.3).astype(int)
            return raw_df[["date", "increase_gt03pp"]].dropna()

        elif domain_name == "cpi":
            # YoY change requires 12-month shift
            raw_df = raw_df.set_index("date").sort_index()
            raw_df["yoy_change"] = raw_df["value"].pct_change(periods=12) * 100.0
            raw_df["yoy_gt5pct"] = (raw_df["yoy_change"] > 5.0).astype(int)
            return raw_df[["yoy_gt5pct"]].reset_index().dropna()

        elif domain_name == "recession":
            # recession_start: USREC transitions from 0 to 1 next month
            raw_df = raw_df.sort_values("date").reset_index(drop=True)
            raw_df["next_usrec"] = raw_df["value"].shift(-1)
            raw_df["recession_start"] = (
                (raw_df["value"] == 0) & (raw_df["next_usrec"] == 1)
            ).astype(int)
            return raw_df[["date", "recession_start"]].dropna()

        elif domain_name == "fed_funds":
            raw_df["mom_change"] = raw_df["value"].diff()
            raw_df["rate_hike"] = (raw_df["mom_change"] > 0).astype(int)
            return raw_df[["date", "rate_hike"]].dropna()

        elif domain_name == "earthquakes":
            # Daily aggregate: was there an M>=7.0 event?
            raw_df["m7plus"] = (raw_df["mag"] >= 7.0).astype(int)
            daily = raw_df.groupby("date")["m7plus"].max().reset_index()
            daily["m7plus"] = daily["m7plus"].astype(int)
            return daily

        elif domain_name == "geomagnetic_kp":
            raw_df["kp_storm_day"] = (raw_df["kp_max"] >= 5.0).astype(int)
            return raw_df[["date", "kp_storm_day"]].dropna()

        elif domain_name == "sunspots":
            sn = raw_df["sunspot_number"]
            window = 132  # 11-year rolling window in months
            rolling_mean = sn.rolling(window, min_periods=24).mean()
            rolling_std = sn.rolling(window, min_periods=24).std()
            raw_df["high_sunspot"] = (
                (sn > 150) | (sn > rolling_mean + 2 * rolling_std)
            ).astype(int)
            return raw_df[["date", "high_sunspot"]].dropna()

        elif domain_name == "hurricanes":
            raw_df["cat3plus_landfall"] = (raw_df["cat3plus_count"] > 0).astype(int)
            return raw_df[["date", "cat3plus_landfall"]]

        elif domain_name == "traffic_fatalities":
            fat = raw_df["fatalities"]
            rolling_mean = fat.rolling(12, min_periods=6).mean()
            raw_df["above_avg_month"] = (fat > rolling_mean * 1.10).astype(int)
            return raw_df[["date", "above_avg_month"]].dropna()

        elif domain_name == "influenza_ili":
            ili = raw_df["ili_pct"]
            # National baseline approximation: rolling mean
            rolling_mean = ili.rolling(52, min_periods=12).mean()
            rolling_std = ili.rolling(52, min_periods=12).std()
            baseline = rolling_mean + 0.5 * rolling_std
            raw_df["above_baseline"] = (ili > baseline).astype(int)
            return raw_df[["date", "above_baseline"]].dropna()

        elif domain_name == "solar_flares":
            raw_df["x_class_flare"] = (raw_df["x_flare_count"] > 0).astype(int)
            return raw_df[["date", "x_class_flare"]].dropna()

        elif domain_name == "proton_events":
            raw_df["proton_event"] = (raw_df["proton_count"] > 0).astype(int)
            return raw_df[["date", "proton_event"]].dropna()

        else:
            log.error("No target building logic for domain: %s", domain_name)
            return None

    except Exception as exc:
        log.error("Target building failed for %s: %s", domain_name, exc)
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python run_domain.py <domain_name>")
        print("Available domains:", list(DOMAINS.keys()))
        sys.exit(1)

    domain_name = sys.argv[1].strip()
    if domain_name not in DOMAINS:
        print(f"Unknown domain: {domain_name!r}")
        print("Available domains:", list(DOMAINS.keys()))
        sys.exit(1)

    domain_cfg = DOMAINS[domain_name]
    freq = domain_cfg["frequency"]
    start_date, end_date = domain_cfg["date_range"]
    target_col = domain_cfg["targets"][0]["col"]  # Use first target

    log.info("=" * 70)
    log.info("Domain: %s | Target: %s | Freq: %s", domain_name, target_col, freq)
    log.info("=" * 70)

    # ── 1. Fetch raw data ────────────────────────────────────────────────────
    log.info("Step 1: Fetching raw data …")
    raw_df = fetch_domain(domain_name, _DATA_DIR, force_refresh=False)
    if raw_df is None or len(raw_df) == 0:
        log.error("No data available for domain %s — aborting.", domain_name)
        sys.exit(2)
    log.info("  Raw data: %d rows, columns: %s", len(raw_df), list(raw_df.columns))

    # ── 2. Build target ──────────────────────────────────────────────────────
    log.info("Step 2: Building target variable '%s' …", target_col)
    target_df = build_target(domain_name, raw_df, freq)
    if target_df is None or len(target_df) == 0:
        log.error("Target building failed for %s — aborting.", domain_name)
        sys.exit(3)
    target_df = target_df.sort_values("date").reset_index(drop=True)
    n_pos = int(target_df[target_col].sum())
    n_total = len(target_df)
    log.info("  Target: %d positive events / %d total (base rate: %.3f)",
             n_pos, n_total, n_pos / n_total if n_total > 0 else 0)

    if n_pos < 20:
        log.error("Too few positive target events (%d) for domain %s — aborting.", n_pos, domain_name)
        sys.exit(4)

    # ── 3. Generate astrological features ───────────────────────────────────
    log.info("Step 3: Generating astrological features …")
    date_range_dates = pd.DatetimeIndex(target_df["date"].unique())
    feature_cache = _DATA_DIR / f"{domain_name}_features.parquet"

    feature_df = generate_features_for_dates(date_range_dates, cache_path=feature_cache)
    log.info("  Feature matrix: %d rows × %d columns", len(feature_df), len(feature_df.columns))

    # ── 4. Determine min_train_years ─────────────────────────────────────────
    n_years = int((target_df["date"].max() - target_df["date"].min()).days / 365.25)
    min_train_years = max(5, min(20, n_years // 3))
    log.info("  Years of data: %d | min_train_years: %d", n_years, min_train_years)

    # ── 5. Run pipeline ──────────────────────────────────────────────────────
    log.info("Step 4: Running 5-step statistical pipeline …")
    result = run_domain_pipeline(
        domain_name=domain_name,
        df=target_df,
        feature_df=feature_df,
        target_col=target_col,
        results_dir=_RESULTS_DIR,
        min_train_years=min_train_years,
        freq=freq,
    )

    # ── 6. Print summary ─────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print(f"DOMAIN PIPELINE RESULT: {domain_name}")
    print("=" * 70)
    print(f"  Target:               {target_col}")
    print(f"  N observations:       {result.get('n_obs', 'N/A')}")
    print(f"  Calendar AUC:         {result.get('calendar_auc', 'N/A'):.4f}" if isinstance(result.get('calendar_auc'), float) else f"  Calendar AUC:         N/A")
    print(f"  Astro AUC (full):     {result.get('astro_auc_full', 'N/A'):.4f}" if isinstance(result.get('astro_auc_full'), float) else f"  Astro AUC (full):     N/A")
    print(f"  Astro AUC (fast):     {result.get('astro_auc_fast', 'N/A'):.4f}" if isinstance(result.get('astro_auc_fast'), float) else f"  Astro AUC (fast):     N/A")
    print(f"  Gate passes (Step2):  {result.get('gate_passes', 'N/A')}")
    print(f"  Gate passes (Step3):  {result.get('fast_gate_passes', 'N/A')}")
    verdict = result.get('verdict', 'UNKNOWN')
    print(f"  VERDICT:              {verdict}")
    report_path = _RESULTS_DIR / f"{domain_name}_report.md"
    print(f"  Report:               {report_path}")
    print("=" * 70)
    print()
    print("Historical Use Only — not financial, investment, medical, or legal advice.")


if __name__ == "__main__":
    main()
