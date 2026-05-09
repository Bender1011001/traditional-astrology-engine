import asyncio
import json
import logging
import os
import re
import tempfile

from sqlalchemy.orm import Session

from src.database.core import SessionLocal
from src.database.models import AsyncReportTask
from src.engine.email_service import send_email
from src.scripts.generate_premium_report import generate_chart_data, run_premium_report

logger = logging.getLogger(__name__)

RAW_APPENDIX_MARKER = "### Raw Natal Data (Audit Appendix)"
MIN_CUSTOMER_REPORT_WORDS = 700
DEFAULT_PREMIUM_ITERATIONS = 6
TECHNICAL_APPENDIX_HEADING_RE = re.compile(r"(?mi)^\s*##\s+Technical Appendix\s*$")

TIER_REPORT_ITERATIONS = {
    "free": 0,
    "free_instant": 0,
    "free_premium": 1,
    "free_premium_trial": 1,
    "full_reading": 1,
    "single_reading": 1,
    "full": 1,
    "onetime": 1,
    "premium_audit": 3,
    "complete_analysis": 3,
    "middle": 3,
    "forensic_nativity": 6,
    "top": 6,
    "premium": 6,
}


def _collapse_blank_lines(markdown: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", markdown).strip() + "\n"


def build_customer_facing_report_markdown(report_markdown: str) -> str:
    """
    Remove internal audit appendices from the customer-facing web/PDF body.

    Older reports placed the raw appendix before "# Part 1", which made the
    paid product look like a database dump. New reports place any appendix at
    the end, but the public report body still omits it unless a separate
    technical appendix surface is intentionally built.
    """
    if not report_markdown:
        return ""

    trailing_appendix = TECHNICAL_APPENDIX_HEADING_RE.search(report_markdown)
    if trailing_appendix:
        before_appendix = report_markdown[: trailing_appendix.start()].rstrip()
        before_appendix = re.sub(r"(?m)\n\s*---\s*$", "", before_appendix).rstrip()
        report_markdown = before_appendix

    marker_index = report_markdown.find(RAW_APPENDIX_MARKER)
    if marker_index == -1:
        return _collapse_blank_lines(report_markdown)

    before_marker = report_markdown[:marker_index].rstrip()
    after_marker = report_markdown[marker_index:]

    next_part = re.search(r"(?m)^# Part\s+\d+\s*$", after_marker)
    if next_part:
        after_appendix = after_marker[next_part.start() :].lstrip()
        return _collapse_blank_lines(f"{before_marker}\n\n{after_appendix}")

    return _collapse_blank_lines(before_marker)


def has_customer_interpretation(report_markdown: str) -> bool:
    customer_body = build_customer_facing_report_markdown(report_markdown)
    if re.search(r"(?m)^# Part\s+\d+\s*$", customer_body):
        return True
    words = re.findall(r"\b[\w'-]+\b", customer_body)
    return len(words) >= MIN_CUSTOMER_REPORT_WORDS


def ensure_customer_report_quality(report_markdown: str) -> str:
    customer_body = build_customer_facing_report_markdown(report_markdown)
    if RAW_APPENDIX_MARKER in customer_body:
        raise RuntimeError("Internal audit appendix leaked into customer report body.")
    if TECHNICAL_APPENDIX_HEADING_RE.search(customer_body):
        raise RuntimeError(
            "Internal technical appendix leaked into customer report body."
        )
    if not has_customer_interpretation(customer_body):
        raise RuntimeError(
            "Premium report did not produce enough interpretive customer content."
        )
    return customer_body


def llm_iterations_for_tier(tier: str | None) -> int:
    if not tier:
        return DEFAULT_PREMIUM_ITERATIONS
    return TIER_REPORT_ITERATIONS.get(
        str(tier).strip().lower(), DEFAULT_PREMIUM_ITERATIONS
    )


def _send_report_email(
    customer_email: str, customer_name: str, pdf_bytes: bytes, chart_data: dict
) -> None:
    """Send the completed PDF report to the customer."""
    birth_date = chart_data.get("birth_date_utc", "") or chart_data.get("date", "")
    city = chart_data.get("city", "")

    html = f"""
    <div style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto; color: #222;">
      <div style="background: #09090f; padding: 2rem; text-align: center; border-bottom: 2px solid #c9a84c;">
        <p style="color: #c9a84c; font-size: 1.1rem; margin: 0;">✦ Traditional Astrology</p>
      </div>
      <div style="padding: 2rem;">
        <h1 style="font-size: 1.5rem; margin-bottom: 0.5rem;">Your Forensic Nativity Report is ready.</h1>
        <p style="color: #555; margin-bottom: 1.5rem;">
          Born: {birth_date} &nbsp;·&nbsp; {city}
        </p>
        <p>The PDF is attached to this email. Save it to your device — this is your permanent copy.</p>
        <p style="margin-top: 1.5rem; color: #555; font-size: 0.9rem;">
          The report runs to 50+ pages and covers every classical technique: Almuten Figuris,
          sect, essential dignities at all five levels, Arabic Lots, fixed star contacts,
          firdaria, humoral temperament, and your current annual profection.
        </p>
        <p style="margin-top: 1.5rem; color: #555; font-size: 0.9rem;">
          Questions or calculation corrections:
          <a href="mailto:bugs@traditional-astrology.com" style="color: #c9a84c;">bugs@traditional-astrology.com</a>
        </p>
      </div>
    </div>
    """

    from datetime import datetime, timezone

    filename = f"Traditional_Astrology_Forensic_Nativity_{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf"

    success = send_email(
        to_email=customer_email,
        subject="Your Forensic Nativity Report — Traditional Astrology",
        html_content=html,
        attachment_bytes=pdf_bytes,
        attachment_name=filename,
    )
    if success:
        logger.info("Report email sent to %s", customer_email)
    else:
        logger.error("Failed to send report email to %s", customer_email)


class PremiumGenerator:
    @staticmethod
    def generate_premium_report_markdown(
        chart_data: dict, tier: str | None = None, iterations: int | None = None
    ) -> str:
        """
        Generates the premium report markdown for a given chart data.
        Executes the script logic (run_premium_report) safely.
        """
        # run_premium_report expects JSON string input
        chart_data_json = json.dumps(chart_data)
        iteration_count = (
            max(1, int(iterations))
            if iterations is not None
            else llm_iterations_for_tier(tier)
        )
        if iteration_count < 1:
            raise ValueError("Premium report generation requires at least one LLM pass")

        # Create temp file for output
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp:
            output_path = tmp.name

        try:
            # We call the script logic.
            # Note: run_premium_report is sync, so this blocks.
            # Callers should run this in threadpool/executor.
            run_premium_report(chart_data_json, output_path, iterations=iteration_count)

            with open(output_path, "r", encoding="utf-8") as f:
                report_markdown = f.read()

            return ensure_customer_report_quality(report_markdown)
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
        task.status = "processing"  # type: ignore
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
            ),
        )

        if not chart_data_json:
            raise Exception("Failed to generate chart data")

        # 2. Run Premium Report Logic via Class
        chart_data = json.loads(chart_data_json)
        tier = str(request_data.get("tier") or "").strip().lower()
        requested_iterations = request_data.get("report_iterations")
        iteration_count = (
            max(1, int(requested_iterations))
            if requested_iterations is not None
            else llm_iterations_for_tier(tier)
        )

        report_markdown = await loop.run_in_executor(
            None,
            lambda: PremiumGenerator.generate_premium_report_markdown(
                chart_data, tier=tier, iterations=iteration_count
            ),
        )

        # 3. Generate Computation Trace
        computation_trace = None
        try:
            from src.engine.trace_generator import generate_trace

            computation_trace = await loop.run_in_executor(
                None,
                lambda: generate_trace(
                    date_str=request_data.get("date"),  # type: ignore
                    time_str=request_data.get("time"),  # type: ignore
                    city=request_data.get("city"),  # type: ignore
                    state=request_data.get("state", ""),
                    name=request_data.get("name", "Native"),
                ),
            )
        except Exception as trace_err:
            logger.warning("Trace generation failed (non-fatal): %s", trace_err)
            computation_trace = None

        # 4. Store Result
        result_payload = {
            "report_markdown": report_markdown,
            "chart_data": chart_data,
            "computation_trace": computation_trace,
            "tier": tier,
            "report_iterations": iteration_count,
        }

        task.result_json = result_payload  # type: ignore
        task.status = "completed"  # type: ignore
        db.commit()
        logger.info("Task %s completed successfully", task_id)

        # Generate PDF and email it to the customer if we have their email
        customer_email = request_data.get("customer_email")
        if customer_email:
            try:
                from src.engine.pdf_generator import PDFReportGenerator

                generator = PDFReportGenerator(chart_data, tier="FULL")
                pdf_buffer = await loop.run_in_executor(
                    None, lambda: generator.generate(custom_content=report_markdown)
                )
                pdf_bytes = pdf_buffer.getvalue()
                customer_name = request_data.get("name", "Guest")
                await loop.run_in_executor(
                    None,
                    lambda: _send_report_email(
                        customer_email, customer_name, pdf_bytes, chart_data
                    ),
                )
            except Exception as email_err:
                logger.error(
                    "PDF/email delivery failed for task %s: %s",
                    task_id,
                    repr(email_err),
                    exc_info=True,
                )

    except Exception as e:
        logger.error("Task %s failed: %s", task_id, repr(e), exc_info=True)
        task.status = "failed"  # type: ignore
        task.result_json = {"error": str(e)}  # type: ignore
        db.commit()
    finally:
        db.close()
