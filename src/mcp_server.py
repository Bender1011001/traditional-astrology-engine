#!/usr/bin/env python3
"""
Astrology MCP Server
====================
A Model Context Protocol server exposing all astrology engine features as tools.

Usage:
    python mcp_server.py

This server exposes the following tools:
    - calculate_chart: Calculate a natal chart
    - forensic_audit: Full practitioner-grade nativity analysis
    - find_electional_window: Find optimal timing for activities
    - calculate_decennials: Get Valens-style time lord periods
    - calculate_phasis: Get planetary visibility and synodic phase
    - get_mundane_context: Get eclipses, great conjunctions, firdaria
    - medical_triage: Health analysis from chart
    - horary_judgment: Answer a question with horary astrology
    - calculate_solar_return: Get annual return chart
    - calculate_synastry: Compare two charts
    - get_planetary_hour: Current planetary hour for location
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Any, Optional

# Ensure src is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, ".env"))

# MCP Protocol imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Astrology engine imports
from src.engine.chart_calculator import ChartCalculator, get_coordinates
from src.engine.forensic_engine import Auditor
from src.engine.electional import ElectionalEngine
from src.engine.decennials import DecennialEngine
from src.engine.phasis import PhasisEngine
from src.engine.mundane import MundaneEngine
from src.engine.medical import MedicalEngine
from src.engine.horary import HoraryEngine
from src.engine.solar_return import SolarReturnEngine
from src.engine.synastry import SynastryEngine
from src.engine.planetary_hours import PlanetaryHourCalculator
from src.engine.models import PlanetName

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("astrology-mcp")

# Initialize server
server = Server("astrology")

# =============================================================================
# TOOL DEFINITIONS
# =============================================================================

TOOLS = [
    Tool(
        name="calculate_chart",
        description="Calculate a natal chart for given birth data. Returns planets, houses, aspects, and dignities.",
        inputSchema={
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Birth year (e.g., 1996)"},
                "month": {"type": "integer", "description": "Birth month (1-12)"},
                "day": {"type": "integer", "description": "Birth day (1-31)"},
                "hour": {"type": "integer", "description": "Birth hour (0-23)"},
                "minute": {"type": "integer", "description": "Birth minute (0-59)"},
                "city": {"type": "string", "description": "Birth city (e.g., 'Fairfield')"},
                "state": {"type": "string", "description": "State/region (e.g., 'CA')"},
                "country": {"type": "string", "description": "Country (e.g., 'USA')", "default": "USA"}
            },
            "required": ["year", "month", "day", "hour", "minute", "city"]
        }
    ),
    Tool(
        name="forensic_audit",
        description="Perform a full practitioner-grade forensic astrological audit. Returns comprehensive analysis including Almuten, Lots, Decennials, and forecasting.",
        inputSchema={
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Birth year"},
                "month": {"type": "integer", "description": "Birth month (1-12)"},
                "day": {"type": "integer", "description": "Birth day (1-31)"},
                "hour": {"type": "integer", "description": "Birth hour (0-23)"},
                "minute": {"type": "integer", "description": "Birth minute (0-59)"},
                "city": {"type": "string", "description": "Birth city"},
                "state": {"type": "string", "description": "State/region"},
                "include_forecast": {"type": "boolean", "description": "Include 5-year forecast", "default": True}
            },
            "required": ["year", "month", "day", "hour", "minute", "city"]
        }
    ),
    Tool(
        name="find_electional_window",
        description="Find optimal timing windows for an activity using electional astrology. Uses Bonatti considerations.",
        inputSchema={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "Location city"},
                "state": {"type": "string", "description": "State/region"},
                "activity": {
                    "type": "string",
                    "description": "Type of activity",
                    "enum": ["general", "contract", "signing", "mercantile", "marriage", "romance", "art", "war", "competition", "surgery"]
                },
                "hours_to_scan": {"type": "integer", "description": "Hours to scan ahead", "default": 168},
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD), defaults to now"}
            },
            "required": ["city", "activity"]
        }
    ),
    Tool(
        name="calculate_decennials",
        description="Calculate Valens-style Decennial time lord periods for a chart. Shows major and minor periods.",
        inputSchema={
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Birth year"},
                "month": {"type": "integer", "description": "Birth month (1-12)"},
                "day": {"type": "integer", "description": "Birth day (1-31)"},
                "hour": {"type": "integer", "description": "Birth hour (0-23)"},
                "minute": {"type": "integer", "description": "Birth minute (0-59)"},
                "city": {"type": "string", "description": "Birth city"},
                "state": {"type": "string", "description": "State/region"},
                "target_date": {"type": "string", "description": "Date to check (YYYY-MM-DD), defaults to now"}
            },
            "required": ["year", "month", "day", "hour", "minute", "city"]
        }
    ),
    Tool(
        name="calculate_phasis",
        description="Calculate planetary visibility and synodic phase for each planet in a chart.",
        inputSchema={
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Birth year"},
                "month": {"type": "integer", "description": "Birth month (1-12)"},
                "day": {"type": "integer", "description": "Birth day (1-31)"},
                "hour": {"type": "integer", "description": "Birth hour (0-23)"},
                "minute": {"type": "integer", "description": "Birth minute (0-59)"},
                "city": {"type": "string", "description": "Birth city"},
                "state": {"type": "string", "description": "State/region"}
            },
            "required": ["year", "month", "day", "hour", "minute", "city"]
        }
    ),
    Tool(
        name="get_mundane_context",
        description="Get mundane astrological context: eclipses, great conjunctions, Jupiter-Saturn cycles, and world Firdaria.",
        inputSchema={
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Target year"},
                "month": {"type": "integer", "description": "Target month (1-12)"},
                "day": {"type": "integer", "description": "Target day (1-31)"}
            },
            "required": ["year", "month", "day"]
        }
    ),
    Tool(
        name="medical_triage",
        description="Perform medical astrology analysis (decumbiture). Identifies humoral imbalances and vulnerable body systems.",
        inputSchema={
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "Birth year"},
                "month": {"type": "integer", "description": "Birth month (1-12)"},
                "day": {"type": "integer", "description": "Birth day (1-31)"},
                "hour": {"type": "integer", "description": "Birth hour (0-23)"},
                "minute": {"type": "integer", "description": "Birth minute (0-59)"},
                "city": {"type": "string", "description": "Birth city"},
                "state": {"type": "string", "description": "State/region"}
            },
            "required": ["year", "month", "day", "hour", "minute", "city"]
        }
    ),
    Tool(
        name="horary_judgment",
        description="Cast a horary chart and provide judgment for a question. Uses traditional horary rules.",
        inputSchema={
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "The question to answer"},
                "city": {"type": "string", "description": "Location where question is asked"},
                "state": {"type": "string", "description": "State/region"},
                "question_time": {"type": "string", "description": "Time question was asked (YYYY-MM-DD HH:MM), defaults to now"}
            },
            "required": ["question", "city"]
        }
    ),
    Tool(
        name="calculate_solar_return",
        description="Calculate a Solar Return chart for a given year.",
        inputSchema={
            "type": "object",
            "properties": {
                "birth_year": {"type": "integer", "description": "Birth year"},
                "birth_month": {"type": "integer", "description": "Birth month (1-12)"},
                "birth_day": {"type": "integer", "description": "Birth day (1-31)"},
                "birth_hour": {"type": "integer", "description": "Birth hour (0-23)"},
                "birth_minute": {"type": "integer", "description": "Birth minute (0-59)"},
                "birth_city": {"type": "string", "description": "Birth city"},
                "birth_state": {"type": "string", "description": "Birth state/region"},
                "return_year": {"type": "integer", "description": "Year of solar return"},
                "return_city": {"type": "string", "description": "Location for solar return (defaults to birth city)"},
                "return_state": {"type": "string", "description": "State for solar return"}
            },
            "required": ["birth_year", "birth_month", "birth_day", "birth_hour", "birth_minute", "birth_city", "return_year"]
        }
    ),
    Tool(
        name="calculate_synastry",
        description="Compare two charts for relationship compatibility.",
        inputSchema={
            "type": "object",
            "properties": {
                "person1": {
                    "type": "object",
                    "properties": {
                        "year": {"type": "integer"},
                        "month": {"type": "integer"},
                        "day": {"type": "integer"},
                        "hour": {"type": "integer"},
                        "minute": {"type": "integer"},
                        "city": {"type": "string"},
                        "state": {"type": "string"}
                    },
                    "required": ["year", "month", "day", "hour", "minute", "city"]
                },
                "person2": {
                    "type": "object",
                    "properties": {
                        "year": {"type": "integer"},
                        "month": {"type": "integer"},
                        "day": {"type": "integer"},
                        "hour": {"type": "integer"},
                        "minute": {"type": "integer"},
                        "city": {"type": "string"},
                        "state": {"type": "string"}
                    },
                    "required": ["year", "month", "day", "hour", "minute", "city"]
                }
            },
            "required": ["person1", "person2"]
        }
    ),
    Tool(
        name="get_planetary_hour",
        description="Get the current planetary hour for a location.",
        inputSchema={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "state": {"type": "string", "description": "State/region"},
                "time": {"type": "string", "description": "Time to check (YYYY-MM-DD HH:MM), defaults to now"}
            },
            "required": ["city"]
        }
    )
]

# =============================================================================
# TOOL HANDLERS
# =============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return list of available tools."""
    return TOOLS

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    
    try:
        if name == "calculate_chart":
            result = await handle_calculate_chart(arguments)
        elif name == "forensic_audit":
            result = await handle_forensic_audit(arguments)
        elif name == "find_electional_window":
            result = await handle_electional(arguments)
        elif name == "calculate_decennials":
            result = await handle_decennials(arguments)
        elif name == "calculate_phasis":
            result = await handle_phasis(arguments)
        elif name == "get_mundane_context":
            result = await handle_mundane(arguments)
        elif name == "medical_triage":
            result = await handle_medical(arguments)
        elif name == "horary_judgment":
            result = await handle_horary(arguments)
        elif name == "calculate_solar_return":
            result = await handle_solar_return(arguments)
        elif name == "calculate_synastry":
            result = await handle_synastry(arguments)
        elif name == "get_planetary_hour":
            result = await handle_planetary_hour(arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}
            
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
        
    except Exception as e:
        logger.exception(f"Error in tool {name}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

# =============================================================================
# HANDLER IMPLEMENTATIONS
# =============================================================================

async def handle_calculate_chart(args: dict) -> dict:
    """Calculate a natal chart."""
    dt = datetime(
        args["year"], args["month"], args["day"],
        args["hour"], args["minute"]
    )
    city = args["city"]
    state = args.get("state", "")
    
    calc = ChartCalculator()
    chart = calc.calculate_chart(dt, city, state)
    
    # Convert to serializable format
    return {
        "birth_data": {
            "datetime": dt.isoformat(),
            "location": f"{city}, {state}"
        },
        "planets": [
            {
                "name": p.name.value,
                "longitude": p.longitude,
                "sign": list(from_longitude_to_sign(p.longitude)),
                "speed": p.speed,
                "retrograde": p.speed < 0 if p.speed else False
            }
            for p in chart.planets
        ],
        "houses": {
            "ascendant": chart.ascendant,
            "mc": chart.mc,
            "asc_sign": from_longitude_to_sign(chart.ascendant)[0]
        },
        "sect": "DAY" if chart.sun_altitude > 0 else "NIGHT"
    }

def from_longitude_to_sign(lon: float) -> tuple:
    """Convert longitude to sign and degree."""
    from src.engine.models import Sign
    sign_idx = int(lon / 30) % 12
    sign = list(Sign)[sign_idx]
    degree = lon % 30
    return (sign.value, round(degree, 2))

async def handle_forensic_audit(args: dict) -> dict:
    """Perform full forensic audit."""
    dt = datetime(
        args["year"], args["month"], args["day"],
        args["hour"], args["minute"]
    )
    city = args["city"]
    state = args.get("state", "")
    
    result = Auditor.generate_full_nativity(
        birth_dt=dt,
        city=city,
        state=state
    )
    
    return result

async def handle_electional(args: dict) -> dict:
    """Find electional windows."""
    city = args["city"]
    state = args.get("state", "")
    activity = args.get("activity", "general")
    hours = args.get("hours_to_scan", 168)
    
    start_str = args.get("start_date")
    if start_str:
        start_dt = datetime.fromisoformat(start_str)
    else:
        start_dt = datetime.now()
    
    engine = ElectionalEngine()
    result = engine.find_kairos(
        start_dt=start_dt,
        city=city,
        state=state,
        hours_to_scan=hours,
        activity=activity
    )
    
    return result

async def handle_decennials(args: dict) -> dict:
    """Calculate decennial periods."""
    dt = datetime(
        args["year"], args["month"], args["day"],
        args["hour"], args["minute"]
    )
    city = args["city"]
    state = args.get("state", "")
    
    target_str = args.get("target_date")
    if target_str:
        target_dt = datetime.fromisoformat(target_str)
    else:
        target_dt = datetime.now()
    
    # Calculate chart first
    calc = ChartCalculator()
    chart = calc.calculate_chart(dt, city, state)
    
    engine = DecennialEngine()
    result = engine.calculate(chart, target_dt)
    
    return result

async def handle_phasis(args: dict) -> dict:
    """Calculate planetary phasis."""
    dt = datetime(
        args["year"], args["month"], args["day"],
        args["hour"], args["minute"]
    )
    city = args["city"]
    state = args.get("state", "")
    
    # Calculate chart first
    calc = ChartCalculator()
    chart = calc.calculate_chart(dt, city, state)
    
    engine = PhasisEngine()
    
    results = {}
    for planet in chart.planets:
        if planet.name in [PlanetName.MERCURY, PlanetName.VENUS, PlanetName.MARS, 
                          PlanetName.JUPITER, PlanetName.SATURN]:
            sun = next(p for p in chart.planets if p.name == PlanetName.SUN)
            phasis = engine.calculate_phasis(planet, sun, dt)
            results[planet.name.value] = phasis
    
    return results

async def handle_mundane(args: dict) -> dict:
    """Get mundane context."""
    dt = datetime(args["year"], args["month"], args["day"])
    
    engine = MundaneEngine()
    
    return {
        "eclipses": engine.get_recent_eclipses(dt, years_back=1, years_forward=1),
        "great_conjunctions": engine.get_great_conjunctions(dt.year - 20, dt.year + 10),
        "world_firdaria": engine.get_world_firdaria(dt),
        "mighty_firdaria": engine.get_mighty_firdaria(dt)
    }

async def handle_medical(args: dict) -> dict:
    """Perform medical triage."""
    dt = datetime(
        args["year"], args["month"], args["day"],
        args["hour"], args["minute"]
    )
    city = args["city"]
    state = args.get("state", "")
    
    # Calculate chart first
    calc = ChartCalculator()
    chart = calc.calculate_chart(dt, city, state)
    
    engine = MedicalEngine()
    result = engine.analyze(chart)
    
    return result

async def handle_horary(args: dict) -> dict:
    """Perform horary judgment."""
    question = args["question"]
    city = args["city"]
    state = args.get("state", "")
    
    time_str = args.get("question_time")
    if time_str:
        question_dt = datetime.fromisoformat(time_str)
    else:
        question_dt = datetime.now()
    
    engine = HoraryEngine()
    result = engine.judge(
        question=question,
        question_dt=question_dt,
        city=city,
        state=state
    )
    
    return result

async def handle_solar_return(args: dict) -> dict:
    """Calculate solar return."""
    birth_dt = datetime(
        args["birth_year"], args["birth_month"], args["birth_day"],
        args["birth_hour"], args["birth_minute"]
    )
    birth_city = args["birth_city"]
    birth_state = args.get("birth_state", "")
    
    return_year = args["return_year"]
    return_city = args.get("return_city", birth_city)
    return_state = args.get("return_state", birth_state)
    
    engine = SolarReturnEngine()
    result = engine.calculate(
        birth_dt=birth_dt,
        birth_city=birth_city,
        birth_state=birth_state,
        return_year=return_year,
        return_city=return_city,
        return_state=return_state
    )
    
    return result

async def handle_synastry(args: dict) -> dict:
    """Calculate synastry."""
    p1 = args["person1"]
    p2 = args["person2"]
    
    dt1 = datetime(p1["year"], p1["month"], p1["day"], p1["hour"], p1["minute"])
    dt2 = datetime(p2["year"], p2["month"], p2["day"], p2["hour"], p2["minute"])
    
    calc = ChartCalculator()
    chart1 = calc.calculate_chart(dt1, p1["city"], p1.get("state", ""))
    chart2 = calc.calculate_chart(dt2, p2["city"], p2.get("state", ""))
    
    engine = SynastryEngine()
    result = engine.compare(chart1, chart2)
    
    return result

async def handle_planetary_hour(args: dict) -> dict:
    """Get planetary hour."""
    city = args["city"]
    state = args.get("state", "")
    
    time_str = args.get("time")
    if time_str:
        dt = datetime.fromisoformat(time_str)
    else:
        dt = datetime.now()
    
    lat, lon = get_coordinates(city, state)
    
    calc = PlanetaryHourCalculator()
    result = calc.get_planetary_hour(dt, lat, lon)
    
    return result

# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Run the MCP server."""
    logger.info("Starting Astrology MCP Server...")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
