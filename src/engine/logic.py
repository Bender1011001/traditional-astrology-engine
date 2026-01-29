
from typing import Optional, Dict, List
import re
from datetime import datetime
from .models import Planet, Chart, Sect, PlanetName, Sign
from .lots import calculate_all_lots
from .prediction import (
    calculate_profection_sign,
    get_lord_of_year,
    calculate_monthly_profection,
    calculate_daily_profection,
    calculate_epitasis_days,
    calculate_firdaria,
    calculate_zr_periods,
    calculate_zr_lifetime_map
)
from .stars import check_fixed_stars, get_fixed_star_meta
from .nodes import analyze_nodes
from .dignities import DignityCalculator
from .calculations import calculate_lunar_phase, calculate_prenatal_syzygy
from .mundane import get_recent_eclipses, check_eclipse_impact, check_universal_causation_dec2025, MundaneEngine
from .horary import analyze_horary_physics, calculate_antiscia
from database.db_manager import DelineationLibrary
import swisseph as swe

# Initialize Library
LIB = DelineationLibrary()

PLANET_ESSENCES = {
    PlanetName.SUN: "Sovereignty and Identity",
    PlanetName.MOON: "Emotional Synthesis and Adaptation",
    PlanetName.MERCURY: "Analytical Mastery and Communication",
    PlanetName.VENUS: "Harmony and Value Creation",
    PlanetName.MARS: "Strategic Action and Drive",
    PlanetName.JUPITER: "Expansion and Wisdom",
    PlanetName.SATURN: "Structural Integrity and Responsibility"
}

RULE_SOURCE_MAP = {
    "Bonatti Consideration 5": ["Bonatti, Liber Astronomiae, Consideration 5 (Void of Course)"],
    "Bonatti Consideration 30": ["Bonatti, Liber Astronomiae, Consideration 30 (Planet at 29°)"],
    "Bonatti Consideration 141": ["Bonatti, Liber Astronomiae, Consideration 141 (Significator in Ascendant)"],
    "Via Combusta": ["Traditional doctrine (Lilly, Christian Astrology, p. 115)"],
    "Combustion": ["Traditional doctrine (Ptolemy, Tetrabiblos I.24; Lilly, CA, p. 113)"],
    "Besiegement": ["Traditional doctrine (Lilly, Christian Astrology, p. 114)"],
    "Antiscia": ["Firmicus Maternus, Mathesis II.30", "Lilly, CA, p. 90"],
    "Melothesia": ["Manilius, Astronomica IV", "Culpeper, English Physician"],
    "Sect/Hayz/Halb": ["Ptolemy, Tetrabiblos III.3", "Dorotheus, Carmen Astrologicum I.1"],
    "Universal Overdrive": ["Ptolemy, Tetrabiblos II.1"],
    "Universal Causation": ["Ptolemy, Tetrabiblos II.8"],
    "Mundane Rank 4 > Natal Particulars": ["Traditional mundane hierarchy (Ptolemy, Tetrabiblos II.3)"],
    "Aries Ingress": ["Traditional mundane ingress doctrine (Bonatti, Liber Astronomiae, VIII)"]
}

def _extract_sources(text: Optional[str]) -> List[str]:
    if not text:
        return []
    matches = re.findall(r"\(([^)]+)\)", text)
    return [m.strip() for m in matches if m.strip()]

def _resolve_sources(cause: Optional[str], rule_text: Optional[str]) -> List[str]:
    sources = []
    sources.extend(_extract_sources(rule_text))
    if not sources and rule_text in RULE_SOURCE_MAP:
        sources.extend(RULE_SOURCE_MAP[rule_text])
    if cause:
        for key, refs in RULE_SOURCE_MAP.items():
            if key in cause:
                sources.extend(refs)
                break
    deduped = []
    for src in sources:
        if src not in deduped:
            deduped.append(src)
    return deduped

def _estimate_confidence(sources: List[str], conflicts: List[str], base: int = 70) -> int:
    score = base
    # Increase confidence with more sources
    if sources:
        score += min(15, 5 * len(sources))
    else:
        score -= 15 # No direct source attribution

    # Deduct for internal conflicts in the tradition
    if conflicts:
        score -= min(30, 10 * len(conflicts))
    
    # Check for widespread consensus (heuristic)
    consensus_sources = ["Ptolemy", "Lilly", "Valens", "Bonatti", "Dorotheus"]
    source_str = " ".join(sources)
    consensus_hits = sum(1 for cs in consensus_sources if cs in source_str)
    if consensus_hits >= 3:
        score += 10
    
    if score < 15: score = 15
    if score > 98: score = 98
    return score

def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    return cleaned or "rule"

TERM_METHODS = {
    PlanetName.SUN: "Radiance and Authority",
    PlanetName.MOON: "Receptivity and Fluency",
    PlanetName.MERCURY: "Precision and Communication",
    PlanetName.VENUS: "Grace and Relatability",
    PlanetName.MARS: "Strategy and Fortitude",
    PlanetName.JUPITER: "Growth and Principles",
    PlanetName.SATURN: "Structure and Restraint"
}

def is_benefic_of_sect(planet_name: PlanetName, chart_sect: Sect) -> bool:
    if chart_sect == Sect.DAY:
        return planet_name in [PlanetName.SUN, PlanetName.JUPITER, PlanetName.SATURN]
    else:
        return planet_name in [PlanetName.MOON, PlanetName.VENUS, PlanetName.MARS]
        
def is_malefic_out_of_sect(planet_name: PlanetName, chart_sect: Sect) -> bool:
    if chart_sect == Sect.DAY:
        return planet_name == PlanetName.MARS
    else:
        return planet_name == PlanetName.SATURN

