import json

from app.models.user import Membership, User
from app.core.security import hash_password
from tests.conftest import register_and_login


def _call(name, args, call_id="c1"):
    return {"role": "assistant", "content": None, "tool_calls": [
        {"id": call_id, "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}
    ]}


def _final(text):
    return {"role": "assistant", "content": text}


def _setup(client, email, org_name):
    headers, org = register_and_login(client, email, org_name=org_name)
    assert client.post(f"/onboarding/sample-data?organization_id={org}", headers=headers).status_code == 200
    return headers, org


def _fake_llm(monkeypatch, script):
    """script(messages) -> assistant message. Records every call."""
    seen = []

    def fake(messages, tools, timeout=30.0):
        seen.append(messages)
        return script(messages)

    monkeypatch.setattr("app.agents.llm_provider.is_llm_configured", lambda: True)
    monkeypatch.setattr("app.agents.llm_provider.chat_with_tools", fake)
    monkeypatch.setattr("app.agents.llm_provider.complete", lambda *a, **k: None)
    return seen


def test_agent_runs_simulation_with_user_numbers(client, monkeypatch):
    headers, org = _setup(client, "agent-sim@example.com", "Agent Sim")

    def script(messages):
        if messages[-1]["role"] == "user":
            return _call("simulate_scenario", {"customer_payment_delay_days": 20, "inventory_purchase_amount": 8000})
        return _final("With both changes your lowest point drops further.")

    seen = _fake_llm(monkeypatch, script)
    body = client.post(
        f"/copilot/chat?organization_id={org}",
        json={"message": "What if Atlas pays 20 days late and I buy 8000 of inventory?"},
        headers=headers,
    ).json()

    assert body["ai_generated"] is True
    assert body["message"].startswith("With both changes")
    assert body["agent_trace"][0]["agent"] == "Strategic Planner"
    assert body["agent_trace"][0]["tool"] == "simulate_scenario"
    assert body["agent_trace"][-1]["agent"] == "Risk Guardian"
    assert len(body["chart_points"]) == 90

    tool_result = json.loads(seen[1][-1]["content"])
    assert tool_result["assumptions"]["customer_payment_delay_days"] == "20"
    assert float(tool_result["simulated_lowest_cash"]) < float(tool_result["baseline_lowest_cash"])


def test_agent_drafts_reminder_for_approval_only(client, monkeypatch):
    headers, org = _setup(client, "agent-remind@example.com", "Agent Remind")

    def script(messages):
        last = messages[-1]
        if last["role"] == "user":
            return _call("list_invoices", {"direction": "RECEIVABLE", "status": "overdue"})
        if last["role"] == "tool" and "invoices" in json.loads(last["content"]) and "count" in json.loads(last["content"]):
            ids = [i["id"] for i in json.loads(last["content"])["invoices"]]
            return _call("propose_invoice_reminder", {"invoice_ids": ids}, "c2")
        return _final("I drafted 3 reminders. They are waiting for your approval.")

    _fake_llm(monkeypatch, script)
    body = client.post(
        f"/copilot/chat?organization_id={org}",
        json={"message": "Prepare reminders for my overdue invoices"},
        headers=headers,
    ).json()

    assert [t["tool"] for t in body["agent_trace"][:2]] == ["list_invoices", "propose_invoice_reminder"]
    assert body["actions"][0]["status"] == "PENDING_APPROVAL"
    actions = client.get(f"/actions?organization_id={org}", headers=headers).json()
    assert actions[0]["status"] == "PENDING_APPROVAL"
    assert len(actions[0]["details"]["drafts"]) == 3
    notes = client.get(f"/notifications?organization_id={org}", headers=headers).json()
    assert any(n["category"] == "approval_request" for n in notes)


def test_risk_guardian_blocks_viewer_from_drafting(client, monkeypatch, db_session):
    owner_headers, org = _setup(client, "agent-owner@example.com", "Agent Viewer Co")
    viewer = User(email="viewer@example.com", password_hash=hash_password("StrongPass123"), full_name="Viewer")
    db_session.add(viewer)
    db_session.flush()
    db_session.add(Membership(user_id=viewer.id, organization_id=org, role="VIEWER"))
    db_session.commit()
    token = client.post("/auth/login", json={"email": "viewer@example.com", "password": "StrongPass123"}).json()["access_token"]
    viewer_headers = {"Authorization": f"Bearer {token}"}

    def script(messages):
        if messages[-1]["role"] == "user":
            return _call("propose_invoice_reminder", {"invoice_ids": ["anything"]})
        return _final("Your role can't draft reminders.")

    _fake_llm(monkeypatch, script)
    body = client.post(
        f"/copilot/chat?organization_id={org}", json={"message": "Send reminders"}, headers=viewer_headers
    ).json()

    assert body["agent_trace"][0]["agent"] == "Risk Guardian"
    assert body["actions"] == []
    assert client.get(f"/actions?organization_id={org}", headers=owner_headers).json() == []


def test_llm_failure_falls_back_to_deterministic(client, monkeypatch):
    headers, org = _setup(client, "agent-fallback@example.com", "Agent Fallback")

    def boom(messages, tools, timeout=30.0):
        raise RuntimeError("provider down")

    monkeypatch.setattr("app.agents.llm_provider.is_llm_configured", lambda: True)
    monkeypatch.setattr("app.agents.llm_provider.chat_with_tools", boom)
    monkeypatch.setattr("app.agents.llm_provider.complete", lambda *a, **k: None)

    body = client.post(
        f"/copilot/chat?organization_id={org}", json={"message": "What is my biggest risk?"}, headers=headers
    ).json()
    assert body["ai_generated"] is False
    assert "overdue receivables" in body["message"]
    assert body["agent_trace"][0]["summary"].startswith("Deterministic mode")


def test_conversation_belongs_to_its_author(client):
    headers_a, org = _setup(client, "conv-a@example.com", "Conv Co")
    conv = client.post(f"/copilot/chat?organization_id={org}", json={"message": "hi"}, headers=headers_a).json()
    headers_b, _ = register_and_login(client, "conv-b@example.com", org_name="Other")
    resp = client.post(
        f"/copilot/chat?organization_id={org}",
        json={"message": "hi", "conversation_id": conv["conversation_id"]},
        headers=headers_b,
    )
    assert resp.status_code == 403
