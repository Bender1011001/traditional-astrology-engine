import hashlib
import json
import logging
import re
import time
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.v1.auth import get_current_user
from src.api.v1.client_ip import get_client_ip
from src.api.v1.schemas import ChartRequest  # type: ignore
from src.database.core import get_db
from src.database.models import AsyncReportTask, ChartEvent, Lead, User
from src.services.admin_notifier import notify_chart_created
from src.services.premium_generator import (
    generate_premium_report_task,
    llm_iterations_for_tier,
)

logger = logging.getLogger(__name__)

router = APIRouter()

FREE_CHART_TIER = "premium_audit"
FREE_CHART_ITERATIONS = llm_iterations_for_tier(FREE_CHART_TIER)
FREE_CHART_EVENT_TYPE = "free_complete_analysis"


def _safe_chart_payload(chart_request: ChartRequest) -> dict[str, Any]:
    payload = chart_request.model_dump()
    payload.pop("access_token", None)
    return payload


def _reading_hash(
    payload: dict[str, Any], chart_summary: dict[str, Any], reading_html: str
) -> str:
    hash_payload = {
        "request": payload,
        "summary": chart_summary,
        "reading_html": reading_html,
    }
    encoded = json.dumps(hash_payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _chart_event_from_request(
    *,
    request: Request,
    payload: dict[str, Any],
    status: str,
    event_type: str = FREE_CHART_EVENT_TYPE,
    chart_summary: dict[str, Any] | None = None,
    reading_html: str | None = None,
    error_message: str | None = None,
    free_readings_remaining: int | None = None,
    generation_ms: int | None = None,
) -> ChartEvent:
    summary = chart_summary or {}
    return ChartEvent(
        id=str(uuid.uuid4()),
        event_type=event_type,
        status=status,
        client_ip=get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
        referer=request.headers.get("referer"),
        path=request.url.path,
        request_payload=payload,
        chart_summary=summary,
        reading_hash=(
            _reading_hash(payload, summary, reading_html or "")
            if reading_html is not None
            else None
        ),
        reading_html=reading_html,
        error_message=error_message,
        free_readings_remaining=free_readings_remaining,
        generation_ms=generation_ms,
    )


@router.post("/guest/request")
async def request_premium_guest_reading(
    chart_request: ChartRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Request a free natal chart reading as a guest.

    The free chart now uses the same forensic chart-data and LLM report pipeline
    as the former paid Complete Analysis tier. The caller polls
    /guest/status/{task_id} for completion.
    The public natal report is intentionally uncapped.
    """
    chart_payload = _safe_chart_payload(chart_request)

    # Create a durable chart-event row now, then let the premium generator fill
    # in the complete report markdown, summary, hash, and terminal status.
    event = _chart_event_from_request(
        request=request,
        payload=chart_payload,
        status="pending",
        free_readings_remaining=None,
    )
    task_id = str(uuid.uuid4())
    request_meta = {
        "name": chart_request.name or "Guest",
        "date": chart_request.date,
        "time": chart_request.time,
        "city": chart_request.city,
        "state": chart_request.state or "",
        "tier": FREE_CHART_TIER,
        "free_entitlement": "complete_analysis_free_for_launch",
        "report_iterations": FREE_CHART_ITERATIONS,
        "chart_event_id": event.id,
        "free_readings_remaining": None,
    }
    if chart_request.latitude is not None and chart_request.longitude is not None:
        request_meta["latitude"] = chart_request.latitude
        request_meta["longitude"] = chart_request.longitude
    if chart_request.time_unknown:
        request_meta["time_unknown"] = True

    task = AsyncReportTask(
        id=task_id,
        status="pending",
        request_meta=request_meta,
    )

    db.add(event)
    db.add(task)
    db.commit()
    db.refresh(event)
    db.refresh(task)

    background_tasks.add_task(generate_premium_report_task, task.id, dict(request_meta))
    background_tasks.add_task(notify_chart_created, chart_payload, "Free LLM Chart")

    return {
        "status": "started",
        "task_id": task.id,
        "tier": FREE_CHART_TIER,
        "report_iterations": FREE_CHART_ITERATIONS,
        "chart_event_id": event.id,
        "free_readings_remaining": None,
        "instant": False,
    }


@router.get("/guest/status/{task_id}")
async def check_premium_guest_status(task_id: str, db: Session = Depends(get_db)):
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
        "result": task.result_json if task.status in ("completed", "failed") else None,
    }


@router.post("/free-trial/request")
async def request_free_premium_trial(
    chart_request: ChartRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retired free Complete Analysis add-on.

    The free chart itself now uses the complete LLM report path. Returning
    limit_reached keeps older cached frontends from showing a stuck add-on loader.
    """
    return {
        "status": "limit_reached",
        "message": "The free chart now includes the first premium LLM response.",
    }


@router.post("/email-reading")
async def email_reading_capture(
    request: Request,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,  # type: ignore[assignment]
):
    """
    Capture a visitor's email after they've received their free premium reading.

    Stores in the Lead table (segment='reading_email') for follow-up.
    Sends a Discord notification for real-time visibility.
    """
    body = await request.json()
    email = (body.get("email") or "").strip().lower()
    chart_event_id = body.get("chart_event_id") or None
    name = (body.get("name") or "Guest").strip()[:100]

    # Basic email validation — regex, not full RFC 5322 to keep it simple.
    if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise HTTPException(status_code=422, detail="Valid email address required.")

    client_ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "")[:500]

    # Upsert: if the email already exists from this session we still want to
    # update the chart_event_id linkage, but we don't want duplicate rows.
    existing = (
        db.query(Lead)
        .filter(Lead.email == email, Lead.segment == "reading_email")
        .first()
    )

    if existing:
        # Update existing record with latest context.
        if chart_event_id:
            existing.url = chart_event_id  # re-use url column for chart event linkage
        db.commit()
    else:
        lead = Lead(
            email=email,
            segment="reading_email",
            platform="b2c_free_trial",
            pain=name if name != "Guest" else None,
            url=chart_event_id,
            ip=client_ip,
            ua=user_agent,
        )
        db.add(lead)
        db.commit()

        # Notify via Discord so we can celebrate every email capture.
        from src.services.admin_notifier import _send_discord_embed
        from datetime import datetime, timezone

        try:
            _send_discord_embed(
                {
                    "title": "Email Captured — Free Chart",
                    "color": 0xF6AD55,
                    "fields": [
                        {"name": "Email", "value": email, "inline": True},
                        {"name": "Name", "value": name, "inline": True},
                        {"name": "IP", "value": client_ip or "unknown", "inline": True},
                    ],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "footer": {"text": "Traditional Astrology - Free Chart Funnel"},
                }
            )
        except Exception as discord_err:
            logger.warning("Discord notify for email capture failed: %s", discord_err)

    return {"success": True}
