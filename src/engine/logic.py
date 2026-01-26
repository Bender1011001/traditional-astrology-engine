
from typing import Optional, Dict, List
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
from .stars import check_fixed_stars
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
    
    # Labeling logic
    score = dignity["total_score"]
    if score >= 5: result["power_label"] = "Sovereign"
    elif score >= 2: result["power_label"] = "High Authority"
    elif score <= -4: result["power_label"] = "Vagabond/Corrupt"
    else: result["power_label"] = "Commoner/Average"
        
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
    asc_sign_idx = int(chart.ascendant / 30) % 12
    p_sign_idx = int(planet.longitude / 30) % 12
    house_num = ((p_sign_idx - asc_sign_idx) % 12) + 1
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

def perform_forensic_audit(chart: Chart, jd: float = 0.0, age: Optional[int] = None, month: int = 1, day: int = 1, birth_date: Optional[datetime] = None) -> Dict:
    sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
    
    sun = next((p for p in chart.planets if p.name == PlanetName.SUN), None)
    moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)
    
    # Elemental Balance
    elements = {"FIRE": 0, "EARTH": 0, "AIR": 0, "WATER": 0}
    for p in chart.planets:
        if p.name in [PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]: continue
        el = DignityCalculator.ZODIAC_ELEMENTS.get(p.sign)
        if el: elements[el] += 1

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
            "constructive_team": constructive_team,
            "destructive_team": destructive_team,
            "team_note": "Trust the energies/people of your Constructive Team; exercise caution with the Destructive Team.",
            "universal_events": [],
            "lunar_phase": calculate_lunar_phase(sun.longitude, moon.longitude)[0] if sun and moon else "Unknown",
            "lunar_phase_profile": calculate_lunar_phase(sun.longitude, moon.longitude)[1] if sun and moon else "Unknown",
            "jones_pattern": calculate_jones_pattern([p.longitude for p in chart.planets if p.name.value in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]]),
            "dominant_elements": sorted(elements.items(), key=lambda x: x[1], reverse=True)
        },
        "soul_guardian": generate_soul_guardian_reading(chart, jd) if jd > 0 else {},
        "planets": [],
        "lots": calculate_all_lots(chart, sect),
        "stars": check_fixed_stars(chart),
        "nodes": analyze_nodes(chart)
    }
    
    # 6. Daily Oracle (Traditional Synthesized Forecast)
    report["daily_oracle"] = generate_daily_oracle(chart, report, jd, age, month, day)

    if jd > 0:
        report["summary"]["universal_events"] = get_recent_eclipses(jd)
        report["summary"]["universal_causation_audit"] = check_universal_causation_dec2025(jd)
        
    for planet in chart.planets:
        planet_data = analyze_planet_forensic(planet, chart, jd)
        report["planets"].append(planet_data)

    # 7. Horary Physics (Synthesis of Significators)
    # We analyze physics between the Lord of the 1st and the Lord of the Year (if age provided)
    # Or Moon vs others.
    if age is not None:
        asc_sign_idx = int(chart.ascendant / 30) % 12
        asc_lord = DignityCalculator.DOMICILES[list(Sign)[asc_sign_idx]][0]
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
        
        annual_sign = calculate_profection_sign(asc_sign, age)
        loy_name = get_lord_of_year(annual_sign)
        
        # Monthly
        monthly_sign_cont = calculate_monthly_profection(annual_sign, month, method='Continuous')
        monthly_sign_salt = calculate_monthly_profection(annual_sign, month, method='Saltatory', natal_start_sign=asc_sign, age=age)
        
        # Daily
        daily_sign = calculate_daily_profection(monthly_sign_cont, day)
        
        # Epitasis (needs transiting LoY)
        # Find the LoY in the current chart (assuming 'chart' contains transits)
        loy_planet = next((p for p in chart.planets if p.name == loy_name), None)
        epitasis_days = []
        if loy_planet:
            epitasis_days = calculate_epitasis_days(monthly_sign_cont, loy_planet.sign)
            
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
            "epitasis_days": epitasis_days
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
            now_dt = datetime.now()
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
    
    # Rulers
    ann_sign = calculate_profection_sign(asc_sign, age)
    loy_name = get_lord_of_year(ann_sign)
    
    mon_sign = calculate_monthly_profection(ann_sign, month)
    mon_lord = get_lord_of_year(mon_sign)
    
    day_sign = calculate_daily_profection(mon_sign, float(day))
    day_lord_name = get_lord_of_year(day_sign)
    
    # Find conditions of these Lords in the NATAL chart (the "Promise")
    natal_day_lord = next((p for p in natal_chart.planets if p.name == day_lord_name), None)
    
    # Current Moon (Transit)
    m_res = swe.calc_ut(trans_jd, swe.MOON, swe.FLG_SWIEPH)[0]
    trans_moon_lon = m_res[0]
    trans_moon_sign = list(Sign)[int(trans_moon_lon / 30) % 12]
    
    # Check for Epitasis (Secret Key)
    # Is the Daily sign the sign where the LOY currently transits?
    loy_trans_res = swe.calc_ut(trans_jd, getattr(swe, loy_name.value.upper(), 0), swe.FLG_SWIEPH)[0]
    loy_trans_sign = list(Sign)[int(loy_trans_res[0] / 30) % 12]
    
    is_epitasis = (day_sign == loy_trans_sign)
    
    # Compose Oracle
    forecast = {
        "title": f"ORACLE OF THE {day_sign.value.upper()} DOMAIN",
        "day_lord": day_lord_name.value,
        "mood": "Neutral",
        "summary": "",
        "details": [],
        "secret_key": is_epitasis
    }
    
    # 1. Determine Mood based on Day Lord's Natal Strength
    if natal_day_lord:
        dignity = DignityCalculator.calculate_planet_dignity(natal_day_lord.name, natal_day_lord.longitude, report["summary"]["sect"])
        score = dignity["total_score"]
        if score >= 4: forecast["mood"] = "EXALTED"
        elif score <= -3: forecast["mood"] = "LABORIOUS"
        elif score < 0: forecast["mood"] = "WEAK"
        else: forecast["mood"] = "STABLE"
    
    # 2. Daily Summary
    summary_text = f"Today, the chronocrator of your life shifts into the domain of {day_sign.value}. "
    summary_text += f"{day_lord_name.value}, who holds the keys to this domain in your nativity, is currently {forecast['mood'].lower()}."
    
    if is_epitasis:
        summary_text += " WARNING: The Secret Key (Epitasis) is active. The Lord of the Year has entered the Daily Domain. Events today carry the weight of your entire year's promise."
    
    forecast["summary"] = summary_text
    
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
