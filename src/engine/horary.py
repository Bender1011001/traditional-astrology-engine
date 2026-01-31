from typing import List, Dict, Optional, Tuple
from .models import Planet, Chart, PlanetName, Sign, Sect
from .reference_data import DOMICILES, MOIETIES, PLANET_SECTS
from .dignities import DignityCalculator

MAJOR_ASPECTS = {
    "Conjunction": 0,
    "Sextile": 60,
    "Square": 90,
    "Trine": 120,
    "Opposition": 180
}

def get_moiety_orb(p1_name: PlanetName, p2_name: PlanetName) -> float:
    """
    Returns the sum of moieties (radii) for the two planets.
    Aspect occurs if dist <= moiety1 + moiety2.
    """
    orb1 = MOIETIES.get(p1_name, 5.0)
    orb2 = MOIETIES.get(p2_name, 5.0)
    return orb1 + orb2

def get_aspect_distance(lon1: float, lon2: float, aspect_angle: float) -> float:
    """
    Returns the distance from current configuration to the exact aspect.
    Positive means lon1 needs to increase to reach aspect with lon2 (if lon2 is fixed).
    """
    diff = (lon2 - lon1) % 360
    # For each major aspect, find the closest one
    # But here we specify the aspect_angle
    angle_diff = (diff - aspect_angle) % 360
    if angle_diff > 180:
        angle_diff -= 360
    return angle_diff

def is_applying(p1: Planet, p2: Planet, aspect_angle: float) -> bool:
    """
    Checks if p1 is applying to p2 via aspect_angle.
    p1 is considered the 'faster' or 'applying' planet in a general sense, 
    but we check relative speed here.
    """
    dist = get_aspect_distance(p1.longitude, p2.longitude, aspect_angle)
    rel_speed = p1.speed - p2.speed
    
    # If distance is positive and rel_speed is positive, they are closing.
    # If distance is negative and rel_speed is negative, they are closing.
    moiety_sum = get_moiety_orb(p1.name, p2.name)
    
    if dist > 0 and rel_speed > 0 and dist < moiety_sum:
        return True
    if dist < 0 and rel_speed < 0 and abs(dist) < moiety_sum:
        return True
    return False

def check_translation_of_light(p1: Planet, p2: Planet, chart: Chart) -> Optional[Dict]:
    """
    Translation of Light: A faster planet (usually Moon) separates from p1 and applies to p2.
    """
    for trans in chart.planets:
        if trans.name == p1.name or trans.name == p2.name:
            continue
        
        # trans must be faster than both p1 and p2 (or at least faster than the one it's applying to)
        if trans.speed <= p1.speed and trans.speed <= p2.speed:
            continue
            
        # Check if trans is separating from p1
        sep_from_p1 = False
        for name, angle in MAJOR_ASPECTS.items():
            dist = get_aspect_distance(trans.longitude, p1.longitude, angle)
            rel_speed = trans.speed - p1.speed
            # Separating: dist > 0 and rel_speed < 0 (trans was at angle, now past it)
            # Or dist < 0 and rel_speed > 0
            moiety_sum = get_moiety_orb(trans.name, p1.name)
            if (dist > 0 and rel_speed < 0 and abs(dist) < moiety_sum) or \
               (dist < 0 and rel_speed > 0 and abs(dist) < moiety_sum):
                sep_from_p1 = True
                break
        
        if not sep_from_p1:
            continue
            
        # Check if trans is applying to p2
        app_to_p2 = False
        aspect_found = ""
        for name, angle in MAJOR_ASPECTS.items():
            if is_applying(trans, p2, angle):
                app_to_p2 = True
                aspect_found = name
                break
        
        if app_to_p2:
            return {
                "condition": "Translation of Light",
                "via": trans.name.value,
                "from": p1.name.value,
                "to": p2.name.value,
                "aspect": aspect_found,
                "status": "Active"
            }
    return None

