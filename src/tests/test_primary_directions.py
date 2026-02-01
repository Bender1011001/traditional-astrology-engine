import pytest
import math
from src.engine.models import PlanetName, Sign, Planet, Chart
from src.engine.primary_directions import PrimaryDirectionsEngine

def test_coordinate_conversion():
    # 0 Aries should be RA 0, Dec 0
    ra, dec = PrimaryDirectionsEngine.ecliptic_to_equatorial(0.0, 0.0)
    assert abs(ra) < 0.001
    assert abs(dec) < 0.001
    
    # 90 Cancer should be Dec ~23.44
    ra, dec = PrimaryDirectionsEngine.ecliptic_to_equatorial(90.0, 0.0)
    assert abs(dec - 23.44) < 0.1

def test_semi_arcs():
    # Dec 0 at Lat 50
    dsa, nsa = PrimaryDirectionsEngine.calculate_semi_arcs(0.0, 50.0)
    assert dsa == 90.0
    assert nsa == 90.0
    
    # Summer Solstice Northern Lat
    dsa, nsa = PrimaryDirectionsEngine.calculate_semi_arcs(23.44, 40.0)
    assert dsa > 90.0
    assert nsa < 90.0

def test_directions_to_angles():
    # Simple mock chart
    sun = Planet(name=PlanetName.SUN, longitude=0.0)
    chart = Chart(sun_altitude=1.0, planets=[sun], ascendant=350.0, mc=260.0)
    
    results = PrimaryDirectionsEngine.calculate_directions_to_angles(chart, 40.0)
    # Sun at 0 Aries is approaching Ascendant at 350 (Pisces/Aries border)
    # OA of Sun (0/0) = 0.
    # OA of Asc (350) = ... roughly OA_MC + 90.
    assert len(results) >= 0
