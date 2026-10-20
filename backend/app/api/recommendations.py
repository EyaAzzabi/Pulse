from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_membership
from app.db.session import get_db
from app.models.user import User
from app.services.financial_data import load_financial_inputs
from app.services.rescue_plans import generate_rescue_plans

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("")
def list_recommendations(
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    starting_cash, transactions, invoices, recurring = load_financial_inputs(db, organization_id)
    plans = generate_rescue_plans(starting_cash, transactions, invoices, recurring, date.today())
    return [
        {
            "key": p.key,
            "title": p.title,
            "rationale": p.rationale,
            "expected_impact": str(p.estimated_liquidity_benefit),
            "feasibility": p.feasibility,
            "cost": p.cost,
            "residual_risk": p.residual_risk,
            "requires_approval": True,
        }
        for p in plans
    ]
