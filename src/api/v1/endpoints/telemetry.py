import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.v1.auth import validate_token
from src.api.v1.client_ip import get_client_ip
from src.api.v1.schemas import LeadCapture, ReadingFeedback, TelemetryEvent  # type: ignore
from src.database.core import get_db
from src.database.models import ChartEvent, Lead, ReadingFeedbackEvent
from src.engine.logger import ActivityLogger
from src.services.notifications import AdminNotificationService

router = APIRouter()


def _normalized_vote(vote: str) -> str:
    return "good" if vote in {"good", "up"} else "bad"


def _feedback_counts(db: Session, reading_hash: str) -> dict:
    rows = (
        db.query(ReadingFeedbackEvent.vote)
        .filter(ReadingFeedbackEvent.reading_hash == reading_hash)
        .all()
    )
    good = sum(1 for (vote,) in rows if vote == "good")
    bad = sum(1 for (vote,) in rows if vote == "bad")
    total = good + bad
    return {"total": total, "good": good, "bad": bad, "up": good, "down": bad}


@router.post("/log/telemetry")
async def log_telemetry(event: TelemetryEvent, request: Request):
    """
    Log frontend events (clicks, errors, navigation).
    """
    client_ip = get_client_ip(request)

    # Try to extract user ID from token if present
    auth_header = request.headers.get("Authorization")
    user_id = "guest"
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            payload = validate_token(token)
            if payload and "d" in payload and "user_id" in payload["d"]:
                user_id = payload["d"]["user_id"]
        except Exception as e:
            logging.debug("Telemetry token parse failed: %s", e)

    ActivityLogger.log_activity(
        f"frontend_{event.event_type}",
        user_id=user_id,
        ip=client_ip,
        details={"element": event.element_id, "url": event.url, "data": event.data},
    )
    return {"status": "logged"}


@router.post("/log_event")
async def log_event_alias(event: TelemetryEvent, request: Request):
    """
    Alias for /log/telemetry to support legacy frontend calls.
    """
    return await log_telemetry(event, request)


@router.post("/reading_feedback")
async def log_reading_feedback(
    feedback: ReadingFeedback,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Log user feedback on readings.
    """
    client_ip = get_client_ip(request)
    vote = _normalized_vote(feedback.vote)

    # Try to extract user ID from token if present
    auth_header = request.headers.get("Authorization")
    user_id = "guest"
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            payload = validate_token(token)
            if payload and "d" in payload and "user_id" in payload["d"]:
                user_id = payload["d"]["user_id"]
        except Exception as e:
            logging.debug("Feedback token parse failed: %s", e)

    ActivityLogger.log_activity(
        "reading_feedback",
        user_id=user_id,
        ip=client_ip,
        details={
            "reading_hash": feedback.reading_hash,
            "vote": vote,
            "chart_event_id": feedback.chart_event_id,
            "source": feedback.source,
            "birth": feedback.birth,
            "meta": feedback.meta,
            "time_unknown": feedback.time_unknown,
            "session_id": feedback.session_id,
            "comment": feedback.comment,
            "ts": feedback.ts,
        },
    )

    chart_event_id = feedback.chart_event_id
    if chart_event_id:
        existing_chart_event = (
            db.query(ChartEvent).filter(ChartEvent.id == chart_event_id).first()
        )
        if not existing_chart_event:
            chart_event_id = None

    event = ReadingFeedbackEvent(
        chart_event_id=chart_event_id,
        reading_hash=feedback.reading_hash,
        vote=vote,
        source=feedback.source,
        birth=feedback.birth,
        meta=feedback.meta,
        time_unknown=bool(feedback.time_unknown),
        session_id=feedback.session_id,
        comment=feedback.comment,
        client_ip=client_ip,
        user_agent=request.headers.get("user-agent"),
        referer=request.headers.get("referer"),
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    try:
        AdminNotificationService.notify_reading_feedback(
            vote=vote,
            source=feedback.source or "",
            comment=feedback.comment or "",
            chart_event_id=chart_event_id or "",
            reading_hash=feedback.reading_hash,
            birth=feedback.birth or {},
            url=request.headers.get("referer", ""),
            ua=request.headers.get("user-agent", ""),
        )
    except Exception as e:
        logging.error("Reading feedback notification failed: %s", repr(e), exc_info=True)

    return {
        "status": "feedback_saved",
        "feedback_id": event.id,
        "chart_event_id": chart_event_id,
        "vote": vote,
        "counts": _feedback_counts(db, feedback.reading_hash),
    }


@router.post("/lead")
async def capture_lead(
    lead: LeadCapture, request: Request, db: Session = Depends(get_db)
):
    """
    Minimal marketing lead capture for funnels (e.g., /gig-economy.html).

    Storage:
    - ActivityLogger (JSONL) for easy ops parsing.
    - Optional admin email notification via OWNER_EMAILS.

    Safety:
    - No birth data accepted here.
    - No advice provided; this is operational intake only.
    """
    email = (lead.email or "").strip()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email")

    client_ip = get_client_ip(request)
    details = {
        "email": email,
        "segment": (lead.segment or "").strip(),
        "platform": (lead.platform or "").strip(),
        "volume": (lead.volume or "").strip(),
        "pain": (lead.pain or "").strip(),
        "url": (lead.url or "").strip(),
        "ua": (lead.ua or "").strip(),
    }

    ActivityLogger.log_activity(
        "lead_captured", user_id="guest", ip=client_ip, details=details
    )

    # Persist to DB for KPI visibility + follow-up. De-dupe to reduce spam.
    try:
        window_start = datetime.now(timezone.utc) - timedelta(hours=24)
        existing = (
            db.query(Lead)
            .filter(Lead.email == email)
            .filter(Lead.created_at >= window_start)
            .order_by(Lead.created_at.desc())
            .first()
        )
        if not existing:
            rec = Lead(
                email=email,
                segment=details["segment"] or None,
                platform=details["platform"] or None,
                volume=details["volume"] or None,
                pain=details["pain"] or None,
                url=details["url"] or None,
                ua=details["ua"] or None,
                ip=client_ip,
            )
            db.add(rec)
            db.commit()
    except Exception as e:
        # Non-fatal: we still logged to JSONL.
        logging.error("Lead DB insert failed: %s", repr(e), exc_info=True)
        try:
            db.rollback()
        except Exception:
            pass

    try:
        AdminNotificationService.notify_lead_captured(
            email=email,
            segment=details["segment"],
            platform=details["platform"],
            volume=details["volume"],
            pain=details["pain"],
            url=details["url"],
            ua=details["ua"],
        )
    except Exception as e:
        logging.error("Lead capture notification failed: %s", repr(e), exc_info=True)

    return {"status": "ok"}
