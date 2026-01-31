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
        The 10th sign from the planet is the position of 'Superiority' (Dexter). 
        The 4th sign is 'Sinister' (weaker, but still relevant in some texts, often ignored in strict Kakosis).
        If a Malefic is in the 10th, it dominates the planet.
        """
        res = []
        p_idx = KakosisEngine.get_zodiac_index(planet.sign)
        
        # 10th sign relative to planet (Dexter Square)
        # 1=Aries ... 10=Capricorn. Index + 9.
        tenth_idx = (p_idx + 9) % 12
        
        # 4th sign relative to planet (Sinister Square) - Optional, but Valens mentions it as less specific.
        # We will focus on the 10th as the primary "Overcoming" definition.
        
        for potential_malefic in chart.planets:
            if potential_malefic.name not in KakosisEngine.MALEFICS:
                continue
                
            m_idx = KakosisEngine.get_zodiac_index(potential_malefic.sign)
            
            if m_idx == tenth_idx:
                # Malefic is Overcoming (Dexter/Right)
                msg = f"Overcome by {potential_malefic.name.value} in the 10th sign (Superior/Dexter Square)."
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
                # Check degree orb (say 12 deg for moiety-ish checks or just sign based)
                dist = abs(m.longitude - (planet.longitude + 180) % 360) 
                if dist > 180: dist = 360 - dist
                
                # Malefics opposing by sign is bad, but tighter orb is worse.
                msg = f"Opposed by {m.name.value}."
                sev = 7
                if dist < 12: 
                     msg += f" (Within {int(dist)}° orb)"
                     sev += 1
                
                if KakosisEngine.is_malefic_for_sect(m.name, sect):
                    sev += 1
                
                res.append(MaltreatmentCondition("Opposition", m.name, msg, sev))
        return res

    @staticmethod
    def _check_besiegement(planet: Planet, chart: Chart, sect: Sect) -> List[MaltreatmentCondition]:
        """
        Besiegement (Perischeisis): 
        Bodily: Planet is situated between the two Malefics (Mars and Saturn).
        """
        mars = next((p for p in chart.planets if p.name == PlanetName.MARS), None)
        saturn = next((p for p in chart.planets if p.name == PlanetName.SATURN), None)
        
        if not mars or not saturn:
            return []
            
        def get_shortest_dist(p_lon, target_lon):
            diff = target_lon - p_lon
            if diff > 180: diff -= 360
            if diff < -180: diff += 360
            return diff
            
        dist_mars = get_shortest_dist(planet.longitude, mars.longitude)
        dist_saturn = get_shortest_dist(planet.longitude, saturn.longitude)
        
        # Check if between (one positive, one negative distance)
        # And within orb (e.g. 15 degrees total besiegement span)
        if (dist_mars * dist_saturn < 0) and (abs(dist_mars) + abs(dist_saturn) < 15):
             return [MaltreatmentCondition(
                 "Besiegement", PlanetName.SATURN, # Blame both
                 f"Besieged (Bodily) between Mars and Saturn (Orb: {int(abs(dist_mars) + abs(dist_saturn))}°).",
                 10
             )]
             
        return []

    @staticmethod
    def _check_striking_ray(planet: Planet, chart: Chart, sect: Sect) -> List[MaltreatmentCondition]:
        """
        Aktinobolia: Typically a square where the Malefic is 'looking ahead' at the planet,
        or simply a tight hard aspect.
        Here we treat it as a tight degree-based square (approx 3 deg).
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
        Strict definition: Use speed to determine application.
        """
        res = []
        for m in chart.planets:
            if m.name not in KakosisEngine.MALEFICS: continue
            
            # Check Conjunction distance
            diff = abs(m.longitude - planet.longitude)
            if diff > 180: diff = 360 - diff
            
            if diff < 6: # Orb frame
                # Check applying/separating using relative speed
                # Relative speed = Speed(Planet) - Speed(Malefic)
                # If Planet is faster (>0 rel speed), it must be 'behind' (lesser longitude) to be applying.
                # If Planet is slower (retrograde?), logic holds (speed is negative).
                
                # Let's simplify:
                # Effective velocity of P relative to M
                # If P moves 1 deg/day and M moves 0.1, P closes gap by 0.9/day.
                
                # We need to norm longitude distance relative to movement.
                # Determine 'Lead' and 'Chase'.
                
                # Current separation vector
                # If M is at 10, P is at 8. Target is 10. Gap is +2.
                # We need P's speed > M's speed? Not necessarily, P could be Rx.
                
                # Distance P to M (M - P)
                d_lon = m.longitude - planet.longitude
                if d_lon > 180: d_lon -= 360
                elif d_lon < -180: d_lon += 360
                
                # Relative speed (how much d_lon changes per day)
                # change = (Speed_M - Speed_P)
                # But typically we view it as: P is applying to M if P is catching up.
                
                rel_speed = planet.speed - m.speed
                
                # If d_lon is positive (M ahead of P), we need P to be faster (rel_speed > 0) to catch up.
                # If d_lon is negative (M behind P), we need P to be slower or Rx (rel_speed < 0) to "back into" or M to catch up? 
                # Adherence usually implies the lighter planet applying to the heavier.
                # So P (Light) -> M (Heavy).
                
                is_applying = False
                if d_lon > 0 and rel_speed > 0: is_applying = True # P chasing M
                if d_lon < 0 and rel_speed < 0: is_applying = True # P Rx into M or M chasing P?
                
                # Check MOIETY/ORB for Adherence - usually very tight (3 deg)
                if is_applying and diff < 3:
                     state = "Applying"
                     res.append(MaltreatmentCondition(
                        "Adherence", m.name,
                        f"Adhering (Applying Conjunction) to {m.name.value} within {round(diff,1)}°.",
                        9
                    ))
        return res
