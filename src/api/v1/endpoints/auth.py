from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status, Body
from typing import Dict, Any
from sqlalchemy.orm import Session
from src.api.v1.schemas import LoginRequest, RegisterRequest, ForgotPasswordRequest, ResetPasswordRequest
from src.engine.user_auth import get_user_manager
from src.api.v1.auth import create_access_token, get_current_user
from src.database.models import User
from src.database.core import get_db
from src.services.admin_notifier import notify_user_registered

import logging
import time
from collections import defaultdict

logger = logging.getLogger(__name__)

router = APIRouter()
user_manager = get_user_manager()

_auth_attempts: dict[str, list[float]] = defaultdict(list)
_AUTH_WINDOW = 300
_AUTH_MAX_ATTEMPTS = 10

def _check_auth_rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    attempts = _auth_attempts[ip]
    _auth_attempts[ip] = [t for t in attempts if now - t < _AUTH_WINDOW]
    if len(_auth_attempts[ip]) >= _AUTH_MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")
    _auth_attempts[ip].append(now)

@router.post("/register", dependencies=[Depends(_check_auth_rate_limit)])
async def register(request: RegisterRequest, background_tasks: BackgroundTasks):
    result = user_manager.create_user(request.email, request.password, request.name, plan_tier=request.plan_tier or "")
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )

    user = result["user"]
    # Auto-login: Create token
    access_token = create_access_token(
        chart_hash="",  # Not relevant for general user token
        tier=user.get("subscription_tier", "free"),
        data={"user_id": user["id"]}
    )
    logger.info("New user registered: %s", request.email)

    # Discord notification — runs after response is sent, never blocks the caller.
    background_tasks.add_task(
        notify_user_registered,
        email=request.email,
        name=request.name or "",
        plan_tier=user.get("subscription_tier", "free"),
    )

    return {
        "success": True,
        "token": access_token,
        "user": user,
    }

@router.post("/login", dependencies=[Depends(_check_auth_rate_limit)])
async def login(request: LoginRequest):
    result = user_manager.authenticate(request.email, request.password)
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["message"]
        )
    
    user = result["user"]
    access_token = create_access_token(
        chart_hash="", 
        tier=user.get("subscription_tier", "free"),
        data={"user_id": user["id"]}
    )
    logger.info("User logged in: %s", request.email)
    
    return {
        "success": True,
        "token": access_token,
        "user": user
    }

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    from src.services.subscription import SubscriptionService
    sub_service = SubscriptionService(db)
    usage = sub_service.get_usage_stats(current_user)
    
    user_dict = current_user.to_dict()
    user_dict["usage"] = usage
    
    return {
        "user": user_dict
    }

@router.get("/restore_session")
async def restore_session(token: str):
    from src.api.v1.auth import validate_token
    
    try:
        payload = validate_token(token)
    except Exception as e:
        logger.warning("Session restore failed with invalid token: %s", repr(e), exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid token")

    if not payload:
        raise HTTPException(status_code=400, detail="Invalid token")

    # Check for nested data 'd'
    data = payload.get("d", {})
    if not isinstance(data, dict):
        data = {}

    chart_input = data.get("chart_input")
    # Also check top level just in case textual modification happened
    if not chart_input:
        chart_input = payload.get("chart_input")

    if not chart_input:
        raise HTTPException(status_code=404, detail="No session data found")

    return chart_input

@router.post("/forgot-password", dependencies=[Depends(_check_auth_rate_limit)])
async def forgot_password(request: ForgotPasswordRequest):
    from src.engine.email_service import send_email, render_template
    from src.core.config import settings

    result = user_manager.create_password_reset_token(request.email)
    
    # Always return success to prevent email enumeration
    if result["success"] and result["token"]:
        token = result["token"]
        reset_link = f"{settings.SITE_BASE_URL}/reset-password.html?token={token}"
        
        email_html = render_template("reset_password.html", {
            "link": reset_link,
            "email": request.email
        })
        
        send_email(
            to_email=request.email,
            subject="Reset Your Password - Traditional Astrology",
            html_content=email_html
        )
        
    return {"success": True, "message": "If an account exists with this email, you will receive password reset instructions."}

@router.post("/reset-password", dependencies=[Depends(_check_auth_rate_limit)])
async def reset_password(request: ResetPasswordRequest):
    result = user_manager.reset_password_with_token(request.token, request.new_password)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
        
    return {"success": True, "message": "Password has been reset successfully."}
