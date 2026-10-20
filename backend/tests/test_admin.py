import pytest

from app.core.security import create_access_token, hash_password
from app.models.admin import AccountReview
from app.models.user import User
from tests.conftest import TEST_OTP, register_and_login


@pytest.fixture
def admin_headers(db_session):
    user = User(email="platform-admin@example.com", full_name="Platform Admin", password_hash=hash_password("AdminPassword123"), is_admin=True)
    db_session.add(user)
    db_session.commit()
    yield {"Authorization": f"Bearer {create_access_token(user.id)}"}
    db_session.query(AccountReview).filter(AccountReview.actor_user_id == user.id).delete()
    db_session.delete(user)
    db_session.commit()


def pending_account(client, email):
    assert client.post("/auth/request-otp", json={"email": email}).status_code == 200
    registration = client.post("/auth/register", json={"email": email, "password": "StrongPass123", "full_name": "Pending User", "organization_name": "Pending Co", "otp_code": TEST_OTP, "is_admin": True, "account_status": "APPROVED"})
    assert registration.status_code == 201
    headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}
    me = client.get("/auth/me", headers=headers).json()
    return headers, me["user"]["id"], me["memberships"][0]["organization_id"]


def test_new_account_is_pending_and_cannot_self_promote(client):
    headers, _, org_id = pending_account(client, "pending-access@example.com")
    me = client.get("/auth/me", headers=headers).json()
    assert me["user"]["account_status"] == "PENDING"
    assert me["user"]["is_admin"] is False
    for path in ["/admin/overview", "/organizations", f"/financial/summary?organization_id={org_id}", f"/onboarding?organization_id={org_id}"]:
        assert client.get(path, headers=headers).status_code == 403, path


@pytest.mark.parametrize("path", ["/admin/overview", "/admin/users", "/admin/organizations", "/admin/audit", "/admin/system"])
def test_admin_endpoints_require_platform_admin(client, path):
    assert client.get(path).status_code == 401
    headers, _ = register_and_login(client, f"ordinary-{path.rsplit('/', 1)[1]}@example.com")
    assert client.get(path, headers=headers).status_code == 403


def test_approval_and_suspension_take_effect_on_existing_token(client, admin_headers):
    headers, user_id, org_id = pending_account(client, "review-flow@example.com")
    approved = client.post(f"/admin/users/{user_id}/review", headers=admin_headers, json={"status": "APPROVED", "expected_status": "PENDING", "reason": "Verified business"})
    assert approved.status_code == 200, approved.text
    assert "password_hash" not in approved.json()
    assert client.get(f"/organizations/{org_id}", headers=headers).status_code == 200
    assert client.post(f"/admin/users/{user_id}/review", headers=admin_headers, json={"status": "SUSPENDED", "expected_status": "APPROVED"}).status_code == 422
    assert client.post(f"/admin/users/{user_id}/review", headers=admin_headers, json={"status": "SUSPENDED", "expected_status": "APPROVED", "reason": "Further verification required"}).status_code == 200
    assert client.get(f"/organizations/{org_id}", headers=headers).status_code == 403
    assert client.get("/auth/me", headers=headers).json()["user"]["review_reason"] == "Further verification required"
    assert client.post(f"/admin/users/{user_id}/review", headers=admin_headers, json={"status": "APPROVED", "expected_status": "SUSPENDED"}).status_code == 200
    assert client.get(f"/organizations/{org_id}", headers=headers).status_code == 200
    events = client.get("/admin/audit", headers=admin_headers).json()["items"]
    assert [e["new_status"] for e in events if e["target_email"] == "review-flow@example.com"] == ["APPROVED", "SUSPENDED", "APPROVED"]


def test_reject_reopen_and_conflicting_reviews(client, admin_headers):
    headers, user_id, _ = pending_account(client, "reject-flow@example.com")
    route = f"/admin/users/{user_id}/review"
    assert client.post(route, headers=headers, json={"status": "APPROVED", "expected_status": "PENDING"}).status_code == 403
    assert client.post(route, headers=admin_headers, json={"status": "REJECTED", "expected_status": "PENDING", "reason": "   "}).status_code == 422
    assert client.post(route, headers=admin_headers, json={"status": "REJECTED", "expected_status": "PENDING", "reason": "Company information incomplete"}).status_code == 200
    assert client.post(route, headers=admin_headers, json={"status": "APPROVED", "expected_status": "PENDING"}).status_code == 409
    assert client.post(route, headers=admin_headers, json={"status": "APPROVED", "expected_status": "REJECTED"}).status_code == 409
    assert client.post(route, headers=admin_headers, json={"status": "PENDING", "expected_status": "REJECTED", "reason": "New review"}).status_code == 200


def test_admin_cannot_suspend_admin_or_access_financial_data_by_membership_bypass(client, admin_headers):
    admin_id = client.get("/auth/me", headers=admin_headers).json()["user"]["id"]
    assert client.post(f"/admin/users/{admin_id}/review", headers=admin_headers, json={"status": "SUSPENDED", "expected_status": "APPROVED", "reason": "Test"}).status_code == 403
    _, org_id = register_and_login(client, "isolated-owner@example.com")
    assert client.get(f"/organizations/{org_id}", headers=admin_headers).status_code == 403


def test_admin_search_pagination_overview_and_system(client, admin_headers):
    pending_account(client, "unique-search@example.com")
    result = client.get("/admin/users?q=unique-search&account_status=PENDING", headers=admin_headers)
    assert result.status_code == 200, result.text
    assert result.json()["total"] == 1
    assert result.json()["items"][0]["email"] == "unique-search@example.com"
    assert "password_hash" not in result.json()["items"][0]
    assert client.get("/admin/users?page=0", headers=admin_headers).status_code == 422
    assert client.get("/admin/users?page_size=101", headers=admin_headers).status_code == 422
    assert client.get("/admin/users?q=%", headers=admin_headers).json()["total"] == 0
    overview = client.get("/admin/overview", headers=admin_headers).json()
    assert len(overview["registrations"]) == 14
    assert overview["total_users"] == sum(overview["counts"].values())
    assert client.get("/admin/organizations?q=Pending", headers=admin_headers).json()["total"] > 0
    system = client.get("/admin/system", headers=admin_headers)
    assert system.status_code == 200
    assert "jwt_secret" not in system.text
    assert "smtp_password" not in system.text
