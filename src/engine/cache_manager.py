import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Use /tmp for ephemeral caching on serverless/container platforms
import tempfile
import base64
CACHE_DIR = os.getenv("CACHE_DIR", os.path.join(tempfile.gettempdir(), "astrology_cache"))

try:
    from cryptography.fernet import Fernet
    _HAS_CRYPTO = True
except ImportError:
    _HAS_CRYPTO = False
    logger.warning("'cryptography' library not found. Cache encryption disabled.")

class CacheManager:
    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir, exist_ok=True)
            except OSError:
                # Fallback to local temp if permission denied (rare in /tmp)
                self.cache_dir = os.path.join(tempfile.gettempdir(), "astrology_cache")
                os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize Encryption
        self.key = os.getenv("CACHE_ENCRYPTION_KEY")
        if not self.key:
             # Just a consistent fallback for dev, explicitly insecure but functional
             # In prod, this SHOULD be set.
             self.key = "change_me_in_production_env_var_to_32_bytes_base64"
             
        self.fernet = None
        if _HAS_CRYPTO:
            try:
                # Ensure key is valid base64 url safe 32 bytes
                # If the env var is just a string, we might need to hash it to get a key?
                # Fernet requires 32 url-safe base64-encoded bytes.
                # Let's derive a key if it's not proper.
                if len(self.key) != 44 or not self.key.endswith("="):
                     # Derive valid key from whatever string was provided
                     k = hashlib.sha256(self.key.encode()).digest()
                     self.key = base64.urlsafe_b64encode(k).decode()
                
                self.fernet = Fernet(self.key)
            except Exception as e:
                logger.warning("Encryption Init Error: %s", e)
                
    def _encrypt(self, data: str) -> str:
        if self.fernet:
            return self.fernet.encrypt(data.encode()).decode()
        return data

    def _decrypt(self, data: str) -> str:
        if self.fernet:
            return self.fernet.decrypt(data.encode()).decode()
        return data

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
                content = f.read()
            
            try:
                decrypted = self._decrypt(content)
                data = json.loads(decrypted)
            except Exception as e:
                logger.debug("Cache decrypt/parse failed: %s", e)
                # Decryption failed or JSON error -> invalid cache
                return None
            
            # Check expiry (30 days)
            expires = data.get("expires")
            if expires and datetime.fromisoformat(expires) < datetime.utcnow():
                os.remove(path)
                return None
                
            return data["payload"]
        except Exception as e:
            logger.debug("Cache read failed: %s", e)
            return None

    def set(self, chart_hash: str, tier: str, payload: Dict[str, Any], ttl_days: int = 30) -> None:
        path = self._get_path(chart_hash, tier)
        expires = (datetime.utcnow().replace(microsecond=0) + timedelta(days=ttl_days)).isoformat()
        
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
            json_str = json.dumps(data)
            encrypted = self._encrypt(json_str)
            with open(path, "w", encoding="utf-8") as f:
                f.write(encrypted)
        except Exception as e:
            logger.warning("Cache Write Error: %s", e)

_cache = CacheManager()

def get_from_cache(chart_hash: str, tier: str):
    return _cache.get(chart_hash, tier)

def set_to_cache(chart_hash: str, tier: str, payload: Dict):
    _cache.set(chart_hash, tier, payload)
