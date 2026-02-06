from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import math
from .models import Planet, Chart, PlanetName, Sect

class AspectType(Enum):
    CONJUNCTION = "Conjunction"
    SEXTILE = "Sextile"
    SQUARE = "Square"
    TRINE = "Trine"
    OPPOSITION = "Opposition"
@dataclass
class Aspect:
    planet_a: PlanetName
    planet_b: PlanetName
    type: AspectType
    orb: float # The actual difference from the exact aspect
    is_applying: bool 
    text: str = ""

class AspectEngine:
    # Standard Medieval/Renaissance Orbs (Lilly/Al-Biruni)
    ORBS = {
        PlanetName.SUN: 15.0,
        PlanetName.MOON: 12.0,
        PlanetName.MERCURY: 7.0,
        PlanetName.VENUS: 7.0,
        PlanetName.MARS: 7.0,
        PlanetName.JUPITER: 9.0,
        PlanetName.SATURN: 9.0,
        # Modern Planets (Optional, giving them generic small orbs)
        PlanetName.URANUS: 5.0,
        PlanetName.NEPTUNE: 5.0,
        PlanetName.PLUTO: 5.0,
        PlanetName.NORTH_NODE: 0.0, # Not usually aspected by bodies in this way
        PlanetName.SOUTH_NODE: 0.0
    }

    ASPECT_ANGLES = {
        AspectType.CONJUNCTION: 0,
        AspectType.SEXTILE: 60,
        AspectType.SQUARE: 90,
        AspectType.TRINE: 120,
        AspectType.OPPOSITION: 180
    }

    @staticmethod
    def _get_orb_allowance(p1: PlanetName, p2: PlanetName) -> float:
        orb1 = AspectEngine.ORBS.get(p1, 5.0)
        orb2 = AspectEngine.ORBS.get(p2, 5.0)
        return (orb1 + orb2) / 2.0

    @staticmethod
    def _calculate_min_distance(lon1: float, lon2: float) -> float:
        diff = abs(lon1 - lon2)
        if diff > 180:
            return 360 - diff
        return diff

    @staticmethod
    def is_applying(p1: Planet, p2: Planet, target_angle: float) -> bool:
        """
        Determines if p1 is applying to p2 for a specific aspect angle.
        """
        # 1. Current angular distance to the aspect
        # dist_to_aspect = (lon2 - lon1) - target_angle
        # We need the shortest path.
        
        # Relative longitude
        rel_lon = (p2.longitude - p1.longitude) % 360
        
        # Offset by target_angle
        # Example: p2 at 100, p1 at 0. rel_lon=100. target=90 (square).
        # p1 needs to move 10 degrees more to hit 90 (if p2 fixed).
        # Actually, p1 moves 10 deg -> p1=10, p2=100. diff=90.
        # So we check the 'angle of separation' minus the 'target angle'.
        
        # We calculate the distance p1 must travel relative to p2 to reach the exact angle.
        # This is (rel_lon - target_angle) % 360.
        # But aspect can be from either side? 
        # For a 90 deg square, it's exact if rel_lon is 90 or 270.
        
        d1 = (rel_lon - target_angle) % 360
        d2 = (rel_lon + target_angle) % 360 # Maybe not right for all
        # Simplified: Find the distance to the NEAREST exact aspect angle.
        
        dist = (rel_lon - target_angle) % 360
        if dist > 180: dist -= 360
        
        # Now we have 'dist' which is the degrees p1 is 'ahead' of the aspect.
        # If dist is -5, p1 is 5 degrees 'behind' the aspect.
        # If relative speed (p1.speed - p2.speed) is positive, p1 is catching up.
        # So if dist < 0 and rel_speed > 0 => Applying.
        # If dist > 0 and rel_speed < 0 => Applying (p1 slowed down or p2 caught up from behind? No).
        
        rel_speed = p1.speed - p2.speed
        
        # If distance is negative (behind) and closing (rel_speed > 0)
        if dist < 0 and rel_speed > 0: return True
        # If distance is positive (past) and closing (rel_speed < 0 - meaning p2 catching up or p1 retrograde?)
        if dist > 0 and rel_speed < 0: return True
        
        return False

    @staticmethod
    def calculate_aspects(chart: Chart) -> List[Aspect]:
        aspects = []
        planets = [p for p in chart.planets if p.name in AspectEngine.ORBS]
        
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT

        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                p1 = planets[i]
                p2 = planets[j]
                
                if "Node" in p1.name.value or "Node" in p2.name.value:
                    continue

                # Relative longitude
                rel_lon = (p2.longitude - p1.longitude) % 360
                allowance = AspectEngine._get_orb_allowance(p1.name, p2.name)

                found_type = None
                exact_angle = 0
                actual_orb = 0

                for aspect_type, angle in AspectEngine.ASPECT_ANGLES.items():
                    # Check distance to this specific angle (both directions 90 and 270 are 'Squares')
                    # Actually for Conjunction(0), Sextile(60/300), Square(90/270), Trine(120/240), Opp(180)
                    for test_angle in [angle, (360 - angle) % 360]:
                        orb_diff = (rel_lon - test_angle) % 360
                        if orb_diff > 180: orb_diff -= 360
                        
                        if abs(orb_diff) <= allowance:
                            found_type = aspect_type
                            exact_angle = test_angle # Store the specific angle for applying check
                            actual_orb = abs(orb_diff)
                            break
                    if found_type: break
                
                if found_type:
                    applying = AspectEngine.is_applying(p1, p2, exact_angle)
                    
                    formatted_text = AspectEngine._interpret_aspect(p1, p2, found_type, sect)
                    
                    aspects.append(Aspect(
                        planet_a=p1.name,
                        planet_b=p2.name,
                        type=found_type,
                        orb=actual_orb,
                        is_applying=applying,
                        text=formatted_text
                    ))
        return aspects


    @staticmethod
    def _interpret_aspect(p1: Planet, p2: Planet, type: AspectType, sect: Sect) -> str:
        # Determine which is the modifier (usually the outer planet impacts the inner)
        # Order: Saturn > Jupiter > Mars > Sun > Venus > Mercury > Moon
        # Using a simplified weight system
        weights = {
            PlanetName.PLUTO: 10, PlanetName.NEPTUNE: 9, PlanetName.URANUS: 8,
            PlanetName.SATURN: 7, PlanetName.JUPITER: 6, PlanetName.MARS: 5,
            PlanetName.SUN: 4, PlanetName.VENUS: 3, PlanetName.MERCURY: 2, PlanetName.MOON: 1
        }
        
        w1 = weights.get(p1.name, 0)
        w2 = weights.get(p2.name, 0)
        
        agent = p1 if w1 > w2 else p2
        receiver = p2 if w1 > w2 else p1
        
        # Identify Malefic/Benefic Roles based on Sect
        is_agent_malefic = agent.name in [PlanetName.SATURN, PlanetName.MARS]
        
        status = "Neutral"
        if sect == Sect.DAY:
            if agent.name == PlanetName.SATURN: status = "Constructive" # Disciplinarian
            elif agent.name == PlanetName.MARS: status = "Destructive" # Incendiary
            elif agent.name == PlanetName.JUPITER: status = "Benefic"
            elif agent.name == PlanetName.VENUS: status = "Benefic"
        else: # Night
            if agent.name == PlanetName.SATURN: status = "Destructive" # Malicious
            elif agent.name == PlanetName.MARS: status = "Constructive" # Soldier
            elif agent.name == PlanetName.JUPITER: status = "Benefic"
            elif agent.name == PlanetName.VENUS: status = "Benefic"

        # Special casing for Moderns (always disruptive/transformative)
        if agent.name in [PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]:
            status = "Destructive" # Broadly "Hard" energy in traditional framework

        # Interpret based on Geometry + Status
        base_desc = ""
        
        if type == AspectType.CONJUNCTION:
            if status == "Destructive":
                base_desc = f"Afflicted by conjunction with {agent.name.value}. Energy is oppressed or inflamed."
            elif status == "Constructive":
                base_desc = f"Strengthened by {agent.name.value}. Structured discipline or drive is added."
            elif status == "Benefic":
                base_desc = f"Blessed by conjunction with {agent.name.value}. Expansive or harmonious support."
                
        elif type in [AspectType.SQUARE, AspectType.OPPOSITION]:
            if status == "Destructive":
                base_desc = f"MALIFIC SIEGE: Hard aspect from {agent.name.value} ({status}). Creates destruction, conflict, or failure."
            elif status == "Constructive":
                base_desc = f"CHALLENGE: Hard aspect from {agent.name.value} ({status}). Demands hard work, resilience, and mastery through friction."
            elif status == "Benefic":
                base_desc = f"OVERINDULGENCE: Hard aspect from {agent.name.value}. Too much of a good thing, or friction in achieving desires."

        elif type in [AspectType.SEXTILE, AspectType.TRINE]:
            if status == "Destructive":
                base_desc = f"MITIGATED THREAT: Easy aspect from {agent.name.value}. The harm is lessened or manageable."
            elif status == "Constructive":
                base_desc = f"FLOW: Easy aspect from {agent.name.value}. Structural support and regulated energy."
            elif status == "Benefic":
                base_desc = f"GIFT: Easy aspect from {agent.name.value}. Natural talent, luck, and ease."

        return base_desc
