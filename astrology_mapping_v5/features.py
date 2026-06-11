"""
features.py — Astrological feature generation wrapper for astro-mapping-v5.

Historical Use Only — not financial, investment, medical, or legal advice.

Thin wrapper around financial_astrology_analysis_v4/generate_features.py.
Exposes a single public function: generate_features_for_dates().
Results are cached as Parquet files to avoid re-computation.
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
# Inject v4 directory into sys.path so we can import generate_features
# ---------------------------------------------------------------------------

V4_DIR = Path(__file__).parent.parent / "financial_astrology_analysis_v4"
if not V4_DIR.exists():
    raise FileNotFoundError(
        f"v4 directory not found: {V4_DIR}. "
        "Ensure financial_astrology_analysis_v4/ exists in the project root."
    )

if str(V4_DIR) not in sys.path:
    sys.path.insert(0, str(V4_DIR))

import generate_features as gf  # noqa: E402  (after sys.path manipulation)

# ---------------------------------------------------------------------------
# Fast feature identification
# Fast features are those with synodic periods < ~5 years, meaning their
# signal can cycle multiple times within our training windows.
# ---------------------------------------------------------------------------

_FAST_PREFIXES = (
    "sun_moon_",
    "sun_mercury_",
    "sun_venus_",
    "sun_mars_",
    "mercury_venus_",
    "mercury_mars_",
    "venus_mars_",
    "moon_",
    "near_new_moon",
    "near_full_moon",
    "near_quarter_moon",
    "eclipse_",
    "days_since_solar_eclipse",
    "days_since_lunar_eclipse",
    "mars_near_station",
    "days_to_mars_station",
)


def get_fast_feature_cols(feature_cols: list[str]) -> list[str]:
    """
    Filter feature_cols to only those with synodic periods < ~5 years.
    These are features involving the Sun, Moon, Mercury, Venus, Mars,
    plus eclipse and station markers.
    """
    fast = [
        col for col in feature_cols
        if any(col.startswith(prefix) or col == prefix for prefix in _FAST_PREFIXES)
    ]
    return fast


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def generate_features_for_dates(
    dates: pd.DatetimeIndex,
    cache_path: Path | None = None,
) -> pd.DataFrame:
    """
    Compute all astrological features for the given dates.

    Parameters
    ----------
    dates : pd.DatetimeIndex
        Dates to compute features for.
    cache_path : Path | None
        If provided and the file exists (non-empty), load from cache.
        If provided and file does not exist, compute and save to cache.

    Returns
    -------
    pd.DataFrame
        DataFrame with 'date' column + all astrological feature columns.
        Dates with computation errors will have NaN for all feature columns.
    """
    # ── Cache check ──────────────────────────────────────────────────────────
    if cache_path is not None and cache_path.exists() and cache_path.stat().st_size > 0:
        log.info("Feature cache hit: %s", cache_path)
        df = pd.read_parquet(cache_path)
        df["date"] = pd.to_datetime(df["date"])
        # Only return rows for requested dates
        requested = set(pd.to_datetime(dates).normalize())
        df = df[pd.to_datetime(df["date"]).dt.normalize().isin(requested)]
        return df.reset_index(drop=True)

    t0 = time.time()
    dates = pd.DatetimeIndex(sorted(set(pd.to_datetime(dates).normalize())))
    n = len(dates)
    log.info("Generating astrological features for %d dates …", n)

    # ── 1. Convert dates to Julian Days ─────────────────────────────────────
    trading_jds: list[float] = [gf.date_to_jd(d) for d in dates]

    # ── 2. Pre-compute planet positions (+ buffer day) ───────────────────────
    log.info("Pre-computing planet positions …")
    all_jds = sorted(set(trading_jds + [trading_jds[-1] + 1.0]))
    positions: dict[float, dict] = {}
    for i, jd in enumerate(all_jds):
        if i % 3000 == 0:
            log.info("  positions %d / %d (%.0f%%)", i, len(all_jds), 100.0 * i / len(all_jds))
        positions[jd] = gf._fetch_positions(jd)

    # ── 3. Speed statistics (over the full date range) ───────────────────────
    log.info("Computing speed statistics …")
    speed_stats = gf.compute_speed_stats({jd: positions[jd] for jd in trading_jds})

    # ── 4. Build caches ──────────────────────────────────────────────────────
    jd_min = trading_jds[0] - 400.0
    jd_max = trading_jds[-1] + 30.0

    log.info("Building eclipse cache …")
    solar_ecl, lunar_ecl = gf.build_eclipse_cache(jd_min, jd_max)
    log.info("  %d solar eclipses, %d lunar eclipses", len(solar_ecl), len(lunar_ecl))

    log.info("Building Great Conjunction cache …")
    great_conj = gf.build_great_conjunction_cache(jd_min, jd_max)
    log.info("  %d Great Conjunctions", len(great_conj))

    log.info("Building Mars station cache …")
    mars_st = gf.build_mars_station_cache(jd_min, jd_max)
    log.info("  %d Mars stations", len(mars_st))

    # ── 5. Compute features for each date ────────────────────────────────────
    log.info("Computing features for %d dates …", n)
    rows: list[dict] = []
    for i, (jd, d) in enumerate(zip(trading_jds, dates)):
        if i % 2000 == 0:
            log.info("  features %d / %d (%.0f%%)", i, n, 100.0 * i / n)

        jd_next = jd + 1.0
        if jd_next not in positions:
            positions[jd_next] = gf._fetch_positions(jd_next)

        try:
            feat = gf.compute_all_features(
                jd=jd,
                pos_now=positions[jd],
                pos_next=positions[jd_next],
                solar_eclipses=solar_ecl,
                lunar_eclipses=lunar_ecl,
                great_conjunctions=great_conj,
                mars_stations=mars_st,
                speed_stats=speed_stats,
            )
        except Exception as exc:
            log.warning("Feature computation failed for %s: %s", d, exc)
            feat = {}

        feat["date"] = pd.Timestamp(d)
        rows.append(feat)

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    df["date"] = pd.to_datetime(df["date"])

    log.info(
        "Feature generation complete: %d rows × %d columns in %.1f s",
        len(df), len(df.columns), time.time() - t0
    )

    # ── 6. Cache result ──────────────────────────────────────────────────────
    if cache_path is not None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(cache_path, index=False)
        log.info("Features cached to %s", cache_path)

    return df


# ---------------------------------------------------------------------------
# Convenience: get all feature column names from a feature DataFrame
# ---------------------------------------------------------------------------

_NON_FEATURE_COLS = frozenset({
    "date", "close", "fwd_1d_return", "fwd_5d_return", "fwd_20d_return",
    "high_vol_day", "crash_fwd_5d", "crash_fwd_20d",
})


def get_feature_cols(df: pd.DataFrame) -> list[str]:
    """Return the list of astrological feature column names from a feature DataFrame."""
    return [c for c in df.columns if c not in _NON_FEATURE_COLS]


__all__ = [
    "generate_features_for_dates",
    "get_fast_feature_cols",
    "get_feature_cols",
    "V4_DIR",
]
