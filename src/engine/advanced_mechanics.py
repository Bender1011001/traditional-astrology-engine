from typing import Dict, List, Optional, Tuple, Literal
from dataclasses import dataclass, field
import swisseph as swe
import math
from datetime import datetime

from .models import PlanetName, Sign, Planet, Chart
from .reference_data import (
    DOMICILES, EXALTATIONS, TRIPLICITY_RULERS, EGYPTIAN_TERMS, 
    FACES_ORDER, MOIETIES, PLANET_SECTS
)

def normalize_deg(deg: float) -> float:
    return deg % 360.0

def get_sign_from_lon(lon: float) -> Sign:
    idx = int(lon / 30)
    return list(Sign)[idx]

def get_sect(sun_alt: float) -> Literal["DAY", "NIGHT"]:
    return "DAY" if sun_alt >= 0 else "NIGHT"

# ==========================================
# 1. HERMETIC LOTS (Why wait? Fate is now.)
# ==========================================

@dataclass
class LotResult:
    name: str
    longitude: float
    sign: Sign
    house_number: int # 1-12
    ruler: PlanetName

class HermeticLotEngine:
    @staticmethod
    def calculate_lot(asc: float, a_lon: float, b_lon: float) -> float:
        """
        Generic Lot Formula: Asc + (B - A)
        Vector from A to B projected from Asc.
        """
        return normalize_deg(asc + b_lon - a_lon)

    @staticmethod
    def calculate_all_lots(chart: Chart) -> Dict[str, LotResult]:
        """
        Calculates the 7 Hermetic Lots as per Paulus Alexandrinus.
        Requires Chart object with planetary positions.
        """
        sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
        moon = next(p for p in chart.planets if p.name == PlanetName.MOON)
        mercury = next(p for p in chart.planets if p.name == PlanetName.MERCURY)
        venus = next(p for p in chart.planets if p.name == PlanetName.VENUS)
        mars = next(p for p in chart.planets if p.name == PlanetName.MARS)
        jupiter = next(p for p in chart.planets if p.name == PlanetName.JUPITER)
        saturn = next(p for p in chart.planets if p.name == PlanetName.SATURN)
        
        asc = chart.ascendant
        sect = get_sect(chart.sun_altitude)
        
        lots = {}
        
        # Helper to get house
        def get_house(lon: float) -> int:
            houses = chart.houses
            l = lon % 360.0
            for i in range(1, 13):
                # Current house: i
                # Next house: i+1 (or 1 if 12)
                cusp_curr = houses[i] % 360.0
                next_idx = (i % 12) + 1
                cusp_next = houses[next_idx] % 360.0
                
                if cusp_curr <= cusp_next:
                    if cusp_curr <= l < cusp_next:
                        return i
                else:
                    # House crosses 0 degrees (Pisces -> Aries)
                    if l >= cusp_curr or l < cusp_next:
                        return i
            return 1 # Fallback

        # 1. Fortune (Tyche) & Spirit (Daimon)
        if sect == "DAY":
            # Fortune: Asc + Moon - Sun
            fort_lon = HermeticLotEngine.calculate_lot(asc, sun.longitude, moon.longitude)
            # Spirit: Asc + Sun - Moon
            spir_lon = HermeticLotEngine.calculate_lot(asc, moon.longitude, sun.longitude)
        else:
            # Fortune: Asc + Sun - Moon
            fort_lon = HermeticLotEngine.calculate_lot(asc, moon.longitude, sun.longitude)
            # Spirit: Asc + Moon - Sun
            spir_lon = HermeticLotEngine.calculate_lot(asc, sun.longitude, moon.longitude)
            
        lots["Fortune"] = {"lon": fort_lon}
        lots["Spirit"] = {"lon": spir_lon}
        
        # 2. Planetary Lots
        # Paulus formulas:
        # Necessity (Mercury): Anchor Fortune. Day: Merc->Fort.
        # Eros (Venus): Anchor Spirit. Day: Spir->Ven.
        # Courage (Mars): Anchor Fortune. Day: Mars->Fort.
        # Victory (Jupiter): Anchor Spirit. Day: Spir->Jup.
        # Nemesis (Saturn): Anchor Fortune. Day: Sat->Fort.
        
        # Note: B - A (Target - Origin)
        # Vector A->B is B-A.
        # Formula: Asc + (Target - Origin)
        
        if sect == "DAY":
            nec_lon = HermeticLotEngine.calculate_lot(asc, mercury.longitude, fort_lon)
            eros_lon = HermeticLotEngine.calculate_lot(asc, spir_lon, venus.longitude)
            cour_lon = HermeticLotEngine.calculate_lot(asc, mars.longitude, fort_lon)
            vic_lon = HermeticLotEngine.calculate_lot(asc, spir_lon, jupiter.longitude)
            nem_lon = HermeticLotEngine.calculate_lot(asc, saturn.longitude, fort_lon)
        else:
            # Night Reversal
            # Necessity: Fort->Merc
            nec_lon = HermeticLotEngine.calculate_lot(asc, fort_lon, mercury.longitude)
            # Eros: Ven->Spir
            eros_lon = HermeticLotEngine.calculate_lot(asc, venus.longitude, spir_lon)
            # Courage: Fort->Mars
            cour_lon = HermeticLotEngine.calculate_lot(asc, fort_lon, mars.longitude)
            # Victory: Jup->Spir
            vic_lon = HermeticLotEngine.calculate_lot(asc, jupiter.longitude, spir_lon)
            # Nemesis: Fort->Sat
            nem_lon = HermeticLotEngine.calculate_lot(asc, fort_lon, saturn.longitude)
            
        lots["Necessity"] = {"lon": nec_lon}
        lots["Eros"] = {"lon": eros_lon}
        lots["Courage"] = {"lon": cour_lon}
        lots["Victory"] = {"lon": vic_lon}
        lots["Nemesis"] = {"lon": nem_lon}
        
        # Add basic data
        final_lots = {}
        for name, data in lots.items():
            lon = data["lon"]
            sign = get_sign_from_lon(lon)
            domicile = DOMICILES.get(sign)
            house_num = get_house(lon)
            
            final_lots[name] = {
                "longitude": lon,
                "sign": sign.value,
                "house": house_num,
                "ruler": domicile.value if domicile else "Unknown"
            }
            
        return final_lots

