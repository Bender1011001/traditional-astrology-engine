import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Header, HTTPException
from src.core.config import settings

def create_access_token(chart_hash: str, tier: str, expires_days: int = 30, data: dict = None) -> str:
    payload = {
        'chart_hash': chart_hash,
        'tier': tier,
        'exp': datetime.utcnow() + timedelta(days=expires_days)
    }
    if data:
        payload['d'] = data
        
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')

def validate_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

async def get_current_user_id(authorization: str = Header(None)) -> str:
    # Basic dependency to extract user_id if present
    if not authorization or not authorization.startswith("Bearer "):
        return "guest"
    token = authorization.split(" ")[1]
    payload = validate_token(token)
    if payload and "d" in payload and "user_id" in payload["d"]:
        return payload["d"]["user_id"]
    return "guest"

from fastapi import Depends
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.database.models import User

async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if user_id == "guest":
        return None
    user = db.query(User).filter(User.id == user_id).first()
    return user
