import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.engine.user_auth import get_user_manager
    print("Import successful.")
    
    manager = get_user_manager()
    print("Manager initialized.")
    
    email = "test@example.com"
    password = "password123"
    
    # Try creating user first to ensure it exists (ignore error if exists)
    print("Creating user...")
    try:
        manager.create_user(email, password, "Test User")
    except Exception as e:
        print(f"Create user exception (expected if exists): {e}")

    print("Authenticating...")
    result = manager.authenticate(email, password)
    print(f"Authentication result: {result}")

except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()