def check_collection_of_light(p1: Planet, p2: Planet, chart: Chart) -> Optional[Dict]:
    """
    Collection of Light: p1 and p2 both apply to a slower planet p3.
    """
    for p3 in chart.planets:
        if p3.name == p1.name or p3.name == p2.name:
            continue
            
        # p3 must be slower than p1 and p2
        if p3.speed >= p1.speed or p3.speed >= p2.speed:
            continue
            
        # p1 applying to p3
        p1_app = False
        p1_aspect = ""
        for name, angle in MAJOR_ASPECTS.items():
            if is_applying(p1, p3, angle):
                p1_app = True
                p1_aspect = name
                break
        
        if not p1_app:
            continue
            
        # p2 applying to p3
        p2_app = False
        p2_aspect = ""
        for name, angle in MAJOR_ASPECTS.items():
            if is_applying(p2, p3, angle):
                p2_app = True
                p2_aspect = name
                break
                
        if p2_app:
            return {
                "condition": "Collection of Light",
                "collector": p3.name.value,
                "p1": p1.name.value,
                "p2": p2.name.value,
                "p1_aspect": p1_aspect,
                "p2_aspect": p2_aspect,
                "status": "Active"
            }
    return None

def check_prohibition(p1: Planet, p2: Planet, chart: Chart) -> Optional[Dict]:
    """
    Prohibition: p1 applies to p2, but p3 completes an aspect with p1 or p2 first.
    """
    # Find the primary aspect between p1 and p2
    main_aspect = None
    main_angle = 0
    main_dist = 0
    for name, angle in MAJOR_ASPECTS.items():
        if is_applying(p1, p2, angle):
            main_aspect = name
            main_angle = angle
            main_dist = abs(get_aspect_distance(p1.longitude, p2.longitude, angle))
            break
            
    if not main_aspect:
        # Check if p2 applies to p1
        for name, angle in MAJOR_ASPECTS.items():
            if is_applying(p2, p1, angle):
                p1, p2 = p2, p1 # Swap so p1 is the applying one
                main_aspect = name
                main_angle = angle
                main_dist = abs(get_aspect_distance(p1.longitude, p2.longitude, angle))
                break
    
    if not main_aspect:
        return None

    # Time to completion (approximate) = dist / relative_speed
    rel_speed_main = abs(p1.speed - p2.speed)
    if rel_speed_main == 0: return None
    time_to_main = main_dist / rel_speed_main

    for p3 in chart.planets:
        if p3.name == p1.name or p3.name == p2.name:
            continue
            
        # Does p3 apply to p1 or p2?
        for target in [p1, p2]:
            for name, angle in MAJOR_ASPECTS.items():
                if is_applying(p3, target, angle):
                    dist_p3 = abs(get_aspect_distance(p3.longitude, target.longitude, angle))
                    rel_speed_p3 = abs(p3.speed - target.speed)
                    if rel_speed_p3 == 0: continue
                    time_to_p3 = dist_p3 / rel_speed_p3
                    
                    if time_to_p3 < time_to_main:
                        return {
                            "condition": "Prohibition",
                            "intervener": p3.name.value,
                            "target": target.name.value,
                            "aspect": name,
                            "status": "Active",
                            "details": f"{p3.name.value} completes {name} with {target.name.value} before {p1.name.value} completes {main_aspect} with {p2.name.value}"
                        }
    return None

def check_frustration(p1: Planet, p2: Planet, chart: Chart) -> Optional[Dict]:
    """
    Frustration: p1 applies to p2, but p2 applies to p3 before p1 reaches p2.
    """
    # 1. Check if p1 applies to p2
    main_aspect = None
    main_angle = 0
    main_dist = 0
    for name, angle in MAJOR_ASPECTS.items():
        if is_applying(p1, p2, angle):
            main_aspect = name
            main_angle = angle
            main_dist = abs(get_aspect_distance(p1.longitude, p2.longitude, angle))
            break
            
    if not main_aspect:
        return None
        
    rel_speed_main = abs(p1.speed - p2.speed)
    if rel_speed_main == 0: return None
    time_to_main = main_dist / rel_speed_main
    
    # 2. Check if p2 applies to any p3
    for p3 in chart.planets:
        if p3.name == p1.name or p3.name == p2.name: 
            continue
            
        # Does p2 apply to p3?
        for name, angle in MAJOR_ASPECTS.items():
            if is_applying(p2, p3, angle):
                dist_p2_p3 = abs(get_aspect_distance(p2.longitude, p3.longitude, angle))
                rel_speed_p2_p3 = abs(p2.speed - p3.speed)
                if rel_speed_p2_p3 == 0: continue
                time_to_frustrate = dist_p2_p3 / rel_speed_p2_p3
                
                if time_to_frustrate < time_to_main:
                    return {
                        "condition": "Frustration",
                        "frustrator": p3.name.value,
                        "ignoring_planet": p2.name.value,
                        "details": f"{p2.name.value} joins {p3.name.value} ({time_to_frustrate:.2f}) before {p1.name.value} reaches it ({time_to_main:.2f}).",
                        "status": "Active"
                    }
    return None