def is_besieged(planet: Planet, chart: Chart) -> bool:
    mars = next((p for p in chart.planets if p.name == PlanetName.MARS), None)
    saturn = next((p for p in chart.planets if p.name == PlanetName.SATURN), None)
    
    if not mars or not saturn or planet.name in [PlanetName.MARS, PlanetName.SATURN]:
        return False
        
    def get_shortest_arc(p1_lon, p2_lon):
        diff = p1_lon - p2_lon
        if diff > 180: diff -= 360
        if diff < -180: diff += 360
        return diff
    
    dist_mars = get_shortest_arc(planet.longitude, mars.longitude)
    dist_saturn = get_shortest_arc(planet.longitude, saturn.longitude)
    
    # Check if between
    if (dist_mars * dist_saturn < 0) and (abs(dist_mars) + abs(dist_saturn) < 15):
        return True
    return False

def generate_soul_guardian_reading(chart: Chart, jd: float) -> Dict:
    """
    Calculates the Almuten Figuris and generates a 'Life Job Description'.
    """
    sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
    san_lon = calculate_prenatal_syzygy(jd)
    almuten_data = DignityCalculator.calculate_almuten_figuris(chart, san_lon)
    
    winner_name = almuten_data["almuten_figuris"]
    winner_enum = PlanetName(winner_name)
    
    # Get winner's position to find its terms
    winner_planet = next((p for p in chart.planets if p.name == winner_enum), None)
    if not winner_planet:
        return almuten_data # Should not happen
        
    dignities = DignityCalculator.get_essential_rulers(winner_planet.longitude, sect)
    term_ruler = dignities["term"]
    
    # Generate Job Description
    essence = PLANET_ESSENCES.get(winner_enum, "Sovereignty and Depth")
    method = TERM_METHODS.get(term_ruler, "Unique Pathways")
    
    job_description = f"You are ruled by a Sovereign {winner_name} in the Terms of {term_ruler.value}—your soul's function is {essence} through {method}."
    
    return {
        "almuten": winner_name,
        "term_ruler": term_ruler.value,
        "job_description": job_description,
        "scores": almuten_data["planet_breakdown"],
        "total_score": almuten_data["total_score"],
        "prenatal_syzygy_lon": san_lon
    }

def calculate_solar_status(planet: Planet, sun: Planet) -> str:
    diff = abs(planet.longitude - sun.longitude)
    if diff > 180: diff = 360 - diff
    
    if diff < 0.28: # 17 minutes
        return "CAZIMI"
    if diff < 8.0:
        return "COMBUST"
    if diff < 15.0:
        return "UNDER_BEAMS"
    return "FREE"

def is_in_via_combusta(longitude: float) -> bool:
    """
    Via Combusta (The Burning Way): 15° Libra to 15° Scorpio (195° to 225°).
    """
    return 195.0 <= longitude <= 225.0

def melothesia_check(planet_name: PlanetName, sign: Sign) -> Dict:
    """
    Medical Astrology (Melothesia) mapping.
    Identifies body region and potential pathology based on sign placement.
    Source: Binder1_part_014.txt
    """
    mapping = {
        Sign.ARIES: {"region": "Head, face, brain, eyes, teeth", "pathology": "Headaches, fevers, eye issues"},
        Sign.TAURUS: {"region": "Throat, neck, thyroid, tonsils", "pathology": "Laryngitis, tonsillitis, thyroid issues"},
        Sign.GEMINI: {"region": "Lungs, shoulders, arms, hands", "pathology": "Asthma, bronchitis, respiratory issues"},
        Sign.CANCER: {"region": "Chest, stomach, breasts, diaphragm, lymphatic system", "pathology": "Dyspepsia, gastric ulcers, lymphatic stasis"},
        Sign.LEO: {"region": "Heart, spine, back, circulation", "pathology": "Heart disease, spinal issues, blood pressure"},
        Sign.VIRGO: {"region": "Abdomen, intestines, pancreas, spleen", "pathology": "Digestive disorders, intestinal issues"},
        Sign.LIBRA: {"region": "Kidneys, bladder, lower back, veins", "pathology": "Renal issues, skin disorders, lumbar pain"},
        Sign.SCORPIO: {"region": "Reproductive organs, genitals, rectum", "pathology": "Reproductive/excretory issues, infections"},
        Sign.SAGITTARIUS: {"region": "Liver, hips, thighs, sciatic nerve", "pathology": "Liver disorders, hip issues, sciatica"},
        Sign.CAPRICORN: {"region": "Knees, joints, bones, teeth, skin", "pathology": "Arthritis, bone density issues, skin ailments"},
        Sign.AQUARIUS: {"region": "Shins, calves, ankles, circulatory system", "pathology": "Lower leg issues, circulatory sluggishness"},
        Sign.PISCES: {"region": "Feet, toes, lymphatic system", "pathology": "Foot issues, edema, lymphatic congestion"},
    }
    
    # Specific pathology overrides from binder
    specifics = ""
    if planet_name == PlanetName.SATURN and sign == Sign.CANCER:
        specifics = "Pyorrheas, dyspepsia, gastric ulcer, cancer, nausea, scurvy, jaundice, gall stones."
    elif planet_name == PlanetName.MARS and sign == Sign.TAURUS:
        specifics = "Diphtheria, laryngitis, tonsillitis, quinsy, glandular swelling of the throat."
    elif planet_name == PlanetName.SATURN and sign == Sign.GEMINI:
        specifics = "Asthma, bronchitis, consumption, pleurisy."
        
    res = mapping.get(sign, {"region": "Unknown", "pathology": "General debility"})
    if specifics:
        res["pathology"] = specifics
        
    return res

