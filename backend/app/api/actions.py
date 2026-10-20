import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_membership, require_role
from app.db.session import get_db
from app.models.conversation import AuditLog, Notification
from app.models.financial import Invoice
from app.models.organization import Organization
from app.models.simulation import ActionProposal
from app.models.user import User
from app.schemas.actions import ActionOut, ActionProposeRequest
from app.services.workflows import build_invoice_reminder_draft, dispatch_action

router = APIRouter(prefix="/actions", tags=["actions"])

SUPPORTED_ACTION_TYPES = {"send_invoice_reminder"}


def _to_out(a: ActionProposal) -> ActionOut:
    return ActionOut(
        id=a.id,
        organization_id=a.organization_id,
        action_type=a.action_type,
        target=json.loads(a.target_json),
        details=json.loads(a.details_json),
        expected_result=a.expected_result,
        risks=a.risks,
        evidence=json.loads(a.evidence_json),
        requires_approval=a.requires_approval,
        status=a.status,
        created_at=a.created_at,
        approved_by_user_id=a.approved_by_user_id,
        approved_at=a.approved_at,
        execution_result=json.loads(a.execution_result_json),
    )


@router.post("/propose", response_model=ActionOut, status_code=status.HTTP_201_CREATED)
def propose_action(
    payload: ActionProposeRequest,
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(organization_id, user, db, "ACCOUNTANT")
    if payload.action_type not in SUPPORTED_ACTION_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unsupported action_type '{payload.action_type}'")

    org = db.get(Organization, organization_id)
    drafts = []
    evidence = {}
    if payload.action_type == "send_invoice_reminder":
        invoice_ids = payload.target.get("invoice_ids", [])
        if not invoice_ids:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "target.invoice_ids is required")
        invoices = (
            db.query(Invoice)
            .filter(Invoice.id.in_(invoice_ids), Invoice.organization_id == organization_id)
            .all()
        )
        if len(invoices) != len(invoice_ids):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "One or more invoices not found in this organization")
        for inv in invoices:
            drafts.append(build_invoice_reminder_draft(inv, org.name if org else "Pulse AI", inv.currency))
        evidence = {
            "invoices": [
                {"id": i.id, "counterparty_name": i.counterparty_name, "outstanding": str(i.amount - i.amount_paid)}
                for i in invoices
            ]
        }
        expected_result = f"{len(drafts)} reminder email(s) will be prepared for the listed invoices."
        risks = "Low — no funds are moved. The counterparty will receive a payment reminder email."

    action = ActionProposal(
        organization_id=organization_id,
        created_by_user_id=user.id,
        action_type=payload.action_type,
        target_json=json.dumps(payload.target),
        details_json=json.dumps({"drafts": drafts, **payload.details}),
        expected_result=expected_result,
        risks=risks,
        evidence_json=json.dumps(evidence),
        requires_approval=True,
        status="PENDING_APPROVAL",
        execution_result_json="{}",
    )
    db.add(action)
    db.commit()
    return _to_out(action)


@router.post("/{action_id}/approve", response_model=ActionOut)
def approve_action(
    action_id: str,
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(organization_id, user, db, "FINANCE_MANAGER")
    action = db.get(ActionProposal, action_id)
    if not action or action.organization_id != organization_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Action not found")
    if action.status != "PENDING_APPROVAL":
        raise HTTPException(status.HTTP_409_CONFLICT, f"Action is in status {action.status}, cannot approve")

    action.status = "APPROVED"
    action.approved_by_user_id = user.id
    action.approved_at = datetime.now(timezone.utc).isoformat()
    db.add(
        AuditLog(
            organization_id=organization_id,
            actor_user_id=user.id,
            event_type="action_approved",
            details_json=json.dumps({"action_id": action.id, "action_type": action.action_type}),
        )
    )
    db.commit()
    return _to_out(action)


@router.post("/{action_id}/execute", response_model=ActionOut)
def execute_action(
    action_id: str,
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_role(organization_id, user, db, "FINANCE_MANAGER")
    action = db.get(ActionProposal, action_id)
    if not action or action.organization_id != organization_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Action not found")
    if action.status != "APPROVED":
        raise HTTPException(status.HTTP_409_CONFLICT, f"Action must be APPROVED before execution (current: {action.status})")

    action.status = "QUEUED"
    details = json.loads(action.details_json)
    result = dispatch_action(action.action_type, details)
    action.status = result["status"]
    action.execution_result_json = json.dumps(result)

    db.add(
        Notification(
            organization_id=organization_id,
            user_id=None,
            category="workflow_result",
            severity="info" if result["status"] == "SENT" else "warning",
            title=f"Action {action.action_type} — {result['status']}",
            body=result["detail"],
            link=f"/decisions/{action.id}",
        )
    )
    db.add(
        AuditLog(
            organization_id=organization_id,
            actor_user_id=user.id,
            event_type="action_executed",
            details_json=json.dumps({"action_id": action.id, "result": result}),
        )
    )
    db.commit()
    return _to_out(action)


@router.get("", response_model=list[ActionOut])
def list_actions(
    organization_id: str = Query(...),
    status_filter: str | None = Query(None, alias="status"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    query = db.query(ActionProposal).filter(ActionProposal.organization_id == organization_id)
    if status_filter:
        query = query.filter(ActionProposal.status == status_filter)
    actions = query.order_by(ActionProposal.created_at.desc()).all()
    return [_to_out(a) for a in actions]