def check_refranation(p1: Planet, p2: Planet) -> Optional[Dict]:
    """
    Refranation: p1 applies to p2, but turns retrograde (or p2 turns) before completion.
    """
    main_aspect = None
    for name, angle in MAJOR_ASPECTS.items():
        if is_applying(p1, p2, angle):
            main_aspect = name
            break
    
    if not main_aspect:
        return None
        
    # If speed is very low (less than 10% of average), it might be stationing
    avg_speeds = {
        PlanetName.SUN: 0.9833,
        PlanetName.MOON: 13.1764,
        PlanetName.MERCURY: 1.3,
        PlanetName.VENUS: 1.2,
        PlanetName.MARS: 0.524,
        PlanetName.JUPITER: 0.0831,
        PlanetName.SATURN: 0.0335
    }
    
    # Check p1 (usually faster)
    avg = avg_speeds.get(p1.name, 0.1)
    if 0 < p1.speed < (avg * 0.1): # 10% threshold for caution
             return {
                "condition": "Refranation",
                "planet": p1.name.value,
                "status": "Potential",
                "details": f"{p1.name.value} is moving very slowly ({p1.speed:.4f}) and may station before completing aspect."
            }

    return None

def check_mutual_reception(p1: Planet, p2: Planet, chart: Chart) -> Optional[Dict]:
    """
    Mutual Reception: Planets in each other's dignities (Domicile/Exaltation).
    """
    sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
    
    # Get dignities of p1's position
    p1_pos_rulers = DignityCalculator.get_essential_rulers(p1.longitude, sect)
    # Get dignities of p2's position
    p2_pos_rulers = DignityCalculator.get_essential_rulers(p2.longitude, sect)
    
    # Types of reception
    reception_1_to_2 = []
    if p1_pos_rulers["domicile"] == p2.name: reception_1_to_2.append("Domicile")
    if p1_pos_rulers["exaltation"] == p2.name: reception_1_to_2.append("Exaltation")
    
    reception_2_to_1 = []
    if p2_pos_rulers["domicile"] == p1.name: reception_2_to_1.append("Domicile")
    if p2_pos_rulers["exaltation"] == p1.name: reception_2_to_1.append("Exaltation")
    
    if reception_1_to_2 and reception_2_to_1:
         return {
            "condition": "Mutual Reception",
            "p1": p1.name.value,
            "p2": p2.name.value,
            "p1_receives_p2_by": reception_1_to_2,
            "p2_receives_p1_by": reception_2_to_1,
            "status": "Active"
        }
    elif reception_1_to_2 or reception_2_to_1:
        # Simple reception
        giver = p1.name.value if reception_1_to_2 else p2.name.value
        receiver = p2.name.value if reception_1_to_2 else p1.name.value
        by = reception_1_to_2 if reception_1_to_2 else reception_2_to_1
        return {
            "condition": "Reception",
            "giver": giver,
            "receiver": receiver,
            "by": by,
            "status": "Active"
        }
        
    return None

def calculate_antiscia(longitude: float) -> Tuple[float, float]:
    antiscia = (180 - longitude) % 360
    contra_antiscia = (antiscia + 180) % 360
    return antiscia, contra_antiscia

