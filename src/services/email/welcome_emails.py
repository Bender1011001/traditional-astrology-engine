import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_b2c_welcome_email(to_email, pdf_path):
    """Sends a welcome email to B2C users with their Premium Dossier attached."""
    subject = "Your Premium Forensic Dossier is Ready | Codex Caelestis"
    
    body = f"""
    Greetings,
    
    Your inspections are complete. Your 100+ page Premium Forensic Structural Audit is attached to this email as a PDF.
    
    This document contains your complete natal assessment, timing of Kairos (Zodiacal Releasing), and traditional remediation protocols.
    
    We recommend viewing this on a desktop or tablet for the best experience.
    
    If you have any questions about the method or your results, visit our guide at https://traditional-astrology.com/api-guide
    
    In service to the craft,
    The Codex Caelestis Engine
    """
    
    _send_email(to_email, subject, body, pdf_path)

def send_b2b_welcome_email(to_email, tier, api_key):
    """Sends a welcome email to B2B users with their API Key and Quick Start guide."""
    subject = f"Welcome to Codex Caelestis | {tier.capitalize()} Tier Activated"
    
    body = f"""
    Welcome to the Practice,
    
    Your {tier} subscription is now active. You have been granted access to the high-throughput generation engine.
    
    YOUR API KEY: {api_key}
    
    Quick Start:
    1. View your dashboard: https://traditional-astrology.com/dashboard
    2. API Documentation: https://traditional-astrology.com/api-guide
    3. Join the Practitioner Community (Discord): [Link TBD]
    
    Your tier includes {get_quota(tier)} reports per month. Usage progress can be tracked in your dashboard.
    
    For technical support, simply reply to this email.
    
    The Codex Caelestis Practice
    """
    
    _send_email(to_email, subject, body)

def get_quota(tier):
    quotas = {"apprentice": 5, "practitioner": 25, "master": 100, "agency": "Unlimited"}
    return quotas.get(tier, "N/A")

def _send_email(to_email, subject, body, attachment_path=None):
    # This is a stub for the actual SMTP logic - User will need to provide creds
    print(f"DEBUG: Sending email to {to_email}")
    print(f"Subject: {subject}")
    # Logic for SMTP would go here
    pass
