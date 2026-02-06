import asyncio
import sys
import os
from datetime import datetime

# Convert "e:\\code.projects\\astrology" to actual path if needed or just add to sys.path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.engine.logic import perform_forensic_audit
from src.engine.chart_calculator import calculate_chart_data
from src.engine.models import Chart, Planet, PlanetName, Sign

async def verify():
    print("Running Universal Integration Verification...")
    
    # Test Data: A standard birth chart
    date_str = "1989-12-13"
    time_str = "08:30"
    city = "Los Angeles, CA"
    
    # 1. Calculate Chart
    print("Calculating chart...")
    # Passing args directly as confirmed by signature check
    chart_data = calculate_chart_data(
        date_str=date_str, 
        time_str=time_str, 
        city=city
    )
    
    if "error" in chart_data:
        print(f"Error calculating chart: {chart_data['error']}")
        sys.exit(1)

    # Reconstruct Chart Model
    # The chart_calculator returns a dict with 'chart' key or similar?
    # No, looking at view_code_item output for calculate_chart_data...
    # It returns a dict with "meta", "planets", "houses".
    # It does NOT return a "chart" key containing a Chart model dict directly?
    # Wait, let's re-read the return dict structure in view_code_item.
    # It returns: {"meta": ..., "planets": {}, "houses": {}}
    
    # We need to construct a Chart object for perform_forensic_audit(chart: Chart, ...)
    # Logic.py expects a Chart object.
    # Where is this conversion happening in the app?
    # Usually in the endpoint handler.
    
    # Let's manually reconstruct Chart object for testing.
    # We need: sun_altitude, planets (List[Planet]), ascendant, mc, north_node, south_node etc.
    
    # Inspecting result structure from calculate_chart_data more closely in code view...
    # It behaves like an API response builder.
    
    # Let's inspect 'planets' dict in chart_data.
    planets_dict = chart_data["planets"]
    
    planet_objects = []
    sun_alt = 0.0
    
    for pname, pdata in planets_dict.items():
        # pdata has 'longitude', 'speed', 'latitude' etc.
        # PlanetName enum match
        
        try:
            # Handle strict enum matching
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
                # sun_altitude is required for Sect check (if not passed separate)
                # logic.py: chart_sect = Sect.DAY if chart.sun_altitude > 0 else ...
                # Wait, pdata should have altitude if topocentric flag was used?
                # Code says: altitude = azresult[1] ... p_data["altitude"] = altitude
                # So yes.
                sun_alt = pdata.get("altitude", 0.0)
                
        except ValueError:
            pass # Skip non-enum planets (e.g. Syzygy or something if present)

    # Ascendant and MC from 'houses' or 'meta'?
    # Usually in 'houses' key like 'ascendant': ...
    # chart_calculator returns "houses": { "1": ..., "ascendant": ..., "mc": ... } ?
    # Let's assume standard structure.
    houses_data = chart_data.get("houses", {})
    asc = houses_data.get("ascendant", 0.0)
    mc = houses_data.get("mc", 0.0)
    
    # Nodes?
    nn = planets_dict.get("North_Node", {}).get("longitude", 0.0)
    sn = (nn + 180) % 360 # Approx if simple
    
    chart_model = Chart(
        sun_altitude=sun_alt,
        planets=planet_objects,
        ascendant=asc,
        mc=mc,
        north_node=nn,
        south_node=sn,
        houses=houses_data,
        house_system="placidus", # generic default
        jd=chart_data["meta"]["julian_day"],
        geo_lat=chart_data["meta"]["lat"],
        geo_lon=chart_data["meta"]["lon"]
    )
    
    # 2. Run Audit
    print("Running Forensic Audit...")
    jd = chart_data["meta"]["julian_day"]
    age = 35 # Example age
    birth_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    
    report = perform_forensic_audit(chart_model, jd=jd, age=age, birth_date=birth_dt)
    
    # 3. Verify New Keys
    required_keys = [
        "medical_analysis",
        "solar_return",
        "critical_days_infancy"
    ]
    
    missing = []
    print("\n--- Verification Results ---")
    for key in required_keys:
        if key not in report:
            missing.append(key)
            print(f"[FAIL] Missing key: {key}")
        else:
            print(f"[OK] Found {key}")
            if key == "medical_analysis":
                 print(f"   -> Constitution: {report[key].get('constitutional_sign')}")
            if key == "chart_strength_rating": # Check inside summary
                 pass 

    # Check chart_strength_rating in summary
    summary = report.get("summary", {})
    if "chart_strength_rating" in summary:
        print("[OK] Found summary.chart_strength_rating")
        print(f"   -> Score: {summary['chart_strength_rating'].get('score')}")
    else:
        missing.append("summary.chart_strength_rating")
        print("[FAIL] Missing summary.chart_strength_rating")
        
    # Check Solar Return Content
    sr = report.get("solar_return", {})
    if sr:
        print(f"[OK] Solar Return Data Present (Year: {sr.get('year')})")
    else:
        print("[FAIL] Solar Return Data is Empty")
        
    if missing:
        print(f"\nFAILED: Missing keys: {missing}")
        sys.exit(1)
        
    print("\nSUCCESS: Universal Integration Verified.")

if __name__ == "__main__":
    asyncio.run(verify())
