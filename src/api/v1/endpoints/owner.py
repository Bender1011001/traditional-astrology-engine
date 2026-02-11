from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from src.api.v1.auth import get_current_user
from src.api.v1.schemas import OwnerSubscriptionUpdateRequest
from src.core.config import settings
from src.database.core import get_db
from src.database.models import Invoice, Lead, OutreachTarget, SubscriptionPlan, User, UserSubscription

router = APIRouter()


def _owner_emails() -> List[str]:
    return [email.strip().lower() for email in settings.OWNER_EMAILS.split(",") if email.strip()]


def require_owner(
    current_user: Optional[User] = Depends(get_current_user),
    owner_key: Optional[str] = Header(None, alias="X-Owner-Key"),
) -> Optional[User]:
    if owner_key and settings.OWNER_BOOTSTRAP_KEY and owner_key == settings.OWNER_BOOTSTRAP_KEY:
        return current_user

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")

    owner_emails = _owner_emails()
    if current_user.email.lower() not in owner_emails:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner access required.")

    return current_user


@router.get("/verify")
def verify_owner(owner: Optional[User] = Depends(require_owner)):
    if owner:
        return {"ok": True, "email": owner.email}
    return {"ok": True}


@router.get("/plans")
def list_plans(
    owner: Optional[User] = Depends(require_owner),
    db: Session = Depends(get_db),
):
    plans = db.query(SubscriptionPlan).order_by(SubscriptionPlan.tier.asc()).all()
    return {
        "plans": [
            {
                "id": plan.id,
                "tier": plan.tier,
                "price_monthly": float(plan.price_monthly),
                "price_annual": float(plan.price_annual) if plan.price_annual is not None else None,
                "chart_quota": plan.chart_quota,
                "api_quota": plan.api_quota,
            }
            for plan in plans
        ]
    }


@router.get("/users")
def list_users(
    owner: Optional[User] = Depends(require_owner),
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    plan: Optional[str] = None,
    status_filter: Optional[str] = None,
    payment_status_filter: Optional[str] = None,
):
    query = db.query(User).outerjoin(UserSubscription).outerjoin(SubscriptionPlan)

    if q:
        query = query.filter(User.email.ilike(f"%{q.lower()}%"))

    if plan:
        query = query.filter(SubscriptionPlan.tier == plan)

    if status_filter:
        query = query.filter(UserSubscription.status == status_filter)

    users = query.order_by(User.created_at.desc()).all()
    results = []
    for user in users:
        sub = user.subscription
        plan_name = sub.plan.tier if sub and sub.plan else "free"
        last_invoice = (
            db.query(Invoice)
            .filter(Invoice.user_id == user.id)
            .order_by(Invoice.created_at.desc())
            .first()
        )

        payment_status = last_invoice.status if last_invoice else "none"
        if payment_status_filter and payment_status != payment_status_filter:
            continue

        results.append(
            {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "email_verified": user.email_verified,
                "charts_saved_count": len(user.charts_saved or []),
                "api_keys_count": len(user.api_keys or []),
                "subscription": {
                    "status": sub.status if sub else "none",
                    "plan_tier": plan_name,
                    "current_period_end": sub.current_period_end.isoformat() if sub and sub.current_period_end else None,
                    "cancel_at_period_end": sub.cancel_at_period_end if sub else False,
                },
                "payment": {
                    "status": payment_status,
                    "amount_paid": float(last_invoice.amount_paid) if last_invoice and last_invoice.amount_paid else None,
                    "amount_due": float(last_invoice.amount_due) if last_invoice and last_invoice.amount_due else None,
                    "invoice_date": last_invoice.created_at.isoformat() if last_invoice else None,
                },
            }
        )

    return {"users": results}


