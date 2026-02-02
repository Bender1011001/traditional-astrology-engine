import requests
import json
import time

def test_calculate_full():
    url = "http://127.0.0.1:8000/api/v1/calculate-full"
    payload = {
        "date": "1990-05-15",
        "time": "10:30",
        "city": "London",
        "state": "",
        "name": "Test Native"
    }
    
    print(f"Testing {url}...")
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Keys in response:", list(data.keys()))
            if "technical_data" in data and "human_translation" in data:
                print("SUCCESS: Response matches the Sovereign Schema.")
                # Save a snippet for review
                with open("sovereign_test_output_snippet.json", "w") as f:
                    # Save only keys and meta to avoid massive dump
                    snippet = {
                        "technical_data_keys": list(data["technical_data"].keys()),
                        "human_translation_keys": list(data["human_translation"].keys()),
                        "meta": data["technical_data"]["meta"]
                    }
                    json.dump(snippet, f, indent=2)
            else:
                print("FAILURE: Missing required top-level keys.")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")

def test_calculate_legacy():
    url = "http://127.0.0.1:8000/api/v1/calculate"
    payload = {
        "date": "1990-05-15",
        "time": "10:30",
        "city": "London",
        "state": "",
        "name": "Test Native"
    }
    
    print(f"\nTesting legacy endpoint {url}...")
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Keys in response:", list(data.keys()))
            if "astronomy" in data and "planets" in data["astronomy"] and "report_markdown" in data:
                print("SUCCESS: Endpoint returns required fields (new schema).")
            else:
                print(f"FAILURE: Endpoint missing fields. Keys found: {list(data.keys())}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    # Wait a bit for uvicorn to pick up changes if it's auto-reloading
    print("Waiting for server reload...")
    time.sleep(3)
    test_calculate_full()
    test_calculate_legacy()
