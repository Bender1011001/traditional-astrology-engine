"""Stress tests and verification for financial astrology calculations."""

import json
from datetime import datetime, timedelta
import pytest
import swisseph as swe

# `financial_astrology_analysis/` is a local research directory and is
# deliberately gitignored ("never ship"), so it is present on a developer
# machine and absent in CI. Importing it at module scope made collection FAIL
# rather than skip, which took the whole suite - and therefore the deploy -
# down with one ImportError. Skip the module instead when the dependency is
# not there.
_finance = pytest.importorskip(
    "financial_astrology_analysis.analyze_finance_astrology",
    reason="financial_astrology_analysis/ is a gitignored local research directory",
)
calculate_date_astrology = _finance.calculate_date_astrology
DISCLAIMER = _finance.DISCLAIMER
from src.engine.models import Sign

# 1. Generate edge-case dates to test
EDGE_CASE_YEARS = [1900, 1920, 1929, 1973, 1987, 2000, 2008, 2020, 2024, 2025, 2026]

EDGE_CASE_DATES = []

# Add early Jan/Feb dates to test preceding ingress fallback to prior year
for yr in EDGE_CASE_YEARS:
    EDGE_CASE_DATES.extend([
        f"{yr}-01-01",
        f"{yr}-01-15",
        f"{yr}-02-15",
        f"{yr}-02-28",
    ])
    # Leap year handling
    is_leap = (yr % 4 == 0 and yr % 100 != 0) or (yr % 400 == 0)
    if is_leap:
        EDGE_CASE_DATES.append(f"{yr}-02-29")

# Add dates right before, during, and after Aries Ingress (approx March 19-21)
for yr in EDGE_CASE_YEARS:
    EDGE_CASE_DATES.extend([
        f"{yr}-03-18",
        f"{yr}-03-19",
        f"{yr}-03-20",
        f"{yr}-03-21",
        f"{yr}-03-22",
        f"{yr}-03-23",
    ])

# Add Mars / Saturn station dates
STATION_DATES = [
    "2024-06-29",  # Saturn station Rx
    "2024-11-15",  # Saturn station Dir
    "2024-12-06",  # Mars station Rx
    "2025-02-24",  # Mars station Dir
    "2022-10-30",  # Mars station Rx
    "2023-01-12",  # Mars station Dir
    "2025-07-13",  # Saturn station Rx
    "2025-11-28",  # Saturn station Dir
]
EDGE_CASE_DATES.extend(STATION_DATES)

# Add eclipse dates (exact days, day before, day after)
ECLIPSE_DATES = [
    # 2024-04-08 Solar Eclipse
    "2024-04-07",
    "2024-04-08",
    "2024-04-09",
    # 2024-09-18 Lunar Eclipse
    "2024-09-17",
    "2024-09-18",
    "2024-09-19",
]
EDGE_CASE_DATES.extend(ECLIPSE_DATES)

# Remove duplicates and sort
EDGE_CASE_DATES = sorted(list(set(EDGE_CASE_DATES)))


