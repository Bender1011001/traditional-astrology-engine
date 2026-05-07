import logging
import os

from src.core.config import settings
from src.engine.email_service import send_email


class AdminNotificationService:
    """
    Service for sending notifications to site administrators.
    """

    @staticmethod
    def _get_admin_emails():
        """
        Returns a list of admin emails.

        Notes:
        - In prod, OWNER_EMAILS is the primary list.
        - In tests, settings may be instantiated before env vars are patched; we also consult os.environ at runtime.
        - We include SENDER_EMAIL as a safe fallback/copy recipient so admin events are never silently dropped.
        """
        raw = []
        if getattr(settings, "OWNER_EMAILS", ""):
            raw.append(settings.OWNER_EMAILS)
        env_owner = os.environ.get("OWNER_EMAILS", "")
        if env_owner:
            raw.append(env_owner)

        emails = []
        for blob in raw:
            for email in blob.split(","):
                email = email.strip()
                if email and email not in emails:
                    emails.append(email)

        sender = (
            getattr(settings, "SENDER_EMAIL", "").strip()
            if getattr(settings, "SENDER_EMAIL", None)
            else ""
        )
        if sender and sender not in emails:
            emails.append(sender)

        return emails

    @staticmethod
    def notify_account_created(user_email: str, user_name: str = ""):
        """Notifies admin when a new account is created."""
        admin_emails = AdminNotificationService._get_admin_emails()
        if not admin_emails:
            logging.warning(
                "No OWNER_EMAILS configured for account creation notification."
            )
            return

        subject = f"New Account Created: {user_email}"
        name_display = f" ({user_name})" if user_name else ""
        html_content = f"""
        <h2>New User Registration</h2>
        <p>A new user has registered on <b>{settings.SITE_BASE_URL}</b>.</p>
        <ul>
            <li><b>Email:</b> {user_email}</li>
            <li><b>Name:</b> {user_name or 'N/A'}</li>
            <li><b>Time:</b> {logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', None, None), '%Y-%m-%d %H:%M:%S')}</li>
        </ul>
        """

        for admin_email in admin_emails:
            send_email(to_email=admin_email, subject=subject, html_content=html_content)

    @staticmethod
    def notify_purchase_completed(
        user_email: str, plan_tier: str, amount: float = 0.0, is_recurring: bool = False
    ):
        """Notifies admin when a purchase is completed."""
        admin_emails = AdminNotificationService._get_admin_emails()
        if not admin_emails:
            logging.warning("No OWNER_EMAILS configured for purchase notification.")
            return

        purchase_type = "Subscription" if is_recurring else "One-time Purchase"
        subject = f"New {purchase_type}: {plan_tier.upper()} - {user_email}"

        html_content = f"""
        <h2>Payment Received</h2>
        <p>A new {purchase_type.lower()} has been completed on <b>{settings.SITE_BASE_URL}</b>.</p>
        <ul>
            <li><b>User:</b> {user_email}</li>
            <li><b>Tier:</b> {plan_tier.upper()}</li>
            <li><b>Amount:</b> ${amount:.2f}</li>
            <li><b>Type:</b> {purchase_type}</li>
        </ul>
        """

        for admin_email in admin_emails:
            send_email(to_email=admin_email, subject=subject, html_content=html_content)

    @staticmethod
    def notify_payment_failed(user_email: str, plan_tier: str, error_message: str = ""):
        """Notifies admin when a payment fails."""
        admin_emails = AdminNotificationService._get_admin_emails()
        if not admin_emails:
            return

        subject = f"PAYMENT FAILED: {user_email}"

        html_content = f"""
        <h2 style="color: red;">Payment Failure Notification</h2>
        <p>A payment attempt failed for user <b>{user_email}</b>.</p>
        <ul>
            <li><b>Tier:</b> {plan_tier.upper()}</li>
            <li><b>Error:</b> {error_message or 'Unknown error'}</li>
        </ul>
        <p>The user's subscription status has been updated to 'past_due'.</p>
        """

        for admin_email in admin_emails:
            send_email(to_email=admin_email, subject=subject, html_content=html_content)

    @staticmethod
    def notify_lead_captured(
        email: str,
        segment: str = "",
        platform: str = "",
        volume: str = "",
        pain: str = "",
        url: str = "",
        ua: str = "",
    ):
        """
        Notifies admin when a marketing lead is captured.

        This is intentionally minimal and operational. No medical, legal, or financial advice is involved.
        """
        admin_emails = AdminNotificationService._get_admin_emails()
        if not admin_emails:
            logging.warning("No OWNER_EMAILS configured for lead capture notification.")
            return

        subject = f"New Lead Captured: {email}"
        html_content = f"""
        <h2>New Lead Captured</h2>
        <ul>
            <li><b>Email:</b> {email}</li>
            <li><b>Segment:</b> {segment or 'N/A'}</li>
            <li><b>Platform:</b> {platform or 'N/A'}</li>
            <li><b>Volume:</b> {volume or 'N/A'}</li>
            <li><b>Bottleneck:</b> {pain or 'N/A'}</li>
            <li><b>URL:</b> {url or 'N/A'}</li>
            <li><b>User-Agent:</b> {ua or 'N/A'}</li>
        </ul>
        """

        for admin_email in admin_emails:
            send_email(to_email=admin_email, subject=subject, html_content=html_content)
