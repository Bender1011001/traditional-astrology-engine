from fastapi import Depends, HTTPException
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timezone

logger = logging.getLogger(__name__)
from src.database.core import get_db
from src.database.models import User, UsageRecord, UserSubscription
from src.api.v1.auth import get_current_user
from typing import Optional

async def verify_quota(
    resource: str = "chart", 
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dependency to verify and record usage against subscription quota.
    Supports 'chart' and 'api_call' resources.
    """
    if not user:
        # Guests handled by rate limit, or can be restricted here
        yield
        return

    # Check Subscription
    sub = user.subscription
    if not sub:
         # Implicit free tier check or Error?
         # For safety, if no subscription record exists, create one or error.
         # Creating one on fly might be side-effecty. Erroring is safer.
         # But usually signup creates it.
         raise HTTPException(status_code=403, detail="No active subscription found.")

    if sub.status not in ["active", "trial"]:
         raise HTTPException(status_code=403, detail="Subscription inactive.")

    plan = sub.plan
    if not plan:
        raise HTTPException(status_code=403, detail="Invalid subscription plan.")

    # Determine Quota Limit
    limit = None
    if resource == "chart":
        limit = plan.chart_quota
    elif resource == "api_call":
        limit = plan.api_quota

    # Check Usage if limit exists
    if limit is not None:
        period_start = sub.current_period_start or datetime.now(timezone.utc).replace(day=1)
        
        used_credits = db.query(func.sum(UsageRecord.cost_credits)).filter(
            UsageRecord.subscription_id == sub.id,
            UsageRecord.resource_type == resource,
            UsageRecord.created_at >= period_start
        ).scalar() or 0
        
        if used_credits >= limit:
             raise HTTPException(status_code=429, detail=f"Quota exceeded for {resource}. Plan limit: {limit}. Used: {used_credits}.")

    # Yield to let endpoint run
    yield
    
    # Record Usage (Transactional)
    try:
        new_record = UsageRecord(
            subscription_id=sub.id,
            user_id=user.id,
            resource_type=resource,
            cost_credits=1, # Default cost
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_record)
        db.commit()
    except Exception as e:
        logger.warning("Failed to record usage: %s", e)
