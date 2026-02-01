
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from engine.models import Chart, Planet, PlanetName, Sign
from engine.logic import perform_forensic_audit
from engine.advanced_mechanics import MonomoiriaEngine, DodecatemoriaEngine
from engine.horary import calculate_antiscia

def test_hidden_geometry():
    print("--- Testing Hidden Geometry & High-Precision Rulers ---")
    
    # Create a dummy chart for testing
    # Sun at 10.0 Aries (0.0 + 10.0)
    # Moon at 15.0 Cancer (90.0 + 15.0)
    # Mars at 10.0 Libra (180.0 + 10.0) - This is the Antiscia of 10.0 Aries (30 - 10 = 20 Pisces? No.)
    # Antiscia of 10 Aries (10 deg from 0 Aries) is 10 deg from 0 Libra? No.
    # Antiscia axis is 0 Cancer / 0 Capricorn.
    # 10 Aries is 80 degrees from 0 Cancer.
    # Mirror is 80 degrees on the other side: 90 + 80 = 170 (20 Virgo).
    # Wait, 0 Aries mirror is 0 Virgo? No.
    # 0 Aries (0) -> 0 Virgo (150)? No.
    # 0 Aries (0) -> 30 Virgo (180)? No.
    # Axis is 0 Cancer (90) and 0 Capricorn (270).
    # Mirror of L is 180 - L.
    # Mirror of 10 is 180 - 10 = 170 (20 Virgo).
    # Mirror of 0 Aries is 180 (0 Libra).
    # Mirror of 30 Aries is 150 (0 Virgo).
    
    sun = Planet(name=PlanetName.SUN, longitude=10.0, latitude=0, speed=0.98)
    moon = Planet(name=PlanetName.MOON, longitude=105.0, latitude=0, speed=13.1)
    mars = Planet(name=PlanetName.MARS, longitude=170.0, latitude=0, speed=0.5) # Antiscia of Sun
    saturn = Planet(name=PlanetName.SATURN, longitude=350.0, latitude=0, speed=0.03) # Contra-Antiscia of Sun?
    # Contra-Antiscia of 10 Aries is 180 + 170 = 350 (20 Pisces).
    
    chart = Chart(
        sun_altitude=10.0, # Day chart
        planets=[sun, moon, mars, saturn],
        ascendant=0.0,
        mc=270.0,
        houses={i: (i-1)*30 for i in range(1, 13)},
        geo_lat=51.5,
        geo_lon=0.0,
        jd=2451545.0
    )
    
    print("\n1. Testing Antiscia/Contra-Antiscia...")
    ant, cant = calculate_antiscia(10.0)
    print(f"Sun at 10.0 Aries -> Antiscia: {ant:.2f} (Expected 170.0), Contra-Antiscia: {cant:.2f} (Expected 350.0)")
    
    report = perform_forensic_audit(chart, jd=2451545.0)
    sun_data = next(p for p in report['planets'] if p['planet'] == 'Sun')
    
    impacts = [i['cause'] for i in sun_data['impacts']]
    print(f"Sun Impacts: {impacts}")
    assert "Antiscia" in impacts
    assert "Contra-Antiscia" in impacts
    
    print("\n2. Testing Monomoiria...")
    # 10.0 Aries. Domicile ruler is Mars.
    # Chaldean Descending: Sat, Jup, Mar, Sun, Ven, Mer, Moo
    # Degree 0-1: Mars
    # Degree 1-2: Sun
    # ...
    # Degree 10-11: (2 + 10) % 7 = 12 % 7 = 5. Index 5 is Mercury.
    # Wait, deg_in_sign = int(10.0 % 30) = 10.
    # start_idx (Mars) = 2.
    # current_idx = (2 + 10) % 7 = 5.
    # Index 5 in CHALDEAN_DESC is Mercury.
    mon = sun_data['classical']['monomoiria']
    print(f"Sun Monomoiria: {mon}")
    
    # Test Pure Intent hint
    # Mars at 180.0 (0 Libra). Domicile ruler is Venus.
    # Degree 0. start_idx (Venus) = 4. current_idx = (4 + 0) % 7 = 4. Ruler = Venus.
    # Should have hint.
    mars_data = next(p for p in report['planets'] if p['planet'] == 'Mars')
    print(f"Mars Monomoiria: {mars_data['classical']['monomoiria']}")
    if "hint" in mars_data['classical']['monomoiria']:
        print(f"Hint found: {mars_data['classical']['monomoiria']['hint']}")
    
    print("\n3. Testing Dodecatemoria...")
    # 10.0 Aries.
    # Valens: 10 + 10*12 = 130 (10 Leo).
    # Paul: 10 + 10*13 = 140 (20 Leo).
    dod = sun_data['classical']['dodecatemoria']
    print(f"Sun Dodecatemoria: {dod}")
    assert abs(dod['valens']['longitude'] - 130.0) < 0.1
    assert abs(dod['paul']['longitude'] - 140.0) < 0.1

    print("\n--- All Hidden Geometry Tests Passed ---")

if __name__ == "__main__":
    test_hidden_geometry()