# ==========================================
# 2. MONOMOIRIA (The Fractal of Fate)
# ==========================================

class MonomoiriaEngine:
    CHALDEAN_DESC = [
        PlanetName.SATURN, PlanetName.JUPITER, PlanetName.MARS, 
        PlanetName.SUN, PlanetName.VENUS, PlanetName.MERCURY, PlanetName.MOON
    ]
    
    @staticmethod
    def get_zoidion_monomoiria(longitude: float) -> PlanetName:
        """
        Chapter 5 System: Sign Ruler starts, then descends Chaldean.
        Resets at sign boundary.
        """
        sign = get_sign_from_lon(longitude)
        deg_in_sign = int(longitude % 30) # 0-29
        
        start_planet = DOMICILES[sign]
        
        # Find index in Chaldean order
        try:
            start_idx = MonomoiriaEngine.CHALDEAN_DESC.index(start_planet)
        except ValueError:
            # Handle Node/Ur/Ne/Pl if they ever sneak in? No, should be classical 7.
            # If Domicile is missing (unlikely), fallback.
            return PlanetName.SATURN 

        # Shift by degree
        # Degree 1 (idx 0) = start_planet
        # Degree 2 (idx 1) = next planet
        current_idx = (start_idx + deg_in_sign) % 7
        return MonomoiriaEngine.CHALDEAN_DESC[current_idx]

    @staticmethod
    def get_trigonal_monomoiria(longitude: float, is_day_chart: bool, sun_sign: Sign, moon_sign: Sign) -> PlanetName:
        """
        Chapter 32 System: Rectification tool.
        Seed based on Triplicity of Sect Light.
        """
        target_sign = get_sign_from_lon(longitude)
        deg_in_sign = int(longitude % 30)

        # 1. Determine Sect Light
        sect_light_sign = sun_sign if is_day_chart else moon_sign
        
        # 2. Determine Triplicity of Sect Light Sign (Use Dorothean)
        # Paul's rules are very specific: 
        # Fire: Sun(D) / Jup(N)
        # Earth: Ven(D) / Moon(N)
        # Air: Sat(D) / Merc(N)
        # Water: Ven(D) / Mars(N) - NOTE VENUS FOR DAY WATER
        
        from .reference_data import SIGN_ELEMENTS
        element = SIGN_ELEMENTS[sect_light_sign]
        
        seed = None
        if element == "Fire":
            seed = PlanetName.SUN if is_day_chart else PlanetName.JUPITER
        elif element == "Earth":
            seed = PlanetName.VENUS if is_day_chart else PlanetName.MOON
        elif element == "Air":
            seed = PlanetName.SATURN if is_day_chart else PlanetName.MERCURY
        elif element == "Water":
            seed = PlanetName.VENUS if is_day_chart else PlanetName.MARS
            
        if not seed:
            seed = PlanetName.SUN # Fallback

        # 3. Progression
        # The seed starts the Triplicity. But is it per sign?
        # The text says: "start from the star that welcomes this light trigonally... 
        # apportioning one degree to each star in the order of zoidia (Chaldean)".
        # Wait, the table shows the seed rule is consistent for the whole Triplicity, NOT resetting per sign?
        # "These tables are applicable to any sign falling within the respective Triplicity."
        # Yes.
        
        start_idx = MonomoiriaEngine.CHALDEAN_DESC.index(seed)
        current_idx = (start_idx + deg_in_sign) % 7
        return MonomoiriaEngine.CHALDEAN_DESC[current_idx]

