import logging
import json
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.core import SessionLocal
from src.database.models import AsyncReportTask
from src.scripts.generate_premium_report import generate_chart_data, run_premium_report
from src.engine.pdf_generator import PDFReportGenerator
import os
import tempfile

logger = logging.getLogger(__name__)

class PremiumGenerator:
    @staticmethod
    def generate_premium_report_markdown(chart_data: dict) -> str:
        """
        Generates the premium report markdown for a given chart data.
        Executes the script logic (run_premium_report) safely.
        """
        # run_premium_report expects JSON string input
        chart_data_json = json.dumps(chart_data)
        
        # Create temp file for output
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp:
            output_path = tmp.name
            
        try:
            # We call the script logic. 
            # Note: run_premium_report is sync, so this blocks. 
            # Callers should run this in threadpool/executor.
            run_premium_report(chart_data_json, output_path, iterations=6)
            
            with open(output_path, "r", encoding="utf-8") as f:
                report_markdown = f.read()
                
            return report_markdown
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

async def generate_premium_report_task(task_id: str, request_data: dict):
    """
    Background task to generate a premium report.
    """
    logger.info("Starting premium report generation for task %s", task_id)
    
    db: Session = SessionLocal()
    task = db.query(AsyncReportTask).filter(AsyncReportTask.id == task_id).first()
    
    if not task:
        logger.error("Task %s not found in DB", task_id)
        db.close()
        return

    try:
        task.status = "processing"
        db.commit()

        # 1. Generate Chart Data
        loop = asyncio.get_event_loop()
        
        chart_data_json = await loop.run_in_executor(
            None,
            lambda: generate_chart_data(
                name=request_data.get("name"),
                date_str=request_data.get("date"),
                time_str=request_data.get("time"),
                city=request_data.get("city"),
                state=request_data.get("state"),
            )
        )
        
        if not chart_data_json:
            raise Exception("Failed to generate chart data")

        # 2. Run Premium Report Logic via Class
        chart_data = json.loads(chart_data_json)
        
        report_markdown = await loop.run_in_executor(
            None,
            lambda: PremiumGenerator.generate_premium_report_markdown(chart_data)
        )
        
        # 3. Generate Computation Trace
        computation_trace = None
        try:
            from src.engine.trace_generator import generate_trace
            computation_trace = await loop.run_in_executor(
                None,
                lambda: generate_trace(
                    date_str=request_data.get("date"),
                    time_str=request_data.get("time"),
                    city=request_data.get("city"),
                    state=request_data.get("state", ""),
                    name=request_data.get("name", "Native"),
                )
            )
        except Exception as trace_err:
            logger.warning("Trace generation failed (non-fatal): %s", trace_err)
            computation_trace = None

        # 4. Store Result
        result_payload = {
            "report_markdown": report_markdown,
            "chart_data": chart_data,
            "computation_trace": computation_trace,
        }
        
        task.result_json = result_payload
        task.status = "completed"
        db.commit()
        logger.info("Task %s completed successfully", task_id)

    except Exception as e:
        logger.error("Task %s failed: %s", task_id, e)
        task.status = "failed"
        task.result_json = {"error": str(e)}
        db.commit()
    finally:
        db.close()

