# Demo steps (core scenario)

1. Start the backend and frontend (root README, Quick start). Run `python scripts/seed_demo.py` to load Northstar Studio.
2. Sign in with the login printed by the seed script. The dashboard shows current cash of EUR 7,020, medium risk, and a shortfall predicted on 7 Nov 2026 (lowest point -EUR 2,308).
3. Open **Forecast** to see the 90-day projection and the shortfall.
4. Open **Simulator** and run a scenario (for example, a 30-day customer delay). Compare the baseline and the scenario.
5. On the dashboard, **Explore rescue strategies**: collect overdue invoices +EUR 7,150, credit line +EUR 4,560 (illustrative), supplier extension +EUR 4,372.
6. Open **Copilot** and ask "What happens if Atlas Retail pays 30 days late, and how can I avoid a cash shortage?". Expand "How PULSE answered" to see the agents.
7. Ask "Prepare reminders for my overdue invoices." The Workflow Coordinator creates a PENDING_APPROVAL action.
8. Open **Decisions**, approve the action, then execute it. Without a webhook the status becomes QUEUED; with n8n configured, the reminder is sent.
9. Open **Notifications** for the shortfall and overdue alerts.