def is_void_of_course(moon_lon: float, chart_planets: List[Planet]) -> bool:
    """
    Bonatti Consideration 5: Void of Course Moon.
    Simplified: No major aspect before leaving the sign (30° boundary).
    """
    moon_sign_idx = int(moon_lon / 30)
    moon_pos_in_sign = moon_lon % 30
    dist_to_end = 30 - moon_pos_in_sign
    
    major_aspects = [0, 60, 90, 120, 180]
    
    for p in chart_planets:
        if p.name == PlanetName.MOON: continue
        # Calculate distance to aspect
        diff = (p.longitude - moon_lon) % 360
        if diff > 180: diff = 360 - diff # Shortest distance
        
        # Check if Moon reaches an aspect with this planet before 30°
        # This is a bit complex without full motion simulation, but we check if any
        # planet is within the remaining degrees of the sign in terms of aspect.
        # Actually, standard VOC is checking if the Moon *completes* any aspect.
        # If the Moon is at 25 deg and another planet is at 28 deg of another sign,
        # it will aspect it before leaving.
        
        for aspect in major_aspects:
            # Distance from current moon to the aspect point of planet p
            # Aspect point = p.longitude - aspect or p.longitude + aspect
            for sign_mult in [-1, 1]:
                target_lon = (p.longitude + (sign_mult * aspect)) % 360
                dist_to_target = (target_lon - moon_lon) % 360
                if dist_to_target < dist_to_end:
                    return False # Found an aspect before sign end
    return True

