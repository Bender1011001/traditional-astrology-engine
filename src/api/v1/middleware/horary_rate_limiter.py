from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

from src.api.v1.auth import get_current_user
from src.database.models import User, HoraryRateLimit
from src.database.core import get_db

logger = logging.getLogger(__name__)

async def enforce_horary_rate_limit(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dependency that enforces a strict limit of 5 requests per IP address per month.
    Bypasses limit entirely for the owner account.
    """
    if current_user and current_user.email == "?":
        return True

    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"

    now = datetime.now(timezone.utc)
    month_str = now.strftime("%Y-%m")
    
    limit_record = db.query(HoraryRateLimit).filter(
        HoraryRateLimit.ip_address == client_ip,
        HoraryRateLimit.month_year == month_str
    ).first()
    
    if not limit_record:
        limit_record = HoraryRateLimit(ip_address=client_ip, month_year=month_str, request_count=0)
        db.add(limit_record)
        try:
            db.commit()
            db.refresh(limit_record)
        except Exception as e:
            db.rollback()
            logger.error("Failed to create HoraryRateLimit record: %s", repr(e), exc_info=True)
            # Fail open or fail closed? Let's fail open but log.
            return True
            
    if limit_record.request_count >= 5:
        raise HTTPException(
            status_code=429, 
            detail="Monthly limit of 5 Horary questions exceeded for this IP address."
        )
        
    # Increment count
    limit_record.request_count += 1
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Failed to increment HoraryRateLimit record: %s", repr(e), exc_info=True)
        
    return True
