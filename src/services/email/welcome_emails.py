import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_b2b_welcome_email(to_email, tier, api_key):
    """Sends a welcome email to B2B users with their API Key and Quick Start guide."""
    subject = f"Welcome to Traditional Astrology | {tier.capitalize()} Tier Activated"
    
    body = f"""
    Welcome to the Practice,
    
    Your {tier} subscription is now active. You have been granted access to the high-throughput generation engine.
    
    YOUR API KEY: {api_key}
    
    Quick Start:
    1. View your dashboard: https://traditional-astrology.com/profile.html
    2. API Documentation: https://traditional-astrology.com/documentation.html
    3. Join the Practitioner Community (Discord): [Link TBD]
    
    Your tier includes {get_quota(tier)} API calls per day. Usage progress can be tracked in your dashboard.
    
    For technical support, simply reply to this email.
    
    Traditional Astrology
    """
    
    _send_email(to_email, subject, body)

def get_quota(tier):
    quotas = {"practitioner": 100, "studio": "Unlimited"}
    return quotas.get(tier, "N/A")

def _send_email(to_email, subject, body, attachment_path=None):
    # This is a stub for the actual SMTP logic - User will need to provide creds
    print(f"DEBUG: Sending email to {to_email}")
    print(f"Subject: {subject}")
    # Logic for SMTP would go here
    pass
