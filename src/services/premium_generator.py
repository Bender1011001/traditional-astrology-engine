import logging
import json
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.core import SessionLocal
from src.database.models import AsyncReportTask
from src.scripts.generate_premium_report import generate_chart_data, run_premium_report
from src.engine.pdf_generator import PDFReportGenerator

logger = logging.getLogger(__name__)

async def generate_premium_report_task(task_id: str, request_data: dict):
    """
    Background task to generate a premium report.
    """
    logger.info(f"Starting premium report generation for task {task_id}")
    
    db: Session = SessionLocal()
    task = db.query(AsyncReportTask).filter(AsyncReportTask.id == task_id).first()
    
    if not task:
        logger.error(f"Task {task_id} not found in DB")
        db.close()
        return

    try:
        task.status = "processing"
        db.commit()

        # 1. Generate Chart Data (Synchronous logic from script)
        # We run this in a thread executor to avoid blocking the async event loop
        # if it does heavy computation (which it does).
        loop = asyncio.get_event_loop()
        
        chart_data_json = await loop.run_in_executor(
            None,
            lambda: generate_chart_data(
                name=request_data.get("name"),
                date_str=request_data.get("date"),
                time_str=request_data.get("time"),
                city=request_data.get("city"),
                state=request_data.get("state"),
                house_system=request_data.get("house_system", "W")
            )
        )
        
        if not chart_data_json:
            raise Exception("Failed to generate chart data")

        # 2. Run Premium Report Logic (Multi-pass LLM)
        # This writes to a file in the script, but we want to capture the output.
        # We need to adapt run_premium_report or replicate its logic.
        # For now, let's use a temporary file approach or refactor run_premium_report to return string.
        # SINCE we are in a hurry, let's modify the script logic here to be inline or importable.
        # Actually, run_premium_report writes to a file. Let's use a temp path.
        
        # We will use the existing run_premium_report logic but capture the result.
        # The existing script writes to a file. 
        # Let's define a helper to run it and read the file back.
        
        import os
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp:
            output_path = tmp.name
            
        await loop.run_in_executor(
            None,
            lambda: run_premium_report(chart_data_json, output_path, iterations=6) # 6 iterations as per script default
        )
        
        with open(output_path, "r", encoding="utf-8") as f:
            report_markdown = f.read()
            
        os.unlink(output_path) # Cleanup
        
        # 3. Generate PDF (Optional? The user just wants the report I think? 
        # Actually the workflow says "Convert to PDF". The user likely wants a PDF download.)
        # Let's convert to PDF using PDFReportGenerator.
        
        chart_data = json.loads(chart_data_json)
        pdf_data = {
            "meta": chart_data.get("meta", {}),
            "forensic_report": chart_data.get("analysis", {}),
        }
        
        generator = PDFReportGenerator(pdf_data)
        pdf_buffer = generator.generate(custom_content=report_markdown)
        
        # We need to store this PDF somewhere. 
        # For now, let's store the MARKDOWN in the database (it's text) and generate PDF on demand?
        # OR store the PDF in a blob storage? 
        # The simplest constraint-compatible way: Store Markdown in JSON result, generate PDF on GET /download.
        
        result_payload = {
            "report_markdown": report_markdown,
            "chart_data": chart_data # Store the full calculated data too
        }
        
        task.result_json = result_payload
        task.status = "completed"
        db.commit()
        logger.info(f"Task {task_id} completed successfully")

    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        task.status = "failed"
        task.result_json = {"error": str(e)}
        db.commit()
    finally:
        db.close()
