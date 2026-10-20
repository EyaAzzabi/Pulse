# Source code information

- Repository: https://github.com/EyaAzzabi/Pulse
- Branch: main
- Code commit used for the evidence: 6e19ba1 (the submission files are committed on top of it; see `git log`)
- Licence and ownership: the PULSE AI team

## Run locally
See the Quick start in the root README.md (backend: FastAPI + Alembic + seed script; frontend: npm run dev).

## Test cases
`cd backend && python -m pytest -q` runs 87 tests in backend/tests/ (auth, OTP, tenant isolation, roles, imports, onboarding,
financial engine, forecast, simulation, rescue plans, agents, actions workflow, notifications, admin).

## Excluded from the ZIP
.env files, credentials, virtual environments, node_modules, build output (dist), caches, local databases.
