import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging

def send_email(to_email: str, subject: str, html_content: str, attachment_bytes: bytes = None, attachment_name: str = "document.pdf") -> bool:
    """
    Sends an email using SMTP (if configured) or SendGrid (if configured).
    If neither is configured, logs the email content to console (dev mode).
    """
    
    # 1. Append Compliance Footer if not present
    if "<footer" not in html_content and "unsubscribe" not in html_content.lower():
        footer = """
        <div style="margin-top: 30px; font-size: 0.75em; color: #666; border-top: 1px solid #eee; padding-top: 10px; text-align: center;">
            <p>You received this email because you requested a reading on <a href="https://traditional-astrology.com" style="color: #666;">traditional-astrology.com</a>.</p>
            <p>
                <a href="https://traditional-astrology.com/privacy.html" style="color: #666;">Privacy Policy</a> | 
                <a href="https://traditional-astrology.com/terms.html" style="color: #666;">Terms of Service</a>
            </p>
            <p>To unsubscribe, please rely to this email with "UNSUBSCRIBE".</p>
        </div>
        """
        # Insert before </body> if present, otherwise append
        if "</body>" in html_content:
            html_content = html_content.replace("</body>", footer + "</body>")
        else:
            html_content += footer

    
    # 1. Try SendGrid
    sendgrid_key = os.getenv("SENDGRID_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL", "noreply@codexcaelestis.com")
    
    if sendgrid_key:
        # Simple SendGrid implementation (using python-http-client or requests if library not found, 
        # but here we'll stick to standard library if possible, or just mock it if we don't want to add deps)
        # Actually, using requests is easier for SendGrid Web API.
        try:
            import requests
            import base64
            
            headers = {
                "Authorization": f"Bearer {sendgrid_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": sender_email, "name": "Codex Caelestis"},
                "subject": subject,
                "content": [{"type": "text/html", "value": html_content}]
            }
            
            if attachment_bytes:
                encoded = base64.b64encode(attachment_bytes).decode()
                data["attachments"] = [{
                    "content": encoded,
                    "filename": attachment_name,
                    "type": "application/pdf",
                    "disposition": "attachment"
                }]
                
            response = requests.post("https://api.sendgrid.com/v3/mail/send", json=data, headers=headers)
            if response.status_code in (200, 201, 202):
                return True
            else:
                logging.error(f"SendGrid Error: {response.text}")
                # Fallthrough to other methods or fail
        except ImportError:
            logging.warning("Requests library not found, skipping SendGrid.")
            pass
        except Exception as e:
            logging.error(f"SendGrid Exception: {e}")

    # 2. Try SMTP
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    
    if smtp_host and smtp_user:
        try:
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = to_email
            msg["Subject"] = subject
            
            msg.attach(MIMEText(html_content, "html"))
            
            if attachment_bytes:
                part = MIMEApplication(attachment_bytes, Name=attachment_name)
                part["Content-Disposition"] = f'attachment; filename="{attachment_name}"'
                msg.attach(part)
                
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            logging.error(f"SMTP Error: {e}")
            return False

    # 3. Dev Mode / No Provider Configured
    logging.warning(f"EMAIL NOT SENT (no provider configured): To={to_email}, Subject={subject}")
    logging.warning("Configure SENDGRID_API_KEY or SMTP_HOST/SMTP_USER to enable email delivery.")
    
    # In development, log the content for debugging
    if os.getenv("DEBUG_EMAIL", "").lower() in ("1", "true"):
        print("="*60)
        print(f"MOCK EMAIL TO: {to_email}")
        print(f"SUBJECT: {subject}")
        print("-" * 20)
        print(html_content[:500] + "..." if len(html_content) > 500 else html_content)
        if attachment_bytes:
            print(f"[Attachment: {attachment_name} ({len(attachment_bytes)} bytes)]")
        print("="*60)
    
    # Return False to indicate email was NOT sent in production
    return False
