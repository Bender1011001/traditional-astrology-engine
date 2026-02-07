import sys
import os
# Ensure the project root is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.database.core import SessionLocal
from src.database.models import SubscriptionPlan

def update_onetime_price():
    db = SessionLocal()
    try:
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == "onetime").first()
        if plan:
            print(f"Updating plan {plan.tier} from {plan.stripe_price_id_monthly} to price_1Sw53FC8BJritqvrkgAS5xJD")
            plan.stripe_price_id_monthly = "price_1Sw53FC8BJritqvrkgAS5xJD"
            db.commit()
            print("Update successful.")
        else:
            print("Onetime plan not found.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_onetime_price()
