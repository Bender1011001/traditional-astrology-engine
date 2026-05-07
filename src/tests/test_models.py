
from src.engine.models import Planet, PlanetName, Sign


def test_planet_sign_calculation():
    # 0 degrees = Aries
    p = Planet(name=PlanetName.SUN, longitude=0.0)
    assert p.sign == Sign.ARIES
    assert p.degree_in_sign == 0.0

    # 35 degrees = Taurus 5
    p = Planet(name=PlanetName.MOON, longitude=35.0)
    assert p.sign == Sign.TAURUS
    assert abs(p.degree_in_sign - 5.0) < 0.001

    # 359 degrees = Pisces 29
    p = Planet(name=PlanetName.SATURN, longitude=359.0)
    assert p.sign == Sign.PISCES
    assert abs(p.degree_in_sign - 29.0) < 0.001


def test_planet_is_retrograde():
    # Normal motion
    p = Planet(name=PlanetName.MERCURY, longitude=100.0, speed=1.5)
    assert not p.is_retrograde

    # Retrograde motion
    p = Planet(name=PlanetName.MERCURY, longitude=100.0, speed=-0.5)
    assert p.is_retrograde

    # Stationary (speed 0)
    p = Planet(name=PlanetName.MERCURY, longitude=100.0, speed=0.0)
    assert not p.is_retrograde


def test_planet_defaults():
    p = Planet(name=PlanetName.MARS, longitude=180.0)
    assert p.latitude == 0.0
    assert p.speed == 0.0
    assert p.is_visible is True
