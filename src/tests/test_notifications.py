import os
import sys
from unittest.mock import patch

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Mock environment variables before imports
os.environ["OWNER_EMAILS"] = "admin@example.com,boss@example.com"
os.environ["SITE_BASE_URL"] = "https://test.com"
os.environ["STRIPE_SECRET_KEY"] = "sk_test_123"
os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_123"
os.environ["JWT_SECRET"] = "test_jwt_secret"
os.environ["SENDER_EMAIL"] = "noreply@test.com"

from src.services.notifications import AdminNotificationService


def test_admin_notifications():
    print("Testing AdminNotificationService...")

    # Mock configuration to ensure emails are sent
    with patch("src.services.notifications.send_email") as mock_send, patch.dict(
        "os.environ", {"OWNER_EMAILS": "admin@example.com"}
    ):

        # Reload module/class config might be needed if it caches env var?
        # Check if AdminNotificationService reads env var at import or runtime.
        # Assuming runtime or property.

        # 1. Test Account Creation
        print("\nChecking notify_account_created...")
        AdminNotificationService.notify_account_created("user@test.com", "Test User")

        assert mock_send.call_count == 2
        args, kwargs = mock_send.call_args
        assert "New Account Created" in kwargs["subject"]
        assert "user@test.com" in kwargs["html_content"]
        assert "Test User" in kwargs["html_content"]
        print("✓ Account creation notification sent to all admins.")

        mock_send.reset_mock()

        # 2. Test Purchase Completion
        print("\nChecking notify_purchase_completed...")
        AdminNotificationService.notify_purchase_completed(
            "buyer@test.com", "practitioner", 397.0, is_recurring=True
        )

        assert mock_send.call_count == 2
        args, kwargs = mock_send.call_args
        assert "New Subscription" in kwargs["subject"]
        assert "PRACTITIONER" in kwargs["subject"]
        assert "buyer@test.com" in kwargs["html_content"]
        assert "$397.00" in kwargs["html_content"]
        print("✓ Purchase notification sent to all admins.")

        mock_send.reset_mock()

        # 3. Test Payment Failure
        print("\nChecking notify_payment_failed...")
        AdminNotificationService.notify_payment_failed(
            "poor_soul@test.com", "apprentice", "Insufficient funds"
        )

        assert mock_send.call_count == 2
        args, kwargs = mock_send.call_args
        assert "PAYMENT FAILED" in kwargs["subject"]
        assert "poor_soul@test.com" in kwargs["subject"]
        assert "Insufficient funds" in kwargs["html_content"]
        print("✓ Payment failure notification sent to all admins.")

    print("\nAll notification tests passed!")


if __name__ == "__main__":
    try:
        test_admin_notifications()
    except Exception as e:
        print(f"\nTests FAILED: {e}")
        sys.exit(1)
