
from src.engine.horary import (check_besiegement, check_strictures,
                               check_void_of_course_hellenistic)
from src.engine.models import Chart, Planet, PlanetName


def test_void_of_course_hellenistic():
    # Hellenistic moon requires an EXACT aspect within 30 degrees.
    moon = Planet(name=PlanetName.MOON, longitude=15.0, speed=13.0)

    # Planet at 40 degrees. Moon is at 15. Distance is 25.
    # Moon applies by conjunction (0 deg aspect) if within 30.
    p_close = Planet(name=PlanetName.VENUS, longitude=40.0, speed=1.2)
    chart1 = Chart(sun_altitude=10, planets=[moon, p_close], ascendant=0)

    # Not void of course, since 40 - 15 = 25 degrees away, which is <= 30
    assert check_void_of_course_hellenistic(moon, chart1) is False

    # Planet at 55 degrees. Distance to conjunction is 40. > 30 degrees.
    p_far = Planet(name=PlanetName.VENUS, longitude=55.0, speed=1.2)
    chart2 = Chart(sun_altitude=10, planets=[moon, p_far], ascendant=0)

    # Void of course, no aspects within 30 degrees.
    assert check_void_of_course_hellenistic(moon, chart2) is True


def test_besiegement():
    # Planet between Mars and Saturn
    p = Planet(name=PlanetName.VENUS, longitude=20.0, speed=1.0)
    mars = Planet(name=PlanetName.MARS, longitude=15.0, speed=0.5)
    saturn = Planet(name=PlanetName.SATURN, longitude=25.0, speed=0.2)
    sun = Planet(name=PlanetName.SUN, longitude=100.0, speed=1.0)

    chart = Chart(sun_altitude=10, planets=[mars, p, saturn, sun], ascendant=0)
    result = check_besiegement(p, chart)

    assert result is not None
    assert result["condition"] == "Besiegement by Malefics"


def test_besiegement_benefics():
    # Planet between Jupiter and Venus
    p = Planet(name=PlanetName.MOON, longitude=20.0, speed=13.0)
    jupiter = Planet(name=PlanetName.JUPITER, longitude=15.0, speed=0.1)
    venus = Planet(name=PlanetName.VENUS, longitude=25.0, speed=1.2)
    sun = Planet(name=PlanetName.SUN, longitude=100.0, speed=1.0)

    chart = Chart(sun_altitude=10, planets=[jupiter, p, venus, sun], ascendant=0)
    result = check_besiegement(p, chart)

    assert result is not None
    assert result["condition"] == "Besiegement by Benefics"


def test_strictures():
    # Test early ascendant
    moon = Planet(name=PlanetName.MOON, longitude=10.0, speed=13.0)
    chart_early = Chart(sun_altitude=10, planets=[moon], ascendant=2.0)
    s = check_strictures(chart_early)
    assert any("Ascendant in early degrees" in x for x in s)

    # Test late ascendant
    chart_late = Chart(sun_altitude=10, planets=[moon], ascendant=28.0)
    s2 = check_strictures(chart_late)
    assert any("Ascendant in late degrees" in x for x in s2)

    # Test Saturn in 1st
    sat = Planet(name=PlanetName.SATURN, longitude=15.0, speed=0.0)
    chart_sat = Chart(sun_altitude=10, planets=[moon, sat], ascendant=10.0)
    s3 = check_strictures(chart_sat)
    assert any("Saturn in 1st" in x for x in s3)
