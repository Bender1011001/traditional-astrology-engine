#!/usr/bin/env python3
import sys
import json
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.calculator.main import calculate_chart_data
from src.engine.forensic_engine import Auditor
from src.engine.horary import build_horary_oracle

def main():
    print("=========================================")
    print("  Classical Horary Astrology QA Tester")
    print("=========================================")
    print("This tool erects a chart for the moment of a query,")
    print("evaluating rigorous Masha'allah/Bonatti perfection physics.")
    print("-----------------------------------------")

    question = input("\nEnter the exact Horary Question: ")
    
    date_str = input("Date (YYYY/MM/DD) [leave blank for today]: ").strip()
    if not date_str:
        date_str = datetime.now().strftime("%Y/%m/%d")
        
    time_str = input("Time (HH:MM) [leave blank for now]: ").strip()
    if not time_str:
        time_str = datetime.now().strftime("%H:%M")
        
    lat_str = input("Latitude (e.g. 38.4340) [default: 38.4340152]: ").strip()
    lat = float(lat_str) if lat_str else 38.4340152
    
    lon_str = input("Longitude (e.g. -121.9613) [default: -121.9613808]: ").strip()
    lon = float(lon_str) if lon_str else -121.9613808

    print("\n[+] Calculating Chart Physics...")
    
    # 1. Calculate underlying astronomy
    raw_data = calculate_chart_data(
        date_str=date_str,
        time_str=time_str,
        city="Local Test",
        state="",
        latitude=lat,
        longitude=lon,
        house_system="R", # Regiomontanus is standard for traditional Horary
        zodiac_system="tropical"
    )
    
    if "error" in raw_data:
        print(f"\n[!] ERROR in calculation: {raw_data['error']}")
        return

    # 2. Rebuild chart object
    chart = Auditor._rebuild_chart_model(raw_data)
    
    # 3. Build the Horary Oracle
    oracle_result = build_horary_oracle(question, chart)
    
    # 4. Display Results
    print("\n=========================================")
    print("            HORARY REPORT")
    print("=========================================")
    print(f"Question:      {oracle_result['question']}")
    print(f"Querent:       Ascendant in {oracle_result['querent_sign']} (L1: {oracle_result['querent_ruler']})")
    print(f"Quesited:      {oracle_result['quesited_label']} ({oracle_result['quesited_house']}H) in {oracle_result['quesited_sign']} (Lord: {oracle_result['quesited_ruler']})")
    
    print("\n--- Strictures & Safety ---")
    if getattr(oracle_result, "strictures", None) or oracle_result.get("strictures"):
        for stricture in oracle_result["strictures"]:
            print(f"[!] Warning: {stricture}")
    else:
        print("[+] Chart is safe to judge.")
        
    print("\n--- Physical Application Conditions ---")
    conditions = oracle_result.get("conditions", [])
    if conditions:
        for c in conditions:
            status = c.get("status", "")
            cond_type = c.get("condition", "")
            print(f"[{status}] {cond_type}")
            if "details" in c:
                print(f"    -> {c['details']}")
            else:
                for k, v in c.items():
                    if k not in ["condition", "status"]:
                        print(f"    -> {k.title()}: {v}")
    else:
        print("[-] No perfection found between significators.")
        
    print("\n-----------------------------------------")
    print(f"FINAL VERDICT: {oracle_result['verdict']} (Weight: {oracle_result['verdict_weight']})")
    print(f"Total Score: {oracle_result['total_score']}")
    
    # Dump full trace for debugging manual Lilly queries
    trace_file = "horary_trace.json"
    with open(trace_file, "w", encoding="utf-8") as f:
        json.dump(oracle_result, f, indent=4)
        
    print(f"\n[i] Full JSON trace saved to {trace_file}")
    
if __name__ == "__main__":
    main()
