from datetime import date, timedelta

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_membership, require_role
from app.db.session import get_db
from app.financial.engine import compute_summary, historical_cash_series
from app.forecasting.engine import run_forecast
from app.models.financial import Transaction
from app.models.organization import Organization
from app.models.user import User
from app.schemas.financial import CashflowPointOut, FinancialSummaryOut, InvoiceOut, TransactionOut
from app.services.csv_import import parse_csv
from app.services.financial_data import load_financial_inputs, refresh_overdue_status

MAX_IMPORT_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

router = APIRouter(tags=["financial"])


@router.get("/financial/summary", response_model=FinancialSummaryOut)
def get_summary(
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    org = db.get(Organization, organization_id)
    as_of = date.today()
    refresh_overdue_status(db, organization_id, as_of)
    starting_cash, transactions, invoices, recurring = load_financial_inputs(db, organization_id)
    summary = compute_summary(starting_cash, transactions, invoices, recurring, as_of)
    return FinancialSummaryOut(currency=org.currency if org else "EUR", **summary.__dict__)


@router.get("/financial/cashflow", response_model=list[CashflowPointOut])
def get_cashflow(
    organization_id: str = Query(...),
    history_days: int = Query(90, ge=0, le=365),
    horizon_days: int = Query(90, ge=0, le=365),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    as_of = date.today()
    starting_cash, transactions, invoices, recurring = load_financial_inputs(db, organization_id)

    points: list[CashflowPointOut] = []
    if history_days:
        history = historical_cash_series(starting_cash, transactions, as_of - timedelta(days=history_days), as_of)
        points.extend(
            CashflowPointOut(date=d, actual_cash=cash, is_forecast=False) for d, cash in history
        )
    if horizon_days:
        forecast = run_forecast(starting_cash, transactions, invoices, recurring, as_of, horizon_days)
        points.extend(
            CashflowPointOut(date=p.date, projected_cash=p.projected_cash, confidence=p.confidence, is_forecast=True)
            for p in forecast
        )
    return points


@router.post("/transactions/import")
async def import_transactions(
    organization_id: str = Query(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(organization_id, user, db, "ACCOUNTANT")

    content = await file.read()
    if len(content) > MAX_IMPORT_SIZE_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File exceeds 5 MB limit")
    if file.filename and not file.filename.lower().endswith(".csv"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only .csv files are supported")

    result = parse_csv(content)

    existing_refs = {
        r[0]
        for r in db.query(Transaction.import_reference)
        .filter(Transaction.organization_id == organization_id)
        .all()
        if r[0]
    }

    imported = 0
    skipped_duplicates = 0
    for row in result.valid_rows:
        if row.import_reference in existing_refs:
            skipped_duplicates += 1
            continue
        db.add(
            Transaction(
                organization_id=organization_id,
                date=row.date,
                amount=row.amount,
                currency="EUR",
                category=row.category,
                direction=row.direction,
                source="csv_import",
                status="posted",
                description=row.description,
                import_reference=row.import_reference,
            )
        )
        existing_refs.add(row.import_reference)
        imported += 1
    db.commit()

    return {
        "imported": imported,
        "skipped_duplicates": skipped_duplicates,
        "errors": [{"row": e.row_number, "reason": e.reason} for e in result.errors],
        "total_rows_in_file": imported + skipped_duplicates + len(result.errors),
    }


@router.get("/transactions", response_model=list[TransactionOut])
def list_transactions(
    organization_id: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    _, transactions, _, _ = load_financial_inputs(db, organization_id)
    ordered = sorted(transactions, key=lambda t: t.date, reverse=True)
    return ordered[skip : skip + limit]


@router.get("/invoices", response_model=list[InvoiceOut])
def list_invoices(
    organization_id: str = Query(...),
    status: str | None = Query(None),
    direction: str | None = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    as_of = date.today()
    refresh_overdue_status(db, organization_id, as_of)
    _, _, invoices, _ = load_financial_inputs(db, organization_id)
    if status:
        invoices = [i for i in invoices if i.status == status]
    if direction:
        invoices = [i for i in invoices if i.direction == direction]
    return sorted(invoices, key=lambda i: i.due_date)
