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
    tier: str = "CALIBRATION" # Default to Calibration for security/skepticism

@router.post("/email-pdf")
async def email_pdf_report(
    request: EmailPDFRequest, 
    background_tasks: BackgroundTasks,
    user_agent: str = Header(None)
):
    """
    Generates a PDF for the provided chart data and emails it to the user.
    If tier is FULL, bundles with JSON and MD in a ZIP.
    """
    if not request.consent:
        raise HTTPException(status_code=400, detail="Consent is required.")

    try:
        tier = request.tier.upper()
        # Security: Calibration tier strictly limited to PDF
        generator = PDFReportGenerator(request.chart_data, tier=tier)
        pdf_buffer = generator.generate()
        pdf_bytes = pdf_buffer.getvalue()
        
        # Immediate cleanup of generator buffer
        generator.buffer.close()
        
        subject = "Your Traditional Astrology Reading"
        attachment_bytes = pdf_bytes
        attachment_name = "calibration_audit.pdf" if tier == "CALIBRATION" else "native_audit.pdf"
        
        # Packaging Logic for FULL tier (Digital Soul Packet)
        if tier == "FULL":
            import zipfile
            import json
            from io import BytesIO
            
            zip_buffer = BytesIO()
            name = request.chart_data.get("meta", {}).get("subject_name", "Native")
            attachment_name = f"Reading_Packet_{name}.zip"
            
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                # 1. PDF
                zf.writestr("native_audit.pdf", pdf_bytes)
                
                # 2. JSON (Machine Readable Source Code for AI Agents)
                json_data = json.dumps(request.chart_data, indent=2)
                zf.writestr("native.json", json_data)
                
                # 3. Markdown (Text Source)
                md_content = request.chart_data.get("human_translation", {}).get("report_markdown", "# Astrology Reading")
                zf.writestr("native.md", md_content)
                
                # 4. README (License & Integration)
                readme = (
                    "Traditional Astrology: DIGITAL READING PACKET\n"
                    "====================================\n\n"
                    "This packet contains your Human Readable Report (PDF) and Machine Readable Source Code (JSON).\n"
                    "LICENSED USE: You may upload the JSON file to personal AI agents (ChatGPT, Claude) to query your chart data.\n"
                    "The JSON includes sect status, planetary dignities, and holistic synchronization data."
                )
                zf.writestr("README.txt", readme)
            
            attachment_bytes = zip_buffer.getvalue()
            zip_buffer.close()
            subject = "Your Complete Astrology Reading Packet (Agent Ready)"
        
        # ZERO LEAKAGE: If tier is CALIBRATION, ensure we HAVEN'T touched zip logic or JSON/MD delivery.
        # The variables 'json_data' and 'md_content' are scoped within the 'if tier == "FULL"' block.

        # Simple HTML body
        upgrade_link = f'<p>For the full investigative report, inclusive of AI-ready JSON data and future forecasts, please consider unlocking the <a href="{settings.SITE_BASE_URL}">Full Reading</a>.</p>' if tier == "CALIBRATION" else ""
        
        html_content = f"""
        <html>
        <body style="font-family: 'Courier New', monospace; color: #333;">
            <h2 style="color: #c07a2b;">Your Codex Audit is Attached.</h2>
            <p>Greetings,</p>
            <p>Attached is your secure {'PDF' if tier == 'CALIBRATION' else 'Reading Packet'} for your recent astrological calculation.</p>
            <p><b>Configuration:</b><br>
               Tier: {tier}<br>
               House System: Placidus<br>
               Zodiac: Tropical<br>
               Engine: v2.5 (Two-Tier Model)
            </p>
            {upgrade_link}
            <br>
            <p><i>Veritas Filia Temporis</i><br>
            (Truth is the Daughter of Time)</p>
            <p>— Traditional Astrology</p>
        </body>
        </html>
        """
        
        background_tasks.add_task(
            send_email,
            to_email=request.email,
            subject=subject,
            html_content=html_content,
            attachment_bytes=attachment_bytes,
            attachment_name=attachment_name
        )
        
        return {"success": True, "detail": "Packet queued for delivery."}

    except Exception as e:
        logging.error(f"Generation/Email Failed: {e}")
        raise HTTPException(status_code=500, detail="Could not generate or send your audit.")
