from datetime import datetime

from pydantic import BaseModel


class ActionProposeRequest(BaseModel):
    action_type: str  # currently supported: "send_invoice_reminder"
    target: dict
    details: dict = {}


class ActionOut(BaseModel):
    id: str
    organization_id: str
    action_type: str
    target: dict
    details: dict
    expected_result: str
    risks: str
    evidence: dict
    requires_approval: bool
    status: str
    created_at: datetime
    approved_by_user_id: str | None
    approved_at: str | None
    execution_result: dict
