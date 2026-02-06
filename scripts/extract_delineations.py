"""
Comprehensive Delineation Extraction Script

Parses all binder chunks and research documents to extract:
1. Planets in Signs (with Day/Night sect variations)
2. Planets in Houses
3. Solar Return Moon positions
4. Fixed Star delineations
5. Detailed planet profiles

Outputs structured JSON files for the database.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
BINDER_DIR = PROJECT_ROOT / "binder_chunks"
DOCS_DIR = PROJECT_ROOT / "docs" / "research"
MISSING_DATA_FILE = PROJECT_ROOT / "missing-data.txt"
OUTPUT_DIR = PROJECT_ROOT / "src" / "database" / "data"

# Planet and Sign definitions
PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SECTS = ["Day", "Night"]


def normalize_key(planet: str, sign: str, sect: str) -> str:
    """Generate a database key like SATURN_GEMINI_DAY"""
    return f"{planet.upper()}_{sign.upper()}_{sect.upper()}"


def normalize_house_key(planet: str, house: int) -> str:
    """Generate a house key like SATURN_1"""
    return f"{planet.upper()}_{house}"


def extract_sect_delineations_from_missing_data(content: str) -> Dict[str, str]:
    """
    Parse the missing-data.txt file for sect-specific delineations.
    Format expected:
    Saturn in Gemini (The Domicile of Mercury)
    Diurnal Geniture (Day Chart):
    Delineation: <text>
    Nocturnal Geniture (Night Chart):
    Delineation: <text>
    """
    results = {}
    
    # Pattern to match planet in sign headers
    planet_sign_pattern = re.compile(
        r'(?P<planet>Saturn|Jupiter|Mars|Sun|Venus|Mercury|Moon)\s+in\s+(?P<sign>Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces)',
        re.IGNORECASE
    )
    
    # Split content into sections by planet-sign headers
    sections = re.split(r'\n(?=(?:Saturn|Jupiter|Mars|Sun|Venus|Mercury|Moon)\s+in\s+(?:Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces))', content)
    
    for section in sections:
        if not section.strip():
            continue
            
        # Find planet and sign
        header_match = planet_sign_pattern.search(section)
        if not header_match:
            continue
            
        planet = header_match.group('planet').title()
        sign = header_match.group('sign').title()
        
        # Extract Day delineation
        day_match = re.search(
            r'Diurnal\s+Geniture\s*\(Day\s+Chart\)\s*:\s*Delineation:\s*(.+?)(?=Nocturnal\s+Geniture|Analysis:|Outcome:|$)',
            section,
            re.DOTALL | re.IGNORECASE
        )
        if day_match:
            delineation = day_match.group(1).strip()
            # Clean up the text
            delineation = re.sub(r'\s+', ' ', delineation)
            key = normalize_key(planet, sign, "Day")
            results[key] = delineation
        
        # Extract Night delineation
        night_match = re.search(
            r'Nocturnal\s+Geniture\s*\(Night\s+Chart\)\s*:\s*Delineation:\s*(.+?)(?=Analysis:|Outcome:|$)',
            section,
            re.DOTALL | re.IGNORECASE
        )
        if night_match:
            delineation = night_match.group(1).strip()
            delineation = re.sub(r'\s+', ' ', delineation)
            key = normalize_key(planet, sign, "Night")
            results[key] = delineation
    
    return results


def extract_house_delineations_from_missing_data(content: str) -> Dict[str, str]:
    """
    Extract Planets in Houses delineations from Part II of missing-data.txt
    """
    results = {}
    
    # Find the section for planets in houses
    house_section_match = re.search(
        r'Part II:\s*Planets\s+in\s+the\s+Houses(.+?)(?=Part III:|$)',
        content,
        re.DOTALL | re.IGNORECASE
    )
    
    if not house_section_match:
        return results
    
    house_content = house_section_match.group(1)
    
    # Pattern for house headers like "House 2:" or "House 5:"
    house_pattern = re.compile(r'House\s+(\d+):', re.IGNORECASE)
    
    # Split by house headers
    house_sections = re.split(r'\n(?=House\s+\d+:)', house_content)
    
    for section in house_sections:
        if not section.strip():
            continue
            
        house_match = house_pattern.search(section)
        if not house_match:
            continue
            
        house_num = int(house_match.group(1))
        
        # Find planet delineations within this house section
        for planet in PLANETS:
            planet_pattern = re.compile(
                rf'{planet}\s+in\s+the\s+\d+(?:st|nd|rd|th)?\s*:\s*Delineation:\s*"?(.+?)"?(?=\n(?:Saturn|Jupiter|Mars|Sun|Venus|Mercury|Moon)\s+in\s+the|\nHouse\s+\d+:|$)',
                re.DOTALL | re.IGNORECASE
            )
            
            planet_match = planet_pattern.search(section)
            if planet_match:
                delineation = planet_match.group(1).strip()
                delineation = re.sub(r'\s+', ' ', delineation)
                key = normalize_house_key(planet, house_num)
                results[key] = delineation
    
    return results


def extract_solar_return_moon(content: str) -> Dict[str, str]:
    """
    Extract Solar Return Moon delineations from Part III
    """
    results = {}
    
    # Find Part III section
    sr_section_match = re.search(
        r'Part III:\s*Solar Return Moon(.+?)(?=Part IV:|Important Note|$)',
        content,
        re.DOTALL | re.IGNORECASE
    )
    
    if not sr_section_match:
        return results
    
    sr_content = sr_section_match.group(1)
    
    # Pattern for SR Moon positions
    for house_num in range(1, 13):
        pattern = re.compile(
            rf'In\s+Natal\s+{house_num}(?:st|nd|rd|th)?\s+House\s*(.+?)(?=In\s+Natal\s+\d+|$)',
            re.DOTALL | re.IGNORECASE
        )
        
        match = pattern.search(sr_content)
        if match:
            delineation = match.group(1).strip()
            delineation = re.sub(r'\s+', ' ', delineation)
            key = f"SR_MOON_NATAL_{house_num}"
            results[key] = delineation
    
    return results


def extract_from_binder_chunks() -> Dict[str, Dict]:
    """
    Parse all binder chunks for additional delineations.
    Returns a dictionary with categories: planets_signs, planets_houses, stars, etc.
    """
    results = {
        'planets_signs': {},
        'planets_houses': {},
        'stars': {},
        'aspects': {},
        'mundane': {}
    }
    
    binder_files = sorted(BINDER_DIR.glob("Binder1_part_*.txt"))
    
    for binder_file in binder_files:
        print(f"Processing {binder_file.name}...")
        
        try:
            with open(binder_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"  Error reading {binder_file.name}: {e}")
            continue
        
        # Extract planet-sign delineations from tables
        # Look for patterns like "Saturn in Aries" followed by interpretation text
        for planet in PLANETS:
            for sign in SIGNS:
                # Pattern 1: Table format "Saturn in Aries   Interpretation: ..."
                pattern1 = re.compile(
                    rf'{planet}\s+in\s+{sign}\s+(?:Interpretation:|Delineation:)?\s*["]?(.+?)["]?(?=\n{planet}\s+in\s+|\nTable|\n\n|\Z)',
                    re.DOTALL | re.IGNORECASE
                )
                
                match = pattern1.search(content)
                if match:
                    text = match.group(1).strip()
                    text = re.sub(r'\s+', ' ', text)
                    if len(text) > 20:  # Filter out short fragments
                        # For now, use both day and night if no sect specified
                        for sect in SECTS:
                            key = normalize_key(planet, sign, sect)
                            if key not in results['planets_signs']:
                                results['planets_signs'][key] = text
        
        # Extract fixed star delineations
        star_names = ['Regulus', 'Aldebaran', 'Antares', 'Fomalhaut', 'Algol', 'Spica', 'Betelgeuse']
        for star in star_names:
            # Look for star sections
            star_pattern = re.compile(
                rf'\b{star}\b[:\s]+(.{{100,1000}}?)(?=\n\n|\n[A-Z][a-z]+:|\Z)',
                re.DOTALL | re.IGNORECASE
            )
            
            match = star_pattern.search(content)
            if match:
                text = match.group(1).strip()
                text = re.sub(r'\s+', ' ', text)
                if star not in results['stars']:
                    results['stars'][star] = text
    
    return results


def merge_delineations(existing: Dict, new: Dict, prefer_new: bool = False) -> Dict:
    """
    Merge new delineations into existing, optionally preferring new values.
    """
    merged = existing.copy()
    
    for key, value in new.items():
        if key not in merged:
            merged[key] = value
        elif prefer_new and value and len(value) > len(merged.get(key, '')):
            merged[key] = value
    
    return merged


def load_existing_json(filepath: Path) -> Dict:
    """Load existing JSON file or return empty dict."""
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"  Warning: Could not load {filepath}: {e}")
    return {}


def save_json(data: Dict, filepath: Path):
    """Save dictionary to JSON file with pretty formatting."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"  Saved {len(data)} entries to {filepath.name}")


