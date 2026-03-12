import sys
import os
import json
from datetime import datetime, date
from dataclasses import is_dataclass, asdict
import swisseph as swe

# Add src to path
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load .env manually
def load_dotenv(path):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env')))

from src.engine.calculator.main import calculate_chart_data
from src.engine.logic import perform_forensic_audit
from src.engine.models import Chart, Planet, PlanetName
from src.engine.forensic_forecast import calculate_5_day_forecast
from src.engine.prediction import AdvancedPredictionEngine

def result_to_model(res):
    model_planets = []
    sun_alt = 0.0
    for name, data in res.get("planets", {}).items():
        try:
            p_enum = PlanetName(name)
        except ValueError:
            continue
        model_planets.append(
            Planet(
                name=p_enum,
                longitude=data["longitude"],
                latitude=data.get("latitude", 0.0),
                speed=data.get("speed", 0.0),
                altitude=data.get("altitude", 0.0)
            )
        )
        if name == "Sun":
            sun_alt = data.get("altitude", 0.0)

    angles = res.get("angles", {})
    return Chart(
        sun_altitude=sun_alt,
        planets=model_planets,
        ascendant=angles.get("Ascendant", 0.0),
        mc=angles.get("MC", 0.0),
        north_node=res.get("planets", {}).get("North_Node", {}).get("longitude", 0.0),
        south_node=res.get("planets", {}).get("South_Node", {}).get("longitude", 0.0),
        geo_lat=res.get("meta", {}).get("lat"),
        geo_lon=res.get("meta", {}).get("lon"),
        jd=res.get("meta", {}).get("julian_day"),
        houses=res.get("houses"),
        house_system=(res.get("meta", {}).get("house_system") or {}).get("code")
    )

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if is_dataclass(obj):
        return asdict(obj)
    if hasattr(obj, 'value'): # Enum
        return obj.value
    raise TypeError (f"Type {type(obj)} not serializable")

def main():
    # User provided data
    date_str = "1996-08-13"
    time_str = "07:18"
    city = "Fairfield"
    state = "CA"
    
    print(f"Calculating chart for {date_str} {time_str} in {city}, {state}...")
    
    result = calculate_chart_data(
        date_str,
        time_str,
        city,
        state
    )
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return

    chart_model = result_to_model(result)
    
    jd = result["meta"]["julian_day"]
    birth_date = datetime.strptime(date_str, "%Y-%m-%d")
    
    # Current date for analysis: 2026-02-08
    now = datetime(2026, 2, 8, 13, 50) 
    
    age = now.year - birth_date.year - ((now.month, now.day) < (birth_date.month, birth_date.day))
    
    analysis_jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0)
    
    print(f"Performing forensic audit (Age: {age})...")
    
    audit_report = perform_forensic_audit(
        chart_model, 
        jd, 
        age=age, 
        month=now.month, 
        day=now.day, 
        birth_date=birth_date, 
        analysis_date=now, 
        analysis_jd=analysis_jd
    )

    # PAID FEATURES
    print("Calculating 5-Day Forecast (Paid)...")
    try:
        forecast_data = calculate_5_day_forecast(chart_model, jd, now)
        audit_report["forensic_forecast"] = forecast_data
    except Exception as e:
        print(f"Forecast Error: {e}")
        audit_report["forensic_forecast_error"] = str(e)
    
    print("Calculating Advanced Prediction (Paid)...")
    predictor = None
    try:
        predictor = AdvancedPredictionEngine(
            chart_model,
            birth_date,
            jd,
            result["meta"]["lat"],
            result["meta"]["lon"]
        )
        prediction_report = predictor.get_prediction_report(now)
        audit_report["advanced_prediction"] = prediction_report
    except Exception as e:
        print(f"Advanced Prediction Error: {e}")
        audit_report["advanced_prediction_error"] = str(e)
        
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../specific_reading_output.json'))
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(audit_report, f, default=json_serial, indent=2)
        
    print(f"Reading saved to {output_path}")

if __name__ == "__main__":
    main()
