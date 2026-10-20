# Demo video recording guide

No demo video has been recorded yet. The video is optional (no longer than 5 minutes). Target length: 2 to 3 minutes.

1. Reset data: `cd backend && python scripts/seed_demo.py`. Start the backend and frontend.
2. Record the screen at 1440x900 (Windows: Win+Alt+R with Xbox Game Bar, or OBS).
3. Script (follow execution_evidence/DEMO_STEPS.md):
   - 0:00 Landing page, one sentence on the problem.
   - 0:15 Dashboard: cash, risk, shortfall date, insight card.
   - 0:40 Forecast, then Simulator with a 30-day customer delay.
   - 1:10 Copilot question about Atlas Retail; open the agent trace.
   - 1:40 "Prepare reminders for my overdue invoices"; Decisions: approve, execute, show the status.
   - 2:10 Notifications and the admin console.
   - 2:30 Closing line: human approval, deterministic numbers.
4. Do not show the login password, .env files or real personal emails.
5. Save as submission/PULSE_Demo.mp4.
