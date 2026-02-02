from fastapi import HTTPException, Request
from datetime import datetime
import redis
from src.core.config import settings
from typing import Optional

class RateLimiter:
    """Token bucket rate limiter using Redis"""
    
    def __init__(self):
        self.redis = None
        if settings.REDIS_URL:
            try:
                self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception as e:
                print(f"Redis connection failed: {e}")

    def check_rate_limit(self, user_id: str, limit_per_minute: int = 60) -> tuple[bool, dict]:
        """
        Check if request is within rate limit
        """
        if not self.redis:
            return True, {"limit": limit_per_minute, "remaining": limit_per_minute, "reset_at": 0}

        key = f"rate_limit:{user_id}:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
        
        try:
            current = self.redis.incr(key)
            if current == 1:
                self.redis.expire(key, 60)
            
            allowed = current <= limit_per_minute
            remaining = max(0, limit_per_minute - current)
            
            return allowed, {
                "limit": limit_per_minute,
                "remaining": remaining,
                "reset_at": 60 # Seconds ttl
            }
        except Exception as e:
            print(f"Rate limit error: {e}")
            return True, {} # Fail open

rate_limiter = RateLimiter()

async def enforce_rate_limit(request: Request, auth_context: Optional[dict] = None):
    """
    Middleware to enforce rate limits.
    Priority: API Key > User ID > Client IP
    """
    # 1. Identify the 'entity' to rate limit
    limit_key = None
    tier = 'free'
    
    if auth_context:
        # B2B / Authenticated Path
        limit_key = auth_context.get('api_key_id') or f"user:{auth_context['user'].id}"
        plan = auth_context.get('plan')
        tier = plan.tier if plan else 'free'
    else:
        # Public / Guest Path (Fallback to IP)
        limit_key = f"ip:{request.client.host if request.client else 'unknown'}"
    
    # 2. Determine limit based on plan/tier
    # Agency: 1000 rpm, Master: 100 rpm, Basic/Free: 10 rpm
    limit = 10 # Default for free/guests
    if tier == 'agency':
        limit = 1000
    elif tier == 'master':
        limit = 100
    elif tier == 'practitioner':
        limit = 60
        
    allowed, info = rate_limiter.check_rate_limit(limit_key, limit)
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "limit": info.get('limit', limit),
                "retry_after": info.get('reset_at', 60)
            }
        )
    return info
