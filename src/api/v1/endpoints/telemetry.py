from fastapi import APIRouter, Request, Depends
from src.api.v1.schemas import TelemetryEvent
from src.engine.logger import ActivityLogger
from src.api.v1.auth import validate_token

router = APIRouter()

@router.post("/log/telemetry")
async def log_telemetry(event: TelemetryEvent, request: Request):
    """
    Log frontend events (clicks, errors, navigation).
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # Try to extract user ID from token if present
    auth_header = request.headers.get("Authorization")
    user_id = "guest"
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = validate_token(token)
        if payload and "d" in payload and "user_id" in payload["d"]:
            user_id = payload["d"]["user_id"]

    ActivityLogger.log_activity(
        f"frontend_{event.event_type}",
        user_id=user_id,
        ip=client_ip,
        details={
            "element": event.element_id,
            "url": event.url,
            "data": event.data
        }
    )
    return {"status": "logged"}
