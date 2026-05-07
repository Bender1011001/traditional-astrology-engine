import pytest

from src.engine.models import PlanetName
from src.engine.mundane import EPOCH_KALI_YUGA, MundaneEngine


def test_world_firdaria_calculation():
    """
    Verify Pillar 7: Firdaria of the World epochs.
    """
    # Test for target JD (e.g., modern day)
    # JD 2460000.5 approx Feb 2023
    engine = MundaneEngine(jd=2460000.5)

    report = engine.get_hierarchy_report()

    # Find rank 0 Universal Cycles
    universal = next((r for r in report if r["rank"] == 0), None)
    assert universal is not None
    assert "world_firdaria" in universal["data"]

    world_firdar = universal["data"]["world_firdaria"]

    # Check if a planet is returned
    assert world_firdar["planet"] in [p.value for p in PlanetName]
    assert world_firdar["duration"] == 75

    # Verify Epoch start
    # Days since epoch / (75*365.25)
    days_per_75y = 75 * 365.25
    elapsed = 2460000.5 - EPOCH_KALI_YUGA
    period_idx = int((elapsed % (525 * 365.25)) // days_per_75y)

    expected_planets = [
        PlanetName.SUN,
        PlanetName.MOON,
        PlanetName.MARS,
        PlanetName.MERCURY,
        PlanetName.JUPITER,
        PlanetName.VENUS,
        PlanetName.SATURN,
    ]
    assert world_firdar["planet"] == expected_planets[period_idx].value


if __name__ == "__main__":
    pytest.main([__file__])