@router.post("/subscription/update")
def update_subscription(
    payload: OwnerSubscriptionUpdateRequest,
    owner: Optional[User] = Depends(require_owner),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == payload.plan_tier).first()
    if not plan:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan not found.")

    sub = user.subscription
    if not sub:
        sub = UserSubscription(user_id=user.id)
        db.add(sub)

    current_plan_tier = sub.plan.tier if sub and sub.plan else "free"
    current_paid = current_plan_tier != "free" and sub.status in {"active", "trial", "past_due"}
    requested_status = payload.status or ("active" if payload.plan_tier != "free" else "active")
    downgrading = payload.plan_tier == "free" or requested_status == "canceled"

    if current_paid and downgrading and not payload.confirm_downgrade:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Confirmation required to downgrade or cancel a paid subscription.",
        )

    sub.plan_id = plan.id
    sub.status = requested_status
    if payload.cancel_at_period_end is not None:
        sub.cancel_at_period_end = payload.cancel_at_period_end

    if downgrading and payload.confirm_downgrade:
        sub.stripe_customer_id = None
        sub.stripe_subscription_id = None
        sub.cancel_at_period_end = False
        sub.current_period_end = datetime.utcnow()

    if payload.current_period_end:
        try:
            parsed = datetime.fromisoformat(payload.current_period_end.replace("Z", "+00:00"))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid current_period_end. Use ISO-8601 format.",
            ) from exc
        sub.current_period_end = parsed

    sub.current_period_start = sub.current_period_start or datetime.utcnow()
    db.commit()
    db.refresh(sub)

    return {
        "success": True,
        "subscription": {
            "status": sub.status,
            "plan_tier": plan.tier,
            "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
            "cancel_at_period_end": sub.cancel_at_period_end,
        },
    }


@router.get("/leads")
def list_leads(
    owner: Optional[User] = Depends(require_owner),
    db: Session = Depends(get_db),
    limit: int = 200,
    q: Optional[str] = None,
    segment: Optional[str] = None,
):
    limit = max(1, min(int(limit or 200), 1000))
    query = db.query(Lead)
    if q:
        qn = q.strip().lower()
        if qn:
            query = query.filter(Lead.email.ilike(f"%{qn}%"))
    if segment:
        seg = segment.strip().lower()
        if seg:
            query = query.filter(Lead.segment == seg)

    leads = query.order_by(Lead.created_at.desc()).limit(limit).all()
    return {
        "leads": [
            {
                "id": l.id,
                "email": l.email,
                "segment": l.segment,
                "platform": l.platform,
                "volume": l.volume,
                "pain": l.pain,
                "url": l.url,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in leads
        ]
    }


@router.get("/kpis")
def owner_kpis(
    owner: Optional[User] = Depends(require_owner),
    db: Session = Depends(get_db),
):
    """
    Minimal KPI snapshot for launch monitoring.

    Notes:
    - Derived from DB tables (users, subscriptions, leads).
    - If you need Stripe-reconciled MRR, we will layer that on via invoice/subscription sync.
    """
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_start = now - timedelta(days=7)

    leads_today = db.query(Lead).filter(Lead.created_at >= today_start).count()
    leads_7d = db.query(Lead).filter(Lead.created_at >= week_start).count()

    signups_today = db.query(User).filter(User.created_at >= today_start).count()
    signups_7d = db.query(User).filter(User.created_at >= week_start).count()

    # Trial and paid states are modeled on UserSubscription.status and plan tier.
    active_trials = (
        db.query(UserSubscription)
        .outerjoin(SubscriptionPlan)
        .filter(UserSubscription.status == "trial")
        .filter(SubscriptionPlan.tier.in_(["practitioner", "studio"]))
        .count()
    )
    active_paid = (
        db.query(UserSubscription)
        .outerjoin(SubscriptionPlan)
        .filter(UserSubscription.status == "active")
        .filter(SubscriptionPlan.tier.in_(["practitioner", "studio"]))
        .count()
    )

    return {
        "now": now.isoformat(),
        "leads": {"today": leads_today, "last_7d": leads_7d},
        "signups": {"today": signups_today, "last_7d": signups_7d},
        "subscriptions": {"active_trials": active_trials, "active_paid": active_paid},
    }


@router.get("/outreach-targets")
def list_outreach_targets(
    owner: Optional[User] = Depends(require_owner),
    db: Session = Depends(get_db),
    limit: int = 500,
    q: Optional[str] = None,
    segment: Optional[str] = None,
    platform_primary: Optional[str] = None,
):
    limit = max(1, min(int(limit or 500), 2000))
    query = db.query(OutreachTarget)

    if q:
        qn = q.strip().lower()
        if qn:
            query = query.filter(OutreachTarget.name.ilike(f"%{qn}%"))

    if segment:
        seg = segment.strip().lower()
        if seg:
            query = query.filter(OutreachTarget.segment == seg)

    if platform_primary:
        pp = platform_primary.strip().lower()
        if pp:
            query = query.filter(OutreachTarget.platform_primary == pp)

    targets = query.order_by(OutreachTarget.name.asc()).limit(limit).all()
    return {
        "targets": [
            {
                "id": t.id,
                "name": t.name,
                "segment": t.segment,
                "platform_primary": t.platform_primary,
                "primary_contact": t.primary_contact,
                "secondary_contact": t.secondary_contact,
                "notes": t.notes,
                "source": t.source,
                "last_verified": t.last_verified,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in targets
        ]
    }
