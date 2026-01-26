from typing import List, Optional
from dataclasses import dataclass
from .models import Planet, Chart, PlanetName

@dataclass
class NodalContact:
    planet_name: str
    node_type: str # "HEAD", "TAIL", "N_BENDING", "S_BENDING"
    description: str
    metabolic_phase: str # "Anabolism", "Catabolism", "Explosion", "Implosion"

def get_shortest_dist(a: float, b: float) -> float:
    d = abs(a - b)
    if d > 180: d = 360 - d
    return d

def analyze_nodes(chart: Chart) -> List[NodalContact]:
    """
    Implements the Digestive Model of the Lunar Nodes (Caput and Cauda Draconis).
    Ref: Binder1_part_029.txt - The Draconic Engine.
    """
    contacts = []
    nn = chart.north_node
    sn = (nn + 180) % 360
    # North Bending: Midway between NN and SN (zodiacal order) = NN + 90
    n_bending = (nn + 90) % 360
    # South Bending: Midway between SN and NN = SN + 90
    s_bending = (sn + 90) % 360
    
    orb = 4.0 # Standard orb for Nodal influence
    
    for planet in chart.planets:
        p_long = planet.longitude
        p_name = planet.name.value
        
        # Check Head (Caput Draconis) - Intake / Anabolism
        if get_shortest_dist(p_long, nn) <= orb:
            contacts.append(NodalContact(
                planet_name=p_name,
                node_type="HEAD",
                metabolic_phase="Anabolism",
                description=(
                    f"INTAKE/AMPLIFICATION: The {p_name} signal is magnified by the Dragon's Maw. "
                    "Material volume increases; risk of gluttony, inflation, and hyper-manifestation. "
                    "The native is insatiable in this domain."
                )
            ))
            continue
            
        # Check Tail (Cauda Draconis) - Excretion / Catabolism
        if get_shortest_dist(p_long, sn) <= orb:
            contacts.append(NodalContact(
                planet_name=p_name,
                node_type="TAIL",
                metabolic_phase="Catabolism",
                description=(
                    f"EXCRETION/DIMINUTION: The {p_name} signal is drained by the Dragon's Tail. "
                    "Material volume is reduced; spectrality, loss of form, and hypo-manifestation. "
                    "The native is haunted by the absence or corruption of this energy."
                )
            ))
            continue
            
        # Check North Bending - Hyper-Exposure / Explosion
        if get_shortest_dist(p_long, n_bending) <= orb:
            contacts.append(NodalContact(
                planet_name=p_name,
                node_type="N_BENDING",
                metabolic_phase="Explosion",
                description=(
                    f"HYPER-EXPOSURE (North Bending): {p_name} is at maximum Northern latitude. "
                    "Structural instability due to overload. 'Icarus' effect—flying too high. "
                    "Risk of public spectacle or burnout."
                )
            ))
            continue

        # Check South Bending - Hyper-Repression / Implosion
        if get_shortest_dist(p_long, s_bending) <= orb:
            contacts.append(NodalContact(
                planet_name=p_name,
                node_type="S_BENDING",
                metabolic_phase="Implosion",
                description=(
                    f"HYPER-REPRESSION (South Bending): {p_name} is at maximum Southern latitude. "
                    "Foundational collapse; the energy implodes. Hidden failure or rot at the root. "
                    "Structural stress test leading to internal fracture."
                )
            ))
            
    return contacts
