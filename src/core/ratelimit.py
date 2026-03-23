import redis
import logging
from datetime import datetime, timezone
from src.core.config import settings

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        # Initialize Redis connection
        # If REDIS_URL is default (localhost), it might fail if redis not running.
        # Fallback to in-memory? Plan says "Support high-volume B2B clients using Redis."
        # If we want robustness, we can try-except connect.
        if settings.REDIS_URL:
            try:
                self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
                self.redis.ping() # Test connection
                self.use_redis = True
            except Exception as e:
                logger.warning("Redis connection failed: %s. Falling back to in-memory.", e)
                self.use_redis = False
                self._requests = {}
        else:
            self.use_redis = False
            self._requests = {}

        self.DAILY_LIMIT = max(0, int(getattr(settings, "FREE_SINGLE_READINGS_PER_IP", 3)))
        self.WINDOW_SECONDS = max(60, int(getattr(settings, "FREE_SINGLE_READINGS_WINDOW_SECONDS", 86400)))

    def consume_free_reading(self, ip: str) -> dict:
        """
        Consume one free reading credit for an IP and return limit status.
        """
        if self.DAILY_LIMIT <= 0:
            return {"allowed": False, "count": 0, "remaining": 0, "limit": 0}

        if self.use_redis:
            key = f"free_reading:{ip}"
            try:
                count = int(self.redis.incr(key))
                if count == 1:
                    self.redis.expire(key, self.WINDOW_SECONDS)

                allowed = count <= self.DAILY_LIMIT
                remaining = max(0, self.DAILY_LIMIT - count)
                return {
                    "allowed": allowed,
                    "count": count,
                    "remaining": remaining,
                    "limit": self.DAILY_LIMIT,
                }
            except Exception as e:
                logger.debug("Redis rate limit check failed, using in-memory fallback: %s", e)

        now = datetime.now(timezone.utc).timestamp()
        if ip not in self._requests:
            self._requests[ip] = []

        self._requests[ip] = [t for t in self._requests[ip] if now - t < self.WINDOW_SECONDS]
        current_count = len(self._requests[ip])
        if current_count >= self.DAILY_LIMIT:
            return {
                "allowed": False,
                "count": current_count,
                "remaining": 0,
                "limit": self.DAILY_LIMIT,
            }

        self._requests[ip].append(now)
        new_count = len(self._requests[ip])
        return {
            "allowed": True,
            "count": new_count,
            "remaining": max(0, self.DAILY_LIMIT - new_count),
            "limit": self.DAILY_LIMIT,
        }

    def is_allowed(self, ip: str) -> bool:
        return bool(self.consume_free_reading(ip).get("allowed"))

rate_limiter = RateLimiter()
