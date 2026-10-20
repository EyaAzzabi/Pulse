# Simulation mode

- **Company data**: Northstar Studio is a sample company loaded by `backend/scripts/seed_demo.py` (transactions, invoices, recurring obligations). No real customer or bank data is used in the evidence.
- **Real computation**: summary, forecast, Digital Twin, rescue plans, notifications, approvals and the audit log run on the real backend and database.
- **Real AI**: the copilot calls the OpenAI API (gpt-4o-mini) with tool calling when a key is configured; otherwise a deterministic router answers from the same tools.
- **Simulated execution**: approved actions are dispatched to an n8n webhook only when one is configured. In the captured run no action webhook was configured, so execution returned status `QUEUED` with the message "No n8n webhook configured (N8N_WEBHOOK_URL). Action recorded but not dispatched." The platform never reports such an action as SENT.
- **No money movement**: no payment, transfer or borrowing is possible. The credit-line rescue strategy uses illustrative terms.
