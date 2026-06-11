"""
domains.py — Domain Registry for astro-mapping-v5 Astrological Correlation Study.

Historical Use Only — not financial, investment, medical, or legal advice.

Defines all 20 study domains: their data sources, date ranges, frequencies,
and target-variable specifications.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# DOMAINS: dict mapping domain_name -> config dict
#
# Keys per config:
#   name         : str           — human-readable name
#   fetch_fn     : str           — function name in fetch_data.py to call
#   date_range   : (str, str)    — (start_date ISO, end_date ISO)
#   frequency    : str           — 'daily', 'weekly', or 'monthly'
#   targets      : list[dict]    — target-column specifications
#   description  : str           — what this domain measures
# ---------------------------------------------------------------------------

DOMAINS: dict[str, dict] = {

    # ── Financial / Market ─────────────────────────────────────────────────────

    "sp500": {
        "name": "S&P 500 Index",
        "fetch_fn": "fetch_sp500",
        "date_range": ("1928-01-01", "2024-12-31"),
        "frequency": "daily",
        "targets": [
            {
                "col": "high_vol_day",
                "description": (
                    "Binary: |daily return| >= 2.5%, detrended against "
                    "3-year rolling median absolute return"
                ),
            }
        ],
        "description": (
            "S&P 500 daily closing prices (1928–2024). "
            "Tests whether astrological features predict extreme volatility days."
        ),
    },

    "vix": {
        "name": "VIX Volatility Index",
        "fetch_fn": "fetch_vix",
        "date_range": ("1990-01-01", "2024-12-31"),
        "frequency": "daily",
        "targets": [
            {
                "col": "spike_gt30",
                "description": "Binary: VIX closing level > 30",
            }
        ],
        "description": (
            "CBOE Volatility Index daily (1990–2024). "
            "Tests whether astrological features predict fear/panic spikes."
        ),
    },

    "gold": {
        "name": "Gold (GC=F futures)",
        "fetch_fn": "fetch_gold",
        "date_range": ("1968-01-01", "2024-12-31"),
        "frequency": "weekly",
        "targets": [
            {
                "col": "big_move",
                "description": "Binary: |weekly return| >= 3%",
            }
        ],
        "description": (
            "Gold futures (or GLD ETF from 2004) weekly prices. "
            "Tests whether astrological features predict large weekly gold moves."
        ),
    },

    "bitcoin": {
        "name": "Bitcoin (BTC-USD)",
        "fetch_fn": "fetch_bitcoin",
        "date_range": ("2010-01-01", "2024-12-31"),
        "frequency": "weekly",
        "targets": [
            {
                "col": "big_move",
                "description": "Binary: |weekly return| >= 10%",
            }
        ],
        "description": (
            "Bitcoin USD weekly prices (2010–2024). "
            "Tests whether astrological features predict extreme BTC moves."
        ),
    },

    "crude_oil": {
        "name": "Crude Oil (CL=F futures)",
        "fetch_fn": "fetch_crude_oil",
        "date_range": ("1983-01-01", "2024-12-31"),
        "frequency": "weekly",
        "targets": [
            {
                "col": "big_move",
                "description": "Binary: |weekly return| >= 5%",
            }
        ],
        "description": (
            "WTI crude oil futures weekly (1983–2024). "
            "Tests whether astrological features predict big weekly oil swings."
        ),
    },

    "treasury_yield": {
        "name": "10-Year Treasury Yield (^TNX)",
        "fetch_fn": "fetch_treasury_yield",
        "date_range": ("1962-01-01", "2024-12-31"),
        "frequency": "weekly",
        "targets": [
            {
                "col": "big_move",
                "description": "Binary: |weekly yield change| >= 0.20 percentage points",
            }
        ],
        "description": (
            "US 10-year Treasury yield weekly (1962–2024). "
            "Tests whether astrological features predict sharp interest rate moves."
        ),
    },

    # ── Macroeconomic (FRED) ───────────────────────────────────────────────────

    "unemployment": {
        "name": "US Unemployment Rate (UNRATE)",
        "fetch_fn": "fetch_unemployment",
        "date_range": ("1948-01-01", "2024-12-31"),
        "frequency": "monthly",
        "targets": [
            {
                "col": "increase_gt03pp",
                "description": "Binary: month-over-month increase > 0.3 percentage points",
            }
        ],
        "description": (
            "US civilian unemployment rate monthly (FRED UNRATE, 1948–2024). "
            "Tests whether astrological features predict sharp unemployment rises."
        ),
    },

    "cpi": {
        "name": "Consumer Price Index (CPIAUCSL)",
        "fetch_fn": "fetch_cpi",
        "date_range": ("1913-01-01", "2024-12-31"),
        "frequency": "monthly",
        "targets": [
            {
                "col": "yoy_gt5pct",
                "description": "Binary: year-over-year CPI change > 5%",
            }
        ],
        "description": (
            "US CPI (All Urban Consumers, seasonally adjusted) monthly (FRED, 1913–2024). "
            "Tests whether astrological features predict high-inflation months."
        ),
    },

    "recession": {
        "name": "US Recession Indicator (USREC)",
        "fetch_fn": "fetch_recession",
        "date_range": ("1854-01-01", "2024-12-31"),
        "frequency": "monthly",
        "targets": [
            {
                "col": "recession_start",
                "description": "Binary: month immediately preceding recession onset (USREC transitions 0→1)",
            }
        ],
        "description": (
            "NBER US recession indicator monthly (FRED USREC, 1854–2024). "
            "Tests whether astrological features predict recession onset."
        ),
    },

    "fed_funds": {
        "name": "Federal Funds Rate (FEDFUNDS)",
        "fetch_fn": "fetch_fed_funds",
        "date_range": ("1954-01-01", "2024-12-31"),
        "frequency": "monthly",
        "targets": [
            {
                "col": "rate_hike",
                "description": "Binary: month-over-month Fed Funds Rate increase (any hike)",
            }
        ],
        "description": (
            "Effective Federal Funds Rate monthly (FRED FEDFUNDS, 1954–2024). "
            "Tests whether astrological features predict FOMC rate hikes."
        ),
    },

    # ── Natural / Geophysical ──────────────────────────────────────────────────

    "earthquakes": {
        "name": "Global Earthquakes M>=5.5 (USGS)",
        "fetch_fn": "fetch_earthquakes",
        "date_range": ("1900-01-01", "2024-12-31"),
        "frequency": "daily",
        "targets": [
            {
                "col": "m7plus",
                "description": "Binary: at least one M>=7.0 earthquake on this day",
            }
        ],
        "description": (
            "USGS global earthquake catalog M>=5.5 (1900–2024). "
            "Tests whether astrological features predict major earthquake days."
        ),
    },

    "geomagnetic_kp": {
        "name": "Geomagnetic Kp Index (GFZ)",
        "fetch_fn": "fetch_geomagnetic_kp",
        "date_range": ("1932-01-01", "2024-12-31"),
        "frequency": "daily",
        "targets": [
            {
                "col": "kp_storm_day",
                "description": "Binary: daily maximum Kp >= 5 (minor geomagnetic storm)",
            }
        ],
        "description": (
            "GFZ Potsdam Kp index daily (1932–2024). "
            "Tests whether astrological features predict geomagnetic storms."
        ),
    },

    "sunspots": {
        "name": "Monthly Sunspot Number (SIDC)",
        "fetch_fn": "fetch_sunspots",
        "date_range": ("1700-01-01", "2024-12-31"),
        "frequency": "monthly",
        "targets": [
            {
                "col": "high_sunspot",
                "description": (
                    "Binary: monthly sunspot number > 150 OR > (rolling mean + 2*rolling std)"
                ),
            }
        ],
        "description": (
            "SILSO monthly sunspot number (Royal Observatory Belgium, 1700–2024). "
            "Tests whether astrological features correlate with solar activity peaks."
        ),
    },

    "hurricanes": {
        "name": "Atlantic Hurricanes Cat 3+ Landfall (HURDAT2)",
        "fetch_fn": "fetch_hurricanes",
        "date_range": ("1851-01-01", "2024-12-31"),
        "frequency": "daily",
        "targets": [
            {
                "col": "cat3plus_landfall",
                "description": (
                    "Binary: at least one Category 3+ hurricane landfall on this day "
                    "(max wind >= 96 knots AND record type 'L')"
                ),
            }
        ],
        "description": (
            "NHC HURDAT2 Atlantic/Eastern Pacific hurricane database (1851–2023). "
            "Tests whether astrological features predict major hurricane landfalls."
        ),
    },

    # ── Human / Social ─────────────────────────────────────────────────────────

    "traffic_fatalities": {
        "name": "US Traffic Fatalities (NHTSA FARS)",
        "fetch_fn": "fetch_traffic_fatalities",
        "date_range": ("1975-01-01", "2022-12-31"),
        "frequency": "monthly",
        "targets": [
            {
                "col": "above_avg_month",
                "description": "Binary: monthly total > 10% above trailing 12-month rolling mean",
            }
        ],
        "description": (
            "NHTSA Fatality Analysis Reporting System monthly fatalities (1975–2022). "
            "Tests whether astrological features predict high-fatality months."
        ),
    },

    "influenza_ili": {
        "name": "US Influenza ILI Surveillance (CDC)",
        "fetch_fn": "fetch_influenza_ili",
        "date_range": ("1997-01-01", "2024-12-31"),
        "frequency": "weekly",
        "targets": [
            {
                "col": "above_baseline",
                "description": "Binary: national weekly ILI% > national baseline threshold",
            }
        ],
        "description": (
            "CDC ILINet national influenza-like illness surveillance weekly (1997–2024). "
            "Tests whether astrological features predict flu activity spikes."
        ),
    },

    # ── Space Weather ──────────────────────────────────────────────────────────

    "solar_flares": {
        "name": "Solar X-class Flares (NOAA SWPC)",
        "fetch_fn": "fetch_solar_flares",
        "date_range": ("1975-01-01", "2024-12-31"),
        "frequency": "daily",
        "targets": [
            {
                "col": "x_class_flare",
                "description": "Binary: at least one X-class solar flare on this day",
            }
        ],
        "description": (
            "NOAA SWPC solar flare catalog X-class events (1975–2024). "
            "Tests whether astrological features predict extreme solar flare days."
        ),
    },

    "proton_events": {
        "name": "Solar Proton Events (NOAA NGDC)",
        "fetch_fn": "fetch_proton_events",
        "date_range": ("1976-01-01", "2024-12-31"),
        "frequency": "daily",
        "targets": [
            {
                "col": "proton_event",
                "description": "Binary: at least one solar proton event on this day",
            }
        ],
        "description": (
            "NOAA NGDC solar proton event catalog (1976–2024). "
            "Tests whether astrological features predict solar particle events."
        ),
    },
}

# ---------------------------------------------------------------------------
# Validation: make sure every domain has required keys
# ---------------------------------------------------------------------------

_REQUIRED_KEYS = {"name", "fetch_fn", "date_range", "frequency", "targets", "description"}

for _domain_name, _cfg in DOMAINS.items():
    _missing = _REQUIRED_KEYS - set(_cfg.keys())
    if _missing:
        raise ValueError(
            f"Domain '{_domain_name}' is missing required keys: {_missing}"
        )
    if _cfg["frequency"] not in ("daily", "weekly", "monthly"):
        raise ValueError(
            f"Domain '{_domain_name}' has invalid frequency: {_cfg['frequency']!r}"
        )
    if not isinstance(_cfg["date_range"], tuple) or len(_cfg["date_range"]) != 2:
        raise ValueError(
            f"Domain '{_domain_name}' date_range must be a 2-tuple of ISO date strings"
        )

__all__ = ["DOMAINS"]
