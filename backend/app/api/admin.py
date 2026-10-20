from datetime import datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, text
from sqlalchemy.orm import Session, joinedload

from app.api.deps import require_admin
from app.core.config import get_settings
from app.db.session import get_db
from app.models.admin import AccountReview
from app.models.organization import OnboardingProgress, Organization
from app.models.user import Membership, User
from app.services.email import smtp_configured

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])
AccountStatus = Literal["PENDING", "APPROVED", "REJECTED", "SUSPENDED"]


class ReviewRequest(BaseModel):
    status: AccountStatus
    expected_status: AccountStatus
    reason: str = Field(default="", max_length=1000)


def user_out(user):
    return {
        "id": user.id, "email": user.email, "full_name": user.full_name,
        "is_admin": user.is_admin, "is_active": user.is_active,
        "account_status": user.account_status, "review_reason": user.review_reason,
        "created_at": user.created_at,
        "email_verified": user.email_verified,
        "waiting_hours": round(max(0, (datetime.utcnow() - user.updated_at).total_seconds() / 3600), 1) if user.account_status == "PENDING" else None,
        "prechecks": [
            {"label": "Email verified by one-time code", "passed": user.email_verified},
            {"label": "Account holder name provided", "passed": bool(user.full_name.strip())},
            {"label": "Organization linked to account", "passed": bool(user.memberships)},
        ],
        "organizations": [{"id": m.organization_id, "name": m.organization.name, "role": m.role}
                          for m in user.memberships if m.organization],
    }


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    counts = dict(db.query(User.account_status, func.count(User.id)).filter(User.is_admin.is_(False)).group_by(User.account_status).all())
    today = datetime.utcnow().date()
    start = datetime.combine(today - timedelta(days=13), datetime.min.time())
    rows = db.query(func.date(User.created_at), func.count(User.id)).filter(User.created_at >= start, User.is_admin.is_(False)).group_by(func.date(User.created_at)).all()
    by_day = {str(day): count for day, count in rows}
    return {
        "total_users": sum(counts.values()), "counts": {s: counts.get(s, 0) for s in ("PENDING", "APPROVED", "REJECTED", "SUSPENDED")},
        "organizations": db.query(Organization).count(),
        "completed_onboarding": db.query(OnboardingProgress).filter(OnboardingProgress.completed.is_(True)).count(),
        "reviews_today": db.query(AccountReview).filter(AccountReview.created_at >= datetime.combine(today, datetime.min.time())).count(),
        "registrations": [{"date": str(start.date() + timedelta(days=i)), "count": by_day.get(str(start.date() + timedelta(days=i)), 0)} for i in range(14)],
    }


@router.get("/system")
def system(db: Session = Depends(get_db)):
    settings = get_settings()
    n8n_email = bool(settings.n8n_otp_webhook_url and settings.n8n_webhook_secret)
    email_ready = n8n_email or smtp_configured()
    try:
        db.execute(text("SELECT 1"))
        database_ok = True
    except Exception:
        db.rollback()
        database_ok = False
    return {
        "database": {"available": database_ok, "engine": db.get_bind().dialect.name},
        "llm": {"configured": settings.llm_provider != "none" and bool(settings.llm_api_key), "provider": settings.llm_provider, "model": settings.llm_model if settings.llm_provider != "none" else None},
        "email": {"configured": email_ready, "mode": "n8n" if n8n_email else "smtp" if smtp_configured() else "server_log" if settings.otp_allow_server_log and settings.environment.lower() in {"development", "test"} else "unconfigured"},
        "workflows": {"configured": bool(settings.n8n_webhook_url)},
        "engine": {"mode": "deterministic", "human_approval": True},
    }


