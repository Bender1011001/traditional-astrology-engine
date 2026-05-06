from fastapi import Depends, HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from src.database.core import get_db as get_db_dep
from src.database.models import ApiKey, User
from src.core.config import settings
import hashlib
from datetime import datetime, timezone
from sqlalchemy.orm import Session

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(
    request: Request,
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db_dep),
):
    """
    Verify API key and return associated user and subscription.

    Supports two auth paths:
    1. Direct: X-API-Key header with a sk_live_* key issued from the dashboard.
    2. RapidAPI proxy: X-RapidAPI-Proxy-Secret header must match
       RAPIDAPI_PROXY_SECRET env var; request is then authenticated as the
       designated RAPIDAPI_MASTER_KEY API key (a single key provisioned for
       all RapidAPI traffic). Falls back to X-API-Key if proxy secret absent.
    """
    rapidapi_proxy_secret = getattr(settings, "RAPIDAPI_PROXY_SECRET", "").strip()
    rapidapi_master_key = getattr(settings, "RAPIDAPI_MASTER_KEY", "").strip()
    incoming_proxy_secret = request.headers.get("X-RapidAPI-Proxy-Secret", "").strip()

    if rapidapi_proxy_secret and incoming_proxy_secret:
        if incoming_proxy_secret != rapidapi_proxy_secret:
            raise HTTPException(status_code=401, detail="Invalid RapidAPI proxy secret")
        if rapidapi_master_key:
            api_key = rapidapi_master_key

    if not api_key:
        return None

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    key_record = db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first()

    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")

    key_record.last_used = datetime.now(timezone.utc)
    db.commit()

    user = key_record.user
    if not user:
        raise HTTPException(status_code=401, detail="Orphaned API key")

    sub = user.subscription
    if not sub or sub.status not in {"active", "trial"}:
        raise HTTPException(status_code=403, detail="No active subscription for this API key")

    features = sub.plan.features or {}
    if not features.get('api_access'):
        if not sub.plan.api_quota and sub.plan.tier not in {"agency"}:
            raise HTTPException(status_code=403, detail="Plan does not support API access")

    return {
        "user": user,
        "subscription": sub,
        "api_key_id": key_record.id,
        "plan": sub.plan
    }
