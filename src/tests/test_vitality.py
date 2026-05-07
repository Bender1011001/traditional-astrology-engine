
from src.engine.hyleg import HylegAlcocodenEngine
from src.engine.models import Chart, Planet, PlanetName


def create_vitality_chart(sun_lon, moon_lon, asc_lon, sun_alt):
    sun = Planet(name=PlanetName.SUN, longitude=sun_lon, altitude=sun_alt)
    moon = Planet(
        name=PlanetName.MOON, longitude=moon_lon, altitude=1.0
    )  # Assume moon is up

    # Needs a ruler to aspect it. Let's add Mars in Aries (Domicile) to aspect Sun in Aries.
    mars = Planet(
        name=PlanetName.MARS, longitude=15.0
    )  # Conjunct or close to Sun at 10

    planets = [sun, moon, mars]
    # Add other 7 planets for Alcocoden check
    planets.extend(
        [
            Planet(name=PlanetName.MERCURY, longitude=200.0),
            Planet(name=PlanetName.VENUS, longitude=210.0),
            Planet(name=PlanetName.JUPITER, longitude=220.0),
            Planet(name=PlanetName.SATURN, longitude=230.0),
        ]
    )

    return Chart(
        sun_altitude=sun_alt,
        planets=planets,
        ascendant=asc_lon,
        houses={1: asc_lon, 10: (asc_lon + 270) % 360},  # Minimal house mock
        jd=2460000.5,
    )


def test_hyleg_selection():
    # Day chart, Sun in 1st house (Aries), aspected by Mars (ruler)
    chart = create_vitality_chart(10.0, 50.0, 5.0, 1.0)
    hyleg = HylegAlcocodenEngine.determine_hyleg(chart)
    assert hyleg["name"] == "Sun"


def test_alcocoden_selection():
    chart = create_vitality_chart(10.0, 50.0, 5.0, 1.0)
    hyleg = {"name": "Sun", "longitude": 5.0}  # 5 Aries -> Jupiter Bound
    # Ruler of 5 Aries terms is Jupiter (0-6).
    # If we put Jupiter in aspect...
    # Let's adjust mock chart to have Jupiter aspecting 5 Aries.
    chart.planets = [p for p in chart.planets if p.name != PlanetName.JUPITER]
    chart.planets.append(
        Planet(name=PlanetName.JUPITER, longitude=5.0)
    )  # Conjunct 5 Aries

    # Term/bound ruler selection (Valens-style): 5 Aries is in Jupiter's bounds.
    alcocoden = HylegAlcocodenEngine.determine_alcocoden(
        hyleg, chart, method="valens_term"
    )
    assert alcocoden is not None
    assert alcocoden["name"] == PlanetName.JUPITER


def test_lifespan_calculation():
    chart = create_vitality_chart(10.0, 50.0, 5.0, 1.0)
    hyleg = {"name": "Sun"}
    jupiter = Planet(name=PlanetName.JUPITER, longitude=12.0)
    alcocoden = {"name": PlanetName.JUPITER, "planet": jupiter}

    report = HylegAlcocodenEngine.calculate_lifespan(hyleg, alcocoden, chart)
    assert "total_years" in report
    assert report["total_years"] > 0
