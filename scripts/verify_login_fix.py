
import sys
import os
import uuid

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.user_auth import UserManager
from src.database.models import User, UserSubscription
from src.database.core import SessionLocal

def verify_user_creation():
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = "StrongPassword123!"
    
    print(f"Attempting to create user: {email}")
    
    um = UserManager()
    result = um.create_user(email, password, "Test User")
    
    if result["success"]:
        print("User creation SUCCESS.")
        user_id = result["user"]["id"]
        
        # Verify subscription exists
        db = SessionLocal()
        try:
            sub = db.query(UserSubscription).filter(UserSubscription.user_id == user_id).first()
            if sub:
                print(f"Subscription verification SUCCESS. Plan ID: {sub.plan_id}, Status: {sub.status}")
                if sub.status == "trial":
                     print("Status is TRIAL (Expected if start_trial was called)")
                elif sub.status == "active":
                     print("Status is ACTIVE (Expected if free plan was assigned)")
                else:
                     print(f"Status is {sub.status}")
            else:
                print("Subscription verification FAILED. No subscription found.")
        finally:
            db.close()
    else:
        print(f"User creation FAILED: {result.get('message')}")
        sys.exit(1)

if __name__ == "__main__":
    verify_user_creation()
