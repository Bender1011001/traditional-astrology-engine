from src.engine.email_service import send_email


def send_b2b_welcome_email(to_email: str, tier: str, api_key: str):
    subject = f"Welcome to Traditional Astrology | {tier.capitalize()} Tier Activated"

    quota = {"practitioner": "100", "studio": "Unlimited"}.get(tier, "N/A")

    body = f"""
    <html><body style="font-family: sans-serif; color: #333;">
    <h2>Welcome to the Practice</h2>
    <p>Your <strong>{tier}</strong> subscription is now active.</p>

    <p><strong>Your API Key:</strong><br>
    <code style="background:#f4f4f4;padding:4px 8px;border-radius:3px;">{api_key}</code></p>

    <p><strong>Quick Start:</strong></p>
    <ol>
        <li><a href="https://traditional-astrology.com/dashboard.html">Go to your dashboard</a></li>
        <li>Your tier includes <strong>{quota}</strong> API calls per day</li>
        <li>For support, reply to this email</li>
    </ol>

    <p>— Traditional Astrology</p>
    </body></html>
    """

    send_email(to_email=to_email, subject=subject, html_content=body)
