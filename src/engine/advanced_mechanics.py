from typing import Dict, List, Optional, Tuple, Literal
from dataclasses import dataclass, field
import swisseph as swe
import math
from datetime import datetime

from .models import PlanetName, Sign, Planet, Chart, Sect
from .reference_data import (
    DOMICILES, EXALTATIONS, TRIPLICITY_RULERS, EGYPTIAN_TERMS,
    FACES_ORDER, MOIETIES, PLANET_SECTS
)
from .lots import calculate_all_lots, LotName
from .dignities import DignityCalculator
from .calculations import calculate_prenatal_syzygy

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
    def calculate_all_lots(chart: Chart) -> Dict[str, Dict]:
        """
        Calculates the 7 Hermetic Lots as per Paulus Alexandrinus.
        Uses the centralized lots.py engine for calculation, then enriches with metadata.
        """
        from .kakosis import KakosisEngine # Import here to avoid circular dependency
        
        # 1. Calculate Raw Lots
        sect_enum = Sect.DAY if chart.sun_altitude >= 0 else Sect.NIGHT
        raw_lots = calculate_all_lots(chart, sect_enum)
        
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

        # 2. Enrich with Metadata
        final_lots = {}
        
        # Only process the 7 Hermetic Lots here
        hermetic_keys = [
            LotName.FORTUNE.value, LotName.SPIRIT.value,
            LotName.NECESSITY.value, LotName.EROS.value,
            LotName.COURAGE.value, LotName.VICTORY.value,
            LotName.NEMESIS.value
        ]
        
        for key in hermetic_keys:
            if key in raw_lots:
                lon = raw_lots[key]
                sign = get_sign_from_lon(lon)
                domicile = DOMICILES.get(sign)
                house_num = get_house(lon)
                ruler_name = domicile if domicile else "Unknown"
                
                # --- STATUS LOGIC (Kakosis) ---
                status_messages = []
                maltreatment_details = []
                
                # A. Check Lot Maltreatment (Virtual Planet)
                # We create a dummy Planet object for the Lot
                # Name it something distinct so Kakosis doesn't think it's a Malefic itself
                lot_planet = Planet(
                    name=PlanetName.NORTH_NODE, # Placeholder enum, name doesn't matter for target
                    longitude=lon,
                    speed=0.0
                )
                # Monkey-patch name for report clarity if needed, or just rely on 'Lot' context
                # But Kakosis checks if 'planet.name' is a malefic. 
                # North Node isn't in MALEFICS list, so it's safe as a target.

                lot_conditions = KakosisEngine.check_maltreatments(lot_planet, chart)
                
                if lot_conditions:
                    status_messages.append("Lot Maltreated")
                    for c in lot_conditions:
                        maltreatment_details.append(f"[Lot] {c.description}")

                # B. Check Ruler Maltreatment
                ruler_obj = next((p for p in chart.planets if p.name == ruler_name), None)
                if ruler_obj:
                    ruler_conditions = KakosisEngine.check_maltreatments(ruler_obj, chart)
                    if ruler_conditions:
                        status_messages.append("Ruler Maltreated")
                        for c in ruler_conditions:
                            maltreatment_details.append(f"[Ruler {ruler_name.value}] {c.description}")
                
                # Final Status String
                if not status_messages:
                    final_status = "Clear"
                else:
                    final_status = " / ".join(status_messages)
                
                final_lots[key] = {
                    "longitude": lon,
                    "sign": sign.value,
                    "house": house_num,
                    "ruler": ruler_name.value if hasattr(ruler_name, 'value') else str(ruler_name),
                    "status": final_status,
                    "maltreatment_details": maltreatment_details
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
    def get_dignity_score(lon: float, planet: PlanetName, is_day: bool) -> int:
        """
        Uses DignityCalculator to get the Almuten-specific score (positive essential dignities).
        """
        sect = Sect.DAY if is_day else Sect.NIGHT
        dignity = DignityCalculator.calculate_planet_dignity(planet, lon, sect)
        
        # Almuten Figuris (Ibn Ezra) sums positive essential strengths:
        # Domicile (5), Exaltation (4), Triplicity (3), Term (2), Face (1).
        breakdown = dignity.get("score_breakdown", {})
        
        return (
            breakdown.get("domicile", 0) +
            breakdown.get("exaltation", 0) +
            breakdown.get("triplicity", 0) +
            breakdown.get("term", 0) +
            breakdown.get("face", 0)
        )

    @staticmethod
    def get_planet_house(lon: float, houses: Dict[int, float]) -> int:
        """
        Uses DignityCalculator for consistent house placement.
        """
        return DignityCalculator.get_house_number(lon, 0.0, houses)

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
            
        syz_lon, syz_type = calculate_prenatal_syzygy(chart.jd or 0.0)
        
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

# ==========================================
# 5. DODECATEMORIA (The Twelfth-Part)
# ==========================================

class DodecatemoriaEngine:
    @staticmethod
    def calculate_dodecatemoria_valens(longitude: float) -> float:
        """
        Calculates the 12-fold Dodecatemoria (Valens/Standard).
        Formula: Longitude + (DegreeInSign * 12).
        Projects the sign's micro-zodiac onto the full zodiac.
        """
        deg_in_sign = longitude % 30.0
        sign_start = (longitude // 30) * 30
        
        # Projection arc is degree * 12
        arc = deg_in_sign * 12.0
        return (longitude + arc) % 360.0

    @staticmethod
    def calculate_dodecatemoria_paul(longitude: float) -> float:
        """
        Calculates the 13-fold Dodecatemoria (Paul of Alexandria).
        Formula: Longitude + (DegreeInSign * 13).
        Intended for 'Apokatastasis' (Cyclical Return).
        """
        deg_in_sign = longitude % 30.0
        sign_start = (longitude // 30) * 30
        
        # Projection arc is degree * 13 (Cyclical variant)
        arc = deg_in_sign * 13.0
        return (longitude + arc) % 360.0

    @staticmethod
    def get_dodecatemoria_data(chart: Chart, is_valens: bool = True) -> Dict[str, Dict]:
        """
        Calculates Dodecatemoria for all planets and return their signs and rulers.
        """
        results = {}
        for p in chart.planets:
            if is_valens:
                lon = DodecatemoriaEngine.calculate_dodecatemoria_valens(p.longitude)
                method = "Valens (x12)"
            else:
                lon = DodecatemoriaEngine.calculate_dodecatemoria_paul(p.longitude)
                method = "Paul (x13)"
                
            sign = get_sign_from_lon(lon)
            domicile = DOMICILES[sign]
            
            # Sub-dignity: Which Egyptian Term is it in?
            term_ruler = "Unknown"
            deg_in_sign = lon % 30
            for term_p, limit in EGYPTIAN_TERMS[sign]:
                if deg_in_sign < limit:
                    term_ruler = term_p.value if hasattr(term_p, 'value') else str(term_p)
                    break
            
            results[p.name.value] = {
                "method": method,
                "longitude": lon,
                "sign": sign.value,
                "ruler": domicile.value,
                "term_ruler": term_ruler
            }
        return results

