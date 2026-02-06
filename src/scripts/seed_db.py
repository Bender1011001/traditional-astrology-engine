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
                chart_quota=10,
                api_quota=0,
                price_monthly=0.00,
                price_annual=0.00,
                stripe_price_id_monthly=None,
                stripe_price_id_annual=None,
                features={"audit": False, "forecasting": False, "advanced": False, "ai_readings": True}
            ),
            SubscriptionPlan(
                tier="onetime",
                chart_quota=0, # Not used for onetime as subscription
                api_quota=0,
                price_monthly=9.99,
                price_annual=0.00,
                stripe_price_id_monthly="price_PLACEHOLDER_ONETIME",
                stripe_price_id_annual=None,
                features={"audit": True, "forecasting": True, "details": True, "timeline": True}
            ),
            SubscriptionPlan(
                tier="starter",
                chart_quota=50,
                api_quota=0,
                price_monthly=29.00,
                price_annual=290.00,
                stripe_price_id_monthly="price_1Sw58CC8BJritqvrOIMIuAXJ",
                stripe_price_id_annual="price_1Sw58lC8BJritqvrJyFBgy98",
                features={"audit": True, "forecasting": True, "pdf_export": True, "priority": True}
            ),
            SubscriptionPlan(
                tier="practitioner",
                chart_quota=None, # Unlimited
                api_quota=0,
                price_monthly=149.00,
                price_annual=1490.00,
                stripe_price_id_monthly="price_1Sw58LC8BJritqvroIwC3kEM",
                stripe_price_id_annual="price_1Sw58mC8BJritqvrWsCXUtqc",
                features={"audit": True, "forecasting": True, "commercial": True, "bulk_upload": True, "templates": True}
            ),
            SubscriptionPlan(
                tier="master",
                chart_quota=None,
                api_quota=3000, # 100/day
                price_monthly=299.00,
                price_annual=2990.00,
                stripe_price_id_monthly="price_1Sw58UC8BJritqvr8oNM3sLX",
                stripe_price_id_annual="price_1Sw58mC8BJritqvru65F49Nd",
                features={"api_access": True, "white_label": True, "webhooks": True}
            ),
            SubscriptionPlan(
                tier="agency",
                chart_quota=None,
                api_quota=30000, # 1000/day
                price_monthly=799.00,
                price_annual=7990.00,
                stripe_price_id_monthly="price_1Sw58cC8BJritqvrZKoQOCzR",
                stripe_price_id_annual="price_1Sw58mC8BJritqvrPqfyFdnJ",
                features={"api_access": True, "white_label": True, "sla": True, "dedicated_support": True}
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
