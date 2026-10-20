<div align="center">

<img src="docs/assets/banner.png" alt="PULSE AI: see the cash crisis before it arrives" width="100%" />

**AI cash-flow copilot for small and medium enterprises**<br/>
Shenzhen International FinTech Competition 2026 (FinTechathon) · International Track · **Topic E**

It predicts the next shortfall, simulates rescue strategies in a Financial Digital Twin,<br/>and lets AI agents propose actions that only run after a human approves them.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-REST-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-strict-3178C6?logo=typescript&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-v4-06B6D4?logo=tailwindcss&logoColor=white)
![OpenAI](https://img.shields.io/badge/LLM-OpenAI%20tool%20calling-412991?logo=openai&logoColor=white)
<br/>
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3FCF8E?logo=supabase&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-automations-EA4B71?logo=n8n&logoColor=white)
![Tests](https://img.shields.io/badge/tests-87%20passed-14B8A6)
![Human in the loop](https://img.shields.io/badge/actions-human%20approval-0B1F3A)

[Why](#why-pulse-ai) · [Product](#the-product) · [Architecture](#architecture) · [Install and test](#installation-and-testing-guide) · [Responsible AI](#responsible-ai)

<br/>

![PULSE AI landing page](submission/screenshots/01_landing.png)

</div>

---

## Why PULSE AI

A profitable SME can still run out of cash. Late customer payments, clustered supplier bills and tax dates add up to a negative balance weeks later, and spreadsheets do not show when or what to do about it.

PULSE AI answers three questions every morning:

1. **Where am I?** Current cash, 30-day net flow, overdue receivables.
2. **What is coming?** A deterministic day-by-day forecast, with the lowest point and the first shortfall date.
3. **What should I do?** Rescue strategies, simulated and ranked by impact, turned into actions a human approves.

Every figure comes from the deterministic financial engine. The language model chooses tools and writes the answer; it never invents numbers.

## The product

### Dashboard
Insight card with read-aloud, KPIs, a 60-day history plus 60-day forecast chart, upcoming 30 days, overdue aging and what changed.

![Dashboard](submission/screenshots/04_dashboard.png)

### AI Copilot with a visible agent trace
Five specialised agents (Financial Analyst, Forecast Analyst, Strategic Planner, Workflow Coordinator, Risk Guardian) use OpenAI tool calling on top of the engines, with a deterministic fallback. Conversation history, voice input and read-aloud are included.

![Copilot answering a late-payment question](submission/screenshots/12_copilot_agent_trace.png)

### Cash forecast
Known flows (open invoices, recurring obligations) plus an uncertain baseline drawn from history.

![Forecast](submission/screenshots/06_forecast.png)

### Financial Digital Twin
Replay the business under any scenario: customer or supplier delays, revenue and expense changes, financing, one-off purchases.

| Simulator | Scenario result |
|---|---|
| ![Simulator](submission/screenshots/07_simulator.png) | ![Simulation result](submission/screenshots/08_simulator_result.png) |

### Human-in-the-loop Decision Center
Agents can only **propose**. A Finance Manager or Owner **approves**, then **executes**. Unapproved or repeated execution is refused, and an action is never marked as sent unless a configured integration confirmed it.

| Decisions | Invoices |
|---|---|
| ![Decision Center](submission/screenshots/10_decisions.png) | ![Invoices](submission/screenshots/09_invoices.png) |

### Notifications
Shortfall and overdue alerts are raised automatically from the forecast, with deduplication.

![Notifications](submission/screenshots/11_notifications.png)

### Onboarding
One coherent flow covers the account, an emailed verification code, the company profile and role, and data: an Excel or CSV upload with column mapping, a Google Sheets link, the Northstar Studio company, or quick estimates.

| Sign in | Sign up and onboarding |
|---|---|
| ![Login](submission/screenshots/03_login.png) | ![Onboarding](submission/screenshots/02_signup_onboarding.png) |

### Administration console
Platform administrators review and suspend accounts, browse users and organizations, check service status and read the activity log. Personal emails are masked in these screenshots.

| Overview | Account approvals |
|---|---|
| ![Admin overview](submission/screenshots/14_admin_overview.png) | ![Admin validations](submission/screenshots/15_admin_validations.png) |
| **Users** | **Organizations** |
| ![Admin users](submission/screenshots/16_admin_users.png) | ![Admin organizations](submission/screenshots/17_admin_organizations.png) |
| **Service status** | **Activity log** |
| ![Admin services](submission/screenshots/18_admin_services.png) | ![Admin audit](submission/screenshots/19_admin_audit.png) |

## Architecture

```
React 19 + Vite + Tailwind  ──JWT──▶  FastAPI
                                       ├─ api/          auth, onboarding, imports, financial, forecast,
                                       │                simulations, recommendations, actions, copilot,
                                       │                notifications, admin
                                       ├─ agents/       orchestrator (OpenAI tool calling + fallback), tools
                                       ├─ forecasting/  deterministic forecast engine (Decimal)
                                       ├─ simulations/  Financial Digital Twin
                                       └─ services/     rescue plans, alerts, OTP, email, tabular import
                                              │ SQLAlchemy 2 + Alembic
                                              ▼
                                     Supabase Postgres   (SQLite in tests)
n8n workflows (signed webhooks): verification code, invoice reminder, cash risk alert, digest, recovery plan
```

Details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Installation and testing guide

Follow these steps in order. Setup takes about 10 minutes and runs entirely on your computer: no cloud account and no API key are required.

### Step 0. Prerequisites

| Tool | Version | Check with |
|---|---|---|
| Git | any recent | `git --version` |
| Python | 3.11 or newer | `python --version` |
| Node.js | 20.19 or newer (includes npm) | `node --version` |

You need **two terminals**: one for the backend, one for the frontend.

### Step 1. Get the code

```bash
git clone https://github.com/EyaAzzabi/Pulse.git
cd Pulse
```

### Step 2. Install the backend (terminal 1)

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

| System | Command |
|---|---|
| Windows (PowerShell) | `.\.venv\Scripts\Activate.ps1` |
| Windows (Git Bash) | `source .venv/Scripts/activate` |
| macOS / Linux | `source .venv/bin/activate` |

Then install the dependencies:

```bash
pip install -r requirements.txt
```

### Step 3. Configure the backend

Create a file named `.env` inside the `backend/` folder with this content:

```env
# Local database (a SQLite file is created automatically)
DATABASE_URL=sqlite:///./pulse.db
JWT_SECRET=change-me-to-any-long-random-string

# Show sign-up verification codes in the backend terminal (local testing only)
OTP_ALLOW_SERVER_LOG=true

# Optional: AI copilot with OpenAI. Without these lines the copilot still
# works in deterministic mode, answering from the financial engine.
# LLM_PROVIDER=openai
# LLM_API_KEY=sk-...
# LLM_MODEL=gpt-4o-mini
```

> Never commit the `.env` file. It is already listed in `.gitignore`.

### Step 4. Create the database and load the sample company

```bash
python -m alembic upgrade head
python scripts/seed_demo.py
```

The seed script loads **Northstar Studio**: six months of transactions, overdue invoices and recurring bills. It prints the login:

```
Northstar Studio seeded successfully.
  Login email:  owner@northstarstudio.demo
  Password:     <generated password>
```

Keep that password. To choose your own, set it before running the script: `export DEMO_USER_PASSWORD=YourPassword123` (PowerShell: `$env:DEMO_USER_PASSWORD="YourPassword123"`). Run the script again at any time to reset the data.

### Step 5. Start the backend

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Check that it works: http://localhost:8000/health returns `"status": "ok"`, and http://localhost:8000/docs shows the interactive API documentation. Leave this terminal open.

### Step 6. Install and start the frontend (terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The frontend forwards API calls to the backend on port 8000 automatically.

### Step 7. Test the application

Sign in with the Northstar Studio login from step 4, then follow this scenario:

1. **Dashboard**: current cash, risk level, and the date the forecast predicts cash will go below zero.
2. **Forecast**: the day-by-day projection for the next 90 days and its lowest point.
3. **Simulator**: set a 30-day customer payment delay, run the simulation and compare it with the baseline.
4. **Dashboard, then Explore rescue strategies**: strategies ranked by how much they improve the lowest cash point.
5. **Copilot**: ask *"What happens if Atlas Retail pays 30 days late, and how can I avoid a cash shortage?"* Open **How PULSE answered** under the reply to see which agents and tools were used. Try the microphone and **Listen** buttons (Chrome or Edge).
6. **Copilot**: ask *"Prepare reminders for my overdue invoices."* The agent only proposes the action.
7. **Decisions**: approve the proposed action, then execute it. Without an email workflow configured, the status becomes `QUEUED`: the action is recorded but nothing is sent.
8. **Notifications**: shortfall and overdue invoice alerts.

**Test the sign-up flow:** log out, choose **Sign up** and use any email address. The 6-digit verification code is printed in the **backend terminal** (`Verification code for ...`). Enter it, complete the company profile, then connect data with one of the options: upload [demo/datasets/test_bank_export.csv](demo/datasets/test_bank_export.csv), paste a Google Sheets link, load the Northstar Studio sample, or enter estimates.

### Step 8. Test the administration console (optional)

In terminal 1, stop the server (Ctrl+C), create an administrator, then start the server again:

```bash
python scripts/create_admin.py admin@example.com --name "Pulse Administrator"
python -m uvicorn app.main:app --reload --port 8000
```

The script asks for a password (12 characters minimum). Sign in with that account to open the admin console: overview, account approvals, users, organizations, service status and activity log. See [docs/ADMIN.md](docs/ADMIN.md).

### Step 9. Run the automated tests

In terminal 1, with the virtual environment active:

```bash
python -m pytest -q
```

Expected result: `87 passed`. The tests use their own temporary SQLite database and do not touch your data. They cover authentication and email codes, tenant isolation, roles, onboarding, imports, the financial engine, forecast and simulation, rescue plans, agent tool permissions, the approval workflow, notifications and administration.

To check the frontend build: `cd frontend && npm run build`.

### Optional integrations

Add these to `backend/.env` and restart the backend:

| Feature | Variables |
|---|---|
| Supabase / PostgreSQL instead of SQLite | `DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/postgres` (for Supabase, use the session pooler host), then run `python -m alembic upgrade head` again |
| Real verification emails (SMTP, e.g. a Gmail app password) | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` |
| n8n workflows (emails, reminders, alerts) | `N8N_WEBHOOK_URL`, `N8N_OTP_WEBHOOK_URL`, `N8N_WEBHOOK_SECRET`. Import the workflows from [n8n/workflows/](n8n/workflows/) as described in [n8n/README.md](n8n/README.md) |

### Troubleshooting

| Problem | Fix |
|---|---|
| `python` not found on Windows | Use `py` instead of `python`, or reinstall Python with "Add to PATH" checked |
| PowerShell refuses to activate the venv | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once |
| `npm run dev` fails | Check that `node --version` is 20.19 or newer |
| Port 8000 or 5173 already in use | Stop the other process, or start uvicorn with `--port 8001` and set `VITE_API_BASE_URL=http://localhost:8001` in `frontend/.env.local` |
| `(trapped) error reading bcrypt version` | Harmless passlib warning, ignore it |
| No verification code appears | Check that `OTP_ALLOW_SERVER_LOG=true` is in `backend/.env`, then restart the backend |
| Login fails after reseeding | Use the new password printed by `seed_demo.py` |

## Responsible AI

- PULSE AI is decision support, not a regulated financial adviser.
- Forecasts and simulations are estimates from recorded data and explicit assumptions, never guarantees.
- The copilot can only state figures the engine computed.
- No money transfer, borrowing or banking transaction is possible through the platform.
- Every consequential action needs explicit human approval and is recorded in the audit log.

## Repository layout

```
backend/     FastAPI app, engines, agents, Alembic migrations, tests, scripts
frontend/    React + Vite + TypeScript app
n8n/         Exportable n8n workflows
demo/        Sample datasets (e.g. demo/datasets/test_bank_export.csv)
docs/        Architecture, feature status, demo script, admin guide
submission/  Screenshots used in this README
```

## Team

Built for FinTechathon 2026 by the PULSE AI team.
