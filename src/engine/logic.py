from typing import Optional, Dict, List, Any
from datetime import datetime
from .models import Chart, Sect, PlanetName
from .synthesis import ReportSynthesizer
from .forensic_engine import Auditor
from .reference_data import Sign

def perform_forensic_audit(
    chart: Chart, 
    jd: float = 0.0, 
    age: Optional[int] = None, 
    month: int = 1, 
    day: int = 1, 
    birth_date: Optional[datetime] = None, 
    analysis_date: Optional[datetime] = None, 
    analysis_jd: Optional[float] = None
) -> Dict:
    """
    DEPRECATED: Use Auditor.perform_audit or Auditor.generate_full_nativity.
    Compatibility wrapper for the legacy logic flow using the central Auditor.
    """
    
    # 1. Execute Centralized Audit
    audit_data = Auditor.perform_audit(
        chart=chart,
        jd=jd,
        birth_dt=birth_date,
        ans_date=analysis_date,
        age=age
    )
    
    analysis = audit_data["analysis"]
    planets_forensic = audit_data["planets_forensic"]
    rule_ledger = audit_data.get("rule_ledger", [])
    
    # 2. Map to Legacy Report Structure
    fate = analysis.get("fate", {})
    supp = analysis.get("supplemental", {})
    adv = analysis.get("advanced_mechanics", {})
    med = analysis.get("medical", {})
    teams = analysis.get("teams", {})
    
    # Reconstruct Profections structure from Enhanced Profections
    enh_prof = analysis.get("enhanced_profections", {})
    profections = {
        "annual_sign": enh_prof.get("annual_sign"),
        "lord_of_year": enh_prof.get("lord_of_year"),
        "monthly_sign": enh_prof.get("monthly_sign", {}).get("continuous"),
        "daily_sign": enh_prof.get("daily_sign")
    }
    
    # Reconstruct Hemispheres (if available in supplemental)
    hemispheres = supp.get("hemispheres", {})
    
    report = {
        "summary": {
            "sect": Sect.DAY.value if chart.sun_altitude > 0 else Sect.NIGHT.value,
            "temperament": med.get("distemper"),
            "lunar_mansion": supp.get("lunar_mansion"),
            "mutual_receptions": teams.get("receptions", []),
            "constructive_team": teams.get("constructive_team", []),
            "destructive_team": teams.get("destructive_team", []),
            "maltreatments": {p["name"]: p["maltreatments"] for p in planets_forensic if p.get("maltreatments")},
            "hemispheres": hemispheres.get("counts"),
            "hemisphere_focus": hemispheres.get("focus")
        },
        "vitality": {"vitality_rating": "Refer to Hyleg-Alcocoden Engine"}, 
        "medical_analysis": med,
        "primary_directions": fate.get("primary_directions", []),
        "primary_direction_distributor": fate.get("primary_direction_distributor", {}),
        "profections": profections, 
        "prediction": {
            "epitasis_days": enh_prof.get("epitasis_days", []),
            "annual_profection": {"lord_of_year": enh_prof.get("lord_of_year")},
            "monthly_profection": {"continuous": enh_prof.get("monthly_sign", {}).get("continuous")}
        },
        "solar_return": analysis.get("solar_return", {}),
        "soul_guardian": adv.get("almuten", {}),
        "planets": planets_forensic,
        "lots": fate.get("hermetic_lots", {}),
        "hermetic_lots": fate.get("hermetic_lots", {}),
        "advanced_mechanics": adv,
        "aspects": analysis.get("aspects", []),
        "rule_ledger": rule_ledger,
        "horary_physics": analysis.get("horary_physics", {})
    }
    
    # 3. Add Synthesis (Dossier Text)
    report["dossier_text"] = ReportSynthesizer.synthesize(report)
    
    return report