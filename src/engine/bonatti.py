from typing import Dict, List, Optional, Tuple, Any
from .models import Chart, Planet, PlanetName, Sect, Sign
from .reference_data import DOMICILES
from .dignities import DignityCalculator

class BonattiEngine:
    """
    Guido Bonatti's 146 Considerations Engine.
    Provides mathematical calculations and rulesets to evaluate charts
    for strictures, radicality, and planetary state mitigations.
    """

    @staticmethod
    def check_void_of_course(
        moon: Planet,
        planets: List[Planet],
        houses: Optional[Dict[int, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculates whether the Moon is Void of Course under both Medieval/Lilly
        (out-of-sign) and Hellenistic (30-degree kinematic) rules.
        Includes Lilly's Alleviation rule.
        """
        moon_lon = moon.longitude
        moon_speed = moon.speed if moon.speed != 0 else 13.1764
        moon_pos_in_sign = moon_lon % 30
        dist_to_end = 30.0 - moon_pos_in_sign

        major_aspects = [0, 60, 90, 120, 180]
        voc_lilly = True
        voc_hellenistic = True

        for p in planets:
            if p.name == PlanetName.MOON or p.name in {
                PlanetName.NORTH_NODE,
                PlanetName.SOUTH_NODE,
                PlanetName.URANUS,
                PlanetName.NEPTUNE,
                PlanetName.PLUTO,
            }:
                continue

            p_speed = p.speed if p.speed is not None else 0.0
            closing_speed = moon_speed - p_speed
            if closing_speed == 0:
                continue

            for aspect in major_aspects:
                for sign_mult in [-1, 1]:
                    target_lon = (p.longitude + (sign_mult * aspect)) % 360
                    dist = (target_lon - moon_lon) % 360

                    # Check if they are closing
                    if dist > 0 and closing_speed > 0:
                        time_to_perfect = dist / closing_speed
                        moon_travel = time_to_perfect * moon_speed
                        
                        # Lilly Out-of-Sign: perfects before leaving sign
                        if moon_travel <= dist_to_end:
                            voc_lilly = False
                        
                        # Hellenistic: perfects within 30 degrees
                        if moon_travel <= 30.0:
                            voc_hellenistic = False
                    elif dist < 0 and closing_speed < 0:
                        time_to_perfect = abs(dist) / abs(closing_speed)
                        moon_travel = time_to_perfect * moon_speed
                        
                        if moon_travel <= dist_to_end:
                            voc_lilly = False
                        
                        if moon_travel <= 30.0:
                            voc_hellenistic = False

        # Alleviation Rule (Lilly, CA p. 112)
        # Void Moon in Cancer, Taurus, Sagittarius, or Pisces is mitigated
        moon_sign = moon.sign
        alleviated = moon_sign in {
            Sign.TAURUS,
            Sign.CANCER,
            Sign.SAGITTARIUS,
            Sign.PISCES,
        }

        is_void = voc_lilly or voc_hellenistic
        if alleviated:
            is_void = False

        details = ""
        if is_void:
            if voc_lilly and voc_hellenistic:
                details = "Moon is strictly Void of Course (Both Hellenistic & Medieval). Absolutely nothing will come of the matter."
            else:
                details = "Moon is Void of Course (Lilly Out-of-Sign Rule). The matter goes hardly on."
        elif alleviated and (voc_lilly or voc_hellenistic):
            details = f"Moon is Void of Course, but mitigated by being in {moon_sign.value} (Taurus, Cancer, Sagittarius, or Pisces). The matter may still proceed."
        else:
            details = "Moon is not Void of Course."

        return {
            "voc_lilly": voc_lilly,
            "voc_hellenistic": voc_hellenistic,
            "is_void": is_void,
            "is_alleviated": alleviated,
            "details": details,
        }

    @staticmethod
    def check_combustion_cazimi(planet: Planet, sun: Planet) -> Dict[str, Any]:
        """
        Guido Bonatti's Combustion and Cazimi logic.
        Evaluates the planetary condition relative to the Sun's light.
        """
        if planet.name == PlanetName.SUN:
            return {"status": "FREE", "details": "The Sun cannot be combust by itself."}

        dist = abs(planet.longitude - sun.longitude) % 360
        if dist > 180:
            dist = 360 - dist

        # Special logic for Moon
        if planet.name == PlanetName.MOON:
            if dist <= (17.0 / 60.0):
                return {
                    "status": "CAZIMI",
                    "details": "Moon is Cazimi (within 17' of Sun). Extreme accidental strength.",
                }
            elif dist <= 8.0:
                return {
                    "status": "COMBUST",
                    "details": "Moon is Combust (within 8° of Sun). Severely weakened/obscured.",
                }
            elif dist <= 15.0:
                return {
                    "status": "UNDER_BEAMS",
                    "details": "Moon is Under the Beams (within 15° of Sun). Moderately weakened.",
                }
            return {"status": "FREE", "details": "Moon is free from solar proximity."}

        # Standard planets
        if dist <= (17.0 / 60.0):
            return {
                "status": "CAZIMI",
                "details": f"{planet.name.value} is Cazimi (within 17' of Sun). Supreme empowerment.",
            }
        elif dist <= 8.5:
            # The Mercury Exception Loop (Bonatti)
            if planet.name == PlanetName.MERCURY:
                sign_idx = int(planet.longitude / 30) % 12
                from .models import Sign
                sign = list(Sign)[sign_idx]
                
                is_mercury_exception = False
                if sign in [Sign.GEMINI, Sign.VIRGO]:
                    is_mercury_exception = True
                else:
                    from .reference_data import EGYPTIAN_TERMS
                    degree = planet.longitude % 30
                    for r_p, limit in EGYPTIAN_TERMS.get(sign, []):
                        if degree < limit:
                            r_name = PlanetName[r_p.upper()] if isinstance(r_p, str) else r_p
                            if r_name == PlanetName.MERCURY:
                                is_mercury_exception = True
                            break
                            
                if is_mercury_exception:
                    return {
                        "status": "MERCURY_EXCEPTION",
                        "details": "Mercury is Combust (within 8.5° of Sun), but shielded by Domicile or Bounds. Retains clarity.",
                    }
                    
            return {
                "status": "COMBUST",
                "details": f"{planet.name.value} is Combust (within 8.5° of Sun). Powerless, blinded, and impeded.",
            }
        elif dist <= 15.0:
            return {
                "status": "UNDER_BEAMS",
                "details": f"{planet.name.value} is Under the Beams (within 15° of Sun). Obscured and weakened.",
            }

        return {"status": "FREE", "details": f"{planet.name.value} is free from solar proximity."}

    @staticmethod
    def check_planet_at_29_degrees(planet: Planet) -> Dict[str, Any]:
        """
        Bonatti Consideration 30: Planet in the last degree of a sign (29° to 30°).
        Indicates instability, transition of state, or that the matter is already settled.
        """
        deg = planet.longitude % 30
        if deg >= 29.0:
            return {
                "active": True,
                "details": f"{planet.name.value} is at late degree ({deg:.2f}°). It signifies that the matter is already settled, too late to change, or in a state of rapid transition.",
            }
        return {"active": False, "details": f"{planet.name.value} is not in late degrees."}

    @staticmethod
    def check_significator_in_ascendant(planet: Planet, chart: Chart) -> Dict[str, Any]:
        """
        Bonatti Consideration 141: If the significator of the quesited is located
        in the Ascendant sign, it indicates the quesited comes to the querent directly.
        """
        asc_sign_idx = int(chart.ascendant / 30) % 12
        p_sign_idx = int(planet.longitude / 30) % 12

        if asc_sign_idx == p_sign_idx:
            return {
                "active": True,
                "details": f"Significator {planet.name.value} is in the Ascendant sign. The Quesited comes to the Querent.",
            }
        return {"active": False, "details": f"Significator {planet.name.value} is not in the Ascendant sign."}

    @staticmethod
    def check_lord_precedence(
        asc_ruler: PlanetName, almuten_ruler: PlanetName, matter_type: str = "body"
    ) -> Dict[str, Any]:
        """
        Bonatti Consideration 125: Precedence of rulers.
        For physical, health, and body matters, the Lord of the Ascendant takes precedence.
        For professional, career, and vocational mastery, the Almuten Figuris / Almuten takes precedence.
        """
        if asc_ruler == almuten_ruler:
            return {
                "precedent_ruler": asc_ruler,
                "details": f"Both roles are ruled by {asc_ruler.value}. Absolute authority.",
            }

        if matter_type.lower() in {"body", "health", "life", "vitality"}:
            return {
                "precedent_ruler": asc_ruler,
                "details": f"Lord of Ascendant ({asc_ruler.value}) takes precedence over Almuten ({almuten_ruler.value}) for bodily and vitality matters.",
            }
        else:
            return {
                "precedent_ruler": almuten_ruler,
                "details": f"Almuten ({almuten_ruler.value}) takes precedence over Lord of Ascendant ({asc_ruler.value}) for professional and vocational matters.",
            }

    @staticmethod
    def check_malefics_in_angles(chart: Chart) -> List[Dict[str, Any]]:
        """
        Bonatti strictures regarding Mars/Saturn in 1st (Ascendant) or 7th (Descendant) signs.
        """
        strictures = []
        saturn = next((p for p in chart.planets if p.name == PlanetName.SATURN), None)
        mars = next((p for p in chart.planets if p.name == PlanetName.MARS), None)

        asc_sign_idx = int(chart.ascendant / 30) % 12
        desc_sign_idx = (asc_sign_idx + 6) % 12
        asc_ruler = DOMICILES[list(Sign)[asc_sign_idx]]
        desc_ruler = DOMICILES[list(Sign)[desc_sign_idx]]

        if saturn:
            sat_sign_idx = int(saturn.longitude / 30) % 12
            if sat_sign_idx == asc_sign_idx and asc_ruler != PlanetName.SATURN:
                strictures.append({
                    "consideration": "Saturn in 1st House",
                    "details": "Saturn is in the 1st House/Sign: The question is damaged or the querent is structurally restricted.",
                })
            elif sat_sign_idx == desc_sign_idx and desc_ruler != PlanetName.SATURN:
                strictures.append({
                    "consideration": "Saturn in 7th House",
                    "details": "Saturn is in the 7th House/Sign: The astrologer's judgment may be impaired, delayed, or blocked.",
                })

        if mars:
            mars_sign_idx = int(mars.longitude / 30) % 12
            if mars_sign_idx == desc_sign_idx and desc_ruler != PlanetName.MARS:
                strictures.append({
                    "consideration": "Mars in 7th House",
                    "details": "Mars is in the 7th House/Sign: The astrologer may be overly aggressive, rash, or mathematically blinded.",
                })

        return strictures
