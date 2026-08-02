"""Tests for the financial astrology analysis script."""

import json
from datetime import datetime
import pytest
import swisseph as swe

# Import functions from our soon-to-be-created script
# Note: we add the project root to path, which is done by pytest automatically.
try:
    from financial_astrology_analysis.analyze_finance_astrology import (
        calculate_date_astrology,
        DISCLAIMER
    )
except ImportError:
    # Fallback to allow initial failing test run
    calculate_date_astrology = None
    DISCLAIMER = "Historical Use Only — not medical, financial, or legal advice. Do not use for investment or trading decisions."


def test_disclaimer_present():
    """Verify that the mandatory safety disclaimer is defined."""
    assert "Historical Use Only" in DISCLAIMER
    assert "not medical, financial, or legal advice" in DISCLAIMER
    assert "Do not use for investment or trading decisions" in DISCLAIMER


def test_calculate_date_astrology_1929():
    """Verify calculation for Black Tuesday (1929-10-29)."""
    if calculate_date_astrology is None:
        pytest.fail("calculate_date_astrology not imported")
        
    result = calculate_date_astrology("1929-10-29")
    
    # 1. Check disclaimer
    assert result["disclaimer"] == DISCLAIMER
    
    # 2. Check preceding eclipses
    assert "preceding_solar_eclipse" in result
    assert "preceding_lunar_eclipse" in result
    assert result["preceding_solar_eclipse"]["jd"] < 2425914.0
    assert result["preceding_lunar_eclipse"]["jd"] < 2425914.0
    assert result["preceding_solar_eclipse"]["distance_days"] > 0
    assert result["preceding_lunar_eclipse"]["distance_days"] > 0
    
    # 3. Check preceding Great Conjunction
    assert "preceding_great_conjunction" in result
    assert result["preceding_great_conjunction"]["jd"] < 2425914.0
    assert result["preceding_great_conjunction"]["sign"] == "Virgo"
    
    # 4. Check outer planet configurations
    assert "outer_planet_aspects" in result
    assert isinstance(result["outer_planet_aspects"], list)
    
    # 5. Check planet speeds and stations
    assert "planet_speeds" in result
    assert "Mercury" in result["planet_speeds"]
    assert "Mars" in result["planet_speeds"]
    assert "Saturn" in result["planet_speeds"]
    
    # 6. Check preceding Aries Ingress
    assert "preceding_aries_ingress" in result
    assert result["preceding_aries_ingress"]["jd"] < 2425914.0
    assert "planets" in result["preceding_aries_ingress"]
    assert "Sun" in result["preceding_aries_ingress"]["planets"]
    
    # 7. Check fixed star alignments
    assert "fixed_star_alignments" in result
    assert isinstance(result["fixed_star_alignments"], list)
