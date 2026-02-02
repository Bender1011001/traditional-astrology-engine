import os
from enum import Enum
import json
import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.engine.sovereign_engine import SovereignEngine
from src.engine.models import Planet, Chart, PlanetName, Sign, LotName, Sect

class AstrologicalEncoder(json.JSONEncoder):
    """Custom JSON encoder for astrological objects."""
    def default(self, o):
        if isinstance(o, Enum):
            return o.value
        if hasattr(o, "__dict__"):
            return {k: v for k, v in o.__dict__.items() if not k.startswith('_')}
        if hasattr(o, "as_dict"):
            return o.as_dict()
        try:
            return super().default(o)
        except TypeError:
            # Fallback for complex objects that might have custom attributes
            return str(o)

def main():
    parser = argparse.ArgumentParser(description="Generate practitioner-grade astrological reports.")
    parser.add_argument("--name", type=str, required=True, help="Name of the person")
    parser.add_argument("--date", type=str, required=True, help="Birth date (YYYY-MM-DD)")
    parser.add_argument("--time", type=str, required=True, help="Birth time (HH:MM)")
    parser.add_argument("--city", type=str, required=True, help="Birth city")
    parser.add_argument("--state", type=str, default="", help="Birth state/province")
    parser.add_argument("--house_system", type=str, default="W", help="House system (W=Whole Sign, P=Placidus, K=Koch, etc.)")
    parser.add_argument("--ayanamsa", type=str, default=None, help="Ayanamsa for sidereal calculations")
    parser.add_argument("--output_dir", type=str, default="practitioner_outputs", help="Directory for output files")

    args = parser.parse_args()

    # Create output directory
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"[*] Initializing Sovereign Engine for {args.name}...")
    
    # Generate data
    result = SovereignEngine.generate_full_nativity(
        date_str=args.date,
        time_str=args.time,
        city=args.city,
        state=args.state,
        name=args.name,
        house_system=args.house_system,
        ayanamsa=args.ayanamsa
    )

    if "error" in result:
        print(f"[!] Error: {result['error']}")
        sys.exit(1)

    technical_data = result.get("technical_data")
    human_translation = result.get("human_translation")

    # Sanitize name for filenames
    safe_name = args.name.replace(" ", "_").lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    json_filename = f"{safe_name}_technical_chart_{timestamp}.json"
    md_filename = f"{safe_name}_reading_report_{timestamp}.md"

    json_path = output_path / json_filename
    md_path = output_path / md_filename

    # Save JSON (The FULL COMPLETE TOTAL CHART)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(technical_data, f, indent=4, cls=AstrologicalEncoder)
    
    # Save Markdown (The detailed translation)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(human_translation.get("report_markdown", "# Failed to generate report"))

    print(f"[+] SUCCESS: Reports generated for {args.name}")
    print(f"    1. Technical Chart: {json_path}")
    print(f"    2. Reading Report:  {md_path}")

if __name__ == "__main__":
    main()