# ==========================================
# 3. ALMUTEN FIGURIS (The Guardian)
# ==========================================

@dataclass
class AlmutenScore:
    planet: PlanetName
    essential_score: int
    house_score: int
    day_hour_score: int
    total_score: int
    breakdown: Dict[str, int]

@dataclass
class AlmutenResult:
    winner: PlanetName
    scores: Dict[str, AlmutenScore]
    hylegs: Dict[str, float]

HOUSE_SCORES_EZRA = {
    1: 12, 10: 11, 7: 10, 4: 9, 
    11: 8, 5: 7, 2: 6, 9: 5, 
    3: 4, 8: 3, 6: 2, 12: 1
}

class AlmutenEngine:
    
    @staticmethod
    def calculate_prenatal_syzygy(jd_utc: float) -> Tuple[float, str]:
        """
        Finds the position of the SAN (Syzygy Ante Nativitatem) using Iterative Newton-Raphson method.
        Resolves to True Syzygy within acceptable tolerance (< 1 sec).
        """
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        
        # 1. Determine Target from Birth chart
        res_sun = swe.calc_ut(jd_utc, swe.SUN, flags)
        res_moon = swe.calc_ut(jd_utc, swe.MOON, flags)
        
        s_l = res_sun[0][0]
        m_l = res_moon[0][0]
        
        phase = (m_l - s_l) % 360.0
        
        if phase < 180:
            target_type = "New"
            target_angle = 0.0
        else:
            target_type = "Full"
            target_angle = 180.0
            
        # 2. Newton-Raphson Search
        t = jd_utc
        # Initial guess: approximate backward by phase diff
        # Avg rel speed ~12.19 deg/day
        diff_est = phase - target_angle
        if diff_est < 0: diff_est += 360
        t -= (diff_est / 12.19)
        
        for _ in range(15):
            r_sun = swe.calc_ut(t, swe.SUN, flags)
            r_moon = swe.calc_ut(t, swe.MOON, flags)
            
            s_l, s_v = r_sun[0][0], r_sun[0][3]
            m_l, m_v = r_moon[0][0], r_moon[0][3]
            
            curr_phase = (m_l - s_l) % 360.0
            
            # Delta = Current - Target
            delta = curr_phase - target_angle
            
            # Unwrap
            if delta > 180: delta -= 360
            if delta < -180: delta += 360
            
            if abs(delta) < 0.00001:
                # Result
                final_lon = m_l if target_type == "Full" else s_l
                return (final_lon, target_type)
            
            v_rel = m_v - s_v
            t -= (delta / v_rel)
            
        return (s_l, target_type)

    @staticmethod
    def get_dignity_score(lon: float, planet: PlanetName, is_day: bool) -> int:
        sign = get_sign_from_lon(lon)
        deg = lon % 30
        score = 0
        
        # Domicile (5)
        if DOMICILES[sign] == planet: score += 5
        # Exaltation (4)
        if EXALTATIONS.get(sign) == planet: score += 4
            
        # Triplicity (3)
        from .reference_data import SIGN_ELEMENTS, DOROTHEAN_TRIPLICITY
        elem = SIGN_ELEMENTS[sign]
        rulers = DOROTHEAN_TRIPLICITY[elem]
        # Dorothean: Day/Night/Participating. Usually primary ruler gets score?
        # Standard Almuten adds 3 if ANY triplicity ruler.
        if planet in rulers: score += 3
            
        # Term (2)
        terms = EGYPTIAN_TERMS[sign]
        for p, limit in terms:
            if deg < limit:
                if p == planet: score += 2
                break
        
        # Face (1)
        face_idx = int(deg / 10)
        sign_list = list(Sign)
        s_idx = sign_list.index(sign)
        global_f_idx = s_idx * 3 + face_idx
        if FACES_ORDER[global_f_idx % 7] == planet: score += 1
            
        return score

    @staticmethod
    def get_planet_house(lon: float, houses: Dict[int, float]) -> int:
        cusps = [houses[i] for i in range(1, 13)]
        l = lon % 360.0
        for i in range(12):
            c1 = cusps[i] % 360.0
            c2 = cusps[(i + 1) % 12] % 360.0
            if c1 <= c2:
                if c1 <= l < c2: return i + 1
            else:
                if l >= c1 or l < c2: return i + 1
        return 1

    @staticmethod
    def calculate_almuten(chart: Chart, day_lord: Optional[PlanetName] = None, hour_lord: Optional[PlanetName] = None) -> AlmutenResult:
        # 1. Hylegs
        asc = chart.ascendant
        sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
        moon = next(p for p in chart.planets if p.name == PlanetName.MOON)
        
        sect = get_sect(chart.sun_altitude)
        is_day = (sect == "DAY")
        
        if is_day:
            pof = normalize_deg(asc + moon.longitude - sun.longitude)
        else:
            pof = normalize_deg(asc + sun.longitude - moon.longitude)
            
        syz_lon, syz_type = AlmutenEngine.calculate_prenatal_syzygy(chart.jd or 0.0)
        
        hylegs = {
            "Sun": sun.longitude,
            "Moon": moon.longitude,
            "Ascendant": asc,
            "Fortune": pof,
            "Syzygy": syz_lon
        }
        
        candidates = [p for p in PlanetName if p not in [PlanetName.NORTH_NODE, PlanetName.SOUTH_NODE, PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]]
        cand_scores = {p: 0 for p in candidates}
        breakdowns = {p: {"essential": 0, "house": 0, "day_hour": 0} for p in candidates}

        # 2. Essential Dignity Loop
        for h_name, h_lon in hylegs.items():
            for p in candidates:
                s = AlmutenEngine.get_dignity_score(h_lon, p, is_day)
                cand_scores[p] += s
                breakdowns[p]["essential"] += s
                
        # 3. Day/Hour Rulers (Day: 7, Hour: 6)
        if day_lord and day_lord in candidates:
            cand_scores[day_lord] += 7
            breakdowns[day_lord]["day_hour"] += 7
            
        if hour_lord and hour_lord in candidates:
            cand_scores[hour_lord] += 6
            breakdowns[hour_lord]["day_hour"] += 6
        
        # 4. House Scores
        for p_name in candidates:
            try:
                planet_obj = next(p for p in chart.planets if p.name == p_name)
                h_num = AlmutenEngine.get_planet_house(planet_obj.longitude, chart.houses or {})
                score = HOUSE_SCORES_EZRA.get(h_num, 0)
                cand_scores[p_name] += score
                breakdowns[p_name]["house"] += score
            except StopIteration:
                pass # Planet not in chart object?
        
        # Final Winner
        winner = max(cand_scores, key=cand_scores.get)
        
        final_scores = {}
        for p in candidates:
            final_scores[p.value] = AlmutenScore(
                planet=p,
                essential_score=breakdowns[p]["essential"],
                house_score=breakdowns[p]["house"],
                day_hour_score=breakdowns[p]["day_hour"],
                total_score=cand_scores[p],
                breakdown={}
            )
            
        return AlmutenResult(
            winner=winner,
            scores=final_scores,
            hylegs=hylegs
        )

