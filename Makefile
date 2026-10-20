.PHONY: backend-install backend-dev backend-test seed frontend-install frontend-dev frontend-build dev

backend-install:
	cd backend && python -m venv .venv && ./.venv/Scripts/pip install -r requirements.txt

backend-dev:
	cd backend && ./.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000

backend-test:
	cd backend && ./.venv/Scripts/python -m pytest -q

seed:
	cd backend && ./.venv/Scripts/python scripts/seed_demo.py

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

dev:
	@echo "Run 'make backend-dev' and 'make frontend-dev' in two separate terminals."
