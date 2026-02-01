from fastapi import HTTPException
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

async def enforce_rate_limit(auth_context: dict):
    """Middleware to enforce rate limits for B2B clients"""
    if not auth_context:
        return # Skip if not B2B authenticated

    user = auth_context['user']
    plan = auth_context['plan']
    
    # Determine limit based on plan
    limit = 60 # Default
    if plan.tier == 'agency':
        limit = 1000
    elif plan.tier == 'master':
        limit = 100
        
    allowed, info = rate_limiter.check_rate_limit(user.id, limit)
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "limit": info['limit']
            }
        )
    return info
