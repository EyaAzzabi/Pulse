import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ["DATABASE_URL"] = "sqlite:///./test_pulse.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["SMTP_HOST"] = ""
os.environ["N8N_OTP_WEBHOOK_URL"] = ""
os.environ["N8N_WEBHOOK_URL"] = ""
os.environ["LLM_PROVIDER"] = "none"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base, get_db
from app.main import app
from app import models  # noqa: F401

TEST_DB_PATH = Path(__file__).resolve().parent.parent / "test_pulse.db"

engine = create_engine("sqlite:///./test_pulse.db", connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


TEST_OTP = "123456"


@pytest.fixture(autouse=True)
def fixed_otp(monkeypatch):
    monkeypatch.setattr("app.services.otp.generate_code", lambda: TEST_OTP)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


def register_and_login(client, email: str, password: str = "StrongPass123", org_name: str = "Test Org"):
    otp = client.post("/auth/request-otp", json={"email": email})
    assert otp.status_code == 200, otp.text
    resp = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Test User",
            "organization_name": org_name,
            "otp_code": TEST_OTP,
        },
    )
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    # Business tests exercise approved accounts; pending access is tested in test_admin.
    from app.models.user import User
    with TestSessionLocal() as session:
        user = session.query(User).filter(User.email == email.lower()).one()
        user.account_status = "APPROVED"
        session.commit()
    headers = {"Authorization": f"Bearer {token}"}
    me = client.get("/auth/me", headers=headers).json()
    org_id = me["memberships"][0]["organization_id"]
    return headers, org_id
