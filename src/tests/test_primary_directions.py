"""Tests for primary_directions.py — Placidus and Regiomontanus Primary Directions."""

from unittest.mock import patch

from src.engine.models import Chart, Planet, PlanetName
from src.engine.primary_directions import DirectionResult, PrimaryDirectionsEngine


def test_normalize_deg():
    assert PrimaryDirectionsEngine._normalize_deg(370.0) == 10.0
    assert PrimaryDirectionsEngine._normalize_deg(-10.0) == 350.0


def test_ptolemy_key():
    assert PrimaryDirectionsEngine.ptolemy_key(10.5) == 10.5


def test_format_years():
    assert PrimaryDirectionsEngine.format_years(10.5) == "10y 6m"
    assert PrimaryDirectionsEngine.format_years(10.0) == "10y 0m"


def test_ecliptic_to_equatorial():
    """Test 0 Aries -> RA 0, Dec 0."""
    ra, dec = PrimaryDirectionsEngine.ecliptic_to_equatorial(0.0, 0.0)
    assert abs(ra) < 0.01
    assert abs(dec) < 0.01

    # 90 Cancer -> RA 90, Dec ~23.4
    ra, dec = PrimaryDirectionsEngine.ecliptic_to_equatorial(90.0, 0.0)
    assert abs(ra - 90.0) < 0.01
    assert abs(dec - 23.44) < 0.01


def test_calculate_ad_and_arcs():
    # Equator (Dec 0) -> AD = 0. DSA = 90, NSA = 90
    ad = PrimaryDirectionsEngine.calculate_ad(0.0, 45.0)
    assert abs(ad) < 0.01

    dsa, nsa = PrimaryDirectionsEngine.calculate_semi_arcs(0.0, 45.0)
    assert dsa == 90.0
    assert nsa == 90.0


def test_calculate_md():
    md = PrimaryDirectionsEngine.calculate_md(100.0, 90.0)
    assert md == 10.0

    md2 = PrimaryDirectionsEngine.calculate_md(80.0, 90.0)
    assert md2 == -10.0


def test_calculate_pole():
    """Pole on the meridian should be 0."""
    pole = PrimaryDirectionsEngine.calculate_pole(0.0, 90.0, 45.0)
    assert pole == 0.0

    """Pole on the horizon should match geographical latitude."""
    pole_hz = PrimaryDirectionsEngine.calculate_pole(90.0, 90.0, 45.0)
    assert abs(pole_hz - 45.0) < 0.01


def test_calculate_mundane_position():
    """Test proportional position calculation."""
    # On MC (RA = RAMC) -> 10.0
    pos = PrimaryDirectionsEngine.calculate_mundane_position(90.0, 0.0, 90.0, 45.0)
    assert pos == 10.0

    # On IC (RA = IC) -> 4.0
    pos2 = PrimaryDirectionsEngine.calculate_mundane_position(270.0, 0.0, 90.0, 45.0)
    assert pos2 == 4.0

    # Ascendant (East, on horizon)
    pos3 = PrimaryDirectionsEngine.calculate_mundane_position(180.0, 0.0, 90.0, 45.0)
    assert pos3 == 7.0 or pos3 == 1.0


def test_get_full_speculum():
    p = Planet(name=PlanetName.SUN, longitude=0.0, speed=1.0)
    spec = PrimaryDirectionsEngine.get_full_speculum(p, 270.0, 0.0)
    assert spec.planet == "Sun"
    assert spec.ra == 0.0
    assert spec.dec == 0.0
    assert spec.ad == 0.0
    assert spec.dsa == 90.0
    assert spec.md == 90.0


@patch("swisseph.houses_armc")
def test_calculate_current_distributor(mock_armc):
    sun = Planet(name=PlanetName.SUN, longitude=10.0, speed=1.0)
    chart = Chart(sun_altitude=10.0, planets=[sun], ascendant=0.0, mc=270.0)

    mock_armc.return_value = (None, [10.0, 280.0])  # asc_dir = 10.0

    res = PrimaryDirectionsEngine.calculate_current_distributor(chart, 10.0, 45.0)
    assert res["type"] == "Distributor (Term Ruler)"
    assert res["directed_ascendant_deg"] == 10.0


