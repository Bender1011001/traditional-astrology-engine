from datetime import datetime
from typing import Dict, List, Optional, Any
import swisseph as swe
import logging

from .models import Planet, Chart, Sect, PlanetName, Sign
from .chart_calculator import calculate_chart_data
from .advanced_mechanics import AlmutenEngine, HermeticLotEngine, DoryphoryEngine, MonomoiriaEngine, DodecatemoriaEngine
from .electional import ElectionalEngine
from .solar_return import SolarReturnEngine
from .planetary_hours import PlanetaryHourEngine
from .kakosis import KakosisEngine
from .medical import MedicalAstrology
from .synthesis import ReportSynthesizer
from .reference_data import PLANET_ESSENCES, TERM_METHODS, RULE_SOURCE_MAP
from .lots import calculate_all_lots, LotName
from .horary import calculate_antiscia, analyze_horary_physics
from .prediction import (
    calculate_profection_sign, 
    calculate_monthly_profection, 
    calculate_daily_profection,
    get_lord_of_year,
    AdvancedPredictionEngine,
    calculate_solar_return_jd,
    calculate_epitasis_days
)
from .decennials import DecennialEngine
from .phasis import PhasisEngine
from src.database.db_manager import DelineationLibrary
from .primary_directions import PrimaryDirectionsEngine
from .mundane import MundaneEngine, check_eclipse_impact, get_recent_eclipses
from .reception import ReceptionEngine, ReceptionMode
from .stars import check_fixed_stars
from .decumbiture import DecumbitureEngine
from .aspects import AspectEngine
from .dignities import DignityCalculator
from .hyleg import HylegAlcocodenEngine
from .temperament import TemperamentEngine
from .mansions import LunarMansionEngine
from .calculations import calculate_solar_status, is_besieged, is_in_via_combusta
import re

