from tests.conftest import TEST_OTP, register_and_login


def _register(client, email, code=TEST_OTP, password="StrongPass123"):
    return client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Test User",
            "organization_name": "Test Co",
            "otp_code": code,
        },
    )


def test_register_with_valid_code_and_login(client):
    assert client.post("/auth/request-otp", json={"email": "alice@example.com"}).json()["delivery"] == "server_log"
    assert _register(client, "alice@example.com").status_code == 201

    login = client.post("/auth/login", json={"email": "alice@example.com", "password": "StrongPass123"})
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_register_rejects_wrong_code(client):
    client.post("/auth/request-otp", json={"email": "wrong-code@example.com"})
    resp = _register(client, "wrong-code@example.com", code="000000")
    assert resp.status_code == 400
    assert "attempt" in resp.json()["detail"]


def test_register_without_requesting_code_fails(client):
    assert _register(client, "no-code@example.com").status_code == 400


def test_register_requires_code_field(client):
    resp = client.post(
        "/auth/register",
        json={"email": "missing@example.com", "password": "StrongPass123", "full_name": "X", "organization_name": "Y"},
    )
    assert resp.status_code == 422


def test_code_is_single_use(client):
    client.post("/auth/request-otp", json={"email": "reuse@example.com"})
    assert _register(client, "reuse@example.com").status_code == 201
    # The account now exists, so a second registration is rejected outright.
    assert _register(client, "reuse@example.com").status_code == 409


def test_too_many_wrong_attempts_invalidates_code(client):
    client.post("/auth/request-otp", json={"email": "brute@example.com"})
    for _ in range(5):
        _register(client, "brute@example.com", code="999999")
    assert _register(client, "brute@example.com").status_code == 400


def test_resend_has_cooldown(client):
    assert client.post("/auth/request-otp", json={"email": "cooldown@example.com"}).status_code == 200
    assert client.post("/auth/request-otp", json={"email": "cooldown@example.com"}).status_code == 429


def test_request_otp_rejects_existing_account(client):
    register_and_login(client, "taken@example.com")
    assert client.post("/auth/request-otp", json={"email": "taken@example.com"}).status_code == 409


def test_login_rejects_wrong_password(client):
    register_and_login(client, "bob@example.com")
    resp = client.post("/auth/login", json={"email": "bob@example.com", "password": "WrongPassword"})
    assert resp.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/auth/me").status_code == 401


def test_me_returns_memberships(client):
    headers, org_id = register_and_login(client, "dave@example.com")
    body = client.get("/auth/me", headers=headers).json()
    assert body["memberships"][0]["role"] == "OWNER"
    assert body["memberships"][0]["organization_id"] == org_id