@patch("swisseph.houses_armc")
def test_current_distributor_partner_is_last_directed_ray_not_present_orb(
    mock_armc, monkeypatch
):
    sun = Planet(name=PlanetName.SUN, longitude=10.0, speed=1.0)
    chart = Chart(sun_altitude=10.0, planets=[sun], ascendant=0.0, mc=270.0)
    mock_armc.return_value = (None, [25.0, 280.0])
    rays = [
        DirectionResult("Ascendant", "Venus", "Sextile", 5.0, 5.0, "5y 0m", "Configured zodiacal OA"),
        DirectionResult("Ascendant", "Mercury", "Conjunction", 19.4, 19.4, "19y 5m", "Configured zodiacal OA"),
        DirectionResult("Ascendant", "Mars", "Square", 35.0, 35.0, "35y 0m", "Configured zodiacal OA"),
    ]
    monkeypatch.setattr(
        PrimaryDirectionsEngine,
        "calculate_directions_to_angles",
        classmethod(lambda cls, chart, geo_lat, key="Ptolemy": rays),
    )

    res = PrimaryDirectionsEngine.calculate_current_distributor(
        chart, 30.0, 45.0
    )

    assert res["partner"] == "Mercury"
    assert "age 19.40" in res["partner_reason"]


@patch("swisseph.houses_armc")
def test_calculate_circumambulations(mock_armc):
    sun = Planet(name=PlanetName.SUN, longitude=10.0, speed=1.0)
    chart = Chart(sun_altitude=10.0, planets=[sun], ascendant=0.0, mc=270.0)

    # We always return ascendant at 10.0 (Aries)
    mock_armc.return_value = (None, [10.0, 280.0])

    res = PrimaryDirectionsEngine.calculate_circumambulations(chart, 45.0, max_years=5)
    assert len(res) == 6
    assert res[0]["age"] == 0
    assert res[0]["directed_asc_lon"] == 10.0
    assert res[0]["sign"] == "Aries"


@patch("swisseph.houses_armc")
def test_circumambulation_transitions_are_solved_between_year_samples(mock_armc):
    sun = Planet(name=PlanetName.SUN, longitude=10.0, speed=1.0)
    chart = Chart(sun_altitude=10.0, planets=[sun], ascendant=0.0, mc=270.0)

    # With MC at 270 RA, make the directed Ascendant advance one zodiacal
    # degree for each degree of RAMC. Aries changes from Jupiter to Venus at 6°.
    def houses_for_armc(armc, _lat, _epsilon, _system):
        return None, [((armc - 270.0) % 360.0), 0.0]

    mock_armc.side_effect = houses_for_armc

    result = PrimaryDirectionsEngine.calculate_circumambulations(
        chart, 45.0, max_years=8
    )
    transition = next(item for item in result if item["is_transition"])

    assert transition["age"] == 6
    assert abs(transition["exact_transition_age"] - 6.0) < 1e-5
    assert transition["bound_ruler"] == "Venus"


def test_calculate_directions_to_angles():
    # Promittor Jupiter at 100 degrees
    jup = Planet(name=PlanetName.JUPITER, longitude=100.0, speed=1.0)
    chart = Chart(sun_altitude=10.0, planets=[jup], ascendant=0.0, mc=270.0)

    # Very simplified chart
    res = PrimaryDirectionsEngine.calculate_directions_to_angles(chart, 0.0)

    assert len(res) > 0
    assert any(r.promittor == "Jupiter" for r in res)
    assert all(r.method == "Configured zodiacal OA" for r in res)


def test_calculate_directions_to_point():
    jup = Planet(name=PlanetName.JUPITER, longitude=100.0, speed=1.0)
    chart = Chart(sun_altitude=10.0, planets=[jup], ascendant=0.0, mc=270.0)

    res = PrimaryDirectionsEngine.calculate_directions_to_point(
        chart, 0.0, 10.0, target_label="Hyleg"
    )

    assert len(res) > 0
    assert all(r.significator == "Hyleg" for r in res)


def test_calculate_directions_to_planets():
    jup = Planet(name=PlanetName.JUPITER, longitude=100.0, speed=1.0)
    mars = Planet(name=PlanetName.MARS, longitude=50.0, speed=1.0)
    chart = Chart(sun_altitude=10.0, planets=[jup, mars], ascendant=0.0, mc=270.0)

    res = PrimaryDirectionsEngine.calculate_directions_to_planets(chart, 0.0)
    assert len(res) > 0
    assert (
        sum(1 for r in res if r.significator == "Mars" and r.promittor == "Jupiter") > 0
    )


def test_naibod_key():
    assert abs(PrimaryDirectionsEngine.naibod_key(0.9856) - 1.0) < 0.001
    assert abs(PrimaryDirectionsEngine.get_arc_from_years(1.0, key="Naibod") - 0.9856) < 0.001
    assert abs(PrimaryDirectionsEngine.get_years_from_arc(0.9856, key="Naibod") - 1.0) < 0.001
