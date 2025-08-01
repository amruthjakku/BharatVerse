.PHONY: help install install-dev run test lint format clean docker-up docker-down sync check fix

# Default target
help:
	@echo "BharatVerse - Development Commands (uv + ruff)"
	@echo "=============================================="
	@echo "make install       - Install core dependencies with uv"
	@echo "make install-dev   - Install development dependencies with uv"
	@echo "make sync          - Sync dependencies with uv"
	@echo "make run          - Run the application"
	@echo "make test         - Run tests"
	@echo "make lint         - Run linting with ruff"
	@echo "make format       - Format code with ruff"
	@echo "make check        - Run all checks (lint + test)"
	@echo "make fix          - Auto-fix code issues with ruff"
	@echo "make clean        - Clean temporary files"
	@echo "make docker-up    - Start Docker services"
	@echo "make docker-down  - Stop Docker services"

# Installation with uv
install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"

sync:
	uv pip sync

# Running
run:
	streamlit run Home.py

run-api:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Testing
test:
	uv run pytest tests/

test-coverage:
	uv run pytest tests/ --cov=. --cov-report=html

# Code quality with ruff (replaces black, isort, flake8, pylint)
lint:
	uv run ruff check .

format:
	uv run ruff format .

fix:
	uv run ruff check --fix .
	uv run ruff format .

check: lint test
	@echo "All checks passed!"

# Type checking
typecheck:
	uv run mypy .

# Cleaning
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete
	find . -type f -name '.coverage' -delete
	find . -type d -name '*.egg-info' -delete
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/

# Docker
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Database
db-migrate:
	python scripts/migrate_database.py

db-backup:
	python scripts/backup_database.py

# Development
dev-setup:
	cp .env.local .env
	uv pip install -e ".[dev]"
	make docker-up
	@echo "Development environment ready with uv!"

# Initialize uv project
uv-init:
	uv init --no-readme --no-pin-python
	@echo "uv project initialized!"

# Production
prod-build:
	docker build -t bharatverse:latest .

prod-deploy:
	@echo "Deployment instructions in docs/deployment.md"
