from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.database.models import GuestRequest, AsyncReportTask
from src.services.premium_generator import generate_premium_report_task
from src.api.v1.schemas import ChartRequest
from src.core.config import settings

router = APIRouter()

# Constants
MAX_FREE_READINGS = 3
PREMIUM_PRICE = 2000 # Cents, so $20.00

@router.post("/guest/request")
async def request_premium_guest_reading(
    chart_request: ChartRequest, 
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request a premium forensic audit as a guest.
    Limits: 3 per IP.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # 1. Check IP Limit
    # Count existing *premium_guest* requests from this IP
    usage_count = db.query(GuestRequest).filter(
        GuestRequest.ip_address == client_ip,
        GuestRequest.request_type == "premium_guest"
    ).count()
    
    # Allow 3, so if count is 0, 1, 2 = OK. If 3, Reject.
    if usage_count >= MAX_FREE_READINGS:
         raise HTTPException(
            status_code=402,
            detail={
                "error": "payment_required",
                "message": f"Free guest limit reached ({MAX_FREE_READINGS}/IP). Premium readings are ${PREMIUM_PRICE/100:.2f} each.",
                "price_usd": PREMIUM_PRICE / 100
            }
        )

    # 2. Create Task
    task = AsyncReportTask(
        status="pending",
        request_meta=chart_request.dict()
    )
    db.add(task)
    
    # 3. Record Usage
    usage = GuestRequest(
        ip_address=client_ip,
        request_type="premium_guest"
    )
    db.add(usage)
    db.commit()
    db.refresh(task)
    
    # 4. Trigger Background Processing
    background_tasks.add_task(
        generate_premium_report_task, 
        task.id, 
        chart_request.dict()
    )
    
    return {
        "task_id": task.id,
        "message": "Premium report generation started. Please poll /guest/status/{task_id}",
        "free_readings_remaining": MAX_FREE_READINGS - (usage_count + 1)
    }

@router.get("/guest/status/{task_id}")
async def check_premium_guest_status(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Poll status of a premium report task.
    """
    task = db.query(AsyncReportTask).filter(AsyncReportTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return {
        "task_id": task.id,
        "status": task.status,
        "result": task.result_json if task.status in ("completed", "failed") else None
    }
