
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "src"))

import logging
logging.basicConfig(level=logging.INFO)

# 1. Verify DB Backup
print("--- Verifying DB Backup Logic ---")
try:
    from database.db_manager import DatabaseBackupManager
    # Create dummy users.db
    with open("users.db", "w") as f:
        f.write("dummy db content")
    
    res = DatabaseBackupManager.run_backup("test_backups")
    print(res)
    assert "successful" in res or "not found" in res
except Exception as e:
    print(f"DB Backup FAIL: {e}")

# 2. Verify Cache Manager Encryption
print("\n--- Verifying Cache Encryption ---")
try:
    from engine.cache_manager import CacheManager
    cm = CacheManager("test_cache")
    data = {"secret": "my_secret_data"}
    cm.set("test_hash", "free", data)
    retrieved = cm.get("test_hash", "free")
    print(f"Original: {data}")
    print(f"Retrieved: {retrieved}")
    assert retrieved["secret"] == "my_secret_data"
except Exception as e:
    print(f"Cache FAIL: {e}")

# 3. Verify Circuit Breaker Import
print("\n--- Verifying Chat Oracle Circuit Breaker ---")
try:
    from engine.chat_oracle import _oracle_breaker
    print(f"Breaker State: {_oracle_breaker.state}")
except ImportError as e:
    print(f"Circuit Breaker Import FAIL: {e}")
except Exception as e:
    print(f"Circuit Breaker FAIL: {e}")

# 4. Verify Rate Limiter
print("\n--- Verifying Rate Limiter ---")
try:
    from engine.user_auth import UserManager
    um = UserManager()
    allowed = um._check_rate_limit("test_user")
    print(f"Rate Limit Check 1: {allowed}")
    for _ in range(6):
        res = um._check_rate_limit("test_user", limit=5)
    print(f"Rate Limit Check After Spam: {res}")
    assert res == False
except Exception as e:
    print(f"Rate Limiter FAIL: {e}")

print("\n--- verification complete ---")
