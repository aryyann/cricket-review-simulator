.PHONY: backend frontend test
backend:
	PYTHONPATH=. uvicorn backend.main:app --reload --port 8000
frontend:
	cd frontend && npm run dev
test:
	PYTHONPATH=. pytest -q
