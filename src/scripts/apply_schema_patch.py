import sys
import os
import sqlalchemy
from sqlalchemy import text, inspect

# Ensure the project root is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.database.core import engine

def patch_database():
    print(f"Connecting to database...")
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # 1. Patch 'subscription_plans'
        print("Checking 'subscription_plans'...")
        columns = [c['name'] for c in inspector.get_columns('subscription_plans')]
        
        if 'api_quota' not in columns:
            print("  Adding 'api_quota'...")
            conn.execute(text("ALTER TABLE subscription_plans ADD COLUMN api_quota INTEGER"))
            
        if 'price_annual' not in columns:
            print("  Adding 'price_annual'...")
            # Numeric(10, 2) roughly translates to DECIMAL(10, 2) in generic SQL
            conn.execute(text("ALTER TABLE subscription_plans ADD COLUMN price_annual NUMERIC(10, 2)"))
            
        if 'stripe_price_id_annual' not in columns:
            print("  Adding 'stripe_price_id_annual'...")
            conn.execute(text("ALTER TABLE subscription_plans ADD COLUMN stripe_price_id_annual VARCHAR"))

        # 2. Patch 'user_subscriptions'
        print("Checking 'user_subscriptions'...")
        columns_subs = [c['name'] for c in inspector.get_columns('user_subscriptions')]
        
        if 'stripe_subscription_id' not in columns_subs:
            print("  Adding 'stripe_subscription_id'...")
            conn.execute(text("ALTER TABLE user_subscriptions ADD COLUMN stripe_subscription_id VARCHAR"))
            
        if 'trial_start_date' not in columns_subs:
            print("  Adding 'trial_start_date'...")
            conn.execute(text("ALTER TABLE user_subscriptions ADD COLUMN trial_start_date TIMESTAMP"))

        if 'trial_end_date' not in columns_subs:
            print("  Adding 'trial_end_date'...")
            conn.execute(text("ALTER TABLE user_subscriptions ADD COLUMN trial_end_date TIMESTAMP"))
            
        if 'current_period_start' not in columns_subs:
            print("  Adding 'current_period_start'...")
            conn.execute(text("ALTER TABLE user_subscriptions ADD COLUMN current_period_start TIMESTAMP"))
            
        if 'cancel_at_period_end' not in columns_subs:
            print("  Adding 'cancel_at_period_end'...")
            conn.execute(text("ALTER TABLE user_subscriptions ADD COLUMN cancel_at_period_end BOOLEAN DEFAULT FALSE"))

        conn.commit()
        print("Database patch completed successfully.")

if __name__ == "__main__":
    try:
        patch_database()
    except Exception as e:
        print(f"Error patching database: {e}")
        sys.exit(1)
