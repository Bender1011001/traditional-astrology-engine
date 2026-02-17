
import logging
from typing import Dict, List, Tuple, Optional
from enum import Enum, auto
from .models import PlanetName, Sign, Sect, Chart, Planet
from .reference_data import (
    TRIPLICITY_RULERS as REF_TRIPLICITY,
    SIGN_ELEMENTS,
    EGYPTIAN_TERMS,
    PTOLEMAIC_TERMS,
    CHALDEAN_TERMS,
    DOROTHEAN_TRIPLICITY,
    PTOLEMAIC_TRIPLICITY,
    FACES_ORDER,
    DOMICILES as REF_DOMICILES,
    EXALTATIONS as REF_EXALTATIONS
)
class TriplicityScheme(Enum):
    DOROTHEAN = "Dorothean"
    PTOLEMAIC_SECT_GATED = "Ptolemaic (sect-gated)"

class TermSystem(Enum):
    EGYPTIAN = "Egyptian"
    PTOLEMAIC = "Ptolemaic"
    CHALDEAN = "Chaldean"

class DignityCalculator:
    # Scores
    DOMICILE = 5
    EXALTATION = 4
    TRIPLICITY = 3
    TERM = 2
    FACE = 1
    PEREGRINE = -5
    DETRIMENT = -5
    FALL = -4

    # Domiciles & Exaltations
    DOMICILES = {
        PlanetName.SUN: [Sign.LEO],
        PlanetName.MOON: [Sign.CANCER],
        PlanetName.MERCURY: [Sign.GEMINI, Sign.VIRGO],
        PlanetName.VENUS: [Sign.TAURUS, Sign.LIBRA],
        PlanetName.MARS: [Sign.ARIES, Sign.SCORPIO],
        PlanetName.JUPITER: [Sign.SAGITTARIUS, Sign.PISCES],
        PlanetName.SATURN: [Sign.CAPRICORN, Sign.AQUARIUS]
    }

    DETRIMENTS = {
        PlanetName.SUN: [Sign.AQUARIUS],
        PlanetName.MOON: [Sign.CAPRICORN],
        PlanetName.MERCURY: [Sign.SAGITTARIUS, Sign.PISCES],
        PlanetName.VENUS: [Sign.ARIES, Sign.SCORPIO],
        PlanetName.MARS: [Sign.LIBRA, Sign.TAURUS],
        PlanetName.JUPITER: [Sign.GEMINI, Sign.VIRGO],
        PlanetName.SATURN: [Sign.CANCER, Sign.LEO]
    }

    EXALTATIONS = {
        PlanetName.SUN: Sign.ARIES,
        PlanetName.MOON: Sign.TAURUS,
        PlanetName.MERCURY: Sign.VIRGO,
        PlanetName.VENUS: Sign.PISCES,
        PlanetName.MARS: Sign.CAPRICORN,
        PlanetName.JUPITER: Sign.CANCER,
        PlanetName.SATURN: Sign.LIBRA
    }

    FALLS = {
        PlanetName.SUN: Sign.LIBRA,
        PlanetName.MOON: Sign.SCORPIO,
        PlanetName.MERCURY: Sign.PISCES,
        PlanetName.VENUS: Sign.VIRGO,
        PlanetName.MARS: Sign.CANCER,
        PlanetName.JUPITER: Sign.CAPRICORN,
        PlanetName.SATURN: Sign.ARIES
    }

    # Dorothean Triplicity (Day, Night, Participant)
    TRIPLICITY_RULERS = {
        "FIRE": (PlanetName.SUN, PlanetName.JUPITER, PlanetName.SATURN),
        "EARTH": (PlanetName.VENUS, PlanetName.MOON, PlanetName.MARS),
        "AIR": (PlanetName.SATURN, PlanetName.MERCURY, PlanetName.JUPITER),
        "WATER": (PlanetName.VENUS, PlanetName.MARS, PlanetName.MOON)
    }

    ZODIAC_ELEMENTS = {
        Sign.ARIES: "FIRE", Sign.LEO: "FIRE", Sign.SAGITTARIUS: "FIRE",
        Sign.TAURUS: "EARTH", Sign.VIRGO: "EARTH", Sign.CAPRICORN: "EARTH",
        Sign.GEMINI: "AIR", Sign.LIBRA: "AIR", Sign.AQUARIUS: "AIR",
        Sign.CANCER: "WATER", Sign.SCORPIO: "WATER", Sign.PISCES: "WATER"
    }

    # Valens Egyptian Terms
    # Using format: {SIGN: [(Planet, MaxDegree), ...]}
    TERMS = {
        Sign.ARIES: [("JUPITER", 6), ("VENUS", 12), ("MERCURY", 20), ("MARS", 25), ("SATURN", 30)],
        Sign.TAURUS: [("VENUS", 8), ("MERCURY", 14), ("JUPITER", 22), ("SATURN", 27), ("MARS", 30)],
        Sign.GEMINI: [("MERCURY", 6), ("JUPITER", 12), ("VENUS", 17), ("MARS", 24), ("SATURN", 30)],
        Sign.CANCER: [("MARS", 7), ("VENUS", 13), ("MERCURY", 19), ("JUPITER", 26), ("SATURN", 30)],
        Sign.LEO: [("JUPITER", 6), ("VENUS", 11), ("SATURN", 18), ("MERCURY", 24), ("MARS", 30)],
        Sign.VIRGO: [("MERCURY", 7), ("VENUS", 17), ("JUPITER", 21), ("MARS", 28), ("SATURN", 30)],
        Sign.LIBRA: [("SATURN", 6), ("MERCURY", 14), ("JUPITER", 21), ("VENUS", 28), ("MARS", 30)],
        Sign.SCORPIO: [("MARS", 7), ("VENUS", 11), ("MERCURY", 19), ("JUPITER", 24), ("SATURN", 30)],
        Sign.SAGITTARIUS: [("JUPITER", 12), ("VENUS", 17), ("MERCURY", 21), ("SATURN", 26), ("MARS", 30)],
        Sign.CAPRICORN: [("MERCURY", 7), ("JUPITER", 14), ("VENUS", 22), ("SATURN", 26), ("MARS", 30)],
        Sign.AQUARIUS: [("MERCURY", 7), ("VENUS", 13), ("JUPITER", 20), ("MARS", 25), ("SATURN", 30)],
        Sign.PISCES: [("VENUS", 12), ("JUPITER", 16), ("MERCURY", 19), ("MARS", 28), ("SATURN", 30)]
    }

    # Chaldean Faces
    FACES = {
        Sign.ARIES: ["MARS", "SUN", "VENUS"],
        Sign.TAURUS: ["MERCURY", "MOON", "SATURN"],
        Sign.GEMINI: ["JUPITER", "MARS", "SUN"],
        Sign.CANCER: ["VENUS", "MERCURY", "MOON"],
        Sign.LEO: ["SATURN", "JUPITER", "MARS"],
        Sign.VIRGO: ["SUN", "VENUS", "MERCURY"],
        Sign.LIBRA: ["MOON", "SATURN", "JUPITER"],
        Sign.SCORPIO: ["MARS", "SUN", "VENUS"],
        Sign.SAGITTARIUS: ["MERCURY", "MOON", "SATURN"],
        Sign.CAPRICORN: ["JUPITER", "MARS", "SUN"],
        Sign.AQUARIUS: ["VENUS", "MERCURY", "MOON"],
        Sign.PISCES: ["SATURN", "JUPITER", "MARS"]
    }

    CHALDEAN_ORDER = [
        PlanetName.SATURN,
        PlanetName.JUPITER,
        PlanetName.MARS,
        PlanetName.SUN,
        PlanetName.VENUS,
        PlanetName.MERCURY,
        PlanetName.MOON
    ]

    # Almuten Figuris House Scores (Ibn Ezra)
    ALMUTEN_HOUSE_SCORES = {
        1: 12, 10: 12,
        4: 11, 7: 11,
        2: 10, 11: 10,
        5: 9, 8: 9,
        3: 8, 9: 8,
        6: 7, 12: 7
    }

    # Planetary Joys (Traditional)
    PLANETARY_JOYS = {
        PlanetName.MERCURY: 1,
        PlanetName.MOON: 3,
        PlanetName.VENUS: 5,
        PlanetName.MARS: 6,
        PlanetName.SUN: 9,
        PlanetName.JUPITER: 11,
        PlanetName.SATURN: 12
    }

    # Average Speeds (Approximate degrees per day)
    # Used for Accidental Dignity weighting
    AVERAGE_SPEEDS = {
        PlanetName.SUN: 0.9833,
        PlanetName.MOON: 13.1764,
        PlanetName.MERCURY: 0.9833,
        PlanetName.VENUS: 1.2, # Varies, but 1.2 is often used as "fast" threshold
        PlanetName.MARS: 0.524,
        PlanetName.JUPITER: 0.0831,
        PlanetName.SATURN: 0.0335
    }

    @classmethod
    def get_house_number(cls, longitude: float, ascendant: float, houses: Optional[Dict[int, float]] = None) -> int:
        """Calculates house number using provided cusps (if available), else Whole Sign."""
        if houses:
            if isinstance(houses, dict):
                try:
                    cusps = [houses[i] for i in range(1, 13)]
                except KeyError:
                    cusps = None
            else:
                cusps = list(houses)[:12]

            if cusps and len(cusps) == 12:
                lon = longitude % 360
                for i in range(12):
                    c1 = cusps[i] % 360
                    c2 = cusps[(i + 1) % 12] % 360
                    if c1 <= c2:
                        if c1 <= lon < c2:
                            return i + 1
                    else:
                        if lon >= c1 or lon < c2:
                            return i + 1
                return 1

        asc_sign_idx = int(ascendant / 30) % 12
        p_sign_idx = int(longitude / 30) % 12
        return ((p_sign_idx - asc_sign_idx) % 12) + 1

    @classmethod
    def get_monomoiria_ruler(cls, sign: Sign, degree: float) -> PlanetName:
        """
        Monomoiria (Degree Rulership):
        First degree (0-1) is ruled by the Domicile Ruler,
        then follow the Chaldean Order.
        """
        # Find domicile ruler of the sign
        domicile_ruler = None
        for planet, signs in cls.DOMICILES.items():
            if sign in signs:
                domicile_ruler = planet
                break
        
        if not domicile_ruler:
            return PlanetName.SATURN # Fallback

        # Degree index 0-29
        deg_idx = int(degree)
        
        # Chaldean order starting from domicile ruler
        start_idx = cls.CHALDEAN_ORDER.index(domicile_ruler)
        ruler_idx = (start_idx + deg_idx) % len(cls.CHALDEAN_ORDER)
        return cls.CHALDEAN_ORDER[ruler_idx]

    @classmethod
    def check_hayz_halb(cls, planet_name: PlanetName, longitude: float, chart: Chart) -> Dict:
        """
        Hayz:
            Diurnal Planet (Sun, Jup, Sat): Day chart, Above horizon, Masculine Sign.
            Nocturnal Planet (Moon, Ven, Mar): Night chart, Below horizon, Feminine Sign.
        Halb: Lesser condition (satisfies sect and either horizon or sign condition).
        """
        chart_sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        is_diurnal = planet_name in [PlanetName.SUN, PlanetName.JUPITER, PlanetName.SATURN]
        is_nocturnal = planet_name in [PlanetName.MOON, PlanetName.VENUS, PlanetName.MARS]
        
        # Masculine: Fire/Air. Feminine: Earth/Water.
        sign_idx = int(longitude / 30) % 12
        sign = list(Sign)[sign_idx]
        element = cls.ZODIAC_ELEMENTS[sign]
        is_masculine = element in ["FIRE", "AIR"]
        
        # Above horizon check (using house number for simplicity/consistency)
        house_num = cls.get_house_number(longitude, chart.ascendant, getattr(chart, "houses", None))
        is_above_horizon = house_num >= 7
        
        status = "None"
        details = []
        
        sect_match = (chart_sect == Sect.DAY and is_diurnal) or (chart_sect == Sect.NIGHT and is_nocturnal)
        horizon_match = (is_above_horizon if is_diurnal else not is_above_horizon)
        sign_match = (is_masculine if is_diurnal else not is_masculine)
        
        if sect_match and horizon_match and sign_match:
            status = "Hayz"
            details.append("In Hayz (Sect, Horizon, and Sign match)")
        elif sect_match and (horizon_match or sign_match):
            status = "Halb"
            details.append("In Halb (Sect match plus either Horizon or Sign)")
        elif sect_match:
            status = "In Sect"
            details.append("Matches chart sect only")
            
        return {"status": status, "details": details}

    @classmethod
    def calculate_planet_dignity(cls, planet_name: PlanetName, longitude: float, sect: Sect, term_system: TermSystem = TermSystem.EGYPTIAN) -> Dict:
        """
        Calculates total essential dignity score for a planet.
        """
        sign_idx = int(longitude / 30) % 12
        sign = list(Sign)[sign_idx]
        deg_in_sign = longitude % 30
        
        details = []
        conflicts = []
        score = 0
        
        score_breakdown = {
            "domicile": 0,
            "exaltation": 0,
            "triplicity": 0,
            "term": 0,
            "face": 0,
            "monomoiria": 0,
            "detriment": 0,
            "fall": 0
        }
        
        # 1. Domicile (+5)
        is_domicile = False
        for p, signs in cls.DOMICILES.items():
            if p == planet_name and sign in signs:
                is_domicile = True
                break
        
        if is_domicile:
            score += cls.DOMICILE
            score_breakdown["domicile"] = cls.DOMICILE
            details.append("Domicile (+5)")
        else:
            is_detriment = False
            for p, signs in cls.DETRIMENTS.items():
                if p == planet_name and sign in signs:
                    is_detriment = True
                    break
            if is_detriment:
                score += cls.DETRIMENT
                score_breakdown["detriment"] = cls.DETRIMENT
                details.append("Detriment (-5)")

        # 2. Exaltation (+4)
        if cls.EXALTATIONS.get(planet_name) == sign:
            score += cls.EXALTATION
            score_breakdown["exaltation"] = cls.EXALTATION
            details.append("Exaltation (+4)")
        elif cls.FALLS.get(planet_name) == sign:
            score += cls.FALL
            score_breakdown["fall"] = cls.FALL
            details.append("Fall (-4)")

        # 3. Triplicity (+3)
        element = cls.ZODIAC_ELEMENTS.get(sign)
        rulers = cls.TRIPLICITY_RULERS.get(element)
        if rulers:
            # Day, Night, Participant
            if (sect == Sect.DAY and planet_name == rulers[0]) or \
               (sect == Sect.NIGHT and planet_name == rulers[1]):
                score += cls.TRIPLICITY
                score_breakdown["triplicity"] = cls.TRIPLICITY
                details.append(f"Triplicity ({sect.value}) (+3)")
            elif planet_name == rulers[2]:
                score += 1
                score_breakdown["triplicity"] = 1
                details.append("Triplicity (Participant) (+1)")

        # 4. Terms (+2)
        term_table = EGYPTIAN_TERMS
        if term_system == TermSystem.PTOLEMAIC:
            term_table = PTOLEMAIC_TERMS
        elif term_system == TermSystem.CHALDEAN:
            term_table = CHALDEAN_TERMS

        bounds = term_table.get(sign)
        if bounds:
            for ruler_val, limit in bounds:
                # Convert string ruler to PlanetName if necessary
                ruler_name = ruler_val
                if isinstance(ruler_val, str):
                    ruler_name = PlanetName[ruler_val.upper()] if ruler_val.upper() in PlanetName.__members__ else None
                
                if deg_in_sign < limit:
                    if ruler_name == planet_name:
                        score += cls.TERM
                        score_breakdown["term"] = cls.TERM
                        details.append(f"Term ({term_system.value}) (+2)")
                    break

        # 5. Face (+1)
        face_idx = int(deg_in_sign / 10)
        face_ruler_val = cls.FACES[sign][face_idx]
        face_ruler_name = PlanetName[face_ruler_val.upper()] if isinstance(face_ruler_val, str) else face_ruler_val
        if face_ruler_name == planet_name:
            score += cls.FACE
            score_breakdown["face"] = cls.FACE
            details.append("Face (+1)")

        # 6. Monomoiria
        mono_ruler = cls.get_monomoiria_ruler(sign, deg_in_sign)
        if mono_ruler == planet_name:
            score += 1
            score_breakdown["monomoiria"] = 1
            details.append(f"Monomoiria (+1, Ruler: {mono_ruler.value})")
        else:
            details.append(f"Monomoiria Ruler: {mono_ruler.value}")

        # 7. Collect variant information for report
        element = cls.ZODIAC_ELEMENTS.get(sign)
        dorothean_rulers = cls.TRIPLICITY_RULERS.get(element)
        ptolemaic_rulers = PTOLEMAIC_TRIPLICITY.get(element) # From reference_data
        
        is_ruler_dorothean = planet_name in (dorothean_rulers[0], dorothean_rulers[1])
        is_ruler_ptolemaic = planet_name in (ptolemaic_rulers[0], ptolemaic_rulers[1]) if ptolemaic_rulers else False

        egyptian_bounds = EGYPTIAN_TERMS.get(sign, [])
        egyptian_term_ruler = None
        egyptian_term_limit = 0
        for p, limit in egyptian_bounds:
            if deg_in_sign < limit:
                egyptian_term_ruler = PlanetName[p.upper()] if isinstance(p, str) else p
                egyptian_term_limit = limit
                break

        ptolemaic_bounds = PTOLEMAIC_TERMS.get(sign, [])
        ptolemaic_term_ruler = None
        ptolemaic_term_limit = 0
        for p, limit in ptolemaic_bounds:
            if deg_in_sign < limit:
                ptolemaic_term_ruler = PlanetName[p.upper()] if isinstance(p, str) else p
                ptolemaic_term_limit = limit
                break

        return {
            "total_score": score,
            "score_breakdown": score_breakdown,
            "details": details,
            "conflicts": conflicts,
            "variants": {
                "triplicity": {
                    "used": "Dorothean",
                    "sect": sect.value,
                    "dorothean": {
                        "day": dorothean_rulers[0].value,
                        "night": dorothean_rulers[1].value,
                        "participant": dorothean_rulers[2].value,
                        "planet_is_ruler": is_ruler_dorothean
                    },
                    "ptolemaic": {
                        "day": ptolemaic_rulers[0].value if ptolemaic_rulers else None,
                        "night": ptolemaic_rulers[1].value if ptolemaic_rulers else None,
                        "planet_is_ruler": is_ruler_ptolemaic
                    }
                },
                "terms": {
                    "used": "Egyptian",
                    "egyptian": {
                        "ruler": egyptian_term_ruler.value if egyptian_term_ruler else None,
                        "limit": egyptian_term_limit
                    },
                    "ptolemaic": {
                        "ruler": ptolemaic_term_ruler.value if ptolemaic_term_ruler else None,
                        "limit": ptolemaic_term_limit
                    }
                }
            },
            "sign": sign.value,
            "degree": deg_in_sign
        }

    @classmethod
    def calculate_planet_dignity_variant(
        cls,
        planet_name: PlanetName,
        longitude: float,
        sect: Sect,
        term_system: TermSystem = TermSystem.EGYPTIAN,
        triplicity_scheme: TriplicityScheme = TriplicityScheme.DOROTHEAN,
        include_monomoiria: bool = True,
    ) -> Dict:
        """
        Variant-capable essential dignity calculator.

        This is used for method-comparison reporting where traditional authorities disagree on:
        - Dorothean (day/night/participant) vs Ptolemaic (day/night) triplicity rulership
        - Egyptian vs Ptolemaic bounds/terms

        Notes:
        - PTOLEMAIC_SECT_GATED: in Day charts only the Day triplicity ruler has rights; in Night charts
          only the Night ruler. (Matches how receptions are sect-gated in STANDARD_LILLY mode.)
        - `include_monomoiria` defaults True to match this engine's existing scoring behavior.
        """
        sign_idx = int(longitude / 30) % 12
        sign = list(Sign)[sign_idx]
        deg_in_sign = longitude % 30

        details: List[str] = []
        conflicts: List[str] = []
        score = 0

        score_breakdown = {
            "domicile": 0,
            "exaltation": 0,
            "triplicity": 0,
            "term": 0,
            "face": 0,
            "monomoiria": 0,
            "detriment": 0,
            "fall": 0,
        }

        # 1. Domicile (+5) / Detriment (-5)
        is_domicile = any(p == planet_name and sign in signs for p, signs in cls.DOMICILES.items())
        if is_domicile:
            score += cls.DOMICILE
            score_breakdown["domicile"] = cls.DOMICILE
            details.append("Domicile (+5)")
        else:
            is_detriment = any(p == planet_name and sign in signs for p, signs in cls.DETRIMENTS.items())
            if is_detriment:
                score += cls.DETRIMENT
                score_breakdown["detriment"] = cls.DETRIMENT
                details.append("Detriment (-5)")

        # 2. Exaltation (+4) / Fall (-4)
        if cls.EXALTATIONS.get(planet_name) == sign:
            score += cls.EXALTATION
            score_breakdown["exaltation"] = cls.EXALTATION
            details.append("Exaltation (+4)")
        elif cls.FALLS.get(planet_name) == sign:
            score += cls.FALL
            score_breakdown["fall"] = cls.FALL
            details.append("Fall (-4)")

        # 3. Triplicity (+3) / participant (+1, Dorothean only)
        element = cls.ZODIAC_ELEMENTS.get(sign)
        if element:
            if triplicity_scheme == TriplicityScheme.DOROTHEAN:
                rulers = cls.TRIPLICITY_RULERS.get(element)
                if rulers:
                    if (sect == Sect.DAY and planet_name == rulers[0]) or (sect == Sect.NIGHT and planet_name == rulers[1]):
                        score += cls.TRIPLICITY
                        score_breakdown["triplicity"] = cls.TRIPLICITY
                        details.append(f"Triplicity ({TriplicityScheme.DOROTHEAN.value}, {sect.value}) (+3)")
                    elif len(rulers) >= 3 and planet_name == rulers[2]:
                        score += 1
                        score_breakdown["triplicity"] = 1
                        details.append(f"Triplicity (Participant, {TriplicityScheme.DOROTHEAN.value}) (+1)")
            else:
                pt = PTOLEMAIC_TRIPLICITY.get(element)
                if pt and len(pt) >= 2:
                    day_ruler, night_ruler = pt[0], pt[1]
                    if sect == Sect.DAY and planet_name == day_ruler:
                        score += cls.TRIPLICITY
                        score_breakdown["triplicity"] = cls.TRIPLICITY
                        details.append(f"Triplicity ({TriplicityScheme.PTOLEMAIC_SECT_GATED.value}, Day) (+3)")
                    elif sect == Sect.NIGHT and planet_name == night_ruler:
                        score += cls.TRIPLICITY
                        score_breakdown["triplicity"] = cls.TRIPLICITY
                        details.append(f"Triplicity ({TriplicityScheme.PTOLEMAIC_SECT_GATED.value}, Night) (+3)")

        # 4. Terms (+2)
        term_table = EGYPTIAN_TERMS
        if term_system == TermSystem.PTOLEMAIC:
            term_table = PTOLEMAIC_TERMS
        elif term_system == TermSystem.CHALDEAN:
            term_table = CHALDEAN_TERMS

        bounds = term_table.get(sign)
        if bounds:
            for ruler_val, limit in bounds:
                ruler_name = ruler_val
                if isinstance(ruler_val, str):
                    ruler_name = PlanetName[ruler_val.upper()] if ruler_val.upper() in PlanetName.__members__ else None
                if deg_in_sign < limit:
                    if ruler_name == planet_name:
                        score += cls.TERM
                        score_breakdown["term"] = cls.TERM
                        details.append(f"Term ({term_system.value}) (+2)")
                    break

        # 5. Face (+1)
        face_idx = int(deg_in_sign / 10)
        face_ruler_val = cls.FACES[sign][face_idx]
        face_ruler_name = PlanetName[face_ruler_val.upper()] if isinstance(face_ruler_val, str) else face_ruler_val
        if face_ruler_name == planet_name:
            score += cls.FACE
            score_breakdown["face"] = cls.FACE
            details.append("Face (+1)")

        # 6. Monomoiria (+1) [engine-specific add-on]
        mono_ruler = cls.get_monomoiria_ruler(sign, deg_in_sign)
        if include_monomoiria:
            if mono_ruler == planet_name:
                score += 1
                score_breakdown["monomoiria"] = 1
                details.append(f"Monomoiria (+1, Ruler: {mono_ruler.value})")
            else:
                details.append(f"Monomoiria Ruler: {mono_ruler.value}")

        # 7. Peregrine (-5): no essential dignity at all (and not in detriment/fall scoring above)
        if (
            score_breakdown["domicile"] == 0
            and score_breakdown["exaltation"] == 0
            and score_breakdown["triplicity"] == 0
            and score_breakdown["term"] == 0
            and score_breakdown["face"] == 0
            and score_breakdown["detriment"] == 0
            and score_breakdown["fall"] == 0
        ):
            score += cls.PEREGRINE
            details.append("Peregrine (-5)")

        return {
            "total_score": score,
            "score_breakdown": score_breakdown,
            "details": details,
            "conflicts": conflicts,
            "variants": {
                "triplicity_scheme": triplicity_scheme.value,
                "term_system": term_system.value,
                "include_monomoiria": include_monomoiria,
            },
            "sign": sign.value,
            "degree": deg_in_sign,
        }

    @classmethod
    def calculate_planetary_joy(cls, planet: Planet, house_num: int) -> int:
        """
        Check if a planet is in its 'Joy' house.
        Mercury: 1st, Moon: 3rd, Venus: 5th, Mars: 6th, Sun: 9th, Jupiter: 11th, Saturn: 12th.
        Add +2 points for being in Joy.
        """
        joy_house = cls.PLANETARY_JOYS.get(planet.name)
        if joy_house == house_num:
            return 2
        return 0

    @classmethod
    def calculate_accidental_dignity(cls, planet: Planet, chart: Chart) -> Dict:
        """
        Implement a comprehensive scoring system for accidental dignity.
        """
        score = 0
        details = []
        
        house_num = cls.get_house_number(planet.longitude, chart.ascendant, getattr(chart, "houses", None))
        
        # 1. House Position
        if house_num in [1, 4, 7, 10]:
            score += 5
            details.append(f"Angular House ({house_num}) (+5)")
        elif house_num in [2, 5, 8, 11]:
            score += 3
            details.append(f"Succedent House ({house_num}) (+3)")
        elif house_num in [3, 6, 9, 12]:
            score += 1
            details.append(f"Cadent House ({house_num}) (+1)")

        # 2. Retrograde / Speed
        if planet.speed < 0:
            score -= 5
            details.append("Retrograde (-5)")
        else:
            # Station Direct check: Very slow but positive speed
            # Since we don't have historical data, we use a small threshold
            if planet.speed < 0.01: # Threshold for station
                score += 4
                details.append("Station Direct (Estimated) (+4)")
            
            # Speed comparison
            avg_speed = cls.AVERAGE_SPEEDS.get(planet.name, 0)
            if planet.speed > avg_speed:
                score += 2
                details.append(f"Faster than average speed (+2, {planet.speed:.4f} > {avg_speed:.4f})")
            elif planet.speed < avg_speed and planet.speed > 0:
                score -= 2
                details.append(f"Slower than average speed (-2, {planet.speed:.4f} < {avg_speed:.4f})")

        # 3. Solar Relationship (Oriental/Occidental)
        sun = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
        if sun and planet.name != PlanetName.SUN:
            # Oriental: Planet rises before Sun (smaller longitude)
            is_oriental = (sun.longitude - planet.longitude) % 360 < 180
            
            if planet.name in [PlanetName.SATURN, PlanetName.JUPITER, PlanetName.MARS]:
                if is_oriental:
                    score += 2
                    details.append("Superior Planet Oriental of Sun (+2)")
            elif planet.name in [PlanetName.VENUS, PlanetName.MERCURY]:
                if not is_oriental: # Occidental
                    score += 2
                    details.append("Inferior Planet Occidental of Sun (+2)")

        # 4. Phase Visibility (Cazimi, Combust, Under Beams)
        if sun and planet.name != PlanetName.SUN:
            dist = abs(planet.longitude - sun.longitude)
            if dist > 180: dist = 360 - dist
            
            if dist < (17/60): # Cazimi (17 mins)
                score += 5
                details.append("Cazimi (+5)")
            elif dist <= 8:
                score -= 5
                if planet.name == PlanetName.MOON:
                    # Lunar near-Sun condition should be labeled as phase/visibility, not planetary combustion.
                    details.append("Dark Moon (<=8° from Sun) (-5)")
                else:
                    details.append("Combust (-5)")
            elif dist <= 15:
                score -= 4
                if planet.name == PlanetName.MOON:
                    details.append("Moon Under Beams (8°-15° from Sun) (-4)")
                else:
                    details.append("Under Beams (-4)")

        # 5. Planetary Joy
        joy_score = cls.calculate_planetary_joy(planet, house_num)
        if joy_score > 0:
            score += joy_score
            details.append(f"Planetary Joy in {house_num}th House (+{joy_score})")

        return {
            "total_score": score,
            "details": details,
            "house": house_num
        }

    @classmethod
    def get_essential_rulers(cls, longitude: float, chart_sect: Sect) -> Dict[str, PlanetName]:
        """Returns the 5 essential dignity rulers for a given longitude."""
        sign_idx = int(longitude / 30) % 12
        sign = list(Sign)[sign_idx]
        deg = longitude % 30
        
        # Domicile
        domicile = REF_DOMICILES[sign]
        
        # Exaltation
        exaltation = REF_EXALTATIONS.get(sign)
        
        # Triplicity
        element = SIGN_ELEMENTS[sign]
        trips = REF_TRIPLICITY[element]
        # REF_TRIPLICITY is now a tuple (Day, Night, Part) in Dorothean mode
        # or (Day, Night) in Ptolemaic.
        # Assuming Dorothean structure from reference_data.py defaults
        if chart_sect == Sect.DAY:
            triplicity = trips[0]
        else:
            triplicity = trips[1]
        
        # Term
        term = None
        terms = EGYPTIAN_TERMS[sign]
        for p, limit in terms:
            if deg < limit:
                term = p
                break
        
        # Face
        face_idx = int(deg / 10)
        global_face_idx = (sign_idx * 3) + face_idx
        face = FACES_ORDER[global_face_idx % len(FACES_ORDER)]
        
        return {
            "domicile": domicile,
            "exaltation": exaltation,
            "triplicity": triplicity,
            "term": term,
            "face": face
        }

