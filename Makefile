.PHONY: help install install-dev run test lint format clean docker-up docker-down

# Default target
help:
	@echo "BharatVerse - Development Commands"
	@echo "================================="
	@echo "make install       - Install core dependencies"
	@echo "make install-dev   - Install development dependencies"
	@echo "make run          - Run the application"
	@echo "make test         - Run tests"
	@echo "make lint         - Run linting"
	@echo "make format       - Format code"
	@echo "make clean        - Clean temporary files"
	@echo "make docker-up    - Start Docker services"
	@echo "make docker-down  - Stop Docker services"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements/dev.txt

# Running
run:
	streamlit run Home.py

run-api:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Testing
test:
	pytest tests/

test-coverage:
	pytest tests/ --cov=. --cov-report=html

# Code quality
lint:
	flake8 . --max-line-length=88 --exclude=venv,__pycache__,.git
	pylint bharatverse

format:
	black .
	isort .

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
	make install-dev
	make docker-up
	@echo "Development environment ready!"

# Production
prod-build:
	docker build -t bharatverse:latest .

prod-deploy:
	@echo "Deployment instructions in docs/deployment.md"
