"""Turns computed risks into notifications. Runs whenever the summary or a
forecast is computed; de-duplication keeps repeated runs from repeating alerts."""
from datetime import date

from sqlalchemy.orm import Session

from app.financial.engine import compute_summary
from app.forecasting.engine import find_shortfall, run_forecast
from app.models.organization import Organization
from app.services.notifications import notify


def evaluate_alerts(db: Session, organization_id: str, starting_cash, transactions, invoices, recurring) -> None:
    today = date.today()
    org = db.get(Organization, organization_id)
    currency = org.currency if org else "EUR"

    points = run_forecast(starting_cash, transactions, invoices, recurring, today, 60)
    shortfall = find_shortfall(points)
    if shortfall:
        days = (shortfall.date - today).days
        notify(
            db,
            organization_id,
            category="liquidity_risk",
            severity="critical",
            title=f"Cash shortfall projected for {shortfall.date.strftime('%d %b %Y')}",
            body=(
                f"The 60-day forecast drops below zero in {days} days "
                f"(projected {currency} {shortfall.projected_cash:,.2f}). Open the simulator to test a rescue plan."
            ),
            link="/simulator",
            dedupe=True,
        )

    summary = compute_summary(starting_cash, transactions, invoices, recurring, today)
    if summary.overdue_receivables_count:
        n = summary.overdue_receivables_count
        notify(
            db,
            organization_id,
            category="overdue_invoices",
            severity="warning",
            title=f"{n} customer invoice{'s are' if n > 1 else ' is'} overdue",
            body=f"{currency} {summary.overdue_receivables_amount:,.2f} is waiting to be collected.",
            link="/invoices",
            dedupe=True,
        )
    db.commit()
