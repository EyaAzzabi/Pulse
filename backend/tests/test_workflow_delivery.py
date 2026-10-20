import httpx

from app.core.config import get_settings
from app.services.workflows import dispatch_action


def setup_channel(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "n8n_webhook_url", "https://workflow.example/webhook/reminder")
    monkeypatch.setattr(settings, "n8n_webhook_secret", "test-secret")


def test_recipient_name_is_not_treated_as_email(monkeypatch):
    setup_channel(monkeypatch)
    result = dispatch_action("send_invoice_reminder", {"drafts": [{"to": "Acme Customer"}]})
    assert result["status"] == "FAILED"
    assert "email address" in result["detail"]


def test_workflow_must_confirm_email_submission(monkeypatch):
    setup_channel(monkeypatch)
    def response(body):
        return lambda *a, **kw: httpx.Response(200, json=body, request=httpx.Request("POST", "https://workflow.example"))
    details = {"drafts": [{"to": "recipient@example.com", "subject": "Reminder", "body": "Test"}]}
    monkeypatch.setattr("app.services.workflows.httpx.post", response({"message": "Workflow was started"}))
    assert dispatch_action("send_invoice_reminder", details)["status"] == "FAILED"
    monkeypatch.setattr("app.services.workflows.httpx.post", response({"sent": True, "message_id": "smtp-message-id"}))
    assert dispatch_action("send_invoice_reminder", details)["status"] == "SENT"
