from typing import Dict, List, Optional, Tuple

from .dignities import DignityCalculator
from .models import Chart, Planet, PlanetName, Sect, Sign
from .reference_data import DOMICILES, MOIETIES

MAJOR_ASPECTS = {
    "Conjunction": 0,
    "Sextile": 60,
    "Square": 90,
    "Trine": 120,
    "Opposition": 180,
}

CHALDEAN_ORDER = {
    PlanetName.MOON: 7,
    PlanetName.MERCURY: 6,
    PlanetName.VENUS: 5,
    PlanetName.SUN: 4,
    PlanetName.MARS: 3,
    PlanetName.JUPITER: 2,
    PlanetName.SATURN: 1,
    PlanetName.NORTH_NODE: 0,
    PlanetName.SOUTH_NODE: 0,
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
    Returns the shortest angular distance from current configuration to the exact aspect.
    Positive distance means lon1 needs to traverse mathematically forward (increase lon) to hit aspect.
    """
    diff = (lon2 - lon1) % 360

    # Check forward configuration (Dexter)
    ad1 = (diff - aspect_angle) % 360
    if ad1 > 180:
        ad1 -= 360

    # Check reverse configuration (Sinister)
    ad2 = (diff - (360 - aspect_angle)) % 360
    if ad2 > 180:
        ad2 -= 360

    return ad1 if abs(ad1) < abs(ad2) else ad2


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


def is_separating(p1: Planet, p2: Planet, aspect_angle: float) -> bool:
    """
    Checks if p1 is separating from p2 moving away from the aspect_angle.
    """
    dist = get_aspect_distance(p1.longitude, p2.longitude, aspect_angle)
    rel_speed = p1.speed - p2.speed
    moiety_sum = get_moiety_orb(p1.name, p2.name)

    if dist > 0 and rel_speed < 0 and abs(dist) < moiety_sum:
        return True
    if dist < 0 and rel_speed > 0 and abs(dist) < moiety_sum:
        return True
    return False


def get_planet_house(lon: float, chart: Chart) -> int:
    if not chart.houses:
        return 0
    for i in range(1, 13):
        cusp1 = chart.houses[i]
        cusp2 = chart.houses[(i % 12) + 1]
        if cusp1 < cusp2:
            if cusp1 <= lon < cusp2:
                return i
        else:
            if lon >= cusp1 or lon < cusp2:
                return i
    return 0


def check_translation_of_light(p1: Planet, p2: Planet, chart: Chart) -> Optional[Dict]:
    """
    Translation of Light: A faster planet (usually Moon) separates from p1 and applies to p2.
    """
    for trans in chart.planets:
        if trans.name == p1.name or trans.name == p2.name:
            continue

        # trans must be a lighter planet (higher Chaldean score) than at least one of the targets
        trans_weight = CHALDEAN_ORDER.get(trans.name, 0)
        p1_weight = CHALDEAN_ORDER.get(p1.name, 0)
        p2_weight = CHALDEAN_ORDER.get(p2.name, 0)

        if trans_weight <= p1_weight or trans_weight <= p2_weight:
            continue

        # Check if trans is separating from p1 or p2
        sep_from = None
        for target in [p1, p2]:
            for name, angle in MAJOR_ASPECTS.items():
                dist = get_aspect_distance(trans.longitude, target.longitude, angle)
                rel_speed = trans.speed - target.speed
                moiety_sum = get_moiety_orb(trans.name, target.name)
                if (dist > 0 and rel_speed < 0 and abs(dist) < moiety_sum) or (
                    dist < 0 and rel_speed > 0 and abs(dist) < moiety_sum
                ):
                    sep_from = target
                    break
            if sep_from:
                break

        if not sep_from:
            continue

        # Check if trans is applying to the OTHER planet
        apply_target = p2 if sep_from == p1 else p1
        app_to_target = False
        aspect_found = ""
        for name, angle in MAJOR_ASPECTS.items():
            if is_applying(trans, apply_target, angle):
                app_to_target = True
                aspect_found = name
                break

        if app_to_target:
            return {
                "condition": "Translation of Light",
                "via": trans.name.value,
                "from": sep_from.name.value,
                "to": apply_target.name.value,
                "aspect": aspect_found,
                "status": "Active",
            }
    return None


def check_collection_of_light(p1: Planet, p2: Planet, chart: Chart) -> Optional[Dict]:
    """
    Collection of Light: p1 and p2 both apply to a slower planet p3.
    """
    for p3 in chart.planets:
        if p3.name == p1.name or p3.name == p2.name:
            continue

        # p3 must be heavier (slower in Chaldean Order) than p1 and p2
        p3_weight = CHALDEAN_ORDER.get(p3.name, 0)
        p1_weight = CHALDEAN_ORDER.get(p1.name, 0)
        p2_weight = CHALDEAN_ORDER.get(p2.name, 0)

        if p3_weight >= p1_weight or p3_weight >= p2_weight:
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
                "status": "Active",
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
            main_angle = float(angle)  # type: ignore
            main_dist = float(abs(get_aspect_distance(p1.longitude, p2.longitude, angle)))  # type: ignore
            break

    if not main_aspect:
        # Check if p2 applies to p1
        for name, angle in MAJOR_ASPECTS.items():
            if is_applying(p2, p1, angle):
                p1, p2 = p2, p1  # Swap so p1 is the applying one
                main_aspect = name
                main_angle = float(angle)  # type: ignore
                main_dist = float(abs(get_aspect_distance(p1.longitude, p2.longitude, angle)))  # type: ignore
                break

    if not main_aspect:
        return None

    # Time to completion (approximate) = dist / relative_speed
    rel_speed_main = abs(p1.speed - p2.speed)
    if rel_speed_main == 0:
        return None
    time_to_main = main_dist / rel_speed_main

    for p3 in chart.planets:
        if p3.name == p1.name or p3.name == p2.name:
            continue

        # Does p3 apply to p1 or p2?
        for target in [p1, p2]:
            for name, angle in MAJOR_ASPECTS.items():
                if is_applying(p3, target, angle):
                    dist_p3 = abs(
                        get_aspect_distance(p3.longitude, target.longitude, angle)
                    )
                    rel_speed_p3 = abs(p3.speed - target.speed)
                    if rel_speed_p3 == 0:
                        continue
                    time_to_p3 = dist_p3 / rel_speed_p3

                    if time_to_p3 < time_to_main:
                        return {
                            "condition": "Prohibition",
                            "intervener": p3.name.value,
                            "target": target.name.value,
                            "aspect": name,
                            "status": "Active",
                            "details": f"{p3.name.value} completes {name} with {target.name.value} before {p1.name.value} completes {main_aspect} with {p2.name.value}",
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
            main_dist = abs(get_aspect_distance(p1.longitude, p2.longitude, angle))  # type: ignore
            break

    if not main_aspect:
        for name, angle in MAJOR_ASPECTS.items():
            if is_applying(p2, p1, angle):
                p1, p2 = p2, p1  # Swap so p1 is the applying one
                main_aspect = name
                main_angle = angle
                main_dist = abs(get_aspect_distance(p1.longitude, p2.longitude, angle))  # type: ignore
                break

    if not main_aspect:
        return None

    rel_speed_main = abs(p1.speed - p2.speed)
    if rel_speed_main == 0:
        return None
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
                if rel_speed_p2_p3 == 0:
                    continue
                time_to_frustrate = dist_p2_p3 / rel_speed_p2_p3

                if time_to_frustrate < time_to_main:
                    return {
                        "condition": "Frustration",
                        "frustrator": p3.name.value,
                        "ignoring_planet": p2.name.value,
                        "details": f"{p2.name.value} joins {p3.name.value} ({time_to_frustrate:.2f}) before {p1.name.value} reaches it ({time_to_main:.2f}).",
                        "status": "Active",
                    }
    return None


def check_abscission(p1: Planet, p2: Planet, chart: Chart) -> Optional[Dict]:
    """
    Abscission of Light (Abscissio Luminis): A third planet interposes itself
    bodily (by conjunction) between two applying significators, preventing
    perfection by cutting the light path.
    Ref: Bonatti, Liber Astronomiae Tr. 5; Lilly CA p.115.
    Distinct from Prohibition, which works by aspect — Abscission works by
    bodily interposition.
    """
    # 1. Find the primary applying aspect between p1 and p2
    main_aspect = None
    main_angle = 0
    faster, slower = (p1, p2) if abs(p1.speed) >= abs(p2.speed) else (p2, p1)

    for name, angle in MAJOR_ASPECTS.items():
        if is_applying(faster, slower, angle):
            main_aspect = name
            main_angle = angle
            break

    if not main_aspect:
        return None

    # 2. Determine the zodiacal arc the faster planet must traverse
    main_dist = get_aspect_distance(faster.longitude, slower.longitude, main_angle)
    arc_start = faster.longitude
    arc_length = abs(main_dist)

    for p3 in chart.planets:
        if p3.name == faster.name or p3.name == slower.name:
            continue

        # Check if p3 is bodily within the arc between faster and the target
        if main_dist > 0:
            dist_to_p3 = (p3.longitude - arc_start) % 360
        else:
            dist_to_p3 = (arc_start - p3.longitude) % 360

        if 0 < dist_to_p3 < arc_length:
            # p3 is in the path — check if faster planet will actually catch p3
            if main_dist > 0:
                closing_speed_p3 = faster.speed - p3.speed
                closing_speed_main = faster.speed - slower.speed
            else:
                closing_speed_p3 = p3.speed - faster.speed
                closing_speed_main = slower.speed - faster.speed

            if closing_speed_p3 <= 0 or closing_speed_main <= 0:
                continue  # Faster is falling behind p3, or they are not actually closing (impossible if applying)

            time_to_p3 = dist_to_p3 / closing_speed_p3
            time_to_main = arc_length / closing_speed_main

            if time_to_p3 < time_to_main:
                return {
                    "condition": "Abscission of Light",
                    "cutter": p3.name.value,
                    "faster": faster.name.value,
                    "slower": slower.name.value,
                    "details": f"{p3.name.value} interposes bodily between {faster.name.value} and {slower.name.value}, cutting the light before {main_aspect} perfects.",
                    "status": "Active",
                }
    return None


def check_refranation(p1: Planet, p2: Planet) -> Optional[Dict]:
    """
    Refranation: p1 applies to p2, but turns retrograde (or p2 turns) before completion.
    """
    applying_planet = None
    for name, angle in MAJOR_ASPECTS.items():
        if is_applying(p1, p2, angle):
            applying_planet = p1
            break
        elif is_applying(p2, p1, angle):
            applying_planet = p2
            break

    if not applying_planet:
        return None

    # If speed is very low (less than 10% of average), it might be stationing
    avg_speeds = {
        PlanetName.SUN: 0.9833,
        PlanetName.MOON: 13.1764,
        PlanetName.MERCURY: 1.3,
        PlanetName.VENUS: 1.2,
        PlanetName.MARS: 0.524,
        PlanetName.JUPITER: 0.0831,
        PlanetName.SATURN: 0.0335,
    }

    avg = avg_speeds.get(applying_planet.name, 0.1)
    if 0 < applying_planet.speed < (avg * 0.1):  # 10% threshold for caution
        return {
            "condition": "Refranation",
            "planet": applying_planet.name.value,
            "status": "Potential",
            "details": f"{applying_planet.name.value} is moving very slowly ({applying_planet.speed:.4f}) and may station before completing aspect.",
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
    if p1_pos_rulers.get("domicile") == p2.name:
        reception_1_to_2.append("Domicile")
    if p1_pos_rulers.get("exaltation") == p2.name:
        reception_1_to_2.append("Exaltation")
    if p1_pos_rulers.get("triplicity") == p2.name:
        reception_1_to_2.append("Triplicity")
    if p1_pos_rulers.get("term") == p2.name:
        reception_1_to_2.append("Term")
    if p1_pos_rulers.get("face") == p2.name:
        reception_1_to_2.append("Face")

    reception_2_to_1 = []
    if p2_pos_rulers.get("domicile") == p1.name:
        reception_2_to_1.append("Domicile")
    if p2_pos_rulers.get("exaltation") == p1.name:
        reception_2_to_1.append("Exaltation")
    if p2_pos_rulers.get("triplicity") == p1.name:
        reception_2_to_1.append("Triplicity")
    if p2_pos_rulers.get("term") == p1.name:
        reception_2_to_1.append("Term")
    if p2_pos_rulers.get("face") == p1.name:
        reception_2_to_1.append("Face")

    if reception_1_to_2 and reception_2_to_1:
        major = {"Domicile", "Exaltation"}
        # It's only a major perfecting reception if BOTH legs have at least one Major dignity
        is_major = any(r in major for r in reception_1_to_2) and any(
            r in major for r in reception_2_to_1
        )
        cond = "Mutual Reception" if is_major else "Minor Mutual Reception"

        return {
            "condition": cond,
            "p1": p1.name.value,
            "p2": p2.name.value,
            "p1_receives_p2_by": reception_1_to_2,
            "p2_receives_p1_by": reception_2_to_1,
            "status": "Active",
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
            "status": "Active",
        }

    return None


def calculate_antiscia(longitude: float) -> Tuple[float, float]:
    antiscia = (180 - longitude) % 360
    contra_antiscia = (antiscia + 180) % 360
    return antiscia, contra_antiscia


def check_void_of_course_hellenistic(moon: Planet, chart: Chart) -> bool:
    """
    Hellenistic / Antiochus Void of Course:
    True if the Moon completes no applying exact major aspects within the next 30 degrees of zodiacal longitude.
    """
    for planet in chart.planets:
        if planet.name == PlanetName.MOON or planet.name in {
            PlanetName.NORTH_NODE,
            PlanetName.SOUTH_NODE,
            PlanetName.URANUS,
            PlanetName.NEPTUNE,
            PlanetName.PLUTO,
        }:
            continue

        for name, angle in MAJOR_ASPECTS.items():
            dist = get_aspect_distance(moon.longitude, planet.longitude, angle)
            rel_speed = moon.speed - planet.speed

            # Use dynamic kinematic projection to determine actual Moon travel distance
            if dist > 0 and rel_speed > 0:
                time_to_perfect = dist / rel_speed
                moon_travel = time_to_perfect * abs(moon.speed)
                if moon_travel <= 30.0:
                    return False  # Not void
            elif dist < 0 and rel_speed < 0:
                time_to_perfect = abs(dist) / abs(rel_speed)
                moon_travel = time_to_perfect * abs(moon.speed)
                if moon_travel <= 30.0:
                    return False  # Not void
    return True


def check_void_of_course_lilly(moon: Planet, chart: Chart) -> bool:
    """
    Medieval/Lilly Void of Course:
    True if the Moon completes no applying exact major aspects before it leaves its current sign.
    """
    distance_to_sign_end = 30.0 - (moon.longitude % 30.0)

    for planet in chart.planets:
        if planet.name == PlanetName.MOON or planet.name in {
            PlanetName.NORTH_NODE,
            PlanetName.SOUTH_NODE,
            PlanetName.URANUS,
            PlanetName.NEPTUNE,
            PlanetName.PLUTO,
        }:
            continue

        for name, angle in MAJOR_ASPECTS.items():
            dist = get_aspect_distance(moon.longitude, planet.longitude, angle)
            rel_speed = moon.speed - planet.speed

            if dist > 0 and rel_speed > 0:
                time_to_perfect = dist / rel_speed
                moon_travel = time_to_perfect * moon.speed
                if moon_travel <= distance_to_sign_end:
                    return False  # Perfects before leaving sign, not void
            elif dist < 0 and rel_speed < 0:
                time_to_perfect = abs(dist) / abs(rel_speed)
                moon_travel = time_to_perfect * moon.speed
                if moon_travel <= distance_to_sign_end:
                    return False
    return True


def check_strictures(chart: Chart) -> List[str]:
    """
    Checks Bonatti/Lilly rules for when a Horary chart is unsafe or difficult to judge.
    """
    strictures = []

    # 1. Ascendant < 3 degrees or > 27 degrees
    asc_deg = chart.ascendant % 30
    if asc_deg < 3.0:
        strictures.append(
            "Ascendant in early degrees (< 3°): The matter is premature or not fully developed."
        )
    elif asc_deg > 27.0:
        strictures.append(
            "Ascendant in late degrees (> 27°): The matter is already settled and too late to change."
        )

    # 1.5 Radicality Check
    if chart.jd and chart.geo_lat is not None and chart.geo_lon is not None:
        try:
            import swisseph as swe
            from datetime import datetime, timezone
            y, m, d, h = swe.revjul(chart.jd)
            hour_int = int(h)
            min_int = int((h - hour_int) * 60)
            sec_int = int((((h - hour_int) * 60) - min_int) * 60)
            dt = datetime(y, m, d, hour_int, min_int, sec_int, tzinfo=timezone.utc)
            
            from .planetary_hours import PlanetaryHourEngine
            hr_data = PlanetaryHourEngine.calculate_hours(dt, chart.geo_lat, chart.geo_lon)
            hour_ruler_val = hr_data.get("hour_ruler")
            
            if hour_ruler_val:
                asc_sign_idx = int(chart.ascendant / 30) % 12
                asc_sign = list(Sign)[asc_sign_idx]
                from .reference_data import TRIPLICITY_RULERS, SIGN_ELEMENTS
                import src.engine.reference_data as ref_data
                asc_ruler = ref_data.DOMICILES[asc_sign]
                
                if hour_ruler_val != asc_ruler.value:
                    element = SIGN_ELEMENTS.get(asc_sign, "Fire")
                    trip_rulers = TRIPLICITY_RULERS.get(element, [])
                    hour_ruler_enum = PlanetName(hour_ruler_val)
                    if hour_ruler_enum not in trip_rulers:
                        strictures.append(
                            f"Chart is Non-Radical: Planetary Hour Ruler ({hour_ruler_val}) does not match or support the Ascendant Ruler ({asc_ruler.value})."
                        )
        except Exception:
            pass

    # 2. Saturn/Mars in the 1st or 7th house sign
    saturn = next((p for p in chart.planets if p.name == PlanetName.SATURN), None)
    mars = next((p for p in chart.planets if p.name == PlanetName.MARS), None)

    asc_sign_idx = int(chart.ascendant / 30) % 12
    desc_sign_idx = (asc_sign_idx + 6) % 12
    asc_ruler = DOMICILES[list(Sign)[asc_sign_idx]]
    desc_ruler = DOMICILES[list(Sign)[desc_sign_idx]]

    if saturn:
        sat_sign_idx = int(saturn.longitude / 30) % 12
        if sat_sign_idx == asc_sign_idx and asc_ruler != PlanetName.SATURN:
            strictures.append(
                "Saturn in 1st House/Sign: The question is damaged or the querent is structurally restricted."
            )
        elif sat_sign_idx == desc_sign_idx and desc_ruler != PlanetName.SATURN:
            strictures.append(
                "Saturn in 7th House/Sign: The astrologer's judgment may be impaired, delayed, or blocked."
            )

    if mars:
        mars_sign_idx = int(mars.longitude / 30) % 12
        if mars_sign_idx == desc_sign_idx and desc_ruler != PlanetName.MARS:
            strictures.append(
                "Mars in 7th House/Sign: The astrologer may be overly aggressive, rash, or mathematically blinded."
            )

    # 3. Moon Void of Course
    moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)
    if moon:
        voc_hellenistic = check_void_of_course_hellenistic(moon, chart)
        voc_lilly = check_void_of_course_lilly(moon, chart)

        moon_sign_idx = int(moon.longitude / 30) % 12
        moon_sign = list(Sign)[moon_sign_idx]

        # Alleviation Rule (Lilly, CA p. 112)
        alleviated = moon_sign in {
            Sign.TAURUS,
            Sign.CANCER,
            Sign.SAGITTARIUS,
            Sign.PISCES,
        }

        if (voc_lilly or voc_hellenistic) and alleviated:
            strictures.append(
                f"Moon is Void of Course, but mitigated by being in {moon_sign.value} (Taurus, Cancer, Sagittarius, or Pisces). The matter may still proceed."
            )
        else:
            if voc_lilly and not voc_hellenistic:
                strictures.append(
                    "Moon is Void of Course (Medieval/Lilly Out-of-Sign Rule): The Moon makes no aspect before leaving its sign. The matter goes hardly on."
                )
            elif voc_lilly and voc_hellenistic:
                strictures.append(
                    "Moon is strictly Void of Course (Both Hellenistic & Medieval): Absolutely nothing will come of the matter."
                )

    # 4. Moon in the Via Combusta (15 Libra to 15 Scorpio)
    # 15 Libra = 195 degrees. 15 Scorpio = 225 degrees.
    # Exemption: Conjunction with Spica Virginis (approx 23.8 Libra, ~203.5 degrees)
    if moon and 195.0 <= moon.longitude <= 225.0:
        if 202.5 <= moon.longitude <= 204.5:  # 2 degree orb for Spica
            strictures.append(
                "Moon in the Via Combusta, but Conjunct Spica: The Querent is walking through fire, but is supremely protected by unexpected grace."
            )
        else:
            strictures.append(
                "Moon in the Via Combusta (15° Libra to 15° Scorpio): The querent is highly distressed; sudden shifts or destructive energies surround the matter."
            )

    # 5. Moon is Combust (within 8.5 degrees of the Sun)
    sun = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
    if moon and sun:
        # Check distance between Moon and Sun
        dist = abs(moon.longitude - sun.longitude) % 360
        if dist > 180:
            dist = 360 - dist
        if (17 / 60) < dist <= 8.5:
            strictures.append(
                "Moon is Combust (-Cazimi): The querent or the matter is overwhelmed, blinded, or severely weakened by a superior force."
            )

    # 6. Ascendant Ruler is Combust
    asc_sign = list(Sign)[int(chart.ascendant / 30) % 12]
    asc_ruler = DOMICILES[asc_sign]
    asc_planet = next((p for p in chart.planets if p.name == asc_ruler), None)

    if sun and asc_planet and asc_ruler != PlanetName.SUN:
        dist = abs(asc_planet.longitude - sun.longitude) % 360
        if dist > 180:
            dist = 360 - dist
        if (17 / 60) < dist <= 8.5:
            strictures.append(
                f"Ascendant Ruler ({asc_ruler.value}) is Combust: The Querent is incapable of action, imprisoned, or structurally destroyed."
            )

    # 7. Ascendant Ruler is Retrograde
    if (
        asc_planet
        and asc_planet.speed < 0
        and asc_planet.name not in {PlanetName.SUN, PlanetName.MOON}
    ):
        strictures.append(
            f"Ascendant Ruler ({asc_ruler.value}) is Retrograde: The Querent will likely change their mind or withdraw from the matter."
        )

    # 8. Moon or Ascendant Ruler Conjunct the South Node (Cauda Draconis)
    south_node = next(
        (p for p in chart.planets if p.name == PlanetName.SOUTH_NODE), None
    )
    if south_node:
        for planet in [p for p in (moon, asc_planet) if p is not None]:
            dist = abs(planet.longitude - south_node.longitude) % 360
            if dist > 180:
                dist = 360 - dist
            if dist <= 3.0:
                # Avoid appending duplicate for Moon if Moon is also Asc ruler
                msg = f"{planet.name.value} is Conjunct the South Node: A malefic omen denoting sudden loss, damage, or corruption in the matter."
                if msg not in strictures:
                    strictures.append(msg)

    # 9. Moon in Late Degrees
    if moon and (moon.longitude % 30) >= 27.0:
        strictures.append(
            "Moon in Late Degrees (>= 27°): The current alignment is rapidly dissolving; the Querent is frantic or the situation is highly unstable."
        )

    # 10. 7th House Ruler is Afflicted (Astrologer's Integrity Check)
    desc_sign_idx = (int(chart.ascendant / 30) + 6) % 12
    desc_sign = list(Sign)[desc_sign_idx]
    desc_ruler = DOMICILES[desc_sign]
    desc_planet = next((p for p in chart.planets if p.name == desc_ruler), None)

    if desc_planet:
        if desc_planet.speed < 0 and desc_ruler not in {
            PlanetName.SUN,
            PlanetName.MOON,
        }:
            strictures.append(
                f"7th House Ruler ({desc_ruler.value}) is Retrograde: The Astrologer's judgment may be impaired, delayed, or reversed."
            )
        if sun and desc_ruler != PlanetName.SUN:
            dist = abs(desc_planet.longitude - sun.longitude) % 360
            if dist > 180:
                dist = 360 - dist
            if (17 / 60) < dist <= 8.5:
                strictures.append(
                    f"7th House Ruler ({desc_ruler.value}) is Combust: The Astrologer is mathematically blinded or incapable of seeing the entire truth of the matter."
                )

    return strictures


def check_besiegement(p: Planet, chart: Chart) -> Optional[Dict]:
    """
    Besiegement: Planet is bodily enclosed exclusively between the two malefics (or benefics).
    """
    if p.name in {
        PlanetName.NORTH_NODE,
        PlanetName.SOUTH_NODE,
        PlanetName.URANUS,
        PlanetName.NEPTUNE,
        PlanetName.PLUTO,
    }:
        return None

    traditional_planets = [
        pl
        for pl in chart.planets
        if pl.name
        in {
            PlanetName.SUN,
            PlanetName.MOON,
            PlanetName.MERCURY,
            PlanetName.VENUS,
            PlanetName.MARS,
            PlanetName.JUPITER,
            PlanetName.SATURN,
        }
    ]

    sorted_planets = sorted(
        traditional_planets, key=lambda x: (x.longitude - p.longitude) % 360
    )

    if len(sorted_planets) >= 3:
        next_planet = sorted_planets[1]
        prev_planet = sorted_planets[-1]

        malefics = {PlanetName.MARS, PlanetName.SATURN}
        benefics = {PlanetName.VENUS, PlanetName.JUPITER}

        if (
            next_planet.name in malefics
            and prev_planet.name in malefics
            and p.name not in malefics
        ):
            if next_planet.name != prev_planet.name:
                # Check Reception Veto
                from .reference_data import DOMICILES, EXALTATIONS, TRIPLICITY_RULERS, SIGN_ELEMENTS
                has_reception = False
                for malefic in (next_planet, prev_planet):
                    m_sign_idx = int(malefic.longitude / 30) % 12
                    m_sign = list(Sign)[m_sign_idx]
                    
                    if DOMICILES.get(m_sign) == p.name:
                        has_reception = True
                    if EXALTATIONS.get(m_sign) == p.name:
                        has_reception = True
                        
                    element = SIGN_ELEMENTS.get(m_sign, "Fire")
                    trip = TRIPLICITY_RULERS.get(element, tuple())
                    if p.name in trip:
                        has_reception = True
                        
                    if has_reception:
                        break
                        
                if not has_reception:
                    return {
                        "condition": "Besiegement by Malefics Without Reception",
                        "target": p.name.value,
                        "malefic_1": prev_planet.name.value,
                        "malefic_2": next_planet.name.value,
                        "details": f"{p.name.value} is bodily besieged between {prev_planet.name.value} and {next_planet.name.value} WITHOUT reception. Fatal constraint and harm.",
                        "status": "VETO",
                    }
                else:
                    return {
                        "condition": "Besiegement by Malefics (Mitigated)",
                        "target": p.name.value,
                        "malefic_1": prev_planet.name.value,
                        "malefic_2": next_planet.name.value,
                        "details": f"{p.name.value} is besieged between {prev_planet.name.value} and {next_planet.name.value}, mitigated by Reception.",
                        "status": "Active",
                    }

        if (
            next_planet.name in benefics
            and prev_planet.name in benefics
            and p.name not in benefics
        ):
            if next_planet.name != prev_planet.name:
                return {
                    "condition": "Besiegement by Benefics",
                    "target": p.name.value,
                    "benefic_1": prev_planet.name.value,
                    "benefic_2": next_planet.name.value,
                    "details": f"{p.name.value} is warmly enclosed between {prev_planet.name.value} and {next_planet.name.value}. Supreme protection and aid.",
                    "status": "Active",
                }
    return None


def analyze_horary_physics(
    p1_name: PlanetName, p2_name: PlanetName, chart: Chart
) -> List[Dict]:
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
            if name in ["Trine", "Sextile"]:
                cond_name = "Easy Perfection"
                det = f"Applying by {name}. The matter perfects smoothly and easily."
            elif name == "Square":
                cond_name = "Hard Perfection"
                det = f"Applying by Square. The matter perfects, but with delays, friction, and struggle."
            elif name == "Opposition":
                cond_name = "Regretful Perfection"
                det = f"Applying by Opposition. The matter perfects, but immediately falls apart or causes bitter regret."
            else:
                cond_name = "Direct Application"
                det = "Applying by Conjunction. Powerful and direct union."

            conditions.append(
                {
                    "condition": cond_name,
                    "aspect": name,
                    "details": det,
                    "status": "Active",
                }
            )
            break
        elif is_separating(p1, p2, angle) or is_separating(p2, p1, angle):
            conditions.append(
                {
                    "condition": "Past Separation",
                    "aspect": name,
                    "details": f"Separating from {name}. The defining event or interaction has already occurred in the recent past.",
                    "status": "Inactive",
                }
            )
            break

    # 2. Translation
    translation = check_translation_of_light(p1, p2, chart)
    if translation:
        conditions.append(translation)

    # 3. Collection
    collection = check_collection_of_light(p1, p2, chart)
    if collection:
        conditions.append(collection)

    # 4. Prohibition
    prohibition = check_prohibition(p1, p2, chart)
    if prohibition:
        conditions.append(prohibition)

    # 5. Frustration (New)
    frustration = check_frustration(p1, p2, chart)
    if frustration:
        conditions.append(frustration)

    # 6. Abscission of Light
    abscission = check_abscission(p1, p2, chart)
    if abscission:
        conditions.append(abscission)

    # 7. Refranation
    refranation = check_refranation(p1, p2)
    if refranation:
        conditions.append(refranation)

    # 8. Mutual Reception (Mitigation)
    reception = check_mutual_reception(p1, p2, chart)
    if reception:
        conditions.append(reception)

    # 9. Besiegement
    besiegement_p1 = check_besiegement(p1, chart)
    if besiegement_p1:
        conditions.append(besiegement_p1)

    besiegement_p2 = check_besiegement(p2, chart)
    if besiegement_p2:
        conditions.append(besiegement_p2)

    # 10. Antiscia / Contra-antiscia
    a1, ca1 = calculate_antiscia(p1.longitude)
    orb = 1.0  # Standard orb for Antiscia

    diff_a = abs(p2.longitude - a1) % 360
    if diff_a > 180:
        diff_a = 360 - diff_a
    if diff_a <= orb:
        conditions.append(
            {
                "condition": "Antiscia",
                "details": f"{p2.name.value} is on the Antiscia of {p1.name.value}. Hidden connection.",
                "status": "Active",
            }
        )

    diff_ca = abs(p2.longitude - ca1) % 360
    if diff_ca > 180:
        diff_ca = 360 - diff_ca
    if diff_ca <= orb:
        conditions.append(
            {
                "condition": "Contra-antiscia",
                "details": f"{p2.name.value} is on the Contra-antiscia of {p1.name.value}.",
                "status": "Active",
            }
        )

    # 11. Retrograde Significator
    if p1.speed < 0 and p1.name not in {
        PlanetName.SUN,
        PlanetName.MOON,
    }:  # Sun/Moon never retrograde
        conditions.append(
            {
                "condition": "Retrograde Significator",
                "details": f"{p1.name.value} is Retrograde. If Querent, they will withdraw or change their mind. If Quesited, the matter unravels or returns to a previous state.",
                "status": "Active",
            }
        )
    if p2.speed < 0 and p2.name not in {PlanetName.SUN, PlanetName.MOON}:
        conditions.append(
            {
                "condition": "Retrograde Significator",
                "details": f"{p2.name.value} is Retrograde. If Querent, they will withdraw or change their mind. If Quesited, the matter unravels or returns to a previous state.",
                "status": "Active",
            }
        )

    # 12. Cazimi
    sun = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
    if sun:
        for p, role in [(p1, "Querent"), (p2, "Quesited")]:
            if p.name != PlanetName.SUN:
                dist = abs(p.longitude - sun.longitude) % 360
                if dist > 180:
                    dist = 360 - dist
                if dist <= (17 / 60):
                    conditions.append(
                        {
                            "condition": "Cazimi",
                            "details": f"{p.name.value} is Cazimi (in the heart of the Sun). Supreme empowerment and protection for the {role}.",
                            "status": "Active",
                        }
                    )

    return conditions


KEYWORD_HOUSES = [
    (
        10,
        "Career/Status",
        ["job", "career", "promotion", "work", "boss", "business", "office"],
    ),
    (
        4,
        "Home/Property",
        [
            "house",
            "home",
            "property",
            "real estate",
            "apartment",
            "land",
            "move",
            "parent",
            "father",
            "mother",
        ],
    ),
    (
        7,
        "Relationships/Contracts",
        [
            "relationship",
            "marriage",
            "partner",
            "spouse",
            "boyfriend",
            "girlfriend",
            "dating",
            "divorce",
            "contract",
            "lawsuit",
            "opponent",
            "enemy",
        ],
    ),
    (
        2,
        "Money/Resources",
        [
            "money",
            "finance",
            "loan",
            "debt",
            "salary",
            "pay",
            "wealth",
            "income",
            "purchase",
            "buy",
            "sell",
            "investment",
        ],
    ),
    (
        6,
        "Health/Service",
        [
            "health",
            "illness",
            "disease",
            "medical",
            "surgery",
            "diagnosis",
            "workout",
            "pet",
            "dog",
            "cat",
            "employee",
        ],
    ),
    (
        5,
        "Children/Creation",
        [
            "child",
            "children",
            "pregnant",
            "baby",
            "fertility",
            "creative",
            "art",
            "romance",
        ],
    ),
    (
        9,
        "Travel/Study",
        [
            "travel",
            "visa",
            "immigration",
            "study",
            "school",
            "college",
            "university",
            "publishing",
            "foreign",
            "religion",
        ],
    ),
    (
        3,
        "Communication/Siblings",
        [
            "sibling",
            "brother",
            "sister",
            "neighbor",
            "message",
            "letter",
            "email",
            "communication",
            "trip",
            "car",
            "drive",
        ],
    ),
    (
        8,
        "Death/Other's Money",
        [
            "death",
            "taxes",
            "inheritance",
            "mortgage",
            "partner's money",
            "debt relief",
            "tax",
            "fear",
        ],
    ),
    (
        11,
        "Friends/Hopes",
        ["friend", "friends", "hope", "wish", "group", "club", "advisor", "network"],
    ),
    (
        12,
        "Secrets/Undoing",
        [
            "secret",
            "prison",
            "jail",
            "magic",
            "hidden",
            "isolation",
            "hospital",
            "asylum",
            "witchcraft",
        ],
    ),
    (
        1,
        "Self/Life",
        ["myself", "me", "my life", "happiness", "my body", "appearance", "vitality"],
    ),
]

POSITIVE_CONDITIONS = {
    "Direct Application",
    "Easy Perfection",
    "Hard Perfection",
    "Translation of Light",
    "Collection of Light",
    "Mutual Reception",
    "Minor Mutual Reception",
    "Reception",
    "Antiscia",
    "Cazimi",
    "Bodily Placement",
    "Besiegement by Benefics",
}

NEGATIVE_CONDITIONS = {
    "Regretful Perfection",
    "Prohibition",
    "Refranation",
    "Frustration",
    "Abscission of Light",
    "Besiegement by Malefics",
    "Contra-antiscia",
    "Retrograde Significator",
}

CONDITION_WEIGHTS = {
    "Direct Application": 4,
    "Easy Perfection": 4,
    "Hard Perfection": 2,
    "Regretful Perfection": -2,
    "Translation of Light": 3,
    "Collection of Light": 3,
    "Bodily Placement": 3,
    "Mutual Reception": 3,
    "Minor Mutual Reception": 1,
    "Reception": 1,
    "Antiscia": 1,
    "Cazimi": 0,  # Double-dipping fixed: score purely delegated to dignities.py (+5)
    "Contra-antiscia": -1,
    "Prohibition": -4,
    "Refranation": -3,
    "Frustration": -4,
    "Abscission of Light": -4,
    "Besiegement by Malefics": -5,
    "Besiegement by Benefics": 5,
    "Retrograde Significator": 0,  # Double-dipping fixed: score purely delegated to dignities.py (-5)
}

BENEFICS = {PlanetName.JUPITER, PlanetName.VENUS}
MALEFICS = {PlanetName.MARS, PlanetName.SATURN}
DIURNAL = {PlanetName.SUN, PlanetName.JUPITER, PlanetName.SATURN}
NOCTURNAL = {PlanetName.MOON, PlanetName.VENUS, PlanetName.MARS}


def get_sect_score(planet_name: PlanetName, chart_sect: Sect) -> int:
    if chart_sect == Sect.DAY:
        if planet_name in DIURNAL:
            return 2
        if planet_name in NOCTURNAL:
            return -2
    else:
        if planet_name in NOCTURNAL:
            return 2
        if planet_name in DIURNAL:
            return -2
    return 0


def get_nature_score(planet_name: PlanetName) -> int:
    if planet_name in BENEFICS:
        return 2
    if planet_name in MALEFICS:
        return -2
    return 0


def score_significator(
    planet: Planet, chart: Chart
) -> Dict[str, int | str | List[str]]:
    chart_sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
    essential = DignityCalculator.calculate_planet_dignity(
        planet.name, planet.longitude, chart_sect
    )
    accidental = DignityCalculator.calculate_accidental_dignity(planet, chart)
    hayz = DignityCalculator.check_hayz_halb(planet.name, planet.longitude, chart)

    hayz_bonus = 0
    if hayz["status"] == "Hayz":
        hayz_bonus = 3
    elif hayz["status"] == "Halb":
        hayz_bonus = 2
    elif hayz["status"] == "In Sect":
        hayz_bonus = 1

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
        "total_score": total,
    }


def score_conditions(conditions: List[Dict]) -> Dict[str, int | List[Dict]]:
    breakdown = []
    total = 0
    for condition in conditions:
        name = str(condition.get("condition", ""))
        weight = CONDITION_WEIGHTS.get(name, 0)
        total += weight
        breakdown.append({"condition": name, "weight": weight})
    return {"total_score": total, "breakdown": breakdown}


def select_quesited_house(question: str) -> Dict[str, str | int]:
    import re

    q = (question or "").lower()

    best_house = 7
    best_label = "Relationships/Other"
    max_hits = 0

    for house, label, keywords in KEYWORD_HOUSES:
        hits = 0
        for k in keywords:
            hits += len(re.findall(rf"\b{re.escape(k)}\b", q))

        if hits > max_hits:
            max_hits = hits
            best_house = house
            best_label = label

    return {"house": best_house, "label": best_label}


def get_house_sign(asc_sign_idx: int, house_num: int) -> Sign:
    signs = list(Sign)
    return signs[(asc_sign_idx + (house_num - 1)) % 12]


def evaluate_horary_conditions(
    conditions: List[Dict],
    condition_score: int,
    strength_score: int,
    strictures: Optional[List[str]] = None,
) -> Dict[str, str | int]:
    strictures = strictures or []
    pos = [c for c in conditions if c.get("condition") in POSITIVE_CONDITIONS]
    neg = [c for c in conditions if c.get("condition") in NEGATIVE_CONDITIONS]
    total_score = condition_score + strength_score

    voc_penalty = 0
    if any("strictly Void of Course" in s for s in strictures):
        voc_penalty = -5
    elif any("Medieval/Lilly Out-of-Sign Rule" in s for s in strictures):
        voc_penalty = -3

    total_score += voc_penalty

    perfection_events = {
        "Direct Application",
        "Easy Perfection",
        "Hard Perfection",
        "Regretful Perfection",
        "Translation of Light",
        "Collection of Light",
        "Antiscia",
        "Mutual Reception",
        "Bodily Placement",
    }
    is_perfecting = any(c.get("condition") in perfection_events for c in conditions)

    if not is_perfecting:
        verdict = "No"
        weight = "No Connection"
    elif total_score >= 6:
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
        "total_score": total_score,
    }


def build_horary_oracle(question: str, chart: Chart) -> Dict:
    asc_sign_idx = int(chart.ascendant / 30) % 12
    asc_sign = list(Sign)[asc_sign_idx]
    querent_ruler = DOMICILES[asc_sign]

    quesited_info = select_quesited_house(question)
    quesited_sign = get_house_sign(asc_sign_idx, quesited_info["house"])  # type: ignore
    quesited_ruler = DOMICILES[quesited_sign]

    # Traditional Override: If the Querent and Quesited share the exact same ruler (e.g. Venus rules both 1st and 8th),
    # the Moon is exclusively assigned to represent the Querent, and the house ruler remains with the Quesited.
    if querent_ruler == quesited_ruler:
        querent_ruler = PlanetName.MOON

    conditions = analyze_horary_physics(querent_ruler, quesited_ruler, chart)

    if querent_ruler != PlanetName.MOON and quesited_ruler != PlanetName.MOON:
        moon_conditions = analyze_horary_physics(PlanetName.MOON, quesited_ruler, chart)
        for mc in moon_conditions:
            mc["details"] = mc.get("details", "") + " [Moon as Co-Significator]"
            conditions.append(mc)

    querent_planet = next((p for p in chart.planets if p.name == querent_ruler), None)
    quesited_planet = next((p for p in chart.planets if p.name == quesited_ruler), None)

    if querent_planet and quesited_planet and chart.houses:
        q_house = get_planet_house(querent_planet.longitude, chart)
        t_house = get_planet_house(quesited_planet.longitude, chart)

        target_house_num = quesited_info["house"]

        if q_house == target_house_num:
            conditions.append(
                {
                    "condition": "Bodily Placement",
                    "details": f"The Querent ({querent_ruler.value}) is bodily located in the Quesited's House ({target_house_num}H). The Querent goes to the Quesited.",
                    "status": "Active",
                }
            )
        if t_house == 1:
            conditions.append(
                {
                    "condition": "Bodily Placement",
                    "details": f"The Quesited ({quesited_ruler.value}) is bodily located in the Querent's House (1H). The Quesited comes to the Querent.",
                    "status": "Active",
                }
            )

    querent_strength = (
        score_significator(querent_planet, chart) if querent_planet else None
    )
    quesited_strength = (
        score_significator(quesited_planet, chart) if quesited_planet else None
    )
    condition_score = score_conditions(conditions)

    strength_total = 0
    if querent_strength:
        strength_total += int(querent_strength.get("total_score", 0))  # type: ignore
    if quesited_strength:
        strength_total += int(quesited_strength.get("total_score", 0))  # type: ignore
    if querent_strength and quesited_strength:
        strength_total = int(round(strength_total / 2))

    strictures = check_strictures(chart)
    cond_total = int(condition_score.get("total_score", 0))  # type: ignore
    verdict_data = evaluate_horary_conditions(
        conditions, cond_total, strength_total, strictures
    )

    return {
        "question": question,
        "querent_sign": asc_sign.value,
        "querent_ruler": querent_ruler.value,
        "quesited_house": quesited_info["house"],
        "quesited_label": quesited_info["label"],
        "quesited_sign": quesited_sign.value,
        "quesited_ruler": quesited_ruler.value,
        "conditions": conditions,
        "strictures": strictures,
        "verdict": verdict_data["verdict"],
        "verdict_weight": verdict_data["weight"],
        "strength_score": strength_total,
        "total_score": verdict_data["total_score"],
    }
