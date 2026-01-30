from datetime import datetime, timedelta
import swisseph as swe
from typing import List, Dict, Optional
from .models import Chart, Planet, PlanetName, Sign, Sect
from .logic import is_void_of_course, calculate_solar_status, is_besieged
from .dignities import DignityCalculator
from .chart_calculator import get_coordinates

class ElectionalEngine:
    """
    Kairos: The Electional Timing Engine.
    Uses Bonatti considerations and Hellenistic dignity to find 'Perfect Timing'.
    """
    def __init__(self):
        self.dignity_calc = DignityCalculator()

    def find_kairos(self, start_dt: datetime, city: str, state: str = "", hours_to_scan: int = 168, activity: str = "general"):
        """
        Finds the best windows for an activity within the next X hours.
        """
        try:
            lat, lon = get_coordinates(city, state)
        except Exception as e:
            return {"error": f"Location error: {str(e)}"}

        results = []
        
        # We'll scan hour by hour
        for i in range(hours_to_scan):
            current_dt = start_dt + timedelta(hours=i)
            
            # Calculate the chart for each hour
            chart = self._calculate_lightweight_chart(current_dt, lat, lon)
            score_data = self._evaluate_chart(chart, activity)
            
            results.append({
                "time": current_dt.isoformat(),
                "score": score_data["total_score"],
                "details": score_data["details"],
                "is_viable": score_data["is_viable"],
                "mood": score_data["mood"]
            })
            
        # Filter viable and sort
        viable_results = [r for r in results if r["is_viable"]]
        viable_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Group into windows (time segments with similar high scores)
        windows = self._group_into_windows(viable_results)
        
        return {
            "query": {
                "activity": activity,
                "location": f"{city}, {state}",
                "start_time": start_dt.isoformat(),
                "scan_range": f"{hours_to_scan} hours"
            },
            "best_windows": windows[:5], # Top 5 best windows
            "raw_top_slots": viable_results[:20]
        }

    def _calculate_lightweight_chart(self, dt: datetime, lat: float, lon: float) -> Chart:
        # JD calculation (UTC)
        # Note: assuming dt is already UTC for precise calculation
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)
        
        planets = []
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        
        planet_ids = {
            PlanetName.SUN: swe.SUN,
            PlanetName.MOON: swe.MOON,
            PlanetName.MERCURY: swe.MERCURY,
            PlanetName.VENUS: swe.VENUS,
            PlanetName.MARS: swe.MARS,
            PlanetName.JUPITER: swe.JUPITER,
            PlanetName.SATURN: swe.SATURN
        }
        
        sun_alt = 0.0
        for name, pid in planet_ids.items():
            res_tuple = swe.calc_ut(jd, pid, flags)
            res = res_tuple[0]
            
            p = Planet(name=name, longitude=res[0], latitude=res[1], speed=res[3])
            planets.append(p)
            
            if name == PlanetName.SUN:
                xin = (res[0], res[1], res[2])
                geopos = (lon, lat, 0)
                az_res = swe.azalt(jd, swe.SE_ECL2HOR, geopos, 0, 0, xin)
                # az_res is (azimuth, true_alt, apparent_alt)
                sun_alt = az_res[1]
                
        # Houses
        try:
            cusps, ascmc = swe.houses(jd, lat, lon, b'P')
            asc = ascmc[0]
            mc = ascmc[1]
        except Exception:
            # Fallback for extreme latitudes
            asc = 0.0
            mc = 0.0
        
        return Chart(
            sun_altitude=sun_alt,
            planets=planets,
            ascendant=asc,
            mc=mc
        )

    def _evaluate_chart(self, chart: Chart, activity: str) -> Dict:
        score = 0
        details = []
        is_viable = True
        
        moon = next(p for p in chart.planets if p.name == PlanetName.MOON)
        sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        
        # 1. Moon Conditions (CRITICAL in Electional)
        # Void of Course
        if is_void_of_course(moon.longitude, chart.planets):
            score -= 60
            details.append("Moon is Void of Course (Bonatti #5) - Critical Weakness")
            is_viable = False 
            
        # Combustion (The Sun's Curse)
        solar_status = calculate_solar_status(moon, sun)
        if solar_status == "COMBUST":
            score -= 50
            details.append("Moon is Combust (Burned by Sun) - Critical Weakness")
            is_viable = False
        elif solar_status == "UNDER_BEAMS":
            score -= 15
            details.append("Moon is Under Beams - Weakness")
            
        # Besiegement (Trapped between Malefics)
        if is_besieged(moon, chart):
            score -= 40
            details.append("Moon is Besieged (Trapped between Mars/Saturn) - Critical Weakness")
            is_viable = False

        # 2. Ascendant & Ruler Conditions
        asc_sign_idx = int(chart.ascendant / 30) % 12
        asc_sign = list(Sign)[asc_sign_idx]
        asc_ruler_name = DignityCalculator.DOMICILES[asc_sign][0]
        asc_ruler = next((p for p in chart.planets if p.name == asc_ruler_name), None)
        
        if asc_ruler:
            # Dignity of Asc Ruler
            dignity = DignityCalculator.calculate_planet_dignity(asc_ruler.name, asc_ruler.longitude, sect)
            r_score = dignity["total_score"]
            score += r_score * 3 # Heavily weighted
            details.append(f"Ascendant Ruler ({asc_ruler_name.value}) in {asc_sign.value} has Essential Dignity of {r_score} (x3)")
            
            # Ruler Solar Status
            ruler_solar = calculate_solar_status(asc_ruler, sun)
            if ruler_solar == "COMBUST":
                score -= 35
                details.append(f"Ascendant Ruler is Combust - Critical Weakness")
                is_viable = False
            elif ruler_solar == "CAZIMI":
                score += 30
                details.append(f"Ascendant Ruler is CAZIMI (In the Heart of Sun) - Supreme Power")

        # 3. House Placements (Whole Sign)
        for p in chart.planets:
            p_sign_idx = int(p.longitude / 30) % 12
            house_num = ((p_sign_idx - asc_sign_idx) % 12) + 1
            
            # Benefic Fortification
            if p.name in [PlanetName.JUPITER, PlanetName.VENUS]:
                if house_num == 1:
                    score += 20
                    details.append(f"Benefic {p.name.value} in 1st House - Strong Fortification")
                if house_num == 10:
                    score += 15
                    details.append(f"Benefic {p.name.value} in 10th House (MC) - Success/Visibility")
            
            # Malefic Obstruction
            if p.name in [PlanetName.MARS, PlanetName.SATURN]:
                is_oosect = (sect == Sect.DAY and p.name == PlanetName.MARS) or \
                             (sect == Sect.NIGHT and p.name == PlanetName.SATURN)
                
                if house_num == 1:
                    penalty = 25 if is_oosect else 15
                    score -= penalty
                    details.append(f"Malefic {p.name.value} in 1st House - {'Severe ' if is_oosect else ''}Obstruction")
                if house_num == 10:
                    penalty = 20 if is_oosect else 10
                    score -= penalty
                    details.append(f"Malefic {p.name.value} in 10th House - {'Severe ' if is_oosect else ''}Reputational Risk")

        # 4. Activity Specific Logic
        if activity.lower() in ["contract", "signing", "mercantile"]:
            # Focus on Mercury
            mercury = next((p for p in chart.planets if p.name == PlanetName.MERCURY), None)
            if mercury:
                m_dig = DignityCalculator.calculate_planet_dignity(mercury.name, mercury.longitude, sect)
                score += m_dig["total_score"] * 2
                details.append(f"Activity Sig (Mercury) Dignity: {m_dig['total_score']} (x2)")
                if mercury.speed < 0:
                    score -= 20
                    details.append("Mercury is Retrograde - Unstable for Contracts")
                    
        elif activity.lower() in ["marriage", "romance", "art"]:
            # Focus on Venus
            venus = next((p for p in chart.planets if p.name == PlanetName.VENUS), None)
            if venus:
                v_dig = DignityCalculator.calculate_planet_dignity(venus.name, venus.longitude, sect)
                score += v_dig["total_score"] * 2
                details.append(f"Activity Sig (Venus) Dignity: {v_dig['total_score']} (x2)")
                
        elif activity.lower() in ["war", "competition", "surgery"]:
            # Focus on Mars
            mars = next((p for p in chart.planets if p.name == PlanetName.MARS), None)
            if mars:
                target_score = 5 if sect == Sect.NIGHT else 0 # Mars better at night
                m_dig = DignityCalculator.calculate_planet_dignity(mars.name, mars.longitude, sect)
                score += (m_dig["total_score"] + target_score) * 2
                details.append(f"Activity Sig (Mars) Strength: {m_dig['total_score'] + target_score} (x2)")

        # 5. Mood Determination
        mood = "Average"
        if score > 50: mood = "Excellent (Kairos)"
        elif score > 20: mood = "Favorable"
        elif score < -20: mood = "Dreadful"
        elif score < 0: mood = "Tenuous"
        
        return {
            "total_score": score,
            "details": details,
            "is_viable": is_viable,
            "mood": mood
        }

    def _group_into_windows(self, sorted_slots: List[Dict]) -> List[Dict]:
        """
        Groups individual hours into contiguous 'windows' of good timing.
        """
        if not sorted_slots:
            return []
            
        # Re-sort by time chronologically for grouping
        chrono_slots = sorted(sorted_slots, key=lambda x: x["time"])
        
        windows = []
        if not chrono_slots: return []
        
        current_window = {
            "start": chrono_slots[0]["time"],
            "end": chrono_slots[0]["time"],
            "peak_score": chrono_slots[0]["score"],
            "peak_time": chrono_slots[0]["time"],
            "mood": chrono_slots[0]["mood"],
            "details": chrono_slots[0]["details"],
            "duration_hours": 1
        }
        
        for i in range(1, len(chrono_slots)):
            prev_time = datetime.fromisoformat(chrono_slots[i-1]["time"])
            curr_time = datetime.fromisoformat(chrono_slots[i]["time"])
            
            # If gap is 1 hour, continue window
            if curr_time - prev_time <= timedelta(hours=1.5):
                current_window["end"] = chrono_slots[i]["time"]
                current_window["duration_hours"] += 1
                if chrono_slots[i]["score"] > current_window["peak_score"]:
                    current_window["peak_score"] = chrono_slots[i]["score"]
                    current_window["peak_time"] = chrono_slots[i]["time"]
                    current_window["mood"] = chrono_slots[i]["mood"]
                    current_window["details"] = chrono_slots[i]["details"]
            else:
                # Close window and start new
                windows.append(current_window)
                current_window = {
                    "start": chrono_slots[i]["time"],
                    "end": chrono_slots[i]["time"],
                    "peak_score": chrono_slots[i]["score"],
                    "peak_time": chrono_slots[i]["time"],
                    "mood": chrono_slots[i]["mood"],
                    "details": chrono_slots[i]["details"],
                    "duration_hours": 1
                }
        
        windows.append(current_window)
        # Sort windows by peak score
        windows.sort(key=lambda x: x["peak_score"], reverse=True)
        return windows