def analyze_horary_physics(p1_name: PlanetName, p2_name: PlanetName, chart: Chart) -> List[Dict]:
    """
    Analyzes the 'Physics' between two significators.
    """
    p1 = next((p for p in chart.planets if p.name == p1_name), None)
    p2 = next((p for p in chart.planets if p.name == p2_name), None)
    
    if not p1 or not p2:
        return []
        
    conditions = []
    
    # 1. Direct Aspect
    for name, angle in MAJOR_ASPECTS.items():
        if is_applying(p1, p2, angle) or is_applying(p2, p1, angle):
            conditions.append({
                "condition": "Direct Application",
                "aspect": name,
                "status": "Active"
            })
            break
            
    # 2. Translation
    translation = check_translation_of_light(p1, p2, chart)
    if translation: conditions.append(translation)
    
    # 3. Collection
    collection = check_collection_of_light(p1, p2, chart)
    if collection: conditions.append(collection)
    
    # 4. Prohibition
    prohibition = check_prohibition(p1, p2, chart)
    if prohibition: conditions.append(prohibition)
    
    # 5. Frustration (New)
    frustration = check_frustration(p1, p2, chart)
    if frustration: conditions.append(frustration)
    
    # 6. Refranation
    refranation = check_refranation(p1, p2)
    if refranation: conditions.append(refranation)
    
    # 7. Mutual Reception (Mitigation)
    reception = check_mutual_reception(p1, p2, chart)
    if reception: conditions.append(reception)

    # 8. Antiscia / Contra-antiscia
    a1, ca1 = calculate_antiscia(p1.longitude)
    orb = 1.0 # Standard orb for Antiscia
    
    diff_a = abs(p2.longitude - a1) % 360
    if diff_a > 180: diff_a = 360 - diff_a
    if diff_a <= orb:
        conditions.append({
            "condition": "Antiscia",
            "details": f"{p2.name.value} is on the Antiscia of {p1.name.value}. Hidden connection.",
            "status": "Active"
        })

    diff_ca = abs(p2.longitude - ca1) % 360
    if diff_ca > 180: diff_ca = 360 - diff_ca
    if diff_ca <= orb:
        conditions.append({
            "condition": "Contra-antiscia",
            "details": f"{p2.name.value} is on the Contra-antiscia of {p1.name.value}.",
            "status": "Active"
        })
    
    return conditions

KEYWORD_HOUSES = [
    (10, "Career/Status", ["job", "career", "promotion", "work", "boss", "business", "office"]),
    (4, "Home/Property", ["house", "home", "property", "real estate", "apartment", "land", "move"]),
    (7, "Relationships/Contracts", ["relationship", "marriage", "partner", "spouse", "boyfriend", "girlfriend", "dating", "divorce", "contract", "lawsuit", "opponent"]),
    (2, "Money/Resources", ["money", "finance", "loan", "debt", "salary", "pay", "wealth", "income", "purchase", "buy", "sell", "investment"]),
    (6, "Health/Service", ["health", "illness", "disease", "medical", "surgery", "diagnosis", "workout", "pet"]),
    (5, "Children/Creation", ["child", "children", "pregnant", "baby", "fertility", "creative", "art", "romance"]),
    (9, "Travel/Study", ["travel", "visa", "immigration", "study", "school", "college", "university", "publishing", "foreign"])
]

POSITIVE_CONDITIONS = {
    "Direct Application",
    "Translation of Light",
    "Collection of Light",
    "Mutual Reception",
    "Reception",
    "Antiscia"
}

NEGATIVE_CONDITIONS = {
    "Prohibition",
    "Refranation",
    "Frustration",
    "Contra-antiscia"
}

CONDITION_WEIGHTS = {
    "Direct Application": 4,
    "Translation of Light": 3,
    "Collection of Light": 3,
    "Mutual Reception": 2,
    "Reception": 1,
    "Antiscia": 1,
    "Contra-antiscia": -1,
    "Prohibition": -4,
    "Refranation": -3,
    "Frustration": -4
}

BENEFICS = {PlanetName.JUPITER, PlanetName.VENUS}
MALEFICS = {PlanetName.MARS, PlanetName.SATURN}
DIURNAL = {PlanetName.SUN, PlanetName.JUPITER, PlanetName.SATURN}
NOCTURNAL = {PlanetName.MOON, PlanetName.VENUS, PlanetName.MARS}

def get_sect_score(planet_name: PlanetName, chart_sect: Sect) -> int:
    if chart_sect == Sect.DAY:
        if planet_name in DIURNAL: return 2
        if planet_name in NOCTURNAL: return -2
    else:
        if planet_name in NOCTURNAL: return 2
        if planet_name in DIURNAL: return -2
    return 0

def get_nature_score(planet_name: PlanetName) -> int:
    if planet_name in BENEFICS: return 2
    if planet_name in MALEFICS: return -2
    return 0

