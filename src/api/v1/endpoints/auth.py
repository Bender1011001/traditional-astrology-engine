import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.v1.auth import get_current_user
from src.api.v1.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
)
from src.database.core import get_db
from src.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter()

_ACCOUNTS_RETIRED = HTTPException(
    status_code=status.HTTP_410_GONE,
    detail="Accounts are retired. Readings and checkout do not require an account.",
)


@router.post("/register")
async def register(request: RegisterRequest, background_tasks: BackgroundTasks):
    raise _ACCOUNTS_RETIRED


@router.post("/login")
async def login(request: LoginRequest):
    raise _ACCOUNTS_RETIRED


@router.get("/me")
async def read_users_me(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    from src.services.subscription import SubscriptionService

    sub_service = SubscriptionService(db)
    usage = sub_service.get_usage_stats(current_user)

    user_dict = current_user.to_dict()
    user_dict["usage"] = usage

    return {"user": user_dict}


@router.get("/restore_session")
async def restore_session(token: str):
    from src.api.v1.auth import validate_token

    try:
        payload = validate_token(token)
    except Exception as e:
        logger.warning(
            "Session restore failed with invalid token: %s", repr(e), exc_info=True
        )
        raise HTTPException(status_code=400, detail="Invalid token")

    if not payload:
        raise HTTPException(status_code=400, detail="Invalid token")

    data = payload.get("d", {})
    if not isinstance(data, dict):
        data = {}

    chart_input = data.get("chart_input")
    if not chart_input:
        chart_input = payload.get("chart_input")

    if not chart_input:
        raise HTTPException(status_code=404, detail="No session data found")

    return chart_input


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    raise _ACCOUNTS_RETIRED


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    raise _ACCOUNTS_RETIRED
