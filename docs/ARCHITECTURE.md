# Architecture

## Overview

Pulse AI is a modular monolith: one FastAPI backend, one React frontend, SQLite
locally (Postgres optional in production), and an optional n8n instance for
outbound automation. There is no distributed system here on purpose — the
competition brief explicitly asks for a modular monolith with clear domain
boundaries, not microservices.

```
frontend (React + Vite + TS)
        |  HTTPS / JSON, Bearer JWT, ?organization_id=...
        v
backend (FastAPI)
  app/api/          <- thin route handlers: auth, validation, authorization only
  app/financial/    <- deterministic financial calculations (Decimal)
  app/forecasting/  <- deterministic baseline cash-flow forecast
  app/simulations/  <- Financial Digital Twin: scenario engine
  app/agents/        <- LLM provider abstraction + orchestrator
  app/services/      <- rescue plans, workflows (n8n dispatch), financial data loader
  app/models/         <- SQLAlchemy ORM models
        |
        v
SQLite (dev) / Postgres (prod)
        |
        v  (optional, only if N8N_WEBHOOK_URL is set)
n8n  -> SMTP / other integrations
```

## Why domain logic is not in route handlers

Every API route in `app/api/*.py` does three things only: authenticate,
authorize (via `require_membership`/`require_role`), and call into a
`financial`, `forecasting`, `simulations`, `services`, or `agents` module. This
keeps the financial logic independently testable (see `backend/tests/`) without
spinning up HTTP at all, and it's what makes the "financial calculations must
be deterministic Python, not an LLM" requirement actually verifiable: you can
read `app/financial/engine.py` top to bottom and see there isn't an LLM call
anywhere near it.

## Data flow for a single number: "cash runway"

1. `scripts/seed_demo.py` (or real usage) writes rows into `transactions`,
   `invoices`, `recurring_obligations`, `business_profiles`.
2. `app/services/financial_data.load_financial_inputs` reads those rows for one
   organization only (tenant-scoped query).
3. `app/financial/engine.compute_summary` runs plain Decimal arithmetic:
   `current_liquidity` replays transactions on top of the opening balance,
   `monthly_burn_rate` looks at trailing 90-day net outflow, `cash_runway_days`
   divides cash by daily burn.
4. `app/api/financial.get_summary` serializes that dataclass into
   `FinancialSummaryOut` and returns it.
5. The frontend renders exactly that payload — it does not compute or guess
   any number client-side.

The same pattern repeats for forecasting (`app/forecasting/engine.run_forecast`)
and simulation (`app/simulations/engine.run_simulation`): inputs are loaded from
the database, a pure function computes a result, the API serializes it, the
frontend displays it.

## Agent interaction (Copilot)

`app/agents/orchestrator.handle_message` is the single entry point used by
`POST /copilot/chat`:

1. **Classify intent** (`classify_intent`) — a small keyword classifier maps
   the user's message to one of: `cash_runway`, `biggest_risk`, `simulate`,
   `affordability`, `invoice_reminders`, `rescue_plan`, `general_summary`.
2. **Financial Analyst / Forecast Analyst role** — `compute_summary` (and, for
   the `simulate` intent, `run_forecast`) is called to get grounded numbers.
3. **Strategic Planner role** — for `rescue_plan`, `generate_rescue_plans` runs
   the simulation engine three times (once per candidate strategy) and ranks
   them by actual simulated liquidity benefit.
4. **Deterministic answer is built first**, in plain Python string
   templates, using only the numbers from step 2–3.
5. **Risk Guardian rule, enforced structurally**: the LLM (if configured) is
   only ever asked to rephrase that deterministic text — the prompt sent to it
   explicitly forbids inventing figures, and the response is labeled
   `ai_generated: true/false` so the frontend can show which mode produced it.
6. If no LLM is configured, or the LLM call fails/times out, step 4's text is
   returned as-is. The copilot never goes offline because of a missing API key.

This collapses the brief's six-agent description into one orchestrator module
with clearly separated responsibilities (each a named function), rather than
six separate services, because a hard separation would mean six more network
hops for no behavioral benefit at this scale — see `docs/SPEC.md` section 13 for
the original per-agent breakdown this maps to.

## Security boundaries

- Every org-scoped endpoint requires a valid JWT (`get_current_user`) and an
  explicit membership check (`require_membership`) or role check
  (`require_role`) against the `organization_id` query parameter — there is no
  endpoint that infers the organization from client-supplied data without
  verifying membership first.
- Passwords are hashed with bcrypt (`passlib`), never logged.
- The LLM is treated as untrusted for factual claims (see above) — it can
  explain, never decide or invent.
- Consequential actions (currently: invoice reminder emails) go through
  `PROPOSE -> APPROVE -> EXECUTE`, each step re-validating organization
  membership and role server-side; execution is idempotent on `status`
  (`test_actions.py::test_approve_then_execute_is_idempotent_on_status`).
- No endpoint can move money, create debt, or touch a real bank account —
  those are explicitly out of scope per the brief and not implemented.

## RAG / document intelligence

Not implemented in this pass (see `docs/FEATURE_STATUS.md`). The data model
(`uploaded_documents`, `document_chunks` in the original spec) is not yet
created; this section will be filled in if/when that phase lands.

## Automation design

See `n8n/workflows/*.json` for the four workflow exports (Cash Risk Alert,
Invoice Reminder, Financial Digest, Approved Recovery Plan) and
`app/services/workflows.py` for the dispatch code they pair with. The backend
never assumes n8n is reachable: `dispatch_action` returns `QUEUED` with a clear
reason when `N8N_WEBHOOK_URL` is unset, and `FAILED` (never `SENT`) if the
webhook call errors.
