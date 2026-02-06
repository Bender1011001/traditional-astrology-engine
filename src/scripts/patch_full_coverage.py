import json
import os

JSON_PATH = "src/database/data/planets_in_signs.json"

# Synthesis of Search Results (Lilly/Valens) for missing keys
PATCHES = {
    # MARS
    "MARS_VIRGO_DAY": "Ruling, leading, lucky in all martial affairs, optimistic/spirited. (Valens, Terms of Virgo)",
    "MARS_VIRGO_NIGHT": "Ruling, leading, lucky in all martial affairs, optimistic/spirited. (Valens, Terms of Virgo)",

    # SUN
    "SUN_TAURUS_DAY": "Patient, laborious, stubborn, and slow to anger, but formidable when provoked. (Lilly)",
    "SUN_TAURUS_NIGHT": "Patient, laborious, stubborn, and slow to anger, but formidable when provoked. (Lilly)",
    "SUN_GEMINI_DAY": "Judicious in worldly affairs, excellent understanding, active body. (Lilly)",
    "SUN_GEMINI_NIGHT": "Judicious in worldly affairs, excellent understanding, active body. (Lilly)",
    "SUN_PISCES_DAY": "Unsteady, unreliable, prone to changes... sensual, thievish. (Valens)",
    "SUN_PISCES_NIGHT": "Unsteady, unreliable, prone to changes... sensual, thievish. (Valens)",

    # VENUS
    "VENUS_LEO_DAY": "Zealous in affections, musical, cheerful, believing. (Lilly)",
    "VENUS_LEO_NIGHT": "Zealous in affections, musical, cheerful, believing. (Lilly)",
    "VENUS_VIRGO_DAY": "Unlucky in marriages, promiscuous. (Valens)",
    "VENUS_VIRGO_NIGHT": "Unlucky in marriages, promiscuous. (Valens)",

    # MERCURY
    "MERCURY_CANCER_DAY": "Good with the good, evil with the evil. Adaptable, having a subtle mind. (Lilly)",
    "MERCURY_CANCER_NIGHT": "Good with the good, evil with the evil. Adaptable, having a subtle mind. (Lilly)",
    "MERCURY_LEO_DAY": "Ambitious in learning, sharp, witty. (Lilly)",
    "MERCURY_LEO_NIGHT": "Ambitious in learning, sharp, witty. (Lilly)",
    "MERCURY_LIBRA_DAY": "Eloquent, an excellent debater, curious about occult knowledge. (Lilly)",
    "MERCURY_LIBRA_NIGHT": "Eloquent, an excellent debater, curious about occult knowledge. (Lilly)",
    "MERCURY_CAPRICORN_DAY": "Melancholic temperament, sharp wit but peevish. (Lilly)",
    "MERCURY_CAPRICORN_NIGHT": "Melancholic temperament, sharp wit but peevish. (Lilly)",
    "MERCURY_AQUARIUS_DAY": "Curious about occult knowledge, skilled in trade. (Lilly)",
    "MERCURY_AQUARIUS_NIGHT": "Curious about occult knowledge, skilled in trade. (Lilly)",
    "MERCURY_SAGITTARIUS_DAY": "In Detriment. Sudden, rash, and unstable in speech. (Lilly)",
    "MERCURY_SAGITTARIUS_NIGHT": "In Detriment. Sudden, rash, and unstable in speech. (Lilly)",
    "MERCURY_PISCES_DAY": "In Detriment and Fall. Ill-disposed, deceptive, or confused. (Lilly)",
    "MERCURY_PISCES_NIGHT": "In Detriment and Fall. Ill-disposed, deceptive, or confused. (Lilly)",

    # MOON
    "MOON_GEMINI_DAY": "Restless nature, much travel, but cadent from its own sign. (Lilly)",
    "MOON_GEMINI_NIGHT": "Restless nature, much travel, but cadent from its own sign. (Lilly)",
    "MOON_LEO_DAY": "Ambitious, Lofty, and Sovereign. (Traditional)",
    "MOON_LEO_NIGHT": "Ambitious, Lofty, and Sovereign. (Traditional)",
    "MOON_VIRGO_DAY": "Modest, religious, administrators of others' goods. (Valens)",
    "MOON_VIRGO_NIGHT": "Modest, religious, administrators of others' goods. (Valens)",
    "MOON_LIBRA_DAY": "Social, changeable, pure trades. (Valens)",
    "MOON_LIBRA_NIGHT": "Social, changeable, pure trades. (Valens)",
    "MOON_SAGITTARIUS_DAY": "Desire for confidence, excitement, but wanderlust. (Valens)",
    "MOON_SAGITTARIUS_NIGHT": "Desire for confidence, excitement, but wanderlust. (Valens)",
    "MOON_AQUARIUS_DAY": "Picking the most unusual partners, unsociable if afflicted. (Valens)",
    "MOON_AQUARIUS_NIGHT": "Picking the most unusual partners, unsociable if afflicted. (Valens)",
    "MOON_PISCES_DAY": "Prolific, sensual, unsteady, wandering. (Valens)",
    "MOON_PISCES_NIGHT": "Prolific, sensual, unsteady, wandering. (Valens)"
}

def apply_full_patch():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Pre-Patch Count: {len(data)} entries.")
    
    count_patched = 0
    for k, v in PATCHES.items():
        # Overwrite if missing or if it contains "Delineation not found"
        if k not in data or "Delineation not found" in data[k] or "No distinct" in data[k]:
            data[k] = v
            count_patched += 1
            print(f"Patched {k}")
            
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print(f"Full Patch Comparison. patched {count_patched} entries.")

if __name__ == "__main__":
    apply_full_patch()
