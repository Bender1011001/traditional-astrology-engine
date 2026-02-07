import sys
import os
import uuid

# Ensure the project root is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.database.core import engine, Base, SessionLocal
from src.database.models import SubscriptionPlan, User, UserSubscription

def seed_plans():
    db = SessionLocal()
    try:
        # Check if plans exist
        existing = db.query(SubscriptionPlan).count()
        if existing > 0:
            print("Plans already exist using new schema. Skipping.")
            return

        print("Seeding Subscription Plans...")
        
        plans = [
            SubscriptionPlan(
                tier="free",
                chart_quota=1, # First report free incentive
                api_quota=0,
                price_monthly=0.00,
                price_annual=0.00,
                stripe_price_id_monthly=None,
                stripe_price_id_annual=None,
                features={"audit": False, "forecasting": False, "advanced": False, "ai_readings": True}
            ),
            SubscriptionPlan(
                tier="onetime",
                chart_quota=1, 
                api_quota=0,
                price_monthly=197.00,
                price_annual=0.00,
                stripe_price_id_monthly="price_1SxueOC8BJritqvrAt2YvNcn", # $197 B2C
                stripe_price_id_annual=None,
                features={"audit": True, "forecasting": True, "details": True, "timeline": True}
            ),
            SubscriptionPlan(
                tier="apprentice",
                chart_quota=5,
                api_quota=100, # Basic API access
                price_monthly=147.00,
                price_annual=1470.00,
                stripe_price_id_monthly="price_1SxueOC8BJritqvrHz4dGn6k", # $147 Apprentice
                stripe_price_id_annual=None, # TBD
                features={"audit": True, "forecasting": True, "pdf_export": True, "priority": False, "api_access": True}
            ),
            SubscriptionPlan(
                tier="practitioner",
                chart_quota=25,
                api_quota=500,
                price_monthly=397.00,
                price_annual=3970.00,
                stripe_price_id_monthly="price_1SxuePC8BJritqvrMv1gjTkP", # $397 Practitioner
                stripe_price_id_annual=None,
                features={"audit": True, "forecasting": True, "pdf_export": True, "priority": True, "api_access": True}
            ),
            SubscriptionPlan(
                tier="master",
                chart_quota=100,
                api_quota=2000,
                price_monthly=797.00,
                price_annual=7970.00,
                stripe_price_id_monthly="price_1SxuePC8BJritqvr760gXP4R", # $797 Master
                stripe_price_id_annual=None,
                features={"audit": True, "forecasting": True, "pdf_export": True, "priority": True, "api_access": True, "slack_support": True}
            ),
            SubscriptionPlan(
                tier="agency",
                chart_quota=None, # Unlimited
                api_quota=50000,
                price_monthly=1297.00, # Example high tier
                price_annual=12970.00,
                stripe_price_id_monthly="price_1SxuelC8BJritqvr3LxqqItk", # $1297 Agency
                stripe_price_id_annual=None,
                features={"api_access": True, "white_label": True, "dedicated_support": True}
            )
        ]
        
        db.add_all(plans)
        db.commit()
        print("Plans seeded successfully.")
        
    except Exception as e:
        print(f"Error seeding plans: {e}")
        db.rollback()
    finally:
        db.close()

def reset_db():
    print("Resetting Database (Clean Break)...")
    # Dropping all tables to ensure clean slate for new schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database tables recreated.")

if __name__ == "__main__":
    seed_plans()
