import swisseph as swe
from src.engine.chart_calculator import calculate_chart_data

def test_phasis():
    # 1996 Fairfield Case
    result = calculate_chart_data('1996-08-13', '07:18', 'Fairfield', 'CA')
    
    print("\n--- Planetary Phasis Verification ---")
    planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    
    for p in planets:
        if p in result["planets"]:
            data = result["planets"][p]["classical"].get("phasis", {})
            print(f"{p:8}: Phase={str(data.get('phase')):20} Prox={str(data.get('solar_proximity')):15} Vis={data.get('is_visible')}")

if __name__ == "__main__":
    test_phasis()
