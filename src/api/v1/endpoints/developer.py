from fastapi import APIRouter, Depends, HTTPException, Body
from src.api.v1.auth import get_current_user
from src.database.core import get_db
from src.database.models import User, ApiKey, UsageRecord, UserSubscription
from sqlalchemy.orm import Session
from sqlalchemy import func
import secrets
import hashlib
from datetime import datetime

router = APIRouter()

@router.post("/keys")
async def create_api_key(
    name: str = Body(..., embed=True),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new API Key"""
    # Generate random key
    raw_key = "sk_live_" + secrets.token_hex(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    
    new_key = ApiKey(
        user_id=user.id,
        key_hash=key_hash,
        name=name
    )
    db.add(new_key)
    db.commit()
    
    # Return raw key ONLY ONCE
    return {"key": raw_key, "name": name, "id": new_key.id}

@router.get("/keys")
async def list_api_keys(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all API keys"""
    keys = db.query(ApiKey).filter(ApiKey.user_id == user.id).all()
    return [{
        "id": k.id,
        "name": k.name,
        "created_at": k.created_at,
        "last_used": k.last_used,
        "prefix": "sk_live_..."
    } for k in keys]

@router.delete("/keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke an API key"""
    key = db.query(ApiKey).filter(ApiKey.id == key_id, ApiKey.user_id == user.id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
        
    db.delete(key)
    db.commit()
    return {"status": "revoked"}

@router.get("/usage")
async def get_developer_usage(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get B2B API usage stats"""
    sub = user.subscription
    if not sub:
        return {"api_calls_used": 0, "quota": 0}
        
    plan = sub.plan
    period_start = sub.current_period_start or datetime.utcnow().replace(day=1)
    
    used = db.query(func.sum(UsageRecord.cost_credits)).filter(
        UsageRecord.subscription_id == sub.id,
        UsageRecord.resource_type == 'api_call',
        UsageRecord.created_at >= period_start
    ).scalar() or 0
    
    return {
        "api_calls_used": used,
        "quota": plan.api_quota or 0,
        "plan_tier": plan.tier
    }
