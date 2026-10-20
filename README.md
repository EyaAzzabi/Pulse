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

[Why](#why-pulse-ai) · [Product](#the-product) · [Architecture](#architecture) · [Quick start](#quick-start) · [Deliverables](#competition-deliverables) · [Responsible AI](#responsible-ai)

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

Details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [submission/PULSE_Technical_Documentation.pdf](submission/PULSE_Technical_Documentation.pdf).

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv
./.venv/Scripts/pip install -r requirements.txt     # macOS/Linux: .venv/bin/pip
# create backend/.env: DATABASE_URL, JWT secret; optional OPENAI_API_KEY, SMTP_*, N8N_*
./.venv/Scripts/python -m alembic upgrade head
./.venv/Scripts/python scripts/seed_demo.py          # loads the Northstar Studio company
./.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000
```

API docs at `http://localhost:8000/docs`, health check at `GET /health`. The seed script prints a login for Northstar Studio (set `DEMO_USER_PASSWORD` to choose it). Without an OpenAI key, the copilot runs in deterministic mode.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173, backend via VITE_API_BASE_URL
```

### 3. Tests

```bash
cd backend
./.venv/Scripts/python -m pytest -q     # 87 passed
```

The tests cover auth and email codes, tenant isolation, roles, onboarding, imports, the financial engine, forecast and simulation regressions, rescue plans, agent tool permissions, the approval workflow, notifications and admin. The latest output is in [submission/execution_evidence/test_output.txt](submission/execution_evidence/test_output.txt).

### 4. Administrator

```bash
cd backend && python scripts/create_admin.py admin@example.com --name "Pulse Administrator"
```

See [docs/ADMIN.md](docs/ADMIN.md) and [n8n/README.md](n8n/README.md).

## Competition deliverables

| # | Deliverable | Location |
|---|---|---|
| 01 | Technical documentation | [submission/PULSE_Technical_Documentation.pdf](submission/PULSE_Technical_Documentation.pdf) |
| 02 | Presentation deck | [submission/PULSE_Presentation.pptx](submission/PULSE_Presentation.pptx), [PDF](submission/PULSE_Presentation.pdf) |
| 03 | Demo video (optional) | [submission/VIDEO_RECORDING_GUIDE.md](submission/VIDEO_RECORDING_GUIDE.md) |
| 04 | Source code | this repository, [submission/SOURCE_CODE_INFORMATION.md](submission/SOURCE_CODE_INFORMATION.md) |
| 05 | Security self-assessment | [submission/PULSE_Security_Self_Assessment.pdf](submission/PULSE_Security_Self_Assessment.pdf) |
| 06 | Execution evidence | [submission/execution_evidence/](submission/execution_evidence/) |

Status of each item: [submission/SUBMISSION_CHECKLIST.md](submission/SUBMISSION_CHECKLIST.md).

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
submission/  Competition deliverables, screenshots, execution evidence
```

## Team

Built for FinTechathon 2026 by the PULSE AI team.
