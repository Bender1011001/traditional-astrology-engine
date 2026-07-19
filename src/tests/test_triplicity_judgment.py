from src.engine.forensic_engine import Auditor
from src.engine.models import Chart, Planet, PlanetName


def test_day_fire_triplicity_has_no_invented_equal_life_thirds():
    chart = Chart(
        sun_altitude=10.0,
        ascendant=150.0,
        planets=[
            Planet(PlanetName.SUN, 140.0),
            Planet(PlanetName.MOON, 133.0),
            Planet(PlanetName.MERCURY, 160.0),
            Planet(PlanetName.VENUS, 112.0),
            Planet(PlanetName.MARS, 118.0),
            Planet(PlanetName.JUPITER, 280.0),
            Planet(PlanetName.SATURN, 7.0),
        ],
    )

    result = Auditor._calculate_triplicity_periods(chart)

    assert result["rulers"] == {
        "first": "Sun",
        "second": "Jupiter",
        "participant": "Saturn",
    }
    assert result["temporal_roles"]["first"].startswith("beginning")
    assert result["temporal_roles"]["second"].startswith("later outcome")
    assert "no fixed final life third" in result["temporal_roles"]["participant"]
    assert "chapters" not in result


def test_night_fire_reverses_first_and_second_but_keeps_participant():
    chart = Chart(
        sun_altitude=-10.0,
        ascendant=150.0,
        planets=[
            Planet(PlanetName.SUN, 140.0),
            Planet(PlanetName.MOON, 133.0),
            Planet(PlanetName.MERCURY, 160.0),
            Planet(PlanetName.VENUS, 112.0),
            Planet(PlanetName.MARS, 118.0),
            Planet(PlanetName.JUPITER, 280.0),
            Planet(PlanetName.SATURN, 7.0),
        ],
    )

    result = Auditor._calculate_triplicity_periods(chart)

    assert result["rulers"] == {
        "first": "Jupiter",
        "second": "Sun",
        "participant": "Saturn",
    }
