# Implementation and verification status

This file distinguishes working local behavior from the larger engineering brief. It does not certify production readiness.

## Implemented and verified against the running API

- Fresh synthetic demo authentication and organization-scoped session.
- Server-calculated summary, dated baseline forecast and liquidity detection.
- Isolated delay, purchase and recovery simulations.
- EUR 18,000 current cash; baseline minimum EUR -600; EUR 8,000 purchase changes ending balance by exactly EUR -8,000; recovery assumptions keep minimum cash positive.
- Attempting execution before approval returns HTTP 409. Approved offline execution returns QUEUED, and replay remains QUEUED.
- Simulation runs leave source financial metrics unchanged.

Verification: `python scripts/verify_demo.py` against a running local FastAPI server. The calendar shortfall date is seed-relative.

## Implemented and tested in the backend suite

Authentication, password hashing, expiring/revocable sessions, tenant and role enforcement; onboarding storage; CSV preview/confirmation/deduplication; invoices; actions and audit; notifications; local text/PDF extraction and lexical document retrieval; offline financial explanations; optional configured provider and authenticated webhook paths.

Additional coverage: invoice payment bookkeeping and duplicate payment references; fractional monetary conservation; ranked rescue strategies; financing-readiness export; owner-only, expiring, single-use invitations bound to the invited email; expired approval rejection; invalid provider numbers falling back to offline explanations.

**Executed result:** `python -m pytest backend/tests -q` — **21 passed**. This includes regression checks preventing invoice settlements from inflating recurring revenue and rejecting future-dated posted CSV transactions. Python compilation passed. `alembic upgrade head` passed on a fresh temporary SQLite database.

## Frontend verification

Final TypeScript compilation and Vite production build passed. The dependency audit reported **zero vulnerabilities**. Chromium exercised demo login, API-driven dashboard, EUR 8,000 purchase simulation, reminder proposal → approval → offline queue, and grounded offline chat. Desktop and mobile screenshots are in `docs/screenshots/`.

**Final browser regression:** passed after the dependency, encoding and financial fixes, with **zero page errors** and no mobile page overflow.

## External configuration not verified

- Live LLM provider output and availability.
- Live n8n webhook and email delivery. Local no-provider queue and simulated provider failures are testable without credentials.
- Docker/Compose and PostgreSQL deployment.
- GitHub Actions execution on a remote repository.

## Partial or planned

- Full nine-step premium onboarding and comprehensive user preferences. A shorter persisted setup flow and organization selector are implemented.
- Embeddings and FAISS. The implemented fallback is explicitly lexical retrieval.
- Six independently orchestrated LLM agents. The implemented offline path invokes deterministic financial tools; it does not simulate a live multi-agent LLM run.
- Real banking feeds, market lending offers, transfers, borrowing or trading execution.
- OCR, provider-confirmed email setup, recurring job scheduler and automatic digest dispatch.
- PDF report export and statistical backtesting.
- Voice capture/synthesis, invoice detail drawers and a full invoice creation/payment-entry interface. Invoice creation and payment tracking are available through authenticated API endpoints.
- Complete audit timeline UI, persisted chat-history navigation and every requested analytics visualization. Audit records and conversations are persisted and exposed through the API.
- Full production rate limiting, deployment hardening and expanded normalized domain model. Some tenant-owned prototype entities use typed record payloads rather than dedicated tables.
- Tailwind/shadcn and a dedicated Vitest suite are not part of the current frontend. It uses shared React controls, custom CSS, TanStack Query, Motion and React Hook Form/Zod; browser tests cover the core journey.

See [VERIFICATION.md](VERIFICATION.md) for executed checks and [screenshots](screenshots/dashboard.png) for the application. Unlisted production capabilities should not be assumed complete.
