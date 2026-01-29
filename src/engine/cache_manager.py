import os
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "cache")

class CacheManager:
    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

    def _get_path(self, chart_hash: str, tier: str) -> str:
        # Separate cache by tier because free != paid content
        # Paid has full reading, Free has partial.
        # Although if paid exists, we can serve it to free users? No, maybe too generous?
        # Actually, if we have the paid version, we can just slice it for free users?
        # For simplicity, keep them separate or just cache by hash if logic permits.
        # But 'tier' implies permissions. Let's suffix the filename.
        return os.path.join(self.cache_dir, f"{chart_hash}_{tier}.json")

    def get(self, chart_hash: str, tier: str) -> Optional[Dict[str, Any]]:
        path = self._get_path(chart_hash, tier)
        if not os.path.exists(path):
            # Fallback: If requesting 'free', but we have 'paid', we could return 'paid' (technically allowed but might reveal too much?)
            # No, strictly return what was requested to avoid leaking paid content to free view logic if that logic is dumb.
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Check expiry (30 days)
            expires = data.get("expires")
            if expires and datetime.fromisoformat(expires) < datetime.utcnow():
                os.remove(path)
                return None
                
            return data["payload"]
        except Exception:
            return None

    def set(self, chart_hash: str, tier: str, payload: Dict[str, Any], ttl_days: int = 30) -> None:
        path = self._get_path(chart_hash, tier)
        expires = (datetime.utcnow().replace(microsecond=0) + datetime.timedelta(days=ttl_days)).isoformat()
        
        data = {
            "created": datetime.utcnow().isoformat(),
            "expires": expires,
            # We store the full API response usually, or just the reading part?
            # The API returns chart_data + reading + meta. 
            # Re-calculating chart data is cheap (pyswisseph). AI reading is expensive.
            # But ensuring consistency is good. Let's cache the whole result object.
            "payload": payload
        }
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Cache Write Error: {e}")

_cache = CacheManager()

def get_from_cache(chart_hash: str, tier: str):
    return _cache.get(chart_hash, tier)

def set_to_cache(chart_hash: str, tier: str, payload: Dict):
    _cache.set(chart_hash, tier, payload)
