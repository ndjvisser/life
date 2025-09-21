# Life Dashboard - Development Commands

.PHONY: help install dev-install generate-constraints setup test test-unit test-integration test-bdd test-domain test-domain-fast test-properties test-contracts test-snapshots test-all-unit test-domain-coverage test-thorough test-parallel test-all lint format type-check type-check-strict check-architecture pre-commit compile-deps sync-deps update-deps check-deps migrate resetdb setup-sample-data reset-admin-password check-dev-env check-boundaries architecture-report dependency-graph runserver clean reset ci-install ci-check docker-build docker-run docs dev collectstatic deploy-check

# Default target
help:
	@echo "Life Dashboard Development Commands"
	@echo "=================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  install          Install production dependencies"
	@echo "  dev-install      Install development dependencies"
	@echo "  setup            Initial project setup"
	@echo ""
	@echo "Development Commands:"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-bdd         Run BDD feature tests"
	@echo ""
	@echo "Domain-First Testing Commands:"
	@echo "  test-domain      Run pure domain tests (fastest)"
	@echo "  test-domain-fast Run domain tests with minimal examples"
	@echo "  test-properties  Run property-based tests with Hypothesis"
	@echo "  test-contracts   Run contract tests with Pydantic validation"
	@echo "  test-snapshots   Run snapshot tests for API responses"
	@echo "  test-all-unit    Run all unit tests (domain + contracts + properties + snapshots)"
	@echo "  test-domain-coverage Run domain tests with coverage"
	@echo "  test-thorough    Run comprehensive tests with maximum examples"
	@echo "  test-parallel    Run tests in parallel"
	@echo ""
	@echo "Code Quality Commands:"
	@echo "  lint             Run linting (ruff)"
	@echo "  format           Format code (ruff format)"
	@echo "  type-check       Run type checking (mypy)"
	@echo "  check-architecture Check architecture boundaries"
	@echo "  pre-commit       Run pre-commit hooks"
	@echo ""
	@echo "Database Commands:"
	@echo "  migrate          Run database migrations"
	@echo "  resetdb          Reset database and run migrations"
	@echo "  setup-sample-data Create sample data for development"
	@echo ""
	@echo "Architecture Commands:"
	@echo "  check-boundaries Check bounded context boundaries"
	@echo "  architecture-report Generate architecture report"
	@echo "  dependency-graph Generate dependency graph"
	@echo ""
	@echo "Cleanup Commands:"
	@echo "  clean            Clean temporary files"
	@echo "  reset            Full reset (clean + resetdb)"

# Installation
install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"
	pre-commit install

generate-constraints:
	@echo "Generating constraints.txt from pyproject.toml..."
	$(MAKE) compile-deps
setup: dev-install migrate setup-sample-data
	@echo "✅ Project setup complete!"

# Testing
test:
	python -m pytest

test-unit:
	python -m pytest -m "unit or not integration"

test-integration:
	python -m pytest -m integration

test-bdd:
	@if command -v behave >/dev/null 2>&1; then \
		behave features/; \
	else \
		echo "⚠️ behave not installed; skipping BDD tests"; \
		if [ -n "$$CI" ]; then echo "❌ BDD tests required in CI"; exit 1; fi; \
	fi
# Domain-first testing targets
test-domain:
	python scripts/run-domain-tests.py --domain-only

test-domain-fast:
	python scripts/run-domain-tests.py --domain-only --profile dev

test-properties:
	python scripts/run-domain-tests.py --with-properties

test-contracts:
	python scripts/run-domain-tests.py --with-contracts

test-snapshots:
	python scripts/run-domain-tests.py --with-snapshots

test-all-unit:
	python scripts/run-domain-tests.py --all-unit

test-domain-coverage:
	python scripts/run-domain-tests.py --domain-only --coverage

test-thorough:
	python scripts/run-domain-tests.py --all-unit --profile thorough --coverage

test-parallel:
	python scripts/run-domain-tests.py --all-unit --parallel

test-all: test test-bdd
	@echo "✅ All tests completed"

