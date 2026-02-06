import requests
import sys

URL = "http://127.0.0.1:8000/api/v1/auth/login"
# Test with a dummy user (or even a valid one if we knew it, but "Internal Server Error" usually happens regardless of credentials if it's a code error)
payload = {
    "email": "test@example.com",
    "password": "password123"
}

try:
    print(f"Sending POST to {URL}...")
    response = requests.post(URL, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