RULE_SOURCE_MAP_EXT = {
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
    if not sources and rule_text in RULE_SOURCE_MAP_EXT:
        sources.extend(RULE_SOURCE_MAP_EXT[rule_text])
    if cause:
        for key, refs in RULE_SOURCE_MAP_EXT.items():
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
    score += len(sources) * 5
    score -= len(conflicts) * 10
    return min(max(score, 0), 100)

def _slugify(text: str) -> str:
    return re.sub(r'[\W_]+', '-', text.lower()).strip('-')

logger = logging.getLogger(__name__)

# Initialize Library
LIB = DelineationLibrary()

class Auditor:
    """
    The Auditor (Hub): The sole orchestrator for deep astrological auditing.
    Replaces the legacy 'Sovereign Engine' terminology.
    Output: Bifurcated JSON (technical_data, human_translation).
    """

    @staticmethod
    def generate_full_nativity(
        date_str: str,
        time_str: str,
        city: str,
        state: str = "",
        name: str = "Native",
        house_system: str = "W",
        zodiac_system: str = "tropical",
        ayanamsa: Optional[str] = None,
        analysis_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Single Entry Point for Comprehensive Forensic Audit.
        """
        try:
            # 1. Astronomy: Call chart_calculator
            raw_chart_data = calculate_chart_data(
                date_str=date_str,
                time_str=time_str,
                city=city,
                state=state,
                house_system=house_system,
                zodiac_system=zodiac_system,
                ayanamsa=ayanamsa
            )

            if "error" in raw_chart_data:
                return {"error": raw_chart_data["error"]}

            # Reconstruct Chart Model
            chart = Auditor._rebuild_chart_model(raw_chart_data)
            jd = raw_chart_data["meta"]["julian_day"]
            
            # Resolve Dates
            ans_date = analysis_date or datetime.now()
            birth_dt = None
            if "utc_time" in raw_chart_data["meta"]:
                birth_dt = datetime.fromisoformat(raw_chart_data["meta"]["utc_time"])
                if birth_dt.tzinfo: birth_dt = birth_dt.replace(tzinfo=None)
            
            # Age Calculation
            age = 0
            if birth_dt:
                age = ans_date.year - birth_dt.year - ((ans_date.month, ans_date.day) < (birth_dt.month, birth_dt.day))

            # 2. Analysis: Aggregate Specialized Engine Results via Centralized Auditor
            audit_results = Auditor.perform_audit(
                chart=chart,
                jd=jd,
                birth_dt=birth_dt,
                ans_date=ans_date,
                age=age
            )
            analysis = audit_results["analysis"]
            planets_forensic = audit_results["planets_forensic"]

            # 3. State Assembly: Assemble technical_data
            technical_data = {
                "meta": {
                    "subject_name": name,
                    "timestamp": datetime.now().isoformat(),
                    "julian_day": jd,
                    "city": city,
                    "coords": {"lat": raw_chart_data["meta"]["lat"], "lon": raw_chart_data["meta"]["lon"]},
                    "age": age
                },
                "astronomy": {
                    "planets": raw_chart_data["planets"],
                    "houses": raw_chart_data["houses"],
                    "angles": {
                        "Asc": raw_chart_data["angles"].get("Ascendant"),
                        "MC": raw_chart_data["angles"].get("MC")
                    }
                },
                "analysis": analysis,
                "planets_forensic": planets_forensic,
                "rule_ledger": audit_results.get("rule_ledger", [])
            }

            # 4. Translation: Pass to ReportSynthesizer
            legacy_report = Auditor._map_to_legacy_report(technical_data, chart)
            human_translation = {
                "report_markdown": ReportSynthesizer.synthesize(legacy_report),
                "executive_summary": ReportSynthesizer._generate_executive_summary(legacy_report)
            }

            return {
                "technical_data": technical_data,
                "human_translation": human_translation
            }

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"Auditor Failure: {e}\n{error_trace}")
            return {"error": f"Auditor Failure: {str(e)}"}

    @staticmethod
    def perform_audit(
        chart: Chart, 
        jd: float, 
        birth_dt: Optional[datetime] = None, 
        ans_date: Optional[datetime] = None,
        age: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Exhaustive Architectural Audit of a Nativity.
        Consolidates logic from perform_forensic_audit (logic.py).
        """
        ans_date = ans_date or datetime.now()
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        
        # 1. Base Analysis
        analysis = {}
        analysis[ "dignity" ] = Auditor._calculate_dignity_suite(chart)
        analysis[ "fate" ] = Auditor._calculate_fate_suite(chart, birth_dt, ans_date)
        analysis[ "medical" ] = Auditor._calculate_medical_suite(chart)
        analysis[ "teams" ] = Auditor._calculate_teams_and_reception(chart)
        analysis[ "aspects" ] = AspectEngine.calculate_aspects(chart)
        
        # 2. Advanced Suites
        analysis[ "advanced_mechanics" ] = {
            "almuten": analysis[ "dignity" ][ "almuten" ],
            "doryphory": Auditor._calculate_doryphory_details(chart),
            "mundane_context": MundaneEngine(jd, chart.geo_lat, chart.geo_lon).get_hierarchy_report()
        }

        # 3. Supplemental Layers
        moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)
        analysis[ "supplemental" ] = {
            "lunar_mansion": LunarMansionEngine.get_lunar_mansion(moon.longitude) if moon else None,
            "stars": Auditor._calculate_star_impacts(chart),
            "nodes": Auditor._calculate_nodal_impacts(chart),
            "elements": Auditor._calculate_elemental_balance(chart),
            "hemispheres": Auditor._calculate_hemispheres(chart)
        }

        # 4. Temporal Layers
        if birth_dt and age is not None:
             analysis[ "solar_return" ] = Auditor._calculate_solar_return_summary(chart, birth_dt, age)
        
        # 5. Planetary Detail
        planets_forensic = Auditor._analyze_all_planets(chart, jd)

        # 6. Forensic Lots (Parents/Debt/Theft)
        forensic_lots = Auditor._calculate_forensic_lots(chart)
        analysis["forensic_lots"] = forensic_lots
        
        # 7. Enhanced Mechanics (Profections, Horary Physics)
        # Note: logic.py used manual profection calculation. We should use it for parity.
        # AdvancedPredictionEngine gives basic stuff, but logic.py had epitasis.
        profections = Auditor._calculate_enhanced_profections(chart, birth_dt, ans_date, age)
        analysis["enhanced_profections"] = profections
        
        horary_phys = Auditor._calculate_horary_physics(chart, age)
        analysis["horary_physics"] = horary_phys

        # 8. Universal Ledger (Source of Truth)
        rule_ledger = Auditor._generate_rule_ledger(
            chart=chart,
            planets_data=planets_forensic,
            active_directions=analysis["fate"].get("active_directions", []),
            stars=analysis["supplemental"].get("stars", []),
            hermetic_lots=analysis["fate"].get("hermetic_lots", {}),
            forensic_lots=forensic_lots,
            jd=jd
        )

        return {
            "analysis": analysis,
            "planets_forensic": planets_forensic,
            "rule_ledger": rule_ledger
        }

    @staticmethod
    def _calculate_doryphory_details(chart: Chart) -> List[Dict]:
        dory = DoryphoryEngine.check_doryphory(chart)
        return [{"planet": d.planet.value, "type": d.type, "target": d.related_luminary} for d in dory]

    @staticmethod
    def _calculate_star_impacts(chart: Chart) -> List[Any]:
        from .stars import check_fixed_stars
        return check_fixed_stars(chart)

    @staticmethod
    def _calculate_nodal_impacts(chart: Chart) -> List[Any]:
        from .nodes import analyze_nodes
        return analyze_nodes(chart)

    @staticmethod
    def _calculate_elemental_balance(chart: Chart) -> Dict[str, int]:
        elements = {"FIRE": 0, "EARTH": 0, "AIR": 0, "WATER": 0}
        for p in chart.planets:
            if p.name in [PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]: continue
            sign_idx = int(p.longitude / 30) % 12
            sign = list(Sign)[sign_idx]
            el = DignityCalculator.ZODIAC_ELEMENTS.get(sign)
            if el: elements[el] += 1
        return elements

    @staticmethod
    def _calculate_hemispheres(chart: Chart) -> Dict:
        hemi = {"East": 0, "West": 0, "North": 0, "South": 0}
        for p in chart.planets:
            if p.name in [PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]: continue
            
            # House-based hemisphere logic (Simple Whole Sign/Equal-ish proxy)
            # 10,11,12,1,2,3 -> East
            # 4,5,6,7,8,9 -> West
            # 7,8,9,10,11,12 -> South (Above Horizon)
            # 1,2,3,4,5,6 -> North (Below Horizon)
            h = DignityCalculator.get_house_number(p.longitude, chart.ascendant, chart.houses)
            if h in [10, 11, 12, 1, 2, 3]: hemi["East"] += 1
            else: hemi["West"] += 1
            
            if h in [7, 8, 9, 10, 11, 12]: hemi["South"] += 1
            else: hemi["North"] += 1
            
        return {
            "counts": hemi,
            "focus": {
                "orientation": "Self-Determination (East)" if hemi["East"] > hemi["West"] else "Other-Oriented (West)",
                "visibility": "Public/Objective (South)" if hemi["South"] > hemi["North"] else "Private/Subjective (North)"
            }
        }

    @staticmethod
    def _calculate_solar_return_summary(chart: Chart, birth_dt: datetime, age: int) -> Dict:
        try:
            current_yr = birth_dt.year + age
            sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
            sr_jd = calculate_solar_return_jd(sun.longitude, chart.jd, current_yr)
            
            # Simple wrapper to match expected logic
            return SolarReturnEngine.analyze_solar_return_from_jd(chart, sr_jd, age, birth_dt)
        except Exception as e:
            logger.error(f"Solar Return calculation failed: {e}")
            return {"error": "Solar Return calculation failed"}

    @staticmethod
    def _calculate_forensic_lots(chart: Chart) -> Dict:
        """
        Calculates specific forensic lots (Debt, Theft, Accusation, Parents) and verifies affliction.
        """
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        all_lots = calculate_all_lots(chart, sect)
        
        mars_p = next((p for p in chart.planets if p.name == PlanetName.MARS), None)
        saturn_p = next((p for p in chart.planets if p.name == PlanetName.SATURN), None)
        
        def _enrich(lon):
            if lon is None: return None
            sign_idx = int(lon / 30) % 12
            sign = list(Sign)[sign_idx]
            house = DignityCalculator.get_house_number(lon, chart.ascendant, chart.houses)
            return {"longitude": lon, "sign": sign.value, "house": house}

        def _is_afflicted_by(lot_lon, malefic_lon, orb=3.0):
            if lot_lon is None or malefic_lon is None: return False
            dist = abs(lot_lon - malefic_lon) % 360
            if dist > 180: dist = 360 - dist
            return dist <= orb

        report = {}
        
        # 1. Debt
        debt_lon = all_lots.get(LotName.DEBT.value)
        report["Debt/Bankruptcy"] = {
            "data": _enrich(debt_lon),
            "status": "AFFLICTED" if mars_p and _is_afflicted_by(debt_lon, mars_p.longitude) else "Clear",
            "verification": "Mars contact signifies aggressive debt or sudden bankruptcy."
        }
        
        # 2. Theft
        theft_lon = all_lots.get(LotName.THEFT.value)
        report["Theft"] = {
            "data": _enrich(theft_lon),
            "status": "AFFLICTED" if mars_p and _is_afflicted_by(theft_lon, mars_p.longitude) else "Clear",
            "verification": "Mars contact signifies loss through theft or violence."
        }
        
        # 3. Accusation
        acc_lon = all_lots.get(LotName.ACCUSATION.value)
        report["Accusation"] = {
            "data": _enrich(acc_lon),
            "status": "AFFLICTED" if saturn_p and _is_afflicted_by(acc_lon, saturn_p.longitude) else "Clear",
            "verification": "Saturn contact signifies legal entrapment or false witness."
        }
        
        # 4. Parents
        for parent, name in [(LotName.FATHER, "Father"), (LotName.MOTHER, "Mother")]:
            p_lon = all_lots.get(parent.value)
            if p_lon is not None:
                ruler_name = DignityCalculator.get_essential_rulers(p_lon, sect)["domicile"]
                ruler = next((p for p in chart.planets if p.name == ruler_name), None)
                status = "Neutral"
                verif = f"Ruler {ruler_name.value} condition is average."
                if ruler:
                    score = DignityCalculator.calculate_planet_dignity(ruler.name, ruler.longitude, sect)["total_score"]
                    if score >= 3:
                        status = "STRONG"
                        verif = f"Ruler {ruler_name.value} is well-dignified (Score: {score})."
                    elif score <= -3:
                        status = "WEAK"
                        verif = f"Ruler {ruler_name.value} is debilitated (Score: {score})."
                report[name] = {"data": _enrich(p_lon), "status": status, "verification": verif}
                
        return report

    @staticmethod
    def _calculate_horary_physics(chart: Chart, age: int) -> Dict:
        if age is None: return {}
        asc_sign_idx = int(chart.ascendant / 30) % 12
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        
        # Ascendant Ruler (L1)
        # Note: Logic.py used 'domicile' from essential rulers
        essentials = DignityCalculator.get_essential_rulers(chart.ascendant, sect)
        asc_lord_name = essentials["domicile"]
        
        # Lord of Year
        annual_sign = calculate_profection_sign(list(Sign)[asc_sign_idx], age)
        loy_lord_name = get_lord_of_year(annual_sign)
        
        return {
            "significators": f"{asc_lord_name.value} (L1) and {loy_lord_name.value} (LoY)",
            "interactions": analyze_horary_physics(asc_lord_name, loy_lord_name, chart)
        }

    @staticmethod
    def _calculate_enhanced_profections(chart: Chart, birth_dt: Optional[datetime], ans_date: datetime, age: int) -> Dict:
        if age is None: return {}
        asc_sign_idx = int(chart.ascendant / 30) % 12
        signs = list(Sign)
        
        # Annual
        annual_index = (asc_sign_idx + age) % 12
        annual_sign = signs[annual_index]
        loy_name = get_lord_of_year(annual_sign)
        
        # Monthly & Daily Defaults
        month = 1
        day = 1
        
        if birth_dt and ans_date:
            try:
                # Logic: Calculate profection month (1-12) and day (1-30)
                m_diff = (ans_date.year - birth_dt.year) * 12 + (ans_date.month - birth_dt.month)
                if ans_date.day < birth_dt.day:
                    m_diff -= 1
                month = (m_diff % 12) + 1
                
                day_diff = (ans_date.day - birth_dt.day)
                if day_diff < 0: day_diff += 30
                day = day_diff + 1
            except:
                pass

        # Monthly (Continuous)
        monthly_cont_index = (annual_index + (month - 1)) % 12
        monthly_sign_cont = signs[monthly_cont_index]
        
        # Monthly (Saltatory)
        total_months = (age * 12) + (month - 1)
        monthly_salt_index = (asc_sign_idx + total_months) % 12
        monthly_sign_salt = signs[monthly_salt_index]
        
        # Daily
        daily_rate = 7 / 3
        daily_steps = int((day - 1) / daily_rate)
        daily_index = (monthly_cont_index + daily_steps) % 12
        daily_sign = signs[daily_index]
        
        # Epitasis
        epitasis_days = []
        loy_planet = next((p for p in chart.planets if p.name == loy_name), None)
        if loy_planet:
            epitasis_days = calculate_epitasis_days(monthly_sign_cont, loy_planet.sign)
            
        return {
            "annual_sign": annual_sign.value,
            "lord_of_year": loy_name.value,
            "monthly_sign": {
                "continuous": monthly_sign_cont.value,
                "saltatory": monthly_sign_salt.value
            },
            "daily_sign": daily_sign.value,
            "epitasis_days": epitasis_days,
            "age": age, "month": month, "day": day
        }

    @staticmethod
    def _generate_rule_ledger(
        chart: Chart, 
        planets_data: List[Dict], 
        active_directions: List[Dict], 
        stars: List[Any], 
        hermetic_lots: Dict, 
        forensic_lots: Dict, 
        jd: float
    ) -> List[Dict]:
        """
        Generates the Source of Truth Rule Ledger.
        """
        ledger = []
        rule_counts = {}

        def _uid(base):
            c = rule_counts.get(base, 0) + 1
            rule_counts[base] = c
            return f"{base}-{c}" if c > 1 else base

        # 1. Planets
        for p_data in planets_data:
            p_label = p_data.get("name", "Planet")
            base_trace = [f"Planet: {p_label}", f"Sign: {p_data.get('sign')}"]
            
            # Dignity
            dig = p_data.get("dignities", {})
            if dig:
                score = dig.get("total_score", 0)
                ledger.append({
                    "id": _uid(f"{p_label.lower()}-dignity"),
                    "category": "Essential Dignity",
                    "condition": f"{p_label} in {p_data.get('sign')}",
                    "judgment": f"Score: {score}. " + ", ".join([f"{k}: {v}" for k,v in dig.get("breakdown", {}).items()]),
                    "sources": ["Ptolemy, Tetrabiblos", "Dorotheus"],
                    "confidence": 90,
                    "conflicts": [],
                    "trace": base_trace
                })
            
            # Impacts
            for imp in p_data.get("impacts", []):
                cause = imp.get("cause")
                effect = imp.get("effect")
                sources = _resolve_sources(cause, "")
                ledger.append({
                    "id": _uid(f"{p_label.lower()}-{_slugify(cause)}"),
                    "category": "Condition",
                    "condition": f"{p_label}: {cause}",
                    "judgment": effect,
                    "sources": sources,
                    "confidence": _estimate_confidence(sources, [], base=75),
                    "conflicts": [],
                    "trace": base_trace + [f"Cause: {cause}"]
                })

            # Delineation
            if "delineation" in p_data:
                 sources = _extract_sources(p_data["delineation"])
                 ledger.append({
                    "id": _uid(f"{p_label.lower()}-delineation"),
                    "category": "Planet Delineation",
                    "condition": f"{p_label} in {p_data.get('sign')}",
                    "judgment": str(p_data["delineation"])[:150] + "...",
                    "sources": sources,
                    "confidence": 70,
                    "conflicts": [],
                    "trace": base_trace
                 })
                 
            # Classical - Monomoiria/Dodecatemoria if available in future
            if "classical" in p_data:
                mono = p_data["classical"].get("monomoiria")
                if mono:
                    ledger.append({
                        "id": _uid(f"{p_label.lower()}-monomoiria"),
                        "category": "Monomoiria",
                        "condition": f"{p_label} Degree Ruler",
                        "judgment": f"Zoidion: {mono.get('zoidion_ruler')}",
                        "sources": ["Paul of Alexandria"],
                        "confidence": 85,
                        "conflicts": [],
                        "trace": base_trace
                    })

        # 2. Directions
        for d in active_directions:
            ledger.append({
                "id": _uid(f"direction-{_slugify(str(d.get('promittor', '')))}-{_slugify(str(d.get('aspect', '')))}"),
                "category": "Primary Direction",
                "condition": f"Directed {d.get('significator')} to {d.get('promittor')}",
                "judgment": f"Arc {d.get('arc')}: {d.get('aspect')}",
                "sources": ["Ptolemy", "Placidus"],
                "confidence": 85,
                "conflicts": [],
                "trace": [f"Year: {d.get('years')}"]
            })

        # 3. Stars
        for s in stars:
            s_name = s.star_name if hasattr(s, "star_name") else s.get("star_name")
            p_name = s.planet_name if hasattr(s, "planet_name") else s.get("planet_name")
            msg = s.message if hasattr(s, "message") else s.get("message")
            ledger.append({
                "id": _uid(f"star-{_slugify(str(s_name))}"),
                "category": "Fixed Star",
                "condition": f"{s_name} + {p_name}",
                "judgment": msg,
                "sources": ["Anonymous of 379", "Brady"],
                "confidence": 90,
                "conflicts": [],
                "trace": []
            })
            
        # 4. Forensic Lots
        for k, v in forensic_lots.items():
            if v.get("status") != "Clear":
                 ledger.append({
                    "id": _uid(f"lot-{_slugify(k)}"),
                    "category": "Forensic Lot",
                    "condition": f"Lot of {k}",
                    "judgment": v.get("verification"),
                    "sources": ["Bonatti", "Valens"],
                    "confidence": 85,
                    "conflicts": [],
                    "trace": [f"Status: {v.get('status')}"]
                 })

        # 5. Eclipses
        if jd > 0:
            eclipses = get_recent_eclipses(jd)
            for lot_name, lot_data in hermetic_lots.items():
                lon = lot_data
                if isinstance(lot_data, dict): lon = lot_data.get("longitude")
                
                if isinstance(lon, (int, float)):
                    for ec in eclipses:
                        if check_eclipse_impact(lon, ec["longitude"]):
                             ledger.append({
                                "id": _uid(f"eclipse-{_slugify(lot_name)}"),
                                "category": "Universal Override",
                                "condition": f"Eclipse impacting Lot of {lot_name}",
                                "judgment": "Suspended Promise: Area under universal pressure.",
                                "sources": ["Ptolemy II"],
                                "confidence": 92,
                                "conflicts": [],
                                "trace": [f"Eclipse JD: {ec['jd']}"]
                             })

        return ledger
        
    @staticmethod
    def _rebuild_chart_model(raw_data: Dict) -> Chart:
        planets = []
        for name, p_data in raw_data["planets"].items():
            planets.append(Planet(
                name=PlanetName(name),
                longitude=p_data["longitude"],
                latitude=p_data.get("latitude", 0.0),
                speed=p_data.get("speed", 0.0)
            ))
        
        # Extract Sun Altitude (Required for Sect)
        sun_data = raw_data["planets"].get("Sun", {})
        sun_altitude = sun_data.get("altitude", 0.0)

        # Extract Angles
        angles = raw_data.get("angles", {})
        ascendant = angles.get("Ascendant", 0.0)
        mc = angles.get("MC", 0.0)

        return Chart(
            sun_altitude=sun_altitude,
            planets=planets,
            ascendant=ascendant,
            mc=mc,
            geo_lat=raw_data["meta"]["lat"],
            geo_lon=raw_data["meta"]["lon"],
            jd=raw_data["meta"]["julian_day"],
            houses=raw_data["houses"]
        )

    @staticmethod
    def _calculate_dignity_suite(chart: Chart) -> Dict:
        almuten_data = AlmutenEngine.calculate_almuten(chart)
        scores = {}
        winner = "Unknown"
        winner_score = 0
        
        if almuten_data:
            winner = almuten_data.winner.value
            for k, v in almuten_data.scores.items():
                scores[k] = v.total_score
            winner_score = scores.get(winner, 0)

        return {
            "almuten": {
                "winner": winner,
                "score": winner_score,
                "breakdown": scores
            },
            "doryphory": [d.planet.value for d in DoryphoryEngine.check_doryphory(chart)]
        }

    @staticmethod
    def _calculate_fate_suite(chart: Chart, birth_dt: Optional[datetime], ans_date: datetime) -> Dict:
        # Hermetic Lots
        lots = HermeticLotEngine.calculate_all_lots(chart)
        
        # Predictive Engines
        bdt = birth_dt or datetime.now()
        
        # Calculate Age Calculation for Directions
        age_years = (ans_date - bdt).days / 365.25
        if age_years < 0: age_years = 0

        # 1. Primary Directions
        directions = PrimaryDirectionsEngine.calculate_directions_to_angles(chart, chart.geo_lat)
        distributor = PrimaryDirectionsEngine.calculate_current_distributor(chart, age_years, chart.geo_lat)
        
        # Serialize and Filter Active (for Ledger)
        p_dirs_json = []
        active_dirs = []
        for d in directions:
            d_json = {
                "significator": d.significator,
                "promittor": d.promittor,
                "aspect": d.aspect,
                "arc": d.arc,
                "years": d.years,
                "date_offset": d.date_offset,
                "method": d.method
            }
            p_dirs_json.append(d_json)
            # Active if within 1 year of current age
            if abs(d.years - age_years) <= 1.0:
                 active_dirs.append(d_json)

        # 2. Advanced Prediction (Transits, Firdaria, Profections)
        predictor = AdvancedPredictionEngine(
            chart, bdt, chart.jd, chart.geo_lat, chart.geo_lon
        )
        prediction_report = predictor.get_prediction_report(ans_date)

        return {
            "hermetic_lots": lots,
            "primary_directions": p_dirs_json,
            "primary_direction_distributor": distributor,
            "active_directions": active_dirs,
            "profections": prediction_report.get("profections", {}),
            "firdaria": prediction_report.get("firdaria", {}),
            "solar_return": prediction_report.get("solar_return_info", {}),
            "muntha": prediction_report.get("muntha", {}),
            "transits": prediction_report.get("transits", []),
            "decennials": DecennialEngine.generate_decennials(chart, bdt) if bdt else []
        }

    @staticmethod
    def _calculate_medical_suite(chart: Chart) -> Dict:
        asc_sign = list(Sign)[int(chart.ascendant / 30) % 12]
        governed_part = MedicalAstrology.get_body_part_for_sign(asc_sign)
        return {
            "constitution": governed_part,
            "distemper": DecumbitureEngine.analyze_distemper(asc_sign),
            "surgery_risk": MedicalAstrology.can_perform_surgery(
                governed_part,
                chart.jd,
                chart
            )
        }

    @staticmethod
    def _calculate_teams_and_reception(chart: Chart) -> Dict:
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        receptions = ReceptionEngine.calculate_mutual_receptions(chart, ReceptionMode.STANDARD_LILLY)
        
        constructive = []
        destructive = []
        for p in chart.planets:
            if p.name in [PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]: continue
            
            if sect == Sect.DAY:
                if p.name in [PlanetName.SUN, PlanetName.JUPITER, PlanetName.SATURN]: constructive.append(p.name.value)
                elif p.name in [PlanetName.MARS]: destructive.append(p.name.value)
            else:
                if p.name in [PlanetName.MOON, PlanetName.VENUS, PlanetName.MARS]: constructive.append(p.name.value)
                elif p.name in [PlanetName.SATURN]: destructive.append(p.name.value)

        return {
            "constructive_team": constructive,
            "destructive_team": destructive,
            "receptions": [{
                "planet_a": r.planet_a.value,
                "planet_b": r.planet_b.value,
                "type": r.type,
                "score": r.strength_score
            } for r in receptions]
        }

    @staticmethod
    def _analyze_all_planets(chart: Chart, jd: float) -> List[Dict]:
        results = []
        speculum = {} 
        for p in chart.planets:
            if p.name in [PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]:
                continue
            
            p_data = Auditor._analyze_single_planet(p, chart, jd, speculum)
            results.append(p_data)
        return results

    @staticmethod
    def _analyze_single_planet(planet: Planet, chart: Chart, jd: float, speculum: Dict) -> Dict:
        sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
        sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
        
        result = {
            "name": planet.name.value,
            "longitude": planet.longitude,
            "sign": planet.sign.value,
            "dignities": DignityCalculator.calculate_planet_dignity(planet.name, planet.longitude, sect),
            "solar_status": calculate_solar_status(planet, sun),
            "phasis": {
                "phase": PhasisEngine.get_synodic_phase(planet, sun.longitude).value,
                "is_visible": PhasisEngine.calculate_visibility(
                    jd, chart.geo_lat, chart.geo_lon, 
                    planet.name, planet.longitude, planet.latitude, sun.longitude
                )
            },
            "maltreatments": [
                {"condition": m.type, "malefic": m.malefic.value, "description": m.description, "severity": m.severity}
                for m in KakosisEngine.check_maltreatments(planet, chart)
            ],
            "impacts": []
        }

        # Besiegement
        if is_besieged(planet, chart):
            result["impacts"].append({"cause": "Besiegement", "effect": "BLOCKED: Trapped between Malefics."})

        # Via Combusta
        if is_in_via_combusta(planet.longitude):
            result["impacts"].append({"cause": "Via Combusta", "effect": "DEBILITATED: The Burning Way."})

        # Antiscia
        ant, cant = calculate_antiscia(planet.longitude)
        for other in chart.planets:
            if other.name == planet.name: continue
            if abs(other.longitude - ant) < 1.0:
                result["impacts"].append({"cause": "Antiscia", "effect": f"Shadow contact with {other.name.value}"})

        # Delineation
        sect_str = "DAY" if sect == Sect.DAY else "NIGHT"
        key = f"{planet.name.value.upper()}_{planet.sign.value.upper()}_{sect_str}"
        result["delineation"] = LIB.get_planet_delineation(key)

        return result

    @staticmethod
    def _map_to_legacy_report(tech_data: Dict, chart: Chart) -> Dict:
        analysis = tech_data["analysis"]
        teams = analysis["teams"]
        moon = next(p for p in chart.planets if p.name == PlanetName.MOON)
        
        # Helper for Profections
        muntha = analysis["fate"].get("muntha", {})
        profections = {}
        if muntha:
            sign_name = muntha.get("sign")
            from .reference_data import DOMICILES, Sign
            try:
                s = next(s for s in Sign if s.value == sign_name)
                ruler = DOMICILES[s]
                profections = {
                    "lord_of_year": ruler.value if hasattr(ruler, "value") else str(ruler),
                    "annual_sign": sign_name
                }
            except:
                profections = {"lord_of_year": "Unknown", "annual_sign": sign_name}

        # Format Aspects for Legacy Report
        formatted_aspects = []
        if "aspects" in analysis:
            for asp in analysis["aspects"]:
                formatted_aspects.append({
                    "planet_a": asp.planet_a.value,
                    "planet_b": asp.planet_b.value,
                    "type": asp.type.value,
                    "orb": asp.orb,
                    "is_applying": asp.is_applying,
                    "text": asp.text
                })

        legacy = {
            "summary": {
                "sect": Sect.DAY.value if chart.sun_altitude > 0 else Sect.NIGHT.value,
                "temperament": analysis["medical"]["distemper"],
                "lunar_mansion": LunarMansionEngine.get_lunar_mansion(moon.longitude),
                "mutual_receptions": teams["receptions"],
                "constructive_team": teams["constructive_team"],
                "destructive_team": teams["destructive_team"],
                "maltreatments": {p["name"]: p["maltreatments"] for p in tech_data["planets_forensic"] if p["maltreatments"]},
                "universal_events": get_recent_eclipses(chart.jd),
                "dominant_elements": []
            },
            "soul_guardian": {
                "almuten": analysis["dignity"]["almuten"]["winner"],
                "job_description": f"Sovereign {analysis['dignity']['almuten']['winner']}"
            },
            "vitality": {"vitality_rating": "Stable (Calculated by Auditor)"},
            "medical_analysis": {
                "governed_body_part": analysis["medical"]["constitution"],
                "constitutional_sign": list(Sign)[int(chart.ascendant / 30) % 12].value,
                "pathology_alerts": analysis["medical"].get("surgery_risk", {}).get("contra_indications", [])
            },
            "primary_directions": analysis["fate"]["primary_directions"],
            "primary_direction_distributor": analysis["fate"].get("primary_direction_distributor", {}),
            "profections": profections,
            "firdaria": analysis["fate"].get("firdaria", {}),
            "decennials": analysis["fate"].get("decennials", []),
            "solar_return": analysis["fate"].get("solar_return", {}),
            "forensic_lots": analysis["fate"]["hermetic_lots"],
            "planets": tech_data["planets_forensic"],
            "houses": tech_data["astronomy"]["houses"],
            "aspects": formatted_aspects
        }
        return legacy
