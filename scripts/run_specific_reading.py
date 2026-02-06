import asyncio
import sys
import os
import json
from datetime import datetime

# Setup paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.engine.logic import perform_forensic_audit
from src.engine.chart_calculator import calculate_chart_data
from src.engine.models import Chart, Planet, PlanetName, Sign
from enum import Enum

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

async def run_reading():
    # User Inputs
    date_str = "1996-08-13"
    time_str = "07:18"
    city = "Fairfield"
    state = "CA"
    
    print(f"--- Running Universal Reading for {date_str} {time_str} at {city}, {state} ---")
    
    # 1. Calculate Chart
    chart_data = calculate_chart_data(
        date_str=date_str, 
        time_str=time_str, 
        city=city,
        state=state
    )
    
    if "error" in chart_data:
        print(f"Error: {chart_data['error']}")
        return

    # 2. Reconstruct Chart Model
    planets_dict = chart_data["planets"]
    planet_objects = []
    sun_alt = 0.0
    
    for pname, pdata in planets_dict.items():
        try:
            p_enum = PlanetName(pname)
            p_obj = Planet(
                name=p_enum,
                longitude=pdata["longitude"],
                latitude=pdata.get("latitude", 0.0),
                speed=pdata.get("speed", 0.0),
                altitude=pdata.get("altitude", 0.0)
            )
            planet_objects.append(p_obj)
            if p_enum == PlanetName.SUN:
                sun_alt = pdata.get("altitude", 0.0)
        except ValueError:
            pass

    houses_data = chart_data.get("houses", {})
    chart_model = Chart(
        sun_altitude=sun_alt,
        planets=planet_objects,
        ascendant=houses_data.get("ascendant", 0.0),
        mc=houses_data.get("mc", 0.0),
        north_node=planets_dict.get("North_Node", {}).get("longitude", 0.0),
        south_node=(planets_dict.get("North_Node", {}).get("longitude", 0.0) + 180) % 360,
        houses=houses_data,
        jd=chart_data["meta"]["julian_day"],
        geo_lat=chart_data["meta"]["lat"],
        geo_lon=chart_data["meta"]["lon"]
    )
    
    # 3. Perform Forensic Audit
    # age = Current age (approx 29)
    report = perform_forensic_audit(
        chart_model, 
        jd=chart_data["meta"]["julian_day"], 
        age=29, 
        birth_date=datetime(1996, 8, 13, 7, 18)
    )
    
    # 4. Output Integrated Results
    print("\n[UNIVERSAL INTEGRATION RESULTS]")
    
    print("\n1. MEDICAL ANALYSIS (Constitution)")
    med = report.get("medical_analysis", {})
    print(f"   Sign: {med.get('constitutional_sign')}")
    print(f"   Governed Body Part: {med.get('governed_body_part')}")
    print(f"   Humoral Distemper: {med.get('distemper')}")
    
    print("\n2. CHART STRENGTH (Electional Rooting)")
    strength = report.get("summary", {}).get("chart_strength_rating", {})
    print(f"   Score: {strength.get('score')}/100")
    print(f"   Mood: {strength.get('mood')}")
    print(f"   Key Detail: {strength.get('details', ['N/A'])[0] if strength.get('details') else 'N/A'}")
    
    print("\n3. SOLAR RETURN (Age 29)")
    sr = report.get("solar_return", {})
    if sr:
        print(f"   Solar Return Year: {sr.get('year')}")
        print(f"   Lord of the Year: {sr.get('lord_of_year', {}).get('planet')}")
        print(f"   Condition: {sr.get('lord_of_year', {}).get('condition')}")
        print(f"   Muntha Sign: {sr.get('muntha', {}).get('sign')}")
    else:
        print("   No SR data found.")

    print("\n4. VITALITY CRISES (Infancy Decumbiture)")
    critical = report.get("critical_days_infancy", [])
    if critical:
        first = critical[0]
        print(f"   First Moon Crisis: {first.get('date')} ({first.get('phase')})")
    
    print(f"\nFinal report generation successful.")

if __name__ == "__main__":
    asyncio.run(run_reading())
