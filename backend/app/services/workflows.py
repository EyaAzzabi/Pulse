"""Agent 5 — Workflow Coordinator support.

Builds safe, previewable drafts for consequential actions and attempts real
dispatch only when an integration is actually configured (n8n webhook or
SMTP). Otherwise the action is queued and clearly labeled as not delivered —
never silently marked as sent.
"""
from __future__ import annotations

import logging
from datetime import date

import httpx
from pydantic import EmailStr, TypeAdapter, ValidationError

from app.core.config import get_settings
from app.models.financial import Invoice

logger = logging.getLogger(__name__)


def build_invoice_reminder_draft(invoice: Invoice, organization_name: str, currency: str) -> dict:
    outstanding = invoice.amount - invoice.amount_paid
    days_overdue = (date.today() - invoice.due_date).days
    subject = f"Payment reminder from {organization_name} — invoice due {invoice.due_date.isoformat()}"
    body = (
        f"Dear {invoice.counterparty_name},\n\n"
        f"This is a reminder that an invoice of {currency} {outstanding:,.2f} "
        f"(reference {invoice.reference or invoice.id}) was due on {invoice.due_date.isoformat()}"
        + (f" and is now {days_overdue} day(s) overdue." if days_overdue > 0 else ".")
        + f"\n\nPlease arrange payment at your earliest convenience.\n\nBest regards,\n{organization_name}"
    )
    return {"invoice_id": invoice.id, "to": invoice.counterparty_name, "subject": subject, "body": body}


def dispatch_action(action_type: str, details: dict) -> dict:
    """Attempts real delivery through the configured n8n webhook. Returns a
    result dict with a `status` field: SENT (confirmed), QUEUED (no
    integration configured — safe offline fallback), or FAILED."""
    settings = get_settings()
    if not settings.n8n_webhook_url:
        return {
            "status": "QUEUED",
            "detail": "No n8n webhook configured (N8N_WEBHOOK_URL). Action recorded but not dispatched.",
        }
    if action_type == "send_invoice_reminder":
        drafts = details.get("drafts", [])
        if not isinstance(drafts, list) or not drafts:
            return {"status": "FAILED", "detail": "No reminder drafts were supplied."}
        try:
            for draft in drafts:
                TypeAdapter(EmailStr).validate_python(draft.get("to", ""))
        except (ValidationError, AttributeError):
            return {"status": "FAILED", "detail": "Each reminder requires a valid recipient email address. Customer names cannot be used as email addresses."}
    if not settings.n8n_webhook_secret:
        return {"status": "FAILED", "detail": "n8n webhook authentication is not configured."}
    try:
        headers = {}
        if settings.n8n_webhook_secret:
            headers["X-Webhook-Secret"] = settings.n8n_webhook_secret
        response = httpx.post(
            settings.n8n_webhook_url,
            json={"action_type": action_type, "details": details},
            headers=headers,
            timeout=10.0,
        )
        response.raise_for_status()
        receipt = response.json()
        if not isinstance(receipt, dict) or receipt.get("sent") is not True or not receipt.get("message_id"):
            return {"status": "FAILED", "detail": "The workflow did not confirm email submission."}
        return {"status": "SENT", "detail": "Delivered via configured n8n webhook."}
    except Exception as exc:
        logger.exception("n8n webhook dispatch failed")
        return {"status": "FAILED", "detail": f"Webhook dispatch failed: {exc}"}
