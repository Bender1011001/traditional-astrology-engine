import redis
from datetime import datetime
from src.core.config import settings

class RateLimiter:
    def __init__(self):
        # Initialize Redis connection
        # If REDIS_URL is default (localhost), it might fail if redis not running.
        # Fallback to in-memory? Plan says "Support high-volume B2B clients using Redis."
        # If we want robustness, we can try-except connect.
        try:
            self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.redis.ping() # Test connection
            self.use_redis = True
        except Exception as e:
            print(f"Redis connection failed: {e}. Falling back to in-memory.")
            self.use_redis = False
            self._requests = {}

        self.DAILY_LIMIT = 5
        self.WINDOW_SECONDS = 86400 # 24 hours

    def is_allowed(self, ip: str) -> bool:
        if self.use_redis:
            key = f"rate_limit:{ip}"
            try:
                # INCR returns new value
                count = self.redis.incr(key)
                if count == 1:
                    self.redis.expire(key, self.WINDOW_SECONDS)
                
                if count > self.DAILY_LIMIT:
                    return False
                return True
            except Exception:
                # Redis failure during op?
                return True # Fail open? Or closed?
        else:
            # In-memory fallback
            now = datetime.utcnow().timestamp()
            if ip not in self._requests:
                self._requests[ip] = []
            self._requests[ip] = [t for t in self._requests[ip] if now - t < self.WINDOW_SECONDS]
            if len(self._requests[ip]) >= self.DAILY_LIMIT:
                return False
            self._requests[ip].append(now)
            return True

rate_limiter = RateLimiter()
