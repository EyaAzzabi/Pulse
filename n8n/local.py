"""Install-time provisioning and local n8n execution for PULSE.

python n8n/local.py prepare   # imports workflows and encrypted credentials
python n8n/local.py start     # starts n8n at 127.0.0.1:5678
python n8n/local.py test      # runs all five workflows against the demo tenant

Only the explicitly selected test recipient receives test emails. Credentials,
keys and n8n's database remain under the ignored .runtime directory.
"""
import argparse
from datetime import date
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
os.chdir(ROOT / "backend")

import httpx
from app.core.config import get_settings
from app.core.security import create_access_token, hash_password
from app.db.session import SessionLocal
from app.models.financial import Invoice
from app.models.organization import Organization, OnboardingProgress
from app.models.user import User, Membership
from app.services.sample_data import load_sample_data

RUNTIME = ROOT / ".runtime"
CLI = RUNTIME / "n8n/node_modules/n8n/bin/n8n"
IDS = {"verification_code": "pulseVerification", "invoice_reminder": "pulseInvoice", "cash_risk_alert": "pulseRiskAlert", "financial_digest": "pulseDigest", "approved_recovery_plan": "pulseRecovery"}


def environment():
    RUNTIME.mkdir(exist_ok=True)
    key_file = RUNTIME / "n8n-encryption-key"
    if not key_file.exists():
        key_file.write_text(secrets.token_urlsafe(48), encoding="utf-8")
    state = json.loads((RUNTIME / "pulse-n8n.json").read_text(encoding="utf-8")) if (RUNTIME / "pulse-n8n.json").exists() else {}
    settings = get_settings()
    return {**os.environ, "N8N_USER_FOLDER": str(RUNTIME / "n8n-user"), "N8N_ENCRYPTION_KEY": key_file.read_text(encoding="utf-8"),
        "N8N_HOST": "127.0.0.1", "N8N_PORT": "5678", "N8N_LISTEN_ADDRESS": "127.0.0.1", "N8N_PROTOCOL": "http",
        "N8N_SECURE_COOKIE": "false", "WEBHOOK_URL": "http://127.0.0.1:5678/", "N8N_BLOCK_ENV_ACCESS_IN_NODE": "false",
        "N8N_DIAGNOSTICS_ENABLED": "false", "N8N_VERSION_NOTIFICATIONS_ENABLED": "false", "N8N_TEMPLATES_ENABLED": "false",
        "GENERIC_TIMEZONE": "Africa/Tunis", "PULSE_EMAIL_FROM": settings.smtp_from or settings.smtp_user or "",
        "PULSE_SMTP_HOST": settings.smtp_host or "", "NODE_OPTIONS": '--require "' + (ROOT / "n8n/smtp-dns.cjs").as_posix() + '"',
        "PULSE_API_BASE_URL": "http://127.0.0.1:8000", "PULSE_ORGANIZATION_ID": state.get("organization_id", ""),
        "DIGEST_RECIPIENTS": state.get("recipient", ""), "N8N_LOG_LEVEL": "warn"}


