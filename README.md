# Pulse AI

**Your business deserves a financial brain.**

Pulse AI is an intelligent financial copilot for SMEs, built around a
**Financial Digital Twin**: a deterministic simulation of a business's future
cash position that lets an owner stress-test decisions — a late-paying
customer, a large purchase, a financing option — before making them for real.

Built for the **Shenzhen International FinTech Competition 2026 (FinTechathon)**,
International Track, Topic E — SME Finance Copilot. See
`docs/COMPETITION_SUBMISSION.md` for the full submission summary and
`docs/SPEC.md` for the original project brief this implementation follows.

## Why it's not "just a chatbot"

Every number Pulse shows — cash balance, forecast, simulation result, rescue
plan ranking — is computed by plain, deterministic, tested Python code in
`backend/app/financial`, `backend/app/forecasting` and `backend/app/simulations`.
An LLM is optional: if none is configured, the AI Copilot still answers using
those same numbers, just in plainer sentences. Nothing is ever invented, and
no action (like sending an invoice reminder) executes without explicit human
approval. See `docs/ARCHITECTURE.md` for how this is enforced.

## Architecture at a glance

- **Backend:** FastAPI + SQLAlchemy + SQLite (dev) / PostgreSQL (prod)
- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **AI:** Pluggable LLM provider (Groq / OpenAI-compatible), with a fully
  functional offline fallback
- **Automation:** n8n workflow exports + webhook dispatch, with a safe
  "queued, not sent" fallback when n8n isn't configured

Full breakdown: `docs/ARCHITECTURE.md`. Current implementation status,
feature by feature, honestly: `docs/FEATURE_STATUS.md`.

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv
./.venv/Scripts/pip install -r requirements.txt     # macOS/Linux: .venv/bin/pip
./.venv/Scripts/python scripts/seed_demo.py          # seeds the Northstar Studio demo org
./.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000
```

The seed script prints a one-time login (email + generated password) for the
demo organization — it is never hardcoded, so re-run it any time to get a
fresh reproducible demo and reset the data to its original state.

Backend runs at `http://localhost:8000`. Interactive API docs (OpenAPI/Swagger)
at `http://localhost:8000/docs`. Health check: `GET /health`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and talks to the backend at
`http://localhost:8000` by default (override with `VITE_API_BASE_URL`).

### 3. Run the tests

```bash
cd backend
./.venv/Scripts/python -m pytest -q
```

32 tests cover auth, tenant isolation, role enforcement, the deterministic
financial engine, forecast determinism, simulation isolation, and the
Decision Center's approval/idempotency rules. See
`docs/COMPETITION_SUBMISSION.md` for what's been run and verified versus
planned.

## Environment variables

Copy `.env.example` to `backend/.env` and adjust. Every variable has a safe
local default — **Pulse runs fully offline** (deterministic engine + SQLite,
no external API keys) out of the box. See the comments in `.env.example` for
what each optional integration (LLM provider, n8n, SMTP) unlocks.

## Demo scenario

The seeded "Northstar Studio" organization (e-commerce/retail, EUR) has six
months of transaction history, several overdue receivables, a large
upcoming inventory payable, and recurring payroll/rent/software obligations —
enough for the deterministic forecast to surface a real (not scripted) future
cash dip. Walkthrough: `docs/DEMO_SCRIPT.md`.

## AI limitations and responsible use

- Pulse AI is **decision support, not a regulated financial adviser**.
- Forecasts and simulations are estimates based on recorded data and explicit
  assumptions — never guarantees.
- The AI copilot can only state figures the deterministic financial engine
  already computed; it cannot invent balances, dates, or outcomes.
- No real money transfer, borrowing, or banking transaction is implemented or
  possible through this platform.
- Every consequential action (e.g. an invoice reminder email) requires
  explicit human approval and is never silently marked as delivered unless a
  configured integration actually confirmed it.

## Security

Passwords are bcrypt-hashed; JWT-based auth; every organization-scoped
endpoint is authorized server-side (see `backend/app/api/deps.py`); secrets
live only in environment variables, never in frontend code or commits. See
`docs/ARCHITECTURE.md#security-boundaries`.

## Repository layout

```
backend/    FastAPI app, financial/forecasting/simulation engines, tests
frontend/   React + Vite + TypeScript app
n8n/        Exportable n8n workflow JSON (cash alerts, reminders, digests)
demo/       (reserved for exported demo datasets/scenarios)
docs/       Architecture, competition submission, demo script, feature status
```
