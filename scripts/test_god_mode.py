import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from engine.models import Chart, Planet, PlanetName, Sect
from engine.logic import perform_forensic_audit

def create_test_chart():
    # Create a simple test chart (approximate positions for 2000-01-01)
    planets = [
        Planet(PlanetName.SUN, 280.0),      # Capricorn
        Planet(PlanetName.MOON, 220.0),     # Scorpio
        Planet(PlanetName.MERCURY, 275.0),  # Capricorn
        Planet(PlanetName.VENUS, 250.0),    # Sagittarius
        Planet(PlanetName.MARS, 330.0),     # Pisces
        Planet(PlanetName.JUPITER, 30.0),   # Taurus
        Planet(PlanetName.SATURN, 50.0),    # Taurus
        Planet(PlanetName.URANUS, 315.0),   # Aquarius
        Planet(PlanetName.NEPTUNE, 303.0),  # Aquarius
        Planet(PlanetName.PLUTO, 251.0),    # Sagittarius
        Planet(PlanetName.NORTH_NODE, 120.0), # Leo
        Planet(PlanetName.SOUTH_NODE, 300.0)  # Aquarius
    ]
    
    # Houses (Whole Sign for simplicity in test)
    houses = {i: (i-1)*30.0 for i in range(1, 13)}
    
    return Chart(
        sun_altitude=10.0, # Day chart
        planets=planets,
        ascendant=0.0, # Aries Rising
        mc=270.0, # Capricorn MC
        houses=houses,
        geo_lat=51.5,
        geo_lon=0.0,
        jd=2451545.0 # J2000
    )

def test_god_mode():
    print("Initializing God Mode Test...")
    chart = create_test_chart()
    
    print("Running Forensic Audit...")
    try:
        report = perform_forensic_audit(chart, jd=2451545.0, age=30)
        
        # 1. Check Lots
        print("\n--- Checking Lots ---")
        lots = report.get("lots", {})
        required_lots = ["Fortune", "Spirit", "Debt", "Theft", "Accusation"]
        for lot in required_lots:
            if lot in lots:
                print(f"[PASS] Lot '{lot}' found: {lots[lot]:.2f}")
            else:
                print(f"[FAIL] Lot '{lot}' MISSING")
                
        # 2. Check Advanced Mechanics
        print("\n--- Checking Advanced Mechanics ---")
        adv = report.get("advanced_mechanics", {})
        
        # Almuten
        if "almuten" in adv and adv["almuten"]["winner"] != "Unknown":
            print(f"[PASS] Almuten Figuris calculated: {adv['almuten']['winner']}")
        else:
            print(f"[FAIL] Almuten Figuris missing or failed")
            
        # Doryphory
        if "doryphory" in adv:
            print(f"[PASS] Doryphory analysis present ({len(adv['doryphory'])} instances)")
        else:
            print(f"[FAIL] Doryphory missing")
            
        # 3. Check Classical Geometry (Monomoiria/Dodecatemoria)
        print("\n--- Checking Classical Geometry ---")
        planets = report.get("planets", [])
        if not planets:
            print("[FAIL] No planets in report")
        else:
            p1 = planets[0]
            classical = p1.get("classical", {})
            
            # Monomoiria
            if "monomoiria" in classical:
                print(f"[PASS] Monomoiria found for {p1['planet']}")
                print(f"       Zoidion Ruler: {classical['monomoiria'].get('zoidion_ruler')}")
            else:
                print(f"[FAIL] Monomoiria missing for {p1['planet']}")
                
            # Dodecatemoria
            if "dodecatemoria" in classical:
                print(f"[PASS] Dodecatemoria found for {p1['planet']}")
                valens = classical['dodecatemoria'].get('valens', {})
                print(f"       Valens: {valens.get('sign')} (Ruler: {valens.get('ruler')})")
            else:
                print(f"[FAIL] Dodecatemoria missing for {p1['planet']}")

        # 4. Check Forensic Lots Report
        print("\n--- Checking Forensic Lots Report ---")
        forensic = report.get("forensic_lots", {})
        if "Debt/Bankruptcy" in forensic:
             debt_data = forensic["Debt/Bankruptcy"].get("data")
             if debt_data and "sign" in debt_data:
                 print(f"[PASS] Debt/Bankruptcy report found with enrichment: {debt_data['sign']} (House {debt_data['house']})")
             else:
                 print(f"[FAIL] Debt/Bankruptcy report found but missing enrichment data")
        else:
             print(f"[FAIL] Debt/Bankruptcy report missing")

        # 5. Check Rule Ledger for Almuten
        print("\n--- Checking Rule Ledger ---")
        ledger = report.get("rule_ledger", [])
        almuten_rule = next((r for r in ledger if r["category"] == "Almuten Figuris"), None)
        if almuten_rule:
            print(f"[PASS] Almuten Figuris found in Rule Ledger: {almuten_rule['judgment']}")
        else:
            print(f"[FAIL] Almuten Figuris missing from Rule Ledger")

        print("\nTest Complete.")
        
    except Exception as e:
        print(f"\n[CRITICAL FAIL] Exception during audit: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_god_mode()
