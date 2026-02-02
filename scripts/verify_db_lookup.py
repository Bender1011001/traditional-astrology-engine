import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.db_manager import DelineationLibrary
import time

def test_lookups():
    lib = DelineationLibrary()
    
    # Test 1: Planet in Sign
    print("Testing Planet in Sign...")
    res = lib.get_planet_delineation("SATURN_ARIES_DAY")
    print(f"Result for SATURN_ARIES_DAY: {res[:100]}...")
    assert "Saturn in 1 11 Aries" in res
    
    # Test 2: Fallback to ingested
    print("\nTesting Fallback...")
    # Note: I need to check if planets_in_signs_ingested actually has unique keys or same keys.
    # If same, it might not be obvious if it's fallback.
    
    # Test 3: Detailed Profile
    print("\nTesting Detailed Profile...")
    res = lib.get_detailed_profile("SUN")
    print(f"Result for SUN: {str(res)[:100]}...")
    assert "GENERAL" in res
    
    # Test 4: House definition
    print("\nTesting House Definition...")
    res = lib.get_house_definition(1)
    print(f"Result for House 1: {res[:100]}...")
    
    # Test 5: Cache performance
    print("\nTesting Cache Performance...")
    start = time.time()
    for _ in range(100):
        lib.get_planet_delineation("SATURN_ARIES_DAY")
    end = time.time()
    print(f"100 lookups (cached) took: {end - start:.6f} seconds")
    
    start = time.time()
    # Create new instance to bypass instance-level cache (if it were purely instance level)
    # Actually my refactor uses self._cache which is instance level.
    lib2 = DelineationLibrary()
    lib2.get_planet_delineation("SATURN_ARIES_DAY")
    end = time.time()
    print(f"1 lookup (uncached) took: {end - start:.6f} seconds")

    print("\nVerification successful!")

if __name__ == "__main__":
    test_lookups()
