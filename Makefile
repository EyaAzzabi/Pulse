.PHONY: backend frontend test build
backend:
	cd backend && python -m uvicorn app.main:app --reload --port 8000
frontend:
	cd frontend && npm run dev
test:
	cd backend && python -m pytest -q
build:
	cd frontend && npm run build
