from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Header
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
import os
import logging
from src.engine.email_service import send_email, render_template
from src.engine.pdf_generator import PDFReportGenerator
from src.core.config import settings

router = APIRouter()

class EmailPDFRequest(BaseModel):
    email: EmailStr
    chart_data: Dict[str, Any]
    consent: bool

@router.post("/email-pdf")
async def email_pdf_report(
    request: EmailPDFRequest, 
    background_tasks: BackgroundTasks,
    user_agent: str = Header(None)
):
    """
    Generates a PDF for the provided chart data and emails it to the user.
    Rate-limiting should ideally be applied here.
    """
    if not request.consent:
        raise HTTPException(status_code=400, detail="Consent is required.")

    # Generate PDF in memory
    try:
        # We process PDF generation synchronously here because it's CPU bound but fast enough (<1s usually)
        # For higher scale, offload to worker.
        generator = PDFReportGenerator(request.chart_data)
        pdf_buffer = generator.generate()
        pdf_bytes = pdf_buffer.getvalue()
        
        # Prepare Email
        subject = "Your Forensic Astrology Report (Codex Caelestis)"
        
        # Simple HTML body
        html_content = f"""
        <html>
        <body style="font-family: 'Courier New', monospace; color: #333;">
            <h2 style="color: #c07a2b;">Your Codex Audit is Attached.</h2>
            <p>Greetings,</p>
            <p>Attached is the secure PDF copy of your recent astrological calculation.</p>
            <p><b>Configuration:</b><br>
               House System: Placidus<br>
               Zodiac: Tropical<br>
               Calculation Engine: v2.0 (Forensic)
            </p>
            <p>For the full investigative dossier, ensuring you have the complete picture of your Time Lords and Vitality, please consider unlocking the <a href="{settings.SITE_BASE_URL}">Full Forensic Report</a>.</p>
            <br>
            <p><i>Veritas Filia Temporis</i><br>
            (Truth is the Daughter of Time)</p>
            <p>— The Codex Caelestis Engine</p>
        </body>
        </html>
        """
        
        # Send Email in Background to avoid blocking response
        background_tasks.add_task(
            send_email,
            to_email=request.email,
            subject=subject,
            html_content=html_content,
            attachment_bytes=pdf_bytes,
            attachment_name="codex_forensic_audit.pdf"
        )
        
        return {"success": True, "detail": "PDF queued for delivery."}

    except Exception as e:
        logging.error(f"PDF Email Failed: {e}")
        raise HTTPException(status_code=500, detail="Could not generate or send PDF.")
