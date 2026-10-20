from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatMessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime
    agent_trace: list[dict] = []


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    ai_generated: bool
    llm_available: bool
    metrics: dict
    risk_indicators: list[str]
    evidence: list[str]
    suggested_follow_ups: list[str]
    chart_points: list[dict]
    agent_trace: list[dict] = []
    actions: list[dict] = []


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    messages: list[ChatMessageOut]
