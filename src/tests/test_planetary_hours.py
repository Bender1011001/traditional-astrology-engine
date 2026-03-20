import pytest
from datetime import datetime
from src.engine.planetary_hours import PlanetaryHourEngine

def test_planetary_hours_logic():
    # New York: 40.71, -74.00, Wednesday noon
    dt = datetime(2023, 10, 25, 12, 0)  # Wednesday (Mercury Day)
    lat, lon = 40.71, -74.00

    report = PlanetaryHourEngine.calculate_hours(dt, lat, lon)
    assert "day_ruler" in report
    assert "hour_ruler" in report
    assert report["day_ruler"] == "Mercury", f"Wednesday day ruler should be Mercury, got {report['day_ruler']}"
    assert report["phase"] == "DAY"
    assert 1 <= report["hour_number_phase"] <= 12

def test_chaldean_order():
    order = PlanetaryHourEngine.CHALDEAN_ORDER
    # Sat, Jup, Mar, Sun, Ven, Mer, Moo
    assert order[0].value == "Saturn"
    assert order[-1].value == "Moon"
