"""Creates (or resets) the Northstar Studio organization with six months of
transactions, invoices and recurring obligations.

Usage:
    python scripts/seed_demo.py

The login password is randomly generated unless DEMO_USER_PASSWORD is set in
the environment. Credentials are printed once and never hardcoded.
"""
import os
import secrets
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.conversation import AuditLog, ChatMessage, Conversation, Notification
from app.models.financial import Invoice, RecurringObligation, Transaction
from app.models.forecast import ForecastPoint, ForecastRun
from app.models.simulation import ActionProposal, Recommendation, SimulationResult, SimulationScenario
from app.models.organization import BusinessProfile, OnboardingProgress, Organization
from app.models.user import Membership, User
from app.services.sample_data import load_sample_data
from app import models  # noqa: F401

DEMO_ORG_NAME = "Northstar Studio"
DEMO_EMAIL = "owner@northstarstudio.demo"


def reset_demo_org(db) -> None:
    org = db.query(Organization).filter(Organization.name == DEMO_ORG_NAME, Organization.is_demo == True).first()  # noqa: E712
    if not org:
        return
    org_id = org.id
    run_ids = [r.id for r in db.query(ForecastRun.id).filter(ForecastRun.organization_id == org_id)]
    if run_ids:
        db.query(ForecastPoint).filter(ForecastPoint.forecast_run_id.in_(run_ids)).delete(synchronize_session=False)
    scenario_ids = [s.id for s in db.query(SimulationScenario.id).filter(SimulationScenario.organization_id == org_id)]
    if scenario_ids:
        db.query(SimulationResult).filter(SimulationResult.scenario_id.in_(scenario_ids)).delete(synchronize_session=False)
    conversation_ids = [c.id for c in db.query(Conversation.id).filter(Conversation.organization_id == org_id)]
    if conversation_ids:
        db.query(ChatMessage).filter(ChatMessage.conversation_id.in_(conversation_ids)).delete(synchronize_session=False)
    for model in (ForecastRun, SimulationScenario, Conversation, Notification, AuditLog, ActionProposal, Recommendation):
        db.query(model).filter(model.organization_id == org_id).delete(synchronize_session=False)
    db.query(Transaction).filter(Transaction.organization_id == org_id).delete()
    db.query(Invoice).filter(Invoice.organization_id == org_id).delete()
    db.query(RecurringObligation).filter(RecurringObligation.organization_id == org_id).delete()
    db.query(BusinessProfile).filter(BusinessProfile.organization_id == org_id).delete()
    db.query(OnboardingProgress).filter(OnboardingProgress.organization_id == org_id).delete()
    db.query(Membership).filter(Membership.organization_id == org_id).delete()
    db.delete(org)
    db.commit()


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        reset_demo_org(db)

        password = os.environ.get("DEMO_USER_PASSWORD") or secrets.token_urlsafe(9)
        user = db.query(User).filter(User.email == DEMO_EMAIL).first()
        if not user:
            user = User(
                email=DEMO_EMAIL,
                password_hash=hash_password(password),
                full_name="Alex Morgan",
                default_currency="EUR",
            )
            db.add(user)
            db.flush()
        else:
            user.password_hash = hash_password(password)

        org = Organization(
            name=DEMO_ORG_NAME,
            industry="ecommerce",
            country="France",
            currency="EUR",
            company_size="11-50",
            timezone="Europe/Paris",
            is_demo=True,
        )
        db.add(org)
        db.flush()

        db.add(Membership(user_id=user.id, organization_id=org.id, role="OWNER"))
        db.add(
            OnboardingProgress(
                organization_id=org.id,
                current_step=8,
                completed=True,
                data_json='{"persona": "owner"}',
            )
        )
        db.commit()

        load_sample_data(db, org.id, date.today())

        print("Northstar Studio seeded successfully.")
        print(f"  Organization: {DEMO_ORG_NAME} ({org.id})")
        print(f"  Login email:  {DEMO_EMAIL}")
        print(f"  Password:     {password}")
        print("  (Development-only account. Do not reuse this password elsewhere.)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
