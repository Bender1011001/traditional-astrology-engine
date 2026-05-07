import os
import sys


# Ensure the project root is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.database.core import SessionLocal
from src.database.models import User
from src.services.subscription import SubscriptionService


def test_onetime_purchase_flow():
    db = SessionLocal()
    try:
        from src.engine.user_auth import get_user_manager

        manager = get_user_manager()

        # 1. Ensure a test user exists
        test_email = "test_customer_automated@example.com"
        user_data = manager.get_user_by_email(test_email)

        if not user_data:
            result = manager.create_user(
                test_email, "testpassword", "Automated Test Customer"
            )
            if not result["success"]:
                print(f"Failed to create user: {result['message']}")
                assert False, f"Failed to create user: {result['message']}"
            user_id = result["user"]["id"]
            print(f"Created test user: {test_email} (ID: {user_id})")
        else:
            user_id = user_data["id"]
            print(f"Using existing test user: {test_email} (ID: {user_id})")

        user = db.query(User).filter(User.id == user_id).first()

        # 2. Create Service
        service = SubscriptionService(db)

        # Override placeholder for test with actual live ID detected
        # price_1Sw53FC8BJritqvrkgAS5xJD - Full Forensic Report ($9.99)
        live_onetime_price = "price_1Sw53FC8BJritqvrkgAS5xJD"

        # 3. Create Checkout Session for 'onetime' tier
        # We manually pass the session creation logic to use the live ID if the DB has placeholder
        plan = service.get_plan_by_tier("onetime")
        plan.stripe_price_id_monthly = (
            live_onetime_price  # Temporary override for this session
        )

        session = service.create_checkout_session(
            user=user,
            plan_tier="onetime",
            success_url="https://astrology.example.com/success",
            cancel_url="https://astrology.example.com/cancel",
        )

        print(f"Created Checkout Session ID: {session.id}")
        print(f"Checkout URL: {session.url}")

        assert session.url is not None

    finally:
        db.close()


if __name__ == "__main__":
    test_onetime_purchase_flow()