# ==========================================
# 4. DORYPHORY (The Bodyguards)
# ==========================================

@dataclass
class DoryphoryInstance:
    planet: PlanetName
    type: str # Bodily, Aspectual
    related_luminary: str # Sun, Moon
    score: int # Qualitative score

class DoryphoryEngine:
    @staticmethod
    def check_doryphory(chart: Chart) -> List[DoryphoryInstance]:
        instances = []
        sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
        moon = next(p for p in chart.planets if p.name == PlanetName.MOON)
        
        # Solar Doryphory (Rise Before Sun)
        # Check planets in range [SunLon - 30, SunLon]
        for p in chart.planets:
            if p.name in [PlanetName.SUN, PlanetName.MOON, PlanetName.NORTH_NODE, PlanetName.SOUTH_NODE]: continue
            
            diff = (sun.longitude - p.longitude) % 360
            if 0 < diff < 35: # Within ~1 sign preceding
                # Check distance from sun (Combustion < 8)
                if diff < 8:
                    continue # Combust guards are useless
                
                instances.append(DoryphoryInstance(
                    planet=p.name,
                    type="Bodily/Oriental",
                    related_luminary="Sun",
                    score=10
                ))
        
        # Lunar Doryphory (Rise After Moon)
        # Check planets in range [MoonLon, MoonLon + 30]
        for p in chart.planets:
             if p.name in [PlanetName.SUN, PlanetName.MOON, PlanetName.NORTH_NODE, PlanetName.SOUTH_NODE]: continue
             
             diff = (p.longitude - moon.longitude) % 360
             if 0 < diff < 35:
                 instances.append(DoryphoryInstance(
                    planet=p.name,
                    type="Bodily/Occidental",
                    related_luminary="Moon",
                    score=10
                ))
                
        return instances
