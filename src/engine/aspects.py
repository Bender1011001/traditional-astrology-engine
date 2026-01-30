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
    is_applying: bool # True if applying, False if separating (Bonus, maybe hard to calc without speed, but we have speed)
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
    def calculate_aspects(chart: Chart) -> List[Aspect]:
        aspects = []
        planets = [p for p in chart.planets if p.name in AspectEngine.ORBS]
        
        # Determine Sect for interpretation context
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT

        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                p1 = planets[i]
                p2 = planets[j]
                
                # Skip Node aspects for now if desired, or keep them
                if "Node" in p1.name.value or "Node" in p2.name.value:
                    continue

                dist = AspectEngine._calculate_min_distance(p1.longitude, p2.longitude)
                allowance = AspectEngine._get_orb_allowance(p1.name, p2.name)

                found_type = None
                exact_angle = 0

                for aspect_type, angle in AspectEngine.ASPECT_ANGLES.items():
                    orb_diff = abs(dist - angle)
                    if orb_diff <= allowance:
                        found_type = aspect_type
                        exact_angle = angle
                        break
                
                if found_type:
                    # Determine applying/separating
                    # Classic checks relative speeds.
                    # Simple check: if faster planet moves towards exact aspect.
                    # P1 is faster?
                    # This is complex, defaulting to True for now or omitting.
                    formatted_text = AspectEngine._interpret_aspect(p1, p2, found_type, sect)
                    
                    aspects.append(Aspect(
                        planet_a=p1.name,
                        planet_b=p2.name,
                        type=found_type,
                        orb=abs(dist - exact_angle),
                        is_applying=True,
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
