import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from src.api.v1.auth import get_current_user
from src.api.v1.endpoints.daily import WeeklyBriefingRequest, weekly_briefing
from src.api.v1.schemas import ChartRequest
from src.api.v1.utils import generate_chart_hash
from src.database.core import get_db
from src.database.models import AsyncReportTask, User

logger = logging.getLogger(__name__)

router = APIRouter()


class SavedChartRequest(BaseModel):
    name: str = Field("Saved Chart", max_length=150)
    date: str = Field(..., max_length=20)
    time: str = Field("12:00", max_length=20)
    city: str = Field(..., max_length=150)
    state: Optional[str] = Field("", max_length=100)
    house_system: Optional[str] = Field("W", max_length=20)
    zodiac_system: Optional[str] = Field("tropical", max_length=50)
    ayanamsa: Optional[str] = Field(None, max_length=50)
    label: Optional[str] = Field("", max_length=80)


def _require_user(current_user: Optional[User]) -> User:
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user


def _chart_limit_for_user(user: User) -> int:
    tier = "free"
    try:
        if user.subscription and user.subscription.plan:
            tier = user.subscription.plan.tier or "free"
    except Exception as e:
        logger.warning("Could not resolve chart limit tier: %s", repr(e), exc_info=True)
    if tier == "studio":
        return 10000
    if tier == "practitioner":
        return 100
    return 10


def _with_indices(charts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{**chart, "index": index} for index, chart in enumerate(charts)]


def _report_summary(task: AsyncReportTask) -> dict[str, Any]:
    meta = task.request_meta or {}
    result = task.result_json or {}
    generated_words = 0
    if isinstance(result, dict):
        report = result.get("report_markdown") or ""
        generated_words = len(str(report).split()) if report else 0
    return {
        "task_id": task.id,
        "status": task.status,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "tier": meta.get(
            "tier", result.get("tier") if isinstance(result, dict) else None
        ),
        "name": meta.get("name") or "Chart",
        "date": meta.get("date"),
        "time": meta.get("time"),
        "city": meta.get("city"),
        "state": meta.get("state"),
        "report_iterations": meta.get(
            "report_iterations",
            result.get("report_iterations") if isinstance(result, dict) else None,
        ),
        "generated_words": generated_words,
        "has_report": bool(generated_words),
    }


def _owned_reports_query(db: Session, user: User):
    email = (user.email or "").lower().strip()
    return db.query(AsyncReportTask).filter(
        or_(
            AsyncReportTask.request_meta["user_id"].as_string() == user.id,
            AsyncReportTask.request_meta["customer_email"].as_string() == email,
            AsyncReportTask.request_meta["account_email"].as_string() == email,
        )
    )


@router.get("/overview")
async def account_overview(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    user = _require_user(current_user)
    charts = list(user.charts_saved or [])
    reports = (
        _owned_reports_query(db, user)
        .order_by(AsyncReportTask.created_at.desc())
        .limit(25)
        .all()
    )
    return {
        "charts": _with_indices(charts),
        "reports": [_report_summary(task) for task in reports],
        "limits": {"saved_charts": _chart_limit_for_user(user)},
    }


@router.get("/charts")
async def account_charts(current_user: User = Depends(get_current_user)):
    user = _require_user(current_user)
    return {
        "charts": _with_indices(list(user.charts_saved or [])),
        "limit": _chart_limit_for_user(user),
    }


@router.post("/charts")
async def save_account_chart(
    payload: SavedChartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = _require_user(current_user)

    chart_request = ChartRequest(
        name=payload.name,
        date=payload.date,
        time=payload.time or "12:00",
        city=payload.city,
        state=payload.state or "",
        house_system=payload.house_system or "W",
        zodiac_system=payload.zodiac_system or "tropical",
        ayanamsa=payload.ayanamsa,
    )
    chart_hash = generate_chart_hash(chart_request)
    charts = list(user.charts_saved or [])

    for index, chart in enumerate(charts):
        if chart.get("hash") == chart_hash:
            updated = {
                **chart,
                "name": payload.name.strip() or chart.get("name") or "Saved Chart",
                "label": (payload.label or chart.get("label") or "").strip()[:80],
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            charts[index] = updated
            user.charts_saved = charts  # type: ignore
            flag_modified(user, "charts_saved")
            db.add(user)
            db.commit()
            return {
                "success": True,
                "chart": {**updated, "index": index},
                "created": False,
            }

    limit = _chart_limit_for_user(user)
    if len(charts) >= limit:
        raise HTTPException(
            status_code=403,
            detail=f"Saved chart limit reached for this account ({limit}).",
        )

    entry = {
        "hash": chart_hash,
        "name": payload.name.strip() or "Saved Chart",
        "date": payload.date,
        "time": payload.time or "12:00",
        "city": payload.city.strip(),
        "state": (payload.state or "").strip(),
        "house_system": payload.house_system or "W",
        "zodiac_system": payload.zodiac_system or "tropical",
        "ayanamsa": payload.ayanamsa,
        "label": (payload.label or "").strip()[:80],
        "source": "account",
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    charts.append(entry)
    user.charts_saved = charts  # type: ignore
    flag_modified(user, "charts_saved")
    db.add(user)
    db.commit()
    return {
        "success": True,
        "chart": {**entry, "index": len(charts) - 1},
        "created": True,
    }


@router.delete("/charts/{chart_index}")
async def delete_account_chart(
    chart_index: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = _require_user(current_user)
    charts = list(user.charts_saved or [])
    if chart_index < 0 or chart_index >= len(charts):
        raise HTTPException(status_code=404, detail="Chart not found")
    removed = charts.pop(chart_index)
    user.charts_saved = charts  # type: ignore
    flag_modified(user, "charts_saved")
    db.add(user)
    db.commit()
    return {"success": True, "removed": removed, "charts": _with_indices(charts)}


@router.get("/charts/{chart_index}/transits")
async def account_chart_transits(
    chart_index: int,
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    days: int = Query(7, ge=1, le=14),
    current_user: User = Depends(get_current_user),
):
    user = _require_user(current_user)
    charts = list(user.charts_saved or [])
    if chart_index < 0 or chart_index >= len(charts):
        raise HTTPException(status_code=404, detail="Chart not found")

    chart = charts[chart_index]
    request = WeeklyBriefingRequest(
        date=chart.get("date", ""),
        time=chart.get("time", "12:00"),
        city=chart.get("city", ""),
        state=chart.get("state", ""),
        name=chart.get("name", "Native"),
        start_date=start_date,
        days=days,
        house_system=chart.get("house_system") or "W",
        zodiac_system=chart.get("zodiac_system") or "tropical",
    )
    return await weekly_briefing(request)


@router.get("/reports")
async def account_reports(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    user = _require_user(current_user)
    reports = (
        _owned_reports_query(db, user)
        .order_by(AsyncReportTask.created_at.desc())
        .limit(50)
        .all()
    )
    return {"reports": [_report_summary(task) for task in reports]}


@router.get("/reports/{task_id}")
async def account_report_detail(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = _require_user(current_user)
    task = _owned_reports_query(db, user).filter(AsyncReportTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Report not found")

    result = task.result_json or {}
    response = _report_summary(task)
    if task.status == "completed" and isinstance(result, dict):
        response["report_markdown"] = result.get("report_markdown") or ""
        response["computation_trace"] = result.get("computation_trace")
    elif task.status == "failed" and isinstance(result, dict):
        response["error"] = result.get("error") or "Report generation failed."
    return {"report": response}
