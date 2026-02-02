from src.engine.chart_calculator import ChartCalculator
from src.engine.logic import perform_forensic_audit, Sect
from src.engine.models import Chart, Planet, PlanetName, Sign
from datetime import datetime
import json

def test_napoleon():
    # Napoleon: Aug 15, 1769, 11:30 AM, Ajaccio, France
    # Latitude: 41.9267, Longitude: 8.7369
    calc = ChartCalculator()
    jd = calc.get_jd(1769, 8, 15, 11.5)
    chart_data = calc.calculate_chart(jd, 41.9267, 8.7369)
    
    # Forensic Audit at age 30 (1799)
    analysis_date = datetime(1799, 8, 15)
    audit = perform_forensic_audit(chart_data, jd=jd, age=30, birth_date=datetime(1769, 8, 15))
    
    # Extract key values
    results = {
        "name": "Napoleon Bonaparte",
        "ascendant": chart_data.ascendant,
        "mc": chart_data.mc,
        "lord_of_year_age_30": audit.get("profections", {}).get("lord_of_year"),
        "almuten_figuris": audit.get("soul_guardian", {}).get("almuten"),
        "hyleg": audit.get("vitality", {}).get("hyleg")
    }
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    test_napoleon()
