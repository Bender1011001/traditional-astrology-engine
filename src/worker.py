import time
import logging
import schedule
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from src.database.core import SessionLocal
from src.database.models import UserSubscription, SubscriptionPlan
from src.services.subscription import SubscriptionService

logger = logging.getLogger(__name__)

def run_trial_cleanup():
    logger.info("Running Trial Cleanup...")
    db: Session = SessionLocal()
    try:
        service = SubscriptionService(db)
        free_plan = service.get_plan_by_tier("free")
        if not free_plan:
            logger.error("Free plan not found in DB. Cannot downgrade expired trials.")
            return

        # Find expired trials
        expired_subs = db.query(UserSubscription).filter(
            UserSubscription.status == 'trial',
            UserSubscription.trial_end_date < datetime.now(timezone.utc)
        ).all()

        if not expired_subs:
            logger.info("No expired trials found.")
            return

        logger.info("Found %d expired trials. Downgrading...", len(expired_subs))
        
        for sub in expired_subs:
            logger.info("Downgrading User %s from trial to free plan.", sub.user_id)
            sub.status = "active"
            sub.plan_id = free_plan.id
            sub.trial_end_date = None
            
        db.commit()
        logger.info("Trial cleanup complete.")
        
    except Exception as e:
        logger.exception("Error during trial cleanup: %s", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    
    logger.info("Starting Worker...")
    run_trial_cleanup()  # Run once on start
    
    schedule.every(1).hours.do(run_trial_cleanup)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
