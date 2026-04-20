from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.database.models import GuestRequest, AsyncReportTask
from src.services.free_reading_generator import generate_free_reading
from src.services.admin_notifier import notify_chart_created
from src.api.v1.schemas import ChartRequest
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Constants
MAX_FREE_READINGS = 3
PREMIUM_PRICE = 2000  # Cents, so $20.00

@router.post("/guest/request")
async def request_premium_guest_reading(
    chart_request: ChartRequest, 
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request a free natal chart reading as a guest.
    
    This endpoint now returns an INSTANT template-based reading (no LLM, no polling).
    The reading includes Sun/Moon/Rising interpretations, sect analysis,
    dignity scorecard, and current-year profection.
    
    Premium (LLM-generated) readings are reserved for paid tiers ($7/$29).
    
    Limits: 3 per IP.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # 1. Check IP Limit
    usage_count = db.query(GuestRequest).filter(
        GuestRequest.ip_address == client_ip,
        GuestRequest.request_type == "premium_guest"
    ).count()
    
    # Allow 3, so if count is 0, 1, 2 = OK. If 3, Reject.
    # Bypass for localhost to enable dev/testing.
    if usage_count >= MAX_FREE_READINGS and client_ip != "127.0.0.1":
         raise HTTPException(
            status_code=402,
            detail={
                "error": "payment_required",
                "message": f"Free guest limit reached ({MAX_FREE_READINGS}/IP). Premium readings are ${PREMIUM_PRICE/100:.2f} each.",
                "price_usd": PREMIUM_PRICE / 100
            }
        )

    # 2. Record Usage
    usage = GuestRequest(
        ip_address=client_ip,
        request_type="premium_guest"
    )
    db.add(usage)
    db.commit()

    free_remaining = MAX_FREE_READINGS - (usage_count + 1)

    # 3. ALL free readings get the Instant Free Reading (template-based, no LLM).
    #    Premium LLM reports are reserved for paid tiers ($7/$29).
    #    Previous approach routed first-time IPs to a slow LLM background task
    #    that took 30-60+ seconds (or hung indefinitely), killing conversions.
    try:
        result = generate_free_reading(
            name=chart_request.name or "Guest",
            date_str=chart_request.date,
            time_str=chart_request.time,
            city=chart_request.city,
            state=chart_request.state or "",
        )
    except Exception as e:
        logger.error("Free reading generation failed: %s", repr(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Chart calculation failed. Please try again.")

    if result["status"] == "failed":
        raise HTTPException(status_code=500, detail=result.get("error", "Chart calculation failed."))

    background_tasks.add_task(
        notify_chart_created, 
        chart_request.model_dump(), 
        "Free Instant"
    )

    # 5. Return instant result (no polling needed!)
    return {
        "status": "completed",
        "reading_html": result["reading_html"],
        "chart_summary": result.get("chart_data_summary", {}),
        "free_readings_remaining": free_remaining,
        # Backward compat: frontend checks for task_id presence
        "instant": True,
    }

@router.get("/guest/status/{task_id}")
async def check_premium_guest_status(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Poll status of a premium report task.
    Used for paid (LLM-generated) readings that still use background processing.
    """
    task = db.query(AsyncReportTask).filter(AsyncReportTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return {
        "task_id": task.id,
        "status": task.status,
        "result": task.result_json if task.status in ("completed", "failed") else None
    }
