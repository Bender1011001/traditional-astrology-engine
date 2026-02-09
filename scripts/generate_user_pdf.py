import sys
import os
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.pdf_generator import PDFReportGenerator

def main():
    # Hardcoded birth data from the previous step
    date_str = "1926-06-01"
    time_str = "09:30"
    city = "Los Angeles"
    state = "CA"
    subject_name = "Marilyn Monroe" # Contextual

    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../user_reading_output.json'))
    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../user_reading_report.pdf'))
    
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found. Please run the reading generation script first.")
        return

    # 1. Load Forensic Report
    with open(json_path, 'r', encoding='utf-8') as f:
        forensic_report = json.load(f)

    # 2. Recalculate Chart Data for "Meta" and "Astronomy" (Houses)
    # We need to import the calculator
    try:
        from src.engine.calculator.main import calculate_chart_data
    except ImportError:
         print("Could not import calculate_chart_data. Ensure you are running from project root or scripts folder.")
         return

    print(f"Recalculating chart for {date_str} {time_str}...")
    chart_result = calculate_chart_data(date_str, time_str, city, state)
    
    if "error" in chart_result:
        print(f"Chart Calculation Error: {chart_result['error']}")
        return

    # 3. Construct Wrapper for PDFRepoerGenerator
    # 3. Construct Wrapper for PDFRepoerGenerator
    from src.engine.models import Sign
    
    def get_sign(lon):
        return list(Sign)[int(lon / 30) % 12].value

    # Placeholder Delineations to replace "Unknown" or "Calculation complete"
    # In a real production system, this would come from the DB.
    # Since the DB is returning "not found" or the generator has placeholders, we inject them here.
    
    HOUSE_DELINEATIONS = {
        "1": "The House of Self. Represents the native's body, appearance, and primary motivation. A focus on personal identity and self-expression.",
        "2": "The House of Resources. Concerns movable assets, income, and livelihood. Indicates how the native gains and manages wealth.",
        "3": "The House of Siblings and Routine. Governs brothers, sisters, short journeys, and daily communication. A focus on the immediate environment.",
        "4": "The House of Home and Parents. Represents the father, conflicting with modern take (mother), ancestry, land, and the end of life. Evaluation of foundations.",
        "5": "The House of Pleasure and Children. Covers procreation, leisure, risk-taking, and creative pursuits. Calling for joy and generative action.",
        "6": "The House of Illness and Service. Relates to physical ailments, subordinates, and unequal relationships. A place of toil and maintenance.",
        "7": "The House of Partners. Governs marriage, open enemies, and contractual relationships. The 'Other' in the native's life.",
        "8": "The House of Death and Inheritance. Concerns benefits from death, other people's money, and fear/anguish. Idle resources not earned.",
        "9": "The House of God and Travel. Relates to religion, philosophy, long journeys, and dreams. The search for higher truth.",
        "10": "The House of Praxis. Represents career, reputation, and authority. The native's public standing and actions.",
        "11": "The House of Good Spirit. Governs friends, hopes, and alliances. The joy of social connection and patronage.",
        "12": "The House of Bad Spirit. Concerns self-undoing, secret enemies, and confinement. Hidden sorrows and labor."
    }

    houses_raw = chart_result.get("houses", {})
    houses_formatted = {}
    for k, v in houses_raw.items():
        # Clean up key to be string '1', '2' etc
        k_str = str(k)
        sign = get_sign(v)
        houses_formatted[k_str] = {
            "sign": sign, 
            "longitude": v,
            "delineation": f"{sign} on the {k_str}th House cusp. {HOUSE_DELINEATIONS.get(k_str, '')}"
        }

    # Inject Planet Delineations if missing or "not found"
    # We can use a simple keyword generator based on Sign + Planet
    def generate_planet_delineation(planet_name, sign_name, house_num):
        return (f"{planet_name} is placed in {sign_name} in the {house_num}th House. "
                f"This placement emphasizes {sign_name} themes—such as its element and mode—"
                f"within the area of life associated with the {house_num}th House.")

    if "planets" not in forensic_report:
        forensic_report["planets"] = []
    
    # Process planets in forensic report to ensure they have delineations
    # The structure in forensic_report (from logic.py) is a list of dicts.
    for p in forensic_report.get("planets", []):
        current_text = p.get("delineation", "")
        if not current_text or "Delineation not found" in current_text:
            # We need to find the house for this planet.
            # We can use the longitude from the planet data and the house cusps.
            # But simpler: we can just ask the chart_result planets if we can match them.
            # Or just use the sign/house data we already have if available.
            
            # Let's try to find the planet in chart_result to get its longitude, then House.
            p_name = p.get("name")
            p_lon = p.get("longitude")
            
            # Find House 
            # Simple approximation if we don't want to re-import the whole calc engine:
            # But we imported models.Sign.
            # Let's use the house dictionary we just built.
            
            # actually logic.py output usually has house? No, it has sign.
            # calculating house dynamically used to be in the engine. 
            # Let's assume Whole Sign for simplicity of text generation if exact house is missing.
            # But wait, we have chart_result['planets'] which has longitudes.
            
            # Match planet in chart_result
            # chart_result["planets"] is Dict[str, Dict]
            p_data_raw = chart_result.get("planets", {}).get(p_name)
            
            house_num = "?"
            if p_data_raw:
                # Calculate house
                # We need the Ascendant.
                asc = chart_result.get("angles", {}).get("Ascendant", 0)
                # Whole Sign House calculation:
                
                p_lon = p_data_raw["longitude"]
                
                # Zero-based sign index from Ascendant sign
                p_sign_idx = int(p_lon / 30)
                asc_sign_idx = int(asc / 30)
                house_idx = (p_sign_idx - asc_sign_idx) % 12
                house_num = house_idx + 1
            
            if house_num != "?":
                p["delineation"] = generate_planet_delineation(p_name, p.get("sign"), house_num)

    wrapper_data = {
        "meta": chart_result.get("meta", {}),
        "forensic_report": forensic_report,
        "astronomy": {
            "houses": houses_formatted,
            "planets": chart_result.get("planets", {}) 
        },
        "technical_data": { 
            "astronomy": chart_result
        }
    }
    
    # Add subject name to meta
    wrapper_data["meta"]["subject_name"] = subject_name

    print("Generating PDF...")
    generator = PDFReportGenerator(wrapper_data, tier="FULL")
    pdf_buffer = generator.generate()
    
    with open(pdf_path, 'wb') as f:
        f.write(pdf_buffer.getvalue())
        
    print(f"PDF Report saved to {pdf_path}")

if __name__ == "__main__":
    main()
