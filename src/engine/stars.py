from dataclasses import dataclass
from typing import List, Optional, Dict
from .models import Planet, Chart, PlanetName

@dataclass
class FixedStar:
    name: str
    longitude: float # 2025 Epoch
    nature: str
    magnitude: int
    glory: str = ""
    nemesis: str = ""
    orb: float = 1.0

# 2025 Coordinates and forensic meanings derived from Binder1_part_030.txt
STARS = [
    FixedStar(
        name="Aldebaran", 
        longitude=70.133, # 10°08' Gemini
        nature="Mars", 
        magnitude=1, 
        glory="Integrity, Honor, Moral Courage",
        nemesis="Compromise of Integrity; Ruin through dishonesty"
    ),
    FixedStar(
        name="Regulus", 
        longitude=150.167, # 00°10' Virgo
        nature="Mars/Jupiter", 
        magnitude=1, 
        glory="Power, Command, Nobility",
        nemesis="Revenge; Total fall from grace due to pettiness"
    ),
    FixedStar(
        name="Antares", 
        longitude=250.100, # 10°06' Sagittarius
        nature="Mars/Jupiter", 
        magnitude=1, 
        glory="Intensity, Bravery, Strategic Genius",
        nemesis="Obsession; Self-destruction through mania"
    ),
    FixedStar(
        name="Fomalhaut", 
        longitude=334.200, # 04°12' Pisces
        nature="Venus/Mercury", 
        magnitude=1, 
        glory="Charisma, Artistic/Spiritual Legacy",
        nemesis="Corruption of Ideals; Dreaming without doing"
    ),
    FixedStar(
        name="Caput Algol", 
        longitude=56.500, # 26°30' Taurus
        nature="Saturn/Mars", 
        magnitude=2, 
        orb=2.5,
        glory="None (Pure Malefic)",
        nemesis="Losing one's head, beheading, extreme violence"
    ),
    FixedStar(
        name="Spica", 
        longitude=204.067, # ~24 Libra (Adjusted for 2025)
        nature="Venus/Mars", 
        magnitude=1, 
        glory="Success through art, diplomacy, and intellect",
        nemesis="None (Pure Benefic)"
    ),
]

@dataclass
class StarContact:
    star_name: str
    planet_name: str
    contact_type: str # "CONJUNCTION" or "PARAN"
    angle: Optional[str] = None
    message: str = ""

def get_shortest_dist(a: float, b: float) -> float:
    d = abs(a - b)
    if d > 180: d = 360 - d
    return d

def calculate_parans(chart: Chart) -> List[StarContact]:
    """
    Detects stars rising, culminating, setting, or on the IC simultaneously with planets or angles.
    As per Binder1_part_030.txt, Parans prioritize visual synchronization over ecliptic longitude.
    """
    parans = []
    
    # Define Angles
    angles = {
        "ASC": chart.ascendant,
        "MC": chart.mc,
        "DSC": (chart.ascendant + 180) % 360,
        "IC": (chart.mc + 180) % 360
    }
    
    orb = 2.0 # Standard orb for Paran detection
    
    # 1. Check Planet-Star Parans
    # A Paran occurs when a Planet is on one angle and a Star is on another (or the same) angle.
    for planet in chart.planets:
        p_long = planet.longitude
        p_name = planet.name.value
        
        # Check if planet is on an angle
        for p_angle_name, p_angle_long in angles.items():
            if get_shortest_dist(p_long, p_angle_long) <= orb:
                # If planet is angular, check if any star is ALSO angular
                for star in STARS:
                    for s_angle_name, s_angle_long in angles.items():
                        if get_shortest_dist(star.longitude, s_angle_long) <= orb:
                            msg = (
                                f"PARAN: {star.name} is on {s_angle_name} while {p_name} is on {p_angle_name}. "
                                f"Eminence Indicator. Nature: {star.nature}. Glory: {star.glory}."
                            )
                            parans.append(StarContact(
                                star_name=star.name,
                                planet_name=p_name,
                                contact_type="PARAN",
                                angle=s_angle_name,
                                message=msg
                            ))
                            
    # 2. Check Light-Angle Parans (Sun/Moon) - The "Dictators" of the Curia
    # We already checked them in the loop above if they are in chart.planets
    
    return parans

def check_fixed_stars(chart: Chart) -> List[StarContact]:
    """
    Main entry point for stellar analysis. 
    Prioritizes Parans over ecliptic conjunctions for eminence, rank, and wealth indicators.
    """
    all_contacts = []
    
    # 1. Calculate Parans (Higher Priority)
    parans = calculate_parans(chart)
    all_contacts.extend(parans)
    
    # 2. Check Ecliptic Conjunctions
    paran_pairs = set((p.star_name, p.planet_name) for p in parans)
    
    for planet in chart.planets:
        p_long = planet.longitude
        p_name = planet.name.value
        
        for star in STARS:
            dist = get_shortest_dist(p_long, star.longitude)
            if dist <= star.orb:
                # Skip if already identified as a Paran (to avoid redundancy, but note conjunction is still valid)
                contact_type = "CONJUNCTION"
                msg = f"CONJUNCT {star.name} (Orb: {dist:.2f}°). Nature: {star.nature}. Nemesis: {star.nemesis}."
                
                all_contacts.append(StarContact(
                    star_name=star.name,
                    planet_name=p_name,
                    contact_type=contact_type,
                    message=msg
                ))
                
    # 3. Check Angles (Asc/MC) for direct star presence
    angles = {"Ascendant": chart.ascendant, "Midheaven": chart.mc}
    for angle_name, angle_long in angles.items():
        for star in STARS:
            dist = get_shortest_dist(angle_long, star.longitude)
            if dist <= star.orb:
                all_contacts.append(StarContact(
                    star_name=star.name,
                    planet_name=angle_name,
                    contact_type="ANGULAR_PRESENCE",
                    message=f"STAR ON {angle_name.upper()}: {star.name}. Glory: {star.glory}. Nemesis: {star.nemesis}."
                ))
                
    # 4. Antares-Aldebaran Axis Alert (Violent Potential)
    # As per Binder1_part_028.txt:
    # Moon/Mars on this axis (opposite stars) signifies violent death potential.
    aldebaran = next((s for s in STARS if s.name == "Aldebaran"), None)
    antares = next((s for s in STARS if s.name == "Antares"), None)
    
    if aldebaran and antares:
        for p_name_target in [PlanetName.MOON, PlanetName.MARS]:
            planet = next((p for p in chart.planets if p.name == p_name_target), None)
            if planet:
                # Check conjunction with either star
                on_aldebaran = get_shortest_dist(planet.longitude, aldebaran.longitude) <= aldebaran.orb
                on_antares = get_shortest_dist(planet.longitude, antares.longitude) <= antares.orb
                
                if on_aldebaran or on_antares:
                    msg = (
                        f"CRITICAL AXIS ALERT: {p_name_target.value} is on the Antares-Aldebaran axis. "
                        "Signifies violent potential / cosmic tension between integrity and obsession. "
                        "Traditionally associated with violent death by the sword or hanging."
                    )
                    all_contacts.append(StarContact(
                        star_name="Antares-Aldebaran Axis",
                        planet_name=p_name_target.value,
                        contact_type="AXIS_ALERT",
                        message=msg
                    ))

    return all_contacts
