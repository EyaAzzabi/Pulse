# Competition Submission Summary

**Competition:** Shenzhen International FinTech Competition 2026 — FinTechathon
**Track:** International Track
**Theme:** AI as a Financial Participant
**Topic:** E — SME Finance Copilot

## Problem

SMEs rarely have a CFO. Owners find out about a cash shortfall when it has
already happened, not when there was still time to act on it. Spreadsheets
show what happened; they don't simulate what happens next if a customer pays
late or a big purchase goes through.

## Solution

Pulse AI is a financial copilot built around a **Financial Digital Twin**: a
deterministic simulation of the business's future cash position that can be
stress-tested (payment delays, a large purchase, financing, expense cuts)
*before* the real decision is made. An AI orchestrator sits on top of that
engine to answer natural-language questions and propose ranked recovery
strategies — but every number it states comes from the deterministic engine,
never from the language model itself.

## Topic E compliance mapping

| Brief requirement | Where it lives |
|---|---|
| Understand a business's financial situation | `app/financial/engine.py` — liquidity, burn rate, receivables/payables, concentration risk |
| Anticipate problems | `app/forecasting/engine.py` — 90-day deterministic baseline forecast, shortfall detection |
| Plan interventions | `app/simulations/engine.py` + `app/services/rescue_plans.py` — Digital Twin scenarios, ranked rescue strategies |
| Prepare safe actions | `app/api/actions.py` — PROPOSE → APPROVE → EXECUTE Decision Center, human approval required, idempotent |
| AI as a participant, not just a chatbot | `app/agents/orchestrator.py` — intent classification routes to the right deterministic tool before any LLM involvement |

## What makes this different from "a chatbot with a database"

1. **The LLM is optional and provably non-authoritative.** Every copilot
   response includes `ai_generated` and `llm_available` flags. Turn off the
   LLM entirely (`LLM_PROVIDER=none`, the default) and the product still
   works — same numbers, plainer sentences.
2. **Simulations are real counterfactuals, not canned scenarios.** The Digital
   Twin re-runs the same forecasting function on a modified copy of the
   organization's actual data; nothing about a scenario's outcome is
   pre-written.
3. **Rescue plans are ranked by a real simulated benefit**, computed by
   running the simulator three times with different assumptions and
   comparing resulting lowest-cash-points — not by an LLM guessing which
   strategy "sounds best."
4. **Nothing is ever falsely marked as executed.** An action can only reach
   `SENT` if a configured delivery mechanism actually confirmed it; otherwise
   it is `QUEUED` with an explicit reason, visible in the UI and the audit
   trail.

## Reproducibility

```bash
git clone <repo-url> && cd pulse-ai  # or: this repository
python -m venv backend/.venv
./backend/.venv/Scripts/pip install -r backend/requirements.txt   # Scripts/ on Windows, bin/ on macOS/Linux
./backend/.venv/Scripts/python backend/scripts/seed_demo.py
./backend/.venv/Scripts/python -m uvicorn app.main:app --app-dir backend --port 8000
# in a second terminal
cd frontend && npm install && npm run dev
```

No external account or API key is required for any of the above. See
`.env.example` for optional integrations (LLM provider, n8n, SMTP).

## Tested functionality

32 backend tests cover authentication, tenant isolation, role enforcement,
the deterministic financial engine, forecast determinism and shortfall
detection, simulation isolation (scenarios never mutate real records), and
the Decision Center's approval/idempotency rules. Run them with:

```bash
cd backend && ./.venv/Scripts/python -m pytest -q
```

See `docs/FEATURE_STATUS.md` for the full, honest breakdown of what is
implemented-and-tested versus planned.

## Honest list of unavailable integrations in this submission

- No real LLM API key is bundled — the copilot runs in deterministic offline
  mode unless the judge/evaluator configures `LLM_PROVIDER`/`LLM_API_KEY`.
- No n8n instance is running as part of this submission — the four workflow
  JSON exports in `n8n/workflows/` have not been executed against a live n8n
  server for this submission; dispatch code exists and fails safe (`QUEUED`,
  never falsely `SENT`) without it.
- No SMTP/email provider is configured — email sending is therefore not
  demonstrated live; the draft content is real and shown in full before
  approval.
- Document intelligence/RAG, voice input, and the full 9-step onboarding
  wizard UI are not implemented in this submission (see `docs/FEATURE_STATUS.md`).
- Pulse AI is decision support, not a regulated financial adviser, and does
  not move money, extend credit, or execute banking transactions.
