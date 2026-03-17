"""
Full Forensic Nativity Reading
Birth: August 13, 1996, 7:18 AM, Fairfield, CA
"""
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.engine.forensic_engine import Auditor

def main():
    print("=" * 80)
    print("GENERATING FULL FORENSIC NATIVITY")
    print("Birth: August 13, 1996 | 7:18 AM | Fairfield, CA")
    print("=" * 80)

    result = Auditor.generate_full_nativity(
        date_str="1996-08-13",
        time_str="07:18",
        city="Fairfield",
        state="CA",
        name="Native",
        house_system="W",
    )

    if "error" in result:
        print(f"\nERROR: {result['error']}")
        return

    # Save full JSON
    output_path = os.path.join(os.path.dirname(__file__), '..', 'chart_outputs', 'native_08131996_reading.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\nFull JSON saved to: {output_path}")

    # Save markdown report
    report_path = output_path.replace('.json', '_report.md')
    human = result.get("human_translation", {})
    md = human.get("report_markdown", "No report generated.")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"Report saved to: {report_path}")

    # Print executive summary
    summary = human.get("executive_summary", "No summary available.")
    print("\n" + "=" * 80)
    print("EXECUTIVE SUMMARY")
    print("=" * 80)
    print(summary)

    # Print key technical data
    td = result.get("technical_data", {})
    analysis = td.get("analysis", {})

    # Sect
    sect = analysis.get("sect", {})
    print(f"\n--- SECT: {sect.get('type', 'Unknown')} (Sun Alt: {sect.get('sun_altitude_deg', 'N/A')}°) ---")

    # Temperament
    temp = analysis.get("temperament", {})
    print(f"\n--- TEMPERAMENT: {temp.get('primary_temperament', 'Unknown')} ---")
    print(f"    Scores: {temp.get('scores', {})}")

    # Dignity Summary
    dignity = analysis.get("dignity", {})
    almuten = dignity.get("almuten", {})
    print(f"\n--- ALMUTEN FIGURIS: {almuten.get('winner', 'Unknown')} ---")

    # Vitality
    vitality = analysis.get("vitality", {})
    hyleg = vitality.get("hyleg", {})
    print(f"\n--- HYLEG: {hyleg.get('name', 'Not found')} ---")
    alcoc = vitality.get("alcocoden", {})
    print(f"--- ALCOCODEN: {alcoc.get('name', 'Not found')} ---")

    # Profections
    profs = analysis.get("enhanced_profections", {})
    print(f"\n--- PROFECTIONS (Age {profs.get('age', 'N/A')}) ---")
    print(f"    Annual Sign: {profs.get('annual_sign', 'N/A')}")
    print(f"    Lord of Year: {profs.get('lord_of_year', 'N/A')}")

    # Stars
    stars = analysis.get("supplemental", {}).get("stars", [])
    if stars:
        print(f"\n--- FIXED STAR CONTACTS ({len(stars)}) ---")
        for s in stars[:5]:
            if isinstance(s, dict):
                print(f"    {s.get('star', 'Unknown')} conjunct {s.get('planet', 'Unknown')} (Orb: {s.get('orb', 'N/A')}°)")

    # Lots
    fate = analysis.get("fate", {})
    lots = fate.get("hermetic_lots", {})
    if lots:
        print(f"\n--- HERMETIC LOTS ---")
        for name, data in list(lots.items())[:5]:
            if isinstance(data, dict):
                print(f"    {name}: {data.get('longitude_fmt', data.get('longitude', 'N/A'))}")

    print("\n" + "=" * 80)
    print("FULL READING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
