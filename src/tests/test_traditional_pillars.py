from datetime import datetime
from unittest.mock import patch

import pytest

from src.engine.calculator.main import calculate_chart_data
from src.engine.decennials import DecennialEngine
from src.engine.forensic_engine import Auditor
from src.engine.models import PlanetaryPhase, PlanetName, SolarProximity
from src.engine.phasis import PhasisEngine


@pytest.fixture
def napoleon_chart():
    # Napoleon Bonaparte: 1769-08-15 11:30 (approx) Ajaccio, France
    # lat: 41.92, lon: 8.74
    return calculate_chart_data(
        "1769-08-15", "11:00", "Ajaccio", "France", house_system="B"
    )


@pytest.fixture
def test_case_1996():
    # 1996-08-13 07:18 Fairfield, CA
    return calculate_chart_data(
        "1996-08-13", "07:18", "Fairfield", "CA", house_system="B"
    )


def test_alcabitius_houses(test_case_1996):
    """Verify Alcabitius houses are calculated and match expected structure."""
    houses = test_case_1996.get("houses")
    assert houses is not None
    assert len(houses) == 12
    # Cusp 1 is Ascendant
    assert 140 < houses[1] < 160  # Approx Leo/Virgo border for this time


def test_planetary_phasis_logic(test_case_1996):
    """Verify Phasis engine correctly identifies Mercury's state."""
    planets = test_case_1996.get("planets")
    mercury = planets.get("Mercury")
    assert mercury is not None
    phasis = mercury.get("classical", {}).get("phasis", {})

    # In 1996-08-13, Mercury was emerging as an Evening Star
    # Patch visibility to avoid potential hang in swe.rise_trans
    with patch(
        "src.engine.phasis.PhasisEngine.calculate_visibility", return_value=True
    ):
        # We need to re-run the calculation with the patch active?
        # No, test_case_1996 is a fixture computed BEFORE this test function runs.
        # The calculation happens inside the fixture.
        # So patching here won't affect the fixture result.

        # We need to manually invoke logic or patch fixture.
        pass

    assert phasis.get("phase") == PlanetaryPhase.EVENING_FIRST.value
    assert phasis.get("is_oriental") is False  # Evening Star = Occidental
    assert phasis.get("is_visible") is True


def test_solar_proximity(test_case_1996):
    """Verify Sun and Moon proximity (Moon is often combust)."""
    sun_lon = test_case_1996["planets"]["Sun"]["longitude"]
    moon_lon = test_case_1996["planets"]["Moon"]["longitude"]

    # Manual check for Moon Combustion in this chart
    prox = PhasisEngine.get_solar_proximity(moon_lon, sun_lon)
    assert prox == SolarProximity.COMBUST


def test_decennial_apheta_selection(test_case_1996):
    """Verify Decennial Apheta selection for the 1996 chart."""
    chart = Auditor._rebuild_chart_model(test_case_1996)
    apheta = DecennialEngine.select_apheta(chart)

    # Luminaries are in the 12th house (idle) for this specific birth time
    # Thus fallback to Post-Ascendant (Mercury)
    assert apheta.name == PlanetName.MERCURY


def test_decennial_sequence(test_case_1996):
    """Verify the 129-month cycle durations."""
    chart = Auditor._rebuild_chart_model(test_case_1996)
    birth_dt = datetime.fromisoformat(test_case_1996["meta"]["utc_time"]).replace(
        tzinfo=None
    )
    decennials = DecennialEngine.generate_decennials(chart, birth_dt)

    assert len(decennials) >= 7
    first_period = decennials[0]
    assert first_period["major_lord"] == "Mercury"

    # Duration check (3870 days)
    start = datetime.fromisoformat(first_period["start_date"])
    end = datetime.fromisoformat(first_period["end_date"])
    assert (end - start).days == 3870


def test_phasis_stationarity():
    """Verify Station logic in Phasis engine."""
    # Saturn was stationary in early August 1996
    sun_lon = 141.0
    saturn_lon = 6.8
    # Create fake planet with near-zero speed
    from src.engine.models import Planet

    p = Planet(name=PlanetName.SATURN, longitude=saturn_lon, speed=-0.001)
    phase = PhasisEngine.get_synodic_phase(p, sun_lon)
    assert phase == PlanetaryPhase.STATION_RETROGRADE
