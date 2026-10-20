import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.agents import llm_provider
from app.agents.orchestrator import run_agent
from app.agents.tools import AgentContext
from app.api.deps import get_current_user, require_membership
from app.db.session import get_db
from app.models.conversation import ChatMessage, Conversation
from app.models.organization import Organization
from app.models.user import User
from app.schemas.copilot import ChatMessageOut, ChatRequest, ChatResponse, ConversationOut
from app.services.financial_data import load_financial_inputs
from app.services.notifications import notify

router = APIRouter(prefix="/copilot", tags=["copilot"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = require_membership(organization_id, user, db)
    org = db.get(Organization, organization_id)

    if payload.conversation_id:
        conversation = db.get(Conversation, payload.conversation_id)
        if not conversation or conversation.organization_id != organization_id or conversation.user_id != user.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    else:
        conversation = Conversation(
            organization_id=organization_id, user_id=user.id, title=payload.message[:80]
        )
        db.add(conversation)
        db.flush()

    prior_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation.id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in prior_messages]

    db.add(ChatMessage(conversation_id=conversation.id, role="user", content=payload.message))

    starting_cash, transactions, invoices, recurring = load_financial_inputs(db, organization_id)
    ctx = AgentContext(
        db=db,
        organization_id=organization_id,
        organization_name=org.name if org else "your business",
        user_id=user.id,
        role=membership.role,
        currency=org.currency if org else "EUR",
        starting_cash=starting_cash,
        transactions=transactions,
        invoices=invoices,
        recurring=recurring,
        as_of=date.today(),
    )
    result = run_agent(payload.message, history, ctx)
    for action in result.actions:
        notify(
            db,
            organization_id,
            category="approval_request",
            severity="warning",
            title=f"Copilot drafted {action['count']} invoice reminder(s)",
            body="Review the drafts and approve or reject them in the Decision Center.",
            link="/decisions",
        )

    db.add(
        ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=result.message,
            metadata_json=json.dumps(
                {"ai_generated": result.ai_generated, "metrics": result.metrics, "agent_trace": result.agent_trace}
            ),
        )
    )
    db.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        message=result.message,
        ai_generated=result.ai_generated,
        llm_available=llm_provider.is_llm_configured(),
        metrics=result.metrics,
        risk_indicators=result.risk_indicators,
        evidence=result.evidence,
        suggested_follow_ups=result.suggested_follow_ups,
        chart_points=result.chart_points,
        agent_trace=result.agent_trace,
        actions=result.actions,
    )


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(
    organization_id: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_membership(organization_id, user, db)
    conversations = (
        db.query(Conversation)
        .filter(Conversation.organization_id == organization_id, Conversation.user_id == user.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )
    return [
        ConversationOut(
            id=c.id,
            title=c.title,
            created_at=c.created_at,
            messages=[
                ChatMessageOut(
                    role=m.role,
                    content=m.content,
                    created_at=m.created_at,
                    agent_trace=json.loads(m.metadata_json or "{}").get("agent_trace", []),
                )
                for m in c.messages
            ],
        )
        for c in conversations
    ]
