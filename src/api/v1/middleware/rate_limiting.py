import logging
import time
from datetime import datetime, timezone
from typing import Optional

import redis
from fastapi import HTTPException, Request

from src.api.v1.client_ip import get_client_ip
from src.core.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter using Redis"""

    def __init__(self):
        self.redis = None
        self.memory_store = {}  # Fallback
        if settings.REDIS_URL:
            try:
                self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception as e:
                logger.warning("Redis connection failed: %s", repr(e), exc_info=True)

    def check_rate_limit(
        self, user_id: str, limit_per_minute: int = 60
    ) -> tuple[bool, dict]:
        """
        Check if request is within rate limit
        """
        if self.redis:
            try:
                # Redis Strategy
                key = f"rate_limit:{user_id}:{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}"
                current = self.redis.incr(key)
                if current == 1:
                    self.redis.expire(key, 60)

                allowed = current <= limit_per_minute
                remaining = max(0, limit_per_minute - current)
                return allowed, {
                    "limit": limit_per_minute,
                    "remaining": remaining,
                    "reset_at": 60,
                }
            except Exception as e:
                logger.warning(
                    "Redis rate limit error: %s. Falling back to memory.",
                    repr(e),
                    exc_info=True,
                )
                # Fall through to memory

        # In-Memory Strategy (Fallback)
        # Simple window based on current minute
        current_minute = int(time.time() / 60)
        key = f"{user_id}:{current_minute}"

        # Cleanup old keys (naive garbage collection)
        if len(self.memory_store) > 10000:
            self.memory_store.clear()

        current = self.memory_store.get(key, 0)
        current += 1
        self.memory_store[key] = current

        allowed = current <= limit_per_minute
        remaining = max(0, limit_per_minute - current)

        return allowed, {
            "limit": limit_per_minute,
            "remaining": remaining,
            "reset_at": 60,
            "backend": "memory",
        }


rate_limiter = RateLimiter()


async def enforce_rate_limit(request: Request, auth_context: Optional[dict] = None):
    """
    Middleware to enforce rate limits.
    Priority: API Key > User ID > Client IP
    """
    # 1. Identify the 'entity' to rate limit
    limit_key = None
    tier = "free"

    if auth_context:
        # B2B / Authenticated Path
        limit_key = auth_context.get("api_key_id") or f"user:{auth_context['user'].id}"
        plan = auth_context.get("plan")
        tier = plan.tier if plan else "free"
    else:
        # Public / Guest Path (Fallback to IP)
        limit_key = f"ip:{get_client_ip(request)}"

    # 2. Determine limit based on plan/tier (requests/minute)
    limit = 10  # Default for free/guests
    if tier == "agency":
        limit = 1000
    elif tier == "studio":
        limit = 120
    elif tier == "practitioner":
        limit = 60

    allowed, info = rate_limiter.check_rate_limit(limit_key, limit)

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "limit": info.get("limit", limit),
                "retry_after": info.get("reset_at", 60),
            },
        )
    return info
