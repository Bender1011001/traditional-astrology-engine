import os
import sys
import json
from datetime import datetime

# Adjust path to include the project root
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT_DIR)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, ".env"))

from src.engine.forensic_engine import Auditor
from src.engine.chat_oracle import explain_reading_in_plain_terms

def run_full_reading(date_str, time_str, city, state):
    print(f"--- STARTING FULL READING FOR {date_str} {time_str} {city} ---")
    
    # 1. Generate Full Nativity (Technical + Synthesis)
    result = Auditor.generate_full_nativity(
        date_str=date_str,
        time_str=time_str,
        city=city,
        state=state,
        name="User"
    )
    
    if "error" in result:
        print(f"Audit Error: {result['error']}")
        return

    technical_data = result["technical_data"]
    
    # 2. Prepare Context for LLM
    planets_context = []
    for p in technical_data.get("planets_forensic", []):
        planets_context.append({
            "planet": p.get("name"),
            "sign": p.get("sign"),
            "power": p.get("power_label"),
            "delineation": p.get("delineation"),
            "impacts": [f"{i.get('cause')}: {i.get('effect')}" for i in (p.get("impacts") or [])[:3]]
        })

    context_json = json.dumps({
        "summary": technical_data.get("analysis", {}).get("teams"),
        "planets": planets_context,
        "lots": technical_data.get("analysis", {}).get("fate", {}).get("hermetic_lots"),
        "soul_guardian": technical_data.get("analysis", {}).get("advanced_mechanics", {}).get("almuten")
    }, indent=2)

    # 3. Call Multi-Turn Synthesis
    print("Calling LLM (Multi-Turn Interrogation Sequence with Gemini 3 Pro Preview)...")
    final_report = explain_reading_in_plain_terms(context_json, tier='paid')
    
    print("\n" + "="*50)
    print("FINAL SYNTHESIZED REPORT")
    print("="*50 + "\n")
    print(final_report)
    print("\n" + "="*50)

if __name__ == "__main__":
    run_full_reading("1996-08-13", "07:18", "Fairfield", "CA")
