import logging
import asyncio
from datetime import datetime
from src.services.engine_bridge import generate_full_nativity_async
from src.engine.pdf_generator import PDFReportGenerator
from src.engine.email_service import send_email, render_template

logger = logging.getLogger(__name__)

class FulfillmentService:
    """
    Handles the post-purchase delivery of the product.
    1. Generates the Astrology Report (Computational expensive)
    2. Generates the PDF (Memory intensive)
    3. Emails the PDF to the user (IO bound)
    """

    @staticmethod
    async def fulfill_order(user_email: str, user_name: str, chart_request: dict, tier: str = "onetime"):
        """
        Execute fulfillment flow. Should be run as a BackgroundTask.
        """
        logger.info(f"Starting fulfillment for {user_email} (Tier: {tier})")
        
        try:
            # 1. Calculate Chart Data
            # chart_request should contain: date, time, city, state, [name]
            logger.info("Generating nativity data...")
            chart_data = await generate_full_nativity_async(
                date_str=chart_request.get("date"),
                time_str=chart_request.get("time", "12:00"),
                city=chart_request.get("city"),
                state=chart_request.get("state", ""),
                name=chart_request.get("name", user_name),
                # defaults
                house_system="P",
                zodiac_system="T", 
                ayanamsa="0"
            )
            
            if "error" in chart_data:
                logger.error(f"Fulfillment Calculation Failed: {chart_data['error']}")
                # TODO: Send "Sorry" email?
                return

            # 2. Generate PDF
            logger.info("Generating PDF...")
            # Detect tier for PDF branding
            pdf_tier = "CALIBRATION" if tier.lower() == "calibration" else "FULL"
            
            # PDF Generator expects the full data object
            generator = PDFReportGenerator(chart_data, tier=pdf_tier)
            pdf_buffer = generator.generate()
            pdf_bytes = pdf_buffer.getvalue()
            
            # 3. Send Email
            logger.info(f"Sending email to {user_email}...")
            
            # Determine email template based on tier
            subject = "Your Astrology Report"
            if pdf_tier == "CALIBRATION":
                subject = "Your Calibration Audit (Codex Caelestis)"
                template = "order_calibration.html" # We need to ensure this exists or use logic
            else:
                subject = "Your Forensic Dossier (Codex Caelestis)"
                template = "order_full.html"

            # Construct simple HTML if template doesn't exist yet (Safety first)
            # But ideally we use render_template
            
            html_content = f"""
            <h1>Your Report is Ready</h1>
            <p>Dear {user_name},</p>
            <p>Thank you for your patience. Your forensic astrology audit has been successfully generated and is attached to this email.</p>
            <p><b>Report Details:</b><br>
            Name: {chart_request.get('name', user_name)}<br>
            Date: {chart_request.get('date')}<br>
            Location: {chart_request.get('city')}
            </p>
            <p>Please save this PDF to your device.</p>
            <p>Sincerely,<br>The Codex Caelestis Engine</p>
            """
            
            # Try to use a better template if we can, but fallback to string above is safe
            # Let's just use the string for now to guarantee it works without file dependencies
            # We can upgrade to templates later.
            
            success = send_email(
                to_email=user_email,
                subject=subject,
                html_content=html_content,
                attachment_bytes=pdf_bytes,
                attachment_name=f"Codex_Report_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
            )
            
            if success:
                logger.info(f"Fulfillment successful for {user_email}")
            else:
                logger.error(f"Email failed to send for {user_email}")

        except Exception as e:
            logger.exception(f"CRITICAL FULFILLMENT ERROR for {user_email}: {e}")

