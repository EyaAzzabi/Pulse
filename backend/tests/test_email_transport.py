import smtplib

import httpx
import pytest

from app.core.config import get_settings
from app.models.otp import EmailOtp
from app.services.email import send_email
from app.services.otp import OtpError, verify_code


def configure_smtp(monkeypatch):
    settings = get_settings()
    for key, value in {"smtp_host": "smtp.example.com", "smtp_port": 587, "smtp_user": "sender@example.com", "smtp_password": "test-password", "smtp_from": "sender@example.com"}.items():
        monkeypatch.setattr(settings, key, value)
    return settings


def test_smtp_tls_submission_and_multipart_email(monkeypatch):
    configure_smtp(monkeypatch)
    calls = []

    class SMTP:
        def __init__(self, host, port, timeout, **kwargs):
            calls.append(("connect", host, port))
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def ehlo(self): calls.append(("ehlo",))
        def starttls(self, context): calls.append(("tls",))
        def login(self, user, password): calls.append(("login", user))
        def send_message(self, msg):
            assert msg["To"] == "recipient@example.com"
            assert msg.get_body(preferencelist=("plain",)).get_content().strip() == "Code 123456"
            assert "123456" in msg.get_body(preferencelist=("html",)).get_content()
            calls.append(("sent",))
            return {}

    monkeypatch.setattr("app.services.email.smtplib.SMTP", SMTP)
    monkeypatch.setattr("app.services.email.smtplib.SMTP_SSL", SMTP)
    send_email("recipient@example.com", "Code", "Code 123456", "<b>123456</b>")
    assert [c[0] for c in calls] == ["connect", "ehlo", "tls", "ehlo", "login", "sent"]
    calls.clear()
    monkeypatch.setattr(get_settings(), "smtp_port", 465)
    send_email("recipient@example.com", "Code", "Code 123456", "<b>123456</b>")
    assert [c[0] for c in calls] == ["connect", "login", "sent"]


def test_n8n_failure_uses_real_smtp_fallback(client, monkeypatch):
    settings = configure_smtp(monkeypatch)
    monkeypatch.setattr(settings, "n8n_otp_webhook_url", "https://n8n.example/webhook/test")
    monkeypatch.setattr(settings, "n8n_webhook_secret", "test-secret")
    monkeypatch.setattr("app.services.otp.httpx.post", lambda *a, **kw: (_ for _ in ()).throw(httpx.ConnectError("offline")))
    sent = []
    monkeypatch.setattr("app.services.otp.send_email", lambda *a: sent.append(a))
    result = client.post("/auth/request-otp", json={"email": "fallback@example.com"})
    assert result.status_code == 200
    assert result.json()["delivery"] == "email"
    assert sent[0][0] == "fallback@example.com"


def test_failed_delivery_removes_code_and_allows_retry(client, monkeypatch, db_session):
    configure_smtp(monkeypatch)
    monkeypatch.setattr("app.services.otp.send_email", lambda *a: (_ for _ in ()).throw(smtplib.SMTPAuthenticationError(535, b"credentials rejected")))
    for _ in range(2):
        result = client.post("/auth/request-otp", json={"email": "retry-delivery@example.com"})
        assert result.status_code == 502
    assert db_session.query(EmailOtp).filter(EmailOtp.email == "retry-delivery@example.com", EmailOtp.consumed.is_(False)).count() == 0
    with pytest.raises(OtpError): verify_code(db_session, "retry-delivery@example.com", "123456")


def test_no_channel_does_not_pretend_email_sent(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "otp_allow_server_log", False)
    result = client.post("/auth/request-otp", json={"email": "no-channel@example.com"})
    assert result.status_code == 502


def test_production_never_logs_codes(client, monkeypatch, caplog):
    monkeypatch.setattr(get_settings(), "environment", "production")
    monkeypatch.setattr(get_settings(), "otp_allow_server_log", True)
    result = client.post("/auth/request-otp", json={"email": "prod-no-channel@example.com"})
    assert result.status_code == 502
    assert "123456" not in caplog.text


def test_n8n_started_response_is_not_delivery_confirmation(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "n8n_otp_webhook_url", "https://n8n.example/webhook/test")
    monkeypatch.setattr(settings, "n8n_webhook_secret", "test-secret")
    monkeypatch.setattr("app.services.otp.httpx.post", lambda *a, **kw: httpx.Response(200, json={"message": "Workflow was started"}, request=httpx.Request("POST", "https://n8n.example")))
    assert client.post("/auth/request-otp", json={"email": "not-confirmed@example.com"}).status_code == 502
