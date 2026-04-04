from datetime import datetime, timedelta
import swisseph as swe
from typing import List, Dict, Optional, Tuple
from .models import PlanetName, Sign, Chart, Planet

class MedicalAstrology:
    """
    Implements traditional Medical Astrology (Iatromathematics) protocols.
    
    CRITICAL MEDICAL DISCLAIMER:
    This module is for HISTORICAL AND EDUCATIONAL RESEARCH PURPOSES ONLY. 
    Traditional 'Iatromathematics' and 'Surgery Rules' are artifacts of 
    pre-modern history and DO NOT constitute medical advice. 
    
    Under no circumstances should this software be used to:
    1. Diagnose, treat, or prevent any medical condition.
    2. Schedule or postpone surgical procedures.
    3. Replace the advice of a qualified healthcare professional.
    
    The authors and contributors accept NO LIABILITY for any health-related 
    decisions made based on the output of this module.
    """
    
    MELOTHESIA = {
        Sign.ARIES: "Head, Face, Eyes",
        Sign.TAURUS: "Throat, Neck, Thyroid",
        Sign.GEMINI: "Shoulders, Arms, Hands, Lungs",
        Sign.CANCER: "Chest, Stomach, Breasts",
        Sign.LEO: "Heart, Upper Back, Spine",
        Sign.VIRGO: "Abdomen, Intestines, Digestive system",
        Sign.LIBRA: "Kidneys, Lower Back, Lumbar",
        Sign.SCORPIO: "Reproductive system, Excretory system",
        Sign.SAGITTARIUS: "Hips, Thighs, Liver",
        Sign.CAPRICORN: "Knees, Joints, Bones, Teeth, Skin",
        Sign.AQUARIUS: "Calves, Ankles, Circulatory system",
        Sign.PISCES: "Feet, Toes, Lymphatic system"
    }

    @staticmethod
    def get_body_part_for_sign(sign: Sign) -> str:
        return MedicalAstrology.MELOTHESIA.get(sign, "Unknown")

    @staticmethod
    def can_perform_surgery(target_body_part: str, jd_current: float, natal_chart: Chart, decumbiture_jd: Optional[float] = None) -> Dict:
        """
        Traditional Surgery Rule:
        1. Avoid surgery when the Moon is in the sign ruling the body part.
        2. Avoid surgery when the Moon is afflicted by Mars or Saturn.
        3. Avoid surgery during Eclipses (±3 days).
        4. Avoid surgery on Critical Days (7, 14, 21 days from onset).
        """
        from .mundane import get_recent_eclipses
        
        # Find the sign associated with the target_body_part
        target_sign = None
        for sign, part in MedicalAstrology.MELOTHESIA.items():
            if target_body_part.lower() in part.lower():
                target_sign = sign
                break
        
        # Current Moon position
        moon_res = swe.calc_ut(jd_current, swe.MOON, swe.FLG_SWIEPH)[0]
        moon_lon = moon_res[0]
        moon_sign_idx = int(moon_lon / 30) % 12
        moon_sign = list(Sign)[moon_sign_idx]
        
        # Affliction check (Mars/Saturn)
        mars_res = swe.calc_ut(jd_current, swe.MARS, swe.FLG_SWIEPH)[0]
        saturn_res = swe.calc_ut(jd_current, swe.SATURN, swe.FLG_SWIEPH)[0]
        
        mars_lon = mars_res[0]
        saturn_lon = saturn_res[0]
        
        afflictions = []
        
        def check_aspect(lon1, lon2, name):
            diff = abs(lon1 - lon2) % 360
            if diff > 180: diff = 360 - diff
            
            # Orbs: Conjunction (8), Square (8), Opposition (8)
            if diff <= 8:
                return f"Conjunction with {name}"
            if abs(diff - 90) <= 8:
                return f"Square with {name}"
            if abs(diff - 180) <= 8:
                return f"Opposition with {name}"
            return None

        m_mars = check_aspect(moon_lon, mars_lon, "Mars")
        if m_mars: afflictions.append(m_mars)
        
        m_saturn = check_aspect(moon_lon, saturn_lon, "Saturn")
        if m_saturn: afflictions.append(m_saturn)
        
        reasons = []
        safe = True
        
        # 1. Sign Rule
        if target_sign and moon_sign == target_sign:
            safe = False
            reasons.append(f"Moon is in {moon_sign.value}, which rules {MedicalAstrology.MELOTHESIA[target_sign]}.")
            
        # 2. Affliction Rule
        if afflictions:
            safe = False
            reasons.extend(afflictions)

        # 3. Eclipse Rule (±3 days)
        # Note: get_recent_eclipses finds the eclipse *previous* to jd_current.
        # We also want to check if one is *upcoming*.
        eclipses = get_recent_eclipses(jd_current + 3) 
        for ec in eclipses:
            if abs(ec["jd"] - jd_current) <= 3:
                safe = False
                reasons.append(f"Surgery near {ec['type']} (JD {ec['jd']:.2f}). Avoid ±3 days.")

        # 4. Critical Days Rule
        if decumbiture_jd:
            critical_days = MedicalAstrology.calculate_critical_days(decumbiture_jd)
            for cd in critical_days:
                if abs(cd["jd"] - jd_current) <= 1.0:
                    safe = False
                    reasons.append(f"Surgery on {cd['label']}. High crisis potential.")

        return {
            "safe": safe,
            "reasons": reasons,
            "moon_sign": moon_sign.value,
            "target_body_part": target_body_part,
            "historical_context": "Based on the rule: 'Touch not with iron that part of the body ruled by the sign the Moon is transiting.' Extended with Eclipse and Crisis Day protocols."
        }

    @staticmethod
    def check_moon_mercury_interference(moon_lon: float, mercury_lon: float) -> Optional[Dict]:
        """
        Moon-Mercury Interference Rule (Doc p. 235):
        'If the Moon applies to an opposition of Mercury, or is in square to Mercury, it disturbs the imaginative faculty, causing delirium...'
        """
        diff = abs(moon_lon - mercury_lon) % 360
        if diff > 180: diff = 360 - diff
        
        if abs(diff - 90) < 8:
            return {
                "type": "WARNING: Diagnostic Confusion",
                "condition": "Moon square Mercury",
                "details": "High risk of delirium or incorrect diagnosis. Rely on physical signs over patient's report."
            }
        elif abs(diff - 180) < 8:
            return {
                "type": "WARNING: Diagnostic Confusion",
                "condition": "Moon opposition Mercury",
                "details": "Speech/Mind disconnected from Body. Warning of confusion or unreliable symptoms."
            }
        return None

    @staticmethod
    def calculate_critical_days(decumbiture_jd: float) -> List[Dict]:
        """
        Calculates 7th, 14th, and 21st day 'crisis' points using the DecumbitureEngine.
        """
        from .decumbiture import DecumbitureEngine
        return DecumbitureEngine.calculate_critical_days(decumbiture_jd)

    @staticmethod
    def calculate_remediation_window(jd_start: float, duration_days: int = 30) -> List[Dict]:
        """
        Identifies periods of high malefic intensity (Mars/Saturn activity)
        and suggests mitigation windows.
        """
        windows = []
        
        for day in range(duration_days):
            jd = jd_start + day
            
            # Check for Mars/Saturn conjunctions or harsh aspects to Sun/Moon
            sun_res = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0][0]
            moon_res = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH)[0][0]
            mars_res = swe.calc_ut(jd, swe.MARS, swe.FLG_SWIEPH)[0][0]
            saturn_res = swe.calc_ut(jd, swe.SATURN, swe.FLG_SWIEPH)[0][0]
            
            malefic_intensity = 0
            reasons = []
            
            # Malefics afflicting Luminaries
            for mal in [("Mars", mars_res), ("Saturn", saturn_res)]:
                for lum in [("Sun", sun_res), ("Moon", moon_res)]:
                    dist = abs(mal[1] - lum[1]) % 360
                    if dist > 180: dist = 360 - dist
                    
                    if dist < 5:
                        malefic_intensity += 10
                        reasons.append(f"{mal[0]} conjunct {lum[0]}")
                    elif abs(dist - 90) < 5:
                        malefic_intensity += 8
                        reasons.append(f"{mal[0]} square {lum[0]}")
                    elif abs(dist - 180) < 5:
                        malefic_intensity += 9
                        reasons.append(f"{mal[0]} opposition {lum[0]}")
            
            # Mars square/opp Saturn
            m_s_dist = abs(mars_res - saturn_res) % 360
            if m_s_dist > 180: m_s_dist = 360 - m_s_dist
            if m_s_dist < 5:
                malefic_intensity += 8
                reasons.append("Mars conjunct Saturn")
            elif abs(m_s_dist - 90) < 5:
                malefic_intensity += 6
                reasons.append("Mars square Saturn")
            elif abs(m_s_dist - 180) < 5:
                malefic_intensity += 7
                reasons.append("Mars opposition Saturn")
                
            if malefic_intensity >= 5:
                windows.append({
                    "jd": jd,
                    "date": swe.revjul(jd),
                    "intensity": malefic_intensity,
                    "reasons": reasons,
                    "mitigation": "Ritual substitute, fasting, or specific planetary charity (Binder Protocol)."
                })
                
        return windows