def validate_coverage(data: Dict, category: str):
    """Check and report coverage of delineations."""
    if category == 'planets_signs':
        expected = set()
        for planet in PLANETS:
            for sign in SIGNS:
                for sect in SECTS:
                    expected.add(normalize_key(planet, sign, sect))
        
        actual = set(data.keys())
        missing = expected - actual
        
        print(f"\n  Coverage: {len(actual)}/{len(expected)} ({100*len(actual)//len(expected)}%)")
        if missing:
            print(f"  Missing: {sorted(list(missing))[:10]}...")
    
    elif category == 'planets_houses':
        expected = set()
        for planet in PLANETS:
            for house in range(1, 13):
                expected.add(normalize_house_key(planet, house))
        
        actual = set(data.keys())
        missing = expected - actual
        
        print(f"\n  Coverage: {len(actual)}/{len(expected)} ({100*len(actual)//len(expected)}%)")
        if missing:
            print(f"  Missing: {sorted(list(missing))[:10]}...")


def main():
    print("=" * 60)
    print("DELINEATION EXTRACTION SCRIPT")
    print("=" * 60)
    
    # Load existing data
    print("\n1. Loading existing database files...")
    existing_signs = load_existing_json(OUTPUT_DIR / "planets_in_signs.json")
    existing_houses = load_existing_json(OUTPUT_DIR / "planets_in_houses.json")
    existing_sr_moon = load_existing_json(OUTPUT_DIR / "solar_return_moon_houses.json")
    print(f"  Loaded {len(existing_signs)} sign entries, {len(existing_houses)} house entries")
    
    # Process missing-data.txt (high quality source)
    print("\n2. Extracting from missing-data.txt...")
    if MISSING_DATA_FILE.exists():
        with open(MISSING_DATA_FILE, 'r', encoding='utf-8') as f:
            missing_data_content = f.read()
        
        new_signs = extract_sect_delineations_from_missing_data(missing_data_content)
        new_houses = extract_house_delineations_from_missing_data(missing_data_content)
        new_sr_moon = extract_solar_return_moon(missing_data_content)
        
        print(f"  Extracted: {len(new_signs)} signs, {len(new_houses)} houses, {len(new_sr_moon)} SR Moon")
    else:
        print("  missing-data.txt not found!")
        new_signs, new_houses, new_sr_moon = {}, {}, {}
    
    # Process binder chunks
    print("\n3. Extracting from binder chunks...")
    binder_data = extract_from_binder_chunks()
    print(f"  Extracted: {len(binder_data['planets_signs'])} signs, {len(binder_data['stars'])} stars")
    
    # Merge all sources (prefer new high-quality extractions)
    print("\n4. Merging data sources...")
    
    # For signs: prefer missing-data.txt > binder > existing
    merged_signs = merge_delineations(existing_signs, binder_data['planets_signs'])
    merged_signs = merge_delineations(merged_signs, new_signs, prefer_new=True)
    
    # For houses: prefer missing-data.txt > existing
    merged_houses = merge_delineations(existing_houses, new_houses, prefer_new=True)
    
    # For SR Moon: prefer new extractions
    merged_sr_moon = merge_delineations(existing_sr_moon, new_sr_moon, prefer_new=True)
    
    # Validate coverage
    print("\n5. Validating coverage...")
    print("  Planets in Signs:")
    validate_coverage(merged_signs, 'planets_signs')
    print("  Planets in Houses:")
    validate_coverage(merged_houses, 'planets_houses')
    
    # Save updated files
    print("\n6. Saving updated database files...")
    save_json(merged_signs, OUTPUT_DIR / "planets_in_signs.json")
    save_json(merged_houses, OUTPUT_DIR / "planets_in_houses.json")
    save_json(merged_sr_moon, OUTPUT_DIR / "solar_return_moon_houses.json")
    
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
