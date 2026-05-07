from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import pytz  # type: ignore

from src.engine.calculator.geo import get_coordinates, get_timezone
from src.engine.calculator.main import (ChartCalculator, calculate_chart_data,  # type: ignore
                                        get_local_datetime_now)
from src.engine.models import Chart

# Mock data
MOCK_CITY = "Los Angeles"
MOCK_STATE = "CA"
MOCK_LAT = 34.0522
MOCK_LON = -118.2437
MOCK_TZ = "America/Los_Angeles"


@pytest.fixture
def mock_geocoder():
    with patch("src.engine.calculator.geo.geolocator.geocode") as mock_geo:
        mock_location = MagicMock()
        mock_location.latitude = MOCK_LAT
        mock_location.longitude = MOCK_LON
        mock_geo.return_value = mock_location
        yield mock_geo


@pytest.fixture
def mock_timezone():
    with patch("src.engine.calculator.geo.tf") as mock_tf_instance:
        mock_tf_instance.timezone_at.return_value = MOCK_TZ
        yield mock_tf_instance.timezone_at


def test_get_coordinates(mock_geocoder):
    lat, lon = get_coordinates(MOCK_CITY, MOCK_STATE)
    assert lat == MOCK_LAT
    assert lon == MOCK_LON
    mock_geocoder.assert_called_once()


def test_get_timezone(mock_timezone):
    tz = get_timezone(MOCK_LAT, MOCK_LON)
    assert tz == MOCK_TZ
    mock_timezone.assert_called_once_with(lng=MOCK_LON, lat=MOCK_LAT)


def test_get_local_datetime_now(mock_geocoder, mock_timezone):
    # Mock datetime.now to return a fixed time?
    # Hard to mock datetime.now() directly on the class without external libs like freezegun.
    # For now, just check it returns a datetime with correct tzinfo.
    dt = get_local_datetime_now(MOCK_CITY, MOCK_STATE)
    assert isinstance(dt, datetime)
    assert str(dt.tzinfo) == MOCK_TZ or MOCK_TZ in str(dt.tzinfo)


def test_calculate_chart_data_integration(mock_geocoder, mock_timezone):
    # This tests the high-level function
    result = calculate_chart_data("2023-01-01", "12:00", MOCK_CITY, MOCK_STATE)

    assert "planets" in result
    assert "houses" in result
    assert "angles" in result
    assert "Ascendant" in result["angles"]

    assert result["meta"]["city"] == MOCK_CITY

    # Check Sun existence
    assert "Sun" in result["planets"]
    sun = result["planets"]["Sun"]
    assert "longitude" in sun


def test_chart_calculator_class_compatibility(mock_geocoder, mock_timezone):
    # Test the Class wrapper for backward compatibility
    calc = ChartCalculator()
    dt = datetime(2023, 1, 1, 12, 0)
    chart = calc.calculate_chart(dt, MOCK_CITY, MOCK_STATE)

    assert isinstance(chart, Chart)
    assert len(chart.planets) > 0
    assert chart.ascendant != 0.0
    # Check is_retrograde property on a planet (e.g., Node usually retrograde, or check speed)
    # Just ensure attribute access works
    p = chart.planets[0]
    assert hasattr(p, "is_retrograde")
    assert isinstance(p.is_retrograde, bool)

    with patch("src.engine.calculator.geo.geolocator.geocode") as mock_geo:
        mock_geo.return_value = None
        with pytest.raises(ValueError, match="Could not find location"):
            get_coordinates("NonExistentCity", "ZZ")


def test_julian_day_conversion():
    from src.engine.calculator.time_utils import get_julian_day

    # 2000-01-01 12:00 UTC is J2000.0 = 2451545.0
    dt = datetime(2000, 1, 1, 12, 0, tzinfo=pytz.UTC)
    jd = get_julian_day(dt)
    assert abs(jd - 2451545.0) < 0.001


def test_astronomy_functions():
    import swisseph as swe

    from src.engine.calculator.astronomy import get_houses, get_planets_ut

    # Mock data
    jd = 2451545.0  # J2000
    lat = 34.05
    lon = -118.24

    # Test get_houses
    houses, ascmc = get_houses(jd, lat, lon, "P")
    assert len(houses) == 12
    assert len(ascmc) > 0

    # Test get_planets_ut (Integration with swe)
    # We need to mock swe.set_topo and calc_ut if we want unit isolation,
    # but for now let's test the wrapper logic.
    # Note: This might fail if ephe files are missing, but previous tests passed so likely ok.
    # We call with standard flags
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    topo_flags = flags | swe.FLG_TOPOCTR
    geopos = (lon, lat, 0)

    planets = get_planets_ut(jd, flags, topo_flags, geopos)
    assert "Sun" in planets
    assert "longitude" in planets["Sun"]

    # Check Sun approx position (Capricorn 280)
    assert 279.0 <= planets["Sun"]["longitude"] <= 281.0
