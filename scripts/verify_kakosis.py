import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from engine.models import Planet, Chart, PlanetName, Sign, Sect
from engine.kakosis import KakosisEngine
from engine.decumbiture import DecumbitureEngine
import swisseph as swe

def mock_planet(name, lon, sign_val, speed=1.0):
    return Planet(name=name, longitude=lon, latitude=0, speed=speed, altitude=0)

def run_tests():
    print("=== KAKOSIS VERIFICATION ===")
    
    # 1. Test OVERCOMING (Dexter vs Sinister)
    # Planet: Moon at 0 Aries
    # Malefic A: Saturn at 0 Capricorn (10th Sign, Dexter) -> SHOULD OVERCOME
    # Malefic B: Mars at 0 Cancer (4th Sign, Sinister) -> SHOULD NOT OVERCOME (in this strict logic)
    
    moon = mock_planet(PlanetName.MOON, 0, Sign.ARIES)
    saturn = mock_planet(PlanetName.SATURN, 270, Sign.CAPRICORN) # 10th from Aries is Capricorn
    mars = mock_planet(PlanetName.MARS, 90, Sign.CANCER) # 4th from Aries is Cancer
    
    chart_dexter = Chart(sun_altitude=10, planets=[moon, saturn], ascendant=0, mc=270, geo_lat=51.5, geo_lon=0, jd=0, houses={})
    chart_sinister = Chart(sun_altitude=10, planets=[moon, mars], ascendant=0, mc=270, geo_lat=51.5, geo_lon=0, jd=0, houses={})
    
    res_dexter = KakosisEngine._check_overcoming(moon, chart_dexter, Sect.DAY)
    res_sinister = KakosisEngine._check_overcoming(moon, chart_sinister, Sect.DAY)
    
    print(f"Test 1 (Dexter Overcoming): Found {len(res_dexter)} conditions (Expect 1).")
    if res_dexter: print(f"  - {res_dexter[0].description}")
    
    print(f"Test 2 (Sinister Overcoming): Found {len(res_sinister)} conditions (Expect 0).")
    if res_sinister: print(f"  - {res_sinister[0].description}")
    
    # 2. Test ADHERENCE (Applying vs Separating)
    # Moon fast (13 deg/day), Saturn slow (0.1 deg/day)
    # Case A: Moon at 10 Aries, Saturn at 13 Aries. Moon chasing Saturn -> APPLYING.
    # Case B: Moon at 10 Aries, Saturn at 7 Aries. Moon leaving Saturn -> SEPARATING.
    
    moon_app = mock_planet(PlanetName.MOON, 10, Sign.ARIES, speed=13.0)
    saturn_tgt = mock_planet(PlanetName.SATURN, 13, Sign.ARIES, speed=0.1)
    
    chart_applying = Chart(sun_altitude=10, planets=[moon_app, saturn_tgt], ascendant=0, mc=0, geo_lat=0, geo_lon=0, jd=0, houses={})
    
    moon_sep = mock_planet(PlanetName.MOON, 10, Sign.ARIES, speed=13.0)
    saturn_past = mock_planet(PlanetName.SATURN, 7, Sign.ARIES, speed=0.1)
    
    chart_separating = Chart(sun_altitude=10, planets=[moon_sep, saturn_past], ascendant=0, mc=0, geo_lat=0, geo_lon=0, jd=0, houses={})
    
    res_app = KakosisEngine._check_adherence(moon_app, chart_applying, Sect.DAY)
    res_sep = KakosisEngine._check_adherence(moon_sep, chart_separating, Sect.DAY)
    
    print(f"Test 3 (Applying Adherence): Found {len(res_app)} conditions (Expect 1).")
    if res_app: print(f"  - {res_app[0].description}")

    print(f"Test 4 (Separating Adherence): Found {len(res_sep)} conditions (Expect 0).")
    if res_sep: print(f"  - {res_sep[0].description}")

    print("\n=== DECUMBITURE VERIFICATION ===")
    
    # Test Critical Days
    jd_now = swe.julday(2025, 1, 1, 12.0)
    days = DecumbitureEngine.calculate_critical_days(jd_now)
    
    print(f"Calculated {len(days)} Critical Day points.")
    if days:
        print(f"  - First Indication: {days[0]['label']} on {days[0]['date']}")
        print(f"  - First Crisis: {days[1]['label']} on {days[1]['date']}")
        
    # Test Distemper
    distemper = DecumbitureEngine.analyze_distemper(Sign.ARIES)
    print(f"Distemper for Aries Moon: {distemper['excess_humor']} (Expect Choleric)")

if __name__ == "__main__":
    run_tests()
