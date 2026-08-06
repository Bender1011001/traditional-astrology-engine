import os
import sys
import json
import argparse
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Tuple

# Adjust path to include the project root
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, ".env"))

import swisseph as swe

from src.engine.electional import ElectionalEngine
from src.engine.calculator.geo import get_coordinates
from src.engine.planetary_hours import PlanetaryHourEngine
from src.engine.mansions import LunarMansionEngine
from src.engine.dignities import DignityCalculator, Sect, TermSystem, PlanetName, Sign
from src.engine.calculations import (
    calculate_solar_status,
    is_in_via_combusta,
    is_besieged,
    is_void_of_course
)
from src.engine.remediation import PLANETARY_CORRESPONDENCES
from src.engine.models import Chart, Planet

def check_planetary_talisman(planet_name: PlanetName, chart: Chart, p_hour_data: dict, sect: Sect) -> Tuple[bool, str, dict]:
    # 1. Planetary Hour ruler
    if p_hour_data["hour_ruler"] != planet_name.value:
        return False, "Not the planetary hour of this planet", {}
    
    planet = next((p for p in chart.planets if p.name == planet_name), None)
    if not planet:
        return False, "Planet not found in chart", {}
    
    # 2. Essential Dignity
    dignity_data = DignityCalculator.calculate_planet_dignity(planet_name, planet.longitude, sect)
    dig_score = dignity_data.get("total_score", 0)
    if dig_score <= 0:
        return False, f"Planet has insufficient essential dignity: {dig_score}", {}
        
    # 3. Planet Retrograde check (speed > 0)
    if planet_name not in [PlanetName.SUN, PlanetName.MOON]:
        if planet.speed <= 0:
            return False, "Planet is retrograde", {}
            
    # 4. Combustion check
    sun = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
    if sun and planet_name != PlanetName.SUN:
        solar_status = calculate_solar_status(planet, sun)
        if solar_status in ["COMBUST", "DARK_MOON"]:
            return False, f"Planet is afflicted by the Sun: {solar_status}", {}
            
    # 5. House placement (Whole Sign)
    planet_sign_idx = int(planet.longitude / 30) % 12
    asc_sign_idx = int(chart.ascendant / 30) % 12
    house = ((planet_sign_idx - asc_sign_idx) % 12) + 1
    if house not in [1, 5, 10, 11]:
        return False, f"Planet in non-benefic house: {house} (must be 1st, 5th, 10th, or 11th)", {}
        
    # 6. Moon condition
    moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)
    if moon and sun:
        if is_void_of_course(moon.longitude, chart.planets):
            return False, "Moon is Void of Course", {}
        if calculate_solar_status(moon, sun) == "DARK_MOON":
            return False, "Moon is combust (Dark Moon)", {}
        if is_in_via_combusta(moon.longitude):
            return False, "Moon is in Via Combusta", {}
            
    # 7. Malefic aspect affliction
    malefic_name = PlanetName.MARS if sect == Sect.DAY else PlanetName.SATURN
    malefic = next((p for p in chart.planets if p.name == malefic_name), None)
    if malefic:
        diff = abs(planet.longitude - malefic.longitude) % 360
        shortest = diff if diff <= 180 else 360 - diff
        for target in [0, 90, 180]:
            if abs(shortest - target) <= 6.0:  # 6-degree orb
                aspect_name = "conjunction" if target == 0 else ("square" if target == 90 else "opposition")
                return False, f"Planet is afflicted by {aspect_name} aspect with malefic {malefic_name.value}", {}
                
    details = {
        "essential_dignity_score": dig_score,
        "house": house,
        "sign": planet.sign.value,
        "degree": planet.degree_in_sign,
        "is_day_ruler": p_hour_data["day_ruler"] == planet_name.value,
        "dignity_breakdown": dignity_data
    }
    return True, "Eligible", details

def check_mansion_talisman(mansion_id: int, chart: Chart) -> Tuple[bool, str, dict]:
    moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)
    if not moon:
        return False, "Moon not found in chart", {}
        
    mansion = LunarMansionEngine.get_lunar_mansion(moon.longitude)
    if mansion["mansion_id"] != mansion_id:
        return False, f"Moon is in mansion {mansion['mansion_id']} ({mansion['name']}), not {mansion_id}", {}
        
    sun = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
    
    # 1. Void of Course
    if is_void_of_course(moon.longitude, chart.planets):
        return False, "Moon is Void of Course", {}
        
    # 2. Combustion
    if sun and calculate_solar_status(moon, sun) == "DARK_MOON":
        return False, "Moon is combust (Dark Moon)", {}
        
    # 3. Via Combusta
    if is_in_via_combusta(moon.longitude):
        return False, "Moon is in Via Combusta", {}
        
    # 4. Besiegement
    if is_besieged(moon, chart):
        return False, "Moon is besieged", {}
        
    # 5. Malefic aspects
    for malefic_name in [PlanetName.MARS, PlanetName.SATURN]:
        malefic = next((p for p in chart.planets if p.name == malefic_name), None)
        if malefic:
            diff = abs(moon.longitude - malefic.longitude) % 360
            shortest = diff if diff <= 180 else 360 - diff
            for target in [0, 90, 180]:
                if abs(shortest - target) <= 6.0:  # 6-degree orb
                    aspect_name = "conjunction" if target == 0 else ("square" if target == 90 else "opposition")
                    return False, f"Moon is afflicted by {aspect_name} aspect with malefic {malefic_name.value}", {}
                    
    details = {
        "moon_longitude": moon.longitude,
        "moon_sign": moon.sign.value,
        "moon_degree": moon.degree_in_sign,
        "mansion_name": mansion["name"],
        "mansion_id": mansion["mansion_id"],
        "intents_good": mansion.get("intents_good", []),
        "intents_bad": mansion.get("intents_bad", [])
    }
    return True, "Eligible", details

