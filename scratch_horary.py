import sys
import os
import json

# Ensure src is in path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from src.engine.calculator.main import calculate_chart_data
from src.engine.horary import build_horary_oracle
from src.api.v1.utils import result_to_model

def main():
    question = "When is the next best time to submit my patent application?"
    city = "Fairfield"
    state = "CA"
    
    # Coordinates for Fairfield, CA
    lat = 38.2493581
    lon = -122.039966
    
    # Target date/time
    date_str = "2026-04-28"
    time_str = "12:00"
    
    # Calculate Chart with Regiomontanus (R) for Horary
    res = calculate_chart_data(
        date_str, 
        time_str, 
        city, 
        state, 
        latitude=lat, 
        longitude=lon,
        house_system="R"
    )
    
    if "error" in res:
        print(f"Error calculating chart: {res['error']}")
        return

    # Convert to Chart model
    chart_model = result_to_model(res)
    
    # Build Horary Oracle Output
    oracle = build_horary_oracle(question, chart_model)
    
    with open('horary_answer_utf8.json', 'w', encoding='utf-8') as f:
        json.dump(oracle, f, indent=2)

if __name__ == "__main__":
    main()
