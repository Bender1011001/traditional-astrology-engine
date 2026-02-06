import re
import json
import os

# Paths
DATA_DIR = "src/database/data"
CHUNKS_DIR = "binder_chunks"

PLANETS_SIGNS_FILE = os.path.join(DATA_DIR, "planets_in_signs.json")
PLANETS_HOUSES_FILE = os.path.join(DATA_DIR, "planets_in_houses.json")
DETAILED_DELINEATIONS_FILE = os.path.join(DATA_DIR, "detailed_delineations.json")

PLANETS = ["SATURN", "JUPITER", "MARS", "SUN", "VENUS", "MERCURY", "MOON"]
SIGNS = ["ARIES", "TAURUS", "GEMINI", "CANCER", "LEO", "VIRGO", "LIBRA", "SCORPIO", "SAGITTARIUS", "CAPRICORN", "AQUARIUS", "PISCES"]
HOUSES = [str(i) for i in range(1, 13)]

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def clean_text(text):
    if not text: return ""
    # Remove BOM if present
    text = text.replace('\ufeff', '')
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_planets_in_signs(files):
    new_data = {}
    for filename in files:
        path = os.path.join(CHUNKS_DIR, filename)
        if not os.path.exists(path): continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for "Planet in Sign" headers
        # Use a regex that captures the planet, sign, and the text following it until the next header
        # Added support for \ufeff and loose spacing
        # Note: Added \ufeff? to the lookahead
        # Using [^\n]* for interpretation if it's short, or re.DOTALL
        # Improved lookahead to avoid stopping on "NOT FOUND"
        pattern = r"([A-Z][a-z]+)\s+in\s+(?:the\s+)?(Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|Sagittarius|Capricorn|Aquarius|Pisces).*?Interpretation:\s*(.*?)(?=\n\s*\ufeff?(?:Saturn|Jupiter|Mars|Sun|Venus|Mercury|Moon)\s+in|\n\s*\ufeff?[A-Z][a-z]+\s+Table|\n\s*Table\s+\d|\n\s*Part\s+\d|$)"
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        
        for planet, sign, interp in matches:
            p_upper = planet.upper()
            s_upper = sign.upper()
            if p_upper in PLANETS and s_upper in SIGNS:
                text = clean_text(interp)
                if text and "NOT FOUND IN SOURCES" not in text.upper():
                    key_day = f"{p_upper}_{s_upper}_DAY"
                    key_night = f"{p_upper}_{s_upper}_NIGHT"
                    new_data[key_day] = text
                    new_data[key_night] = text
    return new_data

def parse_planets_in_houses(files):
    new_data = {}
    for filename in files:
        path = os.path.join(CHUNKS_DIR, filename)
        if not os.path.exists(path): continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split by house sections
        # The First House (Ascendant / Life)
        house_sections = re.split(r"The\s+(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth)\s+House", content)
        
        ordinals = {
            "First": "1", "Second": "2", "Third": "3", "Fourth": "4", "Fifth": "5", "Sixth": "6",
            "Seventh": "7", "Eighth": "8", "Ninth": "9", "Tenth": "10", "Eleventh": "11", "Twelfth": "12"
        }

        for i in range(1, len(house_sections), 2):
            house_num = ordinals.get(house_sections[i])
            house_content = house_sections[i+1]
            
            # Better planet parsing for messy tables
            # Find a planet name, then look for the first quote following it before the next planet name or section end
            for planet in PLANETS:
                # Regex for planet name at start of line or following some spaces
                # Then anything until a quote
                p_pattern = rf"(?:^|\n)\s*{planet.capitalize()}\s+.*?[\"“](.*?)[\"”]"
                match = re.search(p_pattern, house_content, re.DOTALL | re.IGNORECASE)
                if match:
                    key = f"{planet}_{house_num}"
                    new_data[key] = clean_text(match.group(1))
    return new_data

