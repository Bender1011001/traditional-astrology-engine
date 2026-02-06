
import sys
import os
import asyncio
from datetime import datetime

import logging
logging.basicConfig(level=logging.ERROR)

# Add src to path
sys.path.insert(0, os.getcwd())

from src.engine.sovereign_engine import SovereignEngine

async def test_crash():
    print("Testing Sovereign Engine Crash...")
    try:
        result = SovereignEngine.generate_full_nativity(
            date_str="1996-08-13",
            time_str="07:18",
            city="Fairfield, CA",
            state="CA",
            house_system="W",
            zodiac_system="tropical",
            ayanamsa=None
        )
        import json
        json_str = json.dumps(result, default=str, indent=2, ensure_ascii=True) 
        print("Result:", json_str)
        if "error" in result:
            print("Error reported:", result["error"])
    except Exception as e:
        print("CRASHED!")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_crash())