def cli(*args):
    if not CLI.exists():
        raise SystemExit("Install n8n first: npm --cache .runtime/npm-cache install --prefix .runtime/n8n n8n@2.44.4 --omit=dev --no-audit --no-fund")
    result = subprocess.run(["node", str(CLI), *args], env=environment(), cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        # CLI output contains no imported credential payload, but keep it local.
        (RUNTIME / "n8n-cli-error.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        raise SystemExit(f"n8n command failed: {args[0]}. See .runtime/n8n-cli-error.log")
    print(f"n8n: {args[0]} completed.")


def prepare(recipient):
    settings = get_settings()
    if not (settings.smtp_host and settings.smtp_user and settings.smtp_password and settings.n8n_webhook_secret):
        raise SystemExit("Configure SMTP and N8N_WEBHOOK_SECRET in backend/.env first.")
    RUNTIME.mkdir(exist_ok=True)
    with SessionLocal() as db:
        org = db.query(Organization).filter(Organization.name == "PULSE Workflow Test - Demo", Organization.is_demo.is_(True)).first()
        if not org:
            org = Organization(name="PULSE Workflow Test - Demo", is_demo=True)
            db.add(org)
            db.flush()
            db.add(OnboardingProgress(organization_id=org.id, completed=True))
            db.commit()
            load_sample_data(db, org.id, date.today())
        user = db.query(User).filter(User.email == "workflow-service@pulse.local").first()
        if not user:
            user = User(email="workflow-service@pulse.local", full_name="Workflow demo service", password_hash=hash_password(secrets.token_urlsafe(32)), account_status="APPROVED")
            db.add(user)
            db.flush()
            db.add(Membership(user_id=user.id, organization_id=org.id, role="FINANCE_MANAGER"))
            db.commit()
        if not db.query(Membership).filter_by(user_id=user.id, organization_id=org.id, role="FINANCE_MANAGER").first():
            raise SystemExit("Unexpected service account scope; refusing to change its permissions.")
        token = create_access_token(user.id)
        state = {"organization_id": org.id, "recipient": recipient, "service_token": token}
    (RUNTIME / "pulse-n8n.json").write_text(json.dumps(state), encoding="utf-8")
    credentials = [
        {"id": "pulseSmtp", "name": "Pulse SMTP", "type": "smtp", "data": {"host": settings.smtp_host, "port": settings.smtp_port, "user": settings.smtp_user, "password": settings.smtp_password, "secure": settings.smtp_port == 465}},
        {"id": "pulseWebhookAuth", "name": "Pulse webhook secret", "type": "httpHeaderAuth", "data": {"name": "X-Webhook-Secret", "value": settings.n8n_webhook_secret}},
        {"id": "pulseScopedToken", "name": "Pulse API Bearer Token", "type": "httpHeaderAuth", "data": {"name": "Authorization", "value": "Bearer " + token}},
    ]
    credential_file = RUNTIME / "import-credentials.json"
    try:
        credential_file.write_text(json.dumps(credentials), encoding="utf-8")
        cli("import:credentials", "--input=" + str(credential_file))
    finally:
        credential_file.unlink(missing_ok=True)
    workflow_dir = RUNTIME / "workflows"
    workflow_dir.mkdir(exist_ok=True)
    for name, workflow_id in IDS.items():
        workflow = json.loads((ROOT / "n8n/workflows" / (name + ".json")).read_text(encoding="utf-8"))
        workflow["id"] = workflow_id
        workflow.pop("_pulse_notes", None)
        # Local digest is on demand. Publishing it does not enable a daily email schedule.
        if name == "financial_digest":
            workflow["nodes"] = [n for n in workflow["nodes"] if n["type"] != "n8n-nodes-base.scheduleTrigger"]
            workflow["connections"].pop("Daily 08:00", None)
            sender = next(n for n in workflow["nodes"] if n["type"] == "n8n-nodes-base.emailSend")
            sender["parameters"]["subject"] = "[PULSE TEST] Demo financial digest"
            sender["parameters"]["text"] = "Demonstration data only. No real business records.\n\n" + sender["parameters"]["text"]
        for node in workflow["nodes"]:
            for cred_type, credential in node.get("credentials", {}).items():
                credential["id"] = "pulseSmtp" if cred_type == "smtp" else "pulseScopedToken" if credential["name"] == "Pulse API Bearer Token" else "pulseWebhookAuth"
        (workflow_dir / (name + ".json")).write_text(json.dumps(workflow), encoding="utf-8")
    cli("import:workflow", "--separate", "--input=" + str(workflow_dir))
    for workflow_id in IDS.values():
        cli("publish:workflow", "--id=" + workflow_id)
    print("Five workflows provisioned. Demo-only API token expires after the configured JWT lifetime; rerun prepare to renew it.")


def test():
    state = json.loads((RUNTIME / "pulse-n8n.json").read_text(encoding="utf-8"))
    settings = get_settings()
    recipient, org_id = state["recipient"], state["organization_id"]
    headers = {"X-Webhook-Secret": settings.n8n_webhook_secret}
    bearer = {"Authorization": "Bearer " + state["service_token"]}
    results = {}

    def webhook(name, body):
        response = httpx.post("http://127.0.0.1:5678/webhook/pulse/" + name, headers=headers, json=body, timeout=60)
        response.raise_for_status()
        data = response.json()
        if not (data.get("sent") is True and (data.get("message_id") or data.get("status") == "SENT")):
            raise RuntimeError(f"Workflow {name} did not confirm completion")
        results[name] = {"confirmed": True, "message_id": data.get("message_id"), "status": data.get("status")}
        print(f"PASS: {name}")

    webhook("verification-code", {"email": recipient, "code": "000000", "subject": "[PULSE TEST] n8n verification workflow", "html": "<p>n8n workflow test. Demo code: <b>000000</b>. This is not a real signup code.</p>"})
    webhook("cash-risk-alert", {"action_type": "cash_risk_alert", "details": {"recipient_email": recipient, "risk_level": "DEMO TEST", "message": "[PULSE TEST] Demonstration cash risk alert. No real business is affected.", "evidence": {"dataset": "demo"}}})
    webhook("financial-digest", {})
    with SessionLocal() as db:
        invoice_id = db.query(Invoice).filter_by(organization_id=org_id).first().id
    action_url = "http://127.0.0.1:8000/actions"
    payload = {"action_type": "send_invoice_reminder", "target": {"invoice_ids": [invoice_id]}, "details": {"drafts": [{"to": recipient, "subject": "[PULSE TEST] n8n approved reminder", "body": "Demo reminder sent only to the test recipient. No customer has been contacted."}]}}
    response = httpx.post(action_url + "/propose", params={"organization_id": org_id}, headers=bearer, json=payload)
    response.raise_for_status()
    action_id = response.json()["id"]
    blocked = httpx.post(action_url + f"/{action_id}/execute", params={"organization_id": org_id}, headers=bearer)
    assert blocked.status_code == 409, "Unapproved action was not blocked"
    approved = httpx.post(action_url + f"/{action_id}/approve", params={"organization_id": org_id}, headers=bearer)
    approved.raise_for_status()
    # Recovery calls the guarded PULSE execute endpoint, which dispatches the invoice webhook.
    webhook("recovery-plan-approved", {"details": {"action_id": action_id, "organization_id": org_id}})
    replay = httpx.post(action_url + f"/{action_id}/execute", params={"organization_id": org_id}, headers=bearer)
    assert replay.status_code == 409, "Executed action was replayed"
    results["invoice-reminder"] = {"confirmed": True, "via": "approved recovery plan", "action_id": action_id}
    results["approval_and_replay_guards"] = {"confirmed": True}
    (RUNTIME / "n8n-test-results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("PASS: all five workflows, real SMTP delivery, backend approval and replay protection.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "start", "test"])
    parser.add_argument("--recipient", default="")
    args = parser.parse_args()
    if args.command == "prepare":
        if not args.recipient:
            parser.error("--recipient is required for prepare")
        from pydantic import EmailStr, TypeAdapter
        prepare(str(TypeAdapter(EmailStr).validate_python(args.recipient)))
    elif args.command == "start":
        raise SystemExit(subprocess.call(["node", str(CLI), "start"], env=environment(), cwd=ROOT))
    else:
        test()
