import pytest
from src.engine.models import PlanetName, Sign, Planet, Chart
from src.engine.advanced_mechanics import (
    HermeticLotEngine, MonomoiriaEngine, AlmutenEngine, 
    DoryphoryEngine, DodecatemoriaEngine
)

def create_mock_chart(is_day=True):
    # Sun at 10 Aries
    sun = Planet(name=PlanetName.SUN, longitude=10.0, altitude=1.0 if is_day else -1.0)
    # Moon at 20 Taurus
    moon = Planet(name=PlanetName.MOON, longitude=50.0)
    # Mercury at 0 Aries (Oriental, not combust)
    mercury = Planet(name=PlanetName.MERCURY, longitude=0.0)
    # Venus at 15 Gemini
    venus = Planet(name=PlanetName.VENUS, longitude=75.0)
    # Mars at 25 Cancer
    mars = Planet(name=PlanetName.MARS, longitude=115.0)
    # Jupiter at 5 Leo
    jupiter = Planet(name=PlanetName.JUPITER, longitude=125.0)
    # Saturn at 15 Virgo
    saturn = Planet(name=PlanetName.SATURN, longitude=165.0)
    
    planets = [sun, moon, mercury, venus, mars, jupiter, saturn]
    
    # Mock houses (Whole Sign for simplicity in tests unless needed otherwise)
    # Ascendant at 15 Aries
    asc = 15.0
    houses = {i: (asc + (i-1)*30) % 360 for i in range(1, 13)}
    
    return Chart(
        sun_altitude=sun.altitude,
        planets=planets,
        ascendant=asc,
        houses=houses,
        jd=2460000.5 # Arbitrary JD
    )

def test_hermetic_lots():
    chart = create_mock_chart(is_day=True)
    lots = HermeticLotEngine.calculate_all_lots(chart)
    
    # Day: Fortune = Asc + Moon - Sun = 15 + 50 - 10 = 55 (Taurus)
    assert lots["Fortune"]["longitude"] == 55.0
    assert lots["Fortune"]["sign"] == "Taurus"
    
    # Day: Spirit = Asc + Sun - Moon = 15 + 10 - 50 = -25 = 335 (Pisces)
    assert lots["Spirit"]["longitude"] == 335.0
    assert lots["Spirit"]["sign"] == "Pisces"
    
    # Night Reversal check
    chart_night = create_mock_chart(is_day=False)
    lots_night = HermeticLotEngine.calculate_all_lots(chart_night)
    
    # Night: Fortune = Asc + Sun - Moon = 335
    assert lots_night["Fortune"]["longitude"] == 335.0
    # Night: Spirit = Asc + Moon - Sun = 55
    assert lots_night["Spirit"]["longitude"] == 55.0

def test_monomoiria():
    # Aries: Mars (0), Sun (1), Ven (2), Mer (3), Moon (4), Sat (5), Jup (6)
    # Domicile of Aries is Mars.
    # Degree 0-1: Mars
    assert MonomoiriaEngine.get_zoidion_monomoiria(0.5) == PlanetName.MARS
    # Degree 1-2: Sun (Chaldean Descending from Mars: Mar -> Sun -> Ven -> Mer -> Moon -> Sat -> Jup)
    assert MonomoiriaEngine.get_zoidion_monomoiria(1.5) == PlanetName.SUN
    
    # Trigonal
    # Light in Aries (Fire). Day: Sun.
    assert MonomoiriaEngine.get_trigonal_monomoiria(0.5, True, Sign.ARIES, Sign.LEO) == PlanetName.SUN

def test_almuten_scoring():
    chart = create_mock_chart(is_day=True)
    # Mocking day/hour lords
    result = AlmutenEngine.calculate_almuten(chart, day_lord=PlanetName.SUN, hour_lord=PlanetName.VENUS)
    
    assert result.winner in [p for p in PlanetName]
    assert len(result.scores) == 7

def test_doryphory():
    chart = create_mock_chart(is_day=True)
    # Sun at 10, Mercury at 5. Mercury is Oriental (Preceding).
    guards = DoryphoryEngine.check_doryphory(chart)
    
    merc_guard = next((g for g in guards if g.planet == PlanetName.MERCURY and g.related_luminary == "Sun"), None)
    assert merc_guard is not None

def test_dodecatemoria():
    # 10 Aries. Degree 10.
    # Valens: 10 + 10*12 = 10 + 120 = 130 (Leo)
    lon_v = DodecatemoriaEngine.calculate_dodecatemoria_valens(10.0)
    assert lon_v == 130.0
    
    # Paul: 10 + 10*13 = 10 + 130 = 140 (Leo)
    lon_p = DodecatemoriaEngine.calculate_dodecatemoria_paul(10.0)
    assert lon_p == 140.0
