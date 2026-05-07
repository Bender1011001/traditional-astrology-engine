import os
import sys
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/.."
sys.path.insert(0, ROOT_DIR)

from src.engine.electional import ElectionalEngine

def main():
    engine = ElectionalEngine()
    
    results = engine.find_kairos(
        city="Vacaville",
        state="CA",
        activity="mercantile",
        hours_to_scan=24,
        start_dt=datetime(2026, 4, 24, 6, 0, 0)
    )
    
    print("ALL SLOTS FOR NEXT 24 HOURS:")
    for slot in results.get("raw_top_slots", []):
        print(f"{slot['time']} -> Score: {slot['score']} | Mood: {slot.get('mood', '')}")
        for d in slot.get('details', []):
            print(f"  - {d}")

if __name__ == "__main__":
    main()
