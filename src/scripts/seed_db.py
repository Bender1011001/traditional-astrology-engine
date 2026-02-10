import sys
import os
import uuid

# Ensure the project root is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.database.core import engine, Base, SessionLocal
from src.database.models import SubscriptionPlan, User, UserSubscription
from src.core.config import settings

def seed_plans():
    db = SessionLocal()
    try:
        print("Ensuring Subscription Plans exist (upsert)...")

        desired = [
            {
                "tier": "free",
                "chart_quota": None,  # The public demo is rate-limited; signed-in users are not hard-capped here.
                "api_quota": 0,       # No API keys for free plan.
                "price_monthly": 0.00,
                "price_annual": 0.00,
                "stripe_price_id_monthly": None,
                "stripe_price_id_annual": None,
                "features": {"api_access": False}
            },
            {
                "tier": "practitioner",
                "chart_quota": None,  # Unlimited calculations (per plan).
                "api_quota": 100,     # API calls/day
                "price_monthly": 147.00,
                "price_annual": 1470.00,
                "stripe_price_id_monthly": settings.STRIPE_PRICE_PRACTITIONER_MONTHLY or None,
                "stripe_price_id_annual": settings.STRIPE_PRICE_PRACTITIONER_ANNUAL or None,
                "features": {"api_access": True, "saved_charts_limit": 100}
            },
            {
                "tier": "studio",
                "chart_quota": None,  # Unlimited calculations (per plan).
                "api_quota": None,    # Unlimited API calls/day
                "price_monthly": 497.00,
                "price_annual": 4970.00,
                "stripe_price_id_monthly": settings.STRIPE_PRICE_STUDIO_MONTHLY or None,
                "stripe_price_id_annual": settings.STRIPE_PRICE_STUDIO_ANNUAL or None,
                "features": {"api_access": True, "saved_charts_limit": None, "seats": 5}
            }
        ]

        for d in desired:
            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == d["tier"]).first()
            if not plan:
                plan = SubscriptionPlan(tier=d["tier"])
                db.add(plan)

            plan.chart_quota = d["chart_quota"]
            plan.api_quota = d["api_quota"]
            plan.price_monthly = d["price_monthly"]
            plan.price_annual = d["price_annual"]
            plan.stripe_price_id_monthly = d["stripe_price_id_monthly"]
            plan.stripe_price_id_annual = d["stripe_price_id_annual"]
            plan.features = d["features"]

        db.commit()
        print("Plans ensured successfully.")
        
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
