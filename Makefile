PYTHONPATH := .:apps/api
.PHONY: setup dev up down migrate seed test test-unit test-integration test-e2e lint format typecheck verify demo clean model
setup:
	python3 -m venv .venv && .venv/bin/pip install -e '.[postgres,queue,storage,dev]'
dev:
	PYTHONPATH=$(PYTHONPATH) uvicorn motionforge.main:app --reload --port 8000
up:
	docker compose up --build
down:
	docker compose down
migrate:
	PYTHONPATH=$(PYTHONPATH) alembic upgrade head
seed:
	PYTHONPATH=$(PYTHONPATH) python scripts/bootstrap/seed.py
test:
	PYTHONPATH=$(PYTHONPATH) pytest -q
test-unit:
	PYTHONPATH=$(PYTHONPATH) pytest -q tests/unit
test-integration:
	PYTHONPATH=$(PYTHONPATH) pytest -q tests/integration
test-e2e:
	cd apps/web && npx playwright test
lint:
	ruff check apps packages scripts tests
format:
	ruff format apps packages scripts tests
typecheck:
	mypy apps packages
verify:
	PYTHONPATH=$(PYTHONPATH) python scripts/verification/verify_e2e.py
demo:
	PYTHONPATH=$(PYTHONPATH) python scripts/demo/generate_marker_video.py
model:
	python scripts/models/download_movenet.py
clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache apps/web/.next verification_storage verification.db
