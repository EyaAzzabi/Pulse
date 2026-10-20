# Verification — 20 October 2026

## Backend

`python -m pytest backend/tests -q`: **21 passed**. Includes authenticated tenant isolation, authorization, financial conservation, CSV deduplication, isolated scenarios, approval and execution state checks, document isolation, mocked webhook failure/acceptance, provider grounding fallback, invitations and invoice payments. Final regressions exclude settlements from recurring estimates and reject future posted CSV records.

`python -m compileall` passed for the backend application, scripts and Alembic files. `alembic upgrade head` succeeded against a fresh temporary SQLite database. A live Uvicorn server started on port 8000 and served the application API and OpenAPI documentation.

## HTTP demonstration

`python scripts/verify_demo.py`: passed against the live API.

| Calculated quantity | Result |
| --- | ---: |
| Current demo cash | EUR 18,000 |
| Baseline minimum | EUR -600 |
| First shortfall for this seed | 16 November 2026 |
| EUR 8,000 purchase ending-cash impact | EUR -8,000 |
| Recovery scenario minimum | EUR 18,000 |
| Approved offline reminder | QUEUED |
| Repeated execution | Same QUEUED result |
| Source data after simulations | Unchanged |

## Browser

`python scripts/browser_smoke.py`: **passed**, Chromium, **zero page errors**. It exercised demo access, dashboard values, purchase simulation, invoice reminder proposal, approval and local execution, offline copilot, remaining workspace routes and a 390-pixel mobile viewport. Mobile page-width overflow check passed. Screenshots saved under `docs/screenshots/`.

The final TypeScript and production build passed after dependency and form refinements. `npm audit` reported zero vulnerabilities. The final browser regression passed after those changes, again with zero page errors and no mobile page overflow. The live HTTP demonstration was also repeated successfully after the financial corrections.

## Boundaries

Live LLM, email/n8n delivery, Docker, PostgreSQL and remote CI were not exercised. Mocked integration tests establish failure/status behavior; they do not establish real provider connectivity. Browser availability and numerical forecasts do not constitute a security audit or a statistical accuracy benchmark.
