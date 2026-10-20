import json
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_membership, require_role
from app.db.session import get_db
from app.financial.engine import net_cash_flow
from app.models.financial import Transaction
from app.models.organization import BusinessProfile, OnboardingProgress
from app.models.user import User
from app.services.sample_data import SAMPLE_PROFILE, load_sample_data

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


class OnboardingUpdate(BaseModel):
    current_step: int
    data: dict = {}


class FinalizeRequest(BaseModel):
    current_cash_balance: Decimal | None = Field(default=None, ge=0)


@router.post("/sample-data")
def load_sample(
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(organization_id, user, db, "FINANCE_MANAGER")
    has_transactions = (
        db.query(Transaction.id).filter(Transaction.organization_id == organization_id).first() is not None
    )
    if has_transactions:
        raise HTTPException(status.HTTP_409_CONFLICT, "This organization already has transactions")
    load_sample_data(db, organization_id, date.today())
    return {"loaded": True, "profile": {k: str(v) for k, v in SAMPLE_PROFILE.items()}}


@router.post("/finalize")
def finalize_cash_position(
    payload: FinalizeRequest,
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stores the user's stated *current* cash as the engine's opening balance.

    The engine computes today's cash as opening balance + every transaction up
    to today, so when transactions already exist (CSV import) the opening
    balance is the stated cash minus their net, otherwise imported history
    would be counted twice. With no stated cash (sample data), the existing
    opening balance is kept."""
    require_role(organization_id, user, db, "FINANCE_MANAGER")
    profile = db.query(BusinessProfile).filter(BusinessProfile.organization_id == organization_id).first()
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Business profile not found")

    if payload.current_cash_balance is not None:
        transactions = db.query(Transaction).filter(Transaction.organization_id == organization_id).all()
        today = date.today()
        _, _, net = net_cash_flow(transactions, date.min, today)
        profile.current_cash_balance = payload.current_cash_balance - net
        db.commit()

    return {"opening_balance": str(profile.current_cash_balance)}


@router.get("")
def get_onboarding(
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    progress = db.query(OnboardingProgress).filter(OnboardingProgress.organization_id == organization_id).first()
    if not progress:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Onboarding record not found")
    return {
        "current_step": progress.current_step,
        "completed": progress.completed,
        "data": json.loads(progress.data_json),
    }


@router.put("")
def update_onboarding(
    payload: OnboardingUpdate,
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    progress = db.query(OnboardingProgress).filter(OnboardingProgress.organization_id == organization_id).first()
    if not progress:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Onboarding record not found")
    merged = json.loads(progress.data_json)
    merged.update(payload.data)
    progress.data_json = json.dumps(merged)
    progress.current_step = payload.current_step
    db.commit()
    return {"current_step": progress.current_step, "completed": progress.completed, "data": merged}


@router.post("/complete")
def complete_onboarding(
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    progress = db.query(OnboardingProgress).filter(OnboardingProgress.organization_id == organization_id).first()
    if not progress:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Onboarding record not found")
    progress.completed = True
    db.commit()
    return {"completed": True}