def analyze_planet_forensic(planet: Planet, chart: Chart, jd: float = 0.0) -> Dict:
    chart_sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
    
    result = {
        "planet": planet.name.value,
        "sign": planet.sign.value,
        "longitude": planet.longitude,
        "sect_status": "Neutral",
        "dignity_score": 0,
        "dignity_details": [],
        "dignity_conflicts": [],
        "dignity_variants": {},
        "power_label": "Average",
        "solar_status": "FREE",
        "impacts": [],
        "delineation_text": "",
        "house_number": 0,
        "house_delineation_text": ""
    }
    
    # 1. Universal Overrides (Eclipses)
    if jd > 0:
        # Standard Eclipses
        eclipses = get_recent_eclipses(jd)
        for ec in eclipses:
            impact = check_eclipse_impact(planet.longitude, ec["longitude"])
            if impact:
                result["impacts"].append({
                    "cause": f"Universal Overdrive: {ec['type']}",
                    "effect": impact,
                    "rule": "Universal overrides Particular (Ptolemy, Tetrabiblos Book II)"
                })
        
        # Specific December 2025 Universal Causation Audit
        universal_causes = check_universal_causation_dec2025(jd)
        for uc in universal_causes:
            # Check if this universal cause (eclipse) hits the planet
            impact = check_eclipse_impact(planet.longitude, uc["longitude"])
            if impact:
                result["impacts"].append({
                    "cause": f"Universal Causation: {uc['cause']}",
                    "effect": f"SUSPENDED NATAL PROMISE: {impact}",
                    "rule": uc['rule']
                })
        
        # 3. Rank 4: Aries Ingress Override
        year, m, d, h = swe.revjul(jd)
        mundane = MundaneEngine(jd)
        ingress = mundane.get_aries_ingress(int(year))
        # If the planet is in the sign of the Ingress or impacted by it
        if planet.sign == Sign.ARIES:
            result["impacts"].append({
                "cause": f"Aries Ingress {int(year)}",
                "effect": "RANK 4 OVERRIDE: Planet is in the sign of the World's New Year. Natal strength is secondary to Mundane shift.",
                "rule": "Mundane Rank 4 > Natal Particulars"
            })

    # 2. Constitutional Fitness (Sect, Hayz, Halb)
    hayz_halb = DignityCalculator.check_hayz_halb(planet.name, planet.longitude, chart)
    result["sect_status"] = hayz_halb["status"]
    for detail in hayz_halb["details"]:
        result["impacts"].append({"cause": "Sect/Hayz/Halb", "effect": detail})
        
    # 3. Essential Dignity
    dignity = DignityCalculator.calculate_planet_dignity(planet.name, planet.longitude, chart_sect)
    result["dignity_score"] = dignity["total_score"]
    result["dignity_details"] = dignity["details"]
    result["dignity_conflicts"] = dignity.get("conflicts", [])
    result["dignity_variants"] = dignity.get("variants", {})
    
    # 11. Accidental Dignity (Lilly Style)
    acc_dignity = DignityCalculator.calculate_accidental_dignity(planet, chart)
    result["accidental_score"] = acc_dignity["total_score"]
    result["accidental_details"] = acc_dignity["details"]
    
    # 12. Performance Index (Rule Weighting)
    # Weighting: Essential (0.6) + Accidental (0.4)
    essential_norm = (dignity["total_score"] + 5) / 15.0 
    accidental_norm = (acc_dignity["total_score"] + 10) / 25.0
    performance_index = (essential_norm * 0.6) + (accidental_norm * 0.4)
    result["performance_index"] = round(performance_index, 2)
    
    # Refined Power Labeling
    if performance_index >= 0.8: result["power_label"] = "Imperial (Unstoppable)"
    elif performance_index >= 0.65: result["power_label"] = "Sovereign (Resourceful)"
    elif performance_index >= 0.5: result["power_label"] = "Stable (Functional)"
    elif performance_index >= 0.35: result["power_label"] = "Debilitated (Struggling)"
    elif performance_index >= 0.2: result["power_label"] = "Vagabond (Corrupt/Empty)"
    else: result["power_label"] = "Cursed (Actively Harmful)"

    # Conflict Resolution Note
    if dignity["total_score"] > 3 and acc_dignity["total_score"] < -3:
        result["impacts"].append({
            "cause": "Clashing Dignity",
            "effect": "A 'Prisoner of Fortune': The planet has high theoretical power but lacks the means to express it due to accidental affliction.",
            "rule": "Traditional hierarchy of Essential vs Accidental performance."
        })
    elif dignity["total_score"] < -3 and acc_dignity["total_score"] > 5:
        result["impacts"].append({
            "cause": "Clashing Dignity",
            "effect": "An 'Elevated Scoundrel': The planet is inherently weak/malefic but occupies a position of accidental power. It may act boldly but with poor judgment.",
            "rule": "Traditional hierarchy of Essential vs Accidental performance."
        })
        
    # 4. Solar Conditions
    sun = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
    if sun and planet.name != PlanetName.SUN:
        solar_status = calculate_solar_status(planet, sun)
        result["solar_status"] = solar_status
        if solar_status == "COMBUST":
            result["impacts"].append({"cause": "Combustion", "effect": "NULL_RESULT: Planet is burned by the Sun."})

    # 5. Besiegement
    if is_besieged(planet, chart):
        result["impacts"].append({"cause": "Besiegement", "effect": "BLOCKED: Trapped between Malefics."})

    # 6. Via Combusta
    if is_in_via_combusta(planet.longitude):
        result["impacts"].append({
            "cause": "Via Combusta",
            "effect": "DEBILITATED: The Burning Way (15 Libra - 15 Scorpio). Signifies erratic and unstable energy."
        })

    # 7. Medical Astrology (Melothesia)
    medical = melothesia_check(planet.name, planet.sign)
    result["medical_region"] = medical["region"]
    result["medical_pathology"] = medical["pathology"]
    result["impacts"].append({
        "cause": "Melothesia",
        "effect": f"Anatomical Governance: {medical['region']}. Risk of {medical['pathology']}"
    })

    # 8. Bonatti Considerations
    # Consideration 30: Planet at 29° (Anaretic degree)
    pos_in_sign = planet.longitude % 30
    if pos_in_sign >= 29.0:
        result["impacts"].append({
            "cause": "Bonatti Consideration 30",
            "effect": "ANARETIC DEGREE: Planet at 29° (Changing signs). Signifies instability or extreme urgency."
        })
    
    # Consideration 5: Void of Course Moon
    if planet.name == PlanetName.MOON:
        if is_void_of_course(planet.longitude, chart.planets):
            result["impacts"].append({
                "cause": "Bonatti Consideration 5",
                "effect": "VOID OF COURSE: The Moon makes no major aspect before leaving the sign. Matters go hardly on."
            })
            
    # Consideration 141: Significator in the Ascendant
    # (Checking if planet is in 1st House)
    house_num = DignityCalculator.get_house_number(planet.longitude, chart.ascendant, getattr(chart, "houses", None))
    result["house_number"] = house_num
    
    if house_num == 1:
        result["impacts"].append({
            "cause": "Bonatti Consideration 141",
            "effect": "PERFECTION WITHOUT EFFORT: Significator in the Ascendant. High capacity for manifestation."
        })

    # 10. Antiscia Presence
    ant, cant = calculate_antiscia(planet.longitude)
    for other in chart.planets:
        if other.name == planet.name: continue
        dist = abs(other.longitude - ant) % 360
        if dist > 180: dist = 360 - dist
        if dist < 1.0:
            result["impacts"].append({
                "cause": "Antiscia",
                "effect": f"SHADOW CONTACT with {other.name.value}. A hidden or occult influence exists.",
                "rule": "Antiscia provides a 'mirror' strength regardless of ecliptic aspect."
            })

    # 9. Textual Delineations
    sect_str = "DAY" if chart_sect == Sect.DAY else "NIGHT"
    key = f"{planet.name.value.upper()}_{planet.sign.value.upper()}_{sect_str}"
    result["delineation_text"] = LIB.get_planet_delineation(key)
    
    # House (Whole Sign)
    house_key = f"{planet.name.value.upper()}_{house_num}"
    result["house_delineation_text"] = LIB.get_house_planet_delineation(house_key)
    
    return result

def calculate_jones_pattern(longitudes: List[float]) -> str:
    longs = sorted(longitudes)
    # Find max gap
    max_gap = 0
    for i in range(len(longs)):
        gap = (longs[(i+1)%len(longs)] - longs[i]) % 360
        if gap > max_gap:
            max_gap = gap
    
    occupied_arc = 360 - max_gap
    
    if occupied_arc <= 120: return "Bundle"
    if occupied_arc <= 185: return "Bowl"
    if occupied_arc <= 240: return "Locomotive"
    if max_gap < 30: return "Splash"
    return "Splay/Seesaw"

from .temperament import TemperamentEngine
from .mansions import LunarMansionEngine
from .hyleg import HylegAlcocodenEngine
from .planetary_hours import PlanetaryHourEngine
from .primary_directions import PrimaryDirectionsEngine
from .reception import ReceptionEngine, ReceptionMode

