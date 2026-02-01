from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import Dict, Any
from src.api.v1.schemas import LoginRequest, RegisterRequest
from src.engine.user_auth import get_user_manager
from src.api.v1.auth import create_access_token, get_current_user
from src.database.models import User

router = APIRouter()
user_manager = get_user_manager()

@router.post("/register")
async def register(request: RegisterRequest):
    result = user_manager.create_user(request.email, request.password, request.name)
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
async def read_users_me(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Refresh to ensure we have latest charts
    # Actually current_user is a DB model instance from get_current_user dependency
    return {
        "user": current_user.to_dict()
    }