def parse_detailed_delineations(nodes_files, stars_files):
    # This updates detailed_delineations.json for Nodes and Stars
    # Nodes: Digestive Model
    # Stars: Glory vs Nemesis
    
    nodes_data = {}
    for filename in nodes_files:
        path = os.path.join(CHUNKS_DIR, filename)
        if not os.path.exists(path): continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for planet sections in Node chapters
        # e.g. "4. Venus: The Engine of Eros and Desire"
        planet_node_pattern = r"\d\.\s+(Saturn|Jupiter|Mars|Sun|Venus|Mercury|Moon):\s+The\s+Engine\s+of\s+.*?(?=Condition|Mechanics)(.*?)(\d\.\s+(?:Saturn|Jupiter|Mars|Sun|Venus|Mercury|Moon):|$)"
        planet_matches = re.findall(planet_node_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for planet, body, _ in planet_matches:
            p_upper = planet.upper()
            if p_upper in PLANETS:
                # Extract North Node (Caput) and South Node (Cauda)
                # Delineation column typically has both
                # This is tricky because it's a multi-column table in the PDF/Text
                
                # Try to find Delineation section
                delin_match = re.search(r"Delineation\s+(.*?)(?=The Danger|Bonus|$)", body, re.DOTALL)
                if delin_match:
                    text = delin_match.group(1)
                    # Often split into two halves or specific markers
                    # We'll try to find "Bonatti:" or just split by large whitespace
                    parts = re.split(r"\s{5,}", text.strip())
                    if len(parts) >= 2:
                        nodes_data[p_upper] = {
                            "NORTH_NODE": clean_text(parts[0]),
                            "SOUTH_NODE": clean_text(parts[1])
                        }

    stars_data = {}
    for filename in stars_files:
        path = os.path.join(CHUNKS_DIR, filename)
        if not os.path.exists(path): continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Royal Stars
        star_names = ["Regulus", "Aldebaran", "Antares", "Fomalhaut"]
        for star in star_names:
            # Find the section starting with the star name
            # Look for a header like "1. Aldebaran" or "2. Regulus"
            star_section_pattern = rf"\d\.\s+{star}.*?(?=Forensic Delineation \(Glory\))(.*?)(?=\n\d\.\s+|$|V\.\s+The\s+Caput\s+Algol)"
            section_match = re.search(star_section_pattern, content, re.DOTALL | re.IGNORECASE)
            if section_match:
                section_content = section_match.group(1)
                glory_match = re.search(r"Forensic Delineation \(Glory\):\s*(.*?)(?=The Nemesis|$)", section_content, re.DOTALL | re.IGNORECASE)
                nemesis_match = re.search(r"The Nemesis \(.*?\):\s*(.*?)(?=●|Table|Conclusion|$)", section_content, re.DOTALL | re.IGNORECASE)
                
                if glory_match and nemesis_match:
                    stars_data[star.upper()] = {
                        "GLORY": clean_text(glory_match.group(1)),
                        "NEMESIS": clean_text(nemesis_match.group(1))
                    }
            
        # Algol
        if "ALGOL" not in stars_data:
                # Special parsing for Algol since it might not use "Glory/Nemesis" labels exactly
                algol_text = ""
                # Look for the section V. The Caput Algol
                algol_section = re.search(r"V\.\s+The\s+Caput\s+Algol(.*?)(?=VI\.|$)", content, re.DOTALL)
                if algol_section:
                    stars_data["ALGOL"] = {
                        "DESCRIPTION": clean_text(algol_section.group(1))
                    }

    return {"NODES": nodes_data, "STARS": stars_data}

def merge_data(existing, new):
    count = 0
    for key, value in new.items():
        # Overwrite if existing is empty, missing, or a placeholder
        # OR if the existing data seems corrupted (too short or contains \ufeff)
        is_placeholder = key not in existing or "NOT FOUND IN SOURCES" in existing[key].upper() or "Delineation not found" in existing[key]
        is_corrupted = key in existing and ("\ufeff" in existing[key] or (len(existing[key]) < 10 and existing[key].endswith("NOT")))
        
        if is_placeholder or is_corrupted:
            if value and "NOT FOUND IN SOURCES" not in value.upper():
                existing[key] = value
                count += 1
        elif value and len(value) > len(existing.get(key, "")):
            # If we found a longer/better description, use it
            existing[key] = value
            count += 1
    return existing, count

def main():
    print("Ingesting Codex data...")
    
    # 1. Planets in Signs
    existing_p_signs = load_json(PLANETS_SIGNS_FILE)
    new_p_signs = parse_planets_in_signs(["Binder1_part_001.txt", "Binder1_part_002.txt"])
    updated_p_signs, p_signs_count = merge_data(existing_p_signs, new_p_signs)
    save_json(PLANETS_SIGNS_FILE, updated_p_signs)
    print(f"Updated {p_signs_count} entries in planets_in_signs.json")
    
    # 2. Planets in Houses
    existing_p_houses = load_json(PLANETS_HOUSES_FILE)
    new_p_houses = parse_planets_in_houses(["Binder1_part_003.txt"])
    updated_p_houses, p_houses_count = merge_data(existing_p_houses, new_p_houses)
    save_json(PLANETS_HOUSES_FILE, updated_p_houses)
    print(f"Updated {p_houses_count} entries in planets_in_houses.json")
    
    # 3. Detailed Delineations (Nodes and Stars)
    existing_detailed = load_json(DETAILED_DELINEATIONS_FILE)
    new_detailed = parse_detailed_delineations(["Binder1_part_029.txt", "Binder1_part_030.txt"], ["Binder1_part_030.txt", "Binder1_part_031.txt"])
    
    # Merge detailed
    detailed_count = 0
    if "NODES" not in existing_detailed: existing_detailed["NODES"] = {}
    for planet, data in new_detailed["NODES"].items():
        existing_detailed["NODES"][planet] = data
        detailed_count += 1
        
    if "STARS" not in existing_detailed: existing_detailed["STARS"] = {}
    for star, data in new_detailed["STARS"].items():
        existing_detailed["STARS"][star] = data
        detailed_count += 1
        
    save_json(DETAILED_DELINEATIONS_FILE, existing_detailed)
    print(f"Updated {detailed_count} entries in detailed_delineations.json")
    
    print("Ingestion complete.")
    print(f"Summary: Total {p_signs_count + p_houses_count + detailed_count} new delineations added.")

if __name__ == "__main__":
    main()
