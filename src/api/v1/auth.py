from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Header

from src.core.config import settings


def _jwt_secret() -> str:
    return settings.JWT_SECRET.strip()


def create_access_token(
    chart_hash: str, tier: str, expires_days: int = 30, data: dict = None  # type: ignore
) -> str:
    payload = {
        "chart_hash": chart_hash,
        "tier": tier,
        "exp": datetime.now(timezone.utc) + timedelta(days=expires_days),
    }
    if data:
        payload["d"] = data

    return jwt.encode(payload, _jwt_secret(), algorithm="HS256")


def validate_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=["HS256"])
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
from sqlalchemy.orm import Session, joinedload

from src.database.core import get_db
from src.database.models import User, UserSubscription


async def get_current_user(
    user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)
) -> Optional[User]:
    if user_id == "guest":
        return None
    user = (
        db.query(User)
        .options(joinedload(User.subscription).joinedload(UserSubscription.plan))
        .filter(User.id == user_id)
        .first()
    )
    return user
