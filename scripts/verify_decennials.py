import swisseph as swe
from src.engine.chart_calculator import calculate_chart_data
from src.engine.forensic_engine import Auditor
from src.engine.decennials import DecennialEngine
from datetime import datetime

def test_decennials():
    # 1996 Fairfield Case
    # Birth: 1996-08-13 07:18 Fairfield, CA
    # Day Chart. Sun in Leo (12th in Whole Sign if Asc is Leo, but let's check).
    # Fairfield CA @ 07:18. Asc is approximately late Leo.
    
    raw_data = calculate_chart_data('1996-08-13', '07:18', 'Fairfield', 'CA')
    chart = Auditor._rebuild_chart_model(raw_data)
    
    print("\n--- Hellenistic Decennials Verification ---")
    apheta = DecennialEngine.select_apheta(chart)
    print(f"Apheta Selected: {apheta.name.value} at {apheta.longitude:.2f}°")
    
    # Generate Sequence
    seq = DecennialEngine.get_zodiacal_sequence(chart)
    print("Zodiacal sequence from Ascendant:")
    for p in seq:
        print(f"  - {p.name.value:8}: {p.longitude:.2f}°")
        
    # Generate Periods
    birth_dt = datetime.fromisoformat(raw_data["meta"]["utc_time"]).replace(tzinfo=None)
    decennials = DecennialEngine.generate_decennials(chart, birth_dt)
    
    print("\nGeneral Periods (Level 1):")
    for main in decennials:
        print(f"Lord: {main['major_lord']:8} | Start: {main['start_date'][:10]} | End: {main['end_date'][:10]}")
        
    print("\nSub-Periods (Level 2) for first Major Period:")
    if decennials:
        for sub in decennials[0]["sub_periods"]:
            print(f"  Sub: {sub['sub_lord']:8} | Start: {sub['start_date'][:10]} | End: {sub['end_date'][:10]}")

if __name__ == "__main__":
    test_decennials()
