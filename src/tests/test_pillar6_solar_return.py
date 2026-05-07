
import pytest

from src.engine.models import Chart, Planet, PlanetName, Sign
from src.engine.solar_return import SolarReturnEngine


def test_lord_of_the_year_synthesis():
    """
    Verify Pillar 6: Lord of the Year and Muntha calculation.
    """
    # 0 Aries Ascendant
    natal_planets = [
        Planet(name=PlanetName.SUN, longitude=0.0),
        Planet(name=PlanetName.MOON, longitude=120.0),
        Planet(name=PlanetName.MERCURY, longitude=10.0),
        Planet(name=PlanetName.VENUS, longitude=20.0),
        Planet(name=PlanetName.MARS, longitude=30.0),
        Planet(name=PlanetName.JUPITER, longitude=60.0),
        Planet(name=PlanetName.SATURN, longitude=120.0),
    ]
    natal_chart = Chart(
        sun_altitude=10.0,
        planets=natal_planets,
        ascendant=0.0,
        houses={i: (i - 1) * 30 for i in range(1, 13)},
        geo_lat=40.7,
        geo_lon=-74.0,
    )

    # SR Chart: 1 year later (Age 1)
    # Muntha should be in Taurus (1 sign/year from Aries)
    sr_planets = [
        Planet(name=PlanetName.SUN, longitude=0.0),
        Planet(name=PlanetName.MOON, longitude=150.0),
        # Put Venus in the Muntha sign (Taurus) to see bonification
        Planet(name=PlanetName.VENUS, longitude=40.0),
        Planet(name=PlanetName.MARS, longitude=45.0),
        Planet(name=PlanetName.JUPITER, longitude=70.0),
        Planet(name=PlanetName.SATURN, longitude=130.0),
        Planet(name=PlanetName.MERCURY, longitude=5.0),
    ]
    sr_chart = Chart(
        sun_altitude=10.0,
        planets=sr_planets,
        ascendant=15.0,  # SR Asc in Aries
        houses={i: (i - 1) * 30 + 15.0 for i in range(1, 13)},
    )

    analysis = SolarReturnEngine.analyze_solar_return(sr_chart, natal_chart, age=1)

    # 1. Muntha Check
    assert analysis["muntha"]["sign"] == Sign.TAURUS.value
    # Natal Asc 0.0 -> Age 1 -> Muntha 30.0.
    # SR Houses start at 15.0. 1st house is 15-45.
    # Muntha (30.0) should be in SR House 1.
    assert analysis["muntha"]["sr_house"] == 1

    # 2. Lord of the Year (Muntha Ruler)
    # Muntha is Taurus -> Lord is Venus.
    assert analysis["lord_of_year"]["name"] == PlanetName.VENUS.value

    # 3. Assessment
    # Venus in SR is at 40.0.
    # SR Houses: H1 (15-45). Venus is Angular in SR.
    assert any("Angular in SR" in d for d in analysis["lord_of_year"]["details"])


if __name__ == "__main__":
    pytest.main([__file__])
