# n8n setup for Pulse AI

Pulse sends its signup verification code through n8n and Gmail. This guide
sets up that one workflow. It takes about 15 minutes.

## Which workflows to import

| File | Import? | Why |
|---|---|---|
| `workflows/verification_code.json` | **Yes** | Emails the 6-digit signup code. Signup depends on it. |
| `workflows/invoice_reminder.json` | Not yet | Invoices don't store a customer email address yet, so it has nobody to send to. |
| `workflows/cash_risk_alert.json` | No | The backend doesn't send this event yet. |
| `workflows/financial_digest.json` | No | Needs a service API token that doesn't exist yet. |
| `workflows/approved_recovery_plan.json` | No | Optional; the app already does this itself. |

## 1. Choose where n8n runs

The Pulse backend has to be able to reach the n8n webhook URL over the network.

- **n8n Cloud (recommended):** gives you a public URL like
  `https://yourname.app.n8n.cloud`, reachable from anywhere. The free trial is
  enough.
- **n8n on your own laptop:** the backend running on another laptop can't reach
  `localhost` on yours. Only use this if n8n and the backend run on the same
  machine, or you expose n8n with a tunnel such as ngrok.

## 2. Create two credentials

In n8n, go to **Credentials → Add credential**:

1. **Gmail OAuth2**, named `Pulse Gmail`. On n8n Cloud, click
   **Sign in with Google** and pick the Gmail account the codes should be sent
   from.
2. **Header Auth**, named `Pulse webhook secret`:
   - Name: `X-Webhook-Secret`
   - Value: the shared secret Eya sends you privately (it's `N8N_WEBHOOK_SECRET`
     in her `backend/.env`). Never commit it or paste it in a group chat.

The secret stops anyone who finds the webhook URL from sending emails through
your Gmail.

## 3. Import and connect the workflow

1. **Workflows → Import from file** → choose `workflows/verification_code.json`.
2. Open the **Webhook: Verification Code** node, set Credential to
   `Pulse webhook secret`.
3. Open the **Send Code with Gmail** node, set Credential to `Pulse Gmail`.
4. Save, then switch the workflow to **Active** (top right). Inactive workflows
   only answer on the test URL.

## 4. Send Eya the production URL

Open the webhook node and copy the **Production URL**. It ends in
`/webhook/pulse/verification-code`. Don't use the Test URL (`/webhook-test/...`),
which only works while the editor is listening.

Eya puts it in `backend/.env`:

```
N8N_OTP_WEBHOOK_URL=https://yourname.app.n8n.cloud/webhook/pulse/verification-code
```

and restarts the backend.

## 5. Test it

Replace the URL, secret and email, then run:

```bash
curl -X POST "https://yourname.app.n8n.cloud/webhook/pulse/verification-code" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: THE_SHARED_SECRET" \
  -d '{"email":"you@example.com","code":"123456","subject":"Pulse test","html":"<p>Your code is <b>123456</b></p>"}'
```

You should receive the email within a few seconds. A `403` means the secret in
the Header Auth credential doesn't match.

## What the backend sends

```json
{
  "email": "user@example.com",
  "code": "123456",
  "subject": "Your Pulse AI verification code",
  "html": "<div>...formatted email...</div>"
}
```

If n8n is unreachable or returns an error, signup shows an error instead of
pretending the code was sent.