def score_significator(planet: Planet, chart: Chart) -> Dict[str, int | str | List[str]]:
    chart_sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
    essential = DignityCalculator.calculate_planet_dignity(planet.name, planet.longitude, chart_sect)
    accidental = DignityCalculator.calculate_accidental_dignity(planet, chart)
    hayz = DignityCalculator.check_hayz_halb(planet.name, planet.longitude, chart)

    hayz_bonus = 0
    if hayz["status"] == "Hayz": hayz_bonus = 3
    elif hayz["status"] == "Halb": hayz_bonus = 2
    elif hayz["status"] == "In Sect": hayz_bonus = 1

    sect_score = get_sect_score(planet.name, chart_sect)
    nature_score = get_nature_score(planet.name)

    total = (
        essential["total_score"]
        + accidental["total_score"]
        + sect_score
        + nature_score
        + hayz_bonus
    )

    return {
        "planet": planet.name.value,
        "essential_score": essential["total_score"],
        "essential_details": essential["details"],
        "accidental_score": accidental["total_score"],
        "accidental_details": accidental["details"],
        "total_score": total
    }

def score_conditions(conditions: List[Dict]) -> Dict[str, int | List[Dict]]:
    breakdown = []
    total = 0
    for condition in conditions:
        name = condition.get("condition")
        weight = CONDITION_WEIGHTS.get(name, 0)
        total += weight
        breakdown.append({
            "condition": name,
            "weight": weight
        })
    return {
        "total_score": total,
        "breakdown": breakdown
    }

def select_quesited_house(question: str) -> Dict[str, str | int]:
    q = (question or "").lower()
    for house, label, keywords in KEYWORD_HOUSES:
        if any(k in q for k in keywords):
            return {"house": house, "label": label}
    return {"house": 7, "label": "Relationships/Other"}

def get_house_sign(asc_sign_idx: int, house_num: int) -> Sign:
    signs = list(Sign)
    return signs[(asc_sign_idx + (house_num - 1)) % 12]

def evaluate_horary_conditions(conditions: List[Dict], condition_score: int, strength_score: int) -> Dict[str, str | int]:
    pos = [c for c in conditions if c.get("condition") in POSITIVE_CONDITIONS]
    neg = [c for c in conditions if c.get("condition") in NEGATIVE_CONDITIONS]
    total_score = condition_score + strength_score

    if total_score >= 6:
        verdict = "Yes"
        weight = "Favorable"
    elif total_score >= 2:
        verdict = "Struggle, then success" if pos and neg else "Yes"
        weight = "Mixed"
    elif total_score <= -6:
        verdict = "No"
        weight = "Blocked"
    elif total_score <= -2:
        verdict = "No"
        weight = "Mixed"
    else:
        verdict = "Unclear"
        weight = "Mixed"

    return {
        "verdict": verdict,
        "weight": weight,
        "positive_count": len(pos),
        "negative_count": len(neg),
        "total_score": total_score
    }

def build_horary_oracle(question: str, chart: Chart) -> Dict:
    asc_sign_idx = int(chart.ascendant / 30) % 12
    asc_sign = list(Sign)[asc_sign_idx]
    querent_ruler = DOMICILES[asc_sign]

    quesited_info = select_quesited_house(question)
    quesited_sign = get_house_sign(asc_sign_idx, quesited_info["house"])
    quesited_ruler = DOMICILES[quesited_sign]

    conditions = analyze_horary_physics(querent_ruler, quesited_ruler, chart)
    querent_planet = next((p for p in chart.planets if p.name == querent_ruler), None)
    quesited_planet = next((p for p in chart.planets if p.name == quesited_ruler), None)
    querent_strength = score_significator(querent_planet, chart) if querent_planet else None
    quesited_strength = score_significator(quesited_planet, chart) if quesited_planet else None
    condition_score = score_conditions(conditions)

    strength_total = 0
    if querent_strength: strength_total += querent_strength["total_score"]
    if quesited_strength: strength_total += quesited_strength["total_score"]
    if querent_strength and quesited_strength:
        strength_total = int(round(strength_total / 2))

    verdict_data = evaluate_horary_conditions(conditions, condition_score["total_score"], strength_total)

    return {
        "question": question,
        "querent_sign": asc_sign.value,
        "querent_ruler": querent_ruler.value,
        "quesited_house": quesited_info["house"],
        "quesited_label": quesited_info["label"],
        "quesited_sign": quesited_sign.value,
        "quesited_ruler": quesited_ruler.value,
        "conditions": conditions,
        "verdict": verdict_data["verdict"],
        "verdict_weight": verdict_data["weight"],
        "strength_score": strength_total,
        "total_score": verdict_data["total_score"]
    }
