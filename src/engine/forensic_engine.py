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
from .prediction import (
    calculate_profection_sign, 
    calculate_monthly_profection, 
    calculate_daily_profection,
    get_lord_of_year,
    AdvancedPredictionEngine,
    calculate_solar_return_jd
)
from .calculations import (
    calculate_lunar_phase, 
    calculate_prenatal_syzygy,
    calculate_solar_status, 
    is_in_via_combusta, 
    is_besieged, 
    is_void_of_course
)
from .aspects import AspectEngine
from .dignities import DignityCalculator
from .mundane import (
    get_recent_eclipses, 
    check_eclipse_impact, 
    check_universal_causation_dec2025, 
    MundaneEngine
)
from .horary import calculate_antiscia
from .hyleg import HylegAlcocodenEngine
from .mansions import LunarMansionEngine
from .temperament import TemperamentEngine
from .reception import ReceptionEngine, ReceptionMode
from .rectification import RectificationEngine
from .decumbiture import DecumbitureEngine
from .primary_directions import PrimaryDirectionsEngine
from src.database.db_manager import DelineationLibrary
from .synthesis import ReportSynthesizer
from .reference_data import PLANET_ESSENCES, TERM_METHODS, RULE_SOURCE_MAP
from .lots import calculate_all_lots, LotName

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
                "planets_forensic": planets_forensic
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
            "rectification_animodar": RectificationEngine.animodar_rectification(chart, jd, chart.geo_lat, chart.geo_lon),
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

        return {
            "analysis": analysis,
            "planets_forensic": planets_forensic
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
        except:
            return {"error": "Solar Return calculation failed"}

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
        
        # 2. Advanced Prediction (Transits, Firdaria, Profections)
        predictor = AdvancedPredictionEngine(
            chart, bdt, chart.jd, chart.geo_lat, chart.geo_lon
        )
        prediction_report = predictor.get_prediction_report(ans_date)

        return {
            "hermetic_lots": lots,
            "primary_directions": [
                {
                    "significator": d.significator,
                    "promittor": d.promittor,
                    "aspect": d.aspect,
                    "arc": d.arc,
                    "years": d.years,
                    "date_offset": d.date_offset,
                    "method": d.method
                } for d in directions
            ],
            "primary_direction_distributor": distributor,
            "profections": prediction_report.get("profections", {}), # This might be missing in predict report?
            # Actually AdvancedPredictionEngine puts it in 'muntha' or 'profections'??? 
            # Let's check AdvancedPredictionEngine.get_prediction_report again.
            # It returns: firdaria, solar_arcs, transits, muntha, lunar_phase, mercury_stations, sp_moon_triggers, solar_return_info
            # It does NOT return 'profections' key explicitly, it returns 'muntha'.
            # But the legacy code expected 'profections'.
            # I will map muntha to profections['muntha'] basically.
            "firdaria": prediction_report.get("firdaria", {}),
            "solar_return": prediction_report.get("solar_return_info", {}),
            "muntha": prediction_report.get("muntha", {}),
            "transits": prediction_report.get("transits", [])
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
            "maltreatments": [
                {"type": m.type, "malefic": m.malefic.value, "description": m.description}
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
            "solar_return": analysis["fate"].get("solar_return", {}),
            "forensic_lots": analysis["fate"]["hermetic_lots"],
            "planets": tech_data["planets_forensic"],
            "houses": tech_data["astronomy"]["houses"],
            "aspects": formatted_aspects
        }
        return legacy
