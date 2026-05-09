import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter


BASE = "https://traditional-astrology.com"


def owner_key_from_env():
    owner_key = os.environ.get("OWNER_BOOTSTRAP_KEY", "").strip()
    if not owner_key:
        raise RuntimeError("OWNER_BOOTSTRAP_KEY must be set in the environment.")
    return owner_key


def get(path, params="", owner_key=None):
    url = f"{BASE}{path}{params}"
    req = urllib.request.Request(
        url,
        headers={"X-Owner-Key": owner_key or owner_key_from_env()},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        return {"error": f"HTTP {e.code}: {detail}"}
    except urllib.error.URLError as e:
        return {"error": f"Network error: {e.reason}"}
    except TimeoutError as e:
        return {"error": f"Request timed out: {e}"}
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON response: {e}"}


def main():
    try:
        owner_key = owner_key_from_env()
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 2

    res = get("/api/v1/owner/chart-events", "?limit=200", owner_key=owner_key)
    if "error" in res:
        print(res["error"], file=sys.stderr)
        return 1

    events = res.get("chart_events", [])
    total = res.get("total", len(events))

    print(f"Total chart events in DB: {total}")
    print(f"Returned: {len(events)}\n")

    statuses = Counter(e["status"] for e in events)
    types = Counter(e["event_type"] for e in events)
    cities = Counter(e["request_payload"].get("city", "?") for e in events)
    ips = Counter(e["client_ip"] for e in events)

    print(f"Status breakdown: {dict(statuses)}")
    print(f"Event types: {dict(types)}")
    print(f"Top cities: {cities.most_common(10)}")
    print(f"Unique IPs: {len(ips)}")
    print("\nAll chart events (newest first):")
    for e in events:
        p = e.get("request_payload", {})
        s = e.get("chart_summary", {})
        print(
            f"  [{e['created_at'][:16]}] {e['status']:12} | "
            f"{p.get('date', '?')} {p.get('time', '?')} | "
            f"{p.get('city', '?')},{p.get('state', '?')} | "
            f"Sun:{s.get('sun_sign', '?')} Moon:{s.get('moon_sign', '?')} "
            f"Asc:{s.get('rising_sign', '?')} | "
            f"IP:{e['client_ip']} | {e['reading_html_chars']} chars"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
