import sys
import os

# Ensure src in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.database.core import SessionLocal
from src.database.models import SubscriptionPlan

def update_prices():
    print("--- Stripe Price ID Updater ---")
    print("This script will update the Stripe Price IDs in your database.")
    print("You can find these IDs in your Stripe Dashboard (starts with 'price_...').")
    
    db = SessionLocal()
    try:
        plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.price_monthly > 0).all()
        
        for plan in plans:
            print(f"\nPLAN: {plan.tier.upper()} (${plan.price_monthly}/mo)")
            print(f"Current ID: {plan.stripe_price_id_monthly}")
            
            new_id = input(f"Enter new Price ID for {plan.tier} (or press Enter to keep current): ").strip()
            
            if new_id:
                plan.stripe_price_id_monthly = new_id
                print(f"Updated {plan.tier} to {new_id}")
            else:
                print("No change.")
        
        db.commit()
        print("\nSUCCESS: Price IDs updated.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_prices()
