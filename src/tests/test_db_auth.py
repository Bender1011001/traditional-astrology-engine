
import sys
import os
import shutil

# Setup paths
import sys
import os
import shutil

# Setup paths
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine.user_auth import get_user_manager

def test_auth_flow():
    # Use a fresh DB for test (users.db is created in cwd by default)
    # in source code location e:\code.projects\astrology
    
    manager = get_user_manager()
    
    email = "test@example.com"
    password = "securePassword123"
    
    # 1. Create
    print("Creating user...")
    res = manager.create_user(email, password, "Test User")
    print(f"Create Result: {res}")
    
    if not res["success"]:
        print("FAILED to create user")
        # cleanup?
        return

    # 2. Login
    print("Logging in...")
    login_res = manager.authenticate(email, password)
    print(f"Login Result: {login_res}")
    if not login_res["success"]:
        print("FAILED to login")
        return

    # 3. Save Chart
    print("Saving chart...")
    save_res = manager.save_chart(email, "some_hash_123", {"city": "New York"})
    print(f"Save Result: {save_res}")
    
    # 4. Verify Fetch
    print("Fetching user...")
    user = manager.get_user_by_email(email)
    print(f"User Data: {user}")
    
    if len(user["charts_saved"]) == 1:
        print("PASS: Chart saved and retrieved.")
    else:
        print("FAIL: Chart not saved.")

if __name__ == "__main__":
    try:
        test_auth_flow()
    except Exception as e:
        print(f"CRASH: {e}")
