from datetime import datetime
from typing import Dict, List, Optional, Any
import swisseph as swe
import logging

from .models import Planet, Chart, Sect, PlanetName, Sign
from .chart_calculator import calculate_chart_data
from .advanced_mechanics import AlmutenEngine, HermeticLotEngine, DoryphoryEngine
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

class SovereignEngine:
    """
    The Sovereign Engine (Hub): The sole orchestrator for all astrological logic.
    Refactors fragmented logic into a single unified pipeline.
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
        Single Entry Point for Total Omniscience.
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
            chart = SovereignEngine._rebuild_chart_model(raw_chart_data)
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

            # 2. Analysis: Aggregate Specialized Engine Results
            analysis = {}

            # A. Dignity & Almuten
            analysis["dignity"] = SovereignEngine._calculate_dignity_suite(chart)

            # B. Fate & Prediction
            analysis["fate"] = SovereignEngine._calculate_fate_suite(chart, birth_dt, ans_date)

            # C. Medical
            analysis["medical"] = SovereignEngine._calculate_medical_suite(chart)
            
            # D. Teams & Reception
            analysis["teams"] = SovereignEngine._calculate_teams_and_reception(chart)

            # E. Forensic Planet Analysis
            planets_forensic = SovereignEngine._analyze_all_planets(chart, jd)

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
                    "planets": {p["name"]: p for p in raw_chart_data["planets"]},
                    "houses": raw_chart_data["houses"],
                    "angles": {
                        "Asc": raw_chart_data["meta"]["ascendant"],
                        "MC": raw_chart_data["meta"]["mc"]
                    }
                },
                "analysis": analysis,
                "planets_forensic": planets_forensic
            }

            # 4. Translation: Pass to ReportSynthesizer
            legacy_report = SovereignEngine._map_to_legacy_report(technical_data, chart)
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
            logger.error(f"Sovereign Engine Failure: {e}\n{error_trace}")
            return {"error": f"Sovereign Engine Failure: {str(e)}"}

    @staticmethod
    def _rebuild_chart_model(raw_data: Dict) -> Chart:
        planets = []
        for p in raw_data["planets"]:
            planets.append(Planet(
                name=PlanetName(p["name"]),
                longitude=p["longitude"],
                latitude=p.get("latitude", 0.0),
                speed=p.get("speed", 0.0)
            ))
        
        return Chart(
            sun_altitude=raw_data["meta"]["sun_altitude"],
            planets=planets,
            ascendant=raw_data["meta"]["ascendant"],
            mc=raw_data["meta"]["mc"],
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
        # Use fallback if birth_dt is None (should not happen for natal but safety first)
        bdt = birth_dt or datetime.now()
        
        predictor = AdvancedPredictionEngine(
            chart, bdt, chart.jd, chart.geo_lat, chart.geo_lon
        )
        prediction_report = predictor.get_prediction_report(ans_date)

        return {
            "hermetic_lots": {l.name: l.longitude for l in lots},
            "primary_directions": prediction_report.get("primary_directions", []),
            "profections": prediction_report.get("profections", {}),
            "solar_return": prediction_report.get("solar_return", {}),
            "firdaria": prediction_report.get("firdaria", {})
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
        # Pre-calculate speculum for in-mundo aspects (optional heavy lift)
        # mc_ra, _ = PrimaryDirectionsEngine.ecliptic_to_equatorial(chart.mc, 0.0)
        speculum = {} # Minimalist for this pass
        
        for p in chart.planets:
            if p.name in [PlanetName.URANUS, PlanetName.NEPTUNE, PlanetName.PLUTO]:
                continue
            
            p_data = SovereignEngine._analyze_single_planet(p, chart, jd, speculum)
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
            "vitality": {"vitality_rating": "Stable (Calculated by SovereignEngine)"},
            "medical_analysis": {
                "governed_body_part": analysis["medical"]["constitution"],
                "constitutional_sign": list(Sign)[int(chart.ascendant / 30) % 12].value
            },
            "primary_directions": analysis["fate"]["primary_directions"],
            "profections": analysis["fate"]["profections"],
            "forensic_lots": {},
            "planets": tech_data["planets_forensic"]
        }
        return legacy