# Code Quality
lint:
	ruff check .

format:
	ruff format .

type-check:
	mypy life_dashboard/dashboard/domain/ --config-file pyproject.toml
	mypy life_dashboard/stats/domain/ --config-file pyproject.toml

type-check-strict:
	mypy life_dashboard/dashboard/domain/ --config-file pyproject.toml
	mypy life_dashboard/stats/domain/ --config-file pyproject.toml
	mypy life_dashboard/quests/domain/ --config-file pyproject.toml
	mypy life_dashboard/skills/domain/ --config-file pyproject.toml
	mypy life_dashboard/achievements/domain/ --config-file pyproject.toml
	mypy life_dashboard/journals/domain/ --config-file pyproject.toml

check-architecture:
	python scripts/check-architecture.py

pre-commit:
	pre-commit run --all-files

# Dependency Management
compile-deps:
	python scripts/generate-constraints.py

sync-deps:
	pip-sync requirements.txt -c constraints.txt

update-deps: generate-constraints

check-deps:
	@echo "Checking if constraints are up to date..."
	pip install pip-tools
	pip-compile --dry-run --output-file=constraints.txt pyproject.toml || (echo "❌ constraints.txt is out of date. Run 'make generate-constraints' to update it." && exit 1)
	@echo "✅ constraints.txt is up to date"
	@python scripts/generate-constraints.py --check || (echo "❌ Constraints are out of date. Run 'make compile-deps' to update." && exit 1)

# Database
migrate:
	cd life_dashboard && python manage.py migrate

resetdb:
	@echo "🔒 Checking environment before database reset..."
	@if [ "$${ENV}" = "production" ] || [ "$${DJANGO_SETTINGS_MODULE}" = "life_dashboard.settings.production" ]; then \
		echo "❌ Error: Cannot reset database in production environment"; \
		echo "   If you really need to reset the production database, set FORCE_RESET=1"; \
		exit 1; \
	fi
	@if [ -z "$${FORCE_RESET}" ] && [ -f "life_dashboard/db.sqlite3" ]; then \
		echo "❌ Safety check failed: db.sqlite3 exists and FORCE_RESET is not set"; \
		echo "   To confirm database reset, run: make resetdb FORCE_RESET=1"; \
		exit 1; \
	fi
	@echo "🔄 Resetting database..."
	@cd life_dashboard && ( \
		echo "  - Running database flush..." && \
		python manage.py flush --noinput && \
		echo "  - Removing database file..." && \
		rm -f db.sqlite3 && \
		echo "  - Running migrations..." && \
		python manage.py migrate \
	) || (echo "❌ Database reset failed"; exit 1)
	@echo "✅ Database reset complete"

setup-sample-data: check-dev-env
	@echo "🔄 Setting up development admin user..."
	@cd life_dashboard && \
	if ! python -c "import secrets; print(secrets.token_urlsafe(16))" >/dev/null 2>&1; then \
		echo "❌ Python secrets module not available"; exit 1; \
	fi
	@cd life_dashboard && \
	ADMIN_USER=$${ADMIN_USER:-admin} && \
	ADMIN_EMAIL=$${ADMIN_EMAIL:-admin@example.com} && \
	ADMIN_PASSWORD=$$(python -c "import secrets; print(secrets.token_urlsafe(16))") && \
	echo "ADMIN_USER=$$ADMIN_USER" > .env.local && \
	echo "ADMIN_EMAIL=$$ADMIN_EMAIL" >> .env.local && \
	echo "ADMIN_PASSWORD=$$ADMIN_PASSWORD" >> .env.local && \
	echo "DJANGO_SUPERUSER_PASSWORD=$$ADMIN_PASSWORD" >> .env.local && \
	if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='$$ADMIN_USER').exists()" 2>/dev/null | grep -q True; then \
		echo "Creating admin user: $$ADMIN_USER" && \
		python manage.py createsuperuser --noinput --username "$$ADMIN_USER" --email "$$ADMIN_EMAIL" 2>/dev/null || true && \
		python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(username='$$ADMIN_USER'); u.set_password('$$ADMIN_PASSWORD'); u.save()" && \
		echo "✅ Admin user created" && \
		echo "\n🔑 Admin credentials (saved to .env.local):" && \
		echo "   Username: $$ADMIN_USER" && \
		echo "   Password: $$ADMIN_PASSWORD\n" && \
		echo "⚠️  These credentials are for development only. Do not use in production!" && \
		echo "   To use these credentials, run: source .env.local"; \
	else \
		echo "ℹ️  Admin user '$$ADMIN_USER' already exists. Using existing user." && \
		echo "   To reset the password, run: make reset-admin-password"; \
	fi

