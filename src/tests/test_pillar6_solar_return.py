from src.engine.models import Chart, Planet, PlanetName
from src.engine.solar_return import SolarReturnEngine


def test_ibn_ezra_annual_revolution_core_uses_return_ascendant_not_muntha():
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
        geo_lat=40.7,
        geo_lon=-74.0,
    )
    sr_planets = [
        Planet(name=PlanetName.SUN, longitude=0.0),
        Planet(name=PlanetName.MOON, longitude=150.0),
        Planet(name=PlanetName.VENUS, longitude=40.0),
        Planet(name=PlanetName.MARS, longitude=45.0),
        Planet(name=PlanetName.JUPITER, longitude=70.0),
        Planet(name=PlanetName.SATURN, longitude=130.0),
        Planet(name=PlanetName.MERCURY, longitude=5.0),
    ]
    sr_chart = Chart(
        sun_altitude=0.0,
        planets=sr_planets,
        ascendant=45.0,  # Taurus rises, so Venus is the return-Asc ruler.
    )

    analysis = SolarReturnEngine.analyze_solar_return(sr_chart, natal_chart, age=1)

    assert analysis["return_ascendant"]["sign"] == "Taurus"
    assert analysis["return_ascendant_ruler"]["name"] == "Venus"
    assert analysis["return_ascendant_ruler"]["return_house"] == 1
    assert analysis["source_rule_id"] == "ibn_ezra_annual_revolution_core"
    assert "muntha" not in analysis
    assert "lord_of_year" not in analysis
    assert "morin_axiom" not in analysis
    assert len(analysis["determinations"]) == 7


def test_annual_revolution_compares_sect_light_triplicity_ruler():
    natal = Chart(
        sun_altitude=10.0,
        ascendant=0.0,
        planets=[
            Planet(PlanetName.SUN, 5.0),
            Planet(PlanetName.MOON, 35.0),
            Planet(PlanetName.MERCURY, 65.0),
            Planet(PlanetName.VENUS, 95.0),
            Planet(PlanetName.MARS, 125.0),
            Planet(PlanetName.JUPITER, 155.0),
            Planet(PlanetName.SATURN, 185.0),
        ],
    )
    annual = Chart(
        sun_altitude=0.0,
        ascendant=30.0,
        planets=[
            Planet(PlanetName.SUN, 5.0),
            Planet(PlanetName.MOON, 45.0),
            Planet(PlanetName.MERCURY, 75.0),
            Planet(PlanetName.VENUS, 105.0),
            Planet(PlanetName.MARS, 135.0),
            Planet(PlanetName.JUPITER, 165.0),
            Planet(PlanetName.SATURN, 195.0),
        ],
    )

    result = SolarReturnEngine.analyze_solar_return(annual, natal, age=30)

    comparison = result["sect_light_triplicity_comparison"]
    assert comparison["ruler"] == "Sun"
    assert comparison["natal_house"] == 1
    assert comparison["return_house"] == 12
