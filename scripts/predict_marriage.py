import os
import sys
import json
from datetime import datetime, timedelta

# Adjust path to include the project root
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT_DIR)

from src.astrology_tools import AstrologyTools
from src.engine.models import Chart, Planet, PlanetName, Sign, Sect
from src.engine.prediction import AdvancedPredictionEngine, calculate_profection_sign
from src.engine.solar_return import SolarReturnEngine

def predict_marriage_timing():
    tools = AstrologyTools()
    
    # Birth Data
    year, month, day = 1996, 8, 13
    hour, minute = 7, 18
    city, state = "Fairfield", "CA"
    birth_dt = datetime(year, month, day, hour, minute)
    
    # Get Natal Chart
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
        geo_lat=38.2494, # Fairfield approx
        geo_lon=-122.0405, # Fairfield approx
        jd=natal_data.get('jd', 2450308.5 + (hour/24) + (minute/1440)), # Fallback approx
        houses={int(k): v for k, v in natal_data['houses'].items()}
    )
    
    engine = AdvancedPredictionEngine(
        natal_chart=natal_chart,
        birth_date=birth_dt,
        birth_jd=natal_chart.jd,
        lat=natal_chart.geo_lat,
        lon=natal_chart.geo_lon
    )
    
    timeline = []
    
    # Scan from 2026 to 2032
    for target_year in range(2026, 2033):
        target_date = datetime(target_year, 8, 14) # Just after birthday
        age = target_year - 1996
        
        # 1. Profection
        asc_sign = natal_chart.planets[0].sign # Rough find, let's calculate from asc deg
        asc_sign = list(Sign)[int(natal_chart.ascendant / 30) % 12]
        profection_sign = calculate_profection_sign(asc_sign, age)
        
        # 2. Firdaria
        firdaria = engine.get_firdaria(target_date)
        
        # 3. Solar Return Summary
        sr_info = engine.get_solar_return(target_year)
        
        # 4. Detailed SR Analysis for key years
        # If age is 30 (2026) or 32 (2028), or Lord of Year is Jupiter/Venus
        loy = profection_sign.name
        is_marriage_year = False
        if profection_sign in [Sign.PISCES, Sign.SAGITTARIUS, Sign.LIBRA, Sign.TAURUS]:
            is_marriage_year = True
            
        summary = {
            "year": target_year,
            "age": age,
            "profection_sign": profection_sign.value,
            "lord_of_year": firdaria['Sub Period'],
            "firdaria_major": firdaria['Major Period'],
            "firdaria_minor": firdaria['Sub Period'],
            "is_marriage_sensitive": is_marriage_year
        }
        timeline.append(summary)
        
    with open("chart_outputs/marriage_timeline_analysis.json", "w") as f:
        json.dump(timeline, f, indent=2)

if __name__ == "__main__":
    predict_marriage_timing()
