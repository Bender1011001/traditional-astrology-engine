import logging
import time
from datetime import datetime, timezone

import schedule
from sqlalchemy.orm import Session

from src.database.core import SessionLocal
from src.database.models import UserSubscription
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

        batch_size = 100
        total_processed = 0

        while True:
            # Find expired trials in batches to prevent memory OOM and DB locks
            expired_subs = (
                db.query(UserSubscription)
                .filter(
                    UserSubscription.status == "trial",
                    UserSubscription.trial_end_date < datetime.now(timezone.utc),
                )
                .limit(batch_size)
                .all()
            )

            if not expired_subs:
                break

            logger.info(
                "Found %d expired trials in current batch. Downgrading...",
                len(expired_subs),
            )

            for sub in expired_subs:
                sub.status = "active"
                sub.plan_id = free_plan.id
                sub.trial_end_date = None

            db.commit()
            total_processed += len(expired_subs)

        logger.info("Trial cleanup complete. Total downgraded: %d", total_processed)

    except Exception as e:
        logger.error("Error during trial cleanup: %s", repr(e), exc_info=True)
        try:
            db.rollback()
        except Exception:
            pass
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s"
    )

    logger.info("Starting Worker...")
    run_trial_cleanup()  # Run once on start

    schedule.every(1).hours.do(run_trial_cleanup)

    while True:
        schedule.run_pending()
        time.sleep(60)
