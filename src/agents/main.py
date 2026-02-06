import sys
import os
import json
import argparse
from datetime import datetime
import swisseph as swe

# Ensure project root is in path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.engine.chart_calculator import calculate_chart_data
from src.engine.models import Chart, Planet, PlanetName, Sign
from src.engine.logic import perform_forensic_audit
from src.engine.chat_oracle import get_chat_response

class AstroAgent:
    """
    Unified internal interface for AI agents to interact with the Astrology Engine.
    """

    @staticmethod
    def map_to_planet_name(k: str) -> PlanetName:
        k = k.upper()
        if k == "NORTH_NODE": return PlanetName.NORTH_NODE
        if k == "SOUTH_NODE": return PlanetName.SOUTH_NODE
        try:
            return PlanetName[k]
        except KeyError:
            return None

    def calculate(self, date_str: str, time_str: str, city: str, state: str = "") -> dict:
        """Calculate raw astronomical data."""
        data = calculate_chart_data(date_str, time_str, city, state)
        if "error" in data:
            return data
        return data

    def audit(self, chart_data: dict) -> dict:
        """Perform forensic audit on calculated chart data."""
        if "error" in chart_data:
            return chart_data

        # Convert to Chart Object
        planet_objects = []
        sun_alt = 0.0
        
        for name, pdata in chart_data["planets"].items():
            pname = self.map_to_planet_name(name)
            if not pname: continue
            
            planet = Planet(
                name=pname,
                longitude=pdata["longitude"],
                latitude=pdata.get("latitude", 0.0),
                speed=pdata.get("speed", 0.0),
                altitude=pdata.get("altitude", 0.0)
            )
            planet_objects.append(planet)
            
            if pname == PlanetName.SUN:
                sun_alt = pdata.get("altitude", 0.0)

        asc = chart_data["angles"]["Ascendant"]
        mc = chart_data["angles"]["MC"]
        nn = chart_data["planets"].get("North_Node", {}).get("longitude", 0.0)
        sn = chart_data["planets"].get("South_Node", {}).get("longitude", 0.0)

        chart = Chart(
            sun_altitude=sun_alt,
            planets=planet_objects,
            ascendant=asc,
            mc=mc,
            north_node=nn,
            south_node=sn,
            geo_lat=chart_data["meta"].get("lat"),
            geo_lon=chart_data["meta"].get("lon"),
            jd=chart_data["meta"].get("julian_day"),
            houses={int(k): v for k, v in chart_data.get("houses", {}).items()},
            house_system=chart_data["meta"].get("house_system", {}).get("code")
        )

        # Timings
        date_str = chart_data["meta"].get("date")
        time_str = chart_data["meta"].get("time")
        try:
            birth_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except:
            birth_dt = datetime.now()

        analysis_dt = datetime.now()
        age = analysis_dt.year - birth_dt.year - ((analysis_dt.month, analysis_dt.day) < (birth_dt.month, birth_dt.day))

        analysis_jd = swe.julday(
            analysis_dt.year,
            analysis_dt.month,
            analysis_dt.day,
            analysis_dt.hour + analysis_dt.minute / 60.0 + analysis_dt.second / 3600.0
        )

        return perform_forensic_audit(
            chart,
            chart.jd or 0.0,
            age=age,
            birth_date=birth_dt,
            analysis_date=analysis_dt,
            analysis_jd=analysis_jd
        )

    def oracle(self, query: str, context_data: dict) -> str:
        """Consult the Chat Oracle with specific context."""
        context_str = json.dumps(context_data, indent=2)
        return get_chat_response(query, context_str)

    def run_full_dossier(self, date_str: str, time_str: str, city: str, state: str = "") -> dict:
        """Run the full pipeline: Calculate -> Audit."""
        calc_data = self.calculate(date_str, time_str, city, state)
        if "error" in calc_data:
            return calc_data
        
        audit_data = self.audit(calc_data)
        
        return {
            "calculation": calc_data,
            "audit": audit_data
        }

def main():
    parser = argparse.ArgumentParser(description="AstroAgent: Internal Astrology Engine Interface for Agents")
    parser.add_argument("--action", choices=["calculate", "audit", "oracle", "full"], required=True)
    parser.add_argument("--date", help="YYYY-MM-DD")
    parser.add_argument("--time", help="HH:MM")
    parser.add_argument("--city")
    parser.add_argument("--state", default="")
    parser.add_argument("--query", help="Oracle query")
    parser.add_argument("--context_file", help="Path to JSON context for Oracle")

    args = parser.parse_args()
    agent = AstroAgent()

    if args.action == "calculate":
        result = agent.calculate(args.date, args.time, args.city, args.state)
        print(json.dumps(result, indent=2))
    
    elif args.action == "audit":
        calc_data = agent.calculate(args.date, args.time, args.city, args.state)
        result = agent.audit(calc_data)
        # Handle non-serializable objects (like Enums)
        def default_serializer(obj):
            if isinstance(obj, PlanetName) or isinstance(obj, Sign):
                return obj.value
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
            
        print(json.dumps(result, indent=2, default=default_serializer))

    elif args.action == "oracle":
        context = {}
        if args.context_file and os.path.exists(args.context_file):
            with open(args.context_file, "r") as f:
                context = json.load(f)
        
        result = agent.oracle(args.query, context)
        print(result)

    elif args.action == "full":
        result = agent.run_full_dossier(args.date, args.time, args.city, args.state)
        
        def default_serializer(obj):
            if hasattr(obj, 'value'): # Enums
                return obj.value
            if isinstance(obj, datetime):
                return obj.isoformat()
            return str(obj)

        print(json.dumps(result, indent=2, default=default_serializer))

if __name__ == "__main__":
    main()
