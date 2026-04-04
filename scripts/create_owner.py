import os
import sys
import uuid

# Add parent to path to load src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.core import SessionLocal
from src.database.models import User, SubscriptionPlan, UserSubscription
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def main():
    db = SessionLocal()
    
    # 1. Ensure practitioner plan exists
    plan = db.query(SubscriptionPlan).filter_by(tier="practitioner").first()
    if not plan:
        plan = SubscriptionPlan(
            id=str(uuid.uuid4()),
            tier="practitioner",
            price_monthly=29.00,
            features={"unlimited_horary": True}
        )
        db.add(plan)
        db.commit()
    
    # 2. Cleanup old "?"
    old_user = db.query(User).filter_by(email="?").first()
    if old_user:
        db.query(UserSubscription).filter(UserSubscription.user_id == old_user.id).delete()
        db.delete(old_user)
        db.commit()
        
    # 3. Create new "?"
    salt = os.urandom(16).hex()
    hashed = pwd_context.hash("720")
    
    new_user = User(
        id=str(uuid.uuid4()),
        email="?",
        name="?",
        password_hash=hashed,
        salt=salt
    )
    db.add(new_user)
    db.commit()
    
    # 4. Attach sub
    sub = UserSubscription(
        id=str(uuid.uuid4()),
        user_id=new_user.id,
        plan_id=plan.id,
        status="active"
    )
    db.add(sub)
    db.commit()
    
    print("Successfully created owner account '?' with password '720'")
    db.close()

if __name__ == "__main__":
    main()