def perform_forensic_audit(chart: Chart, jd: float = 0.0, age: Optional[int] = None, month: int = 1, day: int = 1, birth_date: Optional[datetime] = None, analysis_date: Optional[datetime] = None, analysis_jd: Optional[float] = None) -> Dict:
    sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
    
    sun = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
    moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)
    
    # Elemental Balance
    elements = {"FIRE": 0, "EARTH": 0, "AIR": 0, "WATER": 0}
    for p in chart.planets:
        if p.name in [PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]: continue
        el = DignityCalculator.ZODIAC_ELEMENTS.get(p.sign)
        if el: elements[el] += 1

    # Temperament Assessment (Lilly)
    temperament = TemperamentEngine.calculate_temperament(chart)
    
    # Lunar Mansion (Picatrix)
    lunar_mansion = LunarMansionEngine.get_lunar_mansion(moon.longitude) if moon else None

    # Hyleg & Alcocoden (Vitality)
    hyleg = HylegAlcocodenEngine.determine_hyleg(chart)
    alcocoden = None
    vitality_report = {}
    if hyleg:
        alcocoden = HylegAlcocodenEngine.determine_alcocoden(hyleg, chart)
        if alcocoden:
            vitality_report = HylegAlcocodenEngine.calculate_lifespan(hyleg, alcocoden, chart)
            
    # Planetary Hours
    hours_data = {}
    # Use chart geo if available; otherwise fallback to London (research default).
    demo_lat = chart.geo_lat if chart.geo_lat is not None else 51.5074
    demo_lon = chart.geo_lon if chart.geo_lon is not None else -0.1278
    
    if birth_date:
        hours_data = PlanetaryHourEngine.calculate_hours(birth_date, demo_lat, demo_lon)

    # Primary Directions (Placidus)
    # Calculate directions to angles for next 100 years
    primary_dirs = PrimaryDirectionsEngine.calculate_directions_to_angles(chart, demo_lat)
    # Filter for reasonable life range (e.g. 0 to 100 years)
    primary_dirs = [d for d in primary_dirs if 0 <= d.years <= 100]
    # Serialize for JSON
    primary_dirs_json = [{
        "significator": d.significator,
        "promittor": d.promittor,
        "aspect": d.aspect,
        "arc": round(d.arc, 2),
        "years": round(d.years, 2),
        "date_offset": d.date_offset,
        "method": d.method
    } for d in primary_dirs]

    # Receptions (Lilly Mode Default)
    receptions = ReceptionEngine.calculate_mutual_receptions(chart, ReceptionMode.STANDARD_LILLY)
    receptions_json = [{
        "planet_a": r.planet_a.value,
        "planet_b": r.planet_b.value,
        "type": r.type,
        "score": r.strength_score,
        "dignities_a_in_b": r.reception_a_in_b.dignities,
        "dignities_b_in_a": r.reception_b_in_a.dignities
    } for r in receptions]

    # Identify Teams
    constructive_team = []
    destructive_team = []
    for p in chart.planets:
        if is_benefic_of_sect(p.name, sect):
            constructive_team.append(p.name.value)
        elif is_malefic_out_of_sect(p.name, sect):
            destructive_team.append(p.name.value)

    report = {
        "summary": {
            "sect": sect.value,
            "temperament": temperament,
            "lunar_mansion": lunar_mansion,
            "planetary_hours": hours_data,
            "mutual_receptions": receptions_json,
            "constructive_team": constructive_team,
            "destructive_team": destructive_team,
            "team_note": "Trust the energies/people of your Constructive Team; exercise caution with the Destructive Team.",
            "universal_events": [],
            "lunar_phase": calculate_lunar_phase(sun.longitude, moon.longitude)[0] if sun and moon else "Unknown",
            "lunar_phase_profile": calculate_lunar_phase(sun.longitude, moon.longitude)[1] if sun and moon else "Unknown",
            "jones_pattern": calculate_jones_pattern([p.longitude for p in chart.planets if p.name.value in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]]),
            "dominant_elements": sorted(elements.items(), key=lambda x: x[1], reverse=True)
        },
        "vitality": vitality_report,
        "primary_directions": primary_dirs_json,
        "soul_guardian": generate_soul_guardian_reading(chart, jd) if jd > 0 else {},
        "planets": [],
        "lots": calculate_all_lots(chart, sect),
        "stars": check_fixed_stars(chart),
        "fixed_star_meta": get_fixed_star_meta(),
        "nodes": analyze_nodes(chart)
    }
    
    # 6. Daily Oracle (Traditional Synthesized Forecast)
    # Use analysis_jd if available (transits), else fall back to birth jd (though that's static)
    oracle_jd = analysis_jd if analysis_jd else jd
    report["daily_oracle"] = generate_daily_oracle(chart, report, oracle_jd, age, month, day)

    if jd > 0:
        report["summary"]["universal_events"] = get_recent_eclipses(jd)
        report["summary"]["universal_causation_audit"] = check_universal_causation_dec2025(jd)
        
    for planet in chart.planets:
        planet_data = analyze_planet_forensic(planet, chart, jd)
        report["planets"].append(planet_data)

    rule_ledger = []
    rule_counts = {}

    def _unique_rule_id(base: str) -> str:
        count = rule_counts.get(base, 0) + 1
        rule_counts[base] = count
        return f"{base}-{count}" if count > 1 else base

    for planet_data in report["planets"]:
        planet_label = planet_data.get("planet", "Planet")
        base_trace = [
            f"Planet: {planet_label}",
            f"Sign: {planet_data.get('sign')}",
            f"Longitude: {planet_data.get('longitude'):.2f}°" if isinstance(planet_data.get("longitude"), (int, float)) else "Longitude: —",
            f"House: {planet_data.get('house_number')}"
        ]

        dignity_details = planet_data.get("dignity_details", [])
        if dignity_details:
            conflicts = planet_data.get("dignity_conflicts", [])
            sources = ["Dorotheus, Carmen Astrologicum I", "Ptolemy, Tetrabiblos I"]
            rule_id = _unique_rule_id(f"{planet_label.lower()}-{_slugify('dignity')}")
            rule_ledger.append({
                "id": rule_id,
                "category": "Essential Dignity",
                "condition": f"{planet_label} in {planet_data.get('sign')}",
                "judgment": f"Dignity score {planet_data.get('dignity_score')}: " + "; ".join(dignity_details),
                "sources": sources,
                "confidence": _estimate_confidence(sources, conflicts, base=72),
                "conflicts": conflicts,
                "trace": base_trace + [f"Details: {detail}" for detail in dignity_details]
            })

            # Educational: Flag source divergence specifically
            if conflicts:
                rule_ledger.append({
                    "id": _unique_rule_id(f"{planet_label.lower()}-divergence"),
                    "category": "Traditional Divergence",
                    "condition": f"Source Clashes for {planet_label}",
                    "judgment": "Authorities disagree: " + " | ".join(conflicts),
                    "sources": ["Ptolemy", "Dorotheus", "Egyptian Codex"],
                    "confidence": 50, # Divergence reduces objective certainty
                    "conflicts": conflicts,
                    "trace": base_trace + ["Reason: Contradiction in primary source traditions"]
                })

        for impact in planet_data.get("impacts", []):
            cause = impact.get("cause") or "Condition"
            effect = impact.get("effect") or ""
            sources = _resolve_sources(cause, impact.get("rule"))
            rule_id = _unique_rule_id(f"{planet_label.lower()}-{_slugify(cause)}")
            trace = base_trace[:]
            if impact.get("rule"):
                trace.append(f"Rule: {impact.get('rule')}")
            rule_ledger.append({
                "id": rule_id,
                "category": "Condition",
                "condition": f"{planet_label}: {cause}",
                "judgment": effect,
                "sources": sources,
                "confidence": _estimate_confidence(sources, [], base=70),
                "conflicts": [],
                "trace": trace
            })

        planet_text = planet_data.get("delineation_text") or ""
        if planet_text and "Delineation not found" not in planet_text:
            sources = _extract_sources(planet_text)
            rule_id = _unique_rule_id(f"{planet_label.lower()}-{_slugify('planet-delineation')}")
            rule_ledger.append({
                "id": rule_id,
                "category": "Planet Delineation",
                "condition": f"{planet_label} in {planet_data.get('sign')}",
                "judgment": planet_text,
                "sources": sources,
                "confidence": _estimate_confidence(sources, [], base=68),
                "conflicts": [],
                "trace": base_trace + ["Source: planet delineation library"]
            })

        house_text = planet_data.get("house_delineation_text") or ""
        if house_text and "Delineation not found" not in house_text:
            sources = _extract_sources(house_text)
            rule_id = _unique_rule_id(f"{planet_label.lower()}-{_slugify('house-delineation')}")
            rule_ledger.append({
                "id": rule_id,
                "category": "House Delineation",
                "condition": f"{planet_label} in House {planet_data.get('house_number')}",
                "judgment": house_text,
                "sources": sources,
                "confidence": _estimate_confidence(sources, [], base=68),
                "conflicts": [],
                "trace": base_trace + ["Source: house delineation library"]
            })

    lunar_mansion = report.get("summary", {}).get("lunar_mansion")
    if lunar_mansion:
        mansion_name = lunar_mansion.get("name")
        mansion_id = lunar_mansion.get("mansion_id")
        sources = lunar_mansion.get("source_refs", [])
        rule_id = _unique_rule_id(f"lunar-mansion-{mansion_id}")
        rule_ledger.append({
            "id": rule_id,
            "category": "Lunar Mansion",
            "condition": f"Moon in Mansion {mansion_id} ({mansion_name})",
            "judgment": "Applied lunar mansion intents for operational guidance.",
            "sources": sources,
            "confidence": _estimate_confidence(sources, [], base=75),
            "conflicts": [],
            "trace": [
                f"Mansion: {mansion_name}",
                f"Range: {lunar_mansion.get('start_lon_deg')}°–{lunar_mansion.get('end_lon_deg')}°"
            ]
        })

    report["rule_ledger"] = rule_ledger

    # 7. Horary Physics (Synthesis of Significators)
    # We analyze physics between the Lord of the 1st and the Lord of the Year (if age provided)
    # Or Moon vs others.
    if age is not None:
        asc_sign_idx = int(chart.ascendant / 30) % 12
        essentials = DignityCalculator.get_essential_rulers(chart.ascendant, sect)
        asc_lord = essentials["domicile"]
        annual_sign = calculate_profection_sign(list(Sign)[asc_sign_idx], age)
        loy_lord = get_lord_of_year(annual_sign)
        
        report["horary_physics"] = {
            "significators": f"{asc_lord.value} (L1) and {loy_lord.value} (LoY)",
            "interactions": analyze_horary_physics(asc_lord, loy_lord, chart)
        }
        
    # 7. Prediction (Profections)
    if age is not None:
        asc_sign_idx = int(chart.ascendant / 30) % 12
        asc_sign = list(Sign)[asc_sign_idx]
        
        signs = list(Sign)
        annual_index = (asc_sign_idx + age) % 12
        annual_sign = signs[annual_index]
        loy_name = get_lord_of_year(annual_sign)
        
        # Monthly
        monthly_cont_index = (annual_index + (month - 1)) % 12
        monthly_sign_cont = signs[monthly_cont_index]
        total_months = None
        if birth_date and analysis_date:
            total_months = (analysis_date.year - birth_date.year) * 12 + (analysis_date.month - birth_date.month)
            if analysis_date.day < birth_date.day:
                total_months -= 1
            if total_months < 0:
                total_months = 0
        elif age is not None:
            total_months = (age * 12) + (month - 1)
        monthly_salt_index = (asc_sign_idx + (total_months or 0)) % 12
        monthly_sign_salt = signs[monthly_salt_index]
        
        # Daily
        daily_rate = 7 / 3
        daily_steps = int((day - 1) / daily_rate)
        daily_index = (monthly_cont_index + daily_steps) % 12
        daily_sign = signs[daily_index]
        
        # Epitasis (needs transiting LoY)
        # Find the LoY in the current chart (assuming 'chart' contains transits)
        loy_planet = next((p for p in chart.planets if p.name == loy_name), None)
        epitasis_days = []
        loy_trans_sign = None
        loy_trans_source = None
        if analysis_jd:
            pid = getattr(swe, loy_name.value.upper(), None)
            if pid is not None:
                try:
                    loy_trans_res = swe.calc_ut(analysis_jd, pid, swe.FLG_SWIEPH)[0]
                    loy_trans_lon = loy_trans_res[0]
                    loy_trans_sign = list(Sign)[int(loy_trans_lon / 30) % 12]
                    loy_trans_source = "transit"
                except swe.Error:
                    loy_trans_sign = None
        if loy_trans_sign:
            epitasis_days = calculate_epitasis_days(monthly_sign_cont, loy_trans_sign)
        elif loy_planet:
            epitasis_days = calculate_epitasis_days(monthly_sign_cont, loy_planet.sign)
            loy_trans_sign = loy_planet.sign
            loy_trans_source = "natal"
            
        report["prediction"] = {
            "age": age,
            "month": month,
            "day": day,
            "annual_profection": {
                "sign": annual_sign.value,
                "lord_of_year": loy_name.value
            },
            "monthly_profection": {
                "continuous": monthly_sign_cont.value,
                "saltatory": monthly_sign_salt.value
            },
            "daily_profection": {
                "sign": daily_sign.value
            },
            "epitasis_days": epitasis_days,
            "calculation_steps": {
                "annual_profection": {
                    "formula": "(asc_index + age) mod 12",
                    "asc_sign": asc_sign.value,
                    "asc_index": asc_sign_idx,
                    "age": age,
                    "target_index": annual_index,
                    "result_sign": annual_sign.value
                },
                "lord_of_year": {
                    "formula": "domicile(annual_sign)",
                    "annual_sign": annual_sign.value,
                    "lord_of_year": loy_name.value
                },
                "monthly_profection": {
                    "continuous": {
                        "formula": "(annual_index + (month - 1)) mod 12",
                        "annual_index": annual_index,
                        "month": month,
                        "target_index": monthly_cont_index,
                        "result_sign": monthly_sign_cont.value
                    },
                    "saltatory": {
                        "formula": "(asc_index + total_months) mod 12",
                        "asc_index": asc_sign_idx,
                        "total_months": total_months or 0,
                        "target_index": monthly_salt_index,
                        "result_sign": monthly_sign_salt.value
                    }
                },
                "daily_profection": {
                    "formula": "steps = floor((day - 1) / (7/3)); sign = (monthly_index + steps) mod 12",
                    "day": day,
                    "rate_days_per_sign": daily_rate,
                    "steps": daily_steps,
                    "monthly_index": monthly_cont_index,
                    "target_index": daily_index,
                    "result_sign": daily_sign.value
                },
                "epitasis": {
                    "formula": "daily_sign == transiting_lord_of_year_sign",
                    "transiting_loy_sign": loy_trans_sign.value if loy_trans_sign else None,
                    "source": loy_trans_source,
                    "matching_days": epitasis_days
                }
            }
        }
        
        # 8. Zodiacal Releasing (Fate Timeline)
        spirit_lon = report["lots"].get("Spirit")
        fortune_lon = report["lots"].get("Fortune")
        
        # Use provided birth_date or fallback to symbolic
        start_dt = birth_date if birth_date else datetime(2000, 1, 1)
        
        if spirit_lon is not None:
            spirit_sign = list(Sign)[int(spirit_lon / 30) % 12]
            report["fate_timeline_spirit"] = calculate_zr_lifetime_map(spirit_sign, start_dt)
            
            # Also calculate current active periods for quick reference
            now_dt = analysis_date if analysis_date else datetime.now()
            report["zodiacal_releasing"] = calculate_zr_periods(spirit_sign, start_dt, now_dt)
            
        if fortune_lon is not None:
            fortune_sign = list(Sign)[int(fortune_lon / 30) % 12]
            report["fate_timeline_fortune"] = calculate_zr_lifetime_map(fortune_sign, start_dt)

        
    return report

