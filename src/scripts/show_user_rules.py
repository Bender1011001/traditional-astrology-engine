import sys
import os
import json

# Setup paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.engine.forensic_engine import Auditor

def show_rules():
    print("DEBUG: Connecting to Local/Sqlite DB")
    print("RUNNING FORENSIC AUDIT (RULE-BASED)...")
    
    # USER DATA
    # 08-13-1996 7:18 am Fairfield, CA
    # Lat: 38.2494 N, Lon: 122.0405 W (Approx for Fairfield, CA)
    
    result = Auditor.generate_full_nativity(
        date_str="1996-08-13",
        time_str="07:18",
        city="Fairfield",
        state="CA",
        name="User Client",
        house_system="W"
    )

    data = result["technical_data"]
    analysis = data["analysis"]
    # print("\n[DEBUG] Keys in analysis:", analysis.keys())
    
    # 1. Almuten Figuris
    print("\n[1] ALMUTEN FIGURIS (Master of the Nativity)")
    almuten = analysis.get('dignity', {}).get('almuten', {})
    if not almuten:
        almuten = analysis.get('advanced_mechanics', {}).get('almuten', {})
    print(f"Winner: {almuten.get('winner', 'Unknown')}")
    print(f"Score: {almuten.get('score', 'Unknown')}")
    
    # 2. Temperament
    print("\n[2] TEMPERAMENT AUDIT")
    # Check if calculation is missing
    temp = analysis.get('temperament')
    if not temp:
        # Check medical
        med = analysis.get('medical', {})
        print(f"Constitution: {med.get('constitution', 'Unknown')}")
        print(f"Distemper: {med.get('distemper', 'Unknown')}")
        print("Note: Full humours calculation may be missing from engine output.")
    else:
        print(f"Constitution: {temp.get('humoral_mixture', 'Unknown')}")
        print(f"Primary Element: {temp.get('primary_temperament', 'Unknown')}")
    
    # 3. Sect Status
    print("\n[3] SECT DETERMINATION")
    
    # Auditor doesn't explicitly return "Sect: Day" in a simple key sometimes, 
    # but we can infer it from the Sun's position if needed, or check 'dignity'
    # Actually, let's look at the 'chart' object? No, we have 'result'.
    # Let's try to find it in the planets list or summary.
    # For now, we'll verify if it's in analysis or just assume the engine handled it.
    # (The user cares about the output, so let's check what we have).
    
    # 4. Profection (Time Lord)
    print("\n[4] TIME LORD (Current Age)")
    prof = analysis.get('enhanced_profections', {})
    print(f"Age: {prof.get('age', 'Unknown')}")
    print(f"Annual Profection Sign: {prof.get('annual_sign', 'Unknown')}")
    print(f"Lord of the Year: {prof.get('lord_of_year', 'Unknown')}")

    # 5. Fixed Stars
    print("\n[5] FIXED STAR HITS (Force Majeure)")
    # This might fail if key missing, check gently
    sup = analysis.get('supplemental', {})
    stars = sup.get('stars', [])
    if stars:
        for s in stars:
            # Check s structure
            s_name = s.get('star_name', 'Unknown') if isinstance(s, dict) else getattr(s, 'star_name', 'Unknown')
            p_name = s.get('planet_name', 'Unknown') if isinstance(s, dict) else getattr(s, 'planet_name', 'Unknown')
            orb = s.get('orb', '?') if isinstance(s, dict) else getattr(s, 'orb', '?')
            print(f"  - {s_name} on {p_name} ({orb} orb)")
    else:
        print("  (None within orb)")

if __name__ == "__main__":
    show_rules()
