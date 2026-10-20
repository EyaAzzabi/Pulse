import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_membership
from app.db.session import get_db
from app.forecasting.engine import find_shortfall, run_forecast
from app.models.forecast import ForecastPoint, ForecastRun
from app.models.user import User
from app.schemas.forecast import ForecastPointOut, ForecastRunOut, ForecastRunRequest
from app.services.financial_data import load_financial_inputs

router = APIRouter(prefix="/forecast", tags=["forecast"])


def _to_out(run: ForecastRun) -> ForecastRunOut:
    points = [ForecastPointOut.model_validate(p, from_attributes=True) for p in run.points]
    shortfall = next((p.date for p in run.points if p.projected_cash < 0), None)
    return ForecastRunOut(
        id=run.id,
        created_at=run.created_at,
        horizon_days=run.horizon_days,
        method=run.method,
        starting_cash=run.starting_cash,
        shortfall_date=shortfall,
        points=points,
    )


@router.post("/run", response_model=ForecastRunOut, status_code=status.HTTP_201_CREATED)
def run_forecast_endpoint(
    organization_id: str = Query(...),
    payload: ForecastRunRequest = ForecastRunRequest(),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    as_of = date.today()
    starting_cash, transactions, invoices, recurring = load_financial_inputs(db, organization_id)
    points = run_forecast(starting_cash, transactions, invoices, recurring, as_of, payload.horizon_days)

    run = ForecastRun(
        organization_id=organization_id,
        horizon_days=payload.horizon_days,
        starting_cash=starting_cash,
        assumptions_json=json.dumps({"method": "deterministic_baseline", "as_of": as_of.isoformat()}),
    )
    db.add(run)
    db.flush()
    for p in points:
        db.add(
            ForecastPoint(
                forecast_run_id=run.id,
                date=p.date,
                projected_cash=p.projected_cash,
                known_component=p.known_component,
                uncertain_component=p.uncertain_component,
                confidence=p.confidence,
            )
        )
    db.commit()
    db.refresh(run)
    return _to_out(run)


@router.get("/latest", response_model=ForecastRunOut)
def latest_forecast(
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    run = (
        db.query(ForecastRun)
        .filter(ForecastRun.organization_id == organization_id)
        .order_by(ForecastRun.created_at.desc())
        .first()
    )
    if not run:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No forecast has been run yet")
    return _to_out(run)
