import json
import os
from typing import Dict, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_json_data(filename: str) -> Dict[str, Any]:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

class DelineationLibrary:
    def __init__(self):
        self.planets_in_signs = load_json_data('planets_in_signs.json')
        self.planets_in_houses = load_json_data('planets_in_houses.json')
        self.house_definitions = load_json_data('house_topoi.json') 
        self.detailed = load_json_data('detailed_delineations.json')
        
    def get_planet_delineation(self, key: str) -> str:
        return self.planets_in_signs.get(key, "Delineation not found in Codex.")

    def get_detailed_profile(self, planet: str) -> Dict:
        return self.detailed.get(planet.upper(), {})

    def get_house_planet_delineation(self, key: str) -> str:
        return self.planets_in_houses.get(key, "Delineation not found for House placement.")

    def get_house_definition(self, house_num: int) -> str:
        key = f"HOUSE_{house_num}"
        return self.house_definitions.get(key, "Unknown House")
