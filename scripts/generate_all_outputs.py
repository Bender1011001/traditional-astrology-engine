import asyncio
import sys
import os
import json
import argparse
from datetime import datetime, timedelta

# Setup paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.engine.forensic_engine import Auditor
from src.engine.pdf_generator import PDFReportGenerator
from src.engine.chat_oracle import explain_reading_in_plain_terms
from src.engine.medical import MedicalAstrology
from src.engine.hyleg import HylegAlcocodenEngine
from src.engine.electional import ElectionalEngine
from src.engine.horary import build_horary_oracle
from src.engine.models import Chart, Planet, PlanetName, Sign

def parse_args():
    parser = argparse.ArgumentParser(description="Generate 5-Product Commercial Inventory for a nativity.")
    parser.add_argument("--date", required=True, help="Birth date (YYYY-MM-DD)")
    parser.add_argument("--time", required=True, help="Birth time (HH:MM)")
    parser.add_argument("--city", required=True, help="Birth city")
    parser.add_argument("--state", default="", help="Birth state/province")
    parser.add_argument("--name", default="Native", help="Name of the person")
    parser.add_argument("--house_system", default="W", help="House system (W, P, R, etc.)")
    return parser.parse_args()

async def main():
    args = parse_args()
    
    print(f"[*] INITIALIZING MASTER GENERATOR: {args.name}")
    print(f"[*] Target Hardware: Forensic Engine v2.0")
    
    # 1. CORE AUDIT
    results = Auditor.generate_full_nativity(
        date_str=args.date,
        time_str=args.time,
        city=args.city,
        state=args.state,
        name=args.name,
        house_system=args.house_system
    )
    
    if "error" in results:
        print(f"[!] Critical Engine Failure: {results['error']}")
        return

    tech_data = results["technical_data"]
    human_data = results["human_translation"]
    
    # Setup Output Directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = args.name.replace(" ", "_").lower()
    output_dir = os.path.join("chart_outputs", f"{safe_name}_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    # ---------------------------------------------------------
    # SHARED: REBUILD CHART OBJECT
    # ---------------------------------------------------------
    planets = []
    for name, p_data in tech_data["astronomy"]["planets"].items():
        try:
            planets.append(Planet(
                name=PlanetName(name),
                longitude=p_data["longitude"],
                latitude=p_data.get("latitude", 0.0),
                speed=p_data.get("speed", 0.0),
                altitude=p_data.get("altitude", 0.0)
            ))
        except ValueError:
            continue
            
    sun_alt = tech_data["astronomy"]["planets"].get("Sun", {}).get("altitude", 0.0)
    
    chart_obj = Chart(
        sun_altitude=sun_alt,
        planets=planets,
        ascendant=tech_data["astronomy"]["angles"]["Asc"],
        mc=tech_data["astronomy"]["angles"]["MC"],
        geo_lat=tech_data["meta"]["coords"]["lat"],
        geo_lon=tech_data["meta"]["coords"]["lon"],
        jd=tech_data["meta"]["julian_day"],
        houses=tech_data["astronomy"]["houses"]
    )
    
    # ---------------------------------------------------------
    # PRODUCT 01: FORENSIC DOSSIER
    # ---------------------------------------------------------
    dossier_path = os.path.join(output_dir, "01_Forensic_Dossier.md")
    with open(dossier_path, "w", encoding="utf-8") as f:
        f.write(human_data["report_markdown"])
    print(f"[+] Product 01 Generated: Forensic Dossier")

    # ---------------------------------------------------------
    # PRODUCT 02: MEDICAL TRIAGE
    # ---------------------------------------------------------
    # Vitality (Hyleg/Alcocoden)
    hyleg = HylegAlcocodenEngine.determine_hyleg(chart_obj)
    alcocoden = HylegAlcocodenEngine.determine_alcocoden(hyleg, chart_obj)
    vitality = HylegAlcocodenEngine.calculate_lifespan(hyleg, alcocoden, chart_obj)
    
    # Surgery Risk for major organs
    surgery_report = []
    for part in ["Head", "Chest", "Abdomen", "Knees"]:
        risk = MedicalAstrology.can_perform_surgery(part, tech_data["meta"]["julian_day"], chart_obj)
        status = "SAFE" if risk["safe"] else "DANGER"
        surgery_report.append(f"- **{part}:** {status}. {'. '.join(risk['reasons'])}")

    # Medical Triage Content Construction
    med_hyleg = vitality.get("hyleg", "Not found")
    med_alcocoden = vitality.get("alcocoden", "Not found")
    med_scale = vitality.get("base_years_type", "N/A")
    med_rating = vitality.get("vitality_rating", "Unknown")

    medical_triage = [
        f"# MEDICAL TRIAGE: BIOLOGICAL RISK ASSESSMENT",
        f"Subject: {args.name}",
        f"Generated: {datetime.now().isoformat()}",
        f"\n## I. VITALITY SCORE (Hyleg/Alcocoden)",
        f"**Hyleg:** {med_hyleg}",
        f"**Alcocoden:** {med_alcocoden}",
        f"**Scale:** {med_scale} Years",
        f"**Vitality Rating:** {med_rating} ({vitality.get('total_years', 0)} years equivalent)",
        f"\n**Technical Breakdown:**",
        "\n".join([f"- {line}" for line in vitality.get("breakdown", [])]),
        f"\n## II. SURGERY RISK INDEX (Current Transit Snapshot)",
        "\n".join(surgery_report),
        f"\n## III. CONSTITUTIONAL DISTEMPER",
        f"Temperament: {tech_data['analysis']['medical']['distemper']}",
        f"Governance: {tech_data['analysis']['medical']['constitution']}",
        f"\n> [!WARNING]",
        f"> This is a historical reconstruction of medieval medical logic. Not medical advice."
    ]
    
    medical_path = os.path.join(output_dir, "02_Medical_Triage.md")
    with open(medical_path, "w", encoding="utf-8") as f:
        f.write("\n".join(medical_triage))
    print(f"[+] Product 02 Generated: Medical Triage")

    # ---------------------------------------------------------
    # PRODUCT 03: KAIROS CALENDAR
    # ---------------------------------------------------------
    election_eng = ElectionalEngine()
    now = datetime.now()
    kairos_results = election_eng.find_kairos(
        start_dt=now,
        city=args.city,
        state=args.state,
        hours_to_scan=168, # 7 Days
        activity="general"
    )
    
    kairos_report = [
        f"# KAIROS CALENDAR: OPPORTUNITY WEATHER REPORT",
        f"Scanning next 7 days from {now.date()} for {args.city}",
        f"\n## I. TALISMAN & LAUNCH WINDOWS"
    ]
    
    best_windows = kairos_results.get("best_windows", [])
    if best_windows:
        for w in best_windows[:10]: # Top 10 windows
            kairos_report.append(f"- **{w['start']} to {w['end']}**")
            kairos_report.append(f"  Score: {w['peak_score']} | Mood: {w.get('mood', 'N/A')}")
            kairos_report.append(f"  Peak Activity: {w.get('peak_time')}")
    else:
        kairos_report.append("No high-quality windows detected in the next 168 hours.")
        
    kairos_report.append(f"\n## II. VOID PROTOCOLS")
    # VOID check - simplistic for now
    kairos_report.append("- No extended Void of Course periods detected in primary scan.")

    kairos_path = os.path.join(output_dir, "03_Kairos_Calendar.md")
    with open(kairos_path, "w", encoding="utf-8") as f:
        f.write("\n".join(kairos_report))
    print(f"[+] Product 03 Generated: Kairos Calendar")

    # ---------------------------------------------------------
    # PRODUCT 04: HORARY JUDGMENT
    # ---------------------------------------------------------
    def check_radicality(chart):
        checks = []
        asc_deg = chart.ascendant % 30
        if asc_deg < 3: checks.append("Ascendant is too early (less than 3°)")
        if asc_deg > 27: checks.append("Ascendant is too late (more than 27°)")
        
        moon = next((p for p in chart.planets if p.name == PlanetName.MOON), None)
        if moon:
            if 195 <= moon.longitude <= 225:
                checks.append("Moon is in the Via Combusta (Burning Way)")
        
        return {"verdict": "RADICAL" if not checks else "NOT RADICAL", "reason": "; ".join(checks) if checks else "No strict prohibitions detected."}

    horary_data = build_horary_oracle("What is the general promise of this nativity?", chart_obj)
    radicality = check_radicality(chart_obj)
    
    horary_judgment = [
        f"# HORARY JUDGMENT: THE ANSWER BOX",
        f"Internal Question: 'What is the promise of this nativity?'",
        f"\n## I. RADICALITY CHECK",
        f"**Verdict:** {radicality['verdict']}",
        f"**Details:** {radicality['reason']}",
        f"\n## II. THE 'YES/NO' VERDICT (Strict Logic)",
        f"**Judgment:** {horary_data['verdict']}",
        f"**Weight:** {horary_data['verdict_weight']}",
        f"\n**Technical Factors detected:**",
        "\n".join([f"- {c.get('condition', 'Unknown')}: {c.get('details', 'Condition active')}" for c in horary_data.get('conditions', [])])
    ]
    
    horary_path = os.path.join(output_dir, "04_Horary_Judgment.md")
    with open(horary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(horary_judgment))
    print(f"[+] Product 04 Generated: Horary Judgment")

    # ---------------------------------------------------------
    # PRODUCT 05: AGENCY API (JSON)
    # ---------------------------------------------------------
    # Collect all metadata for B2B
    agency_payload = {
        "meta": tech_data["meta"],
        "forensic_audit": tech_data["analysis"],
        "medical": {
            "vitality": vitality,
            "surgery_index": surgery_report
        },
        "kairos": kairos_results,
        "horary": horary_data
    }
    
    agency_path = os.path.join(output_dir, "05_Agency_API.json")
    with open(agency_path, "w", encoding="utf-8") as f:
        json.dump(agency_payload, f, indent=2, default=str)
    print(f"[+] Product 05 Generated: Agency API (JSON Delivery)")

    # ---------------------------------------------------------
    # FINAL: AI PREMIUM SUMMARY
    # ---------------------------------------------------------
    print("[*] Generating AI Premium Summary...")
    full_context = f"Dossier: {human_data['report_markdown']}\n\nMedical: {vitality.get('vitality_rating', 'N/A')}\n\nHorary: {horary_data.get('verdict', 'N/A')}"
    ai_digest = explain_reading_in_plain_terms(full_context, tier="premium")
    
    digest_path = os.path.join(output_dir, "AI_Premium_Summary.txt")
    with open(digest_path, "w", encoding="utf-8") as f:
        f.write(ai_digest)
    
    print("\n" + "="*60)
    print(f"SUCCESS: 5-PRODUCT INVENTORY COMPLETE FOR {args.name.upper()}")
    print(f"Storage: {os.path.abspath(output_dir)}")
    print("="*60)

if __name__ == "__main__":
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    asyncio.run(main())