def run_talisman_scan(
    city: str,
    state: str,
    start_dt: datetime,
    days_to_scan: int,
    filter_type: str
) -> Dict[str, Any]:
    try:
        lat, lon = get_coordinates(city, state)
    except Exception as e:
        print(f"[-] Error getting coordinates: {e}")
        sys.exit(1)

    print(f"[+] Scanning from {start_dt.isoformat()} UTC for {days_to_scan} days...")
    print(f"[+] Location: {city}, {state} (Lat: {lat}, Lon: {lon})")

    election_eng = ElectionalEngine()
    hours_to_scan = days_to_scan * 24

    # We collect raw eligible hours for each talisman type
    raw_planetary_hours: Dict[str, List[Dict[str, Any]]] = {p.value: [] for p in PlanetName if p.value in PLANETARY_CORRESPONDENCES}
    raw_mansion_hours: Dict[int, List[Dict[str, Any]]] = {i: [] for i in range(1, 29)}

    for h in range(hours_to_scan):
        current_dt = start_dt + timedelta(hours=h)
        chart = election_eng._calculate_lightweight_chart(current_dt, lat, lon)
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        
        # Calculate planetary hours
        try:
            p_hour_data = PlanetaryHourEngine.calculate_hours(current_dt, lat, lon)
        except Exception as e:
            # Handle polar fallback
            continue

        # Check Planetary Talismans
        if filter_type in ["all", "planet"]:
            for p_name in PlanetName:
                if p_name.value in PLANETARY_CORRESPONDENCES:
                    eligible, reason, details = check_planetary_talisman(p_name, chart, p_hour_data, sect)
                    if eligible:
                        raw_planetary_hours[p_name.value].append({
                            "time": current_dt,
                            "details": details
                        })

        # Check Mansion Talismans
        if filter_type in ["all", "mansion"]:
            moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)
            if moon:
                mansion = LunarMansionEngine.get_lunar_mansion(moon.longitude)
                m_id = mansion["mansion_id"]
                eligible, reason, details = check_mansion_talisman(m_id, chart)
                if eligible:
                    raw_mansion_hours[m_id].append({
                        "time": current_dt,
                        "details": details
                    })

    # Group consecutive hours into windows
    grouped_planetary_windows: Dict[str, List[Dict[str, Any]]] = {}
    grouped_mansion_windows: Dict[int, List[Dict[str, Any]]] = {}

    for planet, hours in raw_planetary_hours.items():
        grouped_planetary_windows[planet] = group_hours(hours)

    for m_id, hours in raw_mansion_hours.items():
        grouped_mansion_windows[m_id] = group_hours(hours)

    return {
        "planetary": grouped_planetary_windows,
        "mansion": grouped_mansion_windows,
        "meta": {
            "city": city,
            "state": state,
            "latitude": lat,
            "longitude": lon,
            "start_time": start_dt.isoformat(),
            "scan_days": days_to_scan
        }
    }

