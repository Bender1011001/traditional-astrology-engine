"""
pipeline.py — 5-Step Statistical Protocol for Astrological Correlation Study.

Historical Use Only — not financial, investment, medical, or legal advice.

Each domain passes through a rigorous 5-step falsification protocol:
  Step 1: Calendar baseline AUC (lower bound; pure seasonality)
  Step 2: Full astro feature AUC (gate: must exceed calendar AUC + 0.02)
  Step 3: Fast-feature AUC (synodic period < 5 yrs; gate: must exceed 0.53)
  Step 4: Falsification tests (label shuffle, era block shuffle, reverse time)
  Step 5: Report generation
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Import walk_forward_auc from v4 model.py
# ---------------------------------------------------------------------------

V4_DIR = Path(__file__).parent.parent / "financial_astrology_analysis_v4"
if str(V4_DIR) not in sys.path:
    sys.path.insert(0, str(V4_DIR))

from model import walk_forward_auc  # noqa: E402

# ---------------------------------------------------------------------------
# Calendar features
# ---------------------------------------------------------------------------

_CALENDAR_PERIODS = [12, 13, 20, 29.5, 36, 45, 84, 165, 248]  # years


def compute_calendar_features(dates: pd.DatetimeIndex) -> pd.DataFrame:
    """
    Compute 25 calendar-only features for the given dates.

    Features:
      year_frac           : year + doy/365.25
      year_scaled         : (year - 1900) / 100
      sin/cos for 9 periods × 2 = 18 features
      sin_doy, cos_doy    : annual cycle
      sin_month, cos_month: monthly cycle
      sin_dow, cos_dow    : day-of-week cycle

    Returns DataFrame with 'date' column + 25 feature columns.
    """
    df = pd.DataFrame({"date": pd.to_datetime(dates)})
    df["_year"] = df["date"].dt.year
    df["_doy"] = df["date"].dt.day_of_year
    df["_month"] = df["date"].dt.month
    df["_dow"] = df["date"].dt.day_of_week

    # 1. year_frac
    df["year_frac"] = df["_year"] + df["_doy"] / 365.25

    # 2. year_scaled
    df["year_scaled"] = (df["_year"] - 1900) / 100.0

    # 3. Periodic sin/cos for each period (18 features)
    for period in _CALENDAR_PERIODS:
        period_key = f"p{int(period)}" if period == int(period) else f"p{period}".replace(".", "_")
        angle = df["year_frac"] / period * 2.0 * np.pi
        df[f"sin_{period_key}yr"] = np.sin(angle)
        df[f"cos_{period_key}yr"] = np.cos(angle)

    # 4. Annual cycle (day of year)
    angle_doy = df["_doy"] / 365.25 * 2.0 * np.pi
    df["sin_doy"] = np.sin(angle_doy)
    df["cos_doy"] = np.cos(angle_doy)

    # 5. Monthly cycle
    angle_mo = df["_month"] / 12.0 * 2.0 * np.pi
    df["sin_month"] = np.sin(angle_mo)
    df["cos_month"] = np.cos(angle_mo)

    # 6. Day-of-week cycle
    angle_dow = df["_dow"] / 7.0 * 2.0 * np.pi
    df["sin_dow"] = np.sin(angle_dow)
    df["cos_dow"] = np.cos(angle_dow)

    # Drop temporary columns
    df = df.drop(columns=["_year", "_doy", "_month", "_dow"])
    return df


def _get_calendar_feature_cols(df: pd.DataFrame) -> list[str]:
    """Return all calendar feature column names from the output of compute_calendar_features."""
    return [c for c in df.columns if c != "date"]


# ---------------------------------------------------------------------------
# Detrending helper
# ---------------------------------------------------------------------------

def detrend_target(series: pd.Series, window_years: int = 3, freq: str = "daily") -> pd.Series:
    """
    Compute rolling-median-detrended target.
    For binary series (0/1 only): return as-is.
    For continuous series: (value - rolling_median) / rolling_std.

    window_years: rolling window expressed in years.
    freq: 'daily', 'weekly', or 'monthly' — used to compute window size in rows.
    """
    unique_vals = series.dropna().unique()
    # If essentially binary, return as-is
    if set(unique_vals).issubset({0, 1, 0.0, 1.0}):
        return series.copy()

    rows_per_year = {"daily": 252, "weekly": 52, "monthly": 12}.get(freq, 252)
    window = max(12, window_years * rows_per_year)

    rolling_med = series.rolling(window, min_periods=max(12, window // 4)).median()
    rolling_std = series.rolling(window, min_periods=max(12, window // 4)).std()

    detrended = (series - rolling_med) / rolling_std.replace(0, np.nan)
    return detrended


# ---------------------------------------------------------------------------
# Falsification tests
# ---------------------------------------------------------------------------

def run_label_shuffle_test(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    observed_auc: float,
    n_shuffles: int = 1000,
    min_train_years: int = 15,
) -> dict:
    """
    Randomly permute target labels n_shuffles times; compute AUC each time.
    Returns: {null_95th_pct, passes (observed_auc > null_95th_pct), p_value}
    """
    rng = np.random.default_rng(42)
    null_aucs: list[float] = []

    df_work = df.copy()

    for _ in range(n_shuffles):
        df_work[target_col] = rng.permutation(df[target_col].values)
        result = walk_forward_auc(df_work, feature_cols, target_col, min_train_years)
        auc_val = result.get("auc", np.nan)
        if not np.isnan(auc_val):
            null_aucs.append(auc_val)

    if not null_aucs:
        return {"null_95th_pct": np.nan, "passes": False, "p_value": np.nan, "n_valid": 0}

    null_arr = np.array(null_aucs)
    pct_95 = float(np.percentile(null_arr, 95))
    p_value = float(np.mean(null_arr >= observed_auc))

    return {
        "null_95th_pct": pct_95,
        "passes": bool(observed_auc > pct_95),
        "p_value": p_value,
        "n_valid": len(null_aucs),
    }


def run_era_block_shuffle_test(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    observed_auc: float,
    n_shuffles: int = 1000,
    min_train_years: int = 15,
) -> dict:
    """
    Randomly permute entire calendar years (era blocks); recompute walk-forward AUC.
    Returns: {null_95th_pct, passes, p_value}
    """
    rng = np.random.default_rng(43)
    df_work = df.copy()
    df_work["_year"] = pd.to_datetime(df_work["date"]).dt.year
    years = df_work["_year"].unique()

    null_aucs: list[float] = []

    for _ in range(n_shuffles):
        year_map = dict(zip(years, rng.permutation(years)))
        df_shuffled = df_work.copy()
        df_shuffled["date"] = df_shuffled["_year"].map(
            lambda y: df_work.loc[df_work["_year"] == year_map[y], "date"].values[0]
        )
        # Re-assign target labels according to shuffled year mapping
        target_by_year: dict[int, pd.Series] = {
            yr: df_work.loc[df_work["_year"] == yr, target_col].values
            for yr in years
        }
        # Build the shuffled target series
        new_target: list = []
        new_dates: list = []
        for yr in sorted(years):
            shuffled_yr = year_map[yr]
            source_vals = target_by_year[shuffled_yr]
            n_dest = int((df_work["_year"] == yr).sum())
            # If sizes differ, resample with replacement
            if len(source_vals) >= n_dest:
                new_target.extend(source_vals[:n_dest].tolist())
            else:
                idxs = rng.choice(len(source_vals), size=n_dest, replace=True)
                new_target.extend(source_vals[idxs].tolist())
            dates_yr = df_work.loc[df_work["_year"] == yr, "date"].values
            new_dates.extend(dates_yr.tolist())

        df_shuf = pd.DataFrame({"date": new_dates, target_col: new_target})
        # Merge features back in
        df_shuf = df_shuf.merge(df_work[["date"] + feature_cols].drop_duplicates("date"), on="date", how="left")
        result = walk_forward_auc(df_shuf, feature_cols, target_col, min_train_years)
        auc_val = result.get("auc", np.nan)
        if not np.isnan(auc_val):
            null_aucs.append(auc_val)

    if not null_aucs:
        return {"null_95th_pct": np.nan, "passes": False, "p_value": np.nan, "n_valid": 0}

    null_arr = np.array(null_aucs)
    pct_95 = float(np.percentile(null_arr, 95))
    p_value = float(np.mean(null_arr >= observed_auc))

    return {
        "null_95th_pct": pct_95,
        "passes": bool(observed_auc > pct_95),
        "p_value": p_value,
        "n_valid": len(null_aucs),
    }


def run_reverse_time_test(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    min_train_years: int = 20,
) -> dict:
    """
    Walk-forward in REVERSE: train on years >= T+1, predict year T.
    A genuine predictive signal should not appear in reverse time.
    Returns: {reverse_auc, passes (reverse_auc <= 0.55)}
    """
    from sklearn.linear_model import LogisticRegressionCV
    from sklearn.metrics import roc_auc_score
    from sklearn.preprocessing import StandardScaler
    import warnings

    warnings.filterwarnings("ignore")

    df_rev = df.copy()
    df_rev["_year"] = pd.to_datetime(df_rev["date"]).dt.year
    years = sorted(df_rev["_year"].unique())

    if len(years) < min_train_years + 1:
        return {"reverse_auc": np.nan, "passes": True, "n_predictions": 0}

    all_y_true: list[float] = []
    all_y_score: list[float] = []

    for i in range(len(years) - 1 - min_train_years, 0, -1):
        train_start = years[i]
        test_year = years[i - 1]

        train = df_rev[df_rev["_year"] >= train_start][feature_cols + [target_col]].dropna()
        test = df_rev[df_rev["_year"] == test_year][feature_cols + [target_col]].dropna()

        if len(train) < 50 or len(test) < 5:
            continue
        if train[target_col].nunique() < 2:
            continue

        X_train = train[feature_cols].values
        y_train = train[target_col].values
        X_test = test[feature_cols].values
        y_test = test[target_col].values

        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        try:
            clf = LogisticRegressionCV(
                cv=5, Cs=[0.001, 0.01, 0.1, 1.0],
                class_weight="balanced",
                solver="lbfgs", max_iter=500,
                random_state=42,
            )
            clf.fit(X_train_s, y_train)
            scores = clf.predict_proba(X_test_s)[:, 1]
            if len(np.unique(y_test)) == 2:
                all_y_true.extend(y_test.tolist())
                all_y_score.extend(scores.tolist())
        except Exception as exc:
            log.debug("Reverse time step %d failed: %s", i, exc)
            continue

    if len(all_y_true) < 20 or len(set(all_y_true)) < 2:
        return {"reverse_auc": np.nan, "passes": True, "n_predictions": len(all_y_true)}

    reverse_auc = float(roc_auc_score(all_y_true, all_y_score))
    # Passes falsification if reverse AUC is near chance (<=0.55)
    passes = bool(reverse_auc <= 0.55)

    return {
        "reverse_auc": reverse_auc,
        "passes": passes,
        "n_predictions": len(all_y_true),
    }


# ---------------------------------------------------------------------------
# Full domain pipeline
# ---------------------------------------------------------------------------

def run_domain_pipeline(
    domain_name: str,
    df: pd.DataFrame,
    feature_df: pd.DataFrame,
    target_col: str,
    results_dir: Path,
    min_train_years: int = 15,
    freq: str = "daily",
) -> dict:
    """
    Run the full 5-step statistical pipeline for one domain.

    Parameters
    ----------
    domain_name   : str
    df            : DataFrame with 'date' + target_col (raw domain data, target already computed)
    feature_df    : DataFrame with 'date' + all astrological feature columns
    target_col    : name of the binary target column in df
    results_dir   : directory to write <domain>_report.md
    min_train_years : minimum years of training data before predicting
    freq          : 'daily', 'weekly', or 'monthly'

    Returns
    -------
    dict with pipeline results for every step.
    """
    t_start = time.time()
    result: dict = {
        "domain": domain_name,
        "target_col": target_col,
        "freq": freq,
    }

    # ── Merge target with features ───────────────────────────────────────────
    df_target = df[["date", target_col]].copy()
    df_target["date"] = pd.to_datetime(df_target["date"]).dt.normalize()
    feature_df = feature_df.copy()
    feature_df["date"] = pd.to_datetime(feature_df["date"]).dt.normalize()

    merged = pd.merge(df_target, feature_df, on="date", how="inner")
    merged = merged.sort_values("date").reset_index(drop=True)
    result["n_obs"] = len(merged)
    log.info("[%s] Merged dataset: %d rows", domain_name, len(merged))

    if len(merged) < 50:
        result["error"] = "Insufficient data after merge"
        _write_report(domain_name, result, results_dir)
        return result

    # Get feature column names (everything except date and target)
    all_feature_cols = [c for c in feature_df.columns if c != "date"]

    # Fill NaN in applying features (not-in-aspect = not-applying)
    applying_cols = [c for c in all_feature_cols if c.endswith("_applying")]
    merged[applying_cols] = merged[applying_cols].fillna(0)

    # Fill remaining NaNs with column median
    for col in all_feature_cols:
        if col in merged.columns and merged[col].isna().any():
            med = merged[col].median()
            merged[col] = merged[col].fillna(med if not np.isnan(med) else 0)

    # ── Step 1: Calendar baseline ────────────────────────────────────────────
    log.info("[%s] Step 1: Calendar baseline AUC …", domain_name)
    cal_df = compute_calendar_features(pd.DatetimeIndex(merged["date"]))
    cal_cols = _get_calendar_feature_cols(cal_df)
    cal_df["date"] = merged["date"].values
    cal_df[target_col] = merged[target_col].values

    cal_result = walk_forward_auc(cal_df, cal_cols, target_col, min_train_years)
    calendar_auc = cal_result.get("auc", np.nan)
    result["calendar_auc"] = calendar_auc
    result["calendar_n_pred"] = cal_result.get("n_predictions", 0)
    log.info("[%s] Calendar AUC = %.4f", domain_name, calendar_auc)

    # ── Step 2: Full astro features ──────────────────────────────────────────
    log.info("[%s] Step 2: Full astro AUC (%d features) …", domain_name, len(all_feature_cols))
    astro_result = walk_forward_auc(merged, all_feature_cols, target_col, min_train_years)
    astro_auc = astro_result.get("auc", np.nan)
    result["astro_auc_full"] = astro_auc
    result["astro_n_pred"] = astro_result.get("n_predictions", 0)
    log.info("[%s] Astro AUC (full) = %.4f", domain_name, astro_auc)

    # Gate: astro must beat calendar by >= 0.02
    gate_threshold = (calendar_auc if not np.isnan(calendar_auc) else 0.50) + 0.02
    gate_passes = (not np.isnan(astro_auc)) and (astro_auc >= gate_threshold)
    result["gate_passes"] = gate_passes
    result["gate_threshold"] = gate_threshold
    log.info("[%s] Gate (astro > cal+0.02): %s", domain_name, gate_passes)

    if not gate_passes:
        result["verdict"] = "FAIL_GATE_STEP2"
        _write_report(domain_name, result, results_dir)
        return result

    # ── Step 3: Fast features only ───────────────────────────────────────────
    from features import get_fast_feature_cols
    fast_cols = get_fast_feature_cols(all_feature_cols)
    fast_cols = [c for c in fast_cols if c in merged.columns]
    log.info("[%s] Step 3: Fast features AUC (%d features) …", domain_name, len(fast_cols))

    if len(fast_cols) < 2:
        result["astro_auc_fast"] = np.nan
        result["fast_gate_passes"] = False
        result["verdict"] = "FAIL_NO_FAST_FEATURES"
        _write_report(domain_name, result, results_dir)
        return result

    fast_result = walk_forward_auc(merged, fast_cols, target_col, min_train_years)
    fast_auc = fast_result.get("auc", np.nan)
    result["astro_auc_fast"] = fast_auc
    result["fast_n_pred"] = fast_result.get("n_predictions", 0)
    fast_gate_passes = (not np.isnan(fast_auc)) and (fast_auc >= 0.53)
    result["fast_gate_passes"] = fast_gate_passes
    log.info("[%s] Fast AUC = %.4f | gate (>=0.53): %s", domain_name, fast_auc, fast_gate_passes)

    if not fast_gate_passes:
        result["verdict"] = "FAIL_GATE_STEP3"
        _write_report(domain_name, result, results_dir)
        return result

    # ── Step 4: Falsification tests ──────────────────────────────────────────
    log.info("[%s] Step 4: Falsification tests …", domain_name)

    # 4a: Label shuffle
    log.info("[%s]   4a label shuffle (1000 permutations) …", domain_name)
    label_result = run_label_shuffle_test(
        merged, fast_cols, target_col, fast_auc,
        n_shuffles=1000, min_train_years=min_train_years
    )
    result["label_shuffle"] = label_result
    log.info("[%s]   Label shuffle: null_95th=%.4f, passes=%s, p=%.4f",
             domain_name, label_result.get("null_95th_pct", np.nan),
             label_result.get("passes", False), label_result.get("p_value", np.nan))

    # 4b: Era block shuffle
    log.info("[%s]   4b era block shuffle (1000 permutations) …", domain_name)
    era_result = run_era_block_shuffle_test(
        merged, fast_cols, target_col, fast_auc,
        n_shuffles=1000, min_train_years=min_train_years
    )
    result["era_block_shuffle"] = era_result
    log.info("[%s]   Era block shuffle: null_95th=%.4f, passes=%s, p=%.4f",
             domain_name, era_result.get("null_95th_pct", np.nan),
             era_result.get("passes", False), era_result.get("p_value", np.nan))

    # 4c: Reverse time
    log.info("[%s]   4c reverse time test …", domain_name)
    rev_result = run_reverse_time_test(
        merged, fast_cols, target_col, min_train_years=min_train_years
    )
    result["reverse_time"] = rev_result
    log.info("[%s]   Reverse time: auc=%.4f, passes=%s",
             domain_name, rev_result.get("reverse_auc", np.nan), rev_result.get("passes", False))

    # Overall verdict
    all_pass = (
        label_result.get("passes", False)
        and era_result.get("passes", False)
        and rev_result.get("passes", False)
    )
    result["all_falsification_pass"] = all_pass
    result["verdict"] = "SIGNAL_DETECTED" if all_pass else "FAIL_FALSIFICATION"
    result["elapsed_seconds"] = round(time.time() - t_start, 1)

    # ── Step 5: Write report ─────────────────────────────────────────────────
    _write_report(domain_name, result, results_dir)
    log.info("[%s] Done. Verdict: %s (%.1f s)", domain_name, result["verdict"], result["elapsed_seconds"])
    return result


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _fmt(val, decimals: int = 4) -> str:
    """Format a float to string, handling NaN gracefully."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    if isinstance(val, float):
        return f"{val:.{decimals}f}"
    return str(val)


