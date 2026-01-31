from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from .models import Planet, Chart, PlanetName, Sect, Sign

@dataclass
class MaltreatmentCondition:
    type: str  # "Overcoming", "Besiegement", "Striking", "Adherence", "Opposition"
    malefic: PlanetName
    description: str
    severity: int  # 1-10

class KakosisEngine:
    """
    Implements the 'Seven Conditions of Maltreatment' (Kakosis) from Hellenistic Astrology (Valens/Hephaistio).
    """

    MALEFICS = [PlanetName.SATURN, PlanetName.MARS]
    BENEFICS = [PlanetName.JUPITER, PlanetName.VENUS]

    @staticmethod
    def get_zodiac_index(sign: str) -> int:
        signs = [
            Sign.ARIES, Sign.TAURUS, Sign.GEMINI, Sign.CANCER,
            Sign.LEO, Sign.VIRGO, Sign.LIBRA, Sign.SCORPIO,
            Sign.SAGITTARIUS, Sign.CAPRICORN, Sign.AQUARIUS, Sign.PISCES
        ]
        try:
            return signs.index(Sign(sign))
        except ValueError:
            return -1

    @staticmethod
    def is_malefic_for_sect(planet_name: PlanetName, sect: Sect) -> bool:
        """
        Determines if a planet is functionally malefic in this chart.
        Standard: Saturn/Mars are always malefic, but sect mitigates them.
        Strict Kakosis often treats them as malefic regardless, but purely worse out of sect.
        """
        if planet_name not in KakosisEngine.MALEFICS:
            return False
        
        # Most severe if Out of Sect
        if sect == Sect.DAY and planet_name == PlanetName.MARS: return True
        if sect == Sect.NIGHT and planet_name == PlanetName.SATURN: return True
        return True # Still technically a malefic, just 'mitigated' if in sect.

    @staticmethod
    def check_maltreatments(planet: Planet, chart: Chart) -> List[MaltreatmentCondition]:
        conditions = []
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT

        # Skip if the planet itself is a malefic (malefics don't usually 'maltreat' themselves in this context, 
        # though they can be impeded. For simplicty, we focus on Lights and Benefics being maltreated).
        # However, Valens does talk about Malefics impeding each other. We will allow all.

        # 1. OVERCOMING (Kathuperteresis)
        # A malefic in the 10th sign from the planet (dexter square)
        conditions.extend(KakosisEngine._check_overcoming(planet, chart, sect))

        # 2. OPPOSITION (Diametria)
        conditions.extend(KakosisEngine._check_opposition(planet, chart, sect))

        # 3. BESIEGEMENT (Perischeisis)
        # Trapped between two malefics (by body or ray)
        conditions.extend(KakosisEngine._check_besiegement(planet, chart, sect))
        
        # 4. STRIKING WITH A RAY (Aktinobolia)
        # Malefic casting a hard aspect (usually square/opp) degree-based
        # Overlap with Overcoming/Opp logic but specifically degree-based.
        conditions.extend(KakosisEngine._check_striking_ray(planet, chart, sect))
        
        # 5. ADHERENCE (Kollesis) or CONNECTION (Sunaphe)
        # Applying to conjunction with a malefic
        conditions.extend(KakosisEngine._check_adherence(planet, chart, sect))

        return conditions

    @staticmethod
    def _check_overcoming(planet: Planet, chart: Chart, sect: Sect) -> List[MaltreatmentCondition]:
        """
        The 10th sign from the planet is the position of 'Superiority'. 
        If a Malefic is there, it dominates the planet.
        """
        res = []
        p_idx = KakosisEngine.get_zodiac_index(planet.sign)
        
        # 10th sign relative to planet (inclusive count). 
        # 1=Aries, 10=Capricorn. Index + 9.
        tenth_idx = (p_idx + 9) % 12
        
        for potential_malefic in chart.planets:
            if potential_malefic.name not in KakosisEngine.MALEFICS:
                continue
                
            m_idx = KakosisEngine.get_zodiac_index(potential_malefic.sign)
            
            if m_idx == tenth_idx:
                # Malefic is Overcoming
                # Check degree (Bonification/Maltreatment often relies on degrees in Hellenistic)
                # But widely, the sign position allows the 'claim'.
                
                # Refinement: Is it a degree-based square?
                msg = f"Overcome by {potential_malefic.name.value} in the 10th sign/Superior Square."
                sev = 8
                if KakosisEngine.is_malefic_for_sect(potential_malefic.name, sect):
                    msg += " (Aggravated by Sect)"
                    sev = 10
                
                res.append(MaltreatmentCondition("Overcoming", potential_malefic.name, msg, sev))
        return res

    @staticmethod
    def _check_opposition(planet: Planet, chart: Chart, sect: Sect) -> List[MaltreatmentCondition]:
        res = []
        p_idx = KakosisEngine.get_zodiac_index(planet.sign)
        opp_idx = (p_idx + 6) % 12
        
        for m in chart.planets:
            if m.name not in KakosisEngine.MALEFICS: continue
            
            if KakosisEngine.get_zodiac_index(m.sign) == opp_idx:
                # Check degree orb (say 10 deg widely)
                dist = abs(m.longitude - (planet.longitude + 180) % 360) 
                if dist > 180: dist = 360 - dist
                
                # Widely considering sign opposition as maltreatment basis, but usually needs orb
                if dist < 12: # Standard moiery orb
                     res.append(MaltreatmentCondition(
                         "Opposition", m.name, 
                         f"Opposed by {m.name.value} ({int(dist)}° orb).", 
                         9 if KakosisEngine.is_malefic_for_sect(m.name, sect) else 7
                     ))
        return res

    @staticmethod
    def _check_besiegement(planet: Planet, chart: Chart, sect: Sect) -> List[MaltreatmentCondition]:
        """
        Planet is separating from one malefic and applying to another.
        """
        # Sort planets by longitude to find neighbors? 
        # Besiegement is complex. Simplified "Ray" besiegement is hard.
        # Bodily besiegement: Planet is between Mars and Saturn in the SAME sign or adjacent?.
        # Classic definition: Separating from Malefic A, Applying to Malefic B.
        return [] # TODO: Implement complex ray besiegement later if needed. Use logic.py's simplified check.

    @staticmethod
    def _check_striking_ray(planet: Planet, chart: Chart, sect: Sect) -> List[MaltreatmentCondition]:
        """
        Aktinobolia: Typically a square where the Malefic is 'looking ahead' at the planet,
        or simply a tight hard aspect.
        """
        res = []
        for m in chart.planets:
            if m.name not in KakosisEngine.MALEFICS: continue
            
            # Distance
            diff = abs(m.longitude - planet.longitude)
            if diff > 180: diff = 360 - diff
            
            # Check for Square (90)
            if abs(diff - 90) < 3: # Tight square (3 deg)
                res.append(MaltreatmentCondition(
                    "Striking with a Ray", m.name,
                    f"Struck by {m.name.value} via tight square ({int(abs(diff-90))}° orb).",
                    8
                ))
        return res

    @staticmethod
    def _check_adherence(planet: Planet, chart: Chart, sect: Sect) -> List[MaltreatmentCondition]:
        """
        Kollesis: Applying to conjunction within orb (usually 3 degrees).
        """
        res = []
        for m in chart.planets:
            if m.name not in KakosisEngine.MALEFICS: continue
            
            # Check Conjunction distance
            diff = abs(m.longitude - planet.longitude)
            if diff > 180: diff = 360 - diff
            
            if diff < 10: # Wide conjunction
                # Check applying/separating.
                # Simplistic: If planet is faster and behind malefic (less longitude), it's applying.
                # Or if planet is slower and ahead of malefic.
                # Moon (Fastest) always applies to planets ahead of it.
                
                # Assume Planet moves direct.
                # If Planet < Malefic (and diff < 10), Planet is chasing Malefic => Applying.
                
                # Normalize longs
                p_lon = planet.longitude
                m_lon = m.longitude
                
                # Check direction (assuming standard zodiacal order)
                # If p_lon = 10, m_lon = 15. P applies to M.
                is_applying = False
                if (m_lon - p_lon) % 360 < 15:
                    is_applying = True
                
                if is_applying and diff < 3: # Tight adherence
                     res.append(MaltreatmentCondition(
                        "Adherence", m.name,
                        f"Adhering (Applying Conjunction) to {m.name.value} within {round(diff,1)}°.",
                        9
                    ))
        return res
