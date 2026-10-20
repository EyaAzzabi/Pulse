# PULSE workflows

## Local installation and execution

Gmail SMTP is sufficient; Google OAuth setup in n8n is not required. Configure
SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM and N8N_WEBHOOK_SECRET
in backend/.env. These secrets are never committed.

From the repository root (Node.js 24 and the backend Python dependencies required):

```powershell
npm --cache .runtime/npm-cache install --prefix .runtime/n8n n8n@2.44.4 --omit=dev --no-audit --no-fund
python n8n/local.py prepare --recipient your-address@gmail.com
python n8n/local.py start
```

Run the PULSE backend on port 8000. Set these local backend variables and restart it:

```dotenv
N8N_OTP_WEBHOOK_URL=http://127.0.0.1:5678/webhook/pulse/verification-code
N8N_WEBHOOK_URL=http://127.0.0.1:5678/webhook/pulse/invoice-reminder
```

Then, in a separate terminal:

```powershell
python n8n/local.py test
```

The test sends email only to the recipient explicitly passed to `prepare`.
It creates an isolated demo organization, uses real engine calculations for the
digest, and verifies approval and replay protection for the recovery plan.
The local digest is on demand: the daily schedule is removed from the runtime
copy, so testing does not subscribe anyone to recurring emails.

n8n is available at http://127.0.0.1:5678. Its database and encryption key live
under ignored .runtime/. SMTP credentials are imported, encrypted by n8n,
and the temporary plaintext import file is deleted. Never commit .runtime/.
The scoped API token can access only the demo organization and expires with
the configured JWT lifetime. Stop n8n and rerun `prepare` to renew it.

The local launcher uses the operating system DNS resolver for SMTP to avoid
Node DNS timeouts on restricted Windows networks. The original hostname is
preserved for TLS certificate verification; certificate checks stay enabled.

## Five supplied workflows

| Workflow | Trigger | Result |
|---|---|---|
| verification_code | Authenticated POST /webhook/pulse/verification-code | SMTP code email and submission receipt |
| invoice_reminder | Authenticated POST /webhook/pulse/invoice-reminder | One email per approved draft, with real recipient addresses |
| cash_risk_alert | Authenticated POST /webhook/pulse/cash-risk-alert | Evidence-based alert to the supplied recipient |
| financial_digest | Schedule (Africa/Tunis, 08:00) or authenticated on-demand POST | Financial engine summary for the scoped organization |
| approved_recovery_plan | Authenticated POST /webhook/pulse/recovery-plan-approved | Calls the guarded PULSE execution endpoint; no approval bypass |

All exports use Header Auth (X-Webhook-Secret), correct webhook body paths,
SMTP credentials and explicit completion receipts. Execution payload saving
is disabled to avoid retaining OTPs in n8n execution history.

## Direct email fallback

PULSE tries the OTP n8n webhook first when configured, then direct SMTP if
available. Gmail uses smtp.gmail.com, port 587, and a Google app password:
https://support.google.com/accounts/answer/185833

From backend, send and verify a real code interactively:

```powershell
python scripts/test_email_delivery.py recipient@example.com
```

OTP_ALLOW_SERVER_LOG=false is the default. Failed sends return an error and
remove the unusable code, allowing a fresh request. Server-log codes require
explicit opt-in and are limited to development/test environments.

## Hosting elsewhere

Import workflows/*.json into your n8n instance, associate real SMTP,
Header Auth and PULSE Bearer Token credentials, and publish the workflows.
Set PULSE_EMAIL_FROM, PULSE_API_BASE_URL, PULSE_ORGANIZATION_ID and
DIGEST_RECIPIENTS for the target organization. Use a tenant-scoped PULSE token;
the platform administrator has no automatic access to tenant financial data.
Only enable the digest schedule for opted-in recipients. The cash risk
webhook is ready to receive events; the backend does not yet automatically
emit risk-threshold events.
