.DEFAULT_GOAL := help
PYTHON := .venv/bin/python
CRUCIBLE := .venv/bin/crucible

.PHONY: help bootstrap clean format lint typecheck test test-properties test-sandbox security sbom build eval-smoke benchmark analyze evidence docs up health down

help:
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "%-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

bootstrap: ## Create the environment and install development dependencies
	uv sync --extra dev --frozen

clean: ## Remove generated build and test artifacts
	rm -rf build dist .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov

format: ## Format Python sources
	uv run --extra dev ruff format .

lint: ## Check formatting and lint rules
	uv run --extra dev ruff format --check .
	uv run --extra dev ruff check .

typecheck: ## Run strict static type checks
	uv run --extra dev mypy crucible

test: ## Run the full test suite
	uv run --extra dev pytest --cov=crucible --cov-report=term-missing

test-properties: ## Run property and invariant tests
	uv run --extra dev pytest tests/property

test-sandbox: ## Validate sandbox architecture and policy
	uv run --extra dev pytest -m sandbox

security: ## Audit Python dependencies
	$(PYTHON) scripts/secret_scan.py
	uv run --extra dev pip-audit

sbom: ## Generate a CycloneDX-compatible dependency inventory
	mkdir -p artifacts
	uv export --format requirements-txt --no-hashes > artifacts/requirements-sbom.txt

build: ## Build source and wheel distributions
	uv build

eval-smoke: ## Run one deterministic bounded evaluation
	$(CRUCIBLE) eval run CODE-001 --model mock --agent bounded

benchmark: ## Run the public BLUE mock validation suite
	$(CRUCIBLE) eval suite blue --model mock --agent bounded

analyze: ## Compare model-only and bounded mock validation runs
	$(CRUCIBLE) compare --condition model-only --condition bounded-agent --suite blue

evidence: ## Verify every generated evidence package
	$(CRUCIBLE) evidence verify-all

docs: ## Validate documentation links and required files
	$(PYTHON) scripts/check_docs.py

up: ## Start the local health/status service
	docker compose up -d --build

health: ## Check the local service health
	$(PYTHON) scripts/healthcheck.py

down: ## Stop the local service
	docker compose down --remove-orphans
