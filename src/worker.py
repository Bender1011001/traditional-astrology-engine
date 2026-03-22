import time
import schedule
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timezone
from src.database.core import SessionLocal
from src.database.models import UserSubscription, SubscriptionPlan
from src.services.subscription import SubscriptionService

def run_trial_cleanup():
    print(f"[{datetime.now(timezone.utc)}] Running Trial Cleanup...")
    db: Session = SessionLocal()
    try:
        service = SubscriptionService(db)
        free_plan = service.get_plan_by_tier("free")
        if not free_plan:
            print("Error: Free plan not found in DB.")
            return

        # Find expired trials
        expired_subs = db.query(UserSubscription).filter(
            UserSubscription.status == 'trial',
            UserSubscription.trial_end_date < datetime.now(timezone.utc)
        ).all()

        if not expired_subs:
            print("No expired trials found.")
            return

        print(f"Found {len(expired_subs)} expired trials. Downgrading...")
        
        for sub in expired_subs:
            print(f"Downgrading User {sub.user_id}...")
            sub.status = "active"
            sub.plan_id = free_plan.id
            sub.trial_end_date = None
            # Optionally send email notification here
            
        db.commit()
        print("Cleanup complete.")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # If run directly, run once then enter schedule loop? 
    # Or just run once. Docker container might run this via cron.
    # For now, let's make it loop every hour.
    
    print("Starting Worker...")
    run_trial_cleanup() # Run once on start
    
    schedule.every(1).hours.do(run_trial_cleanup)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
