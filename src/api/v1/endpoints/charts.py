from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Depends

from src.api.v1.schemas import ChartRequest
from src.api.v1.auth import validate_token, get_current_user
from src.api.v1.utils import generate_chart_hash, log_event, result_to_model
from src.core.ratelimit import rate_limiter
from src.services.engine_bridge import (
    calculate_chart_async,
    perform_forensic_audit_async,
    calculate_forecast_async,
    generate_full_nativity_async
)
import logging

logger = logging.getLogger(__name__)

from src.engine.cache_manager import get_from_cache, set_to_cache
from src.engine.prediction import AdvancedPredictionEngine
from src.api.v1.utils import log_event as _log_event # Alias for compatibility or clarity
from src.middleware.quota import verify_quota
from src.api.v1.middleware.auth import verify_api_key
from src.api.v1.middleware.rate_limiting import enforce_rate_limit
from src.database.core import get_db
from src.database.models import UsageRecord, User
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.core.promo import free_individual_readings_promo_active

router = APIRouter()

# ... (helper function omitted)

@router.post("/generate")
async def generate_chart_b2b(
    chart_request: ChartRequest, 
    request: Request,
    auth_context: dict = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    B2B API Endpoint: Generate a high-throughput natal chart.
    
    Requires 'X-API-Key' header.
    
    Quotas:
    - Practitioner: 100 API calls/day
    - Studio: Unlimited API calls/day
    """
    if not auth_context:
        raise HTTPException(status_code=401, detail="Missing or invalid API Key")

    # 1. Enforce Rate Limit
    await enforce_rate_limit(request, auth_context)

    # 2. Check API Quota (daily)
    sub = auth_context['subscription']
    plan = auth_context['plan']
    
    if plan.api_quota is not None:
        period_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        used = db.query(func.sum(UsageRecord.cost_credits)).filter(
            UsageRecord.subscription_id == sub.id,
            UsageRecord.resource_type == 'api_call',
            UsageRecord.created_at >= period_start
        ).scalar() or 0
        
        if used >= plan.api_quota:
             raise HTTPException(status_code=429, detail="Daily API quota exceeded")

    # 3. Calculate Chart (Reuse existing logic or call bridge directly)
    # We'll call the bridge directly to avoid 'request' object dependency of logic above
    result = await calculate_chart_async(
        chart_request.date,
        chart_request.time,
        chart_request.city,
        chart_request.state,
        chart_request.house_system,
        bool(chart_request.compare_house_systems),
        chart_request.zodiac_system,
        chart_request.ayanamsa,
        chart_request.time_range_start,
        chart_request.time_range_end,
        chart_request.time_range_samples
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # 4. Record Usage
    try:
        new_record = UsageRecord(
            subscription_id=sub.id,
            user_id=auth_context['user'].id,
            resource_type='api_call',
            cost_credits=1,
            created_at=datetime.utcnow()
        )
        db.add(new_record)
        db.commit()
    except Exception as e:
        print(f"Usage recording failed: {e}")

    # 5. Return Result (JSON)
    # Filter result for API response? 
    # For now return full result as it contains positions etc.
    return result




@router.post("/calculate-full")
async def calculate_full_nativity(req: ChartRequest, http_request: Request):
    """
    Single Endpoint for Comprehensive Forensic Audit.
    """
    _log_event("chart_full_request", {"form": req.dict()}, http_request)
    try:
        # Call the new Engine via bridge
        result = await generate_full_nativity_async(
            date_str=req.date,
            time_str=req.time,
            city=req.city,
            state=req.state or "",
            name=req.name or "Native",
            house_system=req.house_system or "W",
            zodiac_system=req.zodiac_system or "tropical",
            ayanamsa=req.ayanamsa
        )
        
        if "error" in result:
            _log_event("chart_full_error", {"error": result["error"]}, http_request)
            raise HTTPException(status_code=400, detail=result["error"])
            
        _log_event("chart_full_success", {"result_keys": list(result.keys())}, http_request)
        return result

    except Exception as e:
        logger.error(f"Engine Failure: {str(e)}")
        _log_event("chart_full_failure", {"error": str(e)}, http_request)
        raise HTTPException(status_code=500, detail="Calculation Engine Error")


@router.post("/calculate")
async def calculate_chart(
    chart_request: ChartRequest,
    http_request: Request,
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Calculates a full natal chart including forensic audit, 5-day forecast, and plain-language synthesis.
    Now refactored to use the ForensicEngine via bridge.
    """
    _log_event("chart_request_server", {"form": chart_request.dict()}, http_request)
    
    chart_hash = generate_chart_hash(chart_request)
    tier = "free"
    plan_tier = None

    # Account required for readings. Exception: a valid access token (legacy magic link / purchase restore).
    if not current_user and not chart_request.access_token:
        raise HTTPException(status_code=401, detail="Account required to generate readings.")

    # Authenticated users with an active/trial subscription get full outputs.
    if current_user and current_user.subscription and current_user.subscription.plan:
        if current_user.subscription.status in {"active", "trial"} and current_user.subscription.plan.tier != "free":
            tier = "paid"
            plan_tier = current_user.subscription.plan.tier

    # Legacy access token path (kept for backward compatibility).
    if tier == "free" and chart_request.access_token:
        payload = validate_token(chart_request.access_token)
        if not payload or payload.get("chart_hash") != chart_hash:
            # No user + invalid token should not get a reading.
            if not current_user:
                raise HTTPException(status_code=401, detail="Invalid or expired access token. Please log in.")
        else:
            tier = "paid"
    
    # Cache Check
    cached_result = get_from_cache(chart_hash, tier)
    if cached_result:
        return cached_result

    # Rate Limiting (Free Tier Only)
    if tier == 'free':
        client_ip = http_request.client.host if http_request.client else "unknown"
        if client_ip != "127.0.0.1" and not rate_limiter.is_allowed(client_ip):
            raise HTTPException(status_code=429, detail="Daily free limit reached.")

    # Call the new Engine via bridge
    engine_result = await generate_full_nativity_async(
        date_str=chart_request.date,
        time_str=chart_request.time,
        city=chart_request.city,
        state=chart_request.state or "",
        name=chart_request.name or "Native",
        house_system=chart_request.house_system or "W",
        zodiac_system=chart_request.zodiac_system or "tropical",
        ayanamsa=chart_request.ayanamsa
    )

    if "error" in engine_result:
        _log_event("chart_error_server", {"error": engine_result["error"]}, http_request)
        raise HTTPException(status_code=400, detail=engine_result["error"])

    # Transform back to legacy format for UI compatibility if needed
    # (Actually the UI should probably be updated but let's keep it working for now)
    # The ForensicEngine already packs what it can into a compatible-ish format.
    # Let's add the meta fields back for the frontend
    final_result = engine_result.get("technical_data", {})
    # Add human translation for the frontend to render
    final_result["report_markdown"] = engine_result["human_translation"]["report_markdown"]
    final_result["executive_summary"] = engine_result["human_translation"]["executive_summary"]
    
    # Mock some legacy fields that script.js might expect
    final_result["forensic_report"] = engine_result["technical_data"]["analysis"]
        
    final_result["meta"]["tier"] = tier
    final_result["meta"]["chart_hash"] = chart_hash
    # Promo: unlock individual readings for a limited time (UI decides how to gate).
    final_result["meta"]["promo_unlocked"] = bool(free_individual_readings_promo_active())
    if plan_tier:
        final_result["meta"]["plan_tier"] = plan_tier

    # Safety: do not run LLM/oracle interpretation in production API responses.
    # Keep deterministic executive summary only.
    final_result["plain_reading"] = final_result.get("executive_summary", "Reading unavailable. Please try again.")

    # SAVE TO CACHE
    set_to_cache(chart_hash, tier, final_result)

    # AUTO-SAVE FOR LOGGED IN USERS
    if current_user:
        try:
            from src.engine.user_auth import get_user_manager
            userManager = get_user_manager()
            userManager.save_chart_by_user_id(
                user_id=current_user.id,
                chart_hash=chart_hash,
                chart_meta={
                    "name": chart_request.name or "Untitled Chart",
                    "date": chart_request.date,
                    "time": chart_request.time,
                    "city": chart_request.city,
                    "state": chart_request.state,
                    "house_system": chart_request.house_system or "W",
                    "zodiac_system": chart_request.zodiac_system or "tropical",
                }
            )
        except Exception as save_err:
            logger.error(f"Auto-save failed: {save_err}")

    _log_event("chart_result_server", {"result_keys": list(final_result.keys())}, http_request)
    return final_result


# ============================================================================
# USER CHART MANAGEMENT ENDPOINTS
# ============================================================================

from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List as _List
from io import BytesIO
import zipfile
import re


@router.get("/saved")
async def get_user_charts(current_user: User = Depends(get_current_user)):
    """
    Get all saved charts for the current user.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    charts = current_user.charts_saved or []
    return {"charts": charts}


@router.get("/saved/{chart_index}")
async def get_saved_chart(chart_index: int, current_user: User = Depends(get_current_user)):
    """
    Get a specific saved chart by index for the current user.
    Returns the chart metadata which can be used to regenerate the full report.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    charts = current_user.charts_saved or []
    
    if chart_index < 0 or chart_index >= len(charts):
        raise HTTPException(status_code=404, detail="Chart not found")
    
    chart = charts[chart_index]
    chart["index"] = chart_index
    return {"chart": chart}


@router.get("/saved/{chart_index}/pdf")
async def download_chart_pdf(chart_index: int, current_user: User = Depends(get_current_user)):
    """
    Generate and download a PDF report for a saved chart.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    charts = current_user.charts_saved or []
    
    if chart_index < 0 or chart_index >= len(charts):
        raise HTTPException(status_code=404, detail="Chart not found")
    
    chart_meta = charts[chart_index]
    
    # Regenerate the chart data
    try:
        engine_result = await generate_full_nativity_async(
            date_str=chart_meta.get("date", ""),
            time_str=chart_meta.get("time", ""),
            city=chart_meta.get("city", ""),
            state=chart_meta.get("state", ""),
            name=chart_meta.get("name", "Native"),
            house_system=chart_meta.get("house_system", "W"),
            zodiac_system=chart_meta.get("zodiac_system", "tropical"),
            ayanamsa=chart_meta.get("ayanamsa")
        )
        
        if "error" in engine_result:
            raise HTTPException(status_code=400, detail=engine_result["error"])
        
        # Generate PDF
        from src.engine.pdf_generator import PDFReportGenerator
        
        report_md = engine_result.get("human_translation", {}).get("report_markdown", "") or ""
        pdf_data = {
            "meta": engine_result.get("technical_data", {}).get("meta", {}),
            "forensic_report": engine_result.get("technical_data", {}).get("analysis", {}),
        }

        generator = PDFReportGenerator(pdf_data)
        # Prefer the deterministic markdown report body (safer than medical/decisioning tables).
        pdf_buffer = generator.generate(custom_content=report_md if report_md else None)
        
        # Create filename from chart name or date
        chart_name = chart_meta.get("name", "chart").replace(" ", "_")
        filename = f"codex_caelestis_{chart_name}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"PDF Generation Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")


@router.delete("/saved/{chart_index}")
async def delete_saved_chart(
    chart_index: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a saved chart by index.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    charts = current_user.charts_saved or []
    
    if chart_index < 0 or chart_index >= len(charts):
        raise HTTPException(status_code=404, detail="Chart not found")
    
    # Remove the chart
    charts.pop(chart_index)
    current_user.charts_saved = charts
    db.commit()
    
    return {"success": True, "message": "Chart deleted"}


class BulkPdfRequest(BaseModel):
    items: _List[ChartRequest]
    filename_prefix: str = "codex_caelestis"


def _safe_filename(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9._-]+", "_", s)
    return s.strip("._-") or "report"


@router.post("/bulk/pdf")
async def bulk_generate_pdfs(
    payload: BulkPdfRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generate a ZIP of PDFs from a batch of ChartRequests.

    Safety: authenticated users only; intended for professional use.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    sub = current_user.subscription
    if not sub or not sub.plan or sub.status not in {"active", "trial"}:
        raise HTTPException(status_code=403, detail="Active subscription required")
    if sub.plan.tier not in {"practitioner", "studio"}:
        raise HTTPException(status_code=403, detail="Upgrade required")

    items = payload.items or []
    if not items:
        raise HTTPException(status_code=400, detail="No items provided")

    max_items = 20 if sub.plan.tier == "practitioner" else 200
    if len(items) > max_items:
        raise HTTPException(status_code=400, detail=f"Too many items (max {max_items})")

    zip_buf = BytesIO()
    errors = []

    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for idx, it in enumerate(items, start=1):
            try:
                engine_result = await generate_full_nativity_async(
                    date_str=it.date,
                    time_str=it.time,
                    city=it.city,
                    state=it.state or "",
                    name=it.name or "Native",
                    house_system=it.house_system or "W",
                    zodiac_system=it.zodiac_system or "tropical",
                    ayanamsa=it.ayanamsa
                )
                if "error" in engine_result:
                    raise ValueError(engine_result["error"])

                report_md = engine_result.get("human_translation", {}).get("report_markdown", "") or ""
                pdf_data = {
                    "meta": engine_result.get("technical_data", {}).get("meta", {}),
                    "forensic_report": engine_result.get("technical_data", {}).get("analysis", {}),
                }
                from src.engine.pdf_generator import PDFReportGenerator
                gen = PDFReportGenerator(pdf_data)
                pdf_buffer = gen.generate(custom_content=report_md if report_md else None)
                pdf_bytes = pdf_buffer.getvalue()
                gen.buffer.close()

                name = _safe_filename(it.name or f"native_{idx}")
                date_part = _safe_filename(it.date or "")
                fn = f"{_safe_filename(payload.filename_prefix)}_{idx:03d}_{name}_{date_part}.pdf"
                zf.writestr(fn, pdf_bytes)
            except Exception as e:
                errors.append(f"Item {idx}: {str(e)}")

        if errors:
            zf.writestr("errors.txt", "\n".join(errors) + "\n")

    zip_buf.seek(0)
    out_name = f"{_safe_filename(payload.filename_prefix)}_pdf_pack.zip"
    return StreamingResponse(
        zip_buf,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={out_name}"},
    )

