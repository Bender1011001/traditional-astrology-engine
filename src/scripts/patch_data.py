import json
import os

JSON_PATH = "src/database/data/planets_in_signs.json"

PATCHES = {
    "SATURN_LEO_DAY": "Disciplined authority, heavy responsibility, eventual honor.",
    "SATURN_LEO_NIGHT": "Envy, obstruction, heat affecting the heart, tyranny.",
    "SATURN_ARIES_DAY": "Skillful, with much hair, good stature, gaze directed at the earth; but foul speech. (Valens/Lilly)",
    "SATURN_ARIES_NIGHT": "Weak constitution, subject to cold and moist diseases. (Inferred from general Saturn/Fall)",
    "SATURN_CANCER_DAY": "Destructive, envious, weak constitution. (Detriment)",
    "SATURN_CANCER_NIGHT": "Malicious, solitary, deceitful... secretive in their trickery. (Valens)",
    "VENUS_LIBRA_DAY": "Great artistic talent and relational desire, but burned up if combust.",
    "VENUS_LIBRA_NIGHT": "Social grace, strong alliances, abundance.",
    "MARS_LEO_DAY": "Destructive / Hot. Sun and Mars in mutual reception (if Sun in Aries) or simply fiery. (Inferred)",
    "MARS_LEO_NIGHT": "Destructive. Heat affecting the heart. (Inferred)"
}

def patch_data():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Loaded {len(data)} entries.")
    
    for k, v in PATCHES.items():
        if k in data:
            data[k] = v
            print(f"Patched {k}")
        else:
            print(f"Warning: Key {k} not in original JSON schema?")
            
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print("Patch complete.")

if __name__ == "__main__":
    patch_data()
