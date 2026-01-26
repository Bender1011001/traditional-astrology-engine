
import os
import re
import json
import glob

BINDER_DIR = r'e:\code.projects\astrology\binder_chunks'
OUTPUT_DIR = r'e:\code.projects\astrology\src\database\data'

def clean_text(text):
    # Remove newlines and extra spaces, handle hyphenation if possible
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace(' \ufeff', '')
    return text

def parse_binder():
    planets_in_signs = {}
    planets_in_houses = {}
    aspects = {}
    
    current_section = None
    current_planet = None
    current_sign = None
    current_house = None
    
    # Regex pointers
    re_table_signs = re.compile(r'Table 1\.(\d+): (.+) in the Twelve Signs', re.IGNORECASE)
    re_placement = re.compile(r'^\s*(\w+) in (\w+)\s+(.*)', re.IGNORECASE) # "Saturn in Aries"
    re_house_header = re.compile(r'The (\w+)\s+House', re.IGNORECASE)
    
    # We will iterate lines and maintain state
    files = sorted(glob.glob(os.path.join(BINDER_DIR, '*.txt')))
    
    # Buffers
    interpretation_buffer = ""
    collecting_interpretation = False
    
    # State for Planets in Signs
    active_planet_sign = None # (Planet, Sign)
    
    # State for Houses
    active_house = None
    active_house_planet = None
    
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            original_line = line
            line = line.strip()
            
            # Detect Sections
            if "Part 1: Planets in Signs" in line:
                current_section = "SIGNS"
            elif "Part 2: Planets in Houses" in line:
                current_section = "HOUSES"
            elif "Part 3: Aspects" in line:
                current_section = "ASPECTS"
                

            # --- PARSING SIGNS ---
            if current_section == "SIGNS":
                # Check for Table Header
                m_table = re_table_signs.search(line)
                if m_table:
                    # Save working buffer if exists
                    if collecting_interpretation and active_planet_sign:
                        store_sign_interpretation(planets_in_signs, active_planet_sign, interpretation_buffer)
                    
                    raw_planet = m_table.group(2).strip()
                    if raw_planet.lower() == "the sun":
                        current_planet = "Sun"
                    elif raw_planet.lower() == "the moon":
                        current_planet = "Moon"
                    else:
                        current_planet = raw_planet.split(' ')[0] # take first word if "Saturn (Kronos)"

                    collecting_interpretation = False
                    interpretation_buffer = ""
                    continue
                    
                # Check for Placement Row "Saturn in Aries"
                # If we encounter a new placement, save previous
                if current_planet and line.lower().startswith(current_planet.lower() + " in "):
                    parts = line.split()
                    # e.g. "Saturn in Aries Condition: Fall"
                    if len(parts) >= 3:
                        # Save previous
                        if collecting_interpretation and active_planet_sign:
                            store_sign_interpretation(planets_in_signs, active_planet_sign, interpretation_buffer)
                        
                        sign = parts[2]
                        active_planet_sign = (current_planet, sign)
                        interpretation_buffer = ""
                        collecting_interpretation = False
                
                # Check for "Interpretation:"
                if "Interpretation:" in line:
                    collecting_interpretation = True
                    # Start extraction. 
                    content = line.split("Interpretation:", 1)[1].strip()
                    interpretation_buffer = content + " "
                    continue
                
                # If collecting, keep adding until we hit empty lines or "Condition:" or new placement
                if collecting_interpretation:
                    stripped = line.strip()
                    if "Condition:" in stripped or (current_planet and stripped.lower().startswith(current_planet.lower() + " in ")) or "Table " in stripped:
                        collecting_interpretation = False
                        store_sign_interpretation(planets_in_signs, active_planet_sign, interpretation_buffer)
                        # Don't continue, loop might need to process this line as a new start
                        # usage of continue above prevents this, but here we are inside if.
                        # We just stop collecting. The next iteration won't re-trigger unless we handle it.
                        # Actually if it's "Condition:", we just stop. If it's a new placement, the logic above handles it?
                        # No, logic above is before this block.
                        # Logic flow is tricky.
                        pass
                    elif line == "" and interpretation_buffer.strip().endswith('"'):
                         pass 
                    else:
                        interpretation_buffer += line + " "

            # --- PARSING HOUSES ---
            if current_section == "HOUSES":
                # Detect House Header "The First House"
                m_house = re_house_header.search(line)
                if m_house:
                    # Save previous planet in house if exists
                    if collecting_interpretation and active_house and active_house_planet:
                         store_house_interpretation(planets_in_houses, active_house, active_house_planet, interpretation_buffer)
                    
                    active_house = m_house.group(1) # "First", "Second"
                    collecting_interpretation = False
                    interpretation_buffer = ""
                    continue
                
                # Check for Planet Start in the table rows (usually bold or first word)
                first_word = line.split(' ')[0] if line else ""
                valid_starters = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Benefics", "Malefics"]
                
                if first_word in valid_starters:
                    # Save previous
                    if collecting_interpretation and active_house and active_house_planet:
                         store_house_interpretation(planets_in_houses, active_house, active_house_planet, interpretation_buffer)
                    
                    active_house_planet = first_word
                    collecting_interpretation = True
                    interpretation_buffer = ""
                    
                    if '"' in line:
                        content = line.split('"', 1)[1]
                        interpretation_buffer = content if '"' in content else '"' + content
                    continue
                
                if collecting_interpretation and active_house and active_house_planet:
                     # Stop conditions (new planet or new house)
                     if "The " in line and " House" in line:
                         store_house_interpretation(planets_in_houses, active_house, active_house_planet, interpretation_buffer)
                         collecting_interpretation = False
                     elif line.split(' ')[0] in valid_starters:
                         store_house_interpretation(planets_in_houses, active_house, active_house_planet, interpretation_buffer)
                         # This will be caught by the starter check in next iteration if we don't continue
                         pass
                     else:
                        interpretation_buffer += line + " "

    # Check matches at end of file
    if current_section == "SIGNS" and collecting_interpretation and active_planet_sign:
        store_sign_interpretation(planets_in_signs, active_planet_sign, interpretation_buffer)
    if current_section == "HOUSES" and collecting_interpretation and active_house and active_house_planet:
        store_house_interpretation(planets_in_houses, active_house, active_house_planet, interpretation_buffer)

    # SECONDPASS: Detailed Delineations (from part_005)
    detailed_delineations = parse_detailed_profiles(files)

    # Write Outputs
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(os.path.join(OUTPUT_DIR, 'planets_in_signs_ingested.json'), 'w') as f:
        json.dump(planets_in_signs, f, indent=4)
        
    with open(os.path.join(OUTPUT_DIR, 'planets_in_houses.json'), 'w') as f:
        json.dump(planets_in_houses, f, indent=4)

    with open(os.path.join(OUTPUT_DIR, 'detailed_delineations.json'), 'w') as f:
        json.dump(detailed_delineations, f, indent=4)

