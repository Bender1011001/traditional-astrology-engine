from datetime import datetime

import pytest

from src.engine.classical_mechanics import calculate_planetary_hours
from src.engine.planetary_hours import PlanetaryHourEngine


def test_planetary_hours_logic():
    """Wednesday noon in New York should be Mercury's day, daytime."""
    dt = datetime(2023, 10, 25, 12, 0)  # Wednesday (Mercury Day)
    lat, lon = 40.71, -74.00

    report = PlanetaryHourEngine.calculate_hours(dt, lat, lon)
    assert "day_ruler" in report
    assert "hour_ruler" in report
    assert (
        report["day_ruler"] == "Mercury"
    ), f"Wednesday day ruler should be Mercury, got {report['day_ruler']}"
    assert report["phase"] == "DAY"
    assert 1 <= report["hour_number_phase"] <= 12


def test_chaldean_order():
    order = PlanetaryHourEngine.CHALDEAN_ORDER
    # Sat, Jup, Mar, Sun, Ven, Mer, Moo
    assert order[0].value == "Saturn"
    assert order[-1].value == "Moon"


@pytest.mark.parametrize(
    "day,expected_ruler",
    [
        (22, "Sun"),  # Sunday
        (23, "Moon"),  # Monday
        (24, "Mars"),  # Tuesday
        (25, "Mercury"),  # Wednesday
        (26, "Jupiter"),  # Thursday
        (27, "Venus"),  # Friday
        (28, "Saturn"),  # Saturday
    ],
)
def test_day_rulers_all_week(day, expected_ruler):
    """Validate day ruler for every day of the week (Oct 22-28, 2023 Sun-Sat)."""
    dt = datetime(2023, 10, day, 14, 0)  # 2 PM local-ish (well into daytime UTC)
    lat, lon = 40.71, -74.00
    report = PlanetaryHourEngine.calculate_hours(dt, lat, lon)
    assert (
        report["day_ruler"] == expected_ruler
    ), f"Day {day} (expected {expected_ruler}) got {report['day_ruler']}"


def test_night_phase():
    """23:00 UTC on Oct 25 should be night phase for New York (sunset ~22 UTC)."""
    dt = datetime(2023, 10, 25, 23, 30)
    lat, lon = 40.71, -74.00
    report = PlanetaryHourEngine.calculate_hours(dt, lat, lon)
    assert report["phase"] == "NIGHT"
    # Still Wednesday's planetary day (night of Wed)
    assert report["day_ruler"] == "Mercury"
    assert 1 <= report["hour_number_phase"] <= 12


def test_classical_mechanics_day_lord():
    """Cross-check: classical_mechanics.py should agree on day lord for Wednesday noon."""
    dt = datetime(2023, 10, 25, 14, 0)  # Wednesday, well into daytime UTC
    lat, lon = 40.71, -74.00
    result = calculate_planetary_hours(dt, lat, lon)
    assert result is not None
    assert (
        result.day_lord == "Mercury"
    ), f"Classical mechanics got {result.day_lord} for Wednesday"
