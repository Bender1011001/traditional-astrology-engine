from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, Any
from sqlalchemy.orm import Session
from src.api.v1.schemas import LoginRequest, RegisterRequest, ForgotPasswordRequest, ResetPasswordRequest
from src.engine.user_auth import get_user_manager
from src.api.v1.auth import create_access_token, get_current_user
from src.database.models import User
from src.database.core import get_db

router = APIRouter()
user_manager = get_user_manager()

@router.post("/register")
async def register(request: RegisterRequest):
    result = user_manager.create_user(request.email, request.password, request.name, plan_tier=request.plan_tier or "")
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    user = result["user"]
    # Auto-login: Create token
    access_token = create_access_token(
        chart_hash="", # Not relevant for general user token
        tier=user.get("subscription_tier", "free"),
        data={"user_id": user["id"]}
    )
    
    return {
        "success": True,
        "token": access_token,
        "user": user
    }

@router.post("/login")
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
    except Exception:
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

@router.post("/forgot-password")
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
            subject="Reset Your Password - Codex Caelestis",
            html_content=email_html
        )
        
    return {"success": True, "message": "If an account exists with this email, you will receive password reset instructions."}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    result = user_manager.reset_password_with_token(request.token, request.new_password)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
        
    return {"success": True, "message": "Password has been reset successfully."}
