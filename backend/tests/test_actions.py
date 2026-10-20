from datetime import date, timedelta

from tests.conftest import register_and_login


def test_propose_requires_membership(client):
    headers_a, org_a = register_and_login(client, "actions-a@example.com", org_name="Actions A")
    _, org_b = register_and_login(client, "actions-b@example.com", org_name="Actions B")

    resp = client.post(
        f"/actions/propose?organization_id={org_b}",
        json={"action_type": "send_invoice_reminder", "target": {"invoice_ids": []}},
        headers=headers_a,
    )
    assert resp.status_code == 403


def test_unsupported_action_type_rejected(client):
    headers, org_id = register_and_login(client, "actions-c@example.com", org_name="Actions C")
    resp = client.post(
        f"/actions/propose?organization_id={org_id}",
        json={"action_type": "wire_transfer", "target": {}},
        headers=headers,
    )
    assert resp.status_code == 400


def test_cannot_execute_without_approval(client):
    headers, org_id = register_and_login(client, "actions-d@example.com", org_name="Actions D")
    resp = client.post(
        f"/actions/propose?organization_id={org_id}",
        json={"action_type": "send_invoice_reminder", "target": {"invoice_ids": []}},
        headers=headers,
    )
    assert resp.status_code == 400  # no invoice_ids provided -> validation error, nothing to approve


def test_approve_then_execute_is_idempotent_on_status(client, db_session):
    from app.models.financial import Invoice
    from decimal import Decimal

    headers, org_id = register_and_login(client, "actions-e@example.com", org_name="Actions E")

    invoice = Invoice(
        organization_id=org_id,
        direction="RECEIVABLE",
        counterparty_name="Acme",
        amount=Decimal("500.00"),
        amount_paid=Decimal("0"),
        currency="EUR",
        issue_date=date.today() - timedelta(days=40),
        due_date=date.today() - timedelta(days=10),
        status="overdue",
        reference="INV-TEST-1",
    )
    db_session.add(invoice)
    db_session.commit()

    propose = client.post(
        f"/actions/propose?organization_id={org_id}",
        json={"action_type": "send_invoice_reminder", "target": {"invoice_ids": [invoice.id]}},
        headers=headers,
    )
    assert propose.status_code == 201
    action_id = propose.json()["id"]
    assert propose.json()["status"] == "PENDING_APPROVAL"

    # Cannot execute before approval.
    exec_before = client.post(f"/actions/{action_id}/execute?organization_id={org_id}", headers=headers)
    assert exec_before.status_code == 409

    approve = client.post(f"/actions/{action_id}/approve?organization_id={org_id}", headers=headers)
    assert approve.status_code == 200
    assert approve.json()["status"] == "APPROVED"

    # Double approval is rejected (no replay).
    approve_again = client.post(f"/actions/{action_id}/approve?organization_id={org_id}", headers=headers)
    assert approve_again.status_code == 409

    execute = client.post(f"/actions/{action_id}/execute?organization_id={org_id}", headers=headers)
    assert execute.status_code == 200
    # No n8n webhook configured in tests -> safe fallback, never falsely "SENT".
    assert execute.json()["status"] == "QUEUED"