reset-admin-password: check-dev-env
	@echo "🔄 Resetting admin password..."
	@cd life_dashboard && \
	if [ ! -f .env.local ]; then \
		echo "❌ .env.local not found. Run 'make setup-sample-data' first."; exit 1; \
	fi
	. .env.local && \
	if [ -z "$$ADMIN_USER" ]; then \
	        echo "❌ ADMIN_USER not found in .env.local"; exit 1; \
	fi; \
	NEW_PASSWORD=$$(python -c "import secrets; print(secrets.token_urlsafe(16))") && \
	NEW_PASSWORD="$$NEW_PASSWORD" python -c "\
import os\nfrom pathlib import Path\n\nenv_path = Path('.env.local')\nnew_password = os.environ['NEW_PASSWORD']\n\ntry:\n    with env_path.open('r') as env_file:\n        lines = [line for line in env_file if not line.startswith(('ADMIN_PASSWORD=', 'DJANGO_SUPERUSER_PASSWORD='))]\nexcept FileNotFoundError:\n    lines = []\n\nlines.append(f'ADMIN_PASSWORD={new_password}\\n')\nlines.append(f'DJANGO_SUPERUSER_PASSWORD={new_password}\\n')\n\nwith env_path.open('w') as env_file:\n    env_file.writelines(lines)\n" && \
	NEW_PASSWORD="$$NEW_PASSWORD" python manage.py shell -c "import os; from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(username='$$ADMIN_USER'); u.set_password(os.environ['NEW_PASSWORD']); u.save()" && \
	echo "✅ Admin password reset successful" && \
	echo "🔑 New password (saved to .env.local): $$NEW_PASSWORD"

check-dev-env:
	@if [ "$${ENV:-development}" != "development" ] && [ ! -f .env.development ]; then \
		echo "❌ This command is only allowed in development environment"; \
		echo "   Set ENV=development or create a .env.development file to continue"; \
		exit 1; \
	fi

# Architecture
check-boundaries: check-architecture
	import-linter --config pyproject.toml || (echo "❌ Import boundary violations found or import-linter not installed"; exit 1)

architecture-report:
	python scripts/check-architecture.py --report

dependency-graph:
	mkdir -p docs/architecture
	pydeps life_dashboard --max-bacon=2 --cluster --rankdir=TB -o docs/architecture/dependency-graph.svg || echo "⚠️  pydeps not installed"

# Development Server
runserver:
	cd life_dashboard && python manage.py runserver

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + || true
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache

reset: clean resetdb
	@echo "✅ Full reset complete"

# CI/CD helpers
ci-install:
	pip install -r requirements.txt
	pip install -e ".[dev]"

ci-check: lint type-check-strict check-architecture
	@echo "✅ CI checks passed"

# Docker helpers (for future use)
docker-build:
	docker build -t life-dashboard .

docker-run:
	docker run -p 8000:8000 life-dashboard

# Documentation
docs:
	@echo "📚 Generating documentation..."
	@echo "Architecture report:"
	$(MAKE) architecture-report
	@echo ""
	@echo "Dependency graph:"
	$(MAKE) dependency-graph

# Development workflow
dev: format lint type-check check-architecture test
	@echo "✅ Development workflow complete!"

# Production helpers
collectstatic:
	cd life_dashboard && python manage.py collectstatic --noinput

deploy-check: ci-check test-all
	@echo "✅ Ready for deployment!"
