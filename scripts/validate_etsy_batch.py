import asyncio
import os
import sys
import random
from datetime import datetime, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.services.engine_bridge import generate_full_nativity_async

async def main():
    print("Generating 50 mock birth records for Etsy Validation...")
    
    cities = ["New York", "London", "Tokyo", "Paris", "Berlin", "Sydney", "Toronto", "Chicago", "Los Angeles", "Rome"]
    states = ["NY", "UK", "JP", "FR", "DE", "NSW", "ON", "IL", "CA", "IT"]
    
    mock_records = []
    base_date = datetime(1980, 1, 1)
    
    for i in range(50):
        # Randomize birth dates
        bdate = base_date + timedelta(days=random.randint(0, 10000))
        btime = f"{random.randint(0,23):02d}:{random.randint(0,59):02d}"
        city_idx = random.randint(0, len(cities)-1)
        
        mock_records.append({
            "name": f"EtsyClient_{i}",
            "date": bdate.strftime("%Y-%m-%d"),
            "time": btime,
            "city": cities[city_idx],
            "state": states[city_idx],
            "house_system": "W",
            "zodiac_system": "tropical"
        })

    print(f"Starting batch processing of {len(mock_records)} charts...")
    
    success = 0
    failures = 0
    
    start_time = datetime.now()
    
    for idx, req in enumerate(mock_records):
        try:
            # Simulate the batch processing loop
            result = await generate_full_nativity_async(
                date_str=req["date"],
                time_str=req["time"],
                city=req["city"],
                state=req["state"],
                name=req["name"],
                house_system=req["house_system"],
                zodiac_system=req["zodiac_system"],
                ayanamsa=None
            )
            
            if "error" in result:
                print(f"[FAIL] {req['name']}: {result['error']}")
                failures += 1
            else:
                success += 1
                if idx % 10 == 0:
                    print(f"Processed {idx}/{len(mock_records)}...")
        except Exception as e:
            print(f"[ERROR] {req['name']} threw exception: {e}")
            failures += 1

    duration = (datetime.now() - start_time).total_seconds()
    
    print("\n--- BATCH PROCESS REPORT ---")
    print(f"Total charts processed: {len(mock_records)}")
    print(f"Success: {success}")
    print(f"Failures: {failures}")
    print(f"Total time: {duration:.2f} seconds")
    print(f"Average time per chart: {duration/len(mock_records):.2f} seconds")
    
    if failures == 0:
        print("\nVALDATION SUCCESSFUL! The backend engine scales to handle Etsy bulk orders safely.")
    else:
        print("\nVALIDATION FAILED! Please check Swiss Ephemeris configuration or timeout settings.")

if __name__ == "__main__":
    asyncio.run(main())
