import hashlib
import hashlib
from datetime import datetime
from fastapi import Request
from src.engine.logger import ActivityLogger
from src.api.v1.auth import validate_token
from src.engine.models import Chart, Planet, PlanetName

def generate_chart_hash(req) -> str:
    # Normalize inputs for hashing
    date = req.date.strip()
    time = req.time.strip()
    city = req.city.strip().lower()
    state = (req.state or "").strip().lower()
    raw = f"{date}_{time}_{city}_{state}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def log_event(event_type: str, payload: dict, request: Request, session_id: str = None, ts: str = None):
    """
    Helper to log business events via ActivityLogger.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # Try to extract user ID from token if present
    user_id = "guest"
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            token_payload = validate_token(token)
            if token_payload and "d" in token_payload and "user_id" in token_payload["d"]:
                user_id = token_payload["d"]["user_id"]
        except:
            pass
            
    details = payload.copy()
    if session_id:
        details["session_id"] = session_id
    if ts:
        details["client_ts"] = ts
        
    ActivityLogger.log_activity(
        event_type,
        user_id=user_id,
        ip=client_ip,
        details=details
    )

def result_to_model(res):
    model_planets = []
    sun_alt = 0.0
    for name, data in res.get("planets", {}).items():
        try:
            p_enum = PlanetName(name)
        except ValueError:
            continue
        model_planets.append(
            Planet(
                name=p_enum,
                longitude=data["longitude"],
                latitude=data.get("latitude", 0.0),
                speed=data.get("speed", 0.0),
                altitude=data.get("altitude", 0.0)
            )
        )
        if name == "Sun":
            sun_alt = data.get("altitude", 0.0)

    angles = res.get("angles", {})
    return Chart(
        sun_altitude=sun_alt,
        planets=model_planets,
        ascendant=angles.get("Ascendant", 0.0),
        mc=angles.get("MC", 0.0),
        north_node=res.get("planets", {}).get("North_Node", {}).get("longitude", 0.0),
        south_node=res.get("planets", {}).get("South_Node", {}).get("longitude", 0.0),
        geo_lat=res.get("meta", {}).get("lat"),
        geo_lon=res.get("meta", {}).get("lon"),
        jd=res.get("meta", {}).get("julian_day"),
        houses=res.get("houses"),
        house_system=(res.get("meta", {}).get("house_system") or {}).get("code")
    )
