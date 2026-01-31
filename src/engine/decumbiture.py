from datetime import datetime
from typing import List, Dict, Optional
import swisseph as swe
from .models import Chart, PlanetName, Sign
from .hyleg import HylegAlcocodenEngine

class DecumbitureEngine:
    """
    Engine for Decumbiture Charts (Moment of falling ill).
    Calculates Critical Days, Distempers, and Prognosis.
    """

    MAX_CRITICAL_DAYS = 40 # Usually checks up to 40 days or 3 crises

    @staticmethod
    def calculate_critical_days(decumbiture_jd: float) -> List[Dict]:
        """
        Calculates the sequence of Critical Days based on the Moon's motion.
        Crisis occurs when Moon is at:
        - 45 degrees (First Semi-Square) - Indication
        - 90 degrees (First Square) - First Crisis
        - 135 degrees (Second Semi-Square) - Indication
        - 180 degrees (Opposition) - Full Crisis
        - 225 degrees (Third Semi-Square) - Indication
        - 270 degrees (Second Square) - Third Crisis
        """
        moon_res = swe.calc_ut(decumbiture_jd, swe.MOON, swe.FLG_SWIEPH)[0]
        start_lon = moon_res[0]

        phases = [
            {"deg": 45, "type": "Indication (Semi-Square)", "severity": 4},
            {"deg": 90, "type": "First Crisis (Square)", "severity": 8},
            {"deg": 135, "type": "Indication (Semi-Square)", "severity": 4},
            {"deg": 180, "type": "Full Crisis (Opposition)", "severity": 10},
            {"deg": 225, "type": "Indication (Semi-Square)", "severity": 4},
            {"deg": 270, "type": "Third Crisis (Square)", "severity": 8},
        ]

        critical_days = []
        
        # Approximate motion of Moon ~13.17 deg/day
        avg_motion = 13.176
        
        for phase in phases:
            target_dist = phase["deg"]
            approx_days = target_dist / avg_motion
            
            # Refine exact time
            # We want to find t where (Moon(t) - Start) = target_dist
            
            t = decumbiture_jd + approx_days
            
            # Simple Newton-like refinement (3 iterations)
            for _ in range(3):
                m_curr = swe.calc_ut(t, swe.MOON, swe.FLG_SWIEPH)[0][0]
                diff = (m_curr - start_lon) % 360
                # Handle wrapping
                # This diff is "how far traveled forward".
                # If start=350, current=10, diff should be 20.
                
                # Check actual travel distance including orbits?
                # The moon doesn't loop 360 in these short ranges usually, 
                # but if we go > 27 days it does.
                
                # We know the target is like 45, 90 etc.
                # Just minimize (diff - target)
                # But diff via modulo might be tricky if it wrapped.
                
                # Calculate total movement
                # But simpler: calculate error in degrees, adjust t
                err = target_dist - diff
                if err > 180: err -= 360 
                elif err < -180: err += 360
                
                # If error is large due to wrap mismatch, careful.
                # Assuming approximate calculation put us close.
                t += err / avg_motion
            
            y, m, d, h = swe.revjul(t)
            # Rounding to nearest hour
            date_str = f"{y:04d}-{m:02d}-{d:02d}"
            
            critical_days.append({
                "label": phase["type"],
                "jd": t,
                "date": date_str,
                "days_from_onset": round(t - decumbiture_jd, 1),
                "severity": phase["severity"]
            })
            
        return critical_days

    @staticmethod
    def analyze_distemper(moon_sign: Sign) -> Dict:
        """
        Determines the Humoral Imbalance (Distemper) based on Moon's sign at onset.
        """
        element = "Unknown"
        humor = "Unknown"
        treatment = "Unknown"
        
        if moon_sign in [Sign.ARIES, Sign.LEO, Sign.SAGITTARIUS]:
            element = "Fire"
            humor = "Choleric (Yellow Bile)"
            treatment = "Cooling and Moistening (e.g., Barley water, Cucumber)"
        elif moon_sign in [Sign.TAURUS, Sign.VIRGO, Sign.CAPRICORN]:
            element = "Earth"
            humor = "Melancholic (Black Bile)"
            treatment = "Heating and Moistening (e.g., Ginger, warm baths)"
        elif moon_sign in [Sign.GEMINI, Sign.LIBRA, Sign.AQUARIUS]:
            element = "Air"
            humor = "Sanguine (Blood)"
            treatment = "Cooling and Drying (e.g., Sour things, venting)"
        elif moon_sign in [Sign.CANCER, Sign.SCORPIO, Sign.PISCES]:
            element = "Water"
            humor = "Phlegmatic (Phlegm)"
            treatment = "Heating and Drying (e.g., Pepper, Mustard, Sweating)"
            
        return {
            "moon_sign": moon_sign.value,
            "element": element,
            "excess_humor": humor,
            "palliative_nature": treatment
        }

    @staticmethod
    def check_prognosis(chart: Chart) -> Dict:
        """
        Basic Decumbiture Prognosis rules.
        """
        asc_ruler = HylegAlcocodenEngine.get_domicile_ruler(chart.ascendant)
        
        # Check Lord of Ascendant combustion
        loa = next((p for p in chart.planets if p.name == asc_ruler), None)
        sun = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
        
        prognosis_score = 0
        notes = []
        
        if loa and sun:
            diff = abs(loa.longitude - sun.longitude)
            if diff > 180: diff = 360 - diff
            if diff < 8:
                notes.append("Lord of Ascendant Combust: Vitality is burned up. Grave prognosis without intervention.")
                prognosis_score -= 5
            elif diff < 15:
                notes.append("Lord of Ascendant Under Beams: Weakened vitality.")
                prognosis_score -= 2
        
        # Check Moon affliction (Kakosis check basically, but simplified here)
        # Using built-in logic or just checking basic squares to Mars/Saturn
        mars = next((p for p in chart.planets if p.name == PlanetName.MARS), None)
        moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)
        
        if mars and moon:
            diff = abs(mars.longitude - moon.longitude)
            if diff > 180: diff = 360 - diff
            if abs(diff - 90) < 5 or abs(diff - 180) < 5 or diff < 5:
                notes.append("Moon afflicted by Mars: Acute fever, surgery risk, inflammation.")
                prognosis_score -= 3

        saturn = next((p for p in chart.planets if p.name == PlanetName.SATURN), None)
        if saturn and moon:
            diff = abs(saturn.longitude - moon.longitude)
            if diff > 180: diff = 360 - diff
            if abs(diff - 90) < 5 or abs(diff - 180) < 5 or diff < 5:
                notes.append("Moon afflicted by Saturn: Chronic lingering, cold, obstruction.")
                prognosis_score -= 3
                
        status = "Neutral"
        if prognosis_score > 0: status = "Good"
        elif prognosis_score < -4: status = "Critically Guarded"
        elif prognosis_score < 0: status = "Difficult"
        
        return {
            "score": prognosis_score,
            "status": status,
            "indicators": notes
        }
