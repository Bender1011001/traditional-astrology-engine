import json
import os
import sys

def main():
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../reading_output.json'))
    if not os.path.exists(json_path):
        print("reading_output.json not found.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    md_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../FULL_READING_1996_08_13.md'))
    
    with open(md_path, 'w', encoding='utf-8') as f:
        # HEADER
        f.write("# Astrological Forensic Audit\n")
        f.write(f"**Date:** 1996-08-13 | **Time:** 07:18 | **Location:** Fairfield, CA\n\n")
        
        # SUMMARY
        summary = data.get("summary", {})
        f.write("## 1. Constitutional Summary\n")
        f.write(f"- **Sect:** {summary.get('sect')}\n")
        
        temp = summary.get("temperament", {})
        if isinstance(temp, dict):
             f.write(f"- **Temperament:** {temp.get('primary_temperament', 'Unknown')}\n")
        else:
             f.write(f"- **Temperament:** {temp}\n")
             
        f.write(f"- **Lunar Phase:** {summary.get('lunar_phase')} ({summary.get('lunar_phase_profile')})\n")
        
        # TEAMS
        f.write("\n### The Teams\n")
        f.write(f"- **Constructive Team:** {', '.join(summary.get('constructive_team', []))}\n")
        f.write(f"- **Destructive Team:** {', '.join(summary.get('destructive_team', []))}\n")
        f.write(f"> *{summary.get('team_note')}*\n\n")
        
        # SOUL GUARDIAN
        sg = data.get("soul_guardian", {})
        if sg:
            f.write("## 2. The Soul Guardian (Almuten Figuris)\n")
            f.write(f"**Guardian Planet:** {sg.get('almuten')}\n\n")
            f.write(f"> **Archetype:** {sg.get('job_description')}\n\n")
        
        # PLANETS
        f.write("## 3. Planetary Architecture\n")
        for p in data.get("planets", []):
            name = p.get("planet")
            sign = p.get("sign")
            house = p.get("house_number")
            power = p.get("power_label")
            f.write(f"### {name} in {sign} (House {house})\n")
            f.write(f"- **Power Status:** {power}\n")
            f.write(f"- **Dignity Score:** {p.get('dignity_score')}\n")
            
            impacts = p.get("impacts", [])
            if impacts:
                f.write("- **Forensic Notes:**\n")
                for imp in impacts:
                    f.write(f"  - *{imp.get('cause')}:* {imp.get('effect')}\n")
            
            delineation = p.get("delineation_text")
            if delineation:
                f.write(f"\n*{delineation}*\n")
            f.write("\n---\n")

        # PREDICTION (ADVANCED)
        adv = data.get("advanced_prediction", {})
        if adv:
            f.write("## 4. Advanced Prediction (Paid Tier)\n")
            
            # Firdaria
            fird = adv.get("firdaria", {})
            if fird:
                f.write("### Firdaria (Time Lords)\n")
                f.write(f"- **Current Major Lord:** {fird.get('Major Period')} (Until {fird.get('Major End')})\n")
                f.write(f"- **Current Sub Lord:** {fird.get('Sub Period')} (Until {fird.get('Sub End')})\n\n")
            
            # Muntha
            muntha = adv.get("muntha", {})
            if muntha:
                f.write(f"### Annual Profection (Age {muntha.get('age')})\n")
                f.write(f"- **Profection Sign:** {muntha.get('sign')}\n\n")
                
        # 5-DAY FORECAST
        forecast = data.get("forensic_forecast", [])
        if forecast:
            f.write("## 5. 5-Day Forensic Forecast\n")
            for day in forecast:
                f.write(f"### {day.get('display_date')}\n")
                f.write(f"- **Ruler:** {day.get('chronocrator')}\n")
                f.write(f"- **Status:** {'High Stakes (Epitasis)' if day.get('epitasis') else 'Standard Flow'}\n")
                f.write(f"- **Summary:** {day.get('summary')}\n\n")

    print(f"Report generated at {md_path}")

if __name__ == "__main__":
    main()