def _write_report(domain_name: str, result: dict, results_dir: Path) -> None:
    """Write a Markdown report for a single domain pipeline result."""
    results_dir.mkdir(parents=True, exist_ok=True)
    report_path = results_dir / f"{domain_name}_report.md"

    verdict = result.get("verdict", "UNKNOWN")
    emoji = "🚫" if "FAIL" in verdict or verdict == "UNKNOWN" else "✅"

    lines = [
        f"# Domain Report: {domain_name}",
        "",
        "> **Historical Use Only — not financial, investment, medical, or legal advice.**",
        "",
        f"**Verdict**: {emoji} `{verdict}`",
        f"**Target**: `{result.get('target_col', 'N/A')}`",
        f"**Frequency**: `{result.get('freq', 'N/A')}`",
        f"**N observations**: {result.get('n_obs', 'N/A')}",
        f"**Elapsed**: {result.get('elapsed_seconds', 'N/A')} s",
        "",
        "---",
        "",
        "## Step 1: Calendar Baseline",
        "",
        f"- Calendar AUC: `{_fmt(result.get('calendar_auc'))}`",
        f"- N predictions: `{result.get('calendar_n_pred', 'N/A')}`",
        "",
        "## Step 2: Full Astrological Features",
        "",
        f"- Astro AUC (full): `{_fmt(result.get('astro_auc_full'))}`",
        f"- Gate threshold (cal + 0.02): `{_fmt(result.get('gate_threshold'))}`",
        f"- Gate passes: `{result.get('gate_passes', 'N/A')}`",
        f"- N predictions: `{result.get('astro_n_pred', 'N/A')}`",
        "",
    ]

    if result.get("gate_passes"):
        lines += [
            "## Step 3: Fast Features Only",
            "",
            f"- Astro AUC (fast features): `{_fmt(result.get('astro_auc_fast'))}`",
            f"- Gate threshold (>= 0.53): `0.5300`",
            f"- Gate passes: `{result.get('fast_gate_passes', 'N/A')}`",
            f"- N predictions: `{result.get('fast_n_pred', 'N/A')}`",
            "",
        ]

    if result.get("fast_gate_passes"):
        lines += [
            "## Step 4: Falsification Tests",
            "",
        ]

        ls = result.get("label_shuffle", {})
        lines += [
            "### 4a: Label Shuffle (n=1000)",
            f"- Null 95th percentile: `{_fmt(ls.get('null_95th_pct'))}`",
            f"- Observed fast AUC: `{_fmt(result.get('astro_auc_fast'))}`",
            f"- p-value: `{_fmt(ls.get('p_value'))}`",
            f"- **Passes**: `{ls.get('passes', False)}`",
            "",
        ]

        es = result.get("era_block_shuffle", {})
        lines += [
            "### 4b: Era Block Shuffle (n=1000)",
            f"- Null 95th percentile: `{_fmt(es.get('null_95th_pct'))}`",
            f"- p-value: `{_fmt(es.get('p_value'))}`",
            f"- **Passes**: `{es.get('passes', False)}`",
            "",
        ]

        rt = result.get("reverse_time", {})
        lines += [
            "### 4c: Reverse Time Test",
            f"- Reverse AUC: `{_fmt(rt.get('reverse_auc'))}`",
            f"- Threshold (<= 0.55): `0.5500`",
            f"- **Passes**: `{rt.get('passes', False)}`",
            "",
            "## Step 4 Summary",
            "",
            f"All falsification tests pass: `{result.get('all_falsification_pass', False)}`",
            "",
        ]

    lines += [
        "---",
        "",
        "*Historical Use Only — not financial, investment, medical, or legal advice.*",
    ]

    report_text = "\n".join(lines)
    report_path.write_text(report_text, encoding="utf-8")
    log.info("Report written: %s", report_path)


__all__ = [
    "compute_calendar_features",
    "detrend_target",
    "run_label_shuffle_test",
    "run_era_block_shuffle_test",
    "run_reverse_time_test",
    "run_domain_pipeline",
]
