# Source code information

Repository: https://github.com/EyaAzzabi/Pulse

Branch: `main`

Local application baseline reviewed: `054e7109c6bbd183e23deb3a72e9219b78cef426`.

The remote README was reviewed on 20 October 2026. It identifies Supabase PostgreSQL as the shared database and SQLite for tests. The local evidence run contains 86 passing tests; this package reports that recorded result rather than the README's separate 87-test claim.

`PULSE_Source_Code.zip` includes the local tracked source snapshot and submission reproduction scripts. It excludes `.env`, local account credentials, `.runtime`, databases, virtual environments, dependencies and Git metadata. The separately generated submission documents are in the outer bundle.

## Run the application

1. Install Python and Node.js; create a backend virtual environment.
2. Run `pip install -r backend/requirements.txt` in that environment.
3. Configure `backend/.env` privately using the repository's example. For the shared team instance, set the Supabase PostgreSQL `DATABASE_URL` and a strong JWT secret. Configure SMTP or n8n for real email delivery.
4. In `backend`, run `python -m alembic upgrade head`, then `python -m uvicorn app.main:app --port 8000`.
5. In `frontend`, run `npm ci`, configure `VITE_API_BASE_URL` to the shared backend URL, then `npm run dev` or deploy `npm run build` output.
6. Use `backend/scripts/create_admin.py` according to `docs/ADMIN.md`. Do not use submission demonstration credentials for a deployed administrator.
7. For checks: in `backend`, run `python -m pytest -q`; in `frontend`, run `npm run build`.

## Reproduce isolated evidence

Run `python submission/scripts/demo_environment.py` to prepare an isolated synthetic database, then `python submission/scripts/demo_environment.py serve` to serve port 8002. Start Vite on port 5175 with `VITE_API_BASE_URL=http://127.0.0.1:8002`. Install Playwright and its Chromium browser, then run `python submission/scripts/capture_evidence.py`. The capture script expects the two servers to be running. Generated credentials remain in ignored `.runtime/submission/` and are never included in the submission.

The document builder additionally requires `python-pptx`, `reportlab` and Pillow. The video conversion uses imageio-ffmpeg. Synthetic dates depend on the date the fixture is created; the included results are dated 20 October 2026.
