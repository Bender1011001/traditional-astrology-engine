import hashlib
import json
import logging
import re
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.v1.auth import get_current_user
from src.api.v1.client_ip import get_client_ip, is_rate_limitable_client_ip
from src.api.v1.schemas import ChartRequest  # type: ignore
from src.core.config import settings
from src.database.core import get_db
from src.database.models import AsyncReportTask, ChartEvent, GuestRequest, Lead, User
from src.services.admin_notifier import notify_chart_created
from src.services.free_reading_generator import generate_free_reading
from src.services.premium_generator import generate_premium_report_task

logger = logging.getLogger(__name__)

router = APIRouter()

# Constants
MAX_FREE_READINGS = max(0, int(getattr(settings, "FREE_SINGLE_READINGS_PER_IP", 3)))
FREE_READING_WINDOW_SECONDS = max(
    60, int(getattr(settings, "FREE_SINGLE_READINGS_WINDOW_SECONDS", 86400))
)
FULL_READING_PRICE_CENTS = 2500


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
    chart_summary: dict[str, Any] | None = None,
    reading_html: str | None = None,
    error_message: str | None = None,
    free_readings_remaining: int | None = None,
    generation_ms: int | None = None,
) -> ChartEvent:
    summary = chart_summary or {}
    return ChartEvent(
        event_type="free_instant",
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

    This endpoint now returns an INSTANT template-based reading (no LLM, no polling).
    The reading includes Sun/Moon/Rising interpretations, sect analysis,
    dignity scorecard, and current-year profection.

    Premium (LLM-generated) readings are reserved for paid tiers ($25/$69).

    Limits: 3 per visitor per rolling window.
    """
    started = time.perf_counter()
    chart_payload = _safe_chart_payload(chart_request)
    client_ip = get_client_ip(request)
    enforce_free_limit = is_rate_limitable_client_ip(client_ip)

    # 1. Check IP Limit
    window_start = datetime.now(timezone.utc) - timedelta(
        seconds=FREE_READING_WINDOW_SECONDS
    )
    usage_count = (
        db.query(GuestRequest)
        .filter(
            GuestRequest.ip_address == client_ip,
            GuestRequest.request_type == "premium_guest",
            GuestRequest.created_at >= window_start,
        )
        .count()
        if enforce_free_limit
        else 0
    )

    # Allow 3, so if count is 0, 1, 2 = OK. If 3, Reject.
    # Bypass non-rate-limitable fallback addresses to avoid locking out all users
    # if a proxy strips visitor headers.
    if enforce_free_limit and usage_count >= MAX_FREE_READINGS:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "payment_required",
                "message": f"Free guest limit reached ({MAX_FREE_READINGS}/visitor). Full readings are ${FULL_READING_PRICE_CENTS/100:.2f} each.",
                "price_usd": FULL_READING_PRICE_CENTS / 100,
            },
        )

    free_remaining = MAX_FREE_READINGS - (usage_count + 1)

    # 3. ALL free readings get the Instant Free Reading (template-based, no LLM).
    #    Premium LLM reports are reserved for paid tiers ($25/$69).
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
        try:
            event = _chart_event_from_request(
                request=request,
                payload=chart_payload,
                status="failed",
                error_message="Chart calculation failed.",
                generation_ms=int((time.perf_counter() - started) * 1000),
            )
            db.add(event)
            db.commit()
        except Exception as event_err:
            logger.error(
                "Chart event failure insert failed: %s",
                repr(event_err),
                exc_info=True,
            )
            db.rollback()
        raise HTTPException(
            status_code=500, detail="Chart calculation failed. Please try again."
        )

    if result["status"] == "failed":
        try:
            event = _chart_event_from_request(
                request=request,
                payload=chart_payload,
                status="failed",
                chart_summary=result.get("chart_data_summary", {}),
                reading_html=result.get("reading_html", ""),
                error_message=result.get("error", "Chart calculation failed."),
                generation_ms=int((time.perf_counter() - started) * 1000),
            )
            db.add(event)
            db.commit()
        except Exception as event_err:
            logger.error(
                "Chart event failure insert failed: %s",
                repr(event_err),
                exc_info=True,
            )
            db.rollback()
        raise HTTPException(
            status_code=500, detail=result.get("error", "Chart calculation failed.")
        )

    # 4. Record only successful free chart generation. Failed calculations should
    # not consume a visitor's free quota or inflate conversion KPIs.
    event = _chart_event_from_request(
        request=request,
        payload=chart_payload,
        status="completed",
        chart_summary=result.get("chart_data_summary", {}),
        reading_html=result["reading_html"],
        free_readings_remaining=free_remaining,
        generation_ms=int((time.perf_counter() - started) * 1000),
    )
    db.add(event)
    if enforce_free_limit:
        usage = GuestRequest(ip_address=client_ip, request_type="premium_guest")
        db.add(usage)
    db.commit()
    db.refresh(event)

    background_tasks.add_task(notify_chart_created, chart_payload, "Free Instant")

    # 5. Return instant result (no polling needed!)
    return {
        "status": "completed",
        "reading_html": result["reading_html"],
        "chart_summary": result.get("chart_data_summary", {}),
        "chart_event_id": event.id,
        "reading_hash": event.reading_hash,
        "free_readings_remaining": free_remaining,
        # Backward compat: frontend checks for task_id presence
        "instant": True,
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


# ─── Free Premium Add-On Constants ────────────────────────────────────────────
# Strictly per-IP using real visitor IPs (X-Forwarded-For via get_client_ip).
# Separate request_type key so this never touches the free-instant quota counter.
MAX_FREE_PREMIUM_REPORTS_PER_IP = 1
FREE_PREMIUM_REQUEST_TYPE = "free_premium_trial"


@router.post("/free-trial/request")
async def request_free_premium_trial(
    chart_request: ChartRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Kick off a free LLM-generated premium report in the background.

    - Limit: 1 lifetime report per real IP.
    - Uses get_client_ip() which reads X-Forwarded-For correctly on Cloud Run,
      so every visitor gets their own independent quota — not a shared proxy IP.
    - When the limit is hit we return status="limit_reached" (200) rather than
      a 402/error so the frontend can quietly hide the loading section without
      disturbing the visitor's free reading experience.
    - The caller polls /guest/status/{task_id} for result delivery.
    """
    client_ip = get_client_ip(request)
    enforce_limit = is_rate_limitable_client_ip(client_ip)
    if not enforce_limit:
        logger.warning(
            "Free premium report denied because client IP is not rate-limitable: %s",
            client_ip,
        )
        return {
            "status": "limit_reached",
            "message": "Free premium report requires a real visitor IP.",
        }

    trial_count = (
        db.query(GuestRequest)
        .filter(
            GuestRequest.ip_address == client_ip,
            GuestRequest.request_type == FREE_PREMIUM_REQUEST_TYPE,
        )
        .count()
    )
    if trial_count >= MAX_FREE_PREMIUM_REPORTS_PER_IP:
        logger.info(
            "Free premium report limit reached for IP %s (%d existing)",
            client_ip,
            trial_count,
        )
        return {
            "status": "limit_reached",
            "message": "The free premium report for this visitor has already been used.",
        }

    # Create the async task record
    task_id = str(uuid.uuid4())
    request_meta = {
        "name": chart_request.name or "Guest",
        "date": chart_request.date,
        "time": chart_request.time,
        "city": chart_request.city,
        "state": chart_request.state or "",
        "tier": "free_premium",
        "report_iterations": 1,
    }
    if current_user:
        request_meta["user_id"] = current_user.id
        request_meta["account_email"] = current_user.email
        request_meta["customer_email"] = current_user.email

    task = AsyncReportTask(
        id=task_id,
        status="pending",
        request_meta=request_meta,
    )
    db.add(task)

    # Record this usage against the visitor's IP so the counter is accurate.
    # Only written after task creation so partial failures don't waste quota.
    usage = GuestRequest(
        ip_address=client_ip,
        request_type=FREE_PREMIUM_REQUEST_TYPE,
    )
    db.add(usage)

    db.commit()
    db.refresh(task)

    # Fire the LLM generation as a background task — caller polls for status.
    request_data = dict(request_meta)
    background_tasks.add_task(generate_premium_report_task, task.id, request_data)
    background_tasks.add_task(notify_chart_created, request_data, "Free Premium")

    logger.info(
        "Free premium report started: task=%s ip=%s",
        task.id,
        client_ip,
    )
    return {
        "status": "started",
        "task_id": task.id,
        "tier": "free_premium",
        "free_premium_remaining": 0,
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
                    "title": "📧 Email Captured — Free Premium Report",
                    "color": 0xF6AD55,
                    "fields": [
                        {"name": "Email", "value": email, "inline": True},
                        {"name": "Name", "value": name, "inline": True},
                        {"name": "IP", "value": client_ip or "unknown", "inline": True},
                    ],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "footer": {"text": "Traditional Astrology · Free Premium Funnel"},
                }
            )
        except Exception as discord_err:
            logger.warning("Discord notify for email capture failed: %s", discord_err)

    return {"success": True}
