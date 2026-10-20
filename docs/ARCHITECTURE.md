# PULSE AI architecture

PULSE is a modular monolith: a React/TypeScript Vite application calls a FastAPI API under `/api`. SQLAlchemy persists organization-owned data in SQLite locally. Financial services use Python Decimal arithmetic; amounts are serialized for display only after calculation.

## Trust boundaries

Authentication establishes the user; organization membership establishes the tenant. The API must resolve membership on every protected request, including requests with an explicit organization header. Roles control mutations. A client-provided organization ID is never itself authorization. Uploaded documents, chat text and provider output are untrusted inputs.

## Financial data flow

Synthetic seed → historical transactions and unpaid invoices → financial summary → dated baseline forecast → isolated scenario assumptions → comparison. A scenario changes forecast inputs, never historical transactions. Known invoice obligations and assumed collection dates are separate from actual cash. Forecasts are decision support, not guarantees; no statistical confidence intervals are claimed.

## Copilot

The local evidence path retrieves calculated metrics and forecast risks. Without an LLM key, responses are explicitly deterministic offline explanations. A configured compatible provider receives grounded context from the backend; secrets remain server-side. Model output cannot authorize or execute an action.

## Approval flow

An invoice selection creates a proposal containing exact draft content. An authorized human approves the persisted proposal. Execution rechecks state and permissions and records an audit entry. Without an external delivery integration the action stays queued, never marked sent. The application does not move money, borrow, or trade.

## Deployment

The default development configuration binds services locally. Docker Compose provides a persistent SQLite volume. PostgreSQL, distributed rate limiting, TLS, backups, production secret management and delivery-provider verification require deployment-specific validation before public use. See FEATURE_STATUS.md for the verified implementation boundary.