def generate_daily_oracle(natal_chart: Chart, report: Dict, trans_jd: float, age: Optional[int], month: int, day: int) -> Dict:
    """
    Synthesizes a daily reading using Profections (Symbolic) and Transits (Physical).
    """
    if age is None:
        return {"summary": "Cast a Nativity with Age to receive the Oracle.", "details": []}

    asc_sign_idx = int(natal_chart.ascendant / 30) % 12
    asc_sign = list(Sign)[asc_sign_idx]
    
    sect = Sect.DAY if natal_chart.sun_altitude > 0 else Sect.NIGHT

    # Rulers (with explicit indices for trace)
    signs = list(Sign)
    annual_index = (asc_sign_idx + age) % 12
    ann_sign = signs[annual_index]
    loy_name = get_lord_of_year(ann_sign)
    
    monthly_index = (annual_index + (month - 1)) % 12
    mon_sign = signs[monthly_index]
    mon_lord = get_lord_of_year(mon_sign)
    
    daily_rate = 7 / 3
    daily_steps = int((day - 1) / daily_rate)
    daily_index = (monthly_index + daily_steps) % 12
    day_sign = signs[daily_index]
    day_lord_name = get_lord_of_year(day_sign)
    
    # Find conditions of these Lords in the NATAL chart (the "Promise")
    natal_day_lord = next((p for p in natal_chart.planets if p.name == day_lord_name), None)
    
    # Current Moon (Transit)
    try:
        m_res = swe.calc_ut(trans_jd, swe.MOON, swe.FLG_SWIEPH)[0]
    except swe.Error:
        try:
            m_res = swe.calc_ut(trans_jd, swe.MOON, swe.FLG_MOSEPH)[0]
        except swe.Error:
             # Moshier fallback failed. Use approximate position (0.0).
             m_res = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    trans_moon_lon = m_res[0]
    trans_moon_sign = list(Sign)[int(trans_moon_lon / 30) % 12]
    
    # Check for Epitasis (Secret Key)
    # Is the Daily sign the sign where the LOY currently transits?
    p_id = getattr(swe, loy_name.value.upper(), 0)
    try:
        loy_trans_res = swe.calc_ut(trans_jd, p_id, swe.FLG_SWIEPH)[0]
    except swe.Error:
        try:
            loy_trans_res = swe.calc_ut(trans_jd, p_id, swe.FLG_MOSEPH)[0]
        except:
            loy_trans_res = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    
    loy_trans_lon = loy_trans_res[0]
    loy_trans_sign = list(Sign)[int(loy_trans_lon / 30) % 12]
    
    is_epitasis = (day_sign == loy_trans_sign)
    
    # Compose Oracle
    forecast = {
        "title": f"ORACLE OF THE {day_sign.value.upper()} DOMAIN",
        "day_lord": day_lord_name.value,
        "mood": "Neutral",
        "summary": "",
        "details": [],
        "secret_key": is_epitasis,
        "calculation_steps": {
            "annual_profection": {
                "formula": "(asc_index + age) mod 12",
                "asc_sign": asc_sign.value,
                "asc_index": asc_sign_idx,
                "age": age,
                "target_index": annual_index,
                "result_sign": ann_sign.value
            },
            "lord_of_year": {
                "formula": "domicile(annual_sign)",
                "annual_sign": ann_sign.value,
                "lord_of_year": loy_name.value
            },
            "monthly_profection": {
                "formula": "(annual_index + (month - 1)) mod 12",
                "annual_index": annual_index,
                "month": month,
                "target_index": monthly_index,
                "result_sign": mon_sign.value
            },
            "daily_profection": {
                "formula": "steps = floor((day - 1) / (7/3)); sign = (monthly_index + steps) mod 12",
                "day": day,
                "rate_days_per_sign": daily_rate,
                "steps": daily_steps,
                "monthly_index": monthly_index,
                "target_index": daily_index,
                "result_sign": day_sign.value
            },
            "epitasis": {
                "formula": "daily_sign == transiting_lord_of_year_sign",
                "transiting_loy_sign": loy_trans_sign.value,
                "transiting_loy_longitude": loy_trans_lon,
                "matching": is_epitasis
            }
        }
    }
    
    # 1. Determine Mood based on Day Lord's Natal Strength
    if natal_day_lord:
        dignity = DignityCalculator.calculate_planet_dignity(natal_day_lord.name, natal_day_lord.longitude, sect)
        score = dignity["total_score"]
        if score >= 4: forecast["mood"] = "EXALTED"
        elif score <= -3: forecast["mood"] = "LABORIOUS"
        elif score < 0: forecast["mood"] = "WEAK"
        else: forecast["mood"] = "STABLE"
    
    # 2. Daily Summary
    summary_text = f"Today, the chronocrator of your life shifts into the domain of {day_sign.value}. "
    summary_text += f"{day_lord_name.value}, who holds the keys to this domain in your nativity, is currently {forecast['mood'].lower()}."
    
    if is_epitasis:
        summary_text += " WARNING: The Secret Key (Epitasis) active. The Lord of the Year has entered the Daily Domain. Events today carry the weight of your entire year's promise."
    
    forecast["summary"] = summary_text
    forecast["tradition_note"] = (
        "This oracle is derived using pre-1700s symbolic 'Profection' techniques and physical 'Transit' analysis. "
        "It provides a lens for psychological and situational reflection based on historical tradition, "
        "not a literal or deterministic prediction of future events."
    )
    
    # 3. Moon's Message
    moon_msg = f"The Lunar Mirror is in {trans_moon_sign.value}. "
    if trans_moon_sign == day_sign:
        moon_msg += "The physical Moon matches your symbolic daily focus. High emotional clarity and manifestation potential."
    elif abs(list(Sign).index(trans_moon_sign) - list(Sign).index(day_sign)) == 6:
        moon_msg += "The Moon opposes your daily direction. Expect tension between your needs and the day's demands."
    
    forecast["details"].append(moon_msg)
    
    # 4. Planetary Years Context
    major_firdaria = calculate_firdaria(report["summary"]["sect"], datetime.now(), datetime.now()) # Dummy usage just to show sub
    # Actually logic.py already calculates firdaria context in real scenarios if integrated. 
    # For now, let's just use what's available.
    
    return forecast
