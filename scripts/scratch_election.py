import os
import sys
import json
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
        hours_to_scan=336,
        start_dt=datetime(2026, 4, 24, 6, 0, 0)
    )
    for i, w in enumerate(results.get("best_windows", [])[:3]):
        print(f"WINDOW {i+1}: {w['start']} to {w['end']}")
        print(f"PEAK: {w['peak_time']} (Score: {w['peak_score']})")
        print(f"MOOD: {w.get('mood', '')}")
        for d in w.get('details', []):
            print(f"  - {d}")
        print("-" * 40)

if __name__ == "__main__":
    main()
