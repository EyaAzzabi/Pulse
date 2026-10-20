# Synthetic demonstration

The running API creates synthetic Northstar Studio transactions and invoices when `POST /api/auth/demo` is called. Each request creates an isolated fresh demo organization and session; no shared password is used. The frontend demo button calls this endpoint.

The three JSON files in `scenarios/` are request bodies for `POST /api/simulations`. Supply the demo bearer token. These scenarios are hypothetical: they never post real transactions or confirm customer collection dates. Compare ending balance, minimum balance and first shortfall date.

Use the UI's demo/reset action where available, or begin a new demo session for a fresh dataset. There is no global database deletion command. Do not use synthetic data for actual financial decisions.
