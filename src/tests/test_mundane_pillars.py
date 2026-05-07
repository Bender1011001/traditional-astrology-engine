import pytest

from src.engine.models import PlanetName
from src.engine.mundane import (MEAN_MOTION_JUPITER, MEAN_MOTION_SATURN,
                                MundaneEngine)


def test_mean_motion_constants():
    """Verify the mean motion constants are approximately correct."""
    # Saturn should take ~29.4 years
    sat_period = 360 / (MEAN_MOTION_SATURN * 365.25)
    assert 29.0 < sat_period < 30.0

    # Jupiter should take ~11.8 years
    jup_period = 360 / (MEAN_MOTION_JUPITER * 365.25)
    assert 11.0 < jup_period < 12.0


def test_mean_conjunction_era():
    # Test for J2000 epoch (JD 2451545.0)
    engine = MundaneEngine(2451545.0)
    era = engine.get_mean_conjunction_era()

    assert "last_mean_jd" in era
    assert era["last_mean_jd"] < 2451545.0
    assert "triplicity" in era
    assert era["triplicity"] in ["Fire", "Earth", "Air", "Water"]


def test_mighty_firdaria():
    # Test for J2000
    engine = MundaneEngine(2451545.0)
    firdaria = engine.get_mighty_firdaria()

    assert "ruler" in firdaria
    assert "years_into_period" in firdaria
    assert firdaria["years_into_period"] >= 0


def test_al_mubtazz_scoring():
    # Test for a known Ingress (e.g., 2024 Aries Ingress)
    # 2024-03-20 approx JD 2460389.6
    ingress_jd = 2460389.6
    engine = MundaneEngine(ingress_jd, lat=40.7, lon=-74.0)
    victor = engine.calculate_al_mubtazz(ingress_jd)

    assert "victor" in victor
    assert victor["victor"] in [p.value for p in PlanetName]
    assert victor["score"] > 0


def test_hierarchy_report_integration():
    engine = MundaneEngine(2451545.0)
    report = engine.get_hierarchy_report()

    # Check for Rank 0 (Universal Periodic Cycles)
    rank_0 = next((i for i in report if i["rank"] == 0), None)
    assert rank_0 is not None
    assert "mighty_firdaria" in rank_0["data"]

    # Check for Rank 2 (Great Conjunction)
    rank_2 = next((i for i in report if i["rank"] == 2), None)
    assert rank_2 is not None
    assert "al_mubtazz" in rank_2["data"]


if __name__ == "__main__":
    pytest.main([__file__])
