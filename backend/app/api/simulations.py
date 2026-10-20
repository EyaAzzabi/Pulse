import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_membership
from app.db.session import get_db
from app.models.simulation import SimulationResult, SimulationScenario
from app.models.user import User
from app.schemas.simulation import SimulationCreateRequest, SimulationListItemOut, SimulationResultOut
from app.services.financial_data import load_financial_inputs
from app.simulations.engine import ScenarioAssumptions, run_simulation

router = APIRouter(prefix="/simulations", tags=["simulations"])


def _points_json(points) -> str:
    return json.dumps(
        [
            {
                "date": p.date.isoformat(),
                "projected_cash": str(p.projected_cash),
                "known_component": str(p.known_component),
                "uncertain_component": str(p.uncertain_component),
                "confidence": p.confidence,
            }
            for p in points
        ]
    )


def _points_from_json(raw: str) -> list[dict]:
    return json.loads(raw)


@router.post("", response_model=SimulationResultOut, status_code=status.HTTP_201_CREATED)
def create_simulation(
    payload: SimulationCreateRequest,
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    as_of = date.today()
    starting_cash, transactions, invoices, recurring = load_financial_inputs(db, organization_id)

    assumptions = ScenarioAssumptions(
        customer_payment_delay_days=payload.customer_payment_delay_days,
        supplier_payment_delay_days=payload.supplier_payment_delay_days,
        revenue_change_pct=payload.revenue_change_pct,
        expense_change_pct=payload.expense_change_pct,
        inventory_purchase_amount=payload.inventory_purchase_amount,
        financing_amount=payload.financing_amount,
        financing_monthly_cost=payload.financing_monthly_cost,
        one_time_cash_injection=payload.one_time_cash_injection,
    )
    output = run_simulation(
        starting_cash, transactions, invoices, recurring, as_of, payload.horizon_days, assumptions
    )

    scenario = SimulationScenario(
        organization_id=organization_id,
        created_by_user_id=user.id,
        name=payload.name,
        assumptions_json=json.dumps(payload.model_dump(mode="json")),
    )
    db.add(scenario)
    db.flush()

    result = SimulationResult(
        scenario_id=scenario.id,
        lowest_cash_point=output.lowest_cash_point,
        lowest_cash_date=output.lowest_cash_date.isoformat() if output.lowest_cash_date else "",
        runway_days=output.runway_days,
        days_below_zero=output.days_below_zero,
        impact_vs_baseline_json=json.dumps({"impact": str(output.impact_vs_baseline)}),
        baseline_points_json=_points_json(output.baseline_points),
        simulated_points_json=_points_json(output.simulated_points),
    )
    db.add(result)
    db.commit()

    return SimulationResultOut(
        id=result.id,
        scenario_id=scenario.id,
        name=scenario.name,
        created_at=scenario.created_at,
        assumptions=payload.model_dump(mode="json"),
        lowest_cash_point=output.lowest_cash_point,
        lowest_cash_date=output.lowest_cash_date,
        runway_days=output.runway_days,
        days_below_zero=output.days_below_zero,
        impact_vs_baseline=output.impact_vs_baseline,
        baseline_points=_points_from_json(result.baseline_points_json),
        simulated_points=_points_from_json(result.simulated_points_json),
    )


@router.get("", response_model=list[SimulationListItemOut])
def list_simulations(
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    scenarios = (
        db.query(SimulationScenario)
        .filter(SimulationScenario.organization_id == organization_id)
        .order_by(SimulationScenario.created_at.desc())
        .all()
    )
    out = []
    for s in scenarios:
        if s.result:
            impact = json.loads(s.result.impact_vs_baseline_json).get("impact", "0")
            out.append(
                SimulationListItemOut(
                    id=s.id,
                    name=s.name,
                    created_at=s.created_at,
                    lowest_cash_point=s.result.lowest_cash_point,
                    impact_vs_baseline=impact,
                )
            )
    return out


@router.get("/{scenario_id}", response_model=SimulationResultOut)
def get_simulation(
    scenario_id: str,
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    scenario = db.get(SimulationScenario, scenario_id)
    if not scenario or scenario.organization_id != organization_id or not scenario.result:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Simulation not found")
    result = scenario.result
    impact = json.loads(result.impact_vs_baseline_json).get("impact", "0")
    return SimulationResultOut(
        id=result.id,
        scenario_id=scenario.id,
        name=scenario.name,
        created_at=scenario.created_at,
        assumptions=json.loads(scenario.assumptions_json),
        lowest_cash_point=result.lowest_cash_point,
        lowest_cash_date=result.lowest_cash_date or None,
        runway_days=result.runway_days,
        days_below_zero=result.days_below_zero,
        impact_vs_baseline=impact,
        baseline_points=_points_from_json(result.baseline_points_json),
        simulated_points=_points_from_json(result.simulated_points_json),
    )
