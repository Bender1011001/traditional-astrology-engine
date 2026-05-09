import logging
import uuid
from typing import Any

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.v1.client_ip import get_client_ip
from src.api.v1.middleware.horary_rate_limiter import enforce_horary_rate_limit
from src.api.v1.schemas import HoraryRequest  # type: ignore
from src.api.v1.utils import result_to_model
from src.core.config import settings
from src.database.core import get_db
from src.database.models import AsyncReportTask, GuestRequest
from src.engine.calculator.main import calculate_chart_data
from src.engine.horary import build_horary_oracle

router = APIRouter()
logger = logging.getLogger(__name__)

HORARY_QUESTION_TIER = "horary_question"
HORARY_QUESTION_PRICE_CENTS = 500
HORARY_QUESTION_PRODUCT_NAME = "Horary Oracle Question"
_HORARY_PRICE_CACHE: str | None = None


def _stripe_field(obj: Any, key: str, default: Any = None) -> Any:
    if hasattr(obj, "get"):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _metadata(obj: Any) -> dict[str, Any]:
    metadata = _stripe_field(obj, "metadata", {}) or {}
    if hasattr(metadata, "to_dict"):
        return dict(metadata.to_dict())
    return dict(metadata)


def _is_ready_horary_price(price_id: str) -> bool:
    try:
        price = stripe.Price.retrieve(price_id, expand=["product"])
        product = _stripe_field(price, "product")
        if isinstance(product, str):
            product = stripe.Product.retrieve(product)

        metadata = _metadata(price)
        return (
            bool(_stripe_field(price, "active", False))
            and bool(_stripe_field(product, "active", False))
            and int(_stripe_field(price, "unit_amount", 0) or 0)
            == HORARY_QUESTION_PRICE_CENTS
            and str(_stripe_field(price, "currency", "") or "").lower() == "usd"
            and metadata.get("tier") == HORARY_QUESTION_TIER
        )
    except Exception as e:
        logger.warning(
            "Stripe horary price validation failed for %s: %s",
            price_id,
            repr(e),
            exc_info=True,
        )
        return False


def _get_or_create_horary_price() -> str:
    global _HORARY_PRICE_CACHE

    if _HORARY_PRICE_CACHE and _is_ready_horary_price(_HORARY_PRICE_CACHE):
        return _HORARY_PRICE_CACHE
    _HORARY_PRICE_CACHE = None

    configured = (getattr(settings, "STRIPE_PRICE_HORARY_QUESTION", "") or "").strip()
    if configured and _is_ready_horary_price(configured):
        _HORARY_PRICE_CACHE = configured
        return configured

    try:
        prices = stripe.Price.search(
            query=f'active:"true" metadata["tier"]:"{HORARY_QUESTION_TIER}"',
            limit=10,
        )
        for candidate in prices.data or []:
            price_id = _stripe_field(candidate, "id")
            if price_id and _is_ready_horary_price(str(price_id)):
                _HORARY_PRICE_CACHE = str(price_id)
                return str(price_id)
    except Exception as e:
        logger.warning("Stripe horary price search failed: %s", repr(e), exc_info=True)

    try:
        product = stripe.Product.create(
            name=HORARY_QUESTION_PRODUCT_NAME,
            description=(
                "One focused traditional horary astrology question, judged by "
                "classical Regiomontanus rules."
            ),
            metadata={"tier": HORARY_QUESTION_TIER},
        )
        price = stripe.Price.create(
            product=product.id,
            unit_amount=HORARY_QUESTION_PRICE_CENTS,
            currency="usd",
            metadata={"tier": HORARY_QUESTION_TIER},
        )
        _HORARY_PRICE_CACHE = price.id
        logger.info("Created Stripe horary price %s", price.id)
        return str(price.id)
    except Exception as e:
        logger.error("Failed to create Stripe horary price: %s", repr(e), exc_info=True)
        raise


def _validated_question_payload(payload: HoraryRequest) -> HoraryRequest:
    question = (payload.question or "").strip()
    city = (payload.city or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required for horary.")
    if not city:
        raise HTTPException(status_code=400, detail="City is required for horary.")
    return payload.model_copy(update={"question": question, "city": city})


def _payload_from_session_metadata(metadata: dict[str, Any]) -> HoraryRequest:
    if str(metadata.get("purchase_type") or "") != HORARY_QUESTION_TIER:
        raise HTTPException(status_code=400, detail="Not a paid horary checkout.")

    def optional_float(value: Any) -> float | None:
        if value in {None, ""}:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    return HoraryRequest(
        question=str(metadata.get("question") or ""),
        city=str(metadata.get("city") or ""),
        state=str(metadata.get("state") or ""),
        date=str(metadata.get("date") or "") or None,
        time=str(metadata.get("time") or "") or None,
        latitude=optional_float(metadata.get("latitude")),
        longitude=optional_float(metadata.get("longitude")),
    )


def _build_horary_answer(payload: HoraryRequest) -> dict[str, Any]:
    payload = _validated_question_payload(payload)

    date_str = payload.date
    time_str = payload.time
    lat = getattr(payload, "latitude", None)
    lon = getattr(payload, "longitude", None)

    if not date_str or not time_str or lat is None or lon is None:
        from datetime import datetime

        import pytz  # type: ignore

        from src.engine.calculator.geo import get_coordinates, get_timezone

        try:
            if lat is None or lon is None:
                lat, lon = get_coordinates(payload.city, payload.state)
            if not date_str or not time_str:
                tz_str = get_timezone(lat, lon)
                local_dt = datetime.now(pytz.timezone(tz_str))
                date_str = date_str or local_dt.strftime("%Y-%m-%d")
                time_str = time_str or local_dt.strftime("%H:%M")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Location error: {str(e)}")

    res = calculate_chart_data(
        date_str,
        time_str,
        payload.city,
        payload.state,
        latitude=lat,
        longitude=lon,
        house_system="R",
    )
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])

    chart_model = result_to_model(res)
    oracle = build_horary_oracle(payload.question, chart_model)
    return {"meta": res.get("meta", {}), "oracle": oracle}


