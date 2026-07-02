import pytest
from src.engine.models import Chart, Planet, PlanetName, Sect, Sign
from src.engine.bonatti import BonattiEngine

def test_void_of_course():
    # 1. Non-void moon: Moon at 10° Taurus applying to Conjunction with Mars at 15° Taurus
    moon = Planet(name=PlanetName.MOON, longitude=40.0, speed=13.0)  # 10° Taurus
    mars = Planet(name=PlanetName.MARS, longitude=45.0, speed=0.5)   # 15° Taurus
    planets = [moon, mars]
    
    voc_res = BonattiEngine.check_void_of_course(moon, planets)
    assert voc_res["is_void"] is False
    assert voc_res["voc_lilly"] is False

    # 2. Lilly Void moon: Moon at 28° Taurus applying to Conjunction with Mars at 5° Gemini
    # It must travel 7° to Mars, but leaves Taurus in 2°.
    moon_late = Planet(name=PlanetName.MOON, longitude=58.0, speed=13.0)  # 28° Taurus
    mars_gem = Planet(name=PlanetName.MARS, longitude=65.0, speed=0.5)   # 5° Gemini
    planets_late = [moon_late, mars_gem]
    
    voc_res2 = BonattiEngine.check_void_of_course(moon_late, planets_late)
    # Mitigated because Taurus is an alleviated sign!
    assert voc_res2["is_void"] is False
    assert voc_res2["voc_lilly"] is True
    assert voc_res2["is_alleviated"] is True

    # 3. Lilly Void Moon (not alleviated): Moon at 28° Aries, Mars at 5° Gemini
    moon_aries = Planet(name=PlanetName.MOON, longitude=28.0, speed=13.0)  # 28° Aries
    planets_aries = [moon_aries, mars_gem]
    voc_res3 = BonattiEngine.check_void_of_course(moon_aries, planets_aries)
    assert voc_res3["is_void"] is True
    assert voc_res3["voc_lilly"] is True
    assert voc_res3["is_alleviated"] is False

def test_combustion_cazimi():
    sun = Planet(name=PlanetName.SUN, longitude=120.0)  # 0° Leo
    
    # 1. Cazimi: planet within 17' of Sun (0.28 degrees)
    mercury_cazimi = Planet(name=PlanetName.MERCURY, longitude=120.1)
    res_cazimi = BonattiEngine.check_combustion_cazimi(mercury_cazimi, sun)
    assert res_cazimi["status"] == "CAZIMI"

    # 2. Combust: planet within 8.5 degrees of Sun
    mercury_combust = Planet(name=PlanetName.MERCURY, longitude=125.0)
    res_combust = BonattiEngine.check_combustion_cazimi(mercury_combust, sun)
    assert res_combust["status"] == "COMBUST"

    # 3. Under the Beams: planet within 15 degrees of Sun
    mercury_beams = Planet(name=PlanetName.MERCURY, longitude=132.0)
    res_beams = BonattiEngine.check_combustion_cazimi(mercury_beams, sun)
    assert res_beams["status"] == "UNDER_BEAMS"

    # 4. Free
    mercury_free = Planet(name=PlanetName.MERCURY, longitude=145.0)
    res_free = BonattiEngine.check_combustion_cazimi(mercury_free, sun)
    assert res_free["status"] == "FREE"

def test_planet_at_29_degrees():
    p_late = Planet(name=PlanetName.MARS, longitude=29.5)  # 29.5° Aries
    res_late = BonattiEngine.check_planet_at_29_degrees(p_late)
    assert res_late["active"] is True

    p_mid = Planet(name=PlanetName.MARS, longitude=15.0)  # 15.0° Aries
    res_mid = BonattiEngine.check_planet_at_29_degrees(p_mid)
    assert res_mid["active"] is False

def test_significator_in_ascendant():
    chart = Chart(sun_altitude=10.0, planets=[], ascendant=15.0)  # Ascendant in Aries
    
    # Significator in Aries
    p_asc = Planet(name=PlanetName.JUPITER, longitude=20.0)
    res = BonattiEngine.check_significator_in_ascendant(p_asc, chart)
    assert res["active"] is True

    # Significator in Taurus
    p_non_asc = Planet(name=PlanetName.JUPITER, longitude=45.0)
    res2 = BonattiEngine.check_significator_in_ascendant(p_non_asc, chart)
    assert res2["active"] is False

def test_lord_precedence():
    # Lord of Ascendant is Mars, Almuten is Jupiter
    res_body = BonattiEngine.check_lord_precedence(PlanetName.MARS, PlanetName.JUPITER, "body")
    assert res_body["precedent_ruler"] == PlanetName.MARS

    res_career = BonattiEngine.check_lord_precedence(PlanetName.MARS, PlanetName.JUPITER, "career")
    assert res_career["precedent_ruler"] == PlanetName.JUPITER

def test_malefics_in_angles():
    # Saturn in Aries (Ascendant) and Mars in Libra (Descendant)
    saturn = Planet(name=PlanetName.SATURN, longitude=10.0)
    mars = Planet(name=PlanetName.MARS, longitude=190.0)
    chart = Chart(sun_altitude=10.0, planets=[saturn, mars], ascendant=15.0)
    
    strictures = BonattiEngine.check_malefics_in_angles(chart)
    assert len(strictures) == 2
    assert any("Saturn in 1st House" in s["consideration"] for s in strictures)
    assert any("Mars in 7th House" in s["consideration"] for s in strictures)
