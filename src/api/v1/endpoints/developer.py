import hashlib
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.api.v1.auth import get_current_user
from src.database.core import get_db
from src.database.models import ApiKey, UsageRecord, User

router = APIRouter()


@router.post("/keys")
async def create_api_key(
    name: str = Body(..., embed=True),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new API Key"""
    sub = user.subscription
    if not sub or not sub.plan or sub.status not in {"active", "trial"}:
        raise HTTPException(
            status_code=403, detail="Subscription required to create API keys"
        )
    if sub.plan.tier not in {"practitioner", "studio"}:
        raise HTTPException(
            status_code=403, detail="Upgrade required to create API keys"
        )

    # Enforce API Key Storage Limits (Prevent Table Exhaustion)
    existing_keys_count = db.query(ApiKey).filter(ApiKey.user_id == user.id).count()
    if existing_keys_count >= 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum number of API keys (10) reached. Please revoke an existing key to create a new one.",
        )

    # Generate random key
    raw_key = "sk_live_" + secrets.token_hex(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

    new_key = ApiKey(
        user_id=user.id,
        key_hash=key_hash,
        name=name[:100],  # Hard cap name length for physical column security
    )
    db.add(new_key)
    db.commit()

    # Return raw key ONLY ONCE
    return {"key": raw_key, "name": name, "id": new_key.id}


@router.get("/keys")
async def list_api_keys(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """List all API keys"""
    keys = db.query(ApiKey).filter(ApiKey.user_id == user.id).all()
    return [
        {
            "id": k.id,
            "name": k.name,
            "created_at": k.created_at,
            "last_used": k.last_used,
            "prefix": "sk_live_...",
        }
        for k in keys
    ]


@router.delete("/keys/{key_id}")
async def revoke_api_key(
    key_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Revoke an API key"""
    key = (
        db.query(ApiKey).filter(ApiKey.id == key_id, ApiKey.user_id == user.id).first()
    )
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")

    db.delete(key)
    db.commit()
    return {"status": "revoked"}


@router.get("/usage")
async def get_developer_usage(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get B2B API usage stats"""
    sub = user.subscription
    if not sub:
        return {"api_calls_used": 0, "quota": 0}

    plan = sub.plan
    period_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    used = (
        db.query(func.sum(UsageRecord.cost_credits))
        .filter(
            UsageRecord.subscription_id == sub.id,
            UsageRecord.resource_type == "api_call",
            UsageRecord.created_at >= period_start,
        )
        .scalar()
        or 0
    )

    return {
        "api_calls_used": used,
        "quota": plan.api_quota or 0,
        "quota_period": "day",
        "plan_tier": plan.tier,
    }
