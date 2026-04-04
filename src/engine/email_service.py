import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import logging
import sys
import threading

def _send_email_blocking(to_email: str, subject: str, html_content: str, attachment_bytes: bytes = None, attachment_name: str = "document.pdf") -> bool:
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
        if "</body>" in html_content:
            html_content = html_content.replace("</body>", footer + "</body>")
        else:
            html_content += footer
    
    # 2. Try SendGrid
    sendgrid_key = os.getenv("SENDGRID_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL", "noreply@codexcaelestis.com")
    
    if sendgrid_key:
        try:
            import requests
            import base64
            
            headers = {
                "Authorization": f"Bearer {sendgrid_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": sender_email, "name": "Traditional Astrology"},
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
                
            response = requests.post("https://api.sendgrid.com/v3/mail/send", json=data, headers=headers, timeout=10)
            if response.status_code in (200, 201, 202):
                return True
            else:
                logging.error("SendGrid Error: %s", response.text)
        except ImportError:
            logging.warning("Requests library not found, skipping SendGrid.")
        except Exception as e:
            logging.error("SendGrid Exception: %s", repr(e), exc_info=True)

    # 3. Try SMTP
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
            logging.error("SMTP Error: %s", repr(e), exc_info=True)
            return False

    # 4. Dev Mode / No Provider Configured
    masked_email = to_email
    if "@" in to_email:
        name, domain = to_email.split("@")
        masked_email = f"{name[:2]}***@***{domain[-4:]}" if len(name) > 2 else f"***@***{domain[-4:]}"

    logging.warning("EMAIL NOT SENT (no provider configured): To=%s, Subject=%s", masked_email, subject)
    
    if os.getenv("DEBUG_EMAIL", "").lower() in ("1", "true"):
        print("="*60)
        print(f"MOCK EMAIL TO: {to_email}")
        print(f"SUBJECT: {subject}")
        print("-" * 20)
        print(html_content[:500] + "..." if len(html_content) > 500 else html_content)
        if attachment_bytes:
            print(f"[Attachment: {attachment_name} ({len(attachment_bytes)} bytes)]")
        print("="*60)
    
    return False

def send_email(to_email: str, subject: str, html_content: str, attachment_bytes: bytes = None, attachment_name: str = "document.pdf") -> bool:
    """
    Non-blocking wrapper that dispatches the email payload to a background thread.
    Returns True indicating the dispatch was successfully enqueued.
    """
    if "pytest" in sys.modules:
        return _send_email_blocking(to_email, subject, html_content, attachment_bytes, attachment_name)
        
    thread = threading.Thread(
        target=_send_email_blocking,
        args=(to_email, subject, html_content, attachment_bytes, attachment_name),
        daemon=True
    )
    thread.start()
    return True

def render_template(template_name: str, context: dict) -> str:
    """
    Loads an HTML template from src/templates/email/ and replaces placeholders.
    Args:
        template_name: Filename (e.g., 'welcome.html')
        context: Dictionary of values to replace {{ key }}
    """
    # robust path handling
    try:
        # Assuming src/engine/email_service.py structure
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        template_path = os.path.join(base_dir, "src", "templates", "email", template_name)
        
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        for key, value in context.items():
            # Replace {{ key }}
            content = content.replace(f"{{{{ {key} }}}}", str(value))
            # Also try {{key}} just in case
            content = content.replace(f"{{{{{key}}}}}", str(value))
            
        return content
    except Exception as e:
        logging.error("Error rendering template %s: %s", template_name, e)
        # Return a basic fallback if template fails
        return f"Error loading template. Context: {context}"
