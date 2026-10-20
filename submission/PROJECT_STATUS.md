# PULSE AI — implementation audit

Audit date: 20 October 2026. Source baseline: `054e7109c6bbd183e23deb3a72e9219b78cef426`.

## Implemented

- React/TypeScript/Vite frontend with landing, signup/onboarding, dashboard, forecast, copilot, simulator, invoices, notifications, decisions, settings and platform administration.
- FastAPI, SQLAlchemy and Alembic backend; SQLite locally, PostgreSQL driver/configuration available.
- Decimal-based liquidity, historical cash flow, burn, runway, overdue invoices, concentration and rule-based risk calculations.
- Daily deterministic forecasts separate scheduled obligations/invoice dates from a trailing-average uncertain flow. Recurring categories are excluded from the historical average to avoid that category-level double count.
- Digital Twin applies copied scenario inputs and recomputes the forecast; original financial records are not edited by the simulation.
- Specialist tool registry and bounded LLM tool-calling loop, plus deterministic fallback when no provider is configured. Financial summary, forecasting, simulation, rescue plans, invoice lookup and reminder proposals are available tools.
- JWT bearer authentication, bcrypt hashes, email OTP, organization membership/role checks, platform approval of new accounts and account-review history.
- Consequential actions require approval before execution; execution and notification records are persisted. Sequential re-execution is rejected by status.
- Five n8n workflow exports and a local provisioning/test harness. Direct SMTP fallback for signup codes. Local n8n execution results must be distinguished from the submission demo's intentionally non-dispatched action.

## Partial, absent or limited

- No implemented vector database, embedding index, document retrieval pipeline or RAG. Structured financial tool calls are not RAG.
- The Risk Guardian enforces tool permissions and supplies prompt rules; it is not a complete semantic verifier of every generated sentence or number.
- Forecast confidence labels are heuristic, not statistically calibrated probabilities. Historical averages are not an ML forecasting model.
- Monthly recurrence matches day-of-month; month-end handling, seasonality, currency conversion and reconciliation need further work. Invoice receipts may overlap with historical average revenue; this is a modeling limitation.
- No bank integration, payment movement or regulated financial advisory service. Financing terms in rescue candidates are illustrative.
- No comprehensive login/IP rate limiter, MFA, refresh-token revocation, immutable external audit storage, tenant database RLS or automated prompt-injection defense is established by the inspected code.
- Action status prevents sequential replay, but concurrent execution and ambiguous external-provider acknowledgements need stronger atomic/idempotent handling.
- Customer names are not email addresses. Invoice reminder execution requires actual addresses in approved drafts.
- SQLite files on different machines are different account stores; multi-user shared deployment needs a common backend/database.

## Startup and verification

Backend: `cd backend`, install `requirements.txt`, run `python -m alembic upgrade head`, optionally `python scripts/seed_demo.py`, then `python -m uvicorn app.main:app --port 8000`.

Frontend: `cd frontend`, run `npm ci`, then `npm run dev`. Production validation: `npm run build`.

Tests: `cd backend`, then `python -m pytest -q`. Fresh results and any failures are recorded in `execution_evidence/`; this audit does not assume they pass.

The package-generation session uses a separate synthetic database and deterministic copilot mode. Evidence must not include live credentials, authentication tokens or private user records. Dependency versions and schema details are captured from actual source during generation.
