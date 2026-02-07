import sys
import os
from decimal import Decimal

# Ensure the project root is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.database.core import SessionLocal
from src.database.models import SubscriptionPlan

def migrate_pricing():
    db = SessionLocal()
    try:
        print("Migrating Pricing Tiers...")
        
        # 1. Update B2C Onetime
        onetime = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == "onetime").first()
        if onetime:
            onetime.price_monthly = Decimal("197.00")
            onetime.stripe_price_id_monthly = "price_1SxueOC8BJritqvrAt2YvNcn"
            onetime.chart_quota = 1
            print("Updated Onetime tier.")

        # 2. Update/Create B2B tiers
        tiers = {
            "apprentice": {
                "price": Decimal("147.00"),
                "id": "price_1SxueOC8BJritqvrHz4dGn6k",
                "charts": 5,
                "api": 100,
                "features": {"audit": True, "forecasting": True, "pdf_export": True, "priority": False, "api_access": True}
            },
            "practitioner": {
                "price": Decimal("397.00"),
                "id": "price_1SxuePC8BJritqvrMv1gjTkP",
                "charts": 25,
                "api": 500,
                "features": {"audit": True, "forecasting": True, "pdf_export": True, "priority": True, "api_access": True}
            },
            "master": {
                "price": Decimal("797.00"),
                "id": "price_1SxuePC8BJritqvr760gXP4R",
                "charts": 100,
                "api": 2000,
                "features": {"audit": True, "forecasting": True, "pdf_export": True, "priority": True, "api_access": True, "slack_support": True}
            },
            "agency": {
                "price": Decimal("1297.00"),
                "id": "price_1SxuelC8BJritqvr3LxqqItk",
                "charts": None,
                "api": 50000,
                "features": {"api_access": True, "white_label": True, "dedicated_support": True}
            }
        }

        for tier, data in tiers.items():
            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == tier).first()
            if not plan:
                # Rename or Create
                # If 'starter' exists, rename to apprentice
                if tier == "apprentice":
                    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == "starter").first()
                    if plan:
                        plan.tier = "apprentice"
                        print("Renamed 'starter' to 'apprentice'.")
                
            if plan:
                plan.price_monthly = data["price"]
                plan.stripe_price_id_monthly = data["id"]
                plan.chart_quota = data["charts"]
                plan.api_quota = data["api"]
                plan.features = data["features"]
                print(f"Updated {tier} tier.")
            else:
                # Create if missing
                new_plan = SubscriptionPlan(
                    tier=tier,
                    price_monthly=data["price"],
                    stripe_price_id_monthly=data["id"],
                    chart_quota=data["charts"],
                    api_quota=data["api"],
                    features=data["features"]
                )
                db.add(new_plan)
                print(f"Created {tier} tier.")

        db.commit()
        print("Pricing migration successful.")
        
    except Exception as e:
        print(f"Error migrating pricing: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_pricing()
