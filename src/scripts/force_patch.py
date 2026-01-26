import json
import os

JSON_PATH = "src/database/data/planets_in_signs.json"

PATCHES = {
    # MOON SPECIFIC
    "MOON_TAURUS_DAY": "In Exaltation. Consistent, composed, tender, but potentially stubborn. (Lilly/Valens)",
    "MOON_TAURUS_NIGHT": "In Exaltation. Consistent, composed, tender, but potentially stubborn. (Lilly/Valens)",
    
   # MERCURY FIXES (From previous attempt which failed to overwrite 'NOT FOUND IN')
    "MERCURY_CAPRICORN_DAY": "Melancholic temperament, sharp wit but peevish. (Lilly)",
    "MERCURY_CAPRICORN_NIGHT": "Melancholic temperament, sharp wit but peevish. (Lilly)",
    "MERCURY_AQUARIUS_DAY": "Curious about occult knowledge, skilled in trade. (Lilly)",
    "MERCURY_AQUARIUS_NIGHT": "Curious about occult knowledge, skilled in trade. (Lilly)",

    # ENSURE ALL OTHERS ARE IN
    "MOON_GEMINI_DAY": "Restless nature, much travel, but cadent from its own sign. (Lilly)",
    "MOON_GEMINI_NIGHT": "Restless nature, much travel, but cadent from its own sign. (Lilly)"
}

def force_patch():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Loaded {len(data)} entries.")
    
    for k, v in PATCHES.items():
        # Blindly overwrite
        data[k] = v
        print(f"Forced Patch: {k}")
            
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print("Force Patch Complete.")

if __name__ == "__main__":
    force_patch()
