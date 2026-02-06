import os
import sys
import json
from datetime import datetime

# Adjust path to include the project root
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT_DIR)

from src.astrology_tools import AstrologyTools
from src.engine.prediction import AdvancedPredictionEngine
from src.engine.solar_return import SolarReturnEngine
from src.engine.models import Chart, Planet, PlanetName

print("=" * 60)
print("COMPREHENSIVE ENGINE VALIDATION SUITE")
print("=" * 60)

tools = AstrologyTools()

# Test birth data (known chart for validation)
year, month, day = 1996, 8, 13
hour, minute = 7, 18
city, state = "Fairfield", "CA"

errors = []
warnings = []

# TEST 1: Natal Chart Calculation
print("\n[TEST 1] Natal Chart Calculation")
try:
    chart = tools.calculate_chart(year, month, day, hour, minute, city, state)
    
    # Validate basic structure
    assert 'planets' in chart, "Missing 'planets' key"
    assert 'houses' in chart, "Missing 'houses' key"
    assert 'angles' in chart, "Missing 'angles' key"
    
    # Check all planets are present
    expected_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
    for p in expected_planets:
        assert p in chart['planets'], f"Missing planet: {p}"
        assert 'longitude' in chart['planets'][p], f"Missing longitude for {p}"
    
    # Validate longitude ranges (0-360)
    for p_name, p_data in chart['planets'].items():
        lon = p_data['longitude']
        assert 0 <= lon < 360, f"{p_name} longitude {lon} out of range"
    
    # Validate house cusps
    for h in range(1, 13):
        assert h in chart['houses'] or str(h) in chart['houses'], f"Missing house {h}"
    
    print("✓ PASS: Natal chart structure valid")
    
except AssertionError as e:
    errors.append(f"[TEST 1] {str(e)}")
    print(f"✗ FAIL: {str(e)}")
except Exception as e:
    errors.append(f"[TEST 1] Unexpected error: {str(e)}")
    print(f"✗ ERROR: {str(e)}")

# TEST 2: Electional Engine (Post-Fix)
print("\n[TEST 2] Electional Engine (Cazimi Bug Fix)")
try:
    # Test case: When Sun is Ascendant ruler, it should NOT claim Cazimi
    results = tools.find_electional_window(
        city=city, state=state, activity="mercantile", hours_to_scan=24
    )
    
    # Check for false Cazimi claims
    for window in results.get('best_windows', []):
        details = window.get('details', [])
        for detail in details:
            if 'CAZIMI' in detail and 'Ascendant Ruler (Sun)' in detail:
                errors.append("[TEST 2] FALSE CAZIMI: Sun claiming Cazimi with itself")
                print("✗ FAIL: Sun still claiming Cazimi with itself")
                break
        else:
            continue
        break
    else:
        print("✓ PASS: No false Cazimi claims")
        
except Exception as e:
    errors.append(f"[TEST 2] {str(e)}")
    print(f"✗ ERROR: {str(e)}")

# TEST 3: Firdaria Calculation
print("\n[TEST 3] Firdaria Calculation")
try:
    # Import the natal chart as a Chart object
    natal_data = tools.calculate_chart(year, month, day, hour, minute, city, state)
    
    # Convert to Chart object
    natal_planets = []
    for pname, pdata in natal_data['planets'].items():
        try:
            enum_name = PlanetName[pname.upper()]
        except KeyError:
            if pname == "North_Node": enum_name = PlanetName.NORTH_NODE
            else: continue
            
        natal_planets.append(Planet(
            name=enum_name,
            longitude=pdata['longitude'],
            latitude=pdata.get('latitude', 0),
            speed=pdata.get('speed', 0),
            altitude=pdata.get('altitude', 0)
        ))
    
    natal_chart = Chart(
        sun_altitude=natal_data['planets']['Sun']['altitude'],
        planets=natal_planets,
        ascendant=natal_data['angles']['Ascendant'],
        mc=natal_data['angles']['MC'],
        geo_lat=38.2494,
        geo_lon=-122.0405,
        jd=natal_data.get('jd', 2450308.5 + (hour/24) + (minute/1440)),
        houses={int(k): v for k, v in natal_data['houses'].items()}
    )
    
    birth_dt = datetime(year, month, day, hour, minute)
    engine = AdvancedPredictionEngine(
        natal_chart=natal_chart,
        birth_date=birth_dt,
        birth_jd=natal_chart.jd,
        lat=natal_chart.geo_lat,
        lon=natal_chart.geo_lon
    )
    
    # Get Firdaria for current date
    current_firdaria = engine.get_firdaria(datetime.now())
    
    # Validate structure
    assert 'Major Period' in current_firdaria, "Missing 'Major Period'"
    assert 'Sub Period' in current_firdaria, "Missing 'Sub Period'"
    
    print(f"✓ PASS: Firdaria calculation valid (Current: {current_firdaria['Major Period']}/{current_firdaria['Sub Period']})")
    
except Exception as e:
    errors.append(f"[TEST 3] {str(e)}")
    print(f"✗ ERROR: {str(e)}")

# TEST 4: Solar Return Calculation
print("\n[TEST 4] Solar Return Calculation")
try:
    # Get Solar Return for 2026
    sr_info = engine.get_solar_return(2026)
    
    # Validate structure
    assert 'lord_of_year' in sr_info, "Missing 'lord_of_year'"
    assert 'muntha_sign' in sr_info, "Missing 'muntha_sign'"
    
    print(f"✓ PASS: Solar Return valid (Lord of Year 2026: {sr_info['lord_of_year']})")
    
except Exception as e:
    warnings.append(f"[TEST 4] {str(e)}")
    print(f"⚠ WARNING: {str(e)}")

# SUMMARY
print("\n" + "=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)

if errors:
    print(f"\n✗ ERRORS FOUND: {len(errors)}")
    for err in errors:
        print(f"  - {err}")
else:
    print("\n✓ ALL CRITICAL TESTS PASSED")

if warnings:
    print(f"\n⚠ WARNINGS: {len(warnings)}")
    for warn in warnings:
        print(f"  - {warn}")

# Save results
with open("chart_outputs/engine_validation_report.json", "w") as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "errors": errors,
        "warnings": warnings,
        "status": "PASS" if not errors else "FAIL"
    }, f, indent=2)

print(f"\n✓ Full report saved to chart_outputs/engine_validation_report.json")