@router.get("/users")
def users(q: str = Query(default="", max_length=255), account_status: AccountStatus | None = None,
          page: int = Query(default=1, ge=1), page_size: int = Query(default=10, ge=1, le=100), db: Session = Depends(get_db)):
    query = db.query(User).options(joinedload(User.memberships).joinedload(Membership.organization)).filter(User.is_admin.is_(False))
    if q.strip():
        term = q.strip().lower()
        query = query.filter(or_(func.lower(User.full_name).contains(term, autoescape=True), func.lower(User.email).contains(term, autoescape=True)))
    if account_status:
        query = query.filter(User.account_status == account_status)
    total = query.count()
    rows = query.order_by(User.created_at.desc(), User.id).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [user_out(u) for u in rows], "total": total, "page": page, "page_size": page_size}


@router.post("/users/{user_id}/review")
def review(user_id: str, payload: ReviewRequest, actor: User = Depends(require_admin), db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404, "Account not found")
    if target.is_admin or target.id == actor.id:
        raise HTTPException(403, "Administrator accounts cannot be reviewed here")
    transitions = {"PENDING": {"APPROVED", "REJECTED"}, "APPROVED": {"SUSPENDED"}, "SUSPENDED": {"APPROVED"}, "REJECTED": {"PENDING"}}
    if payload.status not in transitions.get(payload.expected_status, set()):
        raise HTTPException(409, "Unsupported account status transition")
    reason = payload.reason.strip()
    if payload.status in {"REJECTED", "SUSPENDED"} and not reason:
        raise HTTPException(422, "A reason is required for rejection or suspension")
    changed = db.query(User).filter(User.id == user_id, User.account_status == payload.expected_status, User.is_admin.is_(False)).update(
        {User.account_status: payload.status, User.review_reason: reason}, synchronize_session=False)
    if not changed:
        db.rollback()
        raise HTTPException(409, "Account changed since your last review. Refresh and try again.")
    db.add(AccountReview(actor_user_id=actor.id, target_user_id=target.id, previous_status=payload.expected_status, new_status=payload.status, reason=reason))
    db.commit()
    db.refresh(target)
    return user_out(target)


@router.get("/organizations")
def organizations(q: str = Query(default="", max_length=255), page: int = Query(default=1, ge=1),
                  page_size: int = Query(default=10, ge=1, le=100), db: Session = Depends(get_db)):
    query = db.query(Organization).options(joinedload(Organization.memberships).joinedload(Membership.user))
    if q.strip():
        query = query.filter(func.lower(Organization.name).contains(q.strip().lower(), autoescape=True))
    total = query.count()
    rows = query.order_by(Organization.created_at.desc(), Organization.id).offset((page - 1) * page_size).limit(page_size).all()
    progress = {p.organization_id: p.completed for p in db.query(OnboardingProgress).filter(OnboardingProgress.organization_id.in_([o.id for o in rows])).all()}
    return {"total": total, "items": [{"id": o.id, "name": o.name, "industry": o.industry, "country": o.country,
        "currency": o.currency, "created_at": o.created_at, "is_demo": o.is_demo, "member_count": len(o.memberships),
        "onboarding_completed": progress.get(o.id, False),
        "owners": [{"full_name": m.user.full_name, "email": m.user.email, "account_status": m.user.account_status} for m in o.memberships if m.role == "OWNER" and m.user],
    } for o in rows]}


@router.get("/audit")
def audit(page: int = Query(default=1, ge=1), page_size: int = Query(default=10, ge=1, le=100), db: Session = Depends(get_db)):
    query = db.query(AccountReview)
    total = query.count()
    rows = query.order_by(AccountReview.created_at.desc(), AccountReview.id).offset((page - 1) * page_size).limit(page_size).all()
    ids = {r.actor_user_id for r in rows} | {r.target_user_id for r in rows}
    people = {u.id: u for u in db.query(User).filter(User.id.in_(ids)).all()}
    return {"total": total, "items": [{"id": r.id, "created_at": r.created_at, "actor": people[r.actor_user_id].full_name,
        "target": people[r.target_user_id].full_name, "target_email": people[r.target_user_id].email,
        "previous_status": r.previous_status, "new_status": r.new_status, "reason": r.reason} for r in rows]}
