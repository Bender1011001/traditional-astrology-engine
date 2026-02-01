from fastapi import HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from src.database.core import get_db
from src.database.models import ApiKey, User
from src.core.config import settings
import hashlib
from datetime import datetime
from sqlalchemy.orm import Session

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(
    request: Request,
    api_key: str = Security(api_key_header)
):
    """
    Verify API key and return associated user and subscription.
    """
    if not api_key:
        return None # Allow fallthrough to other auth methods if key is missing

    # Hash the key
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Get DB session from request state or create new?
    # Middleware usually doesn't have easy access to dependency injection.
    # We can use the get_db generator manually.
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Look up key
        key_record = db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first()
        
        if not key_record:
            raise HTTPException(status_code=401, detail="Invalid API key")
            
        # Update last used
        key_record.last_used = datetime.utcnow()
        db.commit()
        
        # Get User
        user = key_record.user
        if not user:
             raise HTTPException(status_code=401, detail="Orphaned API key")

        # Verify Subscription
        sub = user.subscription
        if not sub or sub.status != "active":
             raise HTTPException(status_code=403, detail="No active subscription for this API key")
             
        # Check if plan allows API access?
        if not sub.plan.api_quota and sub.plan.tier not in ['master', 'agency']:
             # Strict B2B check
             # But maybe they have a custom plan?
             # For now, let's allow if they have quota or 'api_access' feature
             features = sub.plan.features or {}
             if not features.get('api_access') and not sub.plan.api_quota:
                  raise HTTPException(status_code=403, detail="Plan does not support API access")

        return {
            "user": user,
            "subscription": sub,
            "api_key_id": key_record.id,
            "plan": sub.plan
        }
    finally:
        db.close()
