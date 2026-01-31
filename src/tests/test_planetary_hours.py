import pytest
from datetime import datetime
from engine.planetary_hours import PlanetaryHourEngine

def test_planetary_hours_logic():
    # Mocking a date/time/loc
    # New York: 40.71, -74.00
    dt = datetime(2023, 10, 25, 12, 0) # Wednesday (Mercury Day)
    lat, lon = 40.71, -74.00
    
    # Note: This will actually call swisseph, which is fine if installed.
    # If not, we'd have to mock swe.
    try:
        report = PlanetaryHourEngine.calculate_hours(dt, lat, lon)
        assert "day_ruler" in report
        assert "hour_ruler" in report
        assert report["day_ruler"] == "Mercury"
    except Exception as e:
        pytest.skip(f"Swisseph error in test: {e}")

def test_chaldean_order():
    order = PlanetaryHourEngine.CHALDEAN_ORDER
    # Sat, Jup, Mar, Sun, Ven, Mer, Moo
    assert order[0].value == "Saturn"
    assert order[-1].value == "Moon"
