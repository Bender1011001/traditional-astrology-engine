import requests
import sys
import json

def test_api(base_url="http://127.0.0.1:8000"):
    base_url = base_url.rstrip("/")
    endpoint = f"{base_url}/api/calculate"
    
    payload = {
        "date": "1990-01-01",
        "time": "12:00",
        "city": "London",
        "state": "UK"
    }

    print(f"Testing URL: {endpoint}")
    print("Sending request...")
    
    try:
        response = requests.post(endpoint, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            plain_reading = data.get("plain_reading")
            
            print("\n--- STATUS: SUCCESS (200) ---")
            if plain_reading:
                print(f"PLAIN REAING RECEIVED (Length: {len(plain_reading)} chars):")
                print("-" * 40)
                print(plain_reading[:500] + "..." if len(plain_reading) > 500 else plain_reading)
                print("-" * 40)
            else:
                print("WARNING: 'plain_reading' field is missing or empty.")
                if "forensic_error" in data:
                    print(f"Forensic Error found: {data['forensic_error']}")
        else:
            print(f"\n--- ERROR: HTTP {response.status_code} ---")
            try:
                err_data = response.json()
                print("Detail:", json.dumps(err_data, indent=2))
            except:
                print(response.text)
                
    except Exception as e:
        print(f"\n--- CRITICAL CONNECTION ERROR ---")
        print(str(e))

if __name__ == "__main__":
    url = "http://127.0.0.1:8000"
    if len(sys.argv) > 1:
        url = sys.argv[1]
    
    test_api(url)
