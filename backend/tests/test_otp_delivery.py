import httpx

from app.core.config import get_settings


class _Resp:
    def __init__(self, status_code: int):
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=None, response=None)


def _use_n8n(monkeypatch, status_code: int, calls: list):
    settings = get_settings()
    monkeypatch.setattr(settings, "n8n_otp_webhook_url", "https://n8n.example/webhook/pulse/verification-code")
    monkeypatch.setattr(settings, "n8n_webhook_secret", "shared-secret")

    def fake_post(url, json, headers, timeout):
        calls.append({"url": url, "json": json, "headers": headers})
        return _Resp(status_code)

    monkeypatch.setattr("app.services.otp.httpx.post", fake_post)


def test_code_sent_through_n8n(client, monkeypatch):
    calls: list = []
    _use_n8n(monkeypatch, 200, calls)

    resp = client.post("/auth/request-otp", json={"email": "n8n-ok@example.com"})

    assert resp.json()["delivery"] == "email"
    assert calls[0]["json"]["email"] == "n8n-ok@example.com"
    assert calls[0]["json"]["code"] == "123456"
    assert calls[0]["headers"]["X-Webhook-Secret"] == "shared-secret"


def test_n8n_failure_is_reported_not_hidden(client, monkeypatch):
    _use_n8n(monkeypatch, 500, [])
    resp = client.post("/auth/request-otp", json={"email": "n8n-down@example.com"})
    assert resp.status_code == 502
