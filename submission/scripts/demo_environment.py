"""Reproducible synthetic submission workspace. No live database or mail is used."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
from datetime import date

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / ".runtime/submission"
RUNTIME.mkdir(parents=True, exist_ok=True)
STATE = RUNTIME / "private-state.json"
if not STATE.exists():
    STATE.write_text(json.dumps({"jwt_secret": secrets.token_urlsafe(48), "password": secrets.token_urlsafe(22)}))
state = json.loads(STATE.read_text())
os.environ.update({"DATABASE_URL": "sqlite:///" + (RUNTIME / "demo.db").as_posix(), "JWT_SECRET": state["jwt_secret"],
    "ENVIRONMENT": "development", "CORS_ORIGINS": "http://localhost:5175,http://127.0.0.1:5175", "LLM_PROVIDER": "none", "LLM_API_KEY": "",
    "SMTP_HOST": "", "SMTP_PASSWORD": "", "N8N_WEBHOOK_URL": "", "N8N_OTP_WEBHOOK_URL": "", "OTP_ALLOW_SERVER_LOG": "false"})
sys.path.insert(0, str(ROOT / "backend"))


def seed():
    from app.db.session import Base, engine, SessionLocal
    from app.models.user import User, Membership
    from app.models.organization import Organization, OnboardingProgress
    from app.core.security import hash_password
    from app.services.sample_data import load_sample_data
    from app import models
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        owner = db.query(User).filter_by(email="owner@northstar.example").first()
        if not owner:
            owner = User(email="owner@northstar.example", full_name="Alex Morgan", password_hash=hash_password(state["password"]), account_status="APPROVED", email_verified=True)
            org = Organization(name="Northstar Studio / Synthetic Demo", is_demo=True, industry="retail", country="Tunisia")
            db.add_all([owner, org]); db.flush()
            db.add(Membership(user_id=owner.id, organization_id=org.id, role="OWNER"))
            db.add(OnboardingProgress(organization_id=org.id, completed=False, current_step=3))
            db.commit(); load_sample_data(db, org.id, date.today())
        membership = db.query(Membership).filter_by(user_id=owner.id).first()
        state.update({"user_id": owner.id, "organization_id": membership.organization_id, "email": owner.email})
        STATE.write_text(json.dumps(state))
    print("Synthetic submission workspace prepared; credentials retained only under ignored .runtime/.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        raise SystemExit(subprocess.call([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8002"], cwd=ROOT / "backend", env=os.environ))
    seed()
