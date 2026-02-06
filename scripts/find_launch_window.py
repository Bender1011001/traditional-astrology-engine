import os
import sys
import json
from datetime import datetime

# Adjust path to include the project root
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, ".env"))

from src.engine.electional import ElectionalEngine

def find_business_launch_window():
    """
    Pure electional timing - no LLM needed.
    The math speaks for itself.
    """
    print("=" * 60)
    print("  ELECTIONAL TIMING: BUSINESS LAUNCH WINDOWS")
    print("  Subject: Mercurial Sovereign (08/13/1996 Fairfield CA)")
    print("  Current Date: February 4, 2026")
    print("  Scanning: Next 336 hours (2 weeks)")
    print("  Activity: Mercantile/Business Launch")
    print("=" * 60)
    
    engine = ElectionalEngine()
    
    # Scan next 2 weeks from tomorrow morning
    start_dt = datetime(2026, 2, 5, 6, 0, 0)
    
    results = engine.find_kairos(
        start_dt=start_dt,
        city="Fairfield",
        state="CA",
        hours_to_scan=336,  # 2 weeks
        activity="mercantile"
    )
    
    print("\n" + "=" * 60)
    print("  TOP 5 LAUNCH WINDOWS (Sorted by Score)")
    print("=" * 60)
    
    for i, window in enumerate(results.get("best_windows", [])[:5], 1):
        print(f"\n{'='*60}")
        print(f"  WINDOW #{i}")
        print(f"{'='*60}")
        print(f"  Start Time: {window['start']}")
        print(f"  End Time:   {window['end']}")
        print(f"  Peak Moment: {window['peak_time']}")
        print(f"  Duration: {window['duration_hours']} hours")
        print(f"  Score: {window['peak_score']} | Mood: {window['mood']}")
        print(f"\n  Astrological Factors:")
        for detail in window.get('details', []):
            print(f"    • {detail}")
    
    # NATAL CONTEXT SYNTHESIS (Manual - no LLM)
    print("\n" + "=" * 60)
    print("  NATAL SYNCHRONIZATION (Your Chart)")
    print("=" * 60)
    print("""
  YOUR KEY FACTORS:
  • Almuten Figuris: Mercury in Virgo (27 pts)
  • Current Time Lord: Saturn Major → Mercury Sub (Oct 2025 - Jun 2027)
  • Mercury rules BOTH your Ascendant AND Midheaven
  • You are in the "Intellectual Bailout" window
  
  STRATEGIC RECOMMENDATION:
  ─────────────────────────────────────────────────────────────
  Given your Mercury-dominated chart, PRIORITIZE windows where:
  
  1. Mercury has positive Essential Dignity (+3 or higher)
  2. Moon is NOT Void of Course
  3. Ascendant Ruler is dignified or Cazimi
  4. Jupiter is angular (1st or 10th House)
  
  Your Saturn Return is ACTIVE. This means the 8th House (debt,
  restructuring) is under pressure. A business launch during the
  Mercury Sub-Period (now through June 2027) leverages your
  "Soul Guardian" to navigate the Saturnian restructuring.
  
  AVOID: Windows with Mercury Retrograde, Combust Moon, or
  Malefics (Mars/Saturn) on the Ascendant.
  ─────────────────────────────────────────────────────────────
    """)
    
    # Save to file
    output = {
        "query": results.get("query"),
        "best_windows": results.get("best_windows", [])[:5],
        "top_20_slots": results.get("raw_top_slots", [])[:20]
    }
    
    with open("chart_outputs/electional_launch_windows.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n  [Saved to chart_outputs/electional_launch_windows.json]")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    find_business_launch_window()