@pytest.mark.parametrize("date_str", EDGE_CASE_DATES)
def test_financial_astrology_correctness(date_str):
    """Verify that calculate_date_astrology does not crash and produces valid outputs."""
    # Run the calculation
    result = calculate_date_astrology(date_str)
    
    # 1. Basic structure and metadata checks
    assert result["date"] == date_str
    assert isinstance(result["jd"], float)
    assert result["disclaimer"] == DISCLAIMER
    
    target_jd = result["jd"]
    
    # 2. Preceding Solar Eclipse Verification
    solar = result["preceding_solar_eclipse"]
    assert "jd" in solar
    assert "date" in solar
    assert "longitude" in solar
    assert "sign" in solar
    assert "degree" in solar
    assert "distance_days" in solar
    
    # Eclipse JD must be strictly less than the target JD
    assert solar["jd"] < target_jd, f"Preceding solar eclipse JD ({solar['jd']}) must be strictly less than target JD ({target_jd}) for date {date_str}"
    
    # Distance days must be positive and mathematically correct
    expected_solar_dist = round(target_jd - solar["jd"], 4)
    assert abs(solar["distance_days"] - expected_solar_dist) < 1e-4, f"Solar eclipse distance mismatch: got {solar['distance_days']}, expected {expected_solar_dist}"
    
    # Check coordinate bounds
    assert 0.0 <= solar["longitude"] < 360.0
    assert 0.0 <= solar["degree"] < 30.0
    assert solar["sign"] in [s.value for s in Sign]
    
    # 3. Preceding Lunar Eclipse Verification
    lunar = result["preceding_lunar_eclipse"]
    assert "jd" in lunar
    assert "date" in lunar
    assert "longitude" in lunar
    assert "sign" in lunar
    assert "degree" in lunar
    assert "distance_days" in lunar
    
    # Eclipse JD must be strictly less than the target JD
    assert lunar["jd"] < target_jd, f"Preceding lunar eclipse JD ({lunar['jd']}) must be strictly less than target JD ({target_jd}) for date {date_str}"
    
    # Distance days must be positive and mathematically correct
    expected_lunar_dist = round(target_jd - lunar["jd"], 4)
    assert abs(lunar["distance_days"] - expected_lunar_dist) < 1e-4, f"Lunar eclipse distance mismatch: got {lunar['distance_days']}, expected {expected_lunar_dist}"
    
    # Check coordinate bounds
    assert 0.0 <= lunar["longitude"] < 360.0
    assert 0.0 <= lunar["degree"] < 30.0
    assert lunar["sign"] in [s.value for s in Sign]
    
    # 4. Preceding Great Conjunction Verification
    gc = result["preceding_great_conjunction"]
    assert "jd" in gc
    assert "date" in gc
    assert "longitude" in gc
    assert "sign" in gc
    assert "degree" in gc
    assert "distance_days" in gc
    
    # Great Conjunction JD must be strictly less than the target JD
    assert gc["jd"] < target_jd, f"Preceding Great Conjunction JD ({gc['jd']}) must be strictly less than target JD ({target_jd}) for date {date_str}"
    
    # Distance days must be positive and mathematically correct
    expected_gc_dist = round(target_jd - gc["jd"], 4)
    assert abs(gc["distance_days"] - expected_gc_dist) < 1e-4, f"Great Conjunction distance mismatch: got {gc['distance_days']}, expected {expected_gc_dist}"
    
    # Check coordinate bounds
    assert 0.0 <= gc["longitude"] < 360.0
    assert 0.0 <= gc["degree"] < 30.0
    assert gc["sign"] in [s.value for s in Sign]
    
    # 5. Preceding Aries Ingress Verification
    ingress = result["preceding_aries_ingress"]
    assert "jd" in ingress
    assert "date" in ingress
    assert "planets" in ingress
    
    # Ingress JD must be strictly less than target JD
    assert ingress["jd"] < target_jd, f"Preceding Aries Ingress JD ({ingress['jd']}) must be strictly less than target JD ({target_jd}) for date {date_str}"
    
    # Ingress year should be equal to the target year or the target year - 1
    target_dt = datetime.strptime(date_str, "%Y-%m-%d")
    ingress_y, _, _, _ = swe.revjul(ingress["jd"])
    assert ingress_y in [target_dt.year, target_dt.year - 1]
    
    # Verify ingress planetary coordinates
    for p_name, p_data in ingress["planets"].items():
        assert "longitude" in p_data
        assert "sign" in p_data
        assert "degree" in p_data
        assert 0.0 <= p_data["longitude"] < 360.0
        assert 0.0 <= p_data["degree"] < 30.0
        assert p_data["sign"] in [s.value for s in Sign]
        
    # 6. Outer Planet Aspects
    for aspect in result["outer_planet_aspects"]:
        assert aspect["planet_a"] in ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
        assert aspect["planet_b"] in ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
        assert aspect["aspect_type"] in ["Conjunction", "Square", "Opposition"]
        assert 0.0 <= aspect["orb"] <= 5.0
        assert 0.0 <= aspect["angle_diff"] <= 180.0
        
    # 7. Planet Speeds and Retrograde / Station Flags
    for p_name, p_data in result["planet_speeds"].items():
        assert "longitude" in p_data
        assert "speed" in p_data
        assert "retrograde" in p_data
        assert "station" in p_data
        
        assert 0.0 <= p_data["longitude"] < 360.0
        assert isinstance(p_data["speed"], float)
        assert p_data["retrograde"] == (p_data["speed"] < 0)
        assert p_data["station"] == (abs(p_data["speed"]) < 0.05)
        
    # 8. Fixed Star Alignments
    for align in result["fixed_star_alignments"]:
        assert "star" in align
        assert "planet" in align
        assert "orb" in align
        assert "defined_orb" in align
        assert align["orb"] <= align["defined_orb"]
