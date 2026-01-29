"""
Enhanced Delineation Extraction Script v2

This version handles the single-line format of missing-data.txt
and extracts all structured delineations for the database.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
BINDER_DIR = PROJECT_ROOT / "binder_chunks"
MISSING_DATA_FILE = PROJECT_ROOT / "missing-data.txt"
OUTPUT_DIR = PROJECT_ROOT / "src" / "database" / "data"

PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


def normalize_key(planet: str, sign: str, sect: str) -> str:
    return f"{planet.upper()}_{sign.upper()}_{sect.upper()}"


def normalize_house_key(planet: str, house: int) -> str:
    return f"{planet.upper()}_{house}"


def extract_planets_in_signs_from_missing_data(content: str) -> Dict[str, str]:
    """
    Extract all Planet in Sign delineations with Day/Night variations.
    """
    results = {}
    
    # Patterns for different section formats
    patterns = [
        # Pattern: Saturn in Gemini ... Diurnal Geniture (Day Chart): Delineation: <text> ... Nocturnal Geniture (Night Chart): Delineation: <text>
        (r'(\w+)\s+in\s+(\w+)\s*\([^)]+\).*?Diurnal\s+Geniture\s*\(Day\s+Chart\)\s*:\s*Delineation:\s*([^.]+(?:\.[^.]+)*?)(?:Analysis:|Outcome:|Nocturnal)',
         r'Nocturnal\s+Geniture\s*\(Night\s+Chart\)\s*:\s*Delineation:\s*([^.]+(?:\.[^.]+)*?)(?:Analysis:|Outcome:|(?:\d+\.\d+)|(?:[A-Z][a-z]+\s+in\s+[A-Z][a-z]+))'),
    ]
    
    # Find all planet-sign section headers
    # E.g., "Saturn in Gemini (The Domicile of Mercury)"
    planet_sign_headers = list(re.finditer(
        r'(?:2\.\d+\s+)?(?P<planet>Saturn|Jupiter|Mars|Sun|Venus|Mercury|Moon)\s*\((?:[^)]+)\)(?P<sign_context>[^2]*?)(?=2\.\d+\s+|$)',
        content, re.IGNORECASE
    ))
    
    # Better approach: extract explicitly formatted delineations
    # Pattern for planet/sign with Diurnal/Nocturnal blocks
    
    for planet in PLANETS:
        for sign in SIGNS:
            # Search for "Planet in Sign" followed by sect delineations
            pattern = rf'{planet}\s+in\s+{sign}\s*\([^)]+\)[^D]*?Diurnal\s+Geniture\s*\(Day\s+Chart\)\s*:\s*Delineation:\s*(.+?)(?:Analysis:|Outcome:|Nocturnal)'
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            
            if match:
                day_text = match.group(1).strip()
                # Clean up quotes
                day_text = day_text.strip('"').strip()
                day_text = re.sub(r'\s+', ' ', day_text)
                
                if len(day_text) > 30:
                    key = normalize_key(planet, sign, "Day")
                    results[key] = day_text
            
            # Night pattern
            pattern_night = rf'{planet}\s+in\s+{sign}\s*\([^)]+\).+?Nocturnal\s+Geniture\s*\(Night\s+Chart\)\s*:\s*Delineation:\s*(.+?)(?:Analysis:|Outcome:|(?:\d+\.\d+)|(?:{"|".join(PLANETS)}\s+in\s+))'
            match = re.search(pattern_night, content, re.IGNORECASE | re.DOTALL)
            
            if match:
                night_text = match.group(1).strip()
                night_text = night_text.strip('"').strip()
                night_text = re.sub(r'\s+', ' ', night_text)
                
                if len(night_text) > 30:
                    key = normalize_key(planet, sign, "Night")
                    results[key] = night_text
    
    return results


def extract_simpler_format(content: str) -> Dict[str, str]:
    """
    Extract delineations with simpler Diurnal/Nocturnal markers.
    """
    results = {}
    
    # Find all sections like "Sun in Taurus" followed by Diurnal:/Nocturnal: blocks
    for planet in PLANETS:
        for sign in SIGNS:
            # Look for simpler format: "Sun in Taurus" then "Diurnal Geniture:" or just "Diurnal:"
            base_pattern = rf'{planet}\s+in\s+{sign}'
            
            # Find the section start
            section_match = re.search(base_pattern, content, re.IGNORECASE)
            if not section_match:
                continue
            
            # Get text from this point to next planet-sign header
            start_pos = section_match.start()
            
            # Find end of section (next planet in sign header)
            next_planet_pattern = rf'(?:{"|".join(PLANETS)})\s+in\s+(?:{"|".join(SIGNS)})'
            remaining_text = content[start_pos + len(section_match.group()):]
            next_match = re.search(next_planet_pattern, remaining_text, re.IGNORECASE)
            
            if next_match:
                section_text = remaining_text[:next_match.start()]
            else:
                section_text = remaining_text[:2000]  # Limit search
            
            # Look for Diurnal delineation
            day_match = re.search(
                r'Diurnal(?:\s+Geniture)?(?:\s*\(Day\s+Chart\))?\s*:\s*(?:Delineation:\s*)?(.+?)(?=Nocturnal|Analysis:|Outcome:|$)',
                section_text, re.IGNORECASE | re.DOTALL
            )
            
            if day_match:
                day_text = day_match.group(1).strip()
                day_text = re.sub(r'\s+', ' ', day_text)
                if len(day_text) > 30 and len(day_text) < 2000:
                    key = normalize_key(planet, sign, "Day")
                    if key not in results:
                        results[key] = day_text
            
            # Look for Nocturnal delineation
            night_match = re.search(
                r'Nocturnal(?:\s+Geniture)?(?:\s*\(Night\s+Chart\))?\s*:\s*(?:Delineation:\s*)?(.+?)(?=Diurnal|Analysis:|Outcome:|(?:\d+\.\d+)|$)',
                section_text, re.IGNORECASE | re.DOTALL
            )
            
            if night_match:
                night_text = night_match.group(1).strip()
                night_text = re.sub(r'\s+', ' ', night_text)
                if len(night_text) > 30 and len(night_text) < 2000:
                    key = normalize_key(planet, sign, "Night")
                    if key not in results:
                        results[key] = night_text
    
    return results


def extract_planets_in_houses(content: str) -> Dict[str, str]:
    """
    Extract planets in houses delineations from Part II.
    """
    results = {}
    
    # Find Part II section
    part2_match = re.search(r'Part II:\s*Planets in the Houses', content, re.IGNORECASE)
    if not part2_match:
        part2_match = re.search(r'3\.\s*Part II', content, re.IGNORECASE)
    
    if not part2_match:
        print("  Warning: Could not find Part II section")
        return results
    
    start_pos = part2_match.start()
    
    # Find end (Part III or Part IV)
    end_match = re.search(r'(?:Part III|Part IV|4\.\s*Part III)', content[start_pos:], re.IGNORECASE)
    if end_match:
        section_text = content[start_pos:start_pos + end_match.start()]
    else:
        section_text = content[start_pos:start_pos + 20000]
    
    # Extract house sections
    for house_num in range(1, 13):
        # Find house header e.g., "House 5:" or "House 5 ("
        house_pattern = rf'House\s+{house_num}\s*[:\(]'
        house_match = re.search(house_pattern, section_text, re.IGNORECASE)
        
        if not house_match:
            continue
        
        # Get text for this house
        house_start = house_match.start()
        next_house_match = re.search(rf'House\s+{house_num + 1}\s*[:\(]', section_text[house_start + 10:], re.IGNORECASE)
        
        if next_house_match:
            house_text = section_text[house_start:house_start + 10 + next_house_match.start()]
        else:
            house_text = section_text[house_start:house_start + 3000]
        
        # Find planet delineations within this house
        for planet in PLANETS:
            # Pattern: "Planet in the Nth:" or "Planet in the Nth House:"
            planet_pattern = rf'{planet}\s+in\s+the\s+\d+(?:st|nd|rd|th)?[:\s]+(?:Delineation:\s*)?"?(.+?)"?(?={"|".join(PLANETS)}\s+in\s+|Condition:|House\s+\d+|$)'
            
            planet_match = re.search(planet_pattern, house_text, re.IGNORECASE | re.DOTALL)
            
            if planet_match:
                delineation = planet_match.group(1).strip()
                delineation = delineation.strip('"')
                delineation = re.sub(r'\s+', ' ', delineation)
                
                if len(delineation) > 20 and len(delineation) < 1500:
                    key = normalize_house_key(planet, house_num)
                    results[key] = delineation
    
    return results


def extract_solar_return_moon(content: str) -> Dict[str, str]:
    """
    Extract Solar Return Moon in natal houses delineations.
    """
    results = {}
    
    # Find Part III or Solar Return section
    part3_match = re.search(r'(?:Part III|4\.\s*Part III|Solar Return Moon)', content, re.IGNORECASE)
    if not part3_match:
        return results
    
    start_pos = part3_match.start()
    section_text = content[start_pos:start_pos + 10000]
    
    ordinals = {
        1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th",
        7: "7th", 8: "8th", 9: "9th", 10: "10th", 11: "11th", 12: "12th"
    }
    
    for house_num in range(1, 13):
        # Pattern: "In Natal 1st House" or "In Natal 1st:"
        pattern = rf'In\s+Natal\s+{house_num}(?:st|nd|rd|th)?\s*(?:House)?\s*(.+?)(?=In\s+Natal\s+\d+|Important\s+Note|5\.\s*Conclusion|$)'
        
        match = re.search(pattern, section_text, re.IGNORECASE | re.DOTALL)
        
        if match:
            delineation = match.group(1).strip()
            delineation = re.sub(r'\s+', ' ', delineation)
            
            if len(delineation) > 20:
                key = f"SR_MOON_NATAL_{house_num}"
                results[key] = delineation
    
    return results


def load_json(filepath: Path) -> Dict:
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_json(data: Dict, filepath: Path):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"  Saved {len(data)} entries to {filepath.name}")


def main():
    print("=" * 60)
    print("DELINEATION EXTRACTION v2")
    print("=" * 60)
    
    # Load existing data
    print("\n1. Loading existing database...")
    existing_signs = load_json(OUTPUT_DIR / "planets_in_signs.json")
    existing_houses = load_json(OUTPUT_DIR / "planets_in_houses.json")
    existing_sr = load_json(OUTPUT_DIR / "solar_return_moon_houses.json")
    
    print(f"  Existing: {len(existing_signs)} signs, {len(existing_houses)} houses, {len(existing_sr)} SR Moon")
    
    # Read missing-data.txt
    print("\n2. Reading missing-data.txt...")
    with open(MISSING_DATA_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f"  File size: {len(content)} chars")
    
    # Extract planets in signs
    print("\n3. Extracting planets in signs...")
    new_signs = extract_planets_in_signs_from_missing_data(content)
    simple_signs = extract_simpler_format(content)
    
    # Merge
    for key, value in simple_signs.items():
        if key not in new_signs:
            new_signs[key] = value
    
    print(f"  Extracted: {len(new_signs)} new sign delineations")
    
    # Print what we found
    if new_signs:
        print("  Found:")
        for key in sorted(new_signs.keys())[:10]:
            print(f"    - {key}: {new_signs[key][:60]}...")
    
    # Extract houses
    print("\n4. Extracting planets in houses...")
    new_houses = extract_planets_in_houses(content)
    print(f"  Extracted: {len(new_houses)} new house delineations")
    
    # Extract SR Moon
    print("\n5. Extracting Solar Return Moon...")
    new_sr = extract_solar_return_moon(content)
    print(f"  Extracted: {len(new_sr)} SR Moon delineations")
    
    # Merge with existing (prefer new high-quality data)
    print("\n6. Merging data...")
    
    merged_signs = existing_signs.copy()
    for key, value in new_signs.items():
        if value and len(value) > len(merged_signs.get(key, '')):
            merged_signs[key] = value
    
    merged_houses = existing_houses.copy()
    for key, value in new_houses.items():
        if value and len(value) > len(merged_houses.get(key, '')):
            merged_houses[key] = value
    
    merged_sr = existing_sr.copy()
    for key, value in new_sr.items():
        if value and len(value) > len(merged_sr.get(key, '')):
            merged_sr[key] = value
    
    # Validate
    print("\n7. Coverage validation...")
    expected_signs = 7 * 12 * 2  # 7 planets × 12 signs × 2 sects
    expected_houses = 7 * 12     # 7 planets × 12 houses
    
    print(f"  Signs: {len(merged_signs)}/{expected_signs} ({100*len(merged_signs)//expected_signs}%)")
    print(f"  Houses: {len(merged_houses)}/{expected_houses} ({100*len(merged_houses)//expected_houses}%)")
    print(f"  SR Moon: {len(merged_sr)}/12 ({100*len(merged_sr)//12}%)")
    
    # Check for Moon_Pisces specifically
    if "MOON_PISCES_DAY" not in merged_signs:
        print("  ⚠️  Still missing MOON_PISCES_DAY")
    if "MOON_PISCES_NIGHT" not in merged_signs:
        print("  ⚠️  Still missing MOON_PISCES_NIGHT")
    
    # Save
    print("\n8. Saving updated data...")
    save_json(merged_signs, OUTPUT_DIR / "planets_in_signs.json")
    save_json(merged_houses, OUTPUT_DIR / "planets_in_houses.json")
    save_json(merged_sr, OUTPUT_DIR / "solar_return_moon_houses.json")
    
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
