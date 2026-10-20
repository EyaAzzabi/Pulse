# Execution evidence

PULSE AI is a non-on-chain topic. Evidence is from the running sandbox (simulated account: the Northstar Studio company).

| File | Content |
|---|---|
| api_core_scenario.md | Real, sanitized API requests and responses: login, summary, forecast, rescue plans, simulation, propose, refused execution, approval, execution, idempotency, unauthenticated rejection |
| capture_api_evidence.py | Script that produced it (`PULSE_DEMO_PASSWORD` env var) |
| test_output.txt | Tail of the real `pytest -q` run (87 passed) |
| DEMO_STEPS.md | Steps to reproduce the core scenario in the UI |
| SIMULATION_MODE.md | What is simulated and what is real |
| ../screenshots/ | Browser screenshots captured with Playwright at 1440x900 from the running app |

Identifiers, emails and tokens are replaced with placeholders. No credentials are included.
