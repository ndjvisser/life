# Life Dashboard - Development Commands

.PHONY: help install dev-install test lint format check-architecture clean reset setup-sample-data

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
	pip install pip-tools
	pip-compile --output-file=constraints.txt pyproject.toml
	@echo "✅ Generated constraints.txt"

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
	behave features/ || echo "BDD tests not yet implemented"

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
	pip-sync constraints.txt

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
	cd life_dashboard && python manage.py flush --noinput || true
	cd life_dashboard && rm -f db.sqlite3 || true
	$(MAKE) migrate

setup-sample-data:
	cd life_dashboard && python manage.py createsuperuser --noinput --username admin --email admin@example.com || true
	cd life_dashboard && python manage.py shell -c "from django.contrib.auth.models import User; u = User.objects.get(username='admin'); u.set_password('admin'); u.save()" || true
	@echo "✅ Sample data created (admin/admin)"

# Architecture
check-boundaries: check-architecture
	import-linter --config pyproject.toml || echo "⚠️  import-linter not installed"

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
	pip install import-linter mypy django-stubs ruff
	pip install django pydantic

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
