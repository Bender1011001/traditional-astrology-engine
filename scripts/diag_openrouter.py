import os
import sys
import json
import urllib.request
from dotenv import load_dotenv

ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
load_dotenv(os.path.join(ROOT_DIR, ".env"))

def list_models():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/models"
    
    headers = {
        "Authorization": f"Bearer {api_key}" if api_key else ""
    }
    
    req = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            raw = response.read().decode("utf-8")
            result = json.loads(raw)
            models = [m["id"] for m in result.get("data", [])]
            print("--- AVAILABLE MODELS (SUBSET) ---")
            for m in models:
                if "gemini" in m:
                    print(m)
            print("---------------------------------")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()
