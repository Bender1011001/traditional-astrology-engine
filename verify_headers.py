import requests
import sys

try:
    url = "https://traditional-astrology.com"
    response = requests.get(url, timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print("-" * 30)
    
    csp = response.headers.get("Content-Security-Policy", "NOT FOUND")
    print(f"CSP Header:\n{csp}")
    print("-" * 30)
    
    # Check for specific directives
    if "unsafe-eval" in csp and "*.googletagmanager.com" in csp:
        print("VERDICT: Updated CSP is LIVE.")
    else:
        print("VERDICT: OLD CSP detected (or CSP missing). Deployment might be pending.")
        
except Exception as e:
    print(f"Error fetching URL: {e}")