def parse_detailed_profiles(files):
    profiles = {}
    current_planet = None
    collecting = None # "GENERAL", "SIGNS", "HOUSES"
    
    re_planet_header = re.compile(r'### The (\w+):', re.IGNORECASE)
    
    for file_path in files:
        if "part_005" not in file_path: continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line_s = line.strip()
            
            m = re_planet_header.search(line_s)
            if m:
                current_planet = m.group(1).upper()
                profiles[current_planet] = {"GENERAL": "", "SIGNS": {}, "HOUSES": {}}
                continue
                
            if not current_planet: continue
            
            if "**General Nature:**" in line_s:
                collecting = "GENERAL"
                profiles[current_planet]["GENERAL"] = line_s.split(":", 1)[1].strip()
                continue
                
            if "in the Twelve Signs:**" in line_s:
                collecting = "SIGNS"
                continue
                
            if "in the Twelve Houses:**" in line_s:
                collecting = "HOUSES"
                continue
                
            if collecting == "GENERAL" and line_s and not line_s.startswith("**"):
                profiles[current_planet]["GENERAL"] += " " + line_s
                
            if collecting == "SIGNS" and "In " in line_s and "," in line_s:
                # e.g. "In Aries, the Sun achieves..."
                parts = line_s.split(",", 1)
                sign_name = parts[0].replace("In ", "").strip().upper()
                text = parts[1].strip()
                profiles[current_planet]["SIGNS"][sign_name] = text

            if collecting == "HOUSES" and "In the " in line_s:
                # e.g. "In the first house (domicile of Mercury), the Sun..."
                # Use regex or split
                # "In the first house" or "In the second house"
                m_h = re.search(r'In the (\w+) house', line_s, re.I)
                if m_h:
                    h_name = m_h.group(1).lower()
                    text = line_s.split(",", 1)[1].strip() if "," in line_s else line_s
                    profiles[current_planet]["HOUSES"][h_name] = text
                    
    return profiles

def store_sign_interpretation(db, key_tuple, text):
    if not key_tuple: return
    planet, sign = key_tuple
    text = clean_text(text)
    if not text: return
    
    # Heuristic for Day/Night splitting
    # If text explicitly contains "by day" or "by night" we might split.
    # For now, let's assign to BOTH and if distinct quotes exist, we append?
    # Actually, simpler: Assign the FULL text to both DAY and NIGHT keys, 
    # unless we parse distinct Day/Night blocks.
    
    # Basic normalization
    planet = planet.upper()
    sign = sign.upper()
    
    # We will just overwrite for now, or append if exists?
    # The existing JSON has explicit keys.
    
    # Create keys
    key_day = f"{planet}_{sign}_DAY"
    key_night = f"{planet}_{sign}_NIGHT"
    
    # Check if text differentiates
    # If text says "by day... by night...", keep it all so the user sees it.
    
    db[key_day] = text
    db[key_night] = text

def store_house_interpretation(db, house, planet, text):
    text = clean_text(text)
    if not text: return
    
    # Normalize House Name to Number
    house_map = {
        "First": "1", "Second": "2", "Third": "3", "Fourth": "4", "Fifth": "5", "Sixth": "6",
        "Seventh": "7", "Eighth": "8", "Ninth": "9", "Tenth": "10", "Eleventh": "11", "Twelfth": "12",
        "1st": "1", "2nd": "2", "3rd": "3", "4th": "4", "5th": "5", "6th": "6",
        "7th": "7", "8th": "8", "9th": "9", "10th": "10", "11th": "11", "12th": "12"
    }
    h_num = house_map.get(house, house)
    
    key = f"{planet.upper()}_{h_num}"
    db[key] = text

if __name__ == '__main__':
    parse_binder()