def group_hours(hours: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not hours:
        return []
    
    windows = []
    current_window: List[Dict[str, Any]] = []

    for h in hours:
        if not current_window:
            current_window.append(h)
        else:
            last_time = current_window[-1]["time"]
            if h["time"] - last_time == timedelta(hours=1):
                current_window.append(h)
            else:
                windows.append(create_window_record(current_window))
                current_window = [h]
                
    if current_window:
        windows.append(create_window_record(current_window))
        
    return windows

def create_window_record(window_hours: List[Dict[str, Any]]) -> Dict[str, Any]:
    start_time = window_hours[0]["time"]
    end_time = window_hours[-1]["time"] + timedelta(hours=1)
    duration = len(window_hours)
    
    # Extract details from first hour as representative
    rep_details = window_hours[0]["details"]
    
    return {
        "start": start_time.isoformat(),
        "end": end_time.isoformat(),
        "duration_hours": duration,
        "details": rep_details
    }

def print_report(scan_results: Dict[str, Any]):
    meta = scan_results["meta"]
    print("\n" + "=" * 80)
    print(f"  TALISMAN ELECTIONAL TIMING REPORT")
    print(f"  Location: {meta['city']}, {meta['state']} | Start: {meta['start_time']}")
    print(f"  Scan Range: {meta['scan_days']} Days")
    print("=" * 80)

    all_windows = []

    # Format Planetary Windows
    print("\n[+] Traditional Planetary Talisman Windows:")
    has_planetary = False
    for planet, windows in scan_results["planetary"].items():
        if windows:
            has_planetary = True
            corr = PLANETARY_CORRESPONDENCES[planet]
            print(f"\n  • {planet.upper()} Talisman:")
            print(f"    Safe Metal: {corr['metal_safe']}")
            print(f"    Stones:     {', '.join(corr['stones'])}")
            print(f"    Colors:     {', '.join(corr['colors'])}")
            print(f"    Incense:    {', '.join(corr['incense'])}")
            for idx, w in enumerate(windows, 1):
                det = w["details"]
                print(f"    Window #{idx}: {w['start']} to {w['end']} ({w['duration_hours']}h)")
                print(f"      Dignity Score: +{det['essential_dignity_score']} | House: {det['house']} in {det['sign']}")
                all_windows.append({
                    "type": f"Planetary - {planet}",
                    "start": w["start"],
                    "end": w["end"],
                    "duration_hours": w["duration_hours"],
                    "description": f"Dignity +{det['essential_dignity_score']}, House {det['house']} in {det['sign']}"
                })
    if not has_planetary:
        print("  No planetary talisman windows detected in this scan range.")

    # Format Mansion Windows
    print("\n[+] Lunar Mansion Talisman Windows:")
    has_mansions = False
    for m_id, windows in scan_results["mansion"].items():
        if windows:
            has_mansions = True
            m_name = windows[0]["details"]["mansion_name"]
            print(f"\n  • Mansion {m_id} ({m_name}):")
            for idx, w in enumerate(windows, 1):
                det = w["details"]
                print(f"    Window #{idx}: {w['start']} to {w['end']} ({w['duration_hours']}h)")
                print(f"      Good for: {', '.join(det['intents_good'])}")
                print(f"      Bad for:  {', '.join(det['intents_bad'])}")
                all_windows.append({
                    "type": f"Mansion {m_id} ({m_name})",
                    "start": w["start"],
                    "end": w["end"],
                    "duration_hours": w["duration_hours"],
                    "description": f"Good for: {', '.join(det['intents_good'][:3])}..."
                })
    if not has_mansions:
        print("  No lunar mansion talisman windows detected in this scan range.")

    print("\n" + "=" * 80)
    print("  SOONEST AVAILABLE TALISMAN WINDOWS")
    print("=" * 80)

    if all_windows:
        # Sort by start time
        all_windows.sort(key=lambda x: x["start"])
        for idx, w in enumerate(all_windows[:5], 1):
            print(f"  {idx}. {w['type']} Talisman")
            print(f"     Start Time: {w['start']}")
            print(f"     End Time:   {w['end']} ({w['duration_hours']} hours)")
            print(f"     Details:    {w['description']}")
            print("-" * 50)
    else:
        print("  No windows found.")
    print("=" * 80 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Find electional windows for creating traditional talismans.")
    parser.add_argument("--city", type=str, default="Fairfield", help="City name")
    parser.add_argument("--state", type=str, default="CA", help="State abbreviation")
    parser.add_argument("--days", type=int, default=30, help="Number of days to scan (default: 30)")
    parser.add_argument("--start", type=str, default=None, help="Start date in YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format (defaults to now)")
    parser.add_argument("--type", type=str, choices=["all", "planet", "mansion"], default="all", help="Filter by talisman type")
    
    args = parser.parse_args()

    if args.start:
        try:
            if "T" in args.start:
                start_dt = datetime.fromisoformat(args.start)
            else:
                start_dt = datetime.strptime(args.start, "%Y-%m-%d")
        except ValueError:
            print("[-] Invalid start date format. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.")
            sys.exit(1)
    else:
        start_dt = datetime.now(timezone.utc).replace(tzinfo=None)

    # Run scan
    results = run_talisman_scan(
        city=args.city,
        state=args.state,
        start_dt=start_dt,
        days_to_scan=args.days,
        filter_type=args.type
    )

    # Print Report to Terminal
    print_report(results)

    # Save to JSON file
    os.makedirs(os.path.join(ROOT_DIR, "chart_outputs"), exist_ok=True)
    out_path = os.path.join(ROOT_DIR, "chart_outputs", "talisman_election_windows.json")
    
    # Helper to serialize datetime in dict
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return super().default(obj)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, cls=DateTimeEncoder, indent=2)
    print(f"[+] Detailed scan results saved to: chart_outputs/talisman_election_windows.json")

if __name__ == "__main__":
    main()