@router.post("/horary/checkout")
async def create_paid_horary_checkout(payload: HoraryRequest, request: Request):
    """
    Create a cheap one-time Stripe Checkout Session for a single horary question.
    """
    payload = _validated_question_payload(payload)

    if str(getattr(settings, "SALES_MODE", "live")).strip().lower() != "live":
        raise HTTPException(status_code=409, detail="Checkout is currently paused.")

    stripe.api_key = (getattr(settings, "STRIPE_SECRET_KEY", "") or "").strip()
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Payment system not configured.")

    try:
        price_id = _get_or_create_horary_price()
        order_id = uuid.uuid4().hex[:12]
        origin = str(request.base_url).rstrip("/")
        metadata = {
            "purchase_type": HORARY_QUESTION_TIER,
            "tier": HORARY_QUESTION_TIER,
            "order_id": order_id,
            "question": payload.question[:500],
            "city": payload.city[:150],
            "state": (payload.state or "")[:100],
            "date": payload.date or "",
            "time": payload.time or "",
            "latitude": "" if payload.latitude is None else str(payload.latitude),
            "longitude": "" if payload.longitude is None else str(payload.longitude),
        }
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
            allow_promotion_codes=True,
            success_url=(
                f"{origin}/horary.html?horary_paid=success"
                f"&session_id={{CHECKOUT_SESSION_ID}}&order={order_id}"
            ),
            cancel_url=f"{origin}/horary.html?horary_paid=cancelled",
            metadata=metadata,
        )
        return {"url": session.url, "session_id": session.id, "order_id": order_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Stripe paid horary checkout creation failed: %s", repr(e), exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Could not create checkout session."
        )


@router.post("/horary/paid-answer")
async def paid_horary_answer(
    request: Request,
    session_id: str,
    db: Session = Depends(get_db),
):
    """
    Verify a paid Stripe session and return the purchased horary answer.
    Idempotent: the same Checkout Session returns the same stored answer.
    """
    stripe.api_key = (getattr(settings, "STRIPE_SECRET_KEY", "") or "").strip()
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Payment system not configured.")

    existing_task = (
        db.query(AsyncReportTask).filter(AsyncReportTask.id == session_id).first()
    )
    if (
        existing_task
        and existing_task.status == "completed"
        and existing_task.result_json
    ):
        result = dict(existing_task.result_json)
        result["paid"] = True
        result["session_id"] = session_id
        return result

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        logger.warning(
            "Stripe paid horary session retrieval failed for %s: %s",
            session_id,
            repr(e),
            exc_info=True,
        )
        raise HTTPException(status_code=400, detail="Invalid checkout session.")

    payment_status = str(_stripe_field(session, "payment_status", "") or "")
    if payment_status not in {"paid", "no_payment_required"}:
        raise HTTPException(status_code=402, detail="Payment not completed.")

    metadata = _metadata(session)
    payload = _payload_from_session_metadata(metadata)
    result = _build_horary_answer(payload)
    result["question"] = payload.question
    result["paid"] = True
    result["session_id"] = session_id
    result["order_id"] = metadata.get("order_id")

    request_meta = payload.model_dump()
    request_meta.update(
        {
            "tier": HORARY_QUESTION_TIER,
            "stripe_session_id": session_id,
            "order_id": metadata.get("order_id"),
        }
    )

    try:
        if existing_task:
            existing_task.status = "completed"
            existing_task.request_meta = request_meta
            existing_task.result_json = result
            task = existing_task
        else:
            task = AsyncReportTask(
                id=session_id,
                status="completed",
                request_meta=request_meta,
                result_json=result,
            )
            db.add(task)

        db.add(
            GuestRequest(
                ip_address=get_client_ip(request),
                request_type="paid_horary_question",
            )
        )
        db.commit()
        db.refresh(task)
    except Exception as e:
        db.rollback()
        logger.error(
            "Failed to persist paid horary answer for %s: %s",
            session_id,
            repr(e),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Could not save horary answer.")

    return result


@router.post("/horary", dependencies=[Depends(enforce_horary_rate_limit)])
async def horary_oracle(payload: HoraryRequest, request: Request):
    """
    Legacy free horary API with IP rate limiting. The public page now uses the
    paid checkout flow, but this route remains for compatibility.
    """
    result = _build_horary_answer(payload)
    result["question"] = payload.question
    result["paid"] = False
    result["checkout_available"] = True
    return result
