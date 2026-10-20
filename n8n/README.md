# Optional n8n delivery bridge

The application works without n8n: approved reminder actions are retained in a local queue. A webhook acknowledgment is not proof that an email was sent.

The workflow exports in `workflows/` implement authenticated receipt and explicit queue acknowledgment. Import a JSON file into your own n8n instance, create a **Header Auth** credential with header name `Authorization` and value `Bearer <your-secret>`, attach it to the webhook node, and activate the workflow. Set the backend `N8N_WEBHOOK_URL` to its production webhook URL and `N8N_WEBHOOK_SECRET` to the same secret. Keep the URL operator-controlled.

These are queue bridges, not configured email delivery workflows. Add your own verified email provider step and delivery handling before claiming delivery. Preserve the application's idempotency key in any provider submission and ensure repeated receipts do not send duplicate email. Never expose credentials in an exported JSON file.

Live n8n operation and email delivery have not been verified in this workspace. Scheduled digest delivery and automatic risk dispatch remain outside the verified scope.
