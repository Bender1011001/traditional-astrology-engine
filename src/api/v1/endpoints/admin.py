from fastapi import APIRouter, HTTPException, Request, Body
from pydantic import BaseModel
import sys
import os
import logging
from datetime import datetime

# Ensure the src directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from src.scripts.apply_schema_patch import patch_database
from src.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory rate limiter for admin endpoint (simple implementation)
_admin_attempts = {}

class AdminActionRequest(BaseModel):
    key: str

def _check_admin_rate_limit(ip: str, max_attempts: int = 5, window: int = 3600) -> bool:
    """Check if admin action is allowed for this IP (5 attempts per hour)"""
    now = datetime.utcnow().timestamp()
    
    if ip not in _admin_attempts:
        _admin_attempts[ip] = []
    
    # Clean old attempts
    _admin_attempts[ip] = [t for t in _admin_attempts[ip] if now - t < window]
    
    if len(_admin_attempts[ip]) >= max_attempts:
        return False
    
    _admin_attempts[ip].append(now)
    return True

@router.post("/patch_db")
async def trigger_patch_db(request: Request, body: AdminActionRequest = Body(...)):
    """
    Emergency endpoint to trigger database schema patch.
    SECURITY: Requires admin key from environment variable, rate limited, with audit logging.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # SECURITY: Rate limiting (5 attempts per hour per IP)
    if not _check_admin_rate_limit(client_ip):
        logger.warning(f"ADMIN SECURITY: Rate limit exceeded for IP {client_ip}")
        raise HTTPException(status_code=429, detail="Too many admin requests. Try again later.")
    
    # SECURITY: Verify admin key from environment
    admin_key = getattr(settings, 'ADMIN_SECRET_KEY', None)
    if not admin_key:
        logger.error("ADMIN SECURITY: ADMIN_SECRET_KEY not configured in environment")
        raise HTTPException(status_code=500, detail="Admin endpoint not configured")
    
    if body.key != admin_key:
        logger.warning(f"ADMIN SECURITY: Invalid admin key attempt from IP {client_ip}")
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # AUDIT LOG: Log successful admin action
    logger.info(f"ADMIN ACTION: Database patch triggered by IP {client_ip} at {datetime.utcnow()}")
    
    try:
        patch_database()
        logger.info(f"ADMIN ACTION: Database patch completed successfully")
        return {"success": True, "message": "Database patch applied successfully."}
    except Exception as e:
        logger.error(f"ADMIN ACTION: Database patch failed - {str(e)}")
        # SECURITY: Don't expose internal error details
        return {"success": False, "message": "Database patch encountered an error. Check server logs."}
