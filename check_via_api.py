import urllib.request
import json

BASE = "https://traditional-astrology.com"
OWNER_KEY = "L2MwmV6b83XarUTeJpByE3GkeU5RHnAUQTAA8t6fk6zLCXy2"

def get(path, params=""):
    url = f"{BASE}{path}{params}"
    req = urllib.request.Request(url, headers={"X-Owner-Key": OWNER_KEY})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"error": str(e)}

res = get("/api/v1/owner/chart-events", "?limit=200")

events = res.get("chart_events", [])
total = res.get("total", len(events))

print(f"Total chart events in DB: {total}")
print(f"Returned: {len(events)}\n")

# Summary breakdown
from collections import Counter
statuses = Counter(e["status"] for e in events)
types = Counter(e["event_type"] for e in events)
cities = Counter(e["request_payload"].get("city","?") for e in events)
ips = Counter(e["client_ip"] for e in events)

print(f"Status breakdown: {dict(statuses)}")
print(f"Event types: {dict(types)}")
print(f"Top cities: {cities.most_common(10)}")
print(f"Unique IPs: {len(ips)}")
print(f"\nAll chart events (newest first):")
for e in events:
    p = e.get("request_payload", {})
    s = e.get("chart_summary", {})
    print(f"  [{e['created_at'][:16]}] {e['status']:12} | {p.get('date','?')} {p.get('time','?')} | {p.get('city','?')},{p.get('state','?')} | "
          f"Sun:{s.get('sun_sign','?')} Moon:{s.get('moon_sign','?')} Asc:{s.get('rising_sign','?')} | "
          f"IP:{e['client_ip']} | {e['reading_html_chars']} chars")
