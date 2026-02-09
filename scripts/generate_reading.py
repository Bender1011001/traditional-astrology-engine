import argparse
import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from engine.forensic_engine import Auditor as SovereignEngine

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if hasattr(obj, 'value'):
        return obj.value
    return str(obj)

def main():
    parser = argparse.ArgumentParser(description="Generate a Sovereign Astrological Reading")
    parser.add_argument("date", help="Date in YYYY-MM-DD format")
    parser.add_argument("time", help="Time in HH:MM format (24h)")
    parser.add_argument("city", help="City name")
    parser.add_argument("--state", help="State/Region code (optional)", default="")
    parser.add_argument("--name", help="Name of the native", default="Native")
    
    args = parser.parse_args()
    
    print(f"Generating reading for {args.name}")
    print(f"Data: {args.date} {args.time}, {args.city} {args.state}")
    
    try:
        report_data = SovereignEngine.generate_full_nativity(
            date_str=args.date,
            time_str=args.time,
            city=args.city,
            state=args.state,
            name=args.name
        )
        
        # Save Outputs
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../chart_outputs'))
        os.makedirs(output_dir, exist_ok=True)
        
        safe_name = args.name.replace(" ", "_").lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{safe_name}_{timestamp}"
        
        # JSON
        json_path = os.path.join(output_dir, f"{base_filename}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, default=str, indent=2)
            
        # Markdown
        md_path = os.path.join(output_dir, f"{base_filename}_report.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(report_data["human_translation"]["report_markdown"])
            
        print(f"Success! Reports generated:")
        print(f"- JSON: {json_path}")
        print(f"- Report: {md_path}")
        
    except Exception as e:
        print(f"Error generating reading: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    from datetime import date
    main()
